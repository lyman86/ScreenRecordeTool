"""
全局快捷键管理器
"""

import platform
from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("警告: keyboard库未安装，快捷键功能将不可用")

class HotkeyManager(QObject):
    """全局快捷键管理器"""
    
    # 信号
    hotkey_triggered = pyqtSignal(str)  # 快捷键触发
    
    def __init__(self):
        super().__init__()
        self.hotkeys: Dict[str, Callable] = {}
        self.registered_keys = set()
        self.enabled = KEYBOARD_AVAILABLE
        
        if not self.enabled:
            print("快捷键管理器初始化失败：缺少依赖库")
    
    def register_hotkey(self, key_combination: str, callback: Callable, description: str = ""):
        """注册全局快捷键"""
        if not self.enabled:
            return False
        
        try:
            # 如果已经注册过，先取消注册
            if key_combination in self.registered_keys:
                self.unregister_hotkey(key_combination)
            
            # 注册新的快捷键
            keyboard.add_hotkey(key_combination, self._on_hotkey_triggered, args=[key_combination, callback])
            self.hotkeys[key_combination] = callback
            self.registered_keys.add(key_combination)
            
            print(f"已注册快捷键: {key_combination} - {description}")
            return True
            
        except Exception as e:
            print(f"注册快捷键失败 {key_combination}: {str(e)}")
            return False
    
    def unregister_hotkey(self, key_combination: str):
        """取消注册快捷键"""
        if not self.enabled:
            return
        
        try:
            if key_combination in self.registered_keys:
                keyboard.remove_hotkey(key_combination)
                self.registered_keys.remove(key_combination)
                if key_combination in self.hotkeys:
                    del self.hotkeys[key_combination]
                print(f"已取消快捷键: {key_combination}")
        except Exception as e:
            print(f"取消快捷键失败 {key_combination}: {str(e)}")
    
    def unregister_all(self):
        """取消所有快捷键"""
        if not self.enabled:
            return
        
        for key_combination in list(self.registered_keys):
            self.unregister_hotkey(key_combination)
    
    def _on_hotkey_triggered(self, key_combination: str, callback: Callable):
        """快捷键触发处理"""
        try:
            self.hotkey_triggered.emit(key_combination)
            if callback:
                callback()
        except Exception as e:
            print(f"快捷键回调执行失败 {key_combination}: {str(e)}")
    
    def is_enabled(self) -> bool:
        """检查快捷键管理器是否可用"""
        return self.enabled
    
    def get_registered_hotkeys(self) -> Dict[str, Callable]:
        """获取已注册的快捷键"""
        return self.hotkeys.copy()
    
    def set_enabled(self, enabled: bool):
        """启用/禁用快捷键管理器"""
        if not KEYBOARD_AVAILABLE:
            return
        
        if enabled and not self.enabled:
            self.enabled = True
            print("快捷键管理器已启用")
        elif not enabled and self.enabled:
            self.unregister_all()
            self.enabled = False
            print("快捷键管理器已禁用")

class DefaultHotkeys:
    """默认快捷键配置"""
    
    # 录制控制
    START_STOP_RECORDING = "f9"
    PAUSE_RESUME_RECORDING = "f10"
    TAKE_SCREENSHOT = "f11"
    
    # 区域选择
    SELECT_REGION = "ctrl+shift+a"
    
    # 窗口控制
    SHOW_HIDE_WINDOW = "ctrl+shift+r"
    
    @classmethod
    def get_all_hotkeys(cls) -> Dict[str, str]:
        """获取所有默认快捷键"""
        return {
            "start_stop": cls.START_STOP_RECORDING,
            "pause_resume": cls.PAUSE_RESUME_RECORDING,
            "screenshot": cls.TAKE_SCREENSHOT,
            "select_region": cls.SELECT_REGION,
            "show_hide": cls.SHOW_HIDE_WINDOW
        }
    
    @classmethod
    def get_descriptions(cls) -> Dict[str, str]:
        """获取快捷键描述"""
        return {
            "start_stop": "开始/停止录制",
            "pause_resume": "暂停/恢复录制",
            "screenshot": "截图",
            "select_region": "选择录制区域",
            "show_hide": "显示/隐藏主窗口"
        }

def get_platform_modifier_key() -> str:
    """获取平台特定的修饰键"""
    if platform.system() == "Darwin":  # macOS
        return "cmd"
    else:  # Windows/Linux
        return "ctrl"

def normalize_hotkey(hotkey: str) -> str:
    """标准化快捷键字符串"""
    # 替换平台特定的修饰键
    if "meta" in hotkey.lower():
        platform_key = get_platform_modifier_key()
        hotkey = hotkey.lower().replace("meta", platform_key)
    
    # 标准化格式
    parts = [part.strip().lower() for part in hotkey.split("+")]
    
    # 排序修饰键
    modifiers = []
    key = ""
    
    for part in parts:
        if part in ["ctrl", "alt", "shift", "cmd", "meta", "win"]:
            modifiers.append(part)
        else:
            key = part
    
    modifiers.sort()
    if key:
        modifiers.append(key)
    
    return "+".join(modifiers)

def is_valid_hotkey(hotkey: str) -> bool:
    """检查快捷键是否有效"""
    if not KEYBOARD_AVAILABLE:
        return False
    
    try:
        # 尝试解析快捷键
        keyboard.parse_hotkey(hotkey)
        return True
    except Exception:
        return False
