"""
FFmpeg安装对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

class FFmpegInstallDialog(QDialog):
    """FFmpeg安装对话框"""
    
    # 信号
    install_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFmpeg安装")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("FFmpeg安装向导")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 说明信息
        info_group = QGroupBox("关于FFmpeg")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
FFmpeg是一个强大的多媒体处理工具，用于：

• 合并录制的音频和视频文件
• 提供更好的视频编码质量
• 支持多种视频格式输出
• 优化文件大小和播放兼容性

安装FFmpeg将显著提升录屏工具的功能和性能。
        """.strip())
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # 安装选项
        options_group = QGroupBox("安装选项")
        options_layout = QVBoxLayout(options_group)
        
        # 自动安装说明
        auto_label = QLabel("✅ 自动安装（推荐）")
        auto_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        options_layout.addWidget(auto_label)
        
        auto_desc = QLabel("• 自动下载并安装FFmpeg\n• 无需手动配置\n• 适合大多数用户")
        options_layout.addWidget(auto_desc)
        
        # 手动安装说明
        manual_label = QLabel("⚙️ 手动安装")
        manual_label.setStyleSheet("font-weight: bold; color: #FF9800;")
        options_layout.addWidget(manual_label)
        
        manual_desc = QLabel("• 从官网下载FFmpeg\n• 手动配置环境变量\n• 适合高级用户")
        options_layout.addWidget(manual_desc)
        
        layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.manual_btn = QPushButton("手动安装指南")
        self.manual_btn.clicked.connect(self.show_manual_guide)
        button_layout.addWidget(self.manual_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.install_btn = QPushButton("自动安装")
        self.install_btn.setDefault(True)
        self.install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                color: #333333;
            }
            QLabel {
                color: #333333;
                background-color: transparent;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #333333;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f5f5f5;
                color: #333333;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#cancel_btn {
                background-color: #757575;
                color: white;
            }
            QPushButton#cancel_btn:hover {
                background-color: #616161;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        self.cancel_btn.setObjectName("cancel_btn")
    
    def start_installation(self):
        """开始安装"""
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setVisible(True)
        self.status_label.setText("准备安装...")
        
        # 禁用按钮
        self.install_btn.setEnabled(False)
        self.manual_btn.setEnabled(False)
        
        # 发送安装信号
        self.install_requested.emit()
    
    def update_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
    
    def installation_finished(self, success, message):
        """安装完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        
        if success:
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.install_btn.setText("安装成功")
            self.install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            # 2秒后自动关闭
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self.accept)
        else:
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.install_btn.setEnabled(True)
            self.manual_btn.setEnabled(True)
            self.install_btn.setText("重试安装")
    
    def show_manual_guide(self):
        """显示手动安装指南"""
        from PyQt6.QtWidgets import QMessageBox
        
        guide_text = """
手动安装FFmpeg指南：

macOS:
1. 使用Homebrew: brew install ffmpeg
2. 或从 https://ffmpeg.org/download.html 下载
3. 解压后将ffmpeg添加到PATH环境变量

Windows:
1. 从 https://ffmpeg.org/download.html 下载
2. 解压到C:\\ffmpeg
3. 将C:\\ffmpeg\\bin添加到系统PATH

Linux:
1. Ubuntu/Debian: sudo apt install ffmpeg
2. CentOS/RHEL: sudo yum install ffmpeg
3. 或从官网下载编译

安装完成后重启应用程序即可。
        """
        
        QMessageBox.information(self, "手动安装指南", guide_text)
