#!/usr/bin/env python3
"""
修复macOS上的问题
1. 安装FFmpeg
2. 修复音频录制权限
3. 测试修复结果
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_ffmpeg():
    """检查FFmpeg是否安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            return True
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg未安装")
        return False
    except Exception as e:
        print(f"❌ 检查FFmpeg时出错: {e}")
        return False

def install_ffmpeg():
    """安装FFmpeg"""
    print("🔧 正在安装FFmpeg...")
    
    # 方法1: 尝试使用Homebrew
    try:
        print("尝试使用Homebrew安装FFmpeg...")
        result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                              capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ 通过Homebrew成功安装FFmpeg")
            return True
        else:
            print(f"❌ Homebrew安装失败: {result.stderr}")
    except Exception as e:
        print(f"❌ Homebrew安装出错: {e}")
    
    # 方法2: 下载预编译二进制文件
    print("尝试下载预编译的FFmpeg...")
    try:
        import urllib.request
        import tarfile
        import shutil
        
        # 创建临时目录
        temp_dir = Path.home() / ".screenrecorder" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载FFmpeg
        ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.0.zip"
        zip_path = temp_dir / "ffmpeg.zip"
        
        print("正在下载FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # 解压
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 移动到系统路径
        ffmpeg_bin = temp_dir / "ffmpeg"
        target_path = Path("/usr/local/bin/ffmpeg")
        
        if ffmpeg_bin.exists():
            # 需要管理员权限
            subprocess.run(['sudo', 'cp', str(ffmpeg_bin), str(target_path)], check=True)
            subprocess.run(['sudo', 'chmod', '+x', str(target_path)], check=True)
            print("✅ FFmpeg安装成功")
            return True
        else:
            print("❌ 下载的FFmpeg文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 下载安装FFmpeg失败: {e}")
        return False

def check_audio_permissions():
    """检查音频权限"""
    print("🔍 检查音频权限...")
    
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        
        # 尝试获取默认输入设备
        default_device = audio.get_default_input_device_info()
        print(f"✅ 默认音频输入设备: {default_device['name']}")
        
        # 尝试创建音频流
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        # 读取一小段音频数据
        data = stream.read(1024, exception_on_overflow=False)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print("✅ 音频录制权限正常")
        return True
        
    except Exception as e:
        print(f"❌ 音频权限检查失败: {e}")
        print("💡 请在系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风 中授予权限")
        return False

def fix_video_encoder():
    """修复视频编码器以使用ffmpeg-python"""
    print("🔧 修复视频编码器...")
    
    encoder_path = Path(__file__).parent / "src" / "core" / "video_encoder.py"
    
    if not encoder_path.exists():
        print("❌ 找不到video_encoder.py文件")
        return False
    
    try:
        # 读取原文件
        with open(encoder_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经修复
        if 'import ffmpeg' in content:
            print("✅ 视频编码器已经使用ffmpeg-python")
            return True
        
        # 添加ffmpeg-python导入
        import_section = """import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import cv2
import numpy as np
try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False
    print("警告: ffmpeg-python未安装，将使用系统FFmpeg命令")"""
        
        # 替换导入部分
        lines = content.split('\n')
        new_lines = []
        import_done = False
        
        for line in lines:
            if line.startswith('import') or line.startswith('from'):
                if not import_done:
                    new_lines.extend(import_section.split('\n'))
                    import_done = True
            else:
                new_lines.append(line)
        
        # 写回文件
        with open(encoder_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ 视频编码器修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复视频编码器失败: {e}")
        return False

def test_recording():
    """测试录制功能"""
    print("🧪 测试录制功能...")
    
    try:
        # 测试屏幕捕获
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 主显示器
            screenshot = sct.grab(monitor)
            print("✅ 屏幕捕获正常")
        
        # 测试音频捕获
        import pyaudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        data = stream.read(1024, exception_on_overflow=False)
        stream.close()
        audio.terminate()
        print("✅ 音频捕获正常")
        
        # 测试FFmpeg
        if check_ffmpeg():
            print("✅ FFmpeg可用")
        else:
            print("❌ FFmpeg不可用")
            return False
        
        print("🎉 所有录制功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 录制功能测试失败: {e}")
        return False

def show_macos_permissions_guide():
    """显示macOS权限设置指南"""
    print("\n" + "="*60)
    print("📋 macOS权限设置指南")
    print("="*60)
    print("1. 屏幕录制权限:")
    print("   - 打开 系统偏好设置 > 安全性与隐私 > 隐私")
    print("   - 选择 '屏幕录制'")
    print("   - 添加 Python 或 终端 应用程序")
    print()
    print("2. 麦克风权限:")
    print("   - 在同一个隐私设置中选择 '麦克风'")
    print("   - 添加 Python 或 终端 应用程序")
    print()
    print("3. 如果权限设置后仍有问题:")
    print("   - 重启终端应用程序")
    print("   - 重新运行录屏工具")
    print("="*60)

def main():
    """主函数"""
    print("🔧 macOS录屏工具问题修复脚本")
    print("="*50)
    
    if platform.system() != "Darwin":
        print("❌ 此脚本仅适用于macOS系统")
        return 1
    
    success_count = 0
    total_checks = 4
    
    # 1. 检查并安装FFmpeg
    print("\n1️⃣ 检查FFmpeg...")
    if check_ffmpeg():
        success_count += 1
    else:
        print("正在安装FFmpeg...")
        if install_ffmpeg():
            success_count += 1
        else:
            print("❌ FFmpeg安装失败，请手动安装")
    
    # 2. 检查音频权限
    print("\n2️⃣ 检查音频权限...")
    if check_audio_permissions():
        success_count += 1
    
    # 3. 修复视频编码器
    print("\n3️⃣ 修复视频编码器...")
    if fix_video_encoder():
        success_count += 1
    
    # 4. 测试录制功能
    print("\n4️⃣ 测试录制功能...")
    if test_recording():
        success_count += 1
    
    # 显示结果
    print("\n" + "="*50)
    print(f"📊 修复结果: {success_count}/{total_checks} 项成功")
    
    if success_count == total_checks:
        print("🎉 所有问题已修复！现在可以正常使用录屏工具了。")
    else:
        print("⚠️  部分问题未能自动修复，请查看上面的错误信息。")
        show_macos_permissions_guide()
    
    return 0 if success_count == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())
