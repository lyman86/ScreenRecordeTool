# ScreenRecorder Makefile
# 提供便捷的开发和构建命令

.PHONY: help install dev test lint format build clean release setup-git

# 默认目标
help:
	@echo "ScreenRecorder 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install     - 安装项目依赖"
	@echo "  dev         - 安装开发依赖"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 代码格式化"
	@echo "  build       - 构建应用程序"
	@echo "  clean       - 清理构建文件"
	@echo "  release     - 创建发布版本"
	@echo "  setup-git   - 设置Git钩子"
	@echo "  run         - 运行应用程序"
	@echo ""
	@echo "发布命令:"
	@echo "  release-patch  - 发布补丁版本"
	@echo "  release-minor  - 发布次要版本"
	@echo "  release-major  - 发布主要版本"

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 安装开发依赖
dev: install
	@echo "🔧 安装开发依赖..."
	pip install pytest pytest-cov black isort flake8 mypy bandit safety pyinstaller
	@echo "✅ 开发环境设置完成"

# 运行测试
test:
	@echo "🧪 运行测试..."
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

# 代码检查
lint:
	@echo "🔍 代码检查..."
	@echo "检查代码格式..."
	black --check src/
	@echo "检查导入排序..."
	isort --check-only src/
	@echo "运行flake8..."
	flake8 src/
	@echo "类型检查..."
	mypy src/ --ignore-missing-imports
	@echo "安全检查..."
	bandit -r src/
	@echo "依赖安全检查..."
	safety check
	@echo "✅ 代码检查完成"

# 代码格式化
format:
	@echo "🎨 格式化代码..."
	black src/
	isort src/
	@echo "✅ 代码格式化完成"

# 构建应用程序
build: clean
	@echo "🔨 构建应用程序..."
	python scripts/build_automation.py
	@echo "✅ 构建完成"

# 快速构建（仅可执行文件）
build-quick:
	@echo "⚡ 快速构建..."
	python scripts/build_automation.py --only-build
	@echo "✅ 快速构建完成"

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"
	@echo "✅ 清理完成"

# 运行应用程序
run:
	@echo "🚀 启动应用程序..."
	python main.py

# 设置Git钩子
setup-git:
	@echo "⚙️ 设置Git钩子..."
	@if not exist .git\hooks mkdir .git\hooks
	@echo "#!/bin/sh" > .git/hooks/pre-commit
	@echo "echo '🔍 运行代码检查...'" >> .git/hooks/pre-commit
	@echo "make lint" >> .git/hooks/pre-commit
	@echo "if [ $$? -ne 0 ]; then" >> .git/hooks/pre-commit
	@echo "  echo '❌ 代码检查失败，请修复后再提交'" >> .git/hooks/pre-commit
	@echo "  exit 1" >> .git/hooks/pre-commit
	@echo "fi" >> .git/hooks/pre-commit
	@echo "✅ Git钩子设置完成"

# 发布版本
release-patch:
	@echo "📦 创建补丁版本..."
	python scripts/auto_release.py --type patch

release-minor:
	@echo "📦 创建次要版本..."
	python scripts/auto_release.py --type minor

release-major:
	@echo "📦 创建主要版本..."
	python scripts/auto_release.py --type major

# 本地发布（不推送到GitHub）
release-local:
	@echo "📦 创建本地发布..."
	python scripts/auto_release.py --no-push

# 检查项目状态
status:
	@echo "📊 项目状态检查..."
	@echo "Git状态:"
	git status --short
	@echo ""
	@echo "分支信息:"
	git branch -v
	@echo ""
	@echo "最近提交:"
	git log --oneline -5
	@echo ""
	@echo "构建文件:"
	@if exist dist (dir dist /b) else (echo "无构建文件")

# 更新依赖
update-deps:
	@echo "🔄 更新依赖..."
	pip list --outdated
	@echo "运行 'pip install --upgrade <package>' 来更新特定包"

# 安全检查
security:
	@echo "🔒 安全检查..."
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "✅ 安全检查完成，报告已生成"

# 性能分析
profile:
	@echo "⚡ 性能分析..."
	python -m cProfile -o profile.stats main.py
	@echo "性能分析完成，结果保存在 profile.stats"

# 生成需求文件
freeze:
	@echo "📋 生成需求文件..."
	pip freeze > requirements-freeze.txt
	@echo "✅ 需求文件已生成: requirements-freeze.txt"

# 文档生成
docs:
	@echo "📚 生成文档..."
	@if exist docs (echo "文档目录已存在") else (mkdir docs)
	@echo "文档生成功能待实现"

# 初始化项目
init: dev setup-git
	@echo "🎉 项目初始化完成！"
	@echo "现在可以运行 'make run' 来启动应用程序"

# Docker相关命令（如果需要）
docker-build:
	@echo "🐳 构建Docker镜像..."
	@if exist Dockerfile (docker build -t screenrecorder .) else (echo "未找到Dockerfile")

docker-run:
	@echo "🐳 运行Docker容器..."
	docker run -it --rm screenrecorder

# 备份项目
backup:
	@echo "💾 备份项目..."
	@set backup_name=screenrecorder-backup-%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%
	@tar -czf %backup_name%.tar.gz --exclude=.git --exclude=__pycache__ --exclude=dist --exclude=build .
	@echo "✅ 备份完成: %backup_name%.tar.gz"