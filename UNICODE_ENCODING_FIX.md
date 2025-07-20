# Windows Unicode编码问题修复

## 🔧 问题描述

Windows构建失败，出现Unicode编码错误：
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 2-7: character maps to <undefined>
```

错误发生在CI构建脚本中的中文字符输出：
```python
print("CI环境构建脚本")  # 中文字符导致编码错误
```

## 🔍 根本原因

1. **Windows默认编码**: Windows环境下Python默认使用cp1252编码
2. **中文字符冲突**: 脚本中的中文字符无法在cp1252编码下正确显示
3. **CI环境限制**: GitHub Actions的Windows环境对Unicode支持有限

## ✅ 修复方案

### 1. 创建英文版本构建脚本

创建`scripts/ci_build_en.py`，完全使用英文：
- ✅ 避免所有中文字符
- ✅ 保持相同的功能逻辑
- ✅ 添加UTF-8编码声明
- ✅ 更好的跨平台兼容性

### 2. 创建英文版本测试脚本

创建`test_installation_en.py`：
- ✅ 英文输出信息
- ✅ 相同的测试逻辑
- ✅ 避免编码问题

### 3. 更新GitHub Actions工作流

修改工作流使用英文版本脚本：
```yaml
- name: Build executable
  run: |
    python scripts/ci_build_en.py  # 使用英文版本
```

## 📁 新增文件

### `scripts/ci_build_en.py`
- 英文版本的CI构建脚本
- 完全避免Unicode编码问题
- 保持所有原有功能

### `test_installation_en.py`
- 英文版本的安装测试脚本
- 跨平台兼容的输出
- 相同的测试覆盖率

## 🔄 修改的文件

### `.github/workflows/build.yml`
```yaml
# 修改前
python scripts/ci_build.py

# 修改后
python scripts/ci_build_en.py
```

### `.github/workflows/manual-release.yml`
```yaml
# 修改前
python scripts/ci_build.py

# 修改后
python scripts/ci_build_en.py
```

## 🎯 预期效果

修复后应该能够：
- ✅ **Windows构建正常执行**，不再出现Unicode编码错误
- ✅ **跨平台兼容性更好**，所有平台使用相同脚本
- ✅ **更清晰的英文输出**，便于国际化用户理解
- ✅ **成功创建dist目录**和构建产物

## 📋 编码最佳实践

### 1. 文件编码声明
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

### 2. 避免非ASCII字符
```python
# 避免
print("设置构建环境...")

# 推荐
print("Setting up build environment...")
```

### 3. 平台特定处理
```python
if platform.system() == 'Windows':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass
```

## 🔍 验证方法

1. **推送修复代码**
2. **触发Windows构建**
3. **检查构建日志**确认不再有Unicode错误
4. **验证dist目录创建**和文件生成
5. **确认Windows包**在Release中正确出现

## 📚 相关资源

- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [Windows Code Pages](https://docs.microsoft.com/en-us/windows/win32/intl/code-pages)
- [GitHub Actions Windows Environment](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)

---

**修复时间**: 2025-07-19  
**影响范围**: Windows构建流程  
**风险等级**: 低 (功能保持不变)  
**测试状态**: 待验证
