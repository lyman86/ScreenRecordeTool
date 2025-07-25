# 更新日志

本文档记录了现代录屏工具的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。


## [v1.0.9] - 2025-07-20

- test

## [未发布]

### 新增
- GitHub Actions自动构建和发布流程
- 跨平台构建脚本（Windows和macOS）
- 安装测试脚本
- 贡献指南和行为准则
- MIT许可证

### 改进
- 完善项目文档和README
- 添加构建状态徽章
- 优化项目结构

### 修复
- 修复PyQt6兼容性问题
- 改进错误处理和用户反馈

## [1.0.0] - 2024-07-19

### 新增
- 🎥 高质量屏幕录制功能
- 🎵 同步音频录制（系统音频和麦克风）
- 🖥️ 多显示器支持
- 📱 区域选择录制
- ⏯️ 实时录制控制（开始/暂停/停止）
- 🎨 现代化UI设计（Material Design风格）
- ⚡ 实时预览功能
- 🔧 多种输出格式（MP4, AVI, MOV, WebM）
- ⌨️ 全局快捷键支持
- 🎛️ 录制参数调节
- 📹 视频后处理功能
- 🔊 音频提取功能
- ⚙️ 高级设置（硬件加速、多线程编码）

### 技术特性
- 基于Python 3.8+和PyQt6
- 使用OpenCV进行视频处理
- MSS库实现高性能屏幕捕获
- PyAudio处理音频录制
- PyInstaller打包可执行文件

### 支持平台
- Windows 10/11
- macOS 10.15+

### 输出格式
- 视频：MP4 (H.264/H.265), AVI, MOV, WebM, MKV
- 音频：MP3, AAC, OGG, WAV
- 图片：PNG, JPG（截图功能）

---

## 版本说明

### 版本号格式
- **主版本号**：不兼容的API更改
- **次版本号**：向后兼容的功能添加
- **修订号**：向后兼容的错误修复

### 更改类型
- **新增**：新功能
- **改进**：现有功能的改进
- **修复**：错误修复
- **移除**：移除的功能
- **安全**：安全相关的修复

### 发布周期
- 主版本：重大功能更新或架构变更
- 次版本：新功能和改进
- 修订版：错误修复和小改进

---

## 贡献

如果您想为项目做出贡献，请查看我们的[贡献指南](CONTRIBUTING.md)。

## 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。
