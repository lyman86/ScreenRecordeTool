#!/usr/bin/env python3
"""
简单构建脚本 - 用于GitHub Actions的备用构建方案
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("简单构建脚本")
    print("="*50)
    
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"Python版本: {sys.version}")
    
    # 项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 创建必要的目录
    for dir_name in ["resources", "build", "dist"]:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"创建目录: {dir_path}")
    
    # 设置环境变量
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        # 基本的PyInstaller命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "ScreenRecorder",
            "--add-data", "src:src",
            "--add-data", "resources:resources",
            "--hidden-import", "PyQt6.QtCore",
            "--hidden-import", "PyQt6.QtGui", 
            "--hidden-import", "PyQt6.QtWidgets",
            "--hidden-import", "cv2",
            "--hidden-import", "numpy",
            "--hidden-import", "PIL",
            "--hidden-import", "mss",
            "--hidden-import", "psutil",
            "main.py"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        print("构建输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 构建成功!")
            
            # 检查输出文件
            dist_dir = Path("dist")
            if dist_dir.exists():
                print("构建文件:")
                for item in dist_dir.iterdir():
                    if item.is_file():
                        size = item.stat().st_size
                        print(f"  {item.name} ({size:,} bytes)")
            
            return 0
        else:
            print("❌ 构建失败!")
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ 构建超时")
        return 1
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
