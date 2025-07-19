#!/usr/bin/env python3
"""
测试CI修复效果的本地验证脚本
"""

import sys
import subprocess
import platform
from pathlib import Path

def test_ci_requirements():
    """测试CI依赖安装"""
    print("🧪 测试CI依赖安装...")
    
    try:
        # 测试CI requirements文件
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements-ci.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ CI依赖安装成功")
            return True
        else:
            print("❌ CI依赖安装失败")
            print("错误输出:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏰ CI依赖安装超时")
        return False
    except Exception as e:
        print(f"❌ CI依赖安装异常: {e}")
        return False

def test_individual_packages():
    """测试单个包安装"""
    print("\n🔧 测试单个包安装...")
    
    packages = [
        "PyQt6",
        "opencv-python-headless",
        "pillow",
        "numpy",
        "mss",
        "psutil",
        "PyInstaller"
    ]
    
    success_count = 0
    for package in packages:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {package}")
                success_count += 1
            else:
                print(f"❌ {package}: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"⏰ {package}: 安装超时")
        except Exception as e:
            print(f"❌ {package}: {e}")
    
    print(f"\n包安装结果: {success_count}/{len(packages)} 成功")
    return success_count >= len(packages) * 0.7  # 70%成功率即可

def test_imports():
    """测试导入功能"""
    print("\n📦 测试包导入...")
    
    import_tests = [
        ("PyQt6.QtCore", "PyQt6核心"),
        ("PyQt6.QtWidgets", "PyQt6组件"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("mss", "MSS"),
        ("psutil", "PSUtil"),
        ("PyInstaller", "PyInstaller")
    ]
    
    success_count = 0
    for module, name in import_tests:
        try:
            __import__(module)
            print(f"✅ {name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name}: {e}")
        except Exception as e:
            print(f"⚠️ {name}: {e}")
    
    print(f"\n导入测试结果: {success_count}/{len(import_tests)} 成功")
    return success_count >= len(import_tests) * 0.7

def test_config_loading():
    """测试配置加载"""
    print("\n⚙️ 测试配置加载...")
    
    try:
        sys.path.insert(0, 'src')
        from config.settings import AppConfig
        
        print(f"✅ 应用名称: {AppConfig.APP_NAME}")
        print(f"✅ 应用版本: {AppConfig.APP_VERSION}")
        print(f"✅ 应用作者: {AppConfig.APP_AUTHOR}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_ci_build_script():
    """测试CI构建脚本"""
    print("\n🏗️ 测试CI构建脚本...")
    
    try:
        # 只测试脚本的基本功能，不进行完整构建
        result = subprocess.run([
            sys.executable, "-c", 
            "import scripts.ci_build as cb; print('CI build script loaded successfully')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CI构建脚本加载成功")
            return True
        else:
            print("❌ CI构建脚本加载失败")
            print("错误:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ CI构建脚本测试失败: {e}")
        return False

def test_platform_compatibility():
    """测试平台兼容性"""
    print("\n🖥️ 测试平台兼容性...")
    
    system = platform.system()
    version = platform.release()
    arch = platform.machine()
    
    print(f"操作系统: {system}")
    print(f"版本: {version}")
    print(f"架构: {arch}")
    
    if system in ["Windows", "Darwin", "Linux"]:
        print("✅ 平台支持")
        return True
    else:
        print("⚠️ 平台可能不完全支持")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 GitHub Actions CI修复验证测试")
    print("=" * 60)
    
    tests = [
        ("平台兼容性", test_platform_compatibility),
        ("CI依赖安装", test_ci_requirements),
        ("单个包安装", test_individual_packages),
        ("包导入测试", test_imports),
        ("配置加载", test_config_loading),
        ("CI构建脚本", test_ci_build_script),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    success_rate = passed_tests / total_tests
    if success_rate >= 0.8:
        print("🎉 修复效果良好！CI应该能够正常工作。")
        return 0
    elif success_rate >= 0.6:
        print("⚠️ 修复部分有效，但仍有一些问题需要解决。")
        return 1
    else:
        print("❌ 修复效果不佳，需要进一步调整。")
        return 2

if __name__ == "__main__":
    sys.exit(main())
