#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色阈值配置使用示例
展示如何使用PDF特征提取器的灵活配置功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
def setup_paths():
    """设置路径，确保能够导入项目模块"""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

# 设置路径
PROJECT_ROOT = setup_paths()

# 尝试导入测试包配置，如果失败则使用本地配置
try:
    from tests import PROJECT_ROOT as TEST_PROJECT_ROOT
    PROJECT_ROOT = TEST_PROJECT_ROOT
except ImportError:
    pass  # 使用本地设置的PROJECT_ROOT

def example_config_file_usage():
    """示例1: 使用配置文件"""
    print("示例1: 使用配置文件")
    print("-" * 40)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 配置文件路径
    config_file = PROJECT_ROOT / "config" / "color_thresholds.json"
    
    if not config_file.exists():
        print(f"配置文件不存在: {config_file}")
        print("请先创建配置文件")
        return
    
    # 使用配置文件创建特征提取器
    extractor = PDFFeatureExtractor(config_file=str(config_file))
    
    print("✅ 已从配置文件加载颜色阈值")
    print("当前配置:")
    config = extractor.get_color_thresholds()
    for key, value in config.items():
        print(f"  {key}: {value}")

def example_environment_variables():
    """示例2: 使用环境变量"""
    print("\n示例2: 使用环境变量")
    print("-" * 40)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 设置环境变量
    os.environ['WHITE_BG_MIN'] = '180'  # 降低白色背景阈值
    os.environ['BLACK_TEXT_MAX'] = '100'  # 提高黑色文字阈值
    os.environ['CONTRAST_MIN'] = '20'  # 降低对比度要求
    
    print("已设置环境变量:")
    print("  WHITE_BG_MIN=180")
    print("  BLACK_TEXT_MAX=100")
    print("  CONTRAST_MIN=20")
    
    # 创建特征提取器（会自动从环境变量加载）
    extractor = PDFFeatureExtractor()
    
    print("\n当前配置:")
    config = extractor.get_color_thresholds()
    for key, value in config.items():
        print(f"  {key}: {value}")

def example_runtime_update():
    """示例3: 运行时更新配置"""
    print("\n示例3: 运行时更新配置")
    print("-" * 40)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    print("原始配置:")
    original_config = extractor.get_color_thresholds()
    for key, value in original_config.items():
        print(f"  {key}: {value}")
    
    # 运行时更新配置
    new_thresholds = {
        'white_bg_min': 190,
        'black_text_max': 90,
        'contrast_min': 25
    }
    
    print(f"\n更新配置: {new_thresholds}")
    extractor.update_color_thresholds(new_thresholds)
    
    print("\n更新后的配置:")
    updated_config = extractor.get_color_thresholds()
    for key, value in updated_config.items():
        print(f"  {key}: {value}")

def example_save_and_reset():
    """示例4: 保存和重置配置"""
    print("\n示例4: 保存和重置配置")
    print("-" * 40)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
    except ImportError as e:
        print(f"❌ 无法导入 PDFFeatureExtractor: {e}")
        return
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 修改一些配置
    extractor.update_color_thresholds({
        'white_bg_min': 185,
        'black_text_max': 85
    })
    
    print("修改后的配置:")
    config = extractor.get_color_thresholds()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # 保存配置到文件
    save_path = PROJECT_ROOT / "test_config.json"
    if extractor.save_color_thresholds(str(save_path)):
        print(f"\n✅ 配置已保存到: {save_path}")
    
    # 重置为默认配置
    extractor.reset_color_thresholds()
    print("\n🔄 配置已重置为默认值")
    
    print("重置后的配置:")
    reset_config = extractor.get_color_thresholds()
    for key, value in reset_config.items():
        print(f"  {key}: {value}")
    
    # 清理测试文件
    if save_path.exists():
        save_path.unlink()
        print(f"\n🧹 已清理测试配置文件: {save_path}")

def main():
    """主函数"""
    print("=== PDF特征提取器 - 颜色阈值配置示例 ===\n")
    print(f"项目根目录: {PROJECT_ROOT}")
    print()
    
    # 运行所有示例
    example_config_file_usage()
    example_environment_variables()
    example_runtime_update()
    example_save_and_reset()
    
    print("\n=== 示例完成 ===")
    print("\n💡 提示:")
    print("1. 可以使用 --config 参数指定配置文件")
    print("2. 可以使用 --show-config 查看当前配置")
    print("3. 可以使用 --save-config 保存当前配置")
    print("4. 可以通过环境变量覆盖默认配置")
    print("5. 可以在运行时动态更新配置")

if __name__ == "__main__":
    main()
