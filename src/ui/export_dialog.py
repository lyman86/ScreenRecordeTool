"""
导出对话框UI
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit,
    QPushButton, QSlider, QProgressBar, QTextEdit, QTabWidget,
    QWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

class ExportWorker(QThread):
    """导出工作线程"""
    
    progress_updated = pyqtSignal(int)
    export_finished = pyqtSignal(str)
    export_failed = pyqtSignal(str)
    
    def __init__(self, processor, input_path, output_path, export_settings):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
        self.export_settings = export_settings
    
    def run(self):
        """执行导出"""
        try:
            export_type = self.export_settings.get("type", "convert")
            
            if export_type == "convert":
                success = self.processor.convert_video(
                    self.input_path,
                    self.output_path,
                    self.export_settings.get("format", "mp4"),
                    self.export_settings.get("quality", "高质量"),
                    self.export_settings.get("custom_options", {})
                )
            elif export_type == "compress":
                success = self.processor.compress_video(
                    self.input_path,
                    self.output_path,
                    self.export_settings.get("target_size"),
                    self.export_settings.get("compression_level", "medium")
                )
            elif export_type == "extract_audio":
                success = self.processor.extract_audio(
                    self.input_path,
                    self.output_path,
                    self.export_settings.get("audio_format", "mp3")
                )
            elif export_type == "trim":
                success = self.processor.trim_video(
                    self.input_path,
                    self.output_path,
                    self.export_settings.get("start_time", "00:00:00"),
                    self.export_settings.get("duration", "00:01:00")
                )
            else:
                success = False
            
            if success:
                self.export_finished.emit(self.output_path)
            else:
                self.export_failed.emit("导出失败")
                
        except Exception as e:
            self.export_failed.emit(str(e))

class ExportDialog(QDialog):
    """导出对话框"""
    
    export_requested = pyqtSignal(str, str, dict)  # input_path, output_path, settings
    
    def __init__(self, input_path: str, video_processor, parent=None):
        super().__init__(parent)
        self.input_path = input_path
        self.video_processor = video_processor
        self.export_worker = None
        
        self.setWindowTitle("导出视频")
        self.setModal(True)
        self.resize(500, 600)
        
        # 获取视频信息
        self.video_info = video_processor.get_video_info(input_path) if video_processor else {}
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 文件信息
        info_group = self.create_info_group()
        layout.addWidget(info_group)
        
        # 导出选项标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 格式转换标签页
        self.convert_tab = self.create_convert_tab()
        self.tab_widget.addTab(self.convert_tab, "格式转换")
        
        # 压缩标签页
        self.compress_tab = self.create_compress_tab()
        self.tab_widget.addTab(self.compress_tab, "视频压缩")
        
        # 音频提取标签页
        self.audio_tab = self.create_audio_tab()
        self.tab_widget.addTab(self.audio_tab, "音频提取")
        
        # 视频裁剪标签页
        self.trim_tab = self.create_trim_tab()
        self.tab_widget.addTab(self.trim_tab, "视频裁剪")
        
        # 输出设置
        output_group = self.create_output_group()
        layout.addWidget(output_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.export_btn = QPushButton("开始导出")
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
    
    def create_info_group(self):
        """创建文件信息组"""
        group = QGroupBox("文件信息")
        layout = QFormLayout(group)
        
        # 文件路径
        filename = os.path.basename(self.input_path)
        layout.addRow("文件名:", QLabel(filename))
        
        # 视频信息
        if self.video_info:
            if "duration" in self.video_info:
                duration = self.video_info["duration"]
                duration_str = f"{int(duration//3600):02d}:{int((duration%3600)//60):02d}:{int(duration%60):02d}"
                layout.addRow("时长:", QLabel(duration_str))
            
            if "resolution" in self.video_info:
                layout.addRow("分辨率:", QLabel(self.video_info["resolution"]))
            
            if "fps" in self.video_info:
                layout.addRow("帧率:", QLabel(f"{self.video_info['fps']:.1f} fps"))
        
        return group
    
    def create_convert_tab(self):
        """创建格式转换标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 输出格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "WebM", "MKV"])
        layout.addRow("输出格式:", self.format_combo)
        
        # 视频质量
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["低质量", "中等质量", "高质量", "超高质量"])
        self.quality_combo.setCurrentText("高质量")
        layout.addRow("视频质量:", self.quality_combo)
        
        # 视频编解码器
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["自动", "H.264", "H.265", "VP9"])
        layout.addRow("视频编解码器:", self.video_codec_combo)
        
        # 音频编解码器
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["自动", "AAC", "MP3", "Opus"])
        layout.addRow("音频编解码器:", self.audio_codec_combo)
        
        # 比特率
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(500, 50000)
        self.bitrate_spin.setValue(2000)
        self.bitrate_spin.setSuffix(" kbps")
        layout.addRow("视频比特率:", self.bitrate_spin)
        
        return widget
    
    def create_compress_tab(self):
        """创建压缩标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 压缩模式
        self.compress_mode_combo = QComboBox()
        self.compress_mode_combo.addItems(["质量优先", "大小优先"])
        layout.addRow("压缩模式:", self.compress_mode_combo)
        
        # 压缩级别
        self.compress_level_combo = QComboBox()
        self.compress_level_combo.addItems(["低", "中", "高"])
        self.compress_level_combo.setCurrentText("中")
        layout.addRow("压缩级别:", self.compress_level_combo)
        
        # 目标文件大小
        self.target_size_spin = QSpinBox()
        self.target_size_spin.setRange(1, 10000)
        self.target_size_spin.setValue(100)
        self.target_size_spin.setSuffix(" MB")
        layout.addRow("目标大小:", self.target_size_spin)
        
        # 启用目标大小
        self.use_target_size_cb = QCheckBox("使用目标文件大小")
        layout.addRow(self.use_target_size_cb)
        
        return widget
    
    def create_audio_tab(self):
        """创建音频提取标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 音频格式
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["MP3", "AAC", "OGG", "WAV"])
        layout.addRow("音频格式:", self.audio_format_combo)
        
        # 音频质量
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
        self.audio_quality_combo.setCurrentText("192 kbps")
        layout.addRow("音频质量:", self.audio_quality_combo)
        
        # 采样率
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["22050 Hz", "44100 Hz", "48000 Hz"])
        self.sample_rate_combo.setCurrentText("44100 Hz")
        layout.addRow("采样率:", self.sample_rate_combo)
        
        return widget
    
    def create_trim_tab(self):
        """创建裁剪标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 开始时间
        self.start_time_edit = QLineEdit("00:00:00")
        self.start_time_edit.setPlaceholderText("HH:MM:SS")
        layout.addRow("开始时间:", self.start_time_edit)
        
        # 结束时间
        self.end_time_edit = QLineEdit("00:01:00")
        self.end_time_edit.setPlaceholderText("HH:MM:SS")
        layout.addRow("结束时间:", self.end_time_edit)
        
        # 或者使用持续时间
        self.duration_edit = QLineEdit("00:01:00")
        self.duration_edit.setPlaceholderText("HH:MM:SS")
        layout.addRow("持续时间:", self.duration_edit)
        
        # 使用持续时间模式
        self.use_duration_cb = QCheckBox("使用持续时间而非结束时间")
        layout.addRow(self.use_duration_cb)
        
        return widget
    
    def create_output_group(self):
        """创建输出设置组"""
        group = QGroupBox("输出设置")
        layout = QFormLayout(group)
        
        # 输出路径
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.browse_output_btn = QPushButton("浏览")
        
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_output_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        layout.addRow("输出路径:", output_widget)
        
        # 覆盖现有文件
        self.overwrite_cb = QCheckBox("覆盖现有文件")
        layout.addRow(self.overwrite_cb)
        
        return group
    
    def connect_signals(self):
        """连接信号"""
        self.cancel_btn.clicked.connect(self.reject)
        self.export_btn.clicked.connect(self.start_export)
        self.browse_output_btn.clicked.connect(self.browse_output_path)
        
        # 标签页切换时更新输出路径
        self.tab_widget.currentChanged.connect(self.update_output_path)
        
        # 格式改变时更新输出路径
        self.format_combo.currentTextChanged.connect(self.update_output_path)
        self.audio_format_combo.currentTextChanged.connect(self.update_output_path)
    
    def update_output_path(self):
        """更新输出路径"""
        if not self.output_path_edit.text():
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # 格式转换
                ext = self.format_combo.currentText().lower()
                output_name = f"{base_name}_converted.{ext}"
            elif current_tab == 1:  # 压缩
                output_name = f"{base_name}_compressed.mp4"
            elif current_tab == 2:  # 音频提取
                ext = self.audio_format_combo.currentText().lower()
                output_name = f"{base_name}_audio.{ext}"
            elif current_tab == 3:  # 裁剪
                output_name = f"{base_name}_trimmed.mp4"
            else:
                output_name = f"{base_name}_processed.mp4"
            
            output_dir = os.path.dirname(self.input_path)
            output_path = os.path.join(output_dir, output_name)
            self.output_path_edit.setText(output_path)
    
    def browse_output_path(self):
        """浏览输出路径"""
        current_path = self.output_path_edit.text()
        if not current_path:
            current_path = os.path.dirname(self.input_path)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择输出文件", current_path
        )
        
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def get_export_settings(self) -> dict:
        """获取导出设置"""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # 格式转换
            return {
                "type": "convert",
                "format": self.format_combo.currentText().lower(),
                "quality": self.quality_combo.currentText(),
                "custom_options": {
                    "b:v": f"{self.bitrate_spin.value()}k"
                }
            }
        elif current_tab == 1:  # 压缩
            settings = {
                "type": "compress",
                "compression_level": {"低": "low", "中": "medium", "高": "high"}[self.compress_level_combo.currentText()]
            }
            if self.use_target_size_cb.isChecked():
                settings["target_size"] = self.target_size_spin.value()
            return settings
        elif current_tab == 2:  # 音频提取
            return {
                "type": "extract_audio",
                "audio_format": self.audio_format_combo.currentText().lower()
            }
        elif current_tab == 3:  # 裁剪
            return {
                "type": "trim",
                "start_time": self.start_time_edit.text(),
                "duration": self.duration_edit.text() if self.use_duration_cb.isChecked() else None,
                "end_time": self.end_time_edit.text() if not self.use_duration_cb.isChecked() else None
            }
        
        return {}
    
    def start_export(self):
        """开始导出"""
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出路径")
            return
        
        # 检查文件是否存在
        if os.path.exists(output_path) and not self.overwrite_cb.isChecked():
            reply = QMessageBox.question(
                self, "文件已存在", 
                f"文件 {os.path.basename(output_path)} 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 获取导出设置
        settings = self.get_export_settings()
        
        # 开始导出
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # 创建工作线程
        self.export_worker = ExportWorker(
            self.video_processor, self.input_path, output_path, settings
        )
        self.export_worker.export_finished.connect(self.on_export_finished)
        self.export_worker.export_failed.connect(self.on_export_failed)
        self.export_worker.start()
    
    def on_export_finished(self, output_path):
        """导出完成"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "导出完成", f"文件已保存到:\n{output_path}")
        self.accept()
    
    def on_export_failed(self, error_message):
        """导出失败"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "导出失败", f"导出失败:\n{error_message}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self, "确认关闭", "导出正在进行中，确定要关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.export_worker.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
