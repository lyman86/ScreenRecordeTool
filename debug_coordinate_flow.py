#!/usr/bin/env python3
"""
调试坐标传递流程
"""

import sys
import platform
from pathlib import Path

# 添加src路径
sys.path.append(str(Path(__file__).parent / "src"))

def test_coordinate_flow():
    """测试完整的坐标传递流程"""
    print("🔍 调试坐标传递流程...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QRect
        from ui.region_selector import RegionSelectorWindow, ScreenAreaSelector
        from core.screen_capture import ScreenCapture
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 1. 获取屏幕信息
        screen = app.primaryScreen()
        logical_geometry = screen.geometry()
        device_pixel_ratio = screen.devicePixelRatio()
        
        print(f"📱 屏幕信息:")
        print(f"   逻辑几何: {logical_geometry.width()}x{logical_geometry.height()}")
        print(f"   设备像素比: {device_pixel_ratio}")
        print(f"   计算的物理分辨率: {int(logical_geometry.width() * device_pixel_ratio)}x{int(logical_geometry.height() * device_pixel_ratio)}")
        
        # 2. 测试区域选择器窗口
        print(f"\n🪟 测试RegionSelectorWindow:")
        region_window = RegionSelectorWindow()
        
        # 模拟用户选择一个区域（逻辑坐标）
        test_logical_rect = QRect(200, 150, 400, 300)
        print(f"   模拟选择逻辑区域: ({test_logical_rect.x()}, {test_logical_rect.y()}, {test_logical_rect.width()}, {test_logical_rect.height()})")
        
        # 3. 测试坐标转换
        physical_rect = region_window._convert_to_physical_coordinates(test_logical_rect)
        print(f"   转换后物理坐标: ({physical_rect.x()}, {physical_rect.y()}, {physical_rect.width()}, {physical_rect.height()})")
        
        # 4. 测试屏幕捕获模块
        print(f"\n📹 测试ScreenCapture:")
        screen_capture = ScreenCapture()
        
        # 设置捕获区域（使用物理坐标）
        screen_capture.set_capture_region(
            physical_rect.x(), 
            physical_rect.y(), 
            physical_rect.width(), 
            physical_rect.height()
        )
        
        # 获取设置后的屏幕尺寸
        capture_size = screen_capture.get_screen_size()
        print(f"   设置的捕获尺寸: {capture_size}")
        
        # 5. 检查MSS监视器信息
        print(f"\n🖥️ 测试MSS监视器信息:")
        import mss
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"   监视器数量: {len(monitors)}")
            for i, monitor in enumerate(monitors):
                if i == 0:
                    print(f"   监视器{i} (全部): {monitor}")
                else:
                    print(f"   监视器{i}: {monitor}")
        
        # 6. 测试实际截图
        print(f"\n📸 测试实际截图:")
        try:
            # 使用设置的区域进行截图测试
            with mss.mss() as sct:
                if screen_capture.region:
                    screenshot = sct.grab(screen_capture.region)
                    print(f"   截图尺寸: {screenshot.width}x{screenshot.height}")
                    print(f"   截图区域: {screen_capture.region}")
                else:
                    print("   未设置捕获区域")
        except Exception as e:
            print(f"   截图测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 坐标流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dpi_scaling_issue():
    """测试DPI缩放问题"""
    print("🔍 测试DPI缩放问题...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        import mss
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Qt屏幕信息
        screen = app.primaryScreen()
        qt_logical = screen.geometry()
        qt_physical = screen.size()
        qt_dpr = screen.devicePixelRatio()
        
        print(f"📱 Qt屏幕信息:")
        print(f"   逻辑几何: {qt_logical.width()}x{qt_logical.height()}")
        print(f"   物理尺寸: {qt_physical.width()}x{qt_physical.height()}")
        print(f"   设备像素比: {qt_dpr}")
        
        # MSS屏幕信息
        with mss.mss() as sct:
            mss_monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            print(f"\n🖥️ MSS屏幕信息:")
            print(f"   监视器: {mss_monitor}")
            print(f"   尺寸: {mss_monitor['width']}x{mss_monitor['height']}")
        
        # 分析差异
        print(f"\n🔍 差异分析:")
        qt_calculated_physical_width = int(qt_logical.width() * qt_dpr)
        qt_calculated_physical_height = int(qt_logical.height() * qt_dpr)
        
        print(f"   Qt计算的物理尺寸: {qt_calculated_physical_width}x{qt_calculated_physical_height}")
        print(f"   MSS实际尺寸: {mss_monitor['width']}x{mss_monitor['height']}")
        
        if (qt_calculated_physical_width == mss_monitor['width'] and 
            qt_calculated_physical_height == mss_monitor['height']):
            print("   ✅ Qt和MSS尺寸匹配")
        else:
            print("   ❌ Qt和MSS尺寸不匹配")
            print(f"   宽度差异: {mss_monitor['width'] - qt_calculated_physical_width}")
            print(f"   高度差异: {mss_monitor['height'] - qt_calculated_physical_height}")
        
        # 测试不同的坐标转换策略
        print(f"\n🧮 测试坐标转换策略:")
        
        # 策略1: 直接使用Qt DPR
        test_x, test_y, test_w, test_h = 100, 100, 200, 150
        strategy1_x = int(test_x * qt_dpr)
        strategy1_y = int(test_y * qt_dpr)
        strategy1_w = int(test_w * qt_dpr)
        strategy1_h = int(test_h * qt_dpr)
        print(f"   策略1 (Qt DPR): ({test_x}, {test_y}, {test_w}, {test_h}) -> ({strategy1_x}, {strategy1_y}, {strategy1_w}, {strategy1_h})")
        
        # 策略2: 使用MSS/Qt比例
        mss_qt_ratio_w = mss_monitor['width'] / qt_logical.width()
        mss_qt_ratio_h = mss_monitor['height'] / qt_logical.height()
        strategy2_x = int(test_x * mss_qt_ratio_w)
        strategy2_y = int(test_y * mss_qt_ratio_h)
        strategy2_w = int(test_w * mss_qt_ratio_w)
        strategy2_h = int(test_h * mss_qt_ratio_h)
        print(f"   策略2 (MSS/Qt比例): ({test_x}, {test_y}, {test_w}, {test_h}) -> ({strategy2_x}, {strategy2_y}, {strategy2_w}, {strategy2_h})")
        print(f"   比例: 宽度{mss_qt_ratio_w:.2f}, 高度{mss_qt_ratio_h:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ DPI缩放测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 坐标传递流程调试")
    print("="*50)
    
    if platform.system() != "Darwin":
        print("⚠️ 此调试主要针对macOS系统")
    
    tests = [
        ("坐标传递流程", test_coordinate_flow),
        ("DPI缩放问题", test_dpi_scaling_issue),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            success_count += 1
        else:
            print(f"   ⚠️ {test_name}测试失败")
    
    print("\n" + "="*50)
    print(f"📊 测试结果: {success_count}/{total_tests} 项通过")
    
    if success_count == total_tests:
        print("🎉 调试完成！")
        print("💡 如果发现问题，请检查上述输出中的差异")
    else:
        print("⚠️ 发现问题，需要进一步修复")
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
