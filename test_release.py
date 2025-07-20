#!/usr/bin/env python3
"""
测试发布流程脚本
"""

import subprocess
import sys
from pathlib import Path

def test_git_setup():
    """测试Git配置"""
    print("🔍 测试Git配置...")
    
    try:
        # 检查远程仓库
        result = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True, text=True, check=True
        )
        print(f"✅ 远程仓库: {result.stdout.strip()}")
        
        # 检查当前分支
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, check=True
        )
        print(f"✅ 当前分支: {result.stdout.strip()}")
        
        # 检查最新标签
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True, text=True, check=True
            )
            print(f"✅ 最新标签: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("ℹ️  暂无标签")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git配置检查失败: {e}")
        return False

def test_workflow_files():
    """测试工作流文件"""
    print("\n🔍 测试工作流文件...")
    
    workflow_files = [
        '.github/workflows/build-release.yml',
        '.github/workflows/build-test.yml'
    ]
    
    all_exist = True
    for file_path in workflow_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path} 存在")
            # 检查文件大小
            size = path.stat().st_size
            print(f"   文件大小: {size} 字节")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_build_scripts():
    """测试构建脚本"""
    print("\n🔍 测试构建脚本...")
    
    build_files = [
        'build.py',
        'build_scripts/build_windows.py',
        'build_scripts/build_macos.py',
        'release.py'
    ]
    
    all_exist = True
    for file_path in build_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """测试依赖"""
    print("\n🔍 测试Python依赖...")
    
    required_modules = [
        'PyQt6',
        'cv2',
        'numpy',
        'mss',
        'pyaudio'
    ]
    
    all_available = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 可用")
        except ImportError:
            print(f"❌ {module} 不可用")
            all_available = False
    
    return all_available

def show_next_steps():
    """显示后续步骤"""
    print("\n📋 后续步骤:")
    print("\n1. 🚀 创建发布:")
    print("   python release.py")
    print("\n2. 🔨 测试构建:")
    print("   访问: https://github.com/lyman86/ScreenRecordeTool/actions/workflows/build-test.yml")
    print("   点击 'Run workflow' 进行测试构建")
    print("\n3. 📦 查看发布:")
    print("   访问: https://github.com/lyman86/ScreenRecordeTool/releases")
    print("\n4. 🔍 监控构建:")
    print("   访问: https://github.com/lyman86/ScreenRecordeTool/actions")
    
    print("\n💡 提示:")
    print("- 推送标签后，GitHub Actions会自动开始构建")
    print("- 构建完成后会自动创建Release")
    print("- 可以手动触发测试构建来验证流程")
    print("- 首次构建可能需要较长时间来下载依赖")

def main():
    """主函数"""
    print("🧪 现代录屏工具 - 发布流程测试")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not Path('main.py').exists():
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 运行所有测试
    tests = [
        ("Git配置", test_git_setup),
        ("工作流文件", test_workflow_files),
        ("构建脚本", test_build_scripts),
        ("Python依赖", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试失败: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n📊 测试结果汇总:")
    print("=" * 30)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 30)
    if all_passed:
        print("🎉 所有测试通过！发布系统已就绪。")
        show_next_steps()
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())