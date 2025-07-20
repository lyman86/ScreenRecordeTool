# 构建和发布指南

本文档介绍如何使用自动化构建和发布系统来打包和发布现代录屏工具。

## 🏗️ 构建系统概述

项目包含以下构建相关文件：

- `build.py` - 通用构建脚本，自动检测平台
- `build_scripts/build_windows.py` - Windows专用构建脚本
- `build_scripts/build_macos.py` - macOS专用构建脚本
- `release.py` - 自动化发布脚本
- `.github/workflows/build-release.yml` - 正式发布工作流
- `.github/workflows/build-test.yml` - 测试构建工作流

## 🚀 快速开始

### 方法1: 使用发布脚本 (推荐)

```bash
# 运行发布脚本
python release.py
```

脚本会引导您完成以下步骤：
1. 选择版本类型 (patch/minor/major)
2. 输入更新内容
3. 自动创建标签
4. 触发GitHub Actions构建

### 方法2: 手动创建标签

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

推送标签后，GitHub Actions会自动开始构建。

### 方法3: 手动触发构建

1. 访问 [GitHub Actions](../../actions/workflows/build-release.yml)
2. 点击 "Run workflow"
3. 输入版本号
4. 点击 "Run workflow" 确认

## 📦 构建产物

### Windows
- `ScreenRecorder.exe` - 可执行文件
- `installer.nsi` - NSIS安装脚本
- `ScreenRecorder-Windows-vX.X.X.zip` - 发布包

### macOS
- `ScreenRecorder.app` - 应用程序包
- `ScreenRecorder_vX.X.X.dmg` - 安装镜像
- `ScreenRecorder-macOS-vX.X.X.dmg` - 发布包

## 🔧 本地构建

### 环境要求

**通用要求：**
- Python 3.8+
- Git

**Windows额外要求：**
- Visual C++ Redistributable
- (可选) NSIS - 用于创建安装程序

**macOS额外要求：**
- Xcode Command Line Tools
- Homebrew
- (可选) 开发者证书 - 用于代码签名

### 构建步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd ScreenRecordeTool
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行构建**
   ```bash
   # 自动检测平台并构建
   python build.py
   
   # 或者直接运行平台特定脚本
   python build_scripts/build_windows.py  # Windows
   python build_scripts/build_macos.py    # macOS
   ```

## 🤖 GitHub Actions工作流

### build-release.yml

**触发条件：**
- 推送版本标签 (如 `v1.0.0`)
- 手动触发

**功能：**
- 并行构建Windows和macOS版本
- 创建GitHub Release
- 上传构建产物
- 生成发布说明

### build-test.yml

**触发条件：**
- 手动触发
- Pull Request (影响构建相关文件时)

**功能：**
- 测试构建过程
- 验证依赖安装
- 上传测试产物 (保留7天)

## 📋 发布流程

### 自动发布 (推荐)

1. **准备发布**
   ```bash
   # 确保所有更改已提交
   git add .
   git commit -m "Prepare for release"
   git push
   ```

2. **运行发布脚本**
   ```bash
   python release.py
   ```

3. **选择版本类型**
   - Patch: 修复版本 (1.0.0 → 1.0.1)
   - Minor: 功能版本 (1.0.0 → 1.1.0)
   - Major: 重大版本 (1.0.0 → 2.0.0)

4. **输入更新内容**
   - 脚本会提示输入更新日志
   - 每行一条更新内容
   - 空行结束输入

5. **确认发布**
   - 脚本会显示新版本号
   - 确认后自动创建标签并推送

6. **等待构建完成**
   - GitHub Actions自动开始构建
   - 构建完成后自动创建Release

### 手动发布

1. **更新版本信息**
   - 手动更新 `CHANGELOG.md`
   - 提交更改

2. **创建标签**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

3. **监控构建**
   - 访问 [GitHub Actions](../../actions)
   - 查看构建状态

## 🔍 故障排除

### 常见问题

**构建失败：依赖安装错误**
```bash
# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**Windows构建：缺少Visual C++**
- 安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

**macOS构建：权限问题**
```bash
# 安装Xcode命令行工具
xcode-select --install

# 安装Homebrew依赖
brew install portaudio
```

**PyInstaller错误**
```bash
# 更新PyInstaller
pip install --upgrade pyinstaller

# 清理构建缓存
rm -rf build/ dist/ *.spec
```

### 调试构建

1. **本地测试**
   ```bash
   # 运行测试构建
   python build.py
   ```

2. **检查依赖**
   ```bash
   # 测试关键模块导入
   python -c "import PyQt6; print('PyQt6 OK')"
   python -c "import cv2; print('OpenCV OK')"
   python -c "import mss; print('MSS OK')"
   ```

3. **查看详细日志**
   - 在GitHub Actions中查看详细构建日志
   - 检查每个步骤的输出

## 📝 版本管理

### 版本号规范

使用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- `v1.0.0` - 主版本.次版本.修订版本
- `v1.0.0-beta.1` - 预发布版本
- `v1.0.0-rc.1` - 候选发布版本

### 分支策略

- `main` - 稳定版本，用于发布
- `develop` - 开发版本，功能集成
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

### 标签管理

```bash
# 查看所有标签
git tag -l

# 查看标签详情
git show v1.0.0

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```

## 🔐 安全考虑

### 代码签名

**Windows:**
- 需要代码签名证书
- 配置在构建脚本中

**macOS:**
- 需要Apple开发者账号
- 配置开发者证书
- 可选：公证 (Notarization)

### 密钥管理

- 使用GitHub Secrets存储敏感信息
- 不要在代码中硬编码密钥
- 定期轮换访问令牌

## 📊 监控和分析

### 构建统计

- 在GitHub Actions中查看构建时间
- 监控构建成功率
- 分析失败原因

### 发布统计

- 在GitHub Releases中查看下载统计
- 分析用户反馈
- 跟踪版本采用率

## 🆘 获取帮助

如果遇到问题：

1. 查看 [GitHub Issues](../../issues)
2. 检查 [GitHub Actions日志](../../actions)
3. 参考 [PyInstaller文档](https://pyinstaller.readthedocs.io/)
4. 查看平台特定的构建指南

---

**注意：** 首次设置时，请确保已正确配置GitHub仓库的Actions权限和Secrets。