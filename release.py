#!/usr/bin/env python3
"""
发布脚本 - 自动化版本发布流程
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime

def get_current_version():
    """获取当前版本号"""
    try:
        # 从git标签获取最新版本
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "v0.0.0"  # 如果没有标签，返回初始版本

def parse_version(version_str):
    """解析版本号"""
    # 移除 'v' 前缀
    version = version_str.lstrip('v')
    parts = version.split('.')
    return [int(p) for p in parts]

def increment_version(version_str, increment_type='patch'):
    """递增版本号"""
    parts = parse_version(version_str)
    
    if increment_type == 'major':
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif increment_type == 'minor':
        parts[1] += 1
        parts[2] = 0
    else:  # patch
        parts[2] += 1
    
    return f"v{'.'.join(map(str, parts))}"

def update_changelog(version, changes=None):
    """更新CHANGELOG.md"""
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        # 创建新的CHANGELOG
        content = "# 更新日志\n\n"
    else:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    # 添加新版本条目
    date_str = datetime.now().strftime('%Y-%m-%d')
    new_entry = f"\n## [{version}] - {date_str}\n\n"
    
    if changes:
        for change in changes:
            new_entry += f"- {change}\n"
    else:
        new_entry += "- 版本更新\n"
    
    # 在第一个 ## 之前插入新条目
    if '## [' in content:
        parts = content.split('## [', 1)
        content = parts[0] + new_entry + "\n## [" + parts[1]
    else:
        content += new_entry
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新 CHANGELOG.md")

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
            return False
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Git状态检查失败")
        return False

def create_and_push_tag(version):
    """创建并推送标签"""
    try:
        # 创建标签
        subprocess.run(
            ['git', 'tag', '-a', version, '-m', f'Release {version}'],
            check=True
        )
        print(f"✅ 已创建标签: {version}")
        
        # 推送标签
        subprocess.run(
            ['git', 'push', 'origin', version],
            check=True
        )
        print(f"✅ 已推送标签到远程仓库")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 标签操作失败: {e}")
        return False

def trigger_manual_build():
    """触发手动构建"""
    print("\n🔨 触发手动构建...")
    print("请访问以下链接手动触发构建:")
    
    # 获取仓库信息
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True, text=True, check=True
        )
        remote_url = result.stdout.strip()
        
        # 解析GitHub仓库信息
        if 'github.com' in remote_url:
            # 提取用户名和仓库名
            match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', remote_url)
            if match:
                username, repo = match.groups()
                actions_url = f"https://github.com/{username}/{repo}/actions/workflows/build-release.yml"
                print(f"🔗 {actions_url}")
                print("\n📝 操作步骤:")
                print("1. 点击上面的链接")
                print("2. 点击 'Run workflow' 按钮")
                print("3. 输入版本号 (如果需要)")
                print("4. 点击 'Run workflow' 确认")
                return True
    except subprocess.CalledProcessError:
        pass
    
    print("❌ 无法获取仓库信息，请手动访问GitHub Actions页面")
    return False

def main():
    """主函数"""
    print("🚀 现代录屏工具 - 发布脚本")
    print("=" * 40)
    
    # 检查是否在Git仓库中
    if not Path('.git').exists():
        print("❌ 当前目录不是Git仓库")
        return 1
    
    # 获取当前版本
    current_version = get_current_version()
    print(f"📦 当前版本: {current_version}")
    
    # 选择发布类型
    print("\n🎯 选择发布类型:")
    print("1. Patch (修复版本, 如 v1.0.0 -> v1.0.1)")
    print("2. Minor (功能版本, 如 v1.0.0 -> v1.1.0)")
    print("3. Major (重大版本, 如 v1.0.0 -> v2.0.0)")
    print("4. 自定义版本号")
    print("5. 仅触发构建 (不创建新版本)")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == '5':
        # 仅触发构建
        trigger_manual_build()
        return 0
    
    # 确定新版本号
    if choice == '1':
        new_version = increment_version(current_version, 'patch')
    elif choice == '2':
        new_version = increment_version(current_version, 'minor')
    elif choice == '3':
        new_version = increment_version(current_version, 'major')
    elif choice == '4':
        new_version = input("请输入版本号 (如 v1.2.3): ").strip()
        if not new_version.startswith('v'):
            new_version = 'v' + new_version
    else:
        print("❌ 无效选择")
        return 1
    
    print(f"\n🎉 新版本: {new_version}")
    
    # 确认发布
    confirm = input(f"\n确认发布版本 {new_version}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 发布已取消")
        return 1
    
    # 检查Git状态
    if not check_git_status():
        commit = input("\n是否提交当前更改? (y/N): ").strip().lower()
        if commit == 'y':
            try:
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', f'Prepare release {new_version}'], check=True)
                print("✅ 已提交更改")
            except subprocess.CalledProcessError:
                print("❌ 提交失败")
                return 1
        else:
            print("❌ 请先提交或暂存更改")
            return 1
    
    # 更新CHANGELOG
    changes = []
    print("\n📝 请输入更新内容 (每行一条，空行结束):")
    while True:
        change = input().strip()
        if not change:
            break
        changes.append(change)
    
    if changes:
        update_changelog(new_version, changes)
        
        # 提交CHANGELOG更改
        try:
            subprocess.run(['git', 'add', 'CHANGELOG.md'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Update CHANGELOG for {new_version}'], check=True)
            print("✅ 已提交CHANGELOG更改")
        except subprocess.CalledProcessError:
            print("⚠️  CHANGELOG提交失败，但继续发布流程")
    
    # 创建并推送标签
    if create_and_push_tag(new_version):
        print(f"\n🎉 版本 {new_version} 发布成功!")
        print("\n📋 后续步骤:")
        print("1. GitHub Actions 将自动开始构建")
        print("2. 构建完成后将自动创建Release")
        print("3. 请访问GitHub Releases页面查看发布状态")
        
        # 显示GitHub链接
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, check=True
            )
            remote_url = result.stdout.strip()
            
            if 'github.com' in remote_url:
                match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', remote_url)
                if match:
                    username, repo = match.groups()
                    print(f"\n🔗 GitHub Actions: https://github.com/{username}/{repo}/actions")
                    print(f"🔗 Releases: https://github.com/{username}/{repo}/releases")
        except subprocess.CalledProcessError:
            pass
        
        return 0
    else:
        print("❌ 发布失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())