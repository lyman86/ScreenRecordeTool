# ScreenRecorder 自动化构建指南

本指南详细介绍如何使用 ScreenRecorder 项目的各种自动化脚本和工具来进行开发、构建和发布。

## 📋 目录

- [快速开始](#快速开始)
- [本地构建脚本](#本地构建脚本)
- [GitHub Actions 工作流](#github-actions-工作流)
- [Python 自动化脚本](#python-自动化脚本)
- [Makefile 命令](#makefile-命令)
- [常见问题](#常见问题)

## 🚀 快速开始

### Windows 用户

```powershell
# 使用 PowerShell 脚本（推荐）
.\build.ps1 dev          # 安装开发依赖
.\build.ps1 build        # 构建应用
.\build.ps1 run          # 运行应用

# 或使用批处理脚本
build.bat dev
build.bat build
build.bat run
```

### Linux/macOS 用户

```bash
# 首先给脚本执行权限
chmod +x build.sh

# 使用 Shell 脚本
./build.sh dev           # 安装开发依赖
./build.sh build         # 构建应用
./build.sh run           # 运行应用

# 或使用 Makefile
make dev
make build
make run
```

## 🛠️ 本地构建脚本

### PowerShell 脚本 (build.ps1)

**适用于**: Windows 用户

```powershell
# 基本命令
.\build.ps1 help                    # 显示帮助
.\build.ps1 install                 # 安装依赖
.\build.ps1 dev                     # 安装开发依赖
.\build.ps1 test                    # 运行测试
.\build.ps1 lint                    # 代码检查
.\build.ps1 format                  # 代码格式化
.\build.ps1 build                   # 构建应用
.\build.ps1 clean                   # 清理构建文件
.\build.ps1 run                     # 运行应用
.\build.ps1 status                  # 检查项目状态

# 发布命令
.\build.ps1 release                 # 创建补丁版本发布
.\build.ps1 release -VersionType minor    # 创建次要版本发布
.\build.ps1 release -VersionType major    # 创建主要版本发布
.\build.ps1 release -NoPush              # 创建发布但不推送到GitHub

# 构建选项
.\build.ps1 build -Quick            # 快速构建模式
```

### 批处理脚本 (build.bat)

**适用于**: 不熟悉 PowerShell 的 Windows 用户

```batch
# 基本命令
build.bat help                      # 显示帮助
build.bat install                   # 安装依赖
build.bat dev                       # 安装开发依赖
build.bat test                      # 运行测试
build.bat lint                      # 代码检查
build.bat format                    # 代码格式化
build.bat build                     # 构建应用
build.bat clean                     # 清理构建文件
build.bat run                       # 运行应用
build.bat release                   # 创建发布
build.bat status                    # 检查项目状态
```

### Shell 脚本 (build.sh)

**适用于**: Linux 和 macOS 用户

```bash
# 基本命令
./build.sh help                     # 显示帮助
./build.sh setup-venv               # 创建虚拟环境
./build.sh install                  # 安装依赖
./build.sh dev                      # 安装开发依赖
./build.sh test                     # 运行测试
./build.sh lint                     # 代码检查
./build.sh format                   # 代码格式化
./build.sh build                    # 构建应用
./build.sh clean                    # 清理构建文件
./build.sh run                      # 运行应用
./build.sh status                   # 检查项目状态

# 发布命令
./build.sh release                  # 创建补丁版本发布
./build.sh release --version-type minor   # 创建次要版本发布
./build.sh release --version-type major   # 创建主要版本发布
./build.sh release --no-push             # 创建发布但不推送到GitHub

# 构建选项
./build.sh build --quick            # 快速构建模式
```

## ⚙️ GitHub Actions 工作流

### 自动构建工作流 (build.yml)

**触发条件**:
- 推送到 `v*` 标签时自动触发
- 对 `main` 或 `master` 分支的 Pull Request
- 手动触发

**功能**:
- 跨平台构建 (Windows, macOS, Linux)
- 多 Python 版本支持 (3.9, 3.10, 3.11, 3.12)
- 自动创建 GitHub Release
- 代码质量检查

### 增强构建工作流 (enhanced_build.yml)

**新增功能**:
- 安全检查 (bandit, safety)
- 代码覆盖率报告
- 文档自动部署
- 更详细的构建选项

### 手动触发工作流 (manual_build.yml)

**使用方法**:
1. 访问 GitHub 仓库的 Actions 页面
2. 选择 "Manual Build and Release" 工作流
3. 点击 "Run workflow"
4. 配置构建选项:
   - **构建类型**: build, release, test-only
   - **版本升级类型**: patch, minor, major
   - **构建平台**: all, windows, macos, linux
   - **Python 版本**: 3.9, 3.10, 3.11, 3.12
   - **跳过测试**: 是/否
   - **创建草稿发布**: 是/否

## 🐍 Python 自动化脚本

### 自动发布脚本 (scripts/auto_release.py)

```bash
# 基本用法
python scripts/auto_release.py --type patch    # 补丁版本
python scripts/auto_release.py --type minor    # 次要版本
python scripts/auto_release.py --type major    # 主要版本

# 高级选项
python scripts/auto_release.py --type patch --message "修复重要bug"  # 自定义变更说明
python scripts/auto_release.py --type minor --no-push              # 不推送到GitHub
python scripts/auto_release.py --dry-run                          # 预览模式
python scripts/auto_release.py --get-version                      # 获取下一个版本号
```

### 构建自动化脚本 (scripts/build_automation.py)

```bash
# 基本用法
python scripts/build_automation.py              # 完整构建流程
python scripts/build_automation.py --only-build # 仅构建可执行文件
python scripts/build_automation.py --no-test    # 跳过测试
python scripts/build_automation.py --no-clean   # 不清理构建目录
python scripts/build_automation.py --no-package # 不创建便携版包
```

## 📝 Makefile 命令

**适用于**: 所有支持 make 的系统

```bash
# 开发命令
make help                    # 显示帮助
make install                 # 安装依赖
make dev                     # 安装开发依赖
make test                    # 运行测试
make lint                    # 代码检查
make format                  # 代码格式化
make clean                   # 清理文件

# 构建命令
make build                   # 构建应用
make build-all               # 构建所有平台
make package                 # 创建发布包

# 运行命令
make run                     # 运行应用
make run-dev                 # 开发模式运行

# Git 命令
make git-hooks               # 设置Git钩子
make status                  # 项目状态

# 发布命令
make release-patch           # 发布补丁版本
make release-minor           # 发布次要版本
make release-major           # 发布主要版本
make release-local           # 本地发布

# 维护命令
make update-deps             # 更新依赖
make security-check          # 安全检查
make performance-test        # 性能测试
make docs                    # 生成文档
```

## 🔧 配置和自定义

### 环境变量

```bash
# 设置构建选项
export BUILD_TYPE=release           # 构建类型
export PYTHON_VERSION=3.11          # Python版本
export SKIP_TESTS=false             # 是否跳过测试
export CREATE_PORTABLE=true         # 是否创建便携版
```

### 自定义构建脚本

如果需要自定义构建流程，可以修改以下文件：
- `build.py` - 主构建脚本
- `scripts/build_automation.py` - 自动化构建脚本
- `.github/workflows/` - GitHub Actions 工作流

## 📦 构建产物

构建完成后，产物将位于以下位置：

```
dist/
├── ScreenRecorder.exe              # Windows 可执行文件
├── ScreenRecorder                  # Linux/macOS 可执行文件
├── ScreenRecorder-Windows-Portable.zip     # Windows 便携版
├── ScreenRecorder-macOS-Portable.tar.gz    # macOS 便携版
└── ScreenRecorder-Linux-Portable.tar.gz    # Linux 便携版
```

## 🚨 常见问题

### Q: PowerShell 脚本无法执行

**A**: 需要设置执行策略：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: Shell 脚本没有执行权限

**A**: 给脚本添加执行权限：
```bash
chmod +x build.sh
```

### Q: 虚拟环境未激活

**A**: 手动激活虚拟环境：
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### Q: 依赖安装失败

**A**: 尝试以下解决方案：
1. 升级 pip: `python -m pip install --upgrade pip`
2. 清理缓存: `pip cache purge`
3. 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

### Q: 构建失败

**A**: 检查以下项目：
1. Python 版本是否符合要求 (3.9+)
2. 所有依赖是否正确安装
3. 系统依赖是否安装 (特别是 Linux 系统)
4. 查看详细错误日志

### Q: GitHub Actions 构建失败

**A**: 常见原因和解决方案：
1. **权限问题**: 确保 `GITHUB_TOKEN` 有足够权限
2. **依赖问题**: 检查 `requirements.txt` 是否正确
3. **平台兼容性**: 某些依赖可能不支持所有平台
4. **资源限制**: GitHub Actions 有时间和资源限制

## 📚 进阶使用

### 自定义 GitHub Actions

可以通过修改 `.github/workflows/` 目录下的文件来自定义构建流程：

1. **添加新的构建平台**
2. **修改 Python 版本矩阵**
3. **添加额外的测试步骤**
4. **自定义发布说明**

### 集成 CI/CD

项目已经配置了完整的 CI/CD 流程：

1. **持续集成**: 每次提交都会触发测试
2. **持续部署**: 标签推送会自动创建发布
3. **代码质量**: 自动进行代码检查和格式化
4. **安全扫描**: 自动检查依赖安全性

### 监控和通知

可以配置以下监控和通知：

1. **构建状态徽章**: 在 README 中显示构建状态
2. **邮件通知**: 构建失败时发送邮件
3. **Slack 集成**: 发送构建结果到 Slack
4. **Discord 通知**: 发送构建结果到 Discord

## 🤝 贡献指南

如果您想改进这些自动化脚本：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

请确保：
- 遵循现有的代码风格
- 添加适当的测试
- 更新相关文档
- 测试所有平台的兼容性

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

**需要帮助？** 请查看 [GitHub Issues](../../issues) 或创建新的 Issue。