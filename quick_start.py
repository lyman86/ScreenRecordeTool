#!/usr/bin/env python3
"""
快速启动脚本 - 一键设置和运行现代录屏工具
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎥 现代录屏工具 - 快速启动脚本")
    print("=" * 60)
    print("这个脚本将帮助您快速设置和运行录屏工具")
    print()

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        print("   请升级Python后重试")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def check_system():
    """检查系统兼容性"""
    print("\n🖥️  检查系统兼容性...")
    system = platform.system()
    print(f"   操作系统: {system}")
    
    if system in ["Windows", "Darwin"]:
        print("✅ 操作系统支持")
        return True
    else:
        print("⚠️  操作系统可能不完全支持，建议使用Windows或macOS")
        return True  # 仍然允许继续

def setup_virtual_environment():
    """设置虚拟环境"""
    print("\n📦 设置虚拟环境...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("   虚拟环境已存在")
        return True
    
    try:
        print("   创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ 虚拟环境创建失败")
        return False

def get_venv_python():
    """获取虚拟环境中的Python路径"""
    system = platform.system()
    if system == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def install_dependencies():
    """安装依赖"""
    print("\n📚 安装项目依赖...")

    venv_python = get_venv_python()
    if not venv_python.exists():
        print("   使用系统Python安装依赖...")
        python_cmd = sys.executable
    else:
        print("   使用虚拟环境Python安装依赖...")
        python_cmd = str(venv_python)

    try:
        # 升级pip
        print("   升级pip...")
        subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
                      check=True, capture_output=True)

        # 首先尝试安装最小依赖
        print("   尝试安装最小依赖...")
        try:
            subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements-minimal.txt"],
                          check=True)
            print("✅ 最小依赖安装成功")
            return True
        except subprocess.CalledProcessError:
            print("   最小依赖安装失败，尝试完整依赖...")

        # 如果最小依赖失败，尝试完整依赖
        subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)

        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print("   建议手动安装依赖: pip install PyQt6 opencv-python pillow numpy mss psutil")
        return False

def run_tests():
    """运行测试"""
    print("\n🧪 运行安装测试...")
    
    venv_python = get_venv_python()
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    try:
        result = subprocess.run([python_cmd, "test_installation.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 所有测试通过")
            return True
        else:
            print("⚠️  部分测试失败，但可以继续")
            print("   详细信息请查看测试输出")
            return True  # 允许继续
    except Exception as e:
        print(f"⚠️  测试运行失败: {e}")
        return True  # 允许继续

def create_desktop_shortcut():
    """创建桌面快捷方式"""
    print("\n🔗 创建桌面快捷方式...")
    
    system = platform.system()
    if system == "Windows":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "现代录屏工具.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = str(Path(__file__).parent / "main.py")
            shortcut.WorkingDirectory = str(Path(__file__).parent)
            shortcut.save()
            
            print("✅ Windows桌面快捷方式创建成功")
            return True
        except ImportError:
            print("⚠️  无法创建Windows快捷方式（缺少winshell模块）")
            return False
    elif system == "Darwin":
        print("ℹ️  macOS用户可以手动将应用添加到Dock")
        return True
    else:
        print("ℹ️  请手动创建快捷方式")
        return True

def start_application():
    """启动应用程序"""
    print("\n🚀 启动应用程序...")
    
    venv_python = get_venv_python()
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    try:
        print("   正在启动现代录屏工具...")
        subprocess.run([python_cmd, "main.py"])
        return True
    except KeyboardInterrupt:
        print("\n   应用程序被用户关闭")
        return True
    except Exception as e:
        print(f"❌ 应用程序启动失败: {e}")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "=" * 60)
    print("🎉 设置完成！")
    print("=" * 60)
    print("后续步骤:")
    print("1. 应用程序已启动，您可以开始录制屏幕")
    print("2. 查看README.md了解详细使用说明")
    print("3. 如需构建可执行文件，运行: python build.py")
    print("4. 如有问题，请查看GitHub Issues页面")
    print()
    print("🔗 有用的链接:")
    print("   - 项目主页: https://github.com/lyman86/ScreenRecordeTool")
    print("   - 使用文档: README.md")
    print("   - 问题反馈: https://github.com/lyman86/ScreenRecordeTool/issues")
    print()
    print("感谢使用现代录屏工具！")

def main():
    """主函数"""
    print_banner()
    
    try:
        # 1. 检查Python版本
        if not check_python_version():
            return 1
        
        # 2. 检查系统兼容性
        if not check_system():
            return 1
        
        # 3. 设置虚拟环境
        if not setup_virtual_environment():
            print("⚠️  虚拟环境设置失败，将使用系统Python")
        
        # 4. 安装依赖
        if not install_dependencies():
            print("❌ 依赖安装失败，无法继续")
            return 1
        
        # 5. 运行测试
        run_tests()
        
        # 6. 创建桌面快捷方式
        create_desktop_shortcut()
        
        # 7. 询问是否立即启动
        response = input("\n是否立即启动应用程序? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            start_application()
        
        # 8. 显示后续步骤
        show_next_steps()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n设置被用户中断")
        return 1
    except Exception as e:
        print(f"\n设置过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
