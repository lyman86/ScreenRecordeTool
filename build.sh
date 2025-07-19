#!/bin/bash
# ScreenRecorder Shell构建脚本
# 为Linux和macOS用户提供便捷的构建和开发命令

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出函数
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}🚀 $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    if ! command_exists python3; then
        if ! command_exists python; then
            print_error "未找到Python，请先安装Python 3.9+"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_info "Python版本: $PYTHON_VERSION"
    
    # 检查pip
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    if command_exists pip3; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
}

# 检查并激活虚拟环境
check_venv() {
    if [ -f ".venv/bin/activate" ]; then
        print_info "激活虚拟环境..."
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        print_info "激活虚拟环境..."
        source venv/bin/activate
    else
        print_warning "未找到虚拟环境，使用系统Python"
    fi
}

# 执行命令并检查结果
run_command() {
    local cmd="$1"
    local desc="$2"
    
    print_info "$desc"
    echo "执行: $cmd"
    
    if ! eval "$cmd"; then
        print_error "$desc 失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    print_header "ScreenRecorder Shell构建工具"
    echo
    echo "用法: ./build.sh <命令> [选项]"
    echo
    echo -e "${YELLOW}可用命令:${NC}"
    echo "  help        - 显示此帮助信息"
    echo "  install     - 安装项目依赖"
    echo "  dev         - 安装开发依赖"
    echo "  test        - 运行测试"
    echo "  lint        - 代码检查"
    echo "  format      - 代码格式化"
    echo "  build       - 构建应用程序"
    echo "  clean       - 清理构建文件"
    echo "  run         - 运行应用程序"
    echo "  release     - 创建发布版本"
    echo "  status      - 检查项目状态"
    echo "  setup-venv  - 创建虚拟环境"
    echo
    echo -e "${YELLOW}选项:${NC}"
    echo "  --version-type <patch|minor|major>  - 版本升级类型 (默认: patch)"
    echo "  --no-push                           - 不推送到GitHub"
    echo "  --quick                             - 快速构建模式"
    echo
    echo -e "${YELLOW}示例:${NC}"
    echo "  ./build.sh install               - 安装依赖"
    echo "  ./build.sh build --quick          - 快速构建"
    echo "  ./build.sh release --version-type minor  - 发布次要版本"
}

# 创建虚拟环境
setup_venv() {
    print_info "创建虚拟环境..."
    
    if [ -d ".venv" ]; then
        print_warning "虚拟环境已存在"
        return
    fi
    
    run_command "$PYTHON_CMD -m venv .venv" "创建虚拟环境"
    
    print_info "激活虚拟环境..."
    source .venv/bin/activate
    
    run_command "$PIP_CMD install --upgrade pip" "升级pip"
    
    print_success "虚拟环境创建完成"
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    run_command "$PIP_CMD install --upgrade pip" "升级pip"
    
    if [ -f "requirements.txt" ]; then
        run_command "$PIP_CMD install -r requirements.txt" "安装项目依赖"
    else
        print_warning "未找到requirements.txt文件"
    fi
    
    print_success "依赖安装完成"
}

# 安装开发依赖
install_dev_dependencies() {
    install_dependencies
    
    print_info "安装开发依赖..."
    
    local dev_packages=(
        "pytest"
        "pytest-cov"
        "black"
        "isort"
        "flake8"
        "mypy"
        "bandit"
        "safety"
        "pyinstaller"
    )
    
    for package in "${dev_packages[@]}"; do
        run_command "$PIP_CMD install $package" "安装 $package"
    done
    
    print_success "开发环境设置完成"
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    
    if [ -d "tests" ]; then
        run_command "$PYTHON_CMD -m pytest tests/ -v --cov=src --cov-report=term-missing" "运行测试"
    else
        print_warning "未找到tests目录，跳过测试"
    fi
}

# 代码检查
run_lint() {
    print_info "代码检查..."
    
    print_info "检查代码格式..."
    $PYTHON_CMD -m black --check src/ || print_warning "代码格式需要修复"
    
    print_info "检查导入排序..."
    $PYTHON_CMD -m isort --check-only src/ || print_warning "导入排序需要修复"
    
    print_info "运行flake8..."
    $PYTHON_CMD -m flake8 src/ || print_warning "发现代码问题"
    
    print_info "类型检查..."
    $PYTHON_CMD -m mypy src/ --ignore-missing-imports || print_warning "发现类型问题"
    
    print_info "安全检查..."
    $PYTHON_CMD -m bandit -r src/ || print_warning "发现安全问题"
    
    print_info "依赖安全检查..."
    $PYTHON_CMD -m safety check || print_warning "发现依赖安全问题"
    
    print_success "代码检查完成"
}

