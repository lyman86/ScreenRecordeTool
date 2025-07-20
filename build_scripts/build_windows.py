"""
Windows packaging script
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "main.spec"

def clean_build():
    """Clean build directory"""
    print("Cleaning build directory...")
    
    dirs_to_clean = [BUILD_DIR, DIST_DIR]
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Deleted: {dir_path}")
    
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"Deleted: {SPEC_FILE}")

def create_spec_file(has_icon=False):
    """Create PyInstaller spec file"""
    print("Creating spec file...")
    
    # Determine icon path based on has_icon parameter
    icon_value = "'resources/icon.ico'" if has_icon else "None"
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

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
    hooksconfig=[],
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
    icon={icon_value},
    version='version_info.txt'
)
"""
    
    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Created: {SPEC_FILE}")

def create_version_info():
    """Create version info file"""
    print("Creating version info file...")
    
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
    
    print(f"Created: {version_file}")

def create_icon():
    """Create application icon"""
    print("Checking application icon...")
    
    icon_dir = PROJECT_ROOT / "resources"
    icon_dir.mkdir(exist_ok=True)
    
    icon_file = icon_dir / "icon.ico"
    if not icon_file.exists():
        print("Warning: icon.ico file not found, skipping icon setup")
        print("The executable will use the default PyInstaller icon")
        return False
    
    # Check if the icon file is valid
    try:
        from PIL import Image
        with Image.open(icon_file) as img:
            print(f"Found valid icon file: {icon_file} ({img.format}, {img.size})")
            return True
    except Exception as e:
        print(f"Warning: icon.ico file exists but is not a valid image: {e}")
        print("The executable will use the default PyInstaller icon")
        return False

def install_dependencies():
    """Install dependencies"""
    print("Checking and installing dependencies...")
    
    try:
        # Check PyInstaller
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Install other dependencies
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        print("Installing project dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

def build_executable():
    """Build executable"""
    print("Starting to build executable...")
    
    # Change to project root directory
    os.chdir(PROJECT_ROOT)
    
    # Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE)
    ]
    
    print(f"Executing command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Build successful!")
        print(f"Executable location: {DIST_DIR / 'ScreenRecorder.exe'}")
    else:
        print("Build failed!")
        print("Error output:")
        print(result.stderr)
        return False
    
    return True



def create_installer():
    """Create installer (using NSIS)"""
    print("Creating installer...")
    
    nsis_script = PROJECT_ROOT / "installer.nsi"
    nsis_content = '''
; Modern Screen Recorder Installation Script

!define APP_NAME "Modern Screen Recorder"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company"
!define APP_EXE "ScreenRecorder.exe"

; Include modern UI
!include "MUI2.nsh"

; Basic settings
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
    """Main function"""
    print("=" * 50)
    print("Windows Build Script")
    print("=" * 50)
    
    try:
        # 1. Clean build directory
        clean_build()
        
        # 2. Install dependencies
        install_dependencies()
        
        # 3. Create necessary files
        create_version_info()
        has_icon = create_icon()
        create_spec_file(has_icon)
        
        # 4. Build executable
        if build_executable():
            print("\nBuild completed!")
            print(f"Executable: {DIST_DIR / 'ScreenRecorder.exe'}")
            
            # 5. Create installer script
            create_installer()
            
            print("\nNext steps:")
            print("1. Test the executable")
            print("2. Use NSIS to compile installer")
            print("3. Test the installer")
        else:
            print("\nBuild failed!")
            return 1
    
    except Exception as e:
        print(f"Error occurred during build: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
