#!/bin/bash
# 设置项目文件权限脚本
# 为Linux和macOS用户提供便捷的权限设置

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info "设置 ScreenRecorder 项目文件权限..."
echo

# 设置脚本文件为可执行
if [ -f "build.sh" ]; then
    chmod +x build.sh
    print_success "build.sh 已设置为可执行"
else
    print_warning "未找到 build.sh 文件"
fi

if [ -f "setup_permissions.sh" ]; then
    chmod +x setup_permissions.sh
    print_success "setup_permissions.sh 已设置为可执行"
fi

# 设置Python脚本为可执行（如果有shebang）
if [ -f "main.py" ]; then
    if head -1 main.py | grep -q "^#!/"; then
        chmod +x main.py
        print_success "main.py 已设置为可执行"
    fi
fi

# 设置scripts目录下的Python脚本
if [ -d "scripts" ]; then
    for script in scripts/*.py; do
        if [ -f "$script" ] && head -1 "$script" | grep -q "^#!/"; then
            chmod +x "$script"
            print_success "$(basename "$script") 已设置为可执行"
        fi
    done
fi

# 设置构建脚本目录权限
if [ -d "build_scripts" ]; then
    find build_scripts -name "*.sh" -exec chmod +x {} \;
    print_success "build_scripts 目录下的脚本已设置为可执行"
fi

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    print_info "创建Python虚拟环境..."
    
    # 检查Python命令
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        print_warning "未找到Python，请先安装Python 3.9+"
        exit 1
    fi
    
    $PYTHON_CMD -m venv .venv
    print_success "虚拟环境已创建在 .venv 目录"
    
    print_info "激活虚拟环境: source .venv/bin/activate"
else
    print_info "虚拟环境已存在"
fi

# 检查Git配置
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_success "Git仓库已初始化"
    
    # 设置Git钩子权限
    if [ -d ".git/hooks" ]; then
        find .git/hooks -type f -exec chmod +x {} \; 2>/dev/null || true
        print_success "Git钩子权限已设置"
    fi
else
    print_warning "这不是一个Git仓库"
fi

echo
print_success "权限设置完成！"
echo
print_info "现在您可以运行以下命令："
echo "  ./build.sh help          # 查看帮助"
echo "  ./build.sh dev           # 安装开发依赖"
echo "  ./build.sh build         # 构建应用"
echo "  ./build.sh run           # 运行应用"
echo
print_info "或者使用Makefile："
echo "  make help                # 查看帮助"
echo "  make dev                 # 安装开发依赖"
echo "  make build               # 构建应用"
echo "  make run                 # 运行应用"