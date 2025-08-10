#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的第二特征检测算法
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
from pdf_feature_extractor import PDFFeatureExtractor
import logging

# 启用DEBUG日志
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_corrected_detection():
    """测试修正后的连通组件分析方法"""
    
    # 加载模板图片
    template_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb.png').convert('RGB'))
    print(f"图片尺寸: {template_img.shape}")
    
    extractor = PDFFeatureExtractor()
    
    print("\n🔍 使用修正后的方法检测第二特征...")
    print("期望检测到两条线:")
    print("  线条1: y≈359 (25%高度), 宽度≈306 (30%)")
    print("  线条2: y≈1245 (86.7%高度), 宽度≈826 (81%)")
    
    result = extractor.detect_mb_second_feature(template_img)
    
    print(f"\n检测结果:")
    print(f"  是否有第二特征: {result['has_second_feature']}")
    print(f"  检测到的长横线数量: {result['detected_lines']}")
    
    if result['has_second_feature']:
        long_lines = result['long_lines']
        print(f"  检测到的长横线:")
        for i, line in enumerate(long_lines):
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / template_img.shape[0] * 100
            length_percent = length / template_img.shape[1] * 100
            print(f"    线条{i+1}: y={y_pos:.0f} ({y_percent:.1f}%高度), 长度={length:.0f} ({length_percent:.1f}%宽度)")
        
        line_distance = result['line_distance']
        distance_percent = line_distance / template_img.shape[0] * 100
        print(f"  两线间距: {line_distance:.0f}像素 ({distance_percent:.1f}%高度)")
        
        # 验证检测准确性
        expected_y1, expected_y2 = 359, 1245
        actual_y1 = long_lines[0]['y_center']
        actual_y2 = long_lines[1]['y_center'] if len(long_lines) > 1 else 0
        
        error_y1 = abs(actual_y1 - expected_y1)
        error_y2 = abs(actual_y2 - expected_y2) if len(long_lines) > 1 else float('inf')
        
        print(f"\n准确性验证:")
        print(f"  第一条线: 期望y={expected_y1}, 实际y={actual_y1:.0f}, 误差={error_y1:.0f}像素")
        if len(long_lines) > 1:
            print(f"  第二条线: 期望y={expected_y2}, 实际y={actual_y2:.0f}, 误差={error_y2:.0f}像素")
        
        accuracy_ok = error_y1 <= 10 and error_y2 <= 50  # 允许一定误差
        print(f"  检测准确性: {'✓ 通过' if accuracy_ok else '❌ 不准确'}")
        
        # 创建可视化
        create_corrected_visualization(template_img, result, expected_y1, expected_y2)
        
    else:
        print(f"  失败原因: {result['reason']}")
    
    return result['has_second_feature']

def create_corrected_visualization(image, result, expected_y1, expected_y2):
    """创建修正后的可视化图像"""
    
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    height, width = image.shape[:2]
    
    # 绘制期望位置（黄色虚线）
    draw.line([(0, expected_y1), (width, expected_y1)], fill='yellow', width=2)
    draw.line([(0, expected_y2), (width, expected_y2)], fill='yellow', width=2)
    draw.text((10, expected_y1-20), f"期望线条1: y={expected_y1}", fill='yellow', font=small_font)
    draw.text((10, expected_y2-20), f"期望线条2: y={expected_y2}", fill='yellow', font=small_font)
    
    if result['has_second_feature']:
        long_lines = result['long_lines']
        
        for i, line in enumerate(long_lines):
            coords = line['coords']
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            
            # 绘制红色检测结果
            draw.line([(x1, y1), (x2, y2)], fill='red', width=4)
            
            # 添加标签
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / height * 100
            length_percent = length / width * 100
            
            label = f"检测线条{i+1}: y={y_pos:.0f}({y_percent:.1f}%) L={length_percent:.0f}%"
            label_x = int((x1 + x2) / 2) - 100
            label_y = int(y_pos) + 15
            
            draw.text((label_x, label_y), label, fill='red', font=font)
        
        # 添加结果信息
        line_distance = result['line_distance']
        distance_percent = line_distance / height * 100
        info_text = f"修正后检测结果: {len(long_lines)}条长横线\n间距: {line_distance:.0f}px ({distance_percent:.1f}%高度)\n黄色=期望位置，红色=检测结果"
        draw.text((10, 10), info_text, fill='black', font=font)
    
    # 保存结果
    output_path = "hengxian_corrected.png"
    pil_image.save(output_path)
    print(f"\n✓ 修正后的可视化结果已保存到: {output_path}")

if __name__ == "__main__":
    success = test_corrected_detection()
    if success:
        print("\n🎉 修正后的检测方法成功！")
    else:
        print("\n❌ 修正后的检测方法仍有问题，需要进一步调整")
