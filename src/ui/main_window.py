"""
主窗口UI
"""

import os
import sys
import cv2
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QSlider, QProgressBar,
    QGroupBox, QCheckBox, QLineEdit, QFileDialog, QMessageBox,
    QSystemTrayIcon, QMenu, QStatusBar, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QPalette, QColor

# 导入核心模块
sys.path.append(str(Path(__file__).parent.parent))
from core.screen_capture import ScreenCapture
from core.audio_capture import AudioCapture
from core.video_encoder import VideoEncoder, ScreenRecorder
from config.settings import AppConfig, UIConfig

class ModernButton(QPushButton):
    """现代化按钮样式"""
    
    def __init__(self, text="", icon_path="", primary=False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setFont(QFont(UIConfig.FONTS["default"], 10))
        
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {UIConfig.COLORS["primary"]};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                QPushButton:pressed {{
                    background-color: #1565C0;
                }}
                QPushButton:disabled {{
                    background-color: #CCCCCC;
                    color: #666666;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {UIConfig.COLORS["light"]};
                    color: {UIConfig.COLORS["dark"]};
                    border: 1px solid #DDDDDD;
                    border-radius: 8px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #E9ECEF;
                    border-color: {UIConfig.COLORS["primary"]};
                }}
                QPushButton:pressed {{
                    background-color: #DEE2E6;
                }}
                QPushButton:disabled {{
                    background-color: #F8F9FA;
                    color: #6C757D;
                    border-color: #E9ECEF;
                }}
            """)

class StatusIndicator(QLabel):
    """状态指示器"""
    
    def __init__(self, text="就绪"):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(80, 30)
        self.setMaximumSize(120, 30)
        self.set_status("ready")
    
    def set_status(self, status):
        """设置状态"""
        status_styles = {
            "ready": f"background-color: {UIConfig.COLORS['light']}; color: {UIConfig.COLORS['dark']}; border: 1px solid #DDDDDD;",
            "recording": f"background-color: {UIConfig.COLORS['danger']}; color: white;",
            "paused": f"background-color: {UIConfig.COLORS['warning']}; color: white;",
            "processing": f"background-color: {UIConfig.COLORS['info']}; color: white;"
        }
        
        style = status_styles.get(status, status_styles["ready"])
        self.setStyleSheet(f"""
            QLabel {{
                {style}
                border-radius: 15px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 10px;
            }}
        """)

class PreviewWidget(QLabel):
    """预览窗口"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #DDDDDD;
                border-radius: 8px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("预览窗口\n点击开始录制后显示")
        self.setStyleSheet("""
            QLabel {
                background-color: #F8F9FA;
                border: 2px dashed #CCCCCC;
                border-radius: 8px;
                color: #6C757D;
                font-size: 14px;
            }
        """)
    
    def update_frame(self, pixmap):
        """更新预览帧"""
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.screen_capture = ScreenCapture()
        self.audio_capture = AudioCapture()
        self.video_encoder = VideoEncoder()
        self.screen_recorder = ScreenRecorder()
        
        # 设置录制器
        self.screen_recorder.setup(
            self.screen_capture, 
            self.video_encoder, 
            self.audio_capture
        )
        
        # 状态变量
        self.is_recording = False
        self.is_paused = False
        self.output_path = AppConfig.get_default_output_dir()
        
        # 定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # 100ms更新一次
        
        self.init_ui()
        self.connect_signals()
        self.setup_system_tray()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        self.setMinimumSize(*UIConfig.MAIN_WINDOW_SIZE)
        self.resize(*UIConfig.MAIN_WINDOW_SIZE)
        
        # 设置中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # 右侧预览面板
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 500])
        
        # 创建状态栏
        self.create_status_bar()
        
        # 应用样式
        self.apply_styles()
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QWidget()
        panel.setMaximumWidth(350)
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)

        # 录制控制组
        record_group = QGroupBox("录制控制")
        record_layout = QVBoxLayout(record_group)

        # 状态指示器
        self.status_indicator = StatusIndicator("就绪")
        record_layout.addWidget(self.status_indicator)

        # 主要按钮
        button_layout = QHBoxLayout()
        self.record_btn = ModernButton("开始录制", primary=True)
        self.pause_btn = ModernButton("暂停")
        self.stop_btn = ModernButton("停止")

        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.record_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        record_layout.addLayout(button_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        record_layout.addWidget(self.progress_bar)

        layout.addWidget(record_group)

        # 录制设置组
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)

        # 输出设置组
        output_group = self.create_output_group()
        layout.addWidget(output_group)

        # 添加弹性空间
        layout.addStretch()

        return panel
    
    def create_settings_group(self):
        """创建设置组"""
        group = QGroupBox("录制设置")
        layout = QGridLayout(group)

        # 帧率设置
        layout.addWidget(QLabel("帧率:"), 0, 0)
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([str(fps) for fps in AppConfig.FPS_OPTIONS])
        self.fps_combo.setCurrentText(str(AppConfig.DEFAULT_FPS))
        layout.addWidget(self.fps_combo, 0, 1)

        # 质量设置
        layout.addWidget(QLabel("质量:"), 1, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(list(AppConfig.QUALITY_SETTINGS.keys()))
        self.quality_combo.setCurrentText(AppConfig.DEFAULT_QUALITY)
        layout.addWidget(self.quality_combo, 1, 1)

        # 格式设置
        layout.addWidget(QLabel("格式:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(AppConfig.SUPPORTED_FORMATS)
        self.format_combo.setCurrentText(AppConfig.DEFAULT_FORMAT)
        layout.addWidget(self.format_combo, 2, 1)

        # 音频录制
        self.audio_checkbox = QCheckBox("录制音频")
        self.audio_checkbox.setChecked(AppConfig.DEFAULT_AUDIO_ENABLED)
        layout.addWidget(self.audio_checkbox, 3, 0, 1, 2)

        # 显示鼠标
        self.cursor_checkbox = QCheckBox("显示鼠标指针")
        self.cursor_checkbox.setChecked(AppConfig.DEFAULT_CURSOR_ENABLED)
        layout.addWidget(self.cursor_checkbox, 4, 0, 1, 2)

        # 录制区域设置
        layout.addWidget(QLabel("录制区域:"), 5, 0)
        region_layout = QHBoxLayout()
        self.region_combo = QComboBox()
        self.region_combo.addItems(["全屏", "选择区域"])
        self.region_combo.setCurrentText("全屏")
        region_layout.addWidget(self.region_combo)

        self.select_region_btn = ModernButton("选择区域")
        self.select_region_btn.setMaximumWidth(80)
        self.select_region_btn.setEnabled(False)
        region_layout.addWidget(self.select_region_btn)

        region_widget = QWidget()
        region_widget.setLayout(region_layout)
        layout.addWidget(region_widget, 5, 1)

        return group

    def create_output_group(self):
        """创建输出组"""
        group = QGroupBox("输出设置")
        layout = QVBoxLayout(group)

        # 输出路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存路径:"))

        self.output_path_edit = QLineEdit(self.output_path)
        self.output_path_edit.setReadOnly(True)
        path_layout.addWidget(self.output_path_edit)

        self.browse_btn = ModernButton("浏览")
        self.browse_btn.setMaximumWidth(80)
        path_layout.addWidget(self.browse_btn)

        layout.addLayout(path_layout)

        # 文件名设置
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("文件名:"))

        self.filename_edit = QLineEdit("录屏_{timestamp}")
        filename_layout.addWidget(self.filename_edit)

        layout.addLayout(filename_layout)

        return group

    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)

        # 预览标题
        title_layout = QHBoxLayout()
        title_label = QLabel("实时预览")
        title_label.setFont(QFont(UIConfig.FONTS["default"], 12, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 预览控制按钮
        self.preview_btn = ModernButton("开启预览")
        self.preview_btn.setMaximumWidth(100)
        title_layout.addWidget(self.preview_btn)

        layout.addLayout(title_layout)

        # 预览窗口
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        # 录制信息
        info_group = QGroupBox("录制信息")
        info_layout = QGridLayout(info_group)

        self.duration_label = QLabel("时长: 00:00:00")
        self.frames_label = QLabel("帧数: 0")
        self.size_label = QLabel("文件大小: 0 MB")

        info_layout.addWidget(self.duration_label, 0, 0)
        info_layout.addWidget(self.frames_label, 0, 1)
        info_layout.addWidget(self.size_label, 1, 0, 1, 2)

        layout.addWidget(info_group)

        return panel
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # 状态信息
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)

        # 音频电平指示器
        status_bar.addPermanentWidget(QLabel("音频:"))
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setMaximumWidth(100)
        self.audio_level_bar.setMaximumHeight(16)
        self.audio_level_bar.setRange(0, 100)
        status_bar.addPermanentWidget(self.audio_level_bar)

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {UIConfig.COLORS["light"]};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {UIConfig.COLORS["light"]};
            }}
            QComboBox, QLineEdit, QSpinBox {{
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }}
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
                border-color: {UIConfig.COLORS["primary"]};
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid #CCCCCC;
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {UIConfig.COLORS["primary"]};
                border-radius: 3px;
                background-color: {UIConfig.COLORS["primary"]};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
        """)

    def connect_signals(self):
        """连接信号"""
        # 按钮信号
        self.record_btn.clicked.connect(self.start_recording)
        self.pause_btn.clicked.connect(self.pause_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.browse_btn.clicked.connect(self.browse_output_path)
        self.preview_btn.clicked.connect(self.toggle_preview)
        self.select_region_btn.clicked.connect(self.select_recording_region)
        self.region_combo.currentTextChanged.connect(self.on_region_mode_changed)

        # 录制器信号
        self.screen_recorder.recording_started.connect(self.on_recording_started)
        self.screen_recorder.recording_stopped.connect(self.on_recording_stopped)
        self.screen_recorder.recording_paused.connect(self.on_recording_paused)
        self.screen_recorder.recording_resumed.connect(self.on_recording_resumed)
        self.screen_recorder.progress_updated.connect(self.on_progress_updated)
        self.screen_recorder.error_occurred.connect(self.on_error_occurred)

        # 屏幕捕获信号
        self.screen_capture.frame_captured.connect(self.on_frame_captured)
        self.screen_capture.frame_captured.connect(self.update_preview)

    def setup_system_tray(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self)

        # 创建默认图标
        icon = self.create_default_icon()
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")

        # 创建托盘菜单
        tray_menu = QMenu()

        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def create_default_icon(self):
        """创建默认图标"""
        # 创建一个简单的默认图标
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 120, 215))  # 蓝色背景
        return QIcon(pixmap)

    def set_recording_controls_enabled(self, enabled: bool):
        """设置录制控件的启用状态"""
        # 录制设置控件
        self.fps_combo.setEnabled(enabled)
        self.quality_combo.setEnabled(enabled)
        self.format_combo.setEnabled(enabled)
        self.audio_checkbox.setEnabled(enabled)
        self.cursor_checkbox.setEnabled(enabled)
        self.region_combo.setEnabled(enabled)
        self.select_region_btn.setEnabled(enabled and self.region_combo.currentText() == "选择区域")

        # 输出设置控件
        self.output_path_edit.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.filename_edit.setEnabled(enabled)

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的无效字符"""
        import re
        # 移除或替换无效字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除前后空格
        filename = filename.strip()
        # 确保不为空
        if not filename:
            filename = "recording"
        return filename

    def update_ui(self):
        """更新UI"""
        # 更新音频电平
        if self.audio_capture and self.is_recording:
            try:
                level = self.audio_capture.get_volume_level() * 100
                # 检查是否为有效数值
                if not (level is None or level != level or level == float('inf') or level == float('-inf')):
                    self.audio_level_bar.setValue(int(max(0, min(100, level))))
                else:
                    self.audio_level_bar.setValue(0)
            except (ValueError, TypeError, OverflowError):
                self.audio_level_bar.setValue(0)

    def update_preview(self, frame):
        """更新预览窗口"""
        try:
            if frame is not None:
                # 转换numpy数组为QPixmap
                from PyQt6.QtGui import QImage
                height, width, channel = frame.shape
                bytes_per_line = 3 * width

                # 转换BGR到RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 创建QImage
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

                # 转换为QPixmap
                pixmap = QPixmap.fromImage(q_image)

                # 更新预览窗口
                self.preview_widget.update_frame(pixmap)
        except Exception as e:
            print(f"预览更新失败: {e}")

    # 事件处理方法
    def _sanitize_filename(self, filename):
        """清理文件名中的无效字符"""
        import re
        # Windows无效字符: < > : " | ? * \ /
        # 替换为下划线
        invalid_chars = r'[<>:"|?*\\/]'
        sanitized = re.sub(invalid_chars, '_', filename)
        # 移除开头和结尾的空格和点
        sanitized = sanitized.strip(' .')
        # 如果文件名为空或只包含无效字符（下划线和空格），使用默认名称
        if not sanitized or sanitized.replace('_', '').replace(' ', '') == '':
            sanitized = "录屏"
        return sanitized

    def start_recording(self):
        """开始录制"""
        try:
            # 检查是否已在录制
            if self.is_recording:
                QMessageBox.warning(self, "提示", "录制已在进行中")
                return
            
            # 获取设置
            fps = int(self.fps_combo.currentText())
            quality = self.quality_combo.currentText()
            format_type = self.format_combo.currentText()
            
            # 验证FPS值
            if fps <= 0 or fps > 120:
                QMessageBox.warning(self, "错误", "FPS值必须在1-120之间")
                return

            # 生成输出文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.filename_edit.text().replace("{timestamp}", timestamp)
            
            # 清理文件名中的无效字符
            filename = self._sanitize_filename(filename)
            
            # 确保输出目录存在
            if not os.path.exists(self.output_path):
                try:
                    os.makedirs(self.output_path, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法创建输出目录: {str(e)}")
                    return
            
            output_path = os.path.join(self.output_path, f"{filename}.{format_type.lower()}")
            
            # 检查文件是否已存在
            if os.path.exists(output_path):
                reply = QMessageBox.question(self, "文件已存在", 
                                           f"文件 {filename}.{format_type.lower()} 已存在，是否覆盖？",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            # 设置音频录制
            if self.audio_checkbox.isChecked():
                # 确保音频捕获器可用
                if not self.audio_capture:
                    self.audio_capture = AudioCapture()
                    self.screen_recorder.audio_capture = self.audio_capture
            else:
                # 禁用音频录制
                self.screen_recorder.audio_capture = None

            # 开始录制
            success = self.screen_recorder.start_recording(output_path, fps, quality, format_type)
            if not success:
                QMessageBox.warning(self, "错误", "无法开始录制，请检查设备和权限")

        except ValueError as e:
            QMessageBox.critical(self, "错误", f"设置参数无效: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"开始录制失败: {str(e)}")

    def pause_recording(self):
        """暂停/恢复录制"""
        if self.is_paused:
            self.screen_recorder.resume_recording()
        else:
            self.screen_recorder.pause_recording()

    def stop_recording(self):
        """停止录制"""
        self.screen_recorder.stop_recording()

    def browse_output_path(self):
        """浏览输出路径"""
        path = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_path)
        if path:
            self.output_path = path
            self.output_path_edit.setText(path)

    def toggle_preview(self):
        """切换预览"""
        if self.screen_capture.is_capturing:
            self.screen_capture.stop_capture()
            self.preview_btn.setText("开启预览")
        else:
            self.screen_capture.start_capture()
            self.preview_btn.setText("关闭预览")

    def on_region_mode_changed(self, mode):
        """录制区域模式改变"""
        if mode == "选择区域":
            self.select_region_btn.setEnabled(True)
        else:
            self.select_region_btn.setEnabled(False)
            # 重置为全屏
            self.screen_capture.set_capture_region(None, None, None, None)

    def select_recording_region(self):
        """选择录制区域"""
        try:
            from ui.region_selector import ScreenAreaSelector

            self.region_selector = ScreenAreaSelector()
            self.region_selector.select_region(self.on_region_selected)

        except ImportError:
            QMessageBox.warning(self, "功能暂不可用", "区域选择功能正在开发中")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动区域选择失败: {str(e)}")

    def on_region_selected(self, *args):
        """区域选择完成"""
        if len(args) == 4:
            # 直接传递的4个参数
            x, y, width, height = args
            self.screen_capture.set_capture_region(x, y, width, height)
            QMessageBox.information(self, "区域选择", f"已选择区域: {width}x{height} at ({x}, {y})")
        elif len(args) == 1 and args[0] is not None:
            # 传递的是元组
            region = args[0]
            if isinstance(region, (tuple, list)) and len(region) == 4:
                x, y, width, height = region
                self.screen_capture.set_capture_region(x, y, width, height)
                QMessageBox.information(self, "区域选择", f"已选择区域: {width}x{height} at ({x}, {y})")
            else:
                # 用户取消选择，回到全屏模式
                self.region_combo.setCurrentText("全屏")
        else:
            # 用户取消选择，回到全屏模式
            self.region_combo.setCurrentText("全屏")

    # 信号处理方法
    def on_recording_started(self):
        """录制开始"""
        self.is_recording = True
        self.is_paused = False
        self.status_indicator.set_status("recording")
        self.status_indicator.setText("录制中")
        self.record_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText("正在录制...")

        # 禁用录制设置控件
        self.set_recording_controls_enabled(False)

    def on_recording_stopped(self):
        """录制停止"""
        self.is_recording = False
        self.is_paused = False
        self.status_indicator.set_status("ready")
        self.status_indicator.setText("就绪")
        self.record_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("录制完成")

        # 重新启用录制设置控件
        self.set_recording_controls_enabled(True)

    def on_recording_paused(self):
        """录制暂停"""
        self.is_paused = True
        self.status_indicator.set_status("paused")
        self.status_indicator.setText("已暂停")
        self.pause_btn.setText("恢复")
        self.status_label.setText("录制已暂停")

    def on_recording_resumed(self):
        """录制恢复"""
        self.is_paused = False
        self.status_indicator.set_status("recording")
        self.status_indicator.setText("录制中")
        self.pause_btn.setText("暂停")
        self.status_label.setText("正在录制...")

    def on_progress_updated(self, frame_count, duration):
        """进度更新"""
        # 更新录制信息
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        self.duration_label.setText(f"时长: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.frames_label.setText(f"帧数: {frame_count}")

    def on_frame_captured(self, frame):
        """帧捕获"""
        # 更新预览（如果启用）
        if hasattr(self, 'preview_widget'):
            # 这里需要将numpy数组转换为QPixmap
            # 由于篇幅限制，简化实现
            pass

    def on_error_occurred(self, error_message):
        """错误处理"""
        QMessageBox.critical(self, "错误", error_message)
