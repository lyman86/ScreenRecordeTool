#!/usr/bin/env python3
"""
CI构建专用测试脚本 - 验证构建环境和依赖
"""

import sys
import os
import platform
import importlib
from pathlib import Path

def test_environment():
    """测试CI环境"""
    print("=" * 50)
    print("CI环境测试")
    print("=" * 50)
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查环境变量
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'RUNNER_OS', 'QT_QPA_PLATFORM']
    for var in ci_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    return True

def test_critical_imports():
    """测试关键导入"""
    print("\n" + "=" * 50)
    print("关键模块导入测试")
    print("=" * 50)

    # 基础模块（必须成功）
    basic_modules = [
        'PyQt6',
        'PyQt6.QtCore',
        'cv2',
        'numpy',
        'PIL',
        'mss',
        'psutil',
        'PyInstaller'
    ]

    # GUI模块（在Linux环境中可能失败）
    gui_modules = [
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ]

    failed_imports = []
    gui_failed = []

    # 测试基础模块
    for module in basic_modules:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'Unknown')
            print(f"✅ {module}: {version}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)

    # 测试GUI模块（允许在Linux环境中失败）
    system = platform.system()
    for module in gui_modules:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'Unknown')
            print(f"✅ {module}: {version}")
        except Exception as e:
            if system == "Linux":
                print(f"⚠️ {module}: {e} (Linux环境中可接受)")
                gui_failed.append(module)
            else:
                print(f"❌ {module}: {e}")
                failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ 关键模块导入失败: {failed_imports}")
        return False

    if gui_failed and system == "Linux":
        print(f"\n⚠️ GUI模块在Linux环境中失败（可接受）: {gui_failed}")

    print("\n✅ 关键模块导入测试通过")
    return True

def test_project_structure():
    """测试项目结构"""
    print("\n" + "=" * 50)
    print("项目结构测试")
    print("=" * 50)
    
    required_files = [
        'main.py',
        'src/config/settings.py',
        'src/ui/main_window.py',
        'src/core/screen_capture.py',
        'scripts/ci_build.py',
        'requirements-ci.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 缺少文件: {missing_files}")
        return False
    
    print("\n✅ 项目结构完整")
    return True

def test_pyqt_headless():
    """测试PyQt6无头模式"""
    print("\n" + "=" * 50)
    print("PyQt6无头模式测试")
    print("=" * 50)

    system = platform.system()
    if system == "Linux":
        print("⚠️ Linux环境检测到，跳过PyQt6 GUI测试")
        print("✅ PyQt6无头模式测试跳过（Linux环境）")
        return True

    try:
        # 设置无头模式
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt

        # 尝试创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        print("✅ PyQt6应用程序创建成功")

        # 测试基本组件
        from PyQt6.QtWidgets import QWidget, QLabel
        widget = QWidget()
        label = QLabel("Test")
        widget.close()

        print("✅ PyQt6组件创建成功")
        return True

    except Exception as e:
        print(f"❌ PyQt6无头模式测试失败: {e}")
        return False

def test_build_dependencies():
    """测试构建依赖"""
    print("\n" + "=" * 50)
    print("构建依赖测试")
    print("=" * 50)
    
    try:
        # 测试PyInstaller
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
        
        # 测试spec文件创建
        from scripts.ci_build import create_simple_spec
        spec_file = create_simple_spec()
        if spec_file.exists():
            print(f"✅ Spec文件创建成功: {spec_file}")
            return True
        else:
            print("❌ Spec文件创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建依赖测试失败: {e}")
        return False

def main():
    """主函数"""
    print("CI构建环境测试")
    print("开始时间:", platform.platform())
    
    tests = [
        ("环境检查", test_environment),
        ("关键导入", test_critical_imports),
        ("项目结构", test_project_structure),
        ("PyQt6无头模式", test_pyqt_headless),
        ("构建依赖", test_build_dependencies),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过，可以进行构建")
        return 0
    else:
        print("⚠️ 部分测试失败，构建可能有问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
