"""
通用构建脚本
"""

import sys
import platform
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("现代录屏工具 - 构建脚本")
    print("=" * 40)
    
    # 检测平台
    current_platform = platform.system()
    print(f"当前平台: {current_platform}")
    
    # 项目根目录
    project_root = Path(__file__).parent
    build_scripts_dir = project_root / "build_scripts"
    
    if current_platform == "Windows":
        build_script = build_scripts_dir / "build_windows.py"
        print("使用Windows构建脚本...")
    elif current_platform == "Darwin":
        build_script = build_scripts_dir / "build_macos.py"
        print("使用macOS构建脚本...")
    else:
        print(f"不支持的平台: {current_platform}")
        print("目前仅支持Windows和macOS")
        return 1
    
    if not build_script.exists():
        print(f"构建脚本不存在: {build_script}")
        return 1
    
    # 执行构建脚本
    try:
        result = subprocess.run([sys.executable, str(build_script)], 
                              cwd=project_root)
        return result.returncode
    except Exception as e:
        print(f"执行构建脚本失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
