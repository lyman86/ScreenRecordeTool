"""
数值输入区域选择对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QGroupBox, QGridLayout,
                             QComboBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import mss

class RegionInputDialog(QDialog):
    """区域输入对话框"""
    
    # 信号
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择录制区域")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        # 获取屏幕信息
        self.screen_info = self._get_screen_info()
        
        self.init_ui()
        self.apply_styles()
        
        # 设置默认值
        self.load_preset("全屏")
    
    def _get_screen_info(self):
        """获取屏幕信息"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                return {
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor.get('left', 0),
                    'top': monitor.get('top', 0)
                }
        except:
            # 默认值
            return {'width': 1440, 'height': 900, 'left': 0, 'top': 0}
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("录制区域设置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 屏幕信息
        info_label = QLabel(f"屏幕分辨率: {self.screen_info['width']} × {self.screen_info['height']}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 预设选择
        preset_group = QGroupBox("快速选择")
        preset_layout = QHBoxLayout(preset_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "全屏",
            "左半屏",
            "右半屏", 
            "上半屏",
            "下半屏",
            "中心区域",
            "左上角",
            "右上角",
            "左下角",
            "右下角",
            "自定义"
        ])
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(QLabel("预设:"))
        preset_layout.addWidget(self.preset_combo)
        
        layout.addWidget(preset_group)
        
        # 坐标输入
        coords_group = QGroupBox("区域坐标")
        coords_layout = QGridLayout(coords_group)
        
        # X坐标
        coords_layout.addWidget(QLabel("X坐标:"), 0, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, self.screen_info['width'] - 1)
        self.x_spin.setValue(0)
        self.x_spin.valueChanged.connect(self.on_coords_changed)
        coords_layout.addWidget(self.x_spin, 0, 1)
        
        # Y坐标
        coords_layout.addWidget(QLabel("Y坐标:"), 0, 2)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, self.screen_info['height'] - 1)
        self.y_spin.setValue(0)
        self.y_spin.valueChanged.connect(self.on_coords_changed)
        coords_layout.addWidget(self.y_spin, 0, 3)
        
        # 宽度
        coords_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, self.screen_info['width'])
        self.width_spin.setValue(self.screen_info['width'])
        self.width_spin.valueChanged.connect(self.on_coords_changed)
        coords_layout.addWidget(self.width_spin, 1, 1)
        
        # 高度
        coords_layout.addWidget(QLabel("高度:"), 1, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, self.screen_info['height'])
        self.height_spin.setValue(self.screen_info['height'])
        self.height_spin.valueChanged.connect(self.on_coords_changed)
        coords_layout.addWidget(self.height_spin, 1, 3)
        
        layout.addWidget(coords_group)
        
        # 预览信息
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 4px;")
        preview_layout.addWidget(self.preview_label)
        
        # 边界检查
        self.boundary_check = QCheckBox("自动修正超出边界的坐标")
        self.boundary_check.setChecked(True)
        preview_layout.addWidget(self.boundary_check)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept_region)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        # 更新预览
        self.update_preview()
    
    def load_preset(self, preset_name):
        """加载预设"""
        if preset_name == "自定义":
            return
        
        w = self.screen_info['width']
        h = self.screen_info['height']
        
        presets = {
            "全屏": (0, 0, w, h),
            "左半屏": (0, 0, w//2, h),
            "右半屏": (w//2, 0, w//2, h),
            "上半屏": (0, 0, w, h//2),
            "下半屏": (0, h//2, w, h//2),
            "中心区域": (w//4, h//4, w//2, h//2),
            "左上角": (0, 0, w//2, h//2),
            "右上角": (w//2, 0, w//2, h//2),
            "左下角": (0, h//2, w//2, h//2),
            "右下角": (w//2, h//2, w//2, h//2),
        }
        
        if preset_name in presets:
            x, y, width, height = presets[preset_name]
            
            # 阻止信号触发，避免循环
            self.x_spin.blockSignals(True)
            self.y_spin.blockSignals(True)
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            
            # 恢复信号
            self.x_spin.blockSignals(False)
            self.y_spin.blockSignals(False)
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
            
            self.update_preview()
    
    def on_coords_changed(self):
        """坐标改变时"""
        # 设置为自定义
        if self.preset_combo.currentText() != "自定义":
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentText("自定义")
            self.preset_combo.blockSignals(False)
        
        # 边界检查
        if self.boundary_check.isChecked():
            self.fix_boundaries()
        
        self.update_preview()
    
    def fix_boundaries(self):
        """修正边界"""
        x = self.x_spin.value()
        y = self.y_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # 修正坐标
        max_x = self.screen_info['width'] - width
        max_y = self.screen_info['height'] - height
        
        if x > max_x:
            self.x_spin.setValue(max(0, max_x))
        if y > max_y:
            self.y_spin.setValue(max(0, max_y))
        
        # 修正尺寸
        if x + width > self.screen_info['width']:
            self.width_spin.setValue(self.screen_info['width'] - x)
        if y + height > self.screen_info['height']:
            self.height_spin.setValue(self.screen_info['height'] - y)
    
    def update_preview(self):
        """更新预览"""
        x = self.x_spin.value()
        y = self.y_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # 检查是否超出边界
        out_of_bounds = (
            x + width > self.screen_info['width'] or
            y + height > self.screen_info['height']
        )
        
        # 计算覆盖比例
        total_pixels = self.screen_info['width'] * self.screen_info['height']
        region_pixels = width * height
        coverage = (region_pixels / total_pixels) * 100
        
        preview_text = f"""
录制区域: {x}, {y}, {width} × {height}
右下角坐标: ({x + width}, {y + height})
屏幕覆盖率: {coverage:.1f}%
        """.strip()
        
        if out_of_bounds:
            preview_text += "\n⚠️ 区域超出屏幕边界"
            self.preview_label.setStyleSheet("background-color: #ffe6e6; color: #d63031; padding: 10px; border-radius: 4px;")
        else:
            preview_text += "\n✅ 区域有效"
            self.preview_label.setStyleSheet("background-color: #e6ffe6; color: #00b894; padding: 10px; border-radius: 4px;")
        
        self.preview_label.setText(preview_text)
    
    def accept_region(self):
        """确认选择"""
        x = self.x_spin.value()
        y = self.y_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # 最终边界检查
        if (x + width > self.screen_info['width'] or
            y + height > self.screen_info['height']):
            reply = QMessageBox.question(
                self,
                "区域超出边界",
                "选择的区域超出屏幕边界，是否自动修正？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.fix_boundaries()
                x = self.x_spin.value()
                y = self.y_spin.value()
                width = self.width_spin.value()
                height = self.height_spin.value()
            else:
                return
        
        # 发送信号
        self.region_selected.emit(x, y, width, height)
        self.accept()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f5f5f5;
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
            }
            QPushButton#cancel_btn:hover {
                background-color: #616161;
            }
            QSpinBox {
                padding: 4px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QComboBox {
                padding: 4px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        self.cancel_btn.setObjectName("cancel_btn")
