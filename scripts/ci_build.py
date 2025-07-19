#!/usr/bin/env python3
"""
CI环境构建脚本 - 简化版本，专门用于GitHub Actions
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def setup_environment():
    """设置构建环境"""
    print("设置构建环境...")
    
    # 项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 创建必要的目录
    dirs_to_create = ["resources", "build", "dist"]
    for dir_name in dirs_to_create:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"创建目录: {dir_path}")
    
    return project_root

def install_dependencies():
    """安装依赖"""
    print("安装依赖...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # 安装项目依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print("运行测试...")
    
    try:
        # 运行安装测试
        result = subprocess.run([sys.executable, "test_installation.py"], 
                              capture_output=True, text=True)
        
        print("测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("测试错误:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"测试运行失败: {e}")
        return False

def create_simple_spec():
    """创建简化的PyInstaller spec文件"""
    print("创建简化的spec文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'cv2',
        'numpy',
        'pyaudio',
        'mss',
        'keyboard',
        'pynput',
        'PIL',
        'imageio',
        'psutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ScreenRecorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # 根据平台调整spec文件
    system = platform.system()
    if system == "Darwin":  # macOS
        spec_content += '''
app = BUNDLE(
    exe,
    name='ScreenRecorder.app',
    bundle_identifier='com.yourcompany.screenrecorder',
    info_plist={
        'CFBundleName': '现代录屏工具',
        'CFBundleDisplayName': '现代录屏工具',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    },
)
'''
    
    spec_file = Path("main.spec")
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"已创建: {spec_file}")
    return spec_file

def build_executable():
    """构建可执行文件"""
    print("构建可执行文件...")
    
    try:
        # 创建spec文件
        spec_file = create_simple_spec()
        
        # 运行PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("构建成功!")
            
            # 检查输出文件
            dist_dir = Path("dist")
            if dist_dir.exists():
                print("构建输出:")
                for item in dist_dir.iterdir():
                    print(f"  {item}")
            
            return True
        else:
            print("构建失败!")
            print("标准输出:")
            print(result.stdout)
            print("错误输出:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("构建超时")
        return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("CI环境构建脚本")
    print("=" * 50)
    
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"Python版本: {sys.version}")
    
    try:
        # 1. 设置环境
        project_root = setup_environment()
        print(f"项目根目录: {project_root}")
        
        # 2. 安装依赖
        if not install_dependencies():
            print("依赖安装失败，退出")
            return 1
        
        # 3. 运行测试
        if not run_tests():
            print("测试失败，但继续构建")
        
        # 4. 构建可执行文件
        if build_executable():
            print("\n🎉 构建成功!")
            return 0
        else:
            print("\n❌ 构建失败!")
            return 1
    
    except KeyboardInterrupt:
        print("\n构建被用户中断")
        return 1
    except Exception as e:
        print(f"\n构建过程中发生未预期的错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
