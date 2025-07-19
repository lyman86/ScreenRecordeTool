# GitHub Actions 自动构建指南

本项目已配置完整的GitHub Actions自动构建流程，支持Windows和macOS平台的自动打包。

## 🚀 工作流概览

### 1. 持续集成 (CI)
**文件**: `.github/workflows/ci.yml`
**触发条件**: 
- 推送到 `main` 或 `master` 分支
- 创建Pull Request

**功能**:
- 在多个Python版本(3.9, 3.10, 3.11)上测试
- 跨平台测试(Ubuntu, Windows, macOS)
- 代码质量检查(Black, isort, mypy)
- 基本功能测试

### 2. 构建和发布 (Build & Release)
**文件**: `.github/workflows/build.yml`
**触发条件**:
- 推送到主分支
- 创建标签(v*)
- 手动触发

**功能**:
- 构建Windows和macOS可执行文件
- 自动创建GitHub Release
- 上传构建产物

### 3. 发布构建 (Release Build)
**文件**: `.github/workflows/release.yml`
**触发条件**:
- 发布Release
- 手动触发

**功能**:
- 专门的发布构建
- 创建安装包
- 生成发布说明

## 📦 如何触发自动构建

### 方法1: 创建Release标签
```bash
# 创建并推送标签
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

### 方法2: 手动触发
1. 访问 [GitHub Actions页面](https://github.com/lyman86/ScreenRecordeTool/actions)
2. 选择 "Release Build" 工作流
3. 点击 "Run workflow"
4. 输入版本号(如 v1.0.1)
5. 点击 "Run workflow" 按钮

### 方法3: 使用发布脚本
```bash
# 使用项目提供的发布脚本
python scripts/release.py
```

## 🔍 监控构建状态

### 查看构建状态
- 访问: https://github.com/lyman86/ScreenRecordeTool/actions
- 查看各个工作流的运行状态
- 点击具体的运行查看详细日志

### 构建状态徽章
README中的徽章会显示最新的构建状态:
- [![CI Status](https://github.com/lyman86/ScreenRecordeTool/workflows/Continuous%20Integration/badge.svg)](https://github.com/lyman86/ScreenRecordeTool/actions)
- [![Build Status](https://github.com/lyman86/ScreenRecordeTool/workflows/Build%20and%20Release/badge.svg)](https://github.com/lyman86/ScreenRecordeTool/actions)

## 📥 下载构建产物

### 从GitHub Releases下载
1. 访问 [Releases页面](https://github.com/lyman86/ScreenRecordeTool/releases)
2. 选择最新版本
3. 下载对应平台的文件:
   - `ScreenRecorder-Windows.zip` - Windows版本
   - `ScreenRecorder-macOS.tar.gz` - macOS版本

### 从Actions Artifacts下载
1. 访问 [Actions页面](https://github.com/lyman86/ScreenRecordeTool/actions)
2. 点击成功的构建运行
3. 在 "Artifacts" 部分下载构建文件

## 🛠️ 自定义构建

### 修改构建配置
编辑 `.github/workflows/` 目录下的YAML文件:

```yaml
# 添加新的Python版本
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']

# 添加新的操作系统
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### 添加构建步骤
```yaml
- name: 自定义构建步骤
  run: |
    echo "执行自定义命令"
    python custom_script.py
```

## 🔧 故障排除

### 常见问题

#### 1. 构建失败
- 检查构建日志中的错误信息
- 确保所有依赖都在 `requirements.txt` 中
- 验证代码在本地能正常运行

#### 2. 权限问题
- 确保仓库有正确的权限设置
- 检查 `GITHUB_TOKEN` 权限

#### 3. 平台特定问题
- Windows: 确保所有路径使用正确的分隔符
- macOS: 检查系统依赖是否正确安装

### 调试技巧

#### 启用调试模式
在工作流中添加:
```yaml
- name: 调试信息
  run: |
    echo "Python版本: $(python --version)"
    echo "工作目录: $(pwd)"
    echo "文件列表: $(ls -la)"
```

#### 本地测试
```bash
# 在本地运行相同的构建命令
python build_scripts/build_windows.py  # Windows
python build_scripts/build_macos.py    # macOS
```

## 📚 相关文档

- [GitHub Actions官方文档](https://docs.github.com/en/actions)
- [PyInstaller文档](https://pyinstaller.readthedocs.io/)
- [项目贡献指南](../CONTRIBUTING.md)
- [版本更新日志](../CHANGELOG.md)

## 🤝 贡献

如果您想改进构建流程:
1. Fork项目
2. 修改工作流文件
3. 测试您的更改
4. 提交Pull Request

---

**注意**: 首次设置后，GitHub Actions可能需要几分钟来识别新的工作流文件。如果工作流没有立即出现，请稍等片刻。
