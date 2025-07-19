"""
macOS打包脚本
"""

import os
import sys
import shutil
import subprocess
import plistlib
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "main.spec"

def clean_build():
    """清理构建目录"""
    print("清理构建目录...")
    
    dirs_to_clean = [BUILD_DIR, DIST_DIR]
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"已删除: {dir_path}")
    
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"已删除: {SPEC_FILE}")

def create_spec_file():
    """创建PyInstaller spec文件"""
    print("创建spec文件...")
    
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
        'pillow',
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
    [],
    exclude_binaries=True,
    name='ScreenRecorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file='entitlements.plist',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScreenRecorder',
)

app = BUNDLE(
    coll,
    name='ScreenRecorder.app',
    icon='resources/icon.icns',
    bundle_identifier='com.yourcompany.screenrecorder',
    info_plist={
        'CFBundleName': '现代录屏工具',
        'CFBundleDisplayName': '现代录屏工具',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSCameraUsageDescription': '此应用需要访问摄像头以录制视频',
        'NSMicrophoneUsageDescription': '此应用需要访问麦克风以录制音频',
        'NSScreenCaptureDescription': '此应用需要录制屏幕内容',
        'LSMinimumSystemVersion': '10.15.0',
        'NSRequiresAquaSystemAppearance': False,
        'NSSupportsAutomaticGraphicsSwitching': True,
    },
)
'''
    
    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"已创建: {SPEC_FILE}")

def create_entitlements():
    """创建权限文件"""
    print("创建权限文件...")
    
    entitlements = {
        'com.apple.security.device.audio-input': True,
        'com.apple.security.device.camera': True,
        'com.apple.security.personal-information.location': False,
        'com.apple.security.files.user-selected.read-write': True,
        'com.apple.security.files.downloads.read-write': True,
        'com.apple.security.network.client': True,
        'com.apple.security.cs.allow-jit': True,
        'com.apple.security.cs.allow-unsigned-executable-memory': True,
        'com.apple.security.cs.disable-library-validation': True,
    }
    
    entitlements_file = PROJECT_ROOT / "entitlements.plist"
    with open(entitlements_file, 'wb') as f:
        plistlib.dump(entitlements, f)
    
    print(f"已创建: {entitlements_file}")

def create_icon():
    """创建应用图标"""
    print("检查应用图标...")
    
    icon_dir = PROJECT_ROOT / "resources"
    icon_dir.mkdir(exist_ok=True)
    
    icon_file = icon_dir / "icon.icns"
    if not icon_file.exists():
        print("警告: 未找到icon.icns文件，将使用默认图标")
        # 可以从PNG文件创建ICNS文件
        png_file = icon_dir / "icon.png"
        if png_file.exists():
            create_icns_from_png(png_file, icon_file)
    else:
        print(f"找到图标文件: {icon_file}")

def create_icns_from_png(png_file, icns_file):
    """从PNG文件创建ICNS文件"""
    try:
        # 使用sips命令转换（macOS内置工具）
        subprocess.run([
            'sips', '-s', 'format', 'icns', 
            str(png_file), '--out', str(icns_file)
        ], check=True)
        print(f"已从PNG创建ICNS: {icns_file}")
    except subprocess.CalledProcessError:
        print("无法从PNG创建ICNS文件")

def install_dependencies():
    """安装依赖"""
    print("检查并安装依赖...")
    
    try:
        # 检查PyInstaller
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("安装PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 安装其他依赖
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        print("安装项目依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

def build_app():
    """构建应用程序"""
    print("开始构建应用程序...")
    
    # 切换到项目根目录
    os.chdir(PROJECT_ROOT)
    
    # 运行PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("构建成功!")
        app_path = DIST_DIR / "ScreenRecorder.app"
        print(f"应用程序位置: {app_path}")
        return app_path
    else:
        print("构建失败!")
        print("错误输出:")
        print(result.stderr)
        return None

def sign_app(app_path):
    """签名应用程序"""
    print("签名应用程序...")
    
    # 检查是否有开发者证书
    try:
        result = subprocess.run([
            'security', 'find-identity', '-v', '-p', 'codesigning'
        ], capture_output=True, text=True)
        
        if "Developer ID Application" in result.stdout:
            print("找到开发者证书，开始签名...")
            
            # 签名应用程序
            subprocess.run([
                'codesign', '--force', '--deep', '--sign', 
                'Developer ID Application', str(app_path)
            ], check=True)
            
            print("签名完成")
            return True
        else:
            print("未找到开发者证书，跳过签名")
            return False
    except subprocess.CalledProcessError as e:
        print(f"签名失败: {e}")
        return False

def create_dmg(app_path):
    """创建DMG安装包"""
    print("创建DMG安装包...")
    
    dmg_name = "ScreenRecorder_v1.0.0.dmg"
    dmg_path = DIST_DIR / dmg_name
    
    # 删除已存在的DMG
    if dmg_path.exists():
        dmg_path.unlink()
    
    try:
        # 创建临时DMG
        temp_dmg = DIST_DIR / "temp.dmg"
        subprocess.run([
            'hdiutil', 'create', '-size', '200m', '-fs', 'HFS+',
            '-volname', 'ScreenRecorder', str(temp_dmg)
        ], check=True)
        
        # 挂载DMG
        mount_result = subprocess.run([
            'hdiutil', 'attach', str(temp_dmg)
        ], capture_output=True, text=True, check=True)
        
        # 获取挂载点
        mount_point = None
        for line in mount_result.stdout.split('\n'):
            if '/Volumes/ScreenRecorder' in line:
                mount_point = '/Volumes/ScreenRecorder'
                break
        
        if mount_point:
            # 复制应用程序
            shutil.copytree(app_path, f"{mount_point}/ScreenRecorder.app")
            
            # 创建应用程序文件夹的符号链接
            os.symlink('/Applications', f"{mount_point}/Applications")
            
            # 卸载DMG
            subprocess.run(['hdiutil', 'detach', mount_point], check=True)
            
            # 转换为压缩的DMG
            subprocess.run([
                'hdiutil', 'convert', str(temp_dmg), '-format', 'UDZO',
                '-o', str(dmg_path)
            ], check=True)
            
            # 删除临时DMG
            temp_dmg.unlink()
            
            print(f"DMG创建完成: {dmg_path}")
            return dmg_path
        else:
            print("无法找到挂载点")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"创建DMG失败: {e}")
        return None

def notarize_app(app_path):
    """公证应用程序（需要Apple ID）"""
    print("应用程序公证...")
    print("注意: 公证需要Apple ID和应用专用密码")
    print("请参考Apple官方文档进行公证配置")
    
    # 这里只是示例，实际公证需要配置Apple ID
    # xcrun altool --notarize-app --primary-bundle-id "com.yourcompany.screenrecorder" 
    #              --username "your-apple-id" --password "app-specific-password" 
    #              --file "ScreenRecorder.dmg"

def main():
    """主函数"""
    print("=" * 50)
    print("macOS打包脚本")
    print("=" * 50)
    
    try:
        # 1. 清理构建目录
        clean_build()
        
        # 2. 安装依赖
        install_dependencies()
        
        # 3. 创建必要文件
        create_entitlements()
        create_icon()
        create_spec_file()
        
        # 4. 构建应用程序
        app_path = build_app()
        if app_path and app_path.exists():
            print(f"\n构建完成: {app_path}")
            
            # 5. 签名应用程序
            signed = sign_app(app_path)
            
            # 6. 创建DMG
            dmg_path = create_dmg(app_path)
            
            print("\n构建完成!")
            print(f"应用程序: {app_path}")
            if dmg_path:
                print(f"安装包: {dmg_path}")
            
            print("\n后续步骤:")
            print("1. 测试应用程序")
            if not signed:
                print("2. 配置开发者证书并重新签名")
            print("3. 如需发布到App Store，请进行公证")
        else:
            print("\n构建失败!")
            return 1
    
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
