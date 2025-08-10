#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：PDF特征提取功能测试
使用mb.png模板图片进行真实测试
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

from main import PDFFeatureExtractor


def load_template_image(template_path=None):
    """
    加载模板图片
    
    Args:
        template_path: 模板图片路径，如果为None则使用默认路径
    
    Returns:
        numpy.ndarray: 图像数组，如果加载失败返回None
    """
    if template_path is None:
        template_path = TEMPLATES_DIR / "mb.png"
    """
    加载模板图片
    
    Args:
        template_path: 模板图片路径
    
    Returns:
        numpy.ndarray: 图像数组，如果加载失败返回None
    """
    try:
        template_path = Path(template_path)
        if not template_path.exists():
            print(f"❌ 模板图片不存在: {template_path}")
            return None
        
        # 使用PIL加载图片
        img = Image.open(template_path)
        # 确保是RGB格式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 转换为numpy数组
        img_array = np.array(img)
        print(f"✓ 成功加载模板图片: {template_path}")
        print(f"  图片尺寸: {img_array.shape}")
        print(f"  图片格式: {img.mode}")
        
        return img_array
        
    except Exception as e:
        print(f"❌ 加载模板图片失败: {str(e)}")
        return None


def create_test_variations(template_img):
    """
    基于模板图片创建测试变体
    
    Args:
        template_img: 模板图像数组
    
    Returns:
        dict: 包含不同测试图像的字典
    """
    if template_img is None:
        return {}
    
    variations = {}
    
    # 原始模板
    variations['original'] = template_img.copy()
    
    # 创建反色版本（用于测试对比）
    variations['inverted'] = 255 - template_img
    
    # 创建低对比度版本
    gray = cv2.cvtColor(template_img, cv2.COLOR_RGB2GRAY)
    low_contrast = cv2.merge([gray//2 + 128] * 3)  # 降低对比度
    variations['low_contrast'] = low_contrast
    
    # 创建偏蓝色版本
    blue_tinted = template_img.copy()
    blue_tinted[:, :, 2] = np.minimum(blue_tinted[:, :, 2] + 50, 255)  # 增加蓝色分量
    variations['blue_tinted'] = blue_tinted
    
    return variations


def test_color_feature_analysis():
    """测试颜色特征分析功能"""
    print("=== 测试颜色特征分析功能 ===")
    
    # 加载mb.png模板图片
    template_img = load_template_image()
    if template_img is None:
        print("❌ 无法加载模板图片，跳过测试")
        return False
    
    extractor = PDFFeatureExtractor()
    
    # 创建测试变体
    test_images = create_test_variations(template_img)
    
    # 测试1：原始mb.png模板
    print("\n测试1：mb.png模板图片（标准参考）")
    features = extractor.analyze_color_features(test_images['original'])
    compliance = extractor.check_standard_compliance(features)
    print(f"符合性检查结果: {'符合' if compliance else '不符合'}")
    
    # 测试2：反色版本
    print("\n测试2：反色版本（应该不符合标准）")
    features = extractor.analyze_color_features(test_images['inverted'])
    compliance = extractor.check_standard_compliance(features)
    print(f"符合性检查结果: {'符合' if compliance else '不符合'}")
    
    # 测试3：低对比度版本
    print("\n测试3：低对比度版本（可能不符合标准）")
    features = extractor.analyze_color_features(test_images['low_contrast'])
    compliance = extractor.check_standard_compliance(features)
    print(f"符合性检查结果: {'符合' if compliance else '不符合'}")
    
    # 测试4：偏蓝色版本
    print("\n测试4：偏蓝色版本（可能不符合标准）")
    features = extractor.analyze_color_features(test_images['blue_tinted'])
    compliance = extractor.check_standard_compliance(features)
    print(f"符合性检查结果: {'符合' if compliance else '不符合'}")
    
    return True


def test_data_saving():
    """测试数据保存功能"""
    print("\n=== 测试数据保存功能 ===")
    
    extractor = PDFFeatureExtractor(data_dir="test_data")
    
    # 创建测试结果
    test_result = {
        'file_path': 'test.pdf',
        'file_name': 'test.pdf',
        'success': True,
        'overall_compliance': True,
        'pages_analyzed': 1,
        'page_results': [
            {
                'page_number': 1,
                'compliance': True,
                'features': {
                    'white_bg_ratio': 0.75,
                    'black_text_ratio': 0.15,
                    'contrast': 85.2,
                    'mean_rgb': [230, 235, 240]
                }
            }
        ],
        'timestamp': '2024-01-15T10:30:00'
    }
    
    # 保存结果
    extractor.save_results(test_result, "test_result.json")
    
    # 检查文件是否存在
    test_data_dir = Path("test_data")
    saved_file = test_data_dir / "test_result.json"
    
    if saved_file.exists():
        print(f"✓ 结果文件已成功保存: {saved_file}")
        
        # 读取并验证内容
        with open(saved_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if loaded_data['file_name'] == 'test.pdf':
            print("✓ 保存的数据内容正确")
        else:
            print("✗ 保存的数据内容有误")
        
        # 清理测试文件
        saved_file.unlink()
        if test_data_dir.exists() and not any(test_data_dir.iterdir()):
            test_data_dir.rmdir()
        print("✓ 测试文件已清理")
        
        return True
    else:
        print("✗ 结果文件保存失败")
        return False


def test_threshold_configuration():
    """测试阈值配置"""
    print("\n=== 测试阈值配置 ===")
    
    # 加载mb.png模板图片
    template_img = load_template_image()
    if template_img is None:
        print("❌ 无法加载模板图片，跳过测试")
        return False
    
    extractor = PDFFeatureExtractor()
    
    # 显示当前阈值配置
    print("当前阈值配置:")
    for key, value in extractor.color_thresholds.items():
        print(f"  {key}: {value}")
    
    # 测试阈值调整
    original_bg_min = extractor.color_thresholds['bg_ratio_min']
    extractor.color_thresholds['bg_ratio_min'] = 0.8  # 提高要求
    
    print(f"\n使用mb.png模板测试不同阈值:")
    features = extractor.analyze_color_features(template_img)
    compliance_strict = extractor.check_standard_compliance(features)
    
    # 恢复原始阈值
    extractor.color_thresholds['bg_ratio_min'] = original_bg_min
    compliance_normal = extractor.check_standard_compliance(features)
    
    print(f"严格阈值下符合性: {'符合' if compliance_strict else '不符合'}")
    print(f"正常阈值下符合性: {'符合' if compliance_normal else '不符合'}")
    
    return True


def test_second_feature_detection():
    """专门测试第二特征检测功能"""
    print("\n=== 测试第二特征检测功能 ===")
    
    # 加载mb.png模板图片
    template_img = load_template_image()
    if template_img is None:
        print("❌ 无法加载模板图片，跳过测试")
        return False
    
    extractor = PDFFeatureExtractor()
    
    print(f"\n🔍 第二特征检测测试:")
    print(f"特征要求：")
    print(f"  1. 有两条左右的长黑线")
    print(f"  2. 黑线长度>=80%页面宽度")
    print(f"  3. 两条黑色线长度相等")
    print(f"  4. 两条黑色线之间距离>=60%页面高度")
    print(f"  5. 且只有两根长黑线")
    
    # 直接测试第二特征检测
    second_feature_result = extractor.detect_mb_second_feature(template_img)
    
    print(f"\n📊 检测结果:")
    print(f"  特征检测: {'✓ 通过' if second_feature_result['has_second_feature'] else '✗ 未通过'}")
    print(f"  检测到线条数: {second_feature_result['detected_lines']}")
    print(f"  检测说明: {second_feature_result['reason']}")
    
    if second_feature_result['detected_lines'] > 0:
        print(f"  线条长度: {second_feature_result['line_lengths']}")
        if second_feature_result['has_second_feature']:
            print(f"  长度比例: {second_feature_result['length_ratio_1']:.1%}, {second_feature_result['length_ratio_2']:.1%}")
            print(f"  线条间距: {second_feature_result['line_distance']:.1f} 像素")
            print(f"  间距比例: {second_feature_result['line_distance_ratio']:.1%}")
    
    # 创建测试变体来验证算法鲁棒性
    test_images = create_test_variations(template_img)
    
    print(f"\n🧪 测试变体验证:")
    for variant_name, variant_img in test_images.items():
        if variant_name == 'original':
            continue
        
        variant_result = extractor.detect_mb_second_feature(variant_img)
        print(f"  {variant_name}: {'✓' if variant_result['has_second_feature'] else '✗'} - {variant_result['reason']}")
    
    return second_feature_result['has_second_feature']


def test_template_analysis():
    """测试mb.png模板图片的详细特征分析"""
    print("\n=== 测试mb.png模板图片详细分析 ===")
    
    # 加载mb.png模板图片
    template_img = load_template_image()
    if template_img is None:
        print("❌ 无法加载模板图片，跳过测试")
        return False
    
    extractor = PDFFeatureExtractor()
    
    print(f"\n📊 mb.png详细特征分析:")
    features = extractor.analyze_color_features(template_img)
    
    if features:
        print(f"  图片尺寸: {features['image_size'][0]} x {features['image_size'][1]}")
        print(f"  总像素数: {features['total_pixels']:,}")
        print(f"  平均RGB值: {[f'{c:.1f}' for c in features['mean_rgb']]}")
        print(f"  白色背景比例: {features['white_bg_ratio']:.3f} ({features['white_bg_ratio']*100:.1f}%)")
        print(f"  黑色文字比例: {features['black_text_ratio']:.3f} ({features['black_text_ratio']*100:.1f}%)")
        print(f"  图像对比度: {features['contrast']:.2f}")
        
        # 第二特征分析
        if 'second_feature' in features:
            second_feature = features['second_feature']
            print(f"\n📏 第二特征（两条长黑线）分析:")
            print(f"  检测状态: {'✓ 通过' if second_feature['has_second_feature'] else '✗ 未通过'}")
            print(f"  检测到线条数: {second_feature['detected_lines']}")
            if second_feature['has_second_feature']:
                print(f"  线条长度: {second_feature['line_lengths'][0]:.1f}, {second_feature['line_lengths'][1]:.1f} 像素")
                print(f"  长度占比: {second_feature['length_ratio_1']:.1%}, {second_feature['length_ratio_2']:.1%}")
                print(f"  线条间距: {second_feature['line_distance']:.1f} 像素")
                print(f"  间距占比: {second_feature['line_distance_ratio']:.1%}")
            print(f"  检测结果: {second_feature['reason']}")
        
        # 检查符合性
        compliance = extractor.check_standard_compliance(features)
        print(f"\n✅ mb.png模板符合性: {'符合标准' if compliance else '不符合标准'}")
        
        # 保存详细分析结果
        template_result = {
            'template_path': str(TEMPLATES_DIR / 'mb.png'),
            'analysis_type': 'template_analysis',
            'features': features,
            'compliance': compliance,
            'timestamp': '2024-01-15T10:30:00'
        }
        
        extractor.save_results(template_result, "mb_template_analysis.json")
        print(f"💾 模板分析结果已保存到: mb_template_analysis.json")
        
        return True
    else:
        print("❌ 特征分析失败")
        return False


def main():
    """运行所有测试"""
    print("开始PDF特征提取功能测试...\n")
    
    tests = [
        ("mb.png模板详细分析", test_template_analysis),
        ("第二特征检测功能", test_second_feature_detection),
        ("颜色特征分析", test_color_feature_analysis),
        ("数据保存功能", test_data_saving),
        ("阈值配置", test_threshold_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"运行测试: {test_name}")
            print('='*50)
            
            success = test_func()
            if success:
                print(f"✓ {test_name} - 通过")
                passed += 1
            else:
                print(f"✗ {test_name} - 失败")
                
        except Exception as e:
            print(f"✗ {test_name} - 异常: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"测试结果汇总: {passed}/{total} 通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败，请检查代码")
        return 1


if __name__ == "__main__":
    sys.exit(main())
