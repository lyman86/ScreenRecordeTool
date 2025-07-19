#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布脚本
用于自动化版本管理和GitHub发布流程
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path


class AutoReleaseManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.version_file = self.project_root / "src" / "config" / "version.py"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        
    def get_current_version(self):
        """获取当前版本号"""
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'__version__\s*=\s*["\']([^"\']*)["\'']', content)
                if match:
                    return match.group(1)
        return "1.0.0"
    
    def bump_version(self, version_type="patch"):
        """升级版本号"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        
        # 更新版本文件
        self.update_version_file(new_version)
        return new_version
    
    def update_version_file(self, version):
        """更新版本文件"""
        version_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息
"""

__version__ = "{version}"
__author__ = "ScreenRecorder Team"
__email__ = "contact@screenrecorder.com"
__description__ = "跨平台屏幕录制工具"
'''
        
        # 确保目录存在
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(version_content)
        
        print(f"✅ 版本文件已更新: {version}")
    
    def update_changelog(self, version, changes=None):
        """更新变更日志"""
        if not changes:
            changes = [
                "Bug修复和性能优化",
                "改进用户界面",
                "增强稳定性"
            ]
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        new_entry = f"""## [{version}] - {date_str}

### 新增
- 功能改进和优化

### 修复
{chr(10).join(f"- {change}" for change in changes)}

### 变更
- 代码重构和优化

"""
        
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在第一个 ## 之前插入新条目
            if "## [" in content:
                parts = content.split("## [", 1)
                new_content = parts[0] + new_entry + "## [" + parts[1]
            else:
                new_content = new_entry + content
        else:
            new_content = f"# 更新日志\n\n{new_entry}"
        
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 变更日志已更新")
    
    def run_command(self, command, check=True):
        """执行命令"""
        print(f"🔄 执行命令: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            raise
    
    def check_git_status(self):
        """检查Git状态"""
        result = self.run_command("git status --porcelain")
        if result.stdout.strip():
            print("⚠️  工作目录有未提交的更改:")
            print(result.stdout)
            return False
        return True
    
    def commit_and_tag(self, version):
        """提交更改并创建标签"""
        # 添加所有更改
        self.run_command("git add .")
        
        # 提交更改
        commit_msg = f"Release v{version}: 版本更新和功能改进"
        self.run_command(f'git commit -m "{commit_msg}"')
        
        # 创建标签
        tag_msg = f"Release v{version}"
        self.run_command(f'git tag -a v{version} -m "{tag_msg}"')
        
        print(f"✅ 已创建标签: v{version}")
    
    def push_to_github(self, version):
        """推送到GitHub"""
        # 推送代码
        self.run_command("git push origin main")
        
        # 推送标签
        self.run_command(f"git push origin v{version}")
        
        print(f"✅ 已推送到GitHub: v{version}")
    
    def create_release(self, version_type="patch", changes=None, push=True):
        """创建发布"""
        print("🚀 开始自动发布流程...")
        
        # 检查Git状态
        if not self.check_git_status():
            response = input("是否继续？(y/N): ")
            if response.lower() != 'y':
                print("❌ 发布已取消")
                return
        
        # 升级版本
        new_version = self.bump_version(version_type)
        print(f"📦 新版本: {new_version}")
        
        # 更新变更日志
        self.update_changelog(new_version, changes)
        
        # 提交并创建标签
        self.commit_and_tag(new_version)
        
        if push:
            # 推送到GitHub
            self.push_to_github(new_version)
            
            print(f"\n🎉 发布完成!")
            print(f"📋 版本: v{new_version}")
            print(f"🔗 GitHub Actions 将自动构建并创建 Release")
            print(f"🌐 查看进度: https://github.com/YOUR_USERNAME/ScreenRecordeTool/actions")
        else:
            print(f"\n✅ 本地发布准备完成: v{new_version}")
            print(f"💡 运行以下命令推送到GitHub:")
            print(f"   git push origin main")
            print(f"   git push origin v{new_version}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动发布脚本")
    parser.add_argument(
        "--type", 
        choices=["major", "minor", "patch"], 
        default="patch",
        help="版本升级类型 (默认: patch)"
    )
    parser.add_argument(
        "--no-push", 
        action="store_true",
        help="不自动推送到GitHub"
    )
    parser.add_argument(
        "--changes", 
        nargs="*",
        help="变更说明列表"
    )
    
    args = parser.parse_args()
    
    manager = AutoReleaseManager()
    
    try:
        manager.create_release(
            version_type=args.type,
            changes=args.changes,
            push=not args.no_push
        )
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()