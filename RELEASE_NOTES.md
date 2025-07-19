# ScreenRecorder 发布说明

## 项目简介

ScreenRecorder 是一个跨平台的屏幕录制工具，支持 Windows、macOS 和 Linux 系统。

## 主要功能

- 🎥 **全屏录制**: 支持录制整个屏幕或指定显示器
- 🎯 **区域录制**: 可以选择特定区域进行录制
- 🎵 **音频录制**: 支持系统音频和麦克风录制
- ⚙️ **多种格式**: 支持 MP4、AVI、MOV 等多种视频格式
- 🎛️ **质量控制**: 可调节视频质量和帧率
- ⌨️ **热键控制**: 支持全局热键快速控制录制
- 🖥️ **跨平台**: 支持 Windows、macOS、Linux

## 系统要求

### Windows
- Windows 10 或更高版本
- Python 3.9+ (如果从源码运行)

### macOS
- macOS 10.14 或更高版本
- Python 3.9+ (如果从源码运行)

### Linux
- Ubuntu 18.04+ 或其他主流发行版
- Python 3.9+ (如果从源码运行)
- 需要安装相关系统依赖

## 安装方式

### 方式一：下载预编译版本
1. 访问 [Releases 页面](https://github.com/YOUR_USERNAME/ScreenRecordeTool/releases)
2. 下载对应平台的最新版本
3. 解压并运行

### 方式二：从源码运行
```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/ScreenRecordeTool.git
cd ScreenRecordeTool

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方式三：构建可执行文件
```bash
# 安装构建依赖
pip install pyinstaller

# 构建
python build.py

# 可执行文件将在 dist/ 目录中生成
```

## 使用说明

1. **启动程序**: 运行 `main.py` 或双击可执行文件
2. **选择录制区域**: 
   - 全屏录制：保持默认设置
   - 区域录制：点击"选择区域"按钮
3. **配置设置**:
   - 选择输出格式 (MP4/AVI/MOV)
   - 设置视频质量
   - 调整帧率
   - 选择音频录制选项
4. **开始录制**: 点击"开始录制"按钮
5. **停止录制**: 点击"停止录制"按钮或使用热键

## 热键说明

- `F9`: 开始/停止录制
- `F10`: 暂停/恢复录制
- `F11`: 截图

## 技术栈

- **GUI框架**: PyQt6
- **屏幕捕获**: mss
- **视频编码**: OpenCV
- **音频处理**: PyAudio
- **打包工具**: PyInstaller
- **CI/CD**: GitHub Actions

## 开发说明

### 项目结构
```
ScreenRecordeTool/
├── src/
│   ├── core/           # 核心功能模块
│   ├── ui/             # 用户界面
│   ├── utils/          # 工具函数
│   └── config/         # 配置管理
├── build_scripts/      # 构建脚本
├── .github/workflows/  # GitHub Actions
├── requirements.txt    # Python依赖
├── build.py           # 构建脚本
└── main.py            # 程序入口
```

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 自动构建和发布

本项目使用 GitHub Actions 进行自动构建和发布：

### 触发条件
- **推送标签**: 当推送 `v*` 格式的标签时，会自动构建并创建 Release
- **Pull Request**: 对 main/master 分支的 PR 会触发构建测试
- **手动触发**: 可以在 Actions 页面手动触发构建

### 构建矩阵
- **操作系统**: Windows, macOS, Ubuntu
- **Python版本**: 3.9, 3.10, 3.11, 3.12
- **输出格式**: 
  - Windows: `.exe` 文件和便携版
  - macOS: `.app` 应用和 `.dmg` 安装包
  - Linux: 可执行文件和 `.tar.gz` 压缩包

### 发布流程

1. **创建标签**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动构建**: GitHub Actions 会自动：
   - 在多个平台上构建应用
   - 运行测试
   - 创建 Release
   - 上传构建产物

3. **下载使用**: 用户可以从 Releases 页面下载对应平台的版本

## 故障排除

### 常见问题

1. **录制失败**:
   - 检查是否有足够的磁盘空间
   - 确认输出目录有写入权限
   - 检查文件名是否包含非法字符

2. **音频录制问题**:
   - 确认音频设备正常工作
   - 检查音频权限设置
   - 尝试重启应用程序

3. **性能问题**:
   - 降低录制质量或帧率
   - 关闭其他占用资源的程序
   - 确保有足够的内存

### 日志文件

程序运行时会生成日志文件，位于：
- Windows: `%APPDATA%/ScreenRecorder/logs/`
- macOS: `~/Library/Application Support/ScreenRecorder/logs/`
- Linux: `~/.local/share/ScreenRecorder/logs/`

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 更新日志

### v1.0.0 (即将发布)
- 初始版本发布
- 支持跨平台屏幕录制
- 实现区域选择功能
- 添加音频录制支持
- 集成热键控制
- 自动构建和发布流程

## 联系方式

- 项目主页: https://github.com/YOUR_USERNAME/ScreenRecordeTool
- 问题反馈: https://github.com/YOUR_USERNAME/ScreenRecordeTool/issues
- 功能建议: https://github.com/YOUR_USERNAME/ScreenRecordeTool/discussions

---

感谢使用 ScreenRecorder！如果您觉得这个项目有用，请给我们一个 ⭐️