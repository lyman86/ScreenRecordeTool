#!/usr/bin/env python3
"""
验证修复脚本 - 本地测试CI构建修复
"""

import sys
import os
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("标准输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("命令执行超时")
        return False
    except Exception as e:
        print(f"命令执行失败: {e}")
        return False

def main():
    """主函数"""
    print("验证CI构建修复")
    print("="*50)
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"工作目录: {project_root}")
    
    # 设置环境变量
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    tests = [
        # 1. 测试CI环境
        ([sys.executable, "test_ci_build.py"], "CI环境测试"),
        
        # 2. 测试依赖安装
        ([sys.executable, "-m", "pip", "install", "-r", "requirements-ci.txt"], "安装CI依赖"),
        
        # 3. 验证关键导入
        ([sys.executable, "-c", "import PyQt6; import cv2; import numpy; import PIL; import mss; import psutil; import PyInstaller; print('All imports OK')"], "验证关键导入"),
        
        # 4. 测试构建脚本
        ([sys.executable, "scripts/ci_build.py"], "执行CI构建"),
    ]
    
    passed = 0
    total = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
            print(f"✅ {description} - 成功")
        else:
            print(f"❌ {description} - 失败")
    
    print(f"\n{'='*50}")
    print("验证总结")
    print('='*50)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有验证通过！修复成功。")
        return 0
    else:
        print("⚠️ 部分验证失败，需要进一步修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
