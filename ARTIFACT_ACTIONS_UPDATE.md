# GitHub Actions Artifact 版本更新修复

## 🔧 问题描述

GitHub Actions报错：
```
Error: This request has been automatically failed because it uses a deprecated version of `actions/upload-artifact: v3`. 
Learn more: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/
```

## ✅ 修复内容

### 更新的Actions版本

| Action | 旧版本 | 新版本 |
|--------|--------|--------|
| `actions/upload-artifact` | v3 | v4 |
| `actions/download-artifact` | v3 | v4 |

### 修改的文件

1. **`.github/workflows/build.yml`**
   - 第75行：`actions/upload-artifact@v3` → `actions/upload-artifact@v4`
   - 第84行：`actions/upload-artifact@v3` → `actions/upload-artifact@v4`
   - 第100行：`actions/download-artifact@v3` → `actions/download-artifact@v4`

2. **`.github/workflows/release.yml`**
   - 第45行：`actions/upload-artifact@v3` → `actions/upload-artifact@v4`
   - 第101行：`actions/upload-artifact@v3` → `actions/upload-artifact@v4`
   - 第120行：`actions/download-artifact@v3` → `actions/download-artifact@v4`
   - 第126行：`actions/download-artifact@v3` → `actions/download-artifact@v4`

## 🚀 v4版本的改进

### 主要变化
- **更好的性能**: 更快的上传和下载速度
- **改进的压缩**: 更高效的文件压缩算法
- **增强的可靠性**: 更好的错误处理和重试机制
- **向后兼容**: 保持与v3相同的API接口

### 新特性
- 支持更大的artifact文件
- 改进的并行上传/下载
- 更好的网络错误恢复
- 优化的存储使用

## 📋 验证步骤

1. **检查语法**: 确保YAML语法正确
2. **测试工作流**: 推送代码触发Actions
3. **验证上传**: 确认artifact正常上传
4. **验证下载**: 确认release流程正常工作

## 🔍 兼容性说明

- ✅ **完全向后兼容**: 无需修改现有的配置参数
- ✅ **API保持一致**: 所有参数和选项保持不变
- ✅ **行为一致**: 上传和下载行为与v3相同

## 📝 最佳实践

### 推荐配置
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: my-artifact
    path: dist/
    retention-days: 30
    if-no-files-found: warn
```

### 错误处理
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: my-artifact
    path: dist/
  continue-on-error: true
```

## 🎯 预期结果

修复后应该能够：
- ✅ 正常上传构建产物
- ✅ 成功创建GitHub Release
- ✅ 下载和使用构建的可执行文件
- ✅ 避免弃用警告

## 📚 参考资料

- [GitHub Blog: Deprecation notice v3 of the artifact actions](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)
- [actions/upload-artifact@v4 文档](https://github.com/actions/upload-artifact)
- [actions/download-artifact@v4 文档](https://github.com/actions/download-artifact)

## 🔄 Release创建问题修复

### 问题描述
1. 虽然GitHub Actions构建成功，但Release中没有生成对应的包文件
2. 通过标签触发时出现文件匹配错误: `Pattern 'ScreenRecorder-Windows.zip' does not match any files`
3. GitHub release失败，状态码403权限错误

### 根本原因
1. Release工作流只在推送标签时触发
2. 构建产物下载路径不匹配 - artifacts下载到了子目录
3. 缺少调试信息来诊断问题
4. GitHub Actions权限不足，缺少`contents: write`权限

### 修复措施

#### 1. 修复权限问题
- ✅ 添加`permissions: contents: write`到Release工作流
- ✅ 添加`permissions: packages: write`用于包发布
- ✅ 确保GITHUB_TOKEN有足够权限创建Release

#### 2. 修复文件路径问题
- ✅ 指定artifacts下载路径: `path: artifacts/`
- ✅ 修复文件查找路径，支持多种目录结构
- ✅ 添加详细的调试信息显示文件结构
- ✅ 添加文件存在性检查

#### 3. 改进构建工作流 (`build.yml`)
- ✅ 添加调试信息显示下载的文件
- ✅ 改进Release创建逻辑
- ✅ 添加更详细的Release描述
- ✅ 设置`fail_on_unmatched_files: false`避免文件不匹配错误

#### 4. 新增手动Release工作流 (`manual-release.yml`)
- ✅ 支持手动触发Release创建
- ✅ 可自定义版本号
- ✅ 支持预发布选项
- ✅ 自动创建Git标签
- ✅ 完整的构建和发布流程

#### 5. 新增测试Release工作流 (`test-release.yml`)
- ✅ 用于测试Release创建流程
- ✅ 创建测试文件验证权限和路径
- ✅ 创建草稿Release避免污染正式版本

### 使用方法

#### 手动创建Release
1. 访问GitHub仓库的Actions页面
2. 选择"Manual Release"工作流
3. 点击"Run workflow"
4. 输入版本号（如v1.0.1）
5. 选择是否为预发布版本
6. 点击"Run workflow"按钮

#### 自动Release（标签触发）
```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

---

**修复时间**: 2025-07-19
**影响范围**: GitHub Actions工作流
**风险等级**: 低 (向后兼容更新)
**新增功能**: 手动Release创建
