# 现代录屏工具 (Modern Screen Recorder)

[![Build Status](https://github.com/lyman86/ScreenRecordeTool/workflows/Continuous%20Integration/badge.svg)](https://github.com/lyman86/ScreenRecordeTool/actions)
[![Release](https://github.com/lyman86/ScreenRecordeTool/workflows/Build%20and%20Release/badge.svg)](https://github.com/lyman86/ScreenRecordeTool/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一款功能强大且符合现代UI设计的跨平台录屏软件，支持Windows和macOS。

## 📥 下载

### 预编译版本
- [Windows版本下载](https://github.com/lyman86/ScreenRecordeTool/releases/latest)
- [macOS版本下载](https://github.com/lyman86/ScreenRecordeTool/releases/latest)

### 从源码构建
请参考下面的[快速开始](#快速开始)部分。

## 功能特性

### 核心功能
- 🎥 高质量屏幕录制 (支持多种分辨率和帧率)
- 🎵 同步音频录制 (支持系统音频和麦克风)
- 🖥️ 多显示器支持 (可选择特定显示器录制)
- 📱 区域选择录制 (自由选择录制区域)
- ⏯️ 实时录制控制 (开始/暂停/停止)

### 高级功能
- 🎨 现代化UI设计 (Material Design风格)
- ⚡ 实时预览 (录制过程中实时查看)
- 🔧 多种输出格式 (MP4, AVI, MOV, WebM)
- ⌨️ 全局快捷键支持 (可自定义快捷键)
- 🎛️ 录制参数调节 (质量、帧率、编码器等)
- 📹 视频后处理 (格式转换、压缩、裁剪)
- 🔊 音频提取 (从视频中提取音频)
- ⚙️ 高级设置 (硬件加速、多线程编码等)

### 输出格式
- **视频**: MP4 (H.264/H.265), AVI, MOV, WebM, MKV
- **音频**: MP3, AAC, OGG, WAV
- **图片**: PNG, JPG (截图功能)

## 系统要求

### Windows
- Windows 10 或更高版本 (推荐 Windows 11)
- 4GB RAM (推荐 8GB 或更多)
- 支持硬件加速的显卡 (可选)
- 1GB 可用磁盘空间

### macOS
- macOS 10.15 (Catalina) 或更高版本
- 4GB RAM (推荐 8GB 或更多)
- Intel 或 Apple Silicon 处理器
- 1GB 可用磁盘空间

## 快速开始

### 方法一：直接运行 (推荐)
```bash
# 1. 克隆项目
git clone https://github.com/lyman86/ScreenRecordeTool.git
cd ScreenRecordeTool

# 2. 运行安装脚本
python setup.py

# 3. 测试安装
python test_installation.py

# 4. 启动应用
python main.py
```

### 方法二：手动安装
```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 运行程序
python main.py
```

## 构建可执行文件

### 自动构建 (推荐)
```bash
# 自动检测平台并构建
python build.py

# 或使用平台特定的脚本
# Windows:
scripts\build.bat

# macOS/Linux:
chmod +x scripts/build.sh
./scripts/build.sh
```

### 手动构建

#### Windows
```bash
# 运行Windows构建脚本
python build_scripts/build_windows.py

# 输出文件: dist/ScreenRecorder.exe
```

#### macOS
```bash
# 运行macOS构建脚本
python build_scripts/build_macos.py

# 输出文件: dist/ScreenRecorder.app
```

### GitHub Actions自动构建

项目配置了GitHub Actions自动构建流程：

- **持续集成**: 每次推送代码时自动运行测试
- **自动构建**: 创建Release时自动构建Windows和macOS版本
- **自动发布**: 构建完成后自动上传到GitHub Releases

#### 手动触发构建
1. 进入项目的GitHub页面
2. 点击"Actions"标签
3. 选择"Release Build"工作流
4. 点击"Run workflow"按钮
5. 输入版本号（如v1.0.0）并运行

## 使用说明

### 基本录制
1. 启动应用程序
2. 选择录制设置 (帧率、质量、格式等)
3. 点击"开始录制"按钮
4. 录制完成后点击"停止录制"

### 区域录制
1. 点击"选择区域"按钮
2. 拖拽鼠标选择要录制的区域
3. 开始录制

### 快捷键 (可自定义)
- `F9`: 开始/停止录制
- `F10`: 暂停/恢复录制
- `F11`: 截图
- `Ctrl+Shift+A`: 选择录制区域
- `Ctrl+Shift+R`: 显示/隐藏主窗口

### 视频处理
1. 录制完成后，右键点击视频文件
2. 选择"导出"或"处理"
3. 选择所需的处理选项 (转换、压缩、裁剪等)

## 项目结构
```
ScreenRecordeTool/
├── main.py                     # 主程序入口
├── setup.py                    # 安装脚本
├── build.py                    # 通用构建脚本
├── test_installation.py        # 安装测试脚本
├── requirements.txt            # Python依赖
├── README.md                   # 项目说明
├── src/                        # 源代码目录
│   ├── config/                 # 配置模块
│   │   └── settings.py         # 应用配置
│   ├── core/                   # 核心功能模块
│   │   ├── screen_capture.py   # 屏幕捕获
│   │   ├── audio_capture.py    # 音频录制
│   │   ├── video_encoder.py    # 视频编码
│   │   └── video_processor.py  # 视频处理
│   ├── ui/                     # 用户界面模块
│   │   ├── main_window.py      # 主窗口
│   │   ├── settings_window.py  # 设置窗口
│   │   ├── export_dialog.py    # 导出对话框
│   │   └── region_selector.py  # 区域选择器
│   └── utils/                  # 工具模块
│       ├── platform_utils.py   # 平台工具
│       ├── config_manager.py   # 配置管理
│       └── hotkey_manager.py   # 快捷键管理
├── build_scripts/              # 构建脚本
│   ├── build_windows.py        # Windows构建
│   └── build_macos.py          # macOS构建
├── resources/                  # 资源文件
├── tests/                      # 测试文件
├── build/                      # 构建临时文件
└── dist/                       # 构建输出
```

## 开发指南

### 环境设置
```bash
# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
```

### 代码结构说明
- `src/core/`: 核心录制功能，包括屏幕捕获、音频录制、视频编码
- `src/ui/`: 用户界面，使用PyQt6构建现代化界面
- `src/utils/`: 工具函数，包括平台兼容性、配置管理等
- `src/config/`: 配置文件和设置管理

### 添加新功能
1. 在相应的模块中添加功能代码
2. 更新UI界面 (如需要)
3. 添加配置选项 (如需要)
4. 更新测试脚本
5. 更新文档

## 故障排除

### 常见问题

#### Windows
- **问题**: 无法录制音频
  - **解决**: 检查音频设备权限，确保麦克风未被其他应用占用
- **问题**: 录制的视频文件很大
  - **解决**: 调整录制质量设置，选择较低的比特率或帧率
- **问题**: 构建失败
  - **解决**: 确保安装了Visual C++ Redistributable

#### macOS
- **问题**: 提示需要屏幕录制权限
  - **解决**: 前往 系统偏好设置 > 安全性与隐私 > 隐私 > 屏幕录制，添加应用权限
- **问题**: 无法录制音频
  - **解决**: 在 系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风 中授予权限
- **问题**: 应用无法启动
  - **解决**: 检查是否安装了所有依赖，运行 `python test_installation.py` 进行诊断

### 性能优化
- 降低录制帧率 (30fps 通常足够)
- 选择合适的录制质量
- 启用硬件加速 (如果支持)
- 定期清理临时文件

### 获取帮助
- 查看错误日志
- 运行测试脚本诊断问题
- 检查系统权限设置
- 确认依赖库版本兼容性

## 技术栈

### 核心技术
- **Python 3.8+**: 主要开发语言
- **PyQt6**: 现代化GUI框架
- **OpenCV**: 视频处理和编码
- **PyAudio**: 音频录制
- **MSS**: 高性能屏幕捕获
- **FFmpeg**: 视频格式转换和处理

### 可选依赖
- **Keyboard**: 全局快捷键支持
- **PyNput**: 输入事件处理
- **Pillow**: 图像处理
- **ImageIO**: 图像和视频I/O

## 贡献指南

### 如何贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档字符串
- 编写单元测试
- 确保跨平台兼容性

## 版本历史

### v1.0.0 (当前版本)
- ✅ 基本屏幕录制功能
- ✅ 音频录制支持
- ✅ 现代化UI界面
- ✅ 多显示器支持
- ✅ 区域选择录制
- ✅ 视频格式转换
- ✅ 全局快捷键
- ✅ 跨平台支持 (Windows/macOS)

### 计划功能
- 🔄 实时流媒体推送
- 🔄 云存储集成
- 🔄 视频编辑功能
- 🔄 多语言支持
- 🔄 插件系统

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 现代化GUI框架
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [FFmpeg](https://ffmpeg.org/) - 多媒体处理框架
- [MSS](https://github.com/BoboTiG/python-mss) - 屏幕截图库

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/lyman86/ScreenRecordeTool)
- 问题反馈: [GitHub Issues](https://github.com/lyman86/ScreenRecordeTool/issues)
- 邮箱: 1050032593@qq.com

---

**现代录屏工具** - 让屏幕录制变得简单而强大！
