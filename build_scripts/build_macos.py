"""
macOS Build Script
"""

import os
import sys
import shutil
import subprocess
import plistlib
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

def create_spec_file():
    """Create PyInstaller spec file"""
    print("Creating spec file...")
    
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
        'CFBundleName': 'Modern Screen Recorder',
        'CFBundleDisplayName': 'Modern Screen Recorder',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSCameraUsageDescription': 'This app needs access to camera for video recording',
        'NSMicrophoneUsageDescription': 'This app needs access to microphone for audio recording',
        'NSScreenCaptureDescription': 'This app needs to record screen content',
        'LSMinimumSystemVersion': '10.15.0',
        'NSRequiresAquaSystemAppearance': False,
        'NSSupportsAutomaticGraphicsSwitching': True,
    },
)
'''
    
    with open(SPEC_FILE, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Created: {SPEC_FILE}")

def create_entitlements():
    """Create entitlements file"""
    print("Creating entitlements file...")
    
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
    
    print(f"Created: {entitlements_file}")

def create_icon():
    """Create application icon"""
    print("Checking application icon...")
    
    icon_dir = PROJECT_ROOT / "resources"
    icon_dir.mkdir(exist_ok=True)
    
    icon_file = icon_dir / "icon.icns"
    if not icon_file.exists():
        print("Warning: icon.icns file not found, will use default icon")
        # Can create ICNS file from PNG file
        png_file = icon_dir / "icon.png"
        if png_file.exists():
            create_icns_from_png(png_file, icon_file)
    else:
        print(f"Found icon file: {icon_file}")

def create_icns_from_png(png_file, icns_file):
    """Create ICNS file from PNG file"""
    try:
        # Use sips command for conversion (macOS built-in tool)
        subprocess.run([
            'sips', '-s', 'format', 'icns', 
            str(png_file), '--out', str(icns_file)
        ], check=True)
        print(f"Created ICNS from PNG: {icns_file}")
    except subprocess.CalledProcessError:
        print("Unable to create ICNS file from PNG")

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
    
    # Install portaudio for PyAudio
    print("Installing portaudio for PyAudio...")
    try:
        subprocess.run(["brew", "install", "portaudio"], check=True)
        print("portaudio installed successfully")
    except subprocess.CalledProcessError:
        print("Warning: Failed to install portaudio via brew")
        print("Please install portaudio manually: brew install portaudio")
    
    # Install other dependencies
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        print("Installing project dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

def build_app():
    """Build application"""
    print("Starting to build application...")
    
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
        app_path = DIST_DIR / "ScreenRecorder.app"
        print(f"Application location: {app_path}")
        return app_path
    else:
        print("Build failed!")
        print("Error output:")
        print(result.stderr)
        return None

def sign_app(app_path):
    """Sign application"""
    print("Signing application...")
    
    # Check if developer certificate exists
    try:
        result = subprocess.run([
            'security', 'find-identity', '-v', '-p', 'codesigning'
        ], capture_output=True, text=True)
        
        if "Developer ID Application" in result.stdout:
            print("Found developer certificate, starting to sign...")
            
            # Sign application
            subprocess.run([
                'codesign', '--force', '--deep', '--sign', 
                'Developer ID Application', str(app_path)
            ], check=True)
            
            print("Signing completed")
            return True
        else:
            print("Developer certificate not found, skipping signing")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Signing failed: {e}")
        return False

def create_dmg(app_path):
    """Create DMG installer"""
    print("Creating DMG installer...")
    
    dmg_name = "ScreenRecorder_v1.0.0.dmg"
    dmg_path = DIST_DIR / dmg_name
    
    # Delete existing DMG
    if dmg_path.exists():
        dmg_path.unlink()
    
    try:
        # Create temporary DMG
        temp_dmg = DIST_DIR / "temp.dmg"
        subprocess.run([
            'hdiutil', 'create', '-size', '200m', '-fs', 'HFS+',
            '-volname', 'ScreenRecorder', str(temp_dmg)
        ], check=True)
        
        # Mount DMG
        mount_result = subprocess.run([
            'hdiutil', 'attach', str(temp_dmg)
        ], capture_output=True, text=True, check=True)
        
        # Get mount point
        mount_point = None
        for line in mount_result.stdout.split('\n'):
            if '/Volumes/ScreenRecorder' in line:
                mount_point = '/Volumes/ScreenRecorder'
                break
        
        if mount_point:
            # Copy application
            shutil.copytree(app_path, f"{mount_point}/ScreenRecorder.app")
            
            # Create symbolic link to Applications folder
            os.symlink('/Applications', f"{mount_point}/Applications")
            
            # Unmount DMG
            subprocess.run(['hdiutil', 'detach', mount_point], check=True)
            
            # Convert to compressed DMG
            subprocess.run([
                'hdiutil', 'convert', str(temp_dmg), '-format', 'UDZO',
                '-o', str(dmg_path)
            ], check=True)
            
            # Delete temporary DMG
            temp_dmg.unlink()
            
            print(f"DMG creation completed: {dmg_path}")
            return dmg_path
        else:
            print("Unable to find mount point")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"DMG creation failed: {e}")
        return None

def notarize_app(app_path):
    """Notarize application (requires Apple ID)"""
    print("App notarization...")
    print("Note: Notarization requires Apple ID and app-specific password")
    print("Please refer to Apple official documentation for notarization configuration")
    
    # This is just an example, actual notarization requires Apple ID configuration
    # xcrun altool --notarize-app --primary-bundle-id "com.yourcompany.screenrecorder" 
    #              --username "your-apple-id" --password "app-specific-password" 
    #              --file "ScreenRecorder.dmg"

def main():
    """Main function"""
    print("=" * 50)
    print("macOS Build Script")
    print("=" * 50)
    
    try:
        # 1. Clean build directory
        clean_build()
        
        # 2. Install dependencies
        install_dependencies()
        
        # 3. Create necessary files
        create_entitlements()
        create_icon()
        create_spec_file()
        
        # 4. Build application
        app_path = build_app()
        if app_path and app_path.exists():
            print(f"\nBuild completed: {app_path}")
            
            # 5. Sign application
            signed = sign_app(app_path)
            
            # 6. Create DMG
            dmg_path = create_dmg(app_path)
            
            print("\nBuild completed!")
            print(f"Application: {app_path}")
            if dmg_path:
                print(f"Installer: {dmg_path}")
            
            print("\nNext steps:")
            print("1. Test the application")
            if not signed:
                print("2. Configure developer certificate and re-sign")
            print("3. If publishing to App Store, perform notarization")
        else:
            print("\nBuild failed!")
            return 1
    
    except Exception as e:
        print(f"Error occurred during build: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
