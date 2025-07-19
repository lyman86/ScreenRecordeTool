"""
跨平台工具模块
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PlatformUtils:
    """平台工具类"""
    
    @staticmethod
    def get_platform() -> str:
        """获取当前平台"""
        system = platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def is_windows() -> bool:
        """是否为Windows平台"""
        return PlatformUtils.get_platform() == "windows"
    
    @staticmethod
    def is_macos() -> bool:
        """是否为macOS平台"""
        return PlatformUtils.get_platform() == "macos"
    
    @staticmethod
    def is_linux() -> bool:
        """是否为Linux平台"""
        return PlatformUtils.get_platform() == "linux"
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """获取系统信息"""
        return {
            "platform": PlatformUtils.get_platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
    
    @staticmethod
    def get_default_paths() -> Dict[str, str]:
        """获取平台默认路径"""
        home = Path.home()
        
        if PlatformUtils.is_windows():
            return {
                "documents": str(home / "Documents"),
                "videos": str(home / "Videos"),
                "pictures": str(home / "Pictures"),
                "desktop": str(home / "Desktop"),
                "downloads": str(home / "Downloads"),
                "appdata": str(Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))),
                "temp": str(Path(os.environ.get("TEMP", home / "AppData" / "Local" / "Temp")))
            }
        elif PlatformUtils.is_macos():
            return {
                "documents": str(home / "Documents"),
                "videos": str(home / "Movies"),
                "pictures": str(home / "Pictures"),
                "desktop": str(home / "Desktop"),
                "downloads": str(home / "Downloads"),
                "appdata": str(home / "Library" / "Application Support"),
                "temp": "/tmp"
            }
        else:  # Linux
            return {
                "documents": str(home / "Documents"),
                "videos": str(home / "Videos"),
                "pictures": str(home / "Pictures"),
                "desktop": str(home / "Desktop"),
                "downloads": str(home / "Downloads"),
                "appdata": str(home / ".config"),
                "temp": "/tmp"
            }
    
    @staticmethod
    def get_app_data_dir(app_name: str) -> str:
        """获取应用数据目录"""
        paths = PlatformUtils.get_default_paths()
        app_data_dir = Path(paths["appdata"]) / app_name
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return str(app_data_dir)
    
    @staticmethod
    def get_executable_extension() -> str:
        """获取可执行文件扩展名"""
        return ".exe" if PlatformUtils.is_windows() else ""
    
    @staticmethod
    def open_file_manager(path: str):
        """打开文件管理器"""
        try:
            if PlatformUtils.is_windows():
                os.startfile(path)
            elif PlatformUtils.is_macos():
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            print(f"无法打开文件管理器: {e}")
    
    @staticmethod
    def open_url(url: str):
        """打开URL"""
        try:
            if PlatformUtils.is_windows():
                os.startfile(url)
            elif PlatformUtils.is_macos():
                subprocess.run(["open", url])
            else:  # Linux
                subprocess.run(["xdg-open", url])
        except Exception as e:
            print(f"无法打开URL: {e}")

class PermissionManager:
    """权限管理器"""
    
    @staticmethod
    def check_screen_recording_permission() -> bool:
        """检查屏幕录制权限"""
        if PlatformUtils.is_macos():
            return PermissionManager._check_macos_screen_recording()
        else:
            # Windows和Linux通常不需要特殊权限
            return True
    
    @staticmethod
    def request_screen_recording_permission() -> bool:
        """请求屏幕录制权限"""
        if PlatformUtils.is_macos():
            return PermissionManager._request_macos_screen_recording()
        else:
            return True
    
    @staticmethod
    def check_microphone_permission() -> bool:
        """检查麦克风权限"""
        if PlatformUtils.is_macos():
            return PermissionManager._check_macos_microphone()
        else:
            return True
    
    @staticmethod
    def request_microphone_permission() -> bool:
        """请求麦克风权限"""
        if PlatformUtils.is_macos():
            return PermissionManager._request_macos_microphone()
        else:
            return True
    
    @staticmethod
    def _check_macos_screen_recording() -> bool:
        """检查macOS屏幕录制权限"""
        try:
            # 尝试捕获屏幕来检查权限
            import mss
            with mss.mss() as sct:
                sct.grab(sct.monitors[1])
            return True
        except Exception:
            return False
    
    @staticmethod
    def _request_macos_screen_recording() -> bool:
        """请求macOS屏幕录制权限"""
        try:
            # 打开系统偏好设置的隐私页面
            subprocess.run([
                "open", 
                "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
            ])
            return True
        except Exception:
            return False
    
    @staticmethod
    def _check_macos_microphone() -> bool:
        """检查macOS麦克风权限"""
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            # 尝试打开音频流
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            stream.close()
            audio.terminate()
            return True
        except Exception:
            return False
    
    @staticmethod
    def _request_macos_microphone() -> bool:
        """请求macOS麦克风权限"""
        try:
            # 打开系统偏好设置的隐私页面
            subprocess.run([
                "open", 
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
            ])
            return True
        except Exception:
            return False

class SystemTrayManager:
    """系统托盘管理器"""
    
    @staticmethod
    def is_supported() -> bool:
        """检查系统托盘是否支持"""
        from PyQt6.QtWidgets import QSystemTrayIcon
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    @staticmethod
    def get_icon_path() -> str:
        """获取托盘图标路径"""
        # 根据平台返回不同的图标
        if PlatformUtils.is_windows():
            return "resources/icon.ico"
        elif PlatformUtils.is_macos():
            return "resources/icon.icns"
        else:
            return "resources/icon.png"

class HotkeySupport:
    """快捷键支持检查"""
    
    @staticmethod
    def is_global_hotkey_supported() -> bool:
        """检查是否支持全局快捷键"""
        try:
            import keyboard
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_modifier_key() -> str:
        """获取平台特定的修饰键"""
        if PlatformUtils.is_macos():
            return "cmd"
        else:
            return "ctrl"
    
    @staticmethod
    def normalize_hotkey(hotkey: str) -> str:
        """标准化快捷键"""
        # 替换平台特定的修饰键
        if "meta" in hotkey.lower():
            platform_key = HotkeySupport.get_modifier_key()
            hotkey = hotkey.lower().replace("meta", platform_key)
        
        return hotkey

class AudioDeviceManager:
    """音频设备管理器"""
    
    @staticmethod
    def get_audio_devices() -> List[Dict]:
        """获取音频设备列表"""
        devices = []
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
            
            audio.terminate()
        except Exception as e:
            print(f"获取音频设备失败: {e}")
        
        return devices
    
    @staticmethod
    def get_default_audio_device() -> Optional[Dict]:
        """获取默认音频设备"""
        devices = AudioDeviceManager.get_audio_devices()
        return devices[0] if devices else None

class DisplayManager:
    """显示器管理器"""
    
    @staticmethod
    def get_displays() -> List[Dict]:
        """获取显示器列表"""
        displays = []
        try:
            import mss
            with mss.mss() as sct:
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # 跳过第一个（所有显示器的组合）
                        continue
                    displays.append({
                        'index': i,
                        'left': monitor['left'],
                        'top': monitor['top'],
                        'width': monitor['width'],
                        'height': monitor['height'],
                        'name': f"显示器 {i}"
                    })
        except Exception as e:
            print(f"获取显示器信息失败: {e}")
        
        return displays
    
    @staticmethod
    def get_primary_display() -> Optional[Dict]:
        """获取主显示器"""
        displays = DisplayManager.get_displays()
        return displays[0] if displays else None
    
    @staticmethod
    def get_display_scale_factor() -> float:
        """获取显示器缩放因子"""
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                return screen.devicePixelRatio()
        except Exception:
            pass
        return 1.0

class FileAssociationManager:
    """文件关联管理器"""
    
    @staticmethod
    def register_file_associations():
        """注册文件关联"""
        if PlatformUtils.is_windows():
            FileAssociationManager._register_windows_associations()
        elif PlatformUtils.is_macos():
            FileAssociationManager._register_macos_associations()
    
    @staticmethod
    def _register_windows_associations():
        """注册Windows文件关联"""
        # Windows文件关联需要修改注册表
        # 这里提供基本框架，实际实现需要更多代码
        pass
    
    @staticmethod
    def _register_macos_associations():
        """注册macOS文件关联"""
        # macOS文件关联通过Info.plist配置
        # 这里提供基本框架
        pass

def get_platform_specific_config() -> Dict:
    """获取平台特定配置"""
    config = {
        "platform": PlatformUtils.get_platform(),
        "paths": PlatformUtils.get_default_paths(),
        "permissions": {
            "screen_recording": PermissionManager.check_screen_recording_permission(),
            "microphone": PermissionManager.check_microphone_permission()
        },
        "features": {
            "system_tray": SystemTrayManager.is_supported(),
            "global_hotkeys": HotkeySupport.is_global_hotkey_supported()
        },
        "devices": {
            "audio": AudioDeviceManager.get_audio_devices(),
            "displays": DisplayManager.get_displays()
        }
    }
    
    return config
