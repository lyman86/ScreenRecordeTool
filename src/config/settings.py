"""
应用程序配置设置
"""
import os
import platform
from pathlib import Path

class AppConfig:
    """应用程序配置类"""
    
    # 应用信息
    APP_NAME = "现代录屏工具"
    APP_VERSION = "1.1.0"
    APP_AUTHOR = "Your Company"
    
    # 默认设置
    DEFAULT_FPS = 30
    DEFAULT_QUALITY = "高质量"
    DEFAULT_FORMAT = "MP4"
    DEFAULT_AUDIO_ENABLED = True
    DEFAULT_CURSOR_ENABLED = True
    
    # 支持的视频格式
    SUPPORTED_FORMATS = ["MP4", "AVI", "MOV", "WebM"]
    
    # 质量设置
    QUALITY_SETTINGS = {
        "低质量": {"bitrate": "1M", "crf": 28},
        "中等质量": {"bitrate": "2M", "crf": 23},
        "高质量": {"bitrate": "4M", "crf": 18},
        "超高质量": {"bitrate": "8M", "crf": 15}
    }
    
    # FPS选项
    FPS_OPTIONS = [15, 24, 30, 60]
    
    # 快捷键
    HOTKEYS = {
        "start_stop": "F9",
        "pause_resume": "F10",
        "screenshot": "F11"
    }
    
    @staticmethod
    def get_default_output_dir():
        """获取默认输出目录"""
        if platform.system() == "Windows":
            return str(Path.home() / "Videos" / "ScreenRecorder")
        else:  # macOS/Linux
            return str(Path.home() / "Movies" / "ScreenRecorder")
    
    @staticmethod
    def get_temp_dir():
        """获取临时文件目录"""
        return str(Path.home() / ".screenrecorder" / "temp")
    
    @staticmethod
    def ensure_directories():
        """确保必要的目录存在"""
        dirs = [
            AppConfig.get_default_output_dir(),
            AppConfig.get_temp_dir()
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

class UIConfig:
    """UI配置类"""
    
    # 窗口设置
    MAIN_WINDOW_SIZE = (800, 600)
    MIN_WINDOW_SIZE = (600, 400)
    
    # 颜色主题
    COLORS = {
        "primary": "#2196F3",
        "secondary": "#FFC107",
        "success": "#4CAF50",
        "danger": "#F44336",
        "warning": "#FF9800",
        "info": "#00BCD4",
        "light": "#F8F9FA",
        "dark": "#343A40"
    }
    
    # 字体设置
    FONTS = {
        "default": "Segoe UI" if platform.system() == "Windows" else "SF Pro Display",
        "monospace": "Consolas" if platform.system() == "Windows" else "SF Mono"
    }
    
    # 图标大小
    ICON_SIZES = {
        "small": 16,
        "medium": 24,
        "large": 32,
        "xlarge": 48
    }
