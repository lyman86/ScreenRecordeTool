#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建自动化脚本
用于本地构建和CI/CD环境的自动化构建
"""

import os
import sys
import subprocess
import shutil
import platform
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime


class BuildAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.scripts_dir = self.project_root / "scripts"
        self.platform = platform.system().lower()
        
        # 确保目录存在
        self.dist_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
    
    def clean_build(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   删除: {dir_path}")
        
        # 清理 __pycache__ 目录
        for pycache in self.project_root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                print(f"   删除: {pycache}")
        
        # 重新创建目录
        self.dist_dir.mkdir(exist_ok=True)
        print("✅ 构建目录已清理")
    
    def run_command(self, command, check=True, cwd=None):
        """执行命令"""
        if cwd is None:
            cwd = self.project_root
        
        print(f"🔄 执行: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            if check:
                raise
            return e
    
    def install_dependencies(self):
        """安装依赖"""
        print("📦 安装依赖...")
        
        # 升级pip
        self.run_command(f"{sys.executable} -m pip install --upgrade pip")
        
        # 安装项目依赖
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self.run_command(f"{sys.executable} -m pip install -r {requirements_file}")
        
        # 安装构建工具
        self.run_command(f"{sys.executable} -m pip install pyinstaller")
        
        print("✅ 依赖安装完成")
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            # 安装测试依赖
            self.run_command(f"{sys.executable} -m pip install pytest pytest-cov", check=False)
            
            # 运行测试
            result = self.run_command(f"{sys.executable} -m pytest tests/ -v", check=False)
            if result.returncode == 0:
                print("✅ 所有测试通过")
            else:
                print("⚠️  测试失败或未找到测试文件")
        else:
            print("ℹ️  未找到测试目录，跳过测试")
    
    def build_executable(self):
        """构建可执行文件"""
        print(f"🔨 构建可执行文件 ({self.platform})...")
        
        # 运行主构建脚本
        build_script = self.project_root / "build.py"
        if build_script.exists():
            self.run_command(f"{sys.executable} {build_script}")
        else:
            # 使用默认的PyInstaller命令
            main_script = self.project_root / "main.py"
            if main_script.exists():
                cmd = f"{sys.executable} -m PyInstaller --onefile --windowed {main_script}"
                self.run_command(cmd)
        
        print("✅ 可执行文件构建完成")
    
    def create_portable_package(self):
        """创建便携版包"""
        print("📦 创建便携版包...")
        
        if self.platform == "windows":
            self._create_windows_portable()
        elif self.platform == "darwin":
            self._create_macos_package()
        elif self.platform == "linux":
            self._create_linux_package()
        
        print("✅ 便携版包创建完成")
    
    def _create_windows_portable(self):
        """创建Windows便携版"""
        portable_dir = self.dist_dir / "portable"
        portable_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件
        exe_file = self.dist_dir / "ScreenRecorder.exe"
        if exe_file.exists():
            shutil.copy2(exe_file, portable_dir)
        
        # 复制文档
        for doc in ["README.md", "LICENSE", "RELEASE_NOTES.md"]:
            doc_file = self.project_root / doc
            if doc_file.exists():
                shutil.copy2(doc_file, portable_dir)
        
        # 创建启动脚本
        start_script = portable_dir / "start.bat"
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write("@echo off\n")
            f.write("cd /d %~dp0\n")
            f.write("ScreenRecorder.exe\n")
            f.write("pause\n")
        
        # 创建ZIP包
        zip_file = self.dist_dir / f"ScreenRecorder-Windows-Portable-{datetime.now().strftime('%Y%m%d')}.zip"
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in portable_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(portable_dir)
                    zf.write(file_path, arcname)
        
        print(f"   创建: {zip_file}")
    
    def _create_macos_package(self):
        """创建macOS包"""
        app_file = self.dist_dir / "ScreenRecorder.app"
        if not app_file.exists():
            print("⚠️  未找到.app文件")
            return
        
        # 创建DMG包
        dmg_dir = self.dist_dir / "dmg"
        dmg_dir.mkdir(exist_ok=True)
        
        # 复制应用
        shutil.copytree(app_file, dmg_dir / "ScreenRecorder.app", dirs_exist_ok=True)
        
        # 复制文档
        for doc in ["README.md", "LICENSE"]:
            doc_file = self.project_root / doc
            if doc_file.exists():
                shutil.copy2(doc_file, dmg_dir)
        
        # 创建DMG
        dmg_file = self.dist_dir / f"ScreenRecorder-macOS-{datetime.now().strftime('%Y%m%d')}.dmg"
        cmd = f'hdiutil create -volname "ScreenRecorder" -srcfolder "{dmg_dir}" -ov -format UDZO "{dmg_file}"'
        self.run_command(cmd)
        
        print(f"   创建: {dmg_file}")
    
    def _create_linux_package(self):
        """创建Linux包"""
        exe_file = self.dist_dir / "ScreenRecorder"
        if not exe_file.exists():
            print("⚠️  未找到可执行文件")
            return
        
        # 创建包目录
        package_dir = self.dist_dir / "linux"
        package_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件
        shutil.copy2(exe_file, package_dir)
        
        # 复制文档
        for doc in ["README.md", "LICENSE", "RELEASE_NOTES.md"]:
            doc_file = self.project_root / doc
            if doc_file.exists():
                shutil.copy2(doc_file, package_dir)
        
        # 创建启动脚本
        start_script = package_dir / "start.sh"
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("cd \"$(dirname \"$0\")\"\n")
            f.write("./ScreenRecorder\n")
        
        # 设置执行权限
        os.chmod(start_script, 0o755)
        os.chmod(package_dir / "ScreenRecorder", 0o755)
        
        # 创建tar.gz包
        tar_file = self.dist_dir / f"ScreenRecorder-Linux-{datetime.now().strftime('%Y%m%d')}.tar.gz"
        with tarfile.open(tar_file, 'w:gz') as tf:
            tf.add(package_dir, arcname="ScreenRecorder")
        
        print(f"   创建: {tar_file}")
    
    def generate_checksums(self):
        """生成校验和文件"""
        print("🔐 生成校验和...")
        
        import hashlib
        
        checksums_file = self.dist_dir / "checksums.txt"
        
        with open(checksums_file, 'w', encoding='utf-8') as f:
            f.write(f"# ScreenRecorder 校验和\n")
            f.write(f"# 生成时间: {datetime.now().isoformat()}\n\n")
            
            for file_path in self.dist_dir.iterdir():
                if file_path.is_file() and file_path.name != "checksums.txt":
                    # 计算SHA256
                    sha256_hash = hashlib.sha256()
                    with open(file_path, 'rb') as bf:
                        for chunk in iter(lambda: bf.read(4096), b""):
                            sha256_hash.update(chunk)
                    
                    f.write(f"{sha256_hash.hexdigest()}  {file_path.name}\n")
        
        print(f"   创建: {checksums_file}")
        print("✅ 校验和生成完成")
    
    def full_build(self, clean=True, test=True, package=True):
        """完整构建流程"""
        print("🚀 开始完整构建流程...")
        print(f"📋 平台: {self.platform}")
        print(f"📁 项目目录: {self.project_root}")
        
        try:
            if clean:
                self.clean_build()
            
            self.install_dependencies()
            
            if test:
                self.run_tests()
            
            self.build_executable()
            
            if package:
                self.create_portable_package()
                self.generate_checksums()
            
            print("\n🎉 构建完成!")
            print(f"📦 输出目录: {self.dist_dir}")
            
            # 显示构建结果
            print("\n📋 构建产物:")
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"   {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"   {item.name}/ (目录)")
            
        except Exception as e:
            print(f"❌ 构建失败: {e}")
            raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="构建自动化脚本")
    parser.add_argument("--no-clean", action="store_true", help="不清理构建目录")
    parser.add_argument("--no-test", action="store_true", help="跳过测试")
    parser.add_argument("--no-package", action="store_true", help="不创建包")
    parser.add_argument("--only-build", action="store_true", help="只构建可执行文件")
    
    args = parser.parse_args()
    
    builder = BuildAutomation()
    
    try:
        if args.only_build:
            builder.build_executable()
        else:
            builder.full_build(
                clean=not args.no_clean,
                test=not args.no_test,
                package=not args.no_package
            )
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()