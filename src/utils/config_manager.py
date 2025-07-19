"""
配置管理器
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from .platform_utils import PlatformUtils
from config.settings import AppConfig

class ConfigManager(QObject):
    """配置管理器"""
    
    config_changed = pyqtSignal(str, object)  # 配置项改变信号
    
    def __init__(self, app_name: str = "ScreenRecorder"):
        super().__init__()
        self.app_name = app_name
        self.config_dir = PlatformUtils.get_app_data_dir(app_name)
        self.config_file = Path(self.config_dir) / "config.json"
        self.config_data = {}
        
        # 加载配置
        self.load_config()
    
    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_file)
    
    def load_config(self):
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # 创建默认配置
                self.config_data = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config_data = self.get_default_config()
    
    def save_config(self):
        """保存配置"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "1.0.0",
            "recording": {
                "fps": AppConfig.DEFAULT_FPS,
                "quality": AppConfig.DEFAULT_QUALITY,
                "format": AppConfig.DEFAULT_FORMAT,
                "audio_enabled": AppConfig.DEFAULT_AUDIO_ENABLED,
                "cursor_enabled": AppConfig.DEFAULT_CURSOR_ENABLED,
                "audio_quality": "高质量",
                "auto_save": True
            },
            "ui": {
                "theme": "浅色主题",
                "language": "简体中文",
                "minimize_to_tray": True,
                "show_preview": True,
                "window_geometry": None
            },
            "hotkeys": {
                "start_stop": "f9",
                "pause_resume": "f10",
                "screenshot": "f11",
                "select_region": "ctrl+shift+a",
                "show_hide": "ctrl+shift+r",
                "enabled": True
            },
            "paths": {
                "output_directory": AppConfig.get_default_output_dir(),
                "filename_template": "录屏_{timestamp}",
                "temp_directory": AppConfig.get_temp_dir()
            },
            "advanced": {
                "hardware_acceleration": True,
                "multithread_encoding": True,
                "buffer_size_mb": 10,
                "max_fps": 60,
                "auto_cleanup_temp": True
            },
            "permissions": {
                "screen_recording_granted": False,
                "microphone_granted": False,
                "notifications_enabled": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config_data
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        # 保存配置
        self.save_config()
        
        # 发出信号
        if old_value != value:
            self.config_changed.emit(key, value)
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config_data = self.get_default_config()
        self.save_config()
    
    def reset_section(self, section: str):
        """重置指定部分的配置"""
        default_config = self.get_default_config()
        if section in default_config:
            self.config_data[section] = default_config[section]
            self.save_config()
    
    def export_config(self, file_path: str) -> bool:
        """导出配置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证配置格式
            if self.validate_config(imported_config):
                self.config_data = imported_config
                self.save_config()
                return True
            else:
                print("配置文件格式无效")
                return False
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def validate_config(self, config: Dict) -> bool:
        """验证配置格式"""
        required_sections = ["recording", "ui", "hotkeys", "paths", "advanced"]
        
        try:
            for section in required_sections:
                if section not in config:
                    return False
            return True
        except Exception:
            return False
    
    def get_recording_config(self) -> Dict[str, Any]:
        """获取录制配置"""
        return self.get("recording", {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.get("ui", {})
    
    def get_hotkey_config(self) -> Dict[str, Any]:
        """获取快捷键配置"""
        return self.get("hotkeys", {})
    
    def get_path_config(self) -> Dict[str, Any]:
        """获取路径配置"""
        return self.get("paths", {})
    
    def get_advanced_config(self) -> Dict[str, Any]:
        """获取高级配置"""
        return self.get("advanced", {})
    
    def update_recording_config(self, config: Dict[str, Any]):
        """更新录制配置"""
        for key, value in config.items():
            self.set(f"recording.{key}", value)
    
    def update_ui_config(self, config: Dict[str, Any]):
        """更新UI配置"""
        for key, value in config.items():
            self.set(f"ui.{key}", value)
    
    def update_hotkey_config(self, config: Dict[str, Any]):
        """更新快捷键配置"""
        for key, value in config.items():
            self.set(f"hotkeys.{key}", value)
    
    def update_path_config(self, config: Dict[str, Any]):
        """更新路径配置"""
        for key, value in config.items():
            self.set(f"paths.{key}", value)
    
    def update_advanced_config(self, config: Dict[str, Any]):
        """更新高级配置"""
        for key, value in config.items():
            self.set(f"advanced.{key}", value)
    
    def backup_config(self) -> bool:
        """备份配置"""
        try:
            backup_file = self.config_file.with_suffix('.backup.json')
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"备份配置失败: {e}")
            return False
    
    def restore_config(self) -> bool:
        """恢复配置"""
        try:
            backup_file = self.config_file.with_suffix('.backup.json')
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self.save_config()
                return True
            else:
                print("备份文件不存在")
                return False
        except Exception as e:
            print(f"恢复配置失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "config_file": str(self.config_file),
            "config_dir": self.config_dir,
            "file_exists": self.config_file.exists(),
            "file_size": self.config_file.stat().st_size if self.config_file.exists() else 0,
            "version": self.get("version", "unknown")
        }

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config(key: str, default: Any = None) -> Any:
    """快捷方式：获取配置值"""
    return get_config_manager().get(key, default)

def set_config(key: str, value: Any):
    """快捷方式：设置配置值"""
    get_config_manager().set(key, value)

def save_config():
    """快捷方式：保存配置"""
    get_config_manager().save_config()
