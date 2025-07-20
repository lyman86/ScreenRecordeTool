"""
FFmpeg管理器 - 检测、安装和管理FFmpeg
"""

import os
import sys
import subprocess
import platform
import tempfile
import urllib.request
import zipfile
import shutil
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox

class FFmpegInstaller(QThread):
    """FFmpeg安装器线程"""
    
    # 信号
    installation_started = pyqtSignal()
    installation_progress = pyqtSignal(str)  # 进度消息
    installation_finished = pyqtSignal(bool, str)  # 成功/失败, 消息
    
    def __init__(self):
        super().__init__()
        self.should_stop = False
    
    def run(self):
        """执行安装"""
        try:
            self.installation_started.emit()
            
            if platform.system() == "Darwin":
                success, message = self._install_macos()
            elif platform.system() == "Windows":
                success, message = self._install_windows()
            else:
                success, message = self._install_linux()
            
            self.installation_finished.emit(success, message)
            
        except Exception as e:
            self.installation_finished.emit(False, f"安装过程中发生错误: {str(e)}")
    
    def _install_macos(self):
        """在macOS上安装FFmpeg"""
        try:
            # 方法1: 尝试使用Homebrew
            self.installation_progress.emit("检查Homebrew...")
            
            try:
                result = subprocess.run(['brew', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.installation_progress.emit("使用Homebrew安装FFmpeg...")
                    result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                                          capture_output=True, text=True, timeout=600)
                    if result.returncode == 0:
                        return True, "FFmpeg通过Homebrew安装成功"
                    else:
                        self.installation_progress.emit("Homebrew安装失败，尝试下载预编译版本...")
                else:
                    self.installation_progress.emit("Homebrew不可用，尝试下载预编译版本...")
            except:
                self.installation_progress.emit("Homebrew不可用，尝试下载预编译版本...")
            
            # 方法2: 下载预编译二进制文件
            return self._download_precompiled_macos()
            
        except Exception as e:
            return False, f"macOS安装失败: {str(e)}"
    
    def _download_precompiled_macos(self):
        """下载macOS预编译FFmpeg"""
        try:
            self.installation_progress.emit("下载FFmpeg预编译版本...")
            
            # 创建临时目录
            temp_dir = Path(tempfile.mkdtemp())
            
            # 下载FFmpeg
            ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.0.zip"
            zip_path = temp_dir / "ffmpeg.zip"
            
            self.installation_progress.emit("正在下载...")
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # 解压
            self.installation_progress.emit("解压文件...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 查找FFmpeg二进制文件
            ffmpeg_bin = temp_dir / "ffmpeg"
            if not ffmpeg_bin.exists():
                return False, "下载的文件中未找到FFmpeg二进制文件"
            
            # 创建本地bin目录
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            
            # 复制到本地bin目录
            target_path = local_bin / "ffmpeg"
            shutil.copy2(ffmpeg_bin, target_path)
            target_path.chmod(0o755)
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            self.installation_progress.emit("安装完成")
            return True, f"FFmpeg已安装到 {target_path}"
            
        except Exception as e:
            return False, f"下载安装失败: {str(e)}"
    
    def _install_windows(self):
        """在Windows上安装FFmpeg"""
        try:
            self.installation_progress.emit("下载Windows版FFmpeg...")
            
            # 创建临时目录
            temp_dir = Path(tempfile.mkdtemp())
            
            # 下载FFmpeg
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = temp_dir / "ffmpeg.zip"
            
            self.installation_progress.emit("正在下载...")
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # 解压
            self.installation_progress.emit("解压文件...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 查找FFmpeg二进制文件
            ffmpeg_bin = None
            for root, dirs, files in os.walk(temp_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_bin = Path(root) / "ffmpeg.exe"
                    break
            
            if not ffmpeg_bin or not ffmpeg_bin.exists():
                return False, "下载的文件中未找到FFmpeg二进制文件"
            
            # 创建本地bin目录
            local_bin = Path.home() / "AppData" / "Local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            
            # 复制到本地bin目录
            target_path = local_bin / "ffmpeg.exe"
            shutil.copy2(ffmpeg_bin, target_path)
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            self.installation_progress.emit("安装完成")
            return True, f"FFmpeg已安装到 {target_path}"
            
        except Exception as e:
            return False, f"Windows安装失败: {str(e)}"
    
    def _install_linux(self):
        """在Linux上安装FFmpeg"""
        try:
            # 尝试使用包管理器
            self.installation_progress.emit("尝试使用系统包管理器...")
            
            # 检测发行版并使用相应的包管理器
            if shutil.which('apt'):
                cmd = ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', 'ffmpeg']
            elif shutil.which('yum'):
                cmd = ['sudo', 'yum', 'install', '-y', 'ffmpeg']
            elif shutil.which('dnf'):
                cmd = ['sudo', 'dnf', 'install', '-y', 'ffmpeg']
            elif shutil.which('pacman'):
                cmd = ['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg']
            else:
                return False, "未找到支持的包管理器"
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return True, "FFmpeg通过系统包管理器安装成功"
            else:
                return False, f"包管理器安装失败: {result.stderr}"
                
        except Exception as e:
            return False, f"Linux安装失败: {str(e)}"
    
    def stop_installation(self):
        """停止安装"""
        self.should_stop = True

class FFmpegManager(QObject):
    """FFmpeg管理器"""
    
    # 信号
    status_changed = pyqtSignal(bool, str)  # 状态改变: 是否可用, 版本信息
    
    def __init__(self):
        super().__init__()
        self.installer = None
        self._ffmpeg_available = False
        self._ffmpeg_version = ""
        self._ffmpeg_path = ""
    
    def check_ffmpeg_status(self):
        """检查FFmpeg状态"""
        try:
            # 检查ffmpeg-python库
            try:
                import ffmpeg
                # 尝试获取FFmpeg版本
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    self._ffmpeg_available = True
                    self._ffmpeg_version = version_line
                    self._ffmpeg_path = shutil.which('ffmpeg') or "系统路径"
                    self.status_changed.emit(True, version_line)
                    return True
            except:
                pass
            
            # 检查系统FFmpeg
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                result = subprocess.run([ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    self._ffmpeg_available = True
                    self._ffmpeg_version = version_line
                    self._ffmpeg_path = ffmpeg_path
                    self.status_changed.emit(True, version_line)
                    return True
            
            # 检查本地安装
            local_paths = [
                Path.home() / ".local" / "bin" / "ffmpeg",
                Path.home() / "AppData" / "Local" / "bin" / "ffmpeg.exe",
            ]
            
            for path in local_paths:
                if path.exists():
                    try:
                        result = subprocess.run([str(path), '-version'], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version_line = result.stdout.split('\n')[0]
                            self._ffmpeg_available = True
                            self._ffmpeg_version = version_line
                            self._ffmpeg_path = str(path)
                            self.status_changed.emit(True, version_line)
                            return True
                    except:
                        continue
            
            # FFmpeg不可用
            self._ffmpeg_available = False
            self._ffmpeg_version = ""
            self._ffmpeg_path = ""
            self.status_changed.emit(False, "FFmpeg未安装")
            return False
            
        except Exception as e:
            self._ffmpeg_available = False
            self._ffmpeg_version = ""
            self._ffmpeg_path = ""
            self.status_changed.emit(False, f"检查失败: {str(e)}")
            return False
    
    def install_ffmpeg(self):
        """安装FFmpeg"""
        if self.installer and self.installer.isRunning():
            return False
        
        self.installer = FFmpegInstaller()
        self.installer.installation_finished.connect(self._on_installation_finished)
        self.installer.start()
        return True
    
    def _on_installation_finished(self, success, message):
        """安装完成回调"""
        if success:
            # 重新检查状态
            self.check_ffmpeg_status()
        
        # 清理安装器
        if self.installer:
            self.installer.deleteLater()
            self.installer = None
    
    def is_available(self):
        """FFmpeg是否可用"""
        return self._ffmpeg_available
    
    def get_version(self):
        """获取FFmpeg版本"""
        return self._ffmpeg_version
    
    def get_path(self):
        """获取FFmpeg路径"""
        return self._ffmpeg_path
