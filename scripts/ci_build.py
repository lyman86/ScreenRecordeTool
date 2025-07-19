#!/usr/bin/env python3
"""
CI环境构建脚本 - 专门用于GitHub Actions自动打包
已验证在Windows和macOS环境下成功构建
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
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)

        # 首先尝试从requirements-ci.txt安装
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-ci.txt"], check=True)
            print("✅ 从requirements-ci.txt安装成功")
        except subprocess.CalledProcessError:
            print("⚠️ requirements-ci.txt安装失败，使用备用方案")

            # 备用：安装最小依赖集合
            minimal_deps = [
                "PyQt6>=6.6.0",
                "opencv-python-headless>=4.8.0",  # 使用headless版本避免GUI依赖
                "pillow>=10.0.0",
                "numpy>=1.24.0",
                "mss>=9.0.0",
                "psutil>=5.9.0",
                "PyInstaller>=6.0.0"
            ]

            for dep in minimal_deps:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                    print(f"✅ {dep} 安装成功")
                except subprocess.CalledProcessError:
                    print(f"⚠️ {dep} 安装失败，跳过")

        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
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
        # PyQt6 核心模块
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.sip',

        # 图像和视频处理
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',

        # 屏幕捕获
        'mss',
        'mss.windows',
        'mss.darwin',

        # 系统工具
        'psutil',

        # 项目模块 - 使用相对路径
        'src.config.settings',
        'src.ui.main_window',
        'src.ui.region_selector',
        'src.ui.settings_window',
        'src.ui.export_dialog',
        'src.core.screen_capture',
        'src.core.video_processor',
        'src.core.video_encoder',
        'src.core.audio_capture',
        'src.utils.config_manager',
        'src.utils.platform_utils',
        'src.utils.hotkey_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
    ],
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
        # 设置环境变量
        env = os.environ.copy()
        env['QT_QPA_PLATFORM'] = 'offscreen'

        # 创建spec文件
        spec_file = create_simple_spec()

        # 清理之前的构建
        build_dir = Path("build")
        dist_dir = Path("dist")

        if build_dir.exists():
            import shutil
            shutil.rmtree(build_dir)
            print("清理build目录")

        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
            print("清理dist目录")

        # 运行PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--log-level", "INFO",
            str(spec_file)
        ]

        print(f"执行命令: {' '.join(cmd)}")
        print("构建环境变量:")
        for key in ['QT_QPA_PLATFORM', 'DISPLAY']:
            print(f"  {key}: {env.get(key, 'Not set')}")

        result = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=900, env=env)  # 增加超时时间到15分钟

        print("PyInstaller输出:")
        print(result.stdout)

        if result.stderr:
            print("PyInstaller错误:")
            print(result.stderr)

        if result.returncode == 0:
            print("构建成功!")

            # 检查输出文件
            if dist_dir.exists():
                print("构建输出:")
                for item in dist_dir.rglob("*"):
                    if item.is_file():
                        size = item.stat().st_size
                        print(f"  {item} ({size} bytes)")

                # 验证主要可执行文件
                system = platform.system()
                if system == "Windows":
                    exe_file = dist_dir / "ScreenRecorder.exe"
                elif system == "Darwin":
                    exe_file = dist_dir / "ScreenRecorder.app"
                else:
                    exe_file = dist_dir / "ScreenRecorder"

                if exe_file.exists():
                    print(f"✅ 主要可执行文件已创建: {exe_file}")
                    return True
                else:
                    print(f"❌ 主要可执行文件未找到: {exe_file}")
                    return False
            else:
                print("❌ dist目录不存在")
                return False
        else:
            print(f"构建失败! 返回码: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("构建超时 (15分钟)")
        return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
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

        # 3. 构建可执行文件
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
