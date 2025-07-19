#!/usr/bin/env python3
"""
现代录屏工具 - 主程序入口
"""

import sys
import os
import platform
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
except ImportError as e:
    print(f"错误：缺少必要的依赖库 {e}")
    print("请运行：pip install -r requirements.txt")
    sys.exit(1)

from config.settings import AppConfig
from ui.main_window import MainWindow

def check_system_requirements():
    """检查系统要求"""
    errors = []
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        errors.append("需要Python 3.8或更高版本")
    
    # 检查操作系统
    if platform.system() not in ["Windows", "Darwin"]:
        errors.append("仅支持Windows和macOS")
    
    return errors

def setup_application():
    """设置应用程序"""
    # 设置应用程序属性
    QApplication.setApplicationName(AppConfig.APP_NAME)
    QApplication.setApplicationVersion(AppConfig.APP_VERSION)
    QApplication.setOrganizationName(AppConfig.APP_AUTHOR)
    
    # 设置高DPI支持 (PyQt6 兼容)
    try:
        # PyQt6 中这些属性可能不存在或已被弃用
        if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # PyQt6 默认启用高DPI支持，无需手动设置
        pass
    
    # 确保必要的目录存在
    AppConfig.ensure_directories()

def main():
    """主函数"""
    # 检查系统要求
    errors = check_system_requirements()
    if errors:
        print("系统要求检查失败：")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序
    setup_application()
    
    try:
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        # 显示错误对话框
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("应用程序错误")
        error_dialog.setText(f"应用程序启动失败：\n{str(e)}")
        error_dialog.exec()
        sys.exit(1)

if __name__ == "__main__":
    main()
