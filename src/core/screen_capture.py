"""
屏幕捕获模块
"""

import time
import threading
from typing import Optional, Tuple, Callable
import numpy as np
import cv2
import mss
import platform
from PyQt6.QtCore import QObject, pyqtSignal

class ScreenCapture(QObject):
    """屏幕捕获类"""
    
    # 信号
    frame_captured = pyqtSignal(np.ndarray)  # 捕获到新帧
    capture_started = pyqtSignal()           # 开始捕获
    capture_stopped = pyqtSignal()           # 停止捕获
    error_occurred = pyqtSignal(str)         # 发生错误
    
    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        self.is_capturing = False
        self.capture_thread = None
        self.fps = 30
        self.region = None  # 捕获区域 (x, y, width, height)
        self.monitor_index = 0  # 显示器索引
        self._thread_local_sct = None  # 线程本地的mss对象
        
    def get_monitors(self):
        """获取所有显示器信息"""
        monitors = []
        for i, monitor in enumerate(self.sct.monitors):
            if i == 0:  # 跳过第一个（所有显示器的组合）
                continue
            monitors.append({
                'index': i,
                'left': monitor['left'],
                'top': monitor['top'],
                'width': monitor['width'],
                'height': monitor['height'],
                'name': f"显示器 {i}"
            })
        return monitors
    
    def set_capture_region(self, x, y, width, height):
        """设置捕获区域"""
        if x is None or y is None or width is None or height is None:
            # 重置为全屏模式
            self.region = None
        else:
            self.region = {'left': x, 'top': y, 'width': width, 'height': height}
    
    def set_monitor(self, monitor_index: int):
        """设置要捕获的显示器"""
        self.monitor_index = monitor_index
    
    def set_fps(self, fps: int):
        """设置帧率"""
        self.fps = max(1, min(fps, 120))  # 限制在1-120之间
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        if self.region:
            return self.region['width'], self.region['height']
        
        monitor = self.sct.monitors[self.monitor_index] if self.monitor_index < len(self.sct.monitors) else self.sct.monitors[1]
        return monitor['width'], monitor['height']
    
    def _get_thread_sct(self):
        """获取线程本地的mss对象"""
        # 在捕获线程中，使用独立的mss对象避免线程本地存储问题
        if threading.current_thread() != threading.main_thread():
            if self._thread_local_sct is None:
                self._thread_local_sct = mss.mss()
            return self._thread_local_sct
        else:
            return self.sct
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """捕获单帧"""
        try:
            # 使用线程安全的mss对象
            sct = self._get_thread_sct()
            
            if self.region:
                # 捕获指定区域
                screenshot = sct.grab(self.region)
            else:
                # 捕获整个显示器
                monitor = sct.monitors[self.monitor_index] if self.monitor_index < len(sct.monitors) else sct.monitors[1]
                screenshot = sct.grab(monitor)
            
            # 转换为numpy数组
            frame = np.array(screenshot)
            
            # 转换颜色格式 BGRA -> BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            return frame
            
        except Exception as e:
            self.error_occurred.emit(f"捕获帧失败: {str(e)}")
            return None
    
    def _capture_loop(self):
        """捕获循环（在单独线程中运行）"""
        frame_interval = 1.0 / self.fps
        last_time = time.time()
        
        while self.is_capturing:
            current_time = time.time()
            
            # 控制帧率
            if current_time - last_time >= frame_interval:
                frame = self.capture_frame()
                if frame is not None:
                    self.frame_captured.emit(frame)
                last_time = current_time
            else:
                # 短暂休眠以避免CPU占用过高
                time.sleep(0.001)
    
    def start_capture(self):
        """开始捕获"""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self.capture_started.emit()
    
    def stop_capture(self):
        """停止捕获"""
        if not self.is_capturing:
            return
        
        self.is_capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        # 清理线程本地的mss对象
        if self._thread_local_sct is not None:
            try:
                self._thread_local_sct.close()
            except:
                pass
            self._thread_local_sct = None
        
        self.capture_stopped.emit()
    
    def take_screenshot(self, save_path: str = None) -> Optional[np.ndarray]:
        """截图"""
        frame = self.capture_frame()
        if frame is not None and save_path:
            cv2.imwrite(save_path, frame)
        return frame

class RegionSelector(QObject):
    """区域选择器"""
    
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    
    def __init__(self):
        super().__init__()
        self.selecting = False
    
    def start_selection(self):
        """开始区域选择"""
        # 这里需要实现一个覆盖整个屏幕的透明窗口
        # 让用户可以拖拽选择区域
        # 由于篇幅限制，这里先提供接口
        pass
    
    def get_selection_window(self):
        """获取选择窗口（需要在UI模块中实现）"""
        pass
