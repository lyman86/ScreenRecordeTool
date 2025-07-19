#!/usr/bin/env python3
"""
最终测试脚本 - 验证所有修复并准备提交
"""

import sys
import os
import subprocess
from pathlib import Path

def run_test(name, cmd, timeout=300):
    """运行测试命令"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        print("标准输出:")
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        
        success = result.returncode == 0
        print(f"\n结果: {'✅ 成功' if success else '❌ 失败'} (返回码: {result.returncode})")
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def check_build_output():
    """检查构建输出"""
    print(f"\n{'='*60}")
    print("检查构建输出")
    print('='*60)
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    files = list(dist_dir.rglob("*"))
    if not files:
        print("❌ dist目录为空")
        return False
    
    print("构建文件:")
    total_size = 0
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            total_size += size
            print(f"  {file.relative_to(dist_dir)} ({size:,} bytes)")
    
    print(f"\n总大小: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # 检查主要可执行文件
    main_exe = dist_dir / "ScreenRecorder"
    if main_exe.exists():
        print(f"✅ 主要可执行文件存在: {main_exe}")
        return True
    else:
        print("❌ 主要可执行文件不存在")
        return False

def main():
    """主函数"""
    print("GitHub Actions CI构建修复 - 最终测试")
    print("="*60)
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"工作目录: {project_root}")
    
    # 设置环境变量
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    tests = [
        # 1. 清理环境
        ("清理构建目录", ["rm", "-rf", "build", "dist", "*.spec"]),
        
        # 2. 安装依赖
        ("安装CI依赖", [sys.executable, "-m", "pip", "install", "-r", "requirements-ci.txt"]),
        
        # 3. 运行CI测试
        ("CI环境测试", [sys.executable, "test_ci_build.py"]),
        
        # 4. 执行构建
        ("执行CI构建", [sys.executable, "scripts/ci_build.py"], 600),  # 10分钟超时
    ]
    
    passed = 0
    total = len(tests)
    
    for test_data in tests:
        if len(test_data) == 3:
            name, cmd, timeout = test_data
        else:
            name, cmd = test_data
            timeout = 300
        
        if run_test(name, cmd, timeout):
            passed += 1
        else:
            print(f"❌ {name} 失败，停止测试")
            break
    
    # 检查构建输出
    if passed == total:
        if check_build_output():
            passed += 1
            total += 1
    
    print(f"\n{'='*60}")
    print("最终测试总结")
    print('='*60)
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功，可以提交和推送。")
        
        # 显示修复摘要
        print(f"\n{'='*60}")
        print("修复摘要")
        print('='*60)
        print("✅ 更新了CI构建脚本，改进依赖安装和错误处理")
        print("✅ 修复了PyInstaller spec文件的隐藏导入")
        print("✅ 改进了GitHub Actions工作流配置")
        print("✅ 创建了CI专用测试脚本")
        print("✅ 添加了无头模式支持")
        print("✅ 优化了构建过程和错误报告")
        
        return 0
    else:
        print("⚠️ 部分测试失败，需要进一步调试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
