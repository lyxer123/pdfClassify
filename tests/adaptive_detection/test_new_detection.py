#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的第二特征检测方法
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from main import PDFFeatureExtractor
import logging

# 启用DEBUG日志
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_new_detection():
    """测试新的连通组件分析方法"""
    
    # 加载模板图片
    template_img = np.array(Image.open('templates/mb.png').convert('RGB'))
    print(f"图片尺寸: {template_img.shape}")
    
    extractor = PDFFeatureExtractor()
    
    print("\n🔍 使用新方法检测第二特征...")
    result = extractor.detect_mb_second_feature(template_img)
    
    print(f"\n检测结果:")
    print(f"  是否有第二特征: {result['has_second_feature']}")
    print(f"  检测到的长横线数量: {result['detected_lines']}")
    
    if result['has_second_feature']:
        long_lines = result['long_lines']
        print(f"  两条主要长横线:")
        for i, line in enumerate(long_lines):
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / template_img.shape[0] * 100
            length_percent = length / template_img.shape[1] * 100
            print(f"    线条{i+1}: y={y_pos:.0f} ({y_percent:.1f}%高度), 长度={length:.0f} ({length_percent:.1f}%宽度)")
        
        line_distance = result['line_distance']
        distance_percent = line_distance / template_img.shape[0] * 100
        print(f"  两线间距: {line_distance:.0f}像素 ({distance_percent:.1f}%高度)")
        
        # 创建可视化
        create_visualization(template_img, result)
        
    else:
        print(f"  失败原因: {result['reason']}")
    
    return result['has_second_feature']

def create_visualization(image, result):
    """创建可视化图像"""
    
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    if result['has_second_feature']:
        long_lines = result['long_lines']
        
        for i, line in enumerate(long_lines):
            coords = line['coords']
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            
            # 绘制红色线条
            draw.line([(x1, y1), (x2, y2)], fill='red', width=4)
            
            # 添加标签
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / image.shape[0] * 100
            length_percent = length / image.shape[1] * 100
            
            label = f"线条{i+1}: y={y_pos:.0f}({y_percent:.1f}%) L={length_percent:.0f}%"
            label_x = int((x1 + x2) / 2) - 80
            label_y = int(y_pos) - 25
            
            draw.text((label_x, label_y), label, fill='red', font=font)
        
        # 添加距离信息
        line_distance = result['line_distance']
        distance_percent = line_distance / image.shape[0] * 100
        info_text = f"新方法检测结果: 2条长横线\n间距: {line_distance:.0f}px ({distance_percent:.1f}%高度)"
        draw.text((10, 10), info_text, fill='red', font=font)
    
    # 保存结果
    output_path = "hengxian_new.png"
    pil_image.save(output_path)
    print(f"\n✓ 可视化结果已保存到: {output_path}")

if __name__ == "__main__":
    success = test_new_detection()
    if success:
        print("\n🎉 新的检测方法成功！")
    else:
        print("\n❌ 新的检测方法失败，需要进一步调整")