# 代码格式化
run_format() {
    print_info "格式化代码..."
    
    run_command "$PYTHON_CMD -m black src/" "格式化代码"
    run_command "$PYTHON_CMD -m isort src/" "排序导入"
    
    print_success "代码格式化完成"
}

# 构建应用程序
run_build() {
    print_info "构建应用程序..."
    
    local quick_mode=false
    if [[ "$*" == *"--quick"* ]]; then
        quick_mode=true
    fi
    
    if [ -f "scripts/build_automation.py" ]; then
        if [ "$quick_mode" = true ]; then
            run_command "$PYTHON_CMD scripts/build_automation.py --only-build" "快速构建"
        else
            run_command "$PYTHON_CMD scripts/build_automation.py" "完整构建"
        fi
    elif [ -f "build.py" ]; then
        run_command "$PYTHON_CMD build.py" "运行构建脚本"
    else
        print_info "使用默认PyInstaller构建..."
        # 根据操作系统选择不同的构建选项
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            run_command "$PYTHON_CMD -m PyInstaller --onefile --windowed --add-data 'src:src' main.py" "PyInstaller构建 (macOS)"
        else
            # Linux
            run_command "$PYTHON_CMD -m PyInstaller --onefile --add-data 'src:src' main.py" "PyInstaller构建 (Linux)"
        fi
    fi
    
    print_success "构建完成"
    
    # 显示构建结果
    if [ -d "dist" ]; then
        print_info "构建产物:"
        ls -la dist/ | while read -r line; do
            echo "  $line"
        done
    fi
}

# 清理构建文件
run_clean() {
    print_info "清理构建文件..."
    
    local clean_dirs=("build" "dist")
    for dir in "${clean_dirs[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo "  删除: $dir"
        fi
    done
    
    # 清理 __pycache__ 目录
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 清理 .pyc 文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理 .pyo 文件
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    print_success "清理完成"
}

# 运行应用程序
run_app() {
    print_info "启动应用程序..."
    
    if [ -f "main.py" ]; then
        $PYTHON_CMD main.py
    else
        print_error "未找到main.py文件"
        exit 1
    fi
}

# 创建发布
run_release() {
    print_info "创建发布版本..."
    
    local version_type="patch"
    local no_push=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version-type)
                version_type="$2"
                shift 2
                ;;
            --no-push)
                no_push=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [ -f "scripts/auto_release.py" ]; then
        local release_args="--type $version_type"
        if [ "$no_push" = true ]; then
            release_args="$release_args --no-push"
        fi
        
        run_command "$PYTHON_CMD scripts/auto_release.py $release_args" "创建发布"
    else
        print_error "未找到自动发布脚本"
        exit 1
    fi
}

# 检查项目状态
show_status() {
    print_info "项目状态检查..."
    
    echo -e "${YELLOW}Git状态:${NC}"
    git status --short
    
    echo
    echo -e "${YELLOW}分支信息:${NC}"
    git branch -v
    
    echo
    echo -e "${YELLOW}最近提交:${NC}"
    git log --oneline -5
    
    echo
    echo -e "${YELLOW}构建文件:${NC}"
    if [ -d "dist" ]; then
        ls -la dist/
    else
        echo "  无构建文件"
    fi
    
    echo
    echo -e "${YELLOW}Python环境:${NC}"
    $PYTHON_CMD --version
    $PIP_CMD --version
    
    echo
    echo -e "${YELLOW}系统信息:${NC}"
    echo "  操作系统: $OSTYPE"
    echo "  架构: $(uname -m)"
}

# 主函数
main() {
    print_header "ScreenRecorder Shell构建工具"
    echo
    
    # 检查Python
    check_python
    
    # 激活虚拟环境（如果存在）
    check_venv
    
    # 解析命令
    case "${1:-help}" in
        help|--help|-h)
            show_help
            ;;
        setup-venv)
            setup_venv
            ;;
        install)
            install_dependencies
            ;;
        dev)
            install_dev_dependencies
            ;;
        test)
            run_tests
            ;;
        lint)
            run_lint
            ;;
        format)
            run_format
            ;;
        build)
            shift
            run_build "$@"
            ;;
        clean)
            run_clean
            ;;
        run)
            run_app
            ;;
        release)
            shift
            run_release "$@"
            ;;
        status)
            show_status
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'print_error "脚本执行出错"' ERR

# 运行主函数
main "$@"