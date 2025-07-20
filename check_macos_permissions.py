#!/usr/bin/env python3
"""
检查和设置macOS权限
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_screen_recording_permission():
    """检查屏幕录制权限"""
    print("🖥️ 检查屏幕录制权限...")
    
    try:
        # 尝试截图测试权限
        import mss
        
        with mss.mss() as sct:
            # 获取主显示器
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            
            # 尝试截图
            screenshot = sct.grab(monitor)
            
            # 检查截图是否有效（不是全黑）
            import numpy as np
            img_array = np.array(screenshot)
            
            # 计算非黑色像素的比例
            non_black_pixels = np.sum(img_array > 10)  # 大于10的像素认为是非黑色
            total_pixels = img_array.size
            non_black_ratio = non_black_pixels / total_pixels
            
            print(f"截图尺寸: {screenshot.width}x{screenshot.height}")
            print(f"非黑色像素比例: {non_black_ratio:.2%}")
            
            if non_black_ratio > 0.1:  # 如果超过10%的像素不是黑色
                print("✅ 屏幕录制权限正常")
                return True
            else:
                print("❌ 屏幕录制权限可能有问题（截图全黑）")
                return False
                
    except Exception as e:
        print(f"❌ 屏幕录制权限检查失败: {e}")
        return False

def check_microphone_permission():
    """检查麦克风权限"""
    print("🎵 检查麦克风权限...")
    
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        # 尝试创建音频流
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        # 尝试读取音频数据
        data = stream.read(1024, exception_on_overflow=False)
        stream.close()
        audio.terminate()
        
        if len(data) > 0:
            print("✅ 麦克风权限正常")
            return True
        else:
            print("❌ 麦克风权限可能有问题（无音频数据）")
            return False
            
    except Exception as e:
        print(f"❌ 麦克风权限检查失败: {e}")
        return False

def show_permission_guide():
    """显示权限设置指南"""
    print("\n" + "="*60)
    print("📋 macOS权限设置指南")
    print("="*60)
    
    print("🖥️ 屏幕录制权限设置:")
    print("1. 打开 系统偏好设置")
    print("2. 点击 安全性与隐私")
    print("3. 选择 隐私 标签")
    print("4. 在左侧列表中选择 屏幕录制")
    print("5. 点击锁图标解锁（需要管理员密码）")
    print("6. 勾选 Python 或 终端")
    print("7. 重启应用程序")
    print()
    
    print("🎵 麦克风权限设置:")
    print("1. 在同一个隐私设置中")
    print("2. 选择 麦克风")
    print("3. 勾选 Python 或 终端")
    print("4. 重启应用程序")
    print()
    
    print("💡 重要提示:")
    print("- 权限设置后必须重启应用程序才能生效")
    print("- 如果列表中没有Python，请先运行一次应用程序")
    print("- 某些情况下可能需要重启系统")
    print("="*60)

def test_region_selector():
    """测试区域选择器"""
    print("🎯 测试区域选择器...")
    
    try:
        # 添加src路径
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from PyQt6.QtWidgets import QApplication
        from ui.region_selector import RegionSelectorWindow
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建区域选择器
        selector = RegionSelectorWindow()
        
        print("✅ 区域选择器创建成功")
        print("💡 如果要测试显示效果，请手动运行应用程序")
        
        return True
        
    except Exception as e:
        print(f"❌ 区域选择器测试失败: {e}")
        return False

def check_system_info():
    """检查系统信息"""
    print("💻 系统信息:")
    
    try:
        # macOS版本
        result = subprocess.run(['sw_vers'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        
        # Python版本
        print(f"   Python版本: {sys.version}")
        
        # 屏幕信息
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            screen = app.primaryScreen()
            geometry = screen.geometry()
            print(f"   主屏幕: {geometry.width()}x{geometry.height()}")
            
            # DPI信息
            dpr = screen.devicePixelRatio()
            print(f"   设备像素比: {dpr}")
            
        except Exception as e:
            print(f"   屏幕信息获取失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统信息检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🍎 macOS权限检查工具")
    print("="*50)
    
    if platform.system() != "Darwin":
        print("❌ 此工具仅适用于macOS系统")
        return 1
    
    # 检查系统信息
    check_system_info()
    print()
    
    # 权限检查
    checks = [
        ("屏幕录制权限", check_screen_recording_permission),
        ("麦克风权限", check_microphone_permission),
        ("区域选择器", test_region_selector),
    ]
    
    success_count = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if check_func():
            success_count += 1
        else:
            print(f"   ⚠️ {check_name}检查未通过")
    
    print("\n" + "="*50)
    print(f"📊 检查结果: {success_count}/{total_checks} 项通过")
    
    if success_count == total_checks:
        print("🎉 所有权限检查通过！")
        print("✨ 现在可以正常使用区域选择功能")
    else:
        print("⚠️ 部分权限需要设置")
        show_permission_guide()
    
    return 0 if success_count == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())
