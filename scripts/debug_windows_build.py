#!/usr/bin/env python3
"""
Windows构建调试脚本 - 专门用于诊断Windows构建问题
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def check_windows_environment():
    """检查Windows环境"""
    print("🔍 检查Windows环境...")
    
    print(f"操作系统: {platform.system()}")
    print(f"版本: {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查环境变量
    important_vars = ['PATH', 'PYTHONPATH', 'TEMP', 'TMP']
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value[:100]}{'...' if len(value) > 100 else ''}")

def check_dependencies():
    """检查依赖"""
    print("\n📦 检查依赖...")
    
    required_packages = [
        'PyQt6',
        'opencv-python-headless',
        'pillow',
        'numpy',
        'mss',
        'psutil',
        'PyInstaller'
    ]
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")

def test_pyinstaller():
    """测试PyInstaller"""
    print("\n🔧 测试PyInstaller...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', '--version'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ PyInstaller版本: {result.stdout.strip()}")
        else:
            print(f"❌ PyInstaller错误: {result.stderr}")
    except Exception as e:
        print(f"❌ PyInstaller测试失败: {e}")

def test_simple_build():
    """测试简单构建"""
    print("\n🏗️ 测试简单构建...")
    
    # 创建简单的测试脚本
    test_script = Path("test_app.py")
    test_content = '''
import sys
print("Hello from test app!")
print(f"Python version: {sys.version}")
input("Press Enter to exit...")
'''
    
    try:
        # 写入测试脚本
        test_script.write_text(test_content)
        print(f"✅ 创建测试脚本: {test_script}")
        
        # 尝试构建
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--console',
            '--name', 'test_app',
            str(test_script)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 简单构建成功")
            
            # 检查输出文件
            exe_path = Path("dist/test_app.exe")
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)
                print(f"✅ 生成可执行文件: {exe_path} ({size:.1f}MB)")
            else:
                print("❌ 可执行文件未生成")
        else:
            print(f"❌ 构建失败:")
            print(f"标准输出: {result.stdout}")
            print(f"错误输出: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 简单构建测试失败: {e}")
    finally:
        # 清理
        if test_script.exists():
            test_script.unlink()
        
        # 清理构建文件
        import shutil
        for cleanup_dir in ['build', 'dist', '__pycache__']:
            if Path(cleanup_dir).exists():
                shutil.rmtree(cleanup_dir, ignore_errors=True)
        
        for cleanup_file in ['test_app.spec']:
            cleanup_path = Path(cleanup_file)
            if cleanup_path.exists():
                cleanup_path.unlink()

def test_main_app_imports():
    """测试主应用导入"""
    print("\n📱 测试主应用导入...")
    
    try:
        # 添加src到路径
        sys.path.insert(0, 'src')
        
        # 测试配置导入
        from config.settings import AppConfig
        print(f"✅ 配置导入成功: {AppConfig.APP_NAME}")
        
        # 测试UI导入
        try:
            from ui.main_window import MainWindow
            print("✅ 主窗口导入成功")
        except Exception as e:
            print(f"⚠️ 主窗口导入失败: {e}")
        
        # 测试核心模块导入
        try:
            from core.screen_capture import ScreenCapture
            print("✅ 屏幕捕获模块导入成功")
        except Exception as e:
            print(f"⚠️ 屏幕捕获模块导入失败: {e}")
            
    except Exception as e:
        print(f"❌ 主应用导入失败: {e}")

def check_disk_space():
    """检查磁盘空间"""
    print("\n💾 检查磁盘空间...")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        
        print(f"总空间: {total // (1024**3)} GB")
        print(f"已使用: {used // (1024**3)} GB")
        print(f"可用空间: {free // (1024**3)} GB")
        
        if free < 2 * (1024**3):  # 少于2GB
            print("⚠️ 可用空间不足，可能影响构建")
        else:
            print("✅ 磁盘空间充足")
            
    except Exception as e:
        print(f"❌ 磁盘空间检查失败: {e}")

def main():
    """主函数"""
    print("🔧 Windows构建调试工具")
    print("=" * 50)
    
    if platform.system() != 'Windows':
        print("⚠️ 此脚本专为Windows设计，当前系统可能不适用")
    
    try:
        check_windows_environment()
        check_dependencies()
        check_disk_space()
        test_pyinstaller()
        test_main_app_imports()
        test_simple_build()
        
        print("\n" + "=" * 50)
        print("🎯 调试完成")
        print("=" * 50)
        print("如果所有测试都通过，Windows构建应该能够成功。")
        print("如果有测试失败，请根据错误信息进行修复。")
        
    except KeyboardInterrupt:
        print("\n调试被用户中断")
    except Exception as e:
        print(f"\n调试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
