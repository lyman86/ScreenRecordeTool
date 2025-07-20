#!/usr/bin/env python3
"""
修复macOS特有问题的综合解决方案
"""

import os
import sys
import subprocess
import platform
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

def fix_ffmpeg_path_issue():
    """修复FFmpeg路径问题"""
    print("🔧 修复FFmpeg路径问题...")
    
    try:
        # 检查是否有ffmpeg-python但找不到ffmpeg二进制
        try:
            import ffmpeg
            print("✅ ffmpeg-python库已安装")
        except ImportError:
            print("❌ ffmpeg-python库未安装")
            return False
        
        # 检查系统FFmpeg
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            print(f"✅ 系统FFmpeg路径: {ffmpeg_path}")
            return True
        
        # 检查常见安装位置
        possible_paths = [
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',
            str(Path.home() / '.local' / 'bin' / 'ffmpeg'),
            '/usr/bin/ffmpeg'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                print(f"✅ 找到FFmpeg: {path}")
                # 添加到PATH
                bin_dir = str(Path(path).parent)
                current_path = os.environ.get('PATH', '')
                if bin_dir not in current_path:
                    os.environ['PATH'] = f"{bin_dir}:{current_path}"
                    print(f"✅ 已添加到PATH: {bin_dir}")
                return True
        
        # 如果都没找到，尝试下载安装
        print("⚠️ 未找到FFmpeg，尝试下载安装...")
        return download_ffmpeg_macos()
        
    except Exception as e:
        print(f"❌ 修复FFmpeg路径失败: {e}")
        return False

def download_ffmpeg_macos():
    """下载macOS版FFmpeg"""
    try:
        print("📥 下载FFmpeg for macOS...")
        
        # 创建本地bin目录
        local_bin = Path.home() / '.local' / 'bin'
        local_bin.mkdir(parents=True, exist_ok=True)
        
        # 下载FFmpeg
        temp_dir = Path(tempfile.mkdtemp())
        ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.0.zip"
        zip_path = temp_dir / "ffmpeg.zip"
        
        print("正在下载...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # 解压
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 移动到本地bin
        ffmpeg_bin = temp_dir / "ffmpeg"
        target_path = local_bin / "ffmpeg"
        
        if ffmpeg_bin.exists():
            shutil.move(str(ffmpeg_bin), str(target_path))
            target_path.chmod(0o755)
            
            # 添加到PATH
            os.environ['PATH'] = f"{local_bin}:{os.environ.get('PATH', '')}"
            
            print(f"✅ FFmpeg已安装到: {target_path}")
            return True
        else:
            print("❌ 下载的文件中未找到FFmpeg")
            return False
            
    except Exception as e:
        print(f"❌ 下载FFmpeg失败: {e}")
        return False

def fix_region_selector_macos():
    """修复macOS区域选择器问题"""
    print("🖥️ 修复区域选择器...")
    
    region_selector_path = Path(__file__).parent / "src" / "ui" / "region_selector.py"
    
    if not region_selector_path.exists():
        print("❌ 区域选择器文件不存在")
        return False
    
    try:
        # 读取文件
        with open(region_selector_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经修复
        if 'macOS区域选择修复' in content:
            print("✅ 区域选择器已经修复")
            return True
        
        # 添加macOS特殊处理
        macos_fix = '''
    def showEvent(self, event):
        """显示事件 - macOS区域选择修复"""
        super().showEvent(event)
        
        import platform
        if platform.system() == "Darwin":
            # macOS特殊处理
            self._setup_macos_region_selector()
        else:
            self._setup_display()
    
    def _setup_macos_region_selector(self):
        """macOS区域选择器设置"""
        from PyQt6.QtCore import QTimer
        
        # 延迟设置以避免黑屏
        QTimer.singleShot(200, self._macos_delayed_setup)
    
    def _macos_delayed_setup(self):
        """macOS延迟设置"""
        try:
            # 强制窗口属性
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |
                Qt.WindowType.BypassWindowManagerHint
            )
            
            # 获取主屏幕几何
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            
            print(f"macOS屏幕几何: {screen_geometry.width()}x{screen_geometry.height()}")
            
            # 设置窗口几何为屏幕大小
            self.setGeometry(screen_geometry)
            
            # 强制显示和激活
            self.show()
            self.raise_()
            self.activateWindow()
            
            # 设置提示标签位置
            if hasattr(self, 'hint_label'):
                label_x = (screen_geometry.width() - self.hint_label.width()) // 2
                label_y = 50
                self.hint_label.move(label_x, label_y)
            
            print("✅ macOS区域选择器设置完成")
            
        except Exception as e:
            print(f"❌ macOS区域选择器设置失败: {e}")
    
    def _convert_to_physical_coordinates(self, logical_rect):
        """将逻辑坐标转换为物理坐标 - macOS优化"""
        try:
            # 获取屏幕信息
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            
            # macOS特殊处理：直接使用逻辑坐标
            if platform.system() == "Darwin":
                # 在macOS上，通常不需要DPI缩放转换
                physical_x = logical_rect.x()
                physical_y = logical_rect.y()
                physical_width = logical_rect.width()
                physical_height = logical_rect.height()
                
                print(f"macOS坐标转换: ({physical_x}, {physical_y}, {physical_width}, {physical_height})")
                
                from PyQt6.QtCore import QRect
                return QRect(physical_x, physical_y, physical_width, physical_height)
            else:
                # 其他系统使用原来的逻辑
                scale = self.device_pixel_ratio
                physical_x = int(logical_rect.x() * scale)
                physical_y = int(logical_rect.y() * scale)
                physical_width = int(logical_rect.width() * scale)
                physical_height = int(logical_rect.height() * scale)
                
                from PyQt6.QtCore import QRect
                return QRect(physical_x, physical_y, physical_width, physical_height)
                
        except Exception as e:
            print(f"坐标转换错误: {e}")
            from PyQt6.QtCore import QRect
            return QRect(logical_rect.x(), logical_rect.y(), logical_rect.width(), logical_rect.height())'''
        
        # 替换原来的方法
        import re
        
        # 替换showEvent方法
        pattern = r'def showEvent\(self, event\):.*?(?=\n    def|\nclass|\Z)'
        new_content = re.sub(pattern, macos_fix.strip(), content, flags=re.DOTALL)
        
        # 添加platform导入
        if 'import platform' not in new_content:
            new_content = new_content.replace('import sys', 'import sys\nimport platform')
        
        # 添加标记
        new_content = '# macOS区域选择修复\n' + new_content
        
        # 写回文件
        with open(region_selector_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 区域选择器macOS修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复区域选择器失败: {e}")
        return False

def fix_audio_recording_macos():
    """修复macOS音频录制问题"""
    print("🎵 修复音频录制...")
    
    try:
        # 检查音频权限
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        # 尝试创建音频流测试
        try:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            # 读取一小段数据
            data = stream.read(1024, exception_on_overflow=False)
            stream.close()
            
            if len(data) > 0:
                print("✅ 音频录制权限正常")
                audio.terminate()
                return True
            else:
                print("⚠️ 音频数据为空，可能权限有问题")
                
        except Exception as e:
            print(f"⚠️ 音频流创建失败: {e}")
        
        audio.terminate()
        
        # 显示权限设置指南
        print("\n💡 macOS音频权限设置:")
        print("1. 系统偏好设置 > 安全性与隐私 > 隐私")
        print("2. 选择 '麦克风'")
        print("3. 添加 Python 或 终端 到允许列表")
        print("4. 重启应用程序")
        
        return False
        
    except Exception as e:
        print(f"❌ 音频录制检查失败: {e}")
        return False

def create_ffmpeg_wrapper():
    """创建FFmpeg包装脚本"""
    print("📝 创建FFmpeg包装脚本...")
    
    try:
        wrapper_path = Path(__file__).parent / "ffmpeg_wrapper.py"
        
        wrapper_content = '''#!/usr/bin/env python3
"""
FFmpeg包装器 - 解决macOS路径问题
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_ffmpeg():
    """查找FFmpeg二进制文件"""
    # 检查PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # 检查常见位置
    possible_paths = [
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
        str(Path.home() / '.local' / 'bin' / 'ffmpeg'),
        '/usr/bin/ffmpeg'
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return None

def run_ffmpeg(args):
    """运行FFmpeg命令"""
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found")
    
    cmd = [ffmpeg_path] + args
    return subprocess.run(cmd, capture_output=True, text=True)

if __name__ == "__main__":
    try:
        result = run_ffmpeg(sys.argv[1:])
        sys.exit(result.returncode)
    except Exception as e:
        print(f"FFmpeg wrapper error: {e}", file=sys.stderr)
        sys.exit(1)
'''
        
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        wrapper_path.chmod(0o755)
        print(f"✅ FFmpeg包装器已创建: {wrapper_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建FFmpeg包装器失败: {e}")
        return False

def main():
    """主函数"""
    print("🍎 macOS特有问题修复工具")
    print("="*50)
    
    if platform.system() != "Darwin":
        print("❌ 此工具仅适用于macOS系统")
        return 1
    
    fixes = [
        ("FFmpeg路径问题", fix_ffmpeg_path_issue),
        ("区域选择器", fix_region_selector_macos),
        ("音频录制", fix_audio_recording_macos),
        ("FFmpeg包装器", create_ffmpeg_wrapper),
    ]
    
    success_count = 0
    total_fixes = len(fixes)
    
    for fix_name, fix_func in fixes:
        print(f"\n🔧 {fix_name}:")
        if fix_func():
            success_count += 1
        else:
            print(f"   ⚠️ {fix_name}修复未完全成功")
    
    print("\n" + "="*50)
    print(f"📊 修复结果: {success_count}/{total_fixes} 项成功")
    
    if success_count >= 3:
        print("🎉 主要问题已修复！")
        print("✨ 建议重启应用程序测试:")
        print("   ./run_app.sh")
        print("\n💡 如果仍有问题，请检查系统权限设置")
    else:
        print("⚠️ 部分问题需要手动处理")
    
    return 0 if success_count >= 3 else 1

if __name__ == "__main__":
    sys.exit(main())
