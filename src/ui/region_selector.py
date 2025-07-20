# macOS区域选择修复
# macOS兼容性修复
"""
区域选择器UI
"""

import sys
import platform
from PyQt6.QtWidgets import QWidget, QApplication, QRubberBand, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

class RegionSelectorWindow(QWidget):
    """区域选择窗口"""
    
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    selection_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # macOS特殊处理
        import platform
        if platform.system() == "Darwin":
            self._setup_macos_window()
        else:
            self._setup_default_window()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 选择状态
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        
        # 橡皮筋选择框
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        # 提示标签
        self.hint_label = QLabel("拖拽鼠标选择录制区域，按ESC取消", self)
        self.hint_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        self.hint_label.adjustSize()
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)

        # 获取DPI缩放信息
        self.device_pixel_ratio = self.devicePixelRatio()
        print(f"区域选择器DPI缩放比例: {self.device_pixel_ratio}")
        
        # 获取屏幕尺寸并居中提示
        screen = QApplication.primaryScreen().geometry()
        self.hint_label.move(
            (screen.width() - self.hint_label.width()) // 2,
            50
        )

    def _setup_macos_window(self):
        """设置macOS窗口属性"""
        # macOS需要特殊的窗口标志组合
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint
        )

        # 设置窗口透明度，但不完全透明
        self.setWindowOpacity(0.3)

        # 获取屏幕几何并设置窗口大小
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()

        # 确保窗口覆盖整个逻辑屏幕
        self.setGeometry(0, 0, geometry.width(), geometry.height())

        print(f"macOS窗口设置: 逻辑屏幕{geometry.width()}x{geometry.height()}, DPR: {screen.devicePixelRatio()}")

    def _setup_default_window(self):
        """设置默认窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
    
    def paintEvent(self, event):
        """绘制半透明遮罩"""
        painter = QPainter(self)

        import platform
        if platform.system() == "Darwin":
            # macOS特殊绘制逻辑
            self._paint_macos(painter)
        else:
            # 默认绘制逻辑
            self._paint_default(painter)

    def _paint_macos(self, painter):
        """macOS特殊绘制方法"""
        # 在macOS上，使用更轻的遮罩，让桌面内容可见
        painter.fillRect(self.rect(), QColor(0, 0, 0, 50))  # 更透明的遮罩

        # 如果有选择区域，绘制高亮边框
        if not self.selection_rect.isEmpty():
            # 绘制选择区域的高亮边框
            pen = QPen(QColor(0, 120, 215), 3)  # 更粗的边框
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)

            # 绘制选择区域内部的半透明高亮
            painter.fillRect(self.selection_rect, QColor(0, 120, 215, 30))

            # 绘制尺寸信息
            self._draw_size_info(painter)

    def _paint_default(self, painter):
        """默认绘制方法"""
        # 绘制半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # 如果有选择区域，绘制透明的选择区域
        if not self.selection_rect.isEmpty():
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.selection_rect, QColor(0, 0, 0, 0))

            # 绘制选择框边框
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)

            # 绘制尺寸信息
            self._draw_size_info(painter)

    def _draw_size_info(self, painter):
        """绘制尺寸信息"""
        if self.selection_rect.width() > 50 and self.selection_rect.height() > 30:
            size_text = f"{self.selection_rect.width()} × {self.selection_rect.height()}"
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", 12))

            # 计算文本位置
            text_rect = painter.fontMetrics().boundingRect(size_text)
            text_x = self.selection_rect.x() + 5
            text_y = self.selection_rect.y() - 5

            # 确保文本在屏幕内
            if text_y < text_rect.height():
                text_y = self.selection_rect.y() + text_rect.height() + 5

            painter.drawText(text_x, text_y, size_text)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selecting = True
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.selection_rect = QRect(self.start_point, self.end_point)
            self.rubber_band.setGeometry(self.selection_rect)
            self.rubber_band.show()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.selecting:
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.rubber_band.setGeometry(self.selection_rect)
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            self.rubber_band.hide()

            # 检查选择区域是否有效
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                # 转换坐标到物理像素
                physical_rect = self._convert_to_physical_coordinates(self.selection_rect)

                self.region_selected.emit(
                    physical_rect.x(),
                    physical_rect.y(),
                    physical_rect.width(),
                    physical_rect.height()
                )
            else:
                self.selection_cancelled.emit()
            
            self.close()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
        super().keyPressEvent(event)


    def showEvent(self, event):
        """显示事件 - 优化的macOS处理"""
        super().showEvent(event)

        import platform
        if platform.system() == "Darwin":
            self._setup_macos_display()
        else:
            self._setup_default_display()

    def _setup_macos_display(self):
        """macOS显示设置 - 解决黑屏问题"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer

            # 获取屏幕信息
            screen = QApplication.primaryScreen()
            geometry = screen.geometry()

            print(f"macOS屏幕设置: {geometry.width()}x{geometry.height()}")

            # 确保窗口覆盖整个屏幕
            self.setGeometry(geometry)

            # 设置窗口属性以确保能看到桌面
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setWindowOpacity(0.8)  # 设置适当的透明度

            # 强制窗口到最前面
            self.raise_()
            self.activateWindow()

            # 设置提示标签位置
            if hasattr(self, 'hint_label'):
                self.hint_label.move(
                    (geometry.width() - self.hint_label.width()) // 2,
                    50
                )
                # 确保提示标签可见
                self.hint_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(0, 0, 0, 200);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)

            print("✅ macOS区域选择器显示设置完成")

        except Exception as e:
            print(f"❌ macOS显示设置失败: {e}")

    def _setup_default_display(self):
        """默认显示设置"""
        # 获取物理屏幕尺寸（MSS使用的坐标系）
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            physical_width = monitor['width']
            physical_height = monitor['height']

        # 转换为逻辑坐标
        logical_width = int(physical_width / self.device_pixel_ratio)
        logical_height = int(physical_height / self.device_pixel_ratio)

        print(f"屏幕尺寸: 物理({physical_width}x{physical_height}) -> 逻辑({logical_width}x{logical_height})")

        # 设置窗口几何
        self.setGeometry(0, 0, logical_width, logical_height)

        # 确保窗口获得焦点
        self.activateWindow()
        self.raise_()

        # 将提示标签放在屏幕中央上方
        if hasattr(self, 'hint_label'):
            screen_center = self.rect().center()
            label_x = screen_center.x() - self.hint_label.width() // 2
            label_y = 50  # 距离顶部50像素
            self.hint_label.move(label_x, label_y)
    
    def _convert_to_physical_coordinates(self, logical_rect):
        """将逻辑坐标转换为物理坐标 - macOS优化"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QRect
            import mss

            screen = QApplication.primaryScreen()
            logical_geometry = screen.geometry()
            device_pixel_ratio = screen.devicePixelRatio()

            if platform.system() == "Darwin":
                # 获取MSS的实际屏幕尺寸
                with mss.mss() as sct:
                    mss_monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    mss_width = mss_monitor['width']
                    mss_height = mss_monitor['height']

                print(f"屏幕信息: Qt逻辑({logical_geometry.width()}x{logical_geometry.height()}) MSS物理({mss_width}x{mss_height}) DPR({device_pixel_ratio})")

                # 计算实际的缩放比例
                actual_scale_x = mss_width / logical_geometry.width()
                actual_scale_y = mss_height / logical_geometry.height()

                # 使用实际的缩放比例
                physical_x = int(logical_rect.x() * actual_scale_x)
                physical_y = int(logical_rect.y() * actual_scale_y)
                physical_width = int(logical_rect.width() * actual_scale_x)
                physical_height = int(logical_rect.height() * actual_scale_y)

                print(f"macOS坐标转换: 逻辑({logical_rect.x()}, {logical_rect.y()}, {logical_rect.width()}, {logical_rect.height()}) -> 物理({physical_x}, {physical_y}, {physical_width}, {physical_height})")
                print(f"实际缩放比例: X={actual_scale_x:.2f}, Y={actual_scale_y:.2f}")

                return QRect(physical_x, physical_y, physical_width, physical_height)
            else:
                # 其他系统使用设备像素比
                scale = device_pixel_ratio
                physical_x = int(logical_rect.x() * scale)
                physical_y = int(logical_rect.y() * scale)
                physical_width = int(logical_rect.width() * scale)
                physical_height = int(logical_rect.height() * scale)

                return QRect(physical_x, physical_y, physical_width, physical_height)

        except Exception as e:
            print(f"坐标转换错误: {e}")
            from PyQt6.QtCore import QRect
            # 出错时使用原始坐标
            return QRect(logical_rect.x(), logical_rect.y(), logical_rect.width(), logical_rect.height())
    def _setup_macos_display(self):
        """macOS显示设置"""
        # 强制窗口到前台
        self.raise_()
        self.activateWindow()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint  # macOS特殊标志
        )
        
        # 重新显示
        self.show()
        self._setup_display()
    
    def _setup_display(self):
        """设置显示参数"""
        # 获取物理屏幕尺寸（MSS使用的坐标系）
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            physical_width = monitor['width']
            physical_height = monitor['height']

        # 转换为逻辑坐标
        logical_width = int(physical_width / self.device_pixel_ratio)
        logical_height = int(physical_height / self.device_pixel_ratio)

        print(f"屏幕尺寸: 物理({physical_width}x{physical_height}) -> 逻辑({logical_width}x{logical_height})")

        # 设置窗口几何
        self.setGeometry(0, 0, logical_width, logical_height)

        # 将提示标签放在屏幕中央上方
        if hasattr(self, 'hint_label'):
            screen_center = self.rect().center()
            label_x = screen_center.x() - self.hint_label.width() // 2
            label_y = 50  # 距离顶部50像素
            self.hint_label.move(label_x, label_y)
class ScreenAreaSelector:
    """屏幕区域选择器"""
    
    def __init__(self):
        self.selector_window = None
        self.selected_region = None
    
    def select_region(self, callback=None):
        """选择屏幕区域"""
        if self.selector_window:
            self.selector_window.close()
        
        self.selector_window = RegionSelectorWindow()
        
        if callback:
            self.selector_window.region_selected.connect(callback)
            self.selector_window.selection_cancelled.connect(lambda: callback(None))
        
        self.selector_window.region_selected.connect(self._on_region_selected)
        self.selector_window.selection_cancelled.connect(self._on_selection_cancelled)
        
        self.selector_window.show()
        return self.selector_window
    
    def _on_region_selected(self, x, y, width, height):
        """区域选择完成"""
        self.selected_region = (x, y, width, height)
    
    def _on_selection_cancelled(self):
        """选择取消"""
        self.selected_region = None
    
    def get_selected_region(self):
        """获取选择的区域"""
        return self.selected_region
