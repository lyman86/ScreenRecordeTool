#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installation Test Script - English version to avoid encoding issues
Verifies that all dependencies are correctly installed
"""

import sys
import platform
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("=" * 50)
    print("Testing Python Version")
    print("=" * 50)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("[ERROR] Python version too low, requires 3.8 or higher")
        return False
    else:
        print("[OK] Python version meets requirements")
        return True

def test_system_compatibility():
    """Test system compatibility"""
    print("\n" + "=" * 50)
    print("Testing System Compatibility")
    print("=" * 50)
    
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"System Version: {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    if system in ["Windows", "Darwin"]:
        print("[OK] Operating system supported")
        return True
    else:
        print("[ERROR] Operating system not supported, only Windows and macOS are supported")
        return False

def test_required_modules():
    """Test required modules"""
    print("\n" + "=" * 50)
    print("Testing Required Modules")
    print("=" * 50)
    
    required_modules = [
        ("PyQt6", "PyQt6"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("Pillow", "PIL"),
        ("MSS", "mss"),
        ("PSUtil", "psutil"),
        ("PyInstaller", "PyInstaller"),
    ]
    
    success_count = 0
    total_count = len(required_modules)
    
    for name, module in required_modules:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'Unknown')
            print(f"[OK] {name}: {version}")
            success_count += 1
        except ImportError as e:
            print(f"[ERROR] {name}: Not installed ({e})")
    
    print(f"\nModule test result: {success_count}/{total_count} successful")
    return success_count == total_count

def test_project_structure():
    """Test project structure"""
    print("\n" + "=" * 50)
    print("Testing Project Structure")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "src/config/settings.py",
        "src/ui/main_window.py",
        "src/core/screen_capture.py",
        "build_scripts/build_windows.py",
        "build_scripts/build_macos.py",
    ]
    
    success_count = 0
    total_count = len(required_files)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
            success_count += 1
        else:
            print(f"[ERROR] {file_path}: File not found")
    
    print(f"\nFile structure test result: {success_count}/{total_count} successful")
    return success_count == total_count

def test_config_loading():
    """Test configuration loading"""
    print("\n" + "=" * 50)
    print("Testing Configuration Loading")
    print("=" * 50)
    
    try:
        # Add src directory to Python path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from config.settings import AppConfig
        print(f"[OK] App Name: {AppConfig.APP_NAME}")
        print(f"[OK] App Version: {AppConfig.APP_VERSION}")
        print(f"[OK] App Author: {AppConfig.APP_AUTHOR}")
        return True
    except Exception as e:
        print(f"[ERROR] Configuration loading failed: {e}")
        return False

def test_gui_availability():
    """Test GUI availability"""
    print("\n" + "=" * 50)
    print("Testing GUI Availability")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # May not have display in CI environment
        import os
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            print("[WARN] CI environment detected, skipping GUI test")
            return True

        # Try to create application instance
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        print("[OK] PyQt6 GUI framework available")
        return True
    except Exception as e:
        print(f"[ERROR] GUI framework not available: {e}")
        return False

def main():
    """Main function"""
    print("Modern Screen Recorder - Installation Test")
    print("Test start time:", platform.platform())
    
    tests = [
        ("Python Version", test_python_version),
        ("System Compatibility", test_system_compatibility),
        ("Required Modules", test_required_modules),
        ("Project Structure", test_project_structure),
        ("Configuration Loading", test_config_loading),
        ("GUI Availability", test_gui_availability),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"[ERROR] {test_name} test exception: {e}")

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Passed tests: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("[SUCCESS] All tests passed! Application should run normally.")
        return 0
    else:
        print("[WARN] Some tests failed, please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
