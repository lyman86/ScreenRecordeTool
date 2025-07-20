"""
Windows打包脚本
"""

import os
import sys
import shutil
import subprocess
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ScreenRecorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico',
    version='version_info.txt'
)
'''
    
    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"已创建: {SPEC_FILE}")

def create_version_info():
    """创建版本信息文件"""
    print("创建版本信息文件...")
    
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Your Company'),
        StringStruct(u'FileDescription', u'Modern Screen Recorder'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'ScreenRecorder'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 Your Company'),
        StringStruct(u'OriginalFilename', u'ScreenRecorder.exe'),
        StringStruct(u'ProductName', u'Modern Screen Recorder'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = PROJECT_ROOT / "version_info.txt"
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print(f"已创建: {version_file}")

def create_icon():
    """创建应用图标"""
    print("检查应用图标...")
    
    icon_dir = PROJECT_ROOT / "resources"
    icon_dir.mkdir(exist_ok=True)
    
    icon_file = icon_dir / "icon.ico"
    if not icon_file.exists():
        print("警告: 未找到icon.ico文件，将使用默认图标")
        # 这里可以创建一个简单的默认图标或从网络下载
    else:
        print(f"找到图标文件: {icon_file}")

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

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
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
        print(f"可执行文件位置: {DIST_DIR / 'ScreenRecorder.exe'}")
    else:
        print("构建失败!")
        print("错误输出:")
        print(result.stderr)
        return False
    
    return True

def create_installer():
    """创建安装程序（使用NSIS）"""
    print("Creating installer...")
    
    nsis_script = PROJECT_ROOT / "installer.nsi"
    nsis_content = '''
; Modern Screen Recorder Installation Script

!define APP_NAME "Modern Screen Recorder"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company"
!define APP_EXE "ScreenRecorder.exe"

; 包含现代UI
!include "MUI2.nsh"

; 基本设置
Name "${APP_NAME}"
OutFile "ScreenRecorder_Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
InstallDirRegKey HKCU "Software\\${APP_NAME}" ""
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\\icon.ico"
!define MUI_UNICON "resources\\icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Installation Section
Section "Main Program" SecMain
    SetOutPath "$INSTDIR"
    File /r "dist\\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    
    ; Write registry
    WriteRegStr HKCU "Software\\${APP_NAME}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; Uninstall Section
Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APP_NAME}\\*.*"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    
    DeleteRegKey HKCU "Software\\${APP_NAME}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
SectionEnd
'''
    
    with open(nsis_script, 'w', encoding='utf-8') as f:
        f.write(nsis_content)
    
    print(f"NSIS script created: {nsis_script}")
    print("Please use NSIS compiler to compile installer.nsi file to create installer")

def main():
    """主函数"""
    print("=" * 50)
    print("Windows Build Script")
    print("=" * 50)
    
    try:
        # 1. 清理构建目录
        clean_build()
        
        # 2. 安装依赖
        install_dependencies()
        
        # 3. 创建必要文件
        create_version_info()
        create_icon()
        create_spec_file()
        
        # 4. 构建可执行文件
        if build_executable():
            print("\n构建完成!")
            print(f"可执行文件: {DIST_DIR / 'ScreenRecorder.exe'}")
            
            # 5. 创建安装程序脚本
            create_installer()
            
            print("\n后续步骤:")
            print("1. 测试可执行文件")
            print("2. 使用NSIS编译安装程序")
            print("3. 测试安装程序")
        else:
            print("\n构建失败!")
            return 1
    
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
