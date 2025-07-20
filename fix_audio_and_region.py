#!/usr/bin/env python3
"""
修复macOS上的音频录制和区域选择问题
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def test_audio_recording():
    """测试音频录制功能"""
    print("🎵 测试音频录制功能...")
    
    try:
        import pyaudio
        import wave
        import tempfile
        import time
        
        # 创建临时文件
        temp_file = tempfile.mktemp(suffix='.wav')
        
        # 音频参数
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 2
        
        audio = pyaudio.PyAudio()
        
        print("开始录制音频测试...")
        
        # 打开音频流
        stream = audio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
        
        frames = []
        
        # 录制音频
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        
        print("录制完成，保存音频文件...")
        
        # 停止录制
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # 保存音频文件
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # 检查文件大小
        file_size = os.path.getsize(temp_file)
        print(f"✅ 音频文件已保存: {temp_file}")
        print(f"✅ 文件大小: {file_size} 字节")
        
        if file_size > 1000:  # 至少1KB
            print("✅ 音频录制功能正常")
            return True
        else:
            print("❌ 音频文件太小，可能没有录制到声音")
            return False
            
    except Exception as e:
        print(f"❌ 音频录制测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

def check_audio_permissions():
    """检查音频权限"""
    print("🔍 检查音频权限...")
    
    try:
        # 检查系统音频权限
        result = subprocess.run([
            'sqlite3', 
            os.path.expanduser('~/Library/Application Support/com.apple.TCC/TCC.db'),
            "SELECT service, client, auth_value FROM access WHERE service='kTCCServiceMicrophone';"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 可以访问权限数据库")
            if 'python' in result.stdout.lower() or 'terminal' in result.stdout.lower():
                print("✅ Python/终端已获得麦克风权限")
                return True
            else:
                print("⚠️ 未找到Python/终端的麦克风权限记录")
        else:
            print("⚠️ 无法访问权限数据库")
            
    except Exception as e:
        print(f"⚠️ 权限检查失败: {e}")
    
    # 尝试实际录制测试
    return test_audio_recording()

def fix_region_selector():
    """修复区域选择器的macOS兼容性"""
    print("🖥️ 修复区域选择器...")
    
    region_selector_path = Path(__file__).parent / "src" / "ui" / "region_selector.py"
    
    if not region_selector_path.exists():
        print("❌ 区域选择器文件不存在")
        return False
    
    try:
        # 读取原文件
        with open(region_selector_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if 'macOS兼容性修复' in content:
            print("✅ 区域选择器已经修复")
            return True
        
        # 添加macOS兼容性修复
        fixes = """
    def showEvent(self, event):
        \"\"\"显示事件 - macOS兼容性修复\"\"\"
        super().showEvent(event)
        
        # macOS特殊处理
        if platform.system() == "Darwin":
            # 延迟显示以避免黑屏问题
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._setup_macos_display)
        else:
            self._setup_display()
    
    def _setup_macos_display(self):
        \"\"\"macOS显示设置\"\"\"
        # 强制窗口到前台
        self.raise_()
        self.activateWindow()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint  # macOS特殊标志
        )
        
        # 重新显示
        self.show()
        self._setup_display()
    
    def _setup_display(self):
        \"\"\"设置显示参数\"\"\"
        # 获取物理屏幕尺寸（MSS使用的坐标系）
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            physical_width = monitor['width']
            physical_height = monitor['height']

        # 转换为逻辑坐标
        logical_width = int(physical_width / self.device_pixel_ratio)
        logical_height = int(physical_height / self.device_pixel_ratio)

        print(f"屏幕尺寸: 物理({physical_width}x{physical_height}) -> 逻辑({logical_width}x{logical_height})")

        # 设置窗口几何
        self.setGeometry(0, 0, logical_width, logical_height)

        # 将提示标签放在屏幕中央上方
        if hasattr(self, 'hint_label'):
            screen_center = self.rect().center()
            label_x = screen_center.x() - self.hint_label.width() // 2
            label_y = 50  # 距离顶部50像素
            self.hint_label.move(label_x, label_y)"""
        
        # 替换原来的showEvent方法
        import re
        pattern = r'def showEvent\(self, event\):.*?(?=\n    def|\nclass|\Z)'
        replacement = fixes.strip()
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 添加platform导入
        if 'import platform' not in new_content:
            new_content = new_content.replace('import sys', 'import sys\nimport platform')
        
        # 添加标记
        new_content = '# macOS兼容性修复\n' + new_content
        
        # 写回文件
        with open(region_selector_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 区域选择器macOS兼容性修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复区域选择器失败: {e}")
        return False

def fix_audio_capture():
    """修复音频捕获模块"""
    print("🔧 修复音频捕获模块...")
    
    audio_capture_path = Path(__file__).parent / "src" / "core" / "audio_capture.py"
    
    if not audio_capture_path.exists():
        print("❌ 音频捕获文件不存在")
        return False
    
    try:
        # 读取原文件
        with open(audio_capture_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if 'macOS音频修复' in content:
            print("✅ 音频捕获已经修复")
            return True
        
        # 修复音频参数设置
        fixes = '''
    def __init__(self):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.record_thread = None
        
        # macOS音频修复 - 优化音频参数
        import platform
        if platform.system() == "Darwin":
            # macOS优化设置
            self.sample_rate = 44100
            self.channels = 1  # macOS上使用单声道更稳定
            self.chunk_size = 2048  # 增大缓冲区
            self.format = pyaudio.paInt16
        else:
            # 其他系统的设置
            self.sample_rate = 44100
            self.channels = 2
            self.chunk_size = 1024
            self.format = pyaudio.paInt16
        
        # 音频数据缓冲
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()

        # 音量监控
        self.volume_level = 0.0
        
        print(f"音频参数: {self.sample_rate}Hz, {self.channels}声道, 缓冲区{self.chunk_size}")'''
        
        # 替换__init__方法
        import re
        pattern = r'def __init__\(self\):.*?(?=\n    def|\n\n    def)'
        new_content = re.sub(pattern, fixes.strip(), content, flags=re.DOTALL)
        
        # 添加标记
        new_content = '# macOS音频修复\n' + new_content
        
        # 写回文件
        with open(audio_capture_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 音频捕获模块修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复音频捕获失败: {e}")
        return False

def show_permission_guide():
    """显示权限设置指南"""
    print("\n" + "="*60)
    print("📋 macOS权限设置指南")
    print("="*60)
    print("1. 屏幕录制权限:")
    print("   - 系统偏好设置 > 安全性与隐私 > 隐私 > 屏幕录制")
    print("   - 点击锁图标解锁")
    print("   - 添加 Python 或 终端 应用程序")
    print("   - 确保开关处于开启状态")
    print()
    print("2. 麦克风权限:")
    print("   - 系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风")
    print("   - 添加 Python 或 终端 应用程序")
    print("   - 确保开关处于开启状态")
    print()
    print("3. 如果区域选择显示黑屏:")
    print("   - 重启应用程序")
    print("   - 确保屏幕录制权限已授予")
    print("   - 尝试使用全屏录制模式")
    print()
    print("4. 如果音频仍无声音:")
    print("   - 检查系统音量设置")
    print("   - 尝试不同的音频输入设备")
    print("   - 重启应用程序")
    print("="*60)

def main():
    """主函数"""
    print("🔧 修复macOS音频录制和区域选择问题")
    print("="*50)
    
    if platform.system() != "Darwin":
        print("❌ 此脚本仅适用于macOS系统")
        return 1
    
    success_count = 0
    total_fixes = 3
    
    # 1. 修复音频捕获
    print("\n1️⃣ 修复音频捕获模块...")
    if fix_audio_capture():
        success_count += 1
    
    # 2. 修复区域选择器
    print("\n2️⃣ 修复区域选择器...")
    if fix_region_selector():
        success_count += 1
    
    # 3. 检查音频权限
    print("\n3️⃣ 检查音频权限...")
    if check_audio_permissions():
        success_count += 1
    
    # 显示结果
    print("\n" + "="*50)
    print(f"📊 修复结果: {success_count}/{total_fixes} 项成功")
    
    if success_count >= 2:
        print("🎉 主要问题已修复！")
        print("✨ 请重启应用程序测试:")
        print("   ./run_app.sh")
    else:
        print("⚠️ 部分问题未能自动修复")
        show_permission_guide()
    
    return 0 if success_count >= 2 else 1

if __name__ == "__main__":
    sys.exit(main())
