#!/usr/bin/env python3
"""
一键触发GitHub自动打包脚本
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def get_current_version():
    """获取当前版本号"""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "v1.0.0"

def increment_version(version, increment_type='patch'):
    """递增版本号"""
    # 移除 'v' 前缀
    if version.startswith('v'):
        version = version[1:]
    
    parts = version.split('.')
    if len(parts) != 3:
        return "v1.0.0"
    
    major, minor, patch = map(int, parts)
    
    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"v{major}.{minor}.{patch}"

def create_and_push_tag(version, message=None):
    """创建并推送标签"""
    if not message:
        message = f"Release {version}"
    
    try:
        # 创建标签
        subprocess.run(
            ['git', 'tag', '-a', version, '-m', message],
            check=True
        )
        print(f"✅ 创建标签: {version}")
        
        # 推送标签
        subprocess.run(
            ['git', 'push', 'origin', version],
            check=True
        )
        print(f"✅ 推送标签: {version}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 标签操作失败: {e}")
        return False

def check_git_status():
    """检查Git状态"""
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, check=True
        )
        
        if result.stdout.strip():
            print("⚠️  检测到未提交的更改:")
            print(result.stdout)
            
            response = input("是否要提交这些更改? (y/N): ").strip().lower()
            if response == 'y':
                # 添加所有更改
                subprocess.run(['git', 'add', '.'], check=True)
                
                # 提交更改
                commit_msg = input("请输入提交信息 (默认: Update for release): ").strip()
                if not commit_msg:
                    commit_msg = "Update for release"
                
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                print("✅ 更改已提交")
                
                # 推送更改
                subprocess.run(['git', 'push'], check=True)
                print("✅ 更改已推送")
            else:
                print("❌ 请先提交或暂存更改")
                return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git状态检查失败: {e}")
        return False

def show_build_links():
    """显示构建链接"""
    print("\n🔗 GitHub链接:")
    print("📦 Actions: https://github.com/lyman86/ScreenRecordeTool/actions")
    print("🚀 Releases: https://github.com/lyman86/ScreenRecordeTool/releases")
    print("🔨 手动构建: https://github.com/lyman86/ScreenRecordeTool/actions/workflows/build-test.yml")

def main():
    """主函数"""
    print("🚀 一键触发GitHub自动打包")
    print("=" * 40)
    
    # 检查是否在正确的目录
    if not Path('main.py').exists():
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 检查Git状态
    print("🔍 检查Git状态...")
    if not check_git_status():
        return 1
    
    # 获取当前版本
    current_version = get_current_version()
    print(f"📋 当前版本: {current_version}")
    
    # 选择版本递增类型
    print("\n📈 选择版本递增类型:")
    print("1. Patch (修复) - 例如: v1.0.0 -> v1.0.1")
    print("2. Minor (功能) - 例如: v1.0.0 -> v1.1.0")
    print("3. Major (重大) - 例如: v1.0.0 -> v2.0.0")
    print("4. 自定义版本号")
    print("5. 仅触发当前版本的构建")
    
    choice = input("\n请选择 (1-5, 默认1): ").strip()
    
    if choice == '2':
        new_version = increment_version(current_version, 'minor')
    elif choice == '3':
        new_version = increment_version(current_version, 'major')
    elif choice == '4':
        custom_version = input("请输入自定义版本号 (例如: v1.2.3): ").strip()
        if not custom_version.startswith('v'):
            custom_version = 'v' + custom_version
        new_version = custom_version
    elif choice == '5':
        # 仅触发构建，不创建新标签
        print(f"\n🔨 触发当前版本 {current_version} 的构建...")
        print("\n请手动访问以下链接触发构建:")
        show_build_links()
        return 0
    else:
        new_version = increment_version(current_version, 'patch')
    
    print(f"\n📦 新版本: {new_version}")
    
    # 确认
    response = input(f"\n确认创建并推送标签 {new_version}? (Y/n): ").strip().lower()
    if response == 'n':
        print("❌ 操作已取消")
        return 0
    
    # 输入发布说明
    release_message = input(f"\n请输入发布说明 (默认: Release {new_version}): ").strip()
    if not release_message:
        release_message = f"Release {new_version}"
    
    # 创建并推送标签
    print(f"\n🏷️  创建标签 {new_version}...")
    if create_and_push_tag(new_version, release_message):
        print(f"\n🎉 成功！标签 {new_version} 已推送到GitHub")
        print("\n⏳ GitHub Actions将自动开始构建...")
        print("   - Windows可执行文件")
        print("   - macOS应用程序")
        print("   - 自动创建Release")
        
        show_build_links()
        
        print("\n💡 提示:")
        print("- 构建通常需要5-15分钟")
        print("- 首次构建可能需要更长时间")
        print("- 构建完成后会自动创建Release")
        print("- 可以在Actions页面监控构建进度")
        
        return 0
    else:
        print("❌ 标签创建失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())