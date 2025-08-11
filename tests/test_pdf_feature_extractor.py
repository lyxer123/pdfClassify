#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF特征提取器功能测试脚本
测试pdf_feature_extractor.py的各种功能
"""

import os
import sys
import json
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

def test_basic_initialization():
    """测试基本初始化功能"""
    print("=" * 50)
    print("测试1: 基本初始化功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        # 测试默认初始化
        extractor = PDFFeatureExtractor()
        print("✅ 默认初始化成功")
        
        # 测试自定义参数初始化
        extractor2 = PDFFeatureExtractor(
            template_path="templates/mb.png",
            data_dir="test_data",
            config_file=None
        )
        print("✅ 自定义参数初始化成功")
        
        # 测试获取颜色阈值
        thresholds = extractor.get_color_thresholds()
        print(f"✅ 获取颜色阈值成功: {len(thresholds)} 个参数")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化测试失败: {str(e)}")
        return False

def test_color_threshold_management():
    """测试颜色阈值管理功能"""
    print("\n" + "=" * 50)
    print("测试2: 颜色阈值管理功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        extractor = PDFFeatureExtractor()
        
        # 测试显示当前配置
        print("当前颜色阈值配置:")
        config = extractor.get_color_thresholds()
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # 测试更新阈值
        new_thresholds = {
            'white_bg_min': 180,
            'contrast_min': 30
        }
        extractor.update_color_thresholds(new_thresholds)
        print("✅ 阈值更新成功")
        
        # 验证更新结果
        updated_config = extractor.get_color_thresholds()
        if updated_config['white_bg_min'] == 180 and updated_config['contrast_min'] == 30:
            print("✅ 阈值更新验证成功")
        else:
            print("❌ 阈值更新验证失败")
        
        # 测试重置阈值
        extractor.reset_color_thresholds()
        print("✅ 阈值重置成功")
        
        # 测试保存配置
        test_config_file = "test_config.json"
        if extractor.save_color_thresholds(test_config_file):
            print("✅ 配置保存成功")
            # 清理测试文件
            if os.path.exists(test_config_file):
                os.remove(test_config_file)
                print("✅ 测试配置文件已清理")
        else:
            print("❌ 配置保存失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 颜色阈值管理测试失败: {str(e)}")
        return False

def test_pdf_conversion():
    """测试PDF转换功能"""
    print("\n" + "=" * 50)
    print("测试3: PDF转换功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        extractor = PDFFeatureExtractor()
        
        # 查找测试PDF文件
        test_pdf = PROJECT_ROOT / "input_pdfs" / "test.pdf"
        
        if not test_pdf.exists():
            print(f"⚠️ 测试PDF文件不存在: {test_pdf}")
            print("请确保在input_pdfs文件夹中有test.pdf文件")
            return False
        
        print(f"使用测试PDF文件: {test_pdf}")
        
        # 测试不同页面模式
        page_modes = ["first_n", "first_page", "all_pages"]
        
        for mode in page_modes:
            print(f"\n测试页面模式: {mode}")
            try:
                images = extractor.pdf_to_images(str(test_pdf), max_pages=3, page_mode=mode)
                if images:
                    print(f"✅ {mode}模式成功，转换了 {len(images)} 页")
                    for i, img in enumerate(images):
                        print(f"  第{i+1}页尺寸: {img.shape}")
                else:
                    print(f"❌ {mode}模式失败，未生成图像")
            except Exception as e:
                print(f"❌ {mode}模式出错: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF转换测试失败: {str(e)}")
        return False

def test_feature_analysis():
    """测试特征分析功能"""
    print("\n" + "=" * 50)
    print("测试4: 特征分析功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        extractor = PDFFeatureExtractor()
        
        # 查找测试PDF文件
        test_pdf = PROJECT_ROOT / "input_pdfs" / "test.pdf"
        
        if not test_pdf.exists():
            print(f"⚠️ 测试PDF文件不存在: {test_pdf}")
            return False
        
        # 转换第一页为图像
        images = extractor.pdf_to_images(str(test_pdf), max_pages=1, page_mode="first_page")
        if not images:
            print("❌ 无法获取测试图像")
            return False
        
        test_image = images[0]
        print(f"✅ 获取测试图像成功，尺寸: {test_image.shape}")
        
        # 测试颜色特征分析
        print("\n分析颜色特征...")
        color_features = extractor.analyze_color_features(test_image)
        if color_features:
            print("✅ 颜色特征分析成功")
            print(f"  白色背景比例: {color_features['white_bg_ratio']:.3f}")
            print(f"  黑色文字比例: {color_features['black_text_ratio']:.3f}")
            print(f"  彩色文字比例: {color_features['colored_text_ratio']:.3f}")
            print(f"  对比度: {color_features['contrast']:.1f}")
            print(f"  图像尺寸: {color_features['image_size']}")
        else:
            print("❌ 颜色特征分析失败")
        
        # 测试第二特征检测
        print("\n检测第二特征（长黑线）...")
        second_feature = extractor.detect_mb_second_feature(test_image)
        if second_feature:
            print("✅ 第二特征检测成功")
            print(f"  检测到线条数: {second_feature['detected_lines']}")
            print(f"  是否有第二特征: {second_feature['has_second_feature']}")
            if second_feature['long_lines']:
                for i, line in enumerate(second_feature['long_lines']):
                    print(f"  线条{i+1}: y={line['y_center']:.0f}, 长度={line['length']:.0f}")
        else:
            print("❌ 第二特征检测失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 特征分析测试失败: {str(e)}")
        return False

def test_standard_compliance():
    """测试标准符合性检查"""
    print("\n" + "=" * 50)
    print("测试5: 标准符合性检查")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        extractor = PDFFeatureExtractor()
        
        # 查找测试PDF文件
        test_pdf = PROJECT_ROOT / "input_pdfs" / "test.pdf"
        
        if not test_pdf.exists():
            print(f"⚠️ 测试PDF文件不存在: {test_pdf}")
            return False
        
        # 转换第一页为图像
        images = extractor.pdf_to_images(str(test_pdf), max_pages=1, page_mode="first_page")
        if not images:
            print("❌ 无法获取测试图像")
            return False
        
        test_image = images[0]
        
        # 分析特征
        features = extractor.analyze_color_features(test_image)
        if not features:
            print("❌ 特征分析失败")
            return False
        
        # 检查标准符合性
        print("检查标准符合性...")
        compliance = extractor.check_standard_compliance(features)
        
        print(f"✅ 标准符合性检查完成")
        print(f"  最终结果: {'符合标准' if compliance else '不符合标准'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 标准符合性检查测试失败: {str(e)}")
        return False

def test_pdf_processing():
    """测试PDF文件处理功能"""
    print("\n" + "=" * 50)
    print("测试6: PDF文件处理功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        extractor = PDFFeatureExtractor()
        
        # 查找测试PDF文件
        test_pdf = PROJECT_ROOT / "input_pdfs" / "test.pdf"
        
        if not test_pdf.exists():
            print(f"⚠️ 测试PDF文件不存在: {test_pdf}")
            return False
        
        # 测试单个PDF文件处理
        print("处理单个PDF文件...")
        result = extractor.process_pdf_file(str(test_pdf), max_pages=2, page_mode="first_n")
        
        if result and result['success']:
            print("✅ PDF文件处理成功")
            print(f"  文件名: {result['file_name']}")
            print(f"  分析页数: {result['pages_analyzed']}")
            print(f"  页面模式: {result['page_mode']}")
            print(f"  整体符合性: {'是' if result['overall_compliance'] else '否'}")
            
            # 显示页面结果
            for page_result in result['page_results']:
                page_num = page_result['page_number']
                compliance = page_result['compliance']
                print(f"  第{page_num}页: {'符合' if compliance else '不符合'}")
        else:
            print("❌ PDF文件处理失败")
            if result:
                print(f"  错误信息: {result.get('error', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF文件处理测试失败: {str(e)}")
        return False

def test_configuration_loading():
    """测试配置文件加载功能"""
    print("\n" + "=" * 50)
    print("测试7: 配置文件加载功能")
    print("=" * 50)
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        # 测试从环境变量加载配置
        print("测试环境变量配置加载...")
        
        # 设置测试环境变量
        os.environ['WHITE_BG_MIN'] = '180'
        os.environ['CONTRAST_MIN'] = '30'
        
        extractor = PDFFeatureExtractor()
        
        # 检查是否加载了环境变量配置
        config = extractor.get_color_thresholds()
        if config['white_bg_min'] == 180 and config['contrast_min'] == 30:
            print("✅ 环境变量配置加载成功")
        else:
            print("❌ 环境变量配置加载失败")
        
        # 测试从JSON文件加载配置
        print("\n测试JSON配置文件加载...")
        test_config = {
            "color_thresholds": {
                "white_bg_min": 190,
                "black_text_max": 70
            }
        }
        
        test_config_file = "test_color_config.json"
        with open(test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2)
        
        try:
            extractor2 = PDFFeatureExtractor(config_file=test_config_file)
            config2 = extractor2.get_color_thresholds()
            
            if config2['white_bg_min'] == 190 and config2['black_text_max'] == 70:
                print("✅ JSON配置文件加载成功")
            else:
                print("❌ JSON配置文件加载失败")
                
        finally:
            # 清理测试文件
            if os.path.exists(test_config_file):
                os.remove(test_config_file)
                print("✅ 测试配置文件已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件加载测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试PDF特征提取器功能")
    print("=" * 60)
    
    # 测试列表
    tests = [
        ("基本初始化功能", test_basic_initialization),
        ("颜色阈值管理功能", test_color_threshold_management),
        ("PDF转换功能", test_pdf_conversion),
        ("特征分析功能", test_feature_analysis),
        ("标准符合性检查", test_standard_compliance),
        ("PDF文件处理功能", test_pdf_processing),
        ("配置文件加载功能", test_configuration_loading)
    ]
    
    # 运行测试
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️ {test_name}测试未通过")
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("🎯 测试结果汇总")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！PDF特征提取器功能正常")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试未通过，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
