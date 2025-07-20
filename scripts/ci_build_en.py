#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI Environment Build Script - English version for GitHub Actions
Simplified version to avoid encoding issues on Windows
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def setup_environment():
    """Setup build environment"""
    print("Setting up build environment...")
    
    # Project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Create necessary directories
    dirs_to_create = ["resources", "build", "dist"]
    for dir_name in dirs_to_create:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return project_root

def install_dependencies():
    """Install dependencies"""
    print("Installing dependencies...")
    
    try:
        # Upgrade pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        
        # Install minimal dependency set
        minimal_deps = [
            "PyQt6",
            "opencv-python-headless",  # Use headless version to avoid GUI dependencies
            "pillow",
            "numpy",
            "mss",
            "psutil",
            "PyInstaller"
        ]
        
        for dep in minimal_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"✓ {dep} installed successfully")
            except subprocess.CalledProcessError:
                print(f"⚠ {dep} installation failed, skipping")
        
        print("Dependencies installation completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Dependencies installation failed: {e}")
        return False

def run_tests():
    """Run tests"""
    print("Running installation tests...")
    
    try:
        # Run installation test
        test_script = "test_installation_en.py" if Path("test_installation_en.py").exists() else "test_installation.py"
        result = subprocess.run([sys.executable, test_script],
                              capture_output=True, text=True)
        
        print("Test output:")
        print(result.stdout)
        
        if result.stderr:
            print("Test errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

def create_simple_spec():
    """Create simplified PyInstaller spec file"""
    print("Creating simplified spec file...")
    
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
        'mss',
        'PIL',
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
    
    # Adjust spec file for platform
    system = platform.system()
    if system == "Darwin":  # macOS
        spec_content += '''
app = BUNDLE(
    exe,
    name='ScreenRecorder.app',
    bundle_identifier='com.yourcompany.screenrecorder',
    info_plist={
        'CFBundleName': 'Modern Screen Recorder',
        'CFBundleDisplayName': 'Modern Screen Recorder',
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
    
    print(f"Created: {spec_file}")
    return spec_file

def build_executable():
    """Build executable file"""
    print("Building executable...")
    
    try:
        # Create spec file
        spec_file = create_simple_spec()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("Build successful!")
            
            # Check output files
            dist_dir = Path("dist")
            if dist_dir.exists():
                print("Build output:")
                for item in dist_dir.iterdir():
                    print(f"  {item}")
            
            return True
        else:
            print("Build failed!")
            print("Standard output:")
            print(result.stdout)
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("Build timeout")
        return False
    except Exception as e:
        print(f"Build process error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("CI Environment Build Script")
    print("=" * 50)
    
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Python Version: {sys.version}")
    
    try:
        # 1. Setup environment
        project_root = setup_environment()
        print(f"Project root: {project_root}")
        
        # 2. Install dependencies
        if not install_dependencies():
            print("Dependencies installation failed, exiting")
            return 1
        
        # 3. Run tests
        if not run_tests():
            print("Tests failed, but continuing with build")
        
        # 4. Build executable
        if build_executable():
            print("\n🎉 Build successful!")
            return 0
        else:
            print("\n❌ Build failed!")
            return 1
    
    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error during build: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
