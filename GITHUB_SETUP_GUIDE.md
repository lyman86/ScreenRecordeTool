# GitHub 仓库创建和发布指南

## 第一步：在 GitHub 上创建仓库

1. **登录 GitHub**
   - 访问 https://github.com
   - 登录您的 GitHub 账户

2. **创建新仓库**
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"
   - 填写仓库信息：
     - **Repository name**: `ScreenRecordeTool`
     - **Description**: `跨平台屏幕录制工具 - Cross-platform screen recording tool`
     - **Visibility**: 选择 Public（公开）或 Private（私有）
     - **不要**勾选 "Add a README file"（我们已经有了）
     - **不要**勾选 "Add .gitignore"（我们已经有了）
     - **不要**选择 "Choose a license"（我们已经有了）
   - 点击 "Create repository"

## 第二步：推送代码到 GitHub

在您的项目目录中执行以下命令：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/ScreenRecordeTool.git

# 设置主分支名称
git branch -M main

# 推送代码到 GitHub
git push -u origin main
```

## 第三步：配置仓库设置

1. **启用 GitHub Actions**
   - 在仓库页面，点击 "Actions" 标签
   - 如果提示启用 Actions，点击 "I understand my workflows, go ahead and enable them"

2. **设置仓库描述和标签**
   - 在仓库主页，点击右侧的齿轮图标（Settings）
   - 在 "About" 部分添加：
     - **Description**: `跨平台屏幕录制工具，支持区域录制、音频录制和热键控制`
     - **Website**: 可以留空或添加项目主页
     - **Topics**: 添加标签如 `screen-recorder`, `python`, `pyqt6`, `cross-platform`, `video-recording`

3. **配置 Pages（可选）**
   - 在 Settings → Pages 中可以设置项目文档页面

## 第四步：创建第一个 Release

1. **创建标签并推送**
   ```bash
   # 创建版本标签
   git tag v1.0.0
   
   # 推送标签到 GitHub
   git push origin v1.0.0
   ```

2. **GitHub Actions 自动构建**
   - 推送标签后，GitHub Actions 会自动开始构建
   - 在 "Actions" 标签页可以查看构建进度
   - 构建完成后会自动创建 Release

3. **手动创建 Release（如果需要）**
   - 在仓库主页，点击右侧的 "Releases"
   - 点击 "Create a new release"
   - 选择刚才创建的标签 `v1.0.0`
   - 填写 Release 信息：
     - **Release title**: `ScreenRecorder v1.0.0`
     - **Description**: 复制 RELEASE_NOTES.md 中的内容
   - 点击 "Publish release"

## 第五步：验证自动构建

1. **检查 Actions 状态**
   - 访问仓库的 "Actions" 页面
   - 确认构建任务正在运行或已完成
   - 如果有错误，查看日志并修复

2. **下载构建产物**
   - 构建完成后，在 "Actions" 页面可以下载 Artifacts
   - 或者在 "Releases" 页面下载正式发布的文件

## 第六步：更新文档中的链接

在以下文件中将 `YOUR_USERNAME` 替换为您的实际 GitHub 用户名：

1. **RELEASE_NOTES.md**
   ```bash
   # 使用文本编辑器或命令行替换
   # Windows (PowerShell)
   (Get-Content RELEASE_NOTES.md) -replace 'YOUR_USERNAME', '您的用户名' | Set-Content RELEASE_NOTES.md
   
   # macOS/Linux
   sed -i 's/YOUR_USERNAME/您的用户名/g' RELEASE_NOTES.md
   ```

2. **README.md**（如果有相关链接）

3. **提交更新**
   ```bash
   git add .
   git commit -m "Update GitHub links with actual username"
   git push origin main
   ```

## 常用 Git 命令

```bash
# 查看仓库状态
git status

# 查看提交历史
git log --oneline

# 查看远程仓库
git remote -v

# 拉取最新代码
git pull origin main

# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 发布新版本的流程

1. **开发和测试新功能**
2. **更新版本号**（在相关文件中）
3. **更新 RELEASE_NOTES.md**
4. **提交所有更改**
   ```bash
   git add .
   git commit -m "Release v1.1.0: Add new features"
   git push origin main
   ```
5. **创建新标签**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
6. **GitHub Actions 自动构建和发布**

## 故障排除

### 推送失败
```bash
# 如果推送被拒绝，可能需要先拉取
git pull origin main --rebase
git push origin main
```

### Actions 构建失败
1. 检查 `.github/workflows/build.yml` 文件
2. 查看 Actions 页面的错误日志
3. 修复问题后重新推送

### 权限问题
1. 确认您有仓库的写入权限
2. 检查 GitHub token 是否有效
3. 可能需要使用 SSH 密钥而不是 HTTPS

## 安全注意事项

1. **不要提交敏感信息**
   - API 密钥
   - 密码
   - 个人信息

2. **使用 .gitignore**
   - 已经配置好，确保敏感文件不会被提交

3. **定期更新依赖**
   - 使用 `pip list --outdated` 检查过时的包
   - 更新 requirements.txt

## 社区参与

1. **启用 Issues**
   - 在 Settings → Features 中确保 Issues 已启用
   - 用户可以报告 bug 和请求功能

2. **启用 Discussions**
   - 在 Settings → Features 中启用 Discussions
   - 用于社区讨论和问答

3. **贡献指南**
   - 可以创建 CONTRIBUTING.md 文件
   - 说明如何贡献代码

---

完成以上步骤后，您的 ScreenRecorder 项目就成功上传到 GitHub 并配置了自动构建和发布功能！