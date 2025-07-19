#!/usr/bin/env python3
"""
安装测试脚本 - 验证所有依赖是否正确安装
"""

import sys
import os
import platform
import importlib
from pathlib import Path

def test_python_version():
    """测试Python版本"""
    print("=" * 50)
    print("测试Python版本")
    print("=" * 50)
    
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def test_system_compatibility():
    """测试系统兼容性"""
    print("\n" + "=" * 50)
    print("测试系统兼容性")
    print("=" * 50)
    
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"系统版本: {platform.release()}")
    print(f"架构: {platform.machine()}")
    
    if system in ["Windows", "Darwin"]:
        print("✅ 操作系统支持")
        return True
    else:
        print("❌ 操作系统不支持，仅支持Windows和macOS")
        return False

def test_required_modules():
    """测试必需的模块"""
    print("\n" + "=" * 50)
    print("测试必需模块")
    print("=" * 50)

    # 检查是否在CI环境中
    is_ci = os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS')

    # 核心必需模块（CI和本地都需要）
    core_modules = [
        ("PyQt6", "PyQt6"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("Pillow", "PIL"),
        ("MSS", "mss"),
        ("PSUtil", "psutil"),
        ("PyInstaller", "PyInstaller"),
    ]

    # 可选模块（仅本地环境测试）
    optional_modules = [
        ("PyAudio", "pyaudio"),
        ("Keyboard", "keyboard"),
        ("PyNput", "pynput"),
        ("ImageIO", "imageio"),
    ]

    # 测试核心模块
    success_count = 0
    total_count = len(core_modules)

    for name, module in core_modules:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'Unknown')
            print(f"✅ {name}: {version}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name}: 未安装 ({e})")

    # 在非CI环境中测试可选模块
    if not is_ci:
        print("\n测试可选模块:")
        optional_success = 0
        for name, module in optional_modules:
            try:
                mod = importlib.import_module(module)
                version = getattr(mod, '__version__', 'Unknown')
                print(f"✅ {name}: {version}")
                optional_success += 1
            except ImportError as e:
                print(f"⚠️ {name}: 未安装 ({e}) - 可选模块")

        print(f"可选模块: {optional_success}/{len(optional_modules)} 可用")
    else:
        print("⚠️ CI环境检测到，跳过可选模块测试")

    print(f"\n核心模块测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_project_structure():
    """测试项目结构"""
    print("\n" + "=" * 50)
    print("测试项目结构")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "src/config/settings.py",
        "src/ui/main_window.py",
        "src/core/screen_capture.py",
        "build_scripts/build_windows.py",
        "build_scripts/build_macos.py",
    ]
    
    success_count = 0
    total_count = len(required_files)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path}: 文件不存在")
    
    print(f"\n文件结构测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_config_loading():
    """测试配置加载"""
    print("\n" + "=" * 50)
    print("测试配置加载")
    print("=" * 50)
    
    try:
        # 添加src目录到Python路径
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from config.settings import AppConfig
        print(f"✅ 应用名称: {AppConfig.APP_NAME}")
        print(f"✅ 应用版本: {AppConfig.APP_VERSION}")
        print(f"✅ 应用作者: {AppConfig.APP_AUTHOR}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_gui_availability():
    """测试GUI可用性"""
    print("\n" + "=" * 50)
    print("测试GUI可用性")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 在CI环境中可能没有显示器
        import os
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            print("⚠️  CI环境检测到，跳过GUI测试")
            return True
        
        # 尝试创建应用程序实例
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        print("✅ PyQt6 GUI框架可用")
        return True
    except Exception as e:
        print(f"❌ GUI框架不可用: {e}")
        return False

def main():
    """主函数"""
    print("现代录屏工具 - 安装测试")
    print("测试开始时间:", platform.platform())
    
    tests = [
        ("Python版本", test_python_version),
        ("系统兼容性", test_system_compatibility),
        ("必需模块", test_required_modules),
        ("项目结构", test_project_structure),
        ("配置加载", test_config_loading),
        ("GUI可用性", test_gui_availability),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！应用程序应该可以正常运行。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
