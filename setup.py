"""
安装脚本
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def install_dependencies():
    """安装依赖"""
    print("安装依赖包...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("错误: requirements.txt文件不存在")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def check_platform_requirements():
    """检查平台特定要求"""
    current_platform = platform.system()
    
    if current_platform == "Darwin":  # macOS
        print("检查macOS特定要求...")
        # 检查是否需要额外的权限或工具
        print("注意: 在macOS上运行时，可能需要授予屏幕录制和麦克风权限")
        
    elif current_platform == "Windows":
        print("检查Windows特定要求...")
        # 检查Windows特定要求
        print("注意: 在Windows上可能需要安装Visual C++ Redistributable")
    
    return True

def create_desktop_shortcut():
    """创建桌面快捷方式"""
    try:
        if platform.system() == "Windows":
            # Windows快捷方式创建
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = Path(desktop) / "现代录屏工具.lnk"
            target = Path(__file__).parent / "main.py"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = str(target)
            shortcut.WorkingDirectory = str(target.parent)
            shortcut.save()
            
            print(f"已创建桌面快捷方式: {path}")
            
        elif platform.system() == "Darwin":  # macOS
            # macOS快捷方式创建
            print("在macOS上，请手动创建快捷方式或使用构建脚本创建应用程序包")
            
    except Exception as e:
        print(f"创建快捷方式失败: {e}")

def main():
    """主函数"""
    print("现代录屏工具 - 安装脚本")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查平台要求
    if not check_platform_requirements():
        return 1
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 创建快捷方式
    create_desktop_shortcut()
    
    print("\n安装完成!")
    print("运行方式:")
    print(f"  python {Path(__file__).parent / 'main.py'}")
    print("\n构建可执行文件:")
    print(f"  python {Path(__file__).parent / 'build.py'}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
