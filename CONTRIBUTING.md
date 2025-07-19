# 贡献指南

感谢您对现代录屏工具项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题
1. 在提交问题前，请先搜索现有的[Issues](https://github.com/lyman86/ScreenRecordeTool/issues)
2. 使用清晰的标题描述问题
3. 提供详细的问题描述，包括：
   - 操作系统和版本
   - Python版本
   - 错误信息和堆栈跟踪
   - 重现步骤

### 提交功能请求
1. 检查是否已有类似的功能请求
2. 详细描述新功能的用途和价值
3. 如果可能，提供设计草图或示例

### 代码贡献

#### 开发环境设置
```bash
# 1. Fork并克隆仓库
git clone https://github.com/YOUR_USERNAME/ScreenRecordeTool.git
cd ScreenRecordeTool

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python test_installation.py
```

#### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 保持代码简洁和可读性

#### 提交流程
1. 创建新分支：`git checkout -b feature/your-feature-name`
2. 进行更改并提交：`git commit -m "Add: your feature description"`
3. 推送分支：`git push origin feature/your-feature-name`
4. 创建Pull Request

#### Pull Request指南
- 使用清晰的标题描述更改
- 在描述中解释更改的原因和影响
- 确保所有测试通过
- 保持提交历史清晰

### 测试
- 运行 `python test_installation.py` 确保基本功能正常
- 在不同平台上测试（如果可能）
- 添加新功能的测试用例

### 文档
- 更新README.md（如果需要）
- 添加或更新代码注释
- 更新用户文档

## 开发指南

### 项目结构
```
src/
├── config/          # 配置管理
├── core/           # 核心功能
├── ui/             # 用户界面
└── utils/          # 工具函数
```

### 添加新功能
1. 在相应模块中添加功能代码
2. 更新配置（如果需要）
3. 更新UI（如果需要）
4. 添加测试
5. 更新文档

### 构建和测试
```bash
# 运行测试
python test_installation.py

# 构建应用
python build.py

# 平台特定构建
python build_scripts/build_windows.py  # Windows
python build_scripts/build_macos.py    # macOS
```

## 社区准则

### 行为准则
- 尊重所有贡献者
- 保持友好和专业的交流
- 欢迎新手和不同背景的贡献者
- 专注于建设性的反馈

### 沟通渠道
- GitHub Issues：问题报告和功能请求
- GitHub Discussions：一般讨论和问答
- Pull Requests：代码审查和讨论

## 发布流程

### 版本号规则
使用语义化版本号：`MAJOR.MINOR.PATCH`
- MAJOR：不兼容的API更改
- MINOR：向后兼容的功能添加
- PATCH：向后兼容的错误修复

### 发布步骤
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Git标签
4. GitHub Actions自动构建和发布

## 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下发布。

## 联系方式

如有疑问，请通过以下方式联系：
- GitHub Issues
- 邮箱：1050032593@qq.com

感谢您的贡献！
