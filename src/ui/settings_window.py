"""
设置窗口UI
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit,
    QPushButton, QSlider, QGridLayout, QFormLayout, QMessageBox,
    QFileDialog, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# 导入配置和工具
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import AppConfig, UIConfig
from utils.hotkey_manager import DefaultHotkeys, is_valid_hotkey

class SettingsWindow(QDialog):
    """设置窗口"""
    
    settings_changed = pyqtSignal(dict)  # 设置更改信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 500)
        
        # 当前设置
        self.current_settings = self.load_default_settings()
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 录制设置标签页
        self.recording_tab = self.create_recording_tab()
        self.tab_widget.addTab(self.recording_tab, "录制设置")
        
        # 快捷键设置标签页
        self.hotkey_tab = self.create_hotkey_tab()
        self.tab_widget.addTab(self.hotkey_tab, "快捷键")
        
        # 高级设置标签页
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "高级设置")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = QPushButton("重置默认")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn = QPushButton("确定")
        
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept_settings)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def create_recording_tab(self):
        """创建录制设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 视频设置组
        video_group = QGroupBox("视频设置")
        video_layout = QFormLayout(video_group)
        
        # 默认帧率
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([str(fps) for fps in AppConfig.FPS_OPTIONS])
        video_layout.addRow("默认帧率:", self.fps_combo)
        
        # 默认质量
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(list(AppConfig.QUALITY_SETTINGS.keys()))
        video_layout.addRow("默认质量:", self.quality_combo)
        
        # 默认格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(AppConfig.SUPPORTED_FORMATS)
        video_layout.addRow("默认格式:", self.format_combo)
        
        layout.addWidget(video_group)
        
        # 音频设置组
        audio_group = QGroupBox("音频设置")
        audio_layout = QFormLayout(audio_group)
        
        # 默认启用音频
        self.audio_enabled_cb = QCheckBox("默认录制音频")
        audio_layout.addRow(self.audio_enabled_cb)
        
        # 音频质量
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["低质量", "中等质量", "高质量", "无损"])
        audio_layout.addRow("音频质量:", self.audio_quality_combo)
        
        layout.addWidget(audio_group)
        
        # 其他设置组
        other_group = QGroupBox("其他设置")
        other_layout = QFormLayout(other_group)
        
        # 显示鼠标指针
        self.cursor_enabled_cb = QCheckBox("默认显示鼠标指针")
        other_layout.addRow(self.cursor_enabled_cb)
        
        # 自动保存
        self.auto_save_cb = QCheckBox("录制完成后自动保存")
        other_layout.addRow(self.auto_save_cb)
        
        # 最小化到系统托盘
        self.minimize_to_tray_cb = QCheckBox("最小化到系统托盘")
        other_layout.addRow(self.minimize_to_tray_cb)
        
        layout.addWidget(other_group)
        
        layout.addStretch()
        return widget
    
    def create_hotkey_tab(self):
        """创建快捷键设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明文本
        info_label = QLabel("点击快捷键输入框，然后按下想要设置的快捷键组合")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # 快捷键设置组
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QFormLayout(hotkey_group)
        
        # 快捷键输入框
        self.hotkey_inputs = {}
        hotkey_descriptions = DefaultHotkeys.get_descriptions()
        
        for key, description in hotkey_descriptions.items():
            hotkey_input = QLineEdit()
            hotkey_input.setPlaceholderText("点击后按下快捷键...")
            hotkey_input.setReadOnly(True)
            hotkey_input.mousePressEvent = lambda event, k=key: self.start_hotkey_capture(k)
            
            clear_btn = QPushButton("清除")
            clear_btn.setMaximumWidth(60)
            clear_btn.clicked.connect(lambda checked, k=key: self.clear_hotkey(k))
            
            hotkey_container = QHBoxLayout()
            hotkey_container.addWidget(hotkey_input)
            hotkey_container.addWidget(clear_btn)
            
            container_widget = QWidget()
            container_widget.setLayout(hotkey_container)
            
            self.hotkey_inputs[key] = hotkey_input
            hotkey_layout.addRow(f"{description}:", container_widget)
        
        layout.addWidget(hotkey_group)
        
        # 全局快捷键启用
        self.global_hotkeys_cb = QCheckBox("启用全局快捷键")
        layout.addWidget(self.global_hotkeys_cb)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能设置组
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout(performance_group)
        
        # 硬件加速
        self.hardware_accel_cb = QCheckBox("启用硬件加速")
        performance_layout.addRow(self.hardware_accel_cb)
        
        # 多线程编码
        self.multithread_cb = QCheckBox("启用多线程编码")
        performance_layout.addRow(self.multithread_cb)
        
        # 缓冲区大小
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1, 100)
        self.buffer_size_spin.setSuffix(" MB")
        performance_layout.addRow("缓冲区大小:", self.buffer_size_spin)
        
        layout.addWidget(performance_group)
        
        # 文件设置组
        file_group = QGroupBox("文件设置")
        file_layout = QFormLayout(file_group)
        
        # 默认输出目录
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.browse_output_btn = QPushButton("浏览")
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_output_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        file_layout.addRow("默认输出目录:", output_widget)
        
        # 文件命名模板
        self.filename_template_edit = QLineEdit()
        self.filename_template_edit.setPlaceholderText("录屏_{timestamp}")
        file_layout.addRow("文件命名模板:", self.filename_template_edit)
        
        layout.addWidget(file_group)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout(ui_group)
        
        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "跟随系统"])
        ui_layout.addRow("主题:", self.theme_combo)
        
        # 语言
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        ui_layout.addRow("语言:", self.language_combo)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        return widget
    
    def load_default_settings(self):
        """加载默认设置"""
        return {
            # 录制设置
            "fps": AppConfig.DEFAULT_FPS,
            "quality": AppConfig.DEFAULT_QUALITY,
            "format": AppConfig.DEFAULT_FORMAT,
            "audio_enabled": AppConfig.DEFAULT_AUDIO_ENABLED,
            "cursor_enabled": AppConfig.DEFAULT_CURSOR_ENABLED,
            "audio_quality": "高质量",
            "auto_save": True,
            "minimize_to_tray": True,
            
            # 快捷键设置
            "hotkeys": DefaultHotkeys.get_all_hotkeys(),
            "global_hotkeys_enabled": True,
            
            # 高级设置
            "hardware_accel": True,
            "multithread": True,
            "buffer_size": 10,
            "output_path": AppConfig.get_default_output_dir(),
            "filename_template": "录屏_{timestamp}",
            "theme": "浅色主题",
            "language": "简体中文"
        }
    
    def load_settings(self):
        """加载设置到UI"""
        settings = self.current_settings
        
        # 录制设置
        self.fps_combo.setCurrentText(str(settings["fps"]))
        self.quality_combo.setCurrentText(settings["quality"])
        self.format_combo.setCurrentText(settings["format"])
        self.audio_enabled_cb.setChecked(settings["audio_enabled"])
        self.cursor_enabled_cb.setChecked(settings["cursor_enabled"])
        self.audio_quality_combo.setCurrentText(settings["audio_quality"])
        self.auto_save_cb.setChecked(settings["auto_save"])
        self.minimize_to_tray_cb.setChecked(settings["minimize_to_tray"])
        
        # 快捷键设置
        for key, hotkey in settings["hotkeys"].items():
            if key in self.hotkey_inputs:
                self.hotkey_inputs[key].setText(hotkey)
        self.global_hotkeys_cb.setChecked(settings["global_hotkeys_enabled"])
        
        # 高级设置
        self.hardware_accel_cb.setChecked(settings["hardware_accel"])
        self.multithread_cb.setChecked(settings["multithread"])
        self.buffer_size_spin.setValue(settings["buffer_size"])
        self.output_path_edit.setText(settings["output_path"])
        self.filename_template_edit.setText(settings["filename_template"])
        self.theme_combo.setCurrentText(settings["theme"])
        self.language_combo.setCurrentText(settings["language"])
    
    def start_hotkey_capture(self, key):
        """开始捕获快捷键"""
        # 这里应该实现快捷键捕获逻辑
        # 由于篇幅限制，简化实现
        pass
    
    def clear_hotkey(self, key):
        """清除快捷键"""
        if key in self.hotkey_inputs:
            self.hotkey_inputs[key].clear()
    
    def browse_output_directory(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择输出目录", self.output_path_edit.text()
        )
        if directory:
            self.output_path_edit.setText(directory)
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self.load_default_settings()
            self.load_settings()
    
    def accept_settings(self):
        """接受设置"""
        # 收集所有设置
        settings = {
            # 录制设置
            "fps": int(self.fps_combo.currentText()),
            "quality": self.quality_combo.currentText(),
            "format": self.format_combo.currentText(),
            "audio_enabled": self.audio_enabled_cb.isChecked(),
            "cursor_enabled": self.cursor_enabled_cb.isChecked(),
            "audio_quality": self.audio_quality_combo.currentText(),
            "auto_save": self.auto_save_cb.isChecked(),
            "minimize_to_tray": self.minimize_to_tray_cb.isChecked(),
            
            # 快捷键设置
            "hotkeys": {key: input_widget.text() for key, input_widget in self.hotkey_inputs.items()},
            "global_hotkeys_enabled": self.global_hotkeys_cb.isChecked(),
            
            # 高级设置
            "hardware_accel": self.hardware_accel_cb.isChecked(),
            "multithread": self.multithread_cb.isChecked(),
            "buffer_size": self.buffer_size_spin.value(),
            "output_path": self.output_path_edit.text(),
            "filename_template": self.filename_template_edit.text(),
            "theme": self.theme_combo.currentText(),
            "language": self.language_combo.currentText()
        }
        
        self.settings_changed.emit(settings)
        self.accept()
