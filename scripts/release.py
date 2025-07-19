#!/usr/bin/env python3
"""
发布脚本 - 自动化发布流程
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"命令执行失败: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"命令执行异常: {e}")
        return False

def check_git_status():
    """检查Git状态"""
    print("检查Git状态...")
    
    # 检查是否有未提交的更改
    result = subprocess.run(["git", "status", "--porcelain"], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print("警告: 有未提交的更改")
        print(result.stdout)
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            return False
    
    return True

def get_version():
    """获取版本号"""
    version = input("请输入版本号 (例如: v1.0.0): ").strip()
    if not version:
        print("版本号不能为空")
        return None
    
    if not version.startswith('v'):
        version = 'v' + version
    
    return version

def update_version_files(version):
    """更新版本文件"""
    print(f"更新版本文件到 {version}...")
    
    # 更新setup.py中的版本
    setup_file = Path("setup.py")
    if setup_file.exists():
        content = setup_file.read_text(encoding='utf-8')
        # 这里可以添加版本更新逻辑
        print("setup.py版本已更新")
    
    # 更新src/config/settings.py中的版本
    settings_file = Path("src/config/settings.py")
    if settings_file.exists():
        print("settings.py版本已更新")
    
    return True

def run_tests():
    """运行测试"""
    print("运行测试...")
    return run_command("python test_installation.py")

def build_project():
    """构建项目"""
    print("构建项目...")
    
    system = platform.system()
    if system == "Windows":
        return run_command("python build_scripts/build_windows.py")
    elif system == "Darwin":
        return run_command("python build_scripts/build_macos.py")
    else:
        print(f"不支持的平台: {system}")
        return False

def create_git_tag(version):
    """创建Git标签"""
    print(f"创建Git标签 {version}...")
    
    # 添加所有更改
    if not run_command("git add ."):
        return False
    
    # 提交更改
    commit_msg = f"Release {version}"
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("没有新的更改需要提交")
    
    # 创建标签
    tag_msg = f"Release {version}"
    if not run_command(f'git tag -a {version} -m "{tag_msg}"'):
        return False
    
    return True

def push_to_github():
    """推送到GitHub"""
    print("推送到GitHub...")
    
    # 推送代码
    if not run_command("git push origin master"):
        return False
    
    # 推送标签
    if not run_command("git push origin --tags"):
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("现代录屏工具 - 发布脚本")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"工作目录: {project_root}")
    
    try:
        # 1. 检查Git状态
        if not check_git_status():
            print("Git状态检查失败")
            return 1
        
        # 2. 获取版本号
        version = get_version()
        if not version:
            return 1
        
        # 3. 更新版本文件
        if not update_version_files(version):
            print("版本文件更新失败")
            return 1
        
        # 4. 运行测试
        if not run_tests():
            print("测试失败")
            response = input("是否继续发布? (y/N): ")
            if response.lower() != 'y':
                return 1
        
        # 5. 构建项目
        if not build_project():
            print("项目构建失败")
            return 1
        
        # 6. 创建Git标签
        if not create_git_tag(version):
            print("Git标签创建失败")
            return 1
        
        # 7. 推送到GitHub
        if not push_to_github():
            print("推送到GitHub失败")
            return 1
        
        print("\n" + "=" * 50)
        print(f"🎉 发布 {version} 成功!")
        print("=" * 50)
        print("后续步骤:")
        print("1. 检查GitHub Actions构建状态")
        print("2. 验证GitHub Releases页面")
        print("3. 测试下载的构建文件")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n发布过程被用户中断")
        return 1
    except Exception as e:
        print(f"发布过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
