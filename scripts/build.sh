#!/bin/bash

# 现代录屏工具构建脚本 (Unix/Linux/macOS)

set -e  # 遇到错误时退出

echo "=================================="
echo "现代录屏工具 - 构建脚本"
echo "=================================="

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    CYGWIN*)    PLATFORM=Cygwin;;
    MINGW*)     PLATFORM=MinGW;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "检测到平台: $PLATFORM"

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "项目根目录: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python版本: $python_version"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "检测到虚拟环境: $VIRTUAL_ENV"
else
    echo "警告: 未检测到虚拟环境，建议使用虚拟环境"
fi

# 安装依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p resources
mkdir -p build
mkdir -p dist

# 根据平台选择构建脚本
if [[ "$PLATFORM" == "macOS" ]]; then
    echo "使用macOS构建脚本..."
    python build_scripts/build_macos.py
elif [[ "$PLATFORM" == "Linux" ]]; then
    echo "Linux平台暂不支持GUI构建，仅进行依赖检查..."
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    from config.settings import AppConfig
    print('✓ 配置模块加载成功')
except Exception as e:
    print(f'✗ 配置模块加载失败: {e}')
    sys.exit(1)
"
else
    echo "不支持的平台: $PLATFORM"
    echo "请在Windows上使用 build_scripts/build_windows.py"
    echo "或在macOS上使用 build_scripts/build_macos.py"
    exit 1
fi

echo "构建完成!"

# 显示输出文件
if [[ -d "dist" ]]; then
    echo "输出文件:"
    ls -la dist/
fi
