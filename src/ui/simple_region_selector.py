"""
简化的区域选择器 - 专门针对macOS优化
"""

import sys
import platform
from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap
import mss

class SimpleRegionSelector(QWidget):
    """简化的区域选择器"""
    
    # 信号
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    selection_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # 选择状态
        self.selecting = False
        self.start_pos = None
        self.current_pos = None
        self.selection_rect = QRect()
        
        # 屏幕信息
        self.screen_info = self._get_screen_info()
        
        self._setup_window()
        self._create_ui()
    
    def _get_screen_info(self):
        """获取屏幕信息"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                return {
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor.get('left', 0),
                    'top': monitor.get('top', 0)
                }
        except:
            # 默认值
            return {'width': 1440, 'height': 900, 'left': 0, 'top': 0}
    
    def _setup_window(self):
        """设置窗口属性"""
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if platform.system() == "Darwin":
            # macOS特殊设置
            self.setWindowOpacity(0.01)  # 几乎完全透明
        else:
            self.setWindowOpacity(0.3)
        
        # 设置窗口大小为屏幕大小
        self.setGeometry(0, 0, self.screen_info['width'], self.screen_info['height'])
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        
        print(f"简化选择器设置: {self.screen_info['width']}x{self.screen_info['height']}")
    
    def _create_ui(self):
        """创建UI元素"""
        # 提示标签
        self.hint_label = QLabel("按住鼠标左键拖拽选择录制区域，按ESC取消", self)
        self.hint_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.hint_label.adjustSize()
        
        # 居中显示提示
        self.hint_label.move(
            (self.screen_info['width'] - self.hint_label.width()) // 2,
            30
        )
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        
        # 强制窗口到前台
        self.raise_()
        self.activateWindow()
        
        if platform.system() == "Darwin":
            # macOS延迟设置，确保窗口正确显示
            QTimer.singleShot(100, self._macos_final_setup)
    
    def _macos_final_setup(self):
        """macOS最终设置"""
        try:
            # 重新设置窗口属性
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |
                Qt.WindowType.BypassWindowManagerHint
            )
            
            # 设置为半透明，让用户能看到桌面
            self.setWindowOpacity(0.1)
            
            # 确保窗口覆盖整个屏幕
            self.setGeometry(0, 0, self.screen_info['width'], self.screen_info['height'])
            
            # 强制显示
            self.show()
            self.raise_()
            self.activateWindow()
            
            print("macOS最终设置完成")
            
        except Exception as e:
            print(f"macOS设置失败: {e}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selecting = True
            self.start_pos = event.position().toPoint()
            self.current_pos = self.start_pos
            self.selection_rect = QRect()
            
            # 隐藏提示标签
            self.hint_label.hide()
            
            print(f"开始选择: {self.start_pos}")
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.selecting and self.start_pos:
            self.current_pos = event.position().toPoint()
            
            # 计算选择矩形
            self.selection_rect = QRect(
                min(self.start_pos.x(), self.current_pos.x()),
                min(self.start_pos.y(), self.current_pos.y()),
                abs(self.current_pos.x() - self.start_pos.x()),
                abs(self.current_pos.y() - self.start_pos.y())
            )
            
            # 重绘
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                # 选择有效，发送信号
                x = self.selection_rect.x()
                y = self.selection_rect.y()
                width = self.selection_rect.width()
                height = self.selection_rect.height()
                
                print(f"选择完成: ({x}, {y}, {width}, {height})")
                
                # 发送选择结果
                self.region_selected.emit(x, y, width, height)
                
                # 关闭窗口
                self.close()
            else:
                # 选择太小，重置
                self.selection_rect = QRect()
                self.hint_label.show()
                self.update()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            # ESC取消选择
            print("用户取消选择")
            self.selection_cancelled.emit()
            self.close()
        
        super().keyPressEvent(event)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        if platform.system() == "Darwin":
            # macOS使用更轻的遮罩
            painter.fillRect(self.rect(), QColor(0, 0, 0, 20))
        else:
            # 其他系统使用标准遮罩
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # 绘制选择区域
        if not self.selection_rect.isEmpty():
            # 清除选择区域的遮罩
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.selection_rect, QColor(0, 0, 0, 0))
            
            # 绘制选择框边框
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            
            # 绘制尺寸信息
            if self.selection_rect.width() > 50 and self.selection_rect.height() > 30:
                size_text = f"{self.selection_rect.width()} × {self.selection_rect.height()}"
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                
                # 计算文本位置
                text_x = self.selection_rect.x() + 5
                text_y = self.selection_rect.y() - 5
                
                # 确保文本在屏幕内
                if text_y < 20:
                    text_y = self.selection_rect.y() + 20
                
                # 绘制文本背景
                text_rect = painter.fontMetrics().boundingRect(size_text)
                bg_rect = QRect(text_x - 3, text_y - text_rect.height() - 3, 
                               text_rect.width() + 6, text_rect.height() + 6)
                painter.fillRect(bg_rect, QColor(0, 0, 0, 180))
                
                # 绘制文本
                painter.drawText(text_x, text_y, size_text)

class RegionSelectorManager:
    """区域选择器管理器"""
    
    def __init__(self):
        self.selector = None
    
    def select_region(self, callback):
        """开始区域选择"""
        try:
            # 创建选择器
            self.selector = SimpleRegionSelector()
            
            # 连接信号
            self.selector.region_selected.connect(callback)
            self.selector.selection_cancelled.connect(lambda: callback(None))
            
            # 显示选择器
            self.selector.show()
            
            return True
            
        except Exception as e:
            print(f"启动区域选择器失败: {e}")
            return False
    
    def close_selector(self):
        """关闭选择器"""
        if self.selector:
            self.selector.close()
            self.selector = None
