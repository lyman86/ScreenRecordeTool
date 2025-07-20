# GitHub Actions Shell语法修复

## 🔧 问题描述

Windows构建失败，错误信息：
```
ParserError: Missing '(' after 'if' in if statement.
if [ -d "dist" ]; then
```

## 🔍 根本原因

GitHub Actions在不同操作系统上使用不同的默认shell：
- **Windows**: PowerShell (pwsh)
- **Linux/macOS**: bash

我们的脚本使用bash语法（`if [ -d "dist" ]`），但在Windows上默认使用PowerShell，导致语法错误。

## ✅ 修复措施

### 1. 明确指定Shell类型

对于使用bash语法的步骤，明确指定`shell: bash`：

```yaml
- name: Create resources directory
  shell: bash
  run: |
    mkdir -p resources
```

### 2. 平台特定的构建检查

创建分别适用于Windows和Unix系统的构建检查：

```yaml
# Windows版本 (PowerShell)
- name: Check build output (Windows)
  if: runner.os == 'Windows'
  shell: pwsh
  run: |
    if (Test-Path "dist") {
      Write-Host "✅ dist directory exists"
      Get-ChildItem -Path "dist" -Recurse
    }

# Unix版本 (bash)
- name: Check build output (Unix)
  if: runner.os != 'Windows'
  shell: bash
  run: |
    if [ -d "dist" ]; then
      echo "✅ dist directory exists"
      ls -la dist/
    fi
```

### 3. 修复的文件

#### `.github/workflows/build.yml`
- ✅ 添加`shell: bash`到"Create resources directory"步骤
- ✅ 分离Windows和Unix的构建检查步骤
- ✅ 使用PowerShell语法处理Windows特定逻辑

#### `.github/workflows/manual-release.yml`
- ✅ 添加`shell: bash`到"Create resources directory"步骤

## 🎯 预期效果

修复后应该能够：
- ✅ Windows构建正常执行，不再出现PowerShell语法错误
- ✅ 跨平台兼容性更好
- ✅ 更清晰的平台特定逻辑处理

## 📋 最佳实践

### Shell选择指南

| 场景 | 推荐Shell | 原因 |
|------|-----------|------|
| 跨平台脚本 | `bash` | 在所有平台都可用 |
| Windows特定 | `pwsh` | 原生PowerShell语法 |
| 简单命令 | 默认 | 避免不必要的复杂性 |

### 语法对比

| 功能 | Bash | PowerShell |
|------|------|------------|
| 目录检查 | `[ -d "dir" ]` | `Test-Path "dir"` |
| 文件列表 | `ls -la` | `Get-ChildItem` |
| 条件语句 | `if [ ]; then` | `if () { }` |
| 变量 | `$VAR` | `$VAR` |

## 🔄 验证方法

1. **推送修复代码**
2. **触发Windows构建**
3. **检查构建日志**确认不再有PowerShell语法错误
4. **验证dist目录检查**正常工作

---

**修复时间**: 2025-07-19  
**影响范围**: Windows构建步骤  
**风险等级**: 低 (语法修复)  
**测试状态**: 待验证
