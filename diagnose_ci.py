#!/usr/bin/env python3
"""
CI诊断脚本 - 帮助调试GitHub Actions问题
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def check_environment():
    """检查环境信息"""
    print_section("环境信息")
    
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"工作目录: {os.getcwd()}")
    
    # 环境变量
    print("\n重要环境变量:")
    env_vars = ['CI', 'GITHUB_ACTIONS', 'RUNNER_OS', 'QT_QPA_PLATFORM', 'DISPLAY']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")

def check_files():
    """检查文件结构"""
    print_section("文件结构检查")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'requirements-ci.txt',
        'src/config/settings.py',
        'src/ui/main_window.py',
        'src/core/screen_capture.py',
        'scripts/ci_build.py',
        'test_ci_build.py',
        'simple_build.py'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"✅ {file_path} ({size} bytes)")
            else:
                print(f"✅ {file_path} (directory)")
        else:
            print(f"❌ {file_path} (missing)")

def check_dependencies():
    """检查依赖"""
    print_section("依赖检查")
    
    # 检查pip
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        print(f"pip版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ pip检查失败: {e}")
    
    # 检查关键模块
    modules = [
        'PyQt6', 'cv2', 'numpy', 'PIL', 'mss', 'psutil', 'PyInstaller'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")

def test_pyinstaller():
    """测试PyInstaller"""
    print_section("PyInstaller测试")
    
    try:
        # 检查PyInstaller版本
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                              capture_output=True, text=True)
        print(f"PyInstaller版本: {result.stdout.strip()}")
        
        # 检查是否可以创建spec文件
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ PyInstaller可用")
        else:
            print("❌ PyInstaller不可用")
            
    except Exception as e:
        print(f"❌ PyInstaller测试失败: {e}")

def test_qt():
    """测试Qt"""
    print_section("Qt测试")
    
    try:
        # 设置无头模式
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt6.QtCore import QCoreApplication
        print("✅ PyQt6.QtCore导入成功")
        
        # 尝试创建应用程序
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication([])
        print("✅ Qt应用程序创建成功")
        
    except Exception as e:
        print(f"❌ Qt测试失败: {e}")

def main():
    """主函数"""
    print("GitHub Actions CI诊断脚本")
    print(f"运行时间: {platform.platform()}")
    
    try:
        check_environment()
        check_files()
        check_dependencies()
        test_pyinstaller()
        test_qt()
        
        print_section("诊断完成")
        print("✅ 诊断脚本执行完成")
        return 0
        
    except Exception as e:
        print(f"\n❌ 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
