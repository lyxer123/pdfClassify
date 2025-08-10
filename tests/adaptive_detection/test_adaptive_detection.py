#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自适应长横线检测算法
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

def test_adaptive_detection():
    """测试自适应检测算法在不同图片上的表现"""
    
    test_images = [
        (str(TEMPLATES_DIR / 'mb.png'), 'mb.png'),
        (str(TEMPLATES_DIR / 'mb9.png'), 'mb9.png')
    ]
    
    extractor = PDFFeatureExtractor()
    
    for img_path, img_name in test_images:
        print(f"\n{'='*60}")
        print(f"测试 {img_name}")
        print(f"{'='*60}")
        
        # 加载图片
        img = np.array(Image.open(img_path).convert('RGB'))
        print(f"{img_name} 尺寸: {img.shape}")
        
        # 检测第二特征
        result = extractor.detect_mb_second_feature(img)
        
        print(f"\n检测结果:")
        print(f"  是否有第二特征: {result['has_second_feature']}")
        print(f"  检测到的长横线数量: {result['detected_lines']}")
        
        if result['has_second_feature']:
            long_lines = result['long_lines']
            print(f"  检测到的长横线:")
            for i, line in enumerate(long_lines):
                y_pos = line['y_center']
                length = line['length']
                y_percent = y_pos / img.shape[0] * 100
                length_percent = line['width_ratio'] * 100
                print(f"    线条{i+1}: y={y_pos:.0f} ({y_percent:.1f}%高度), 长度={length:.0f} ({length_percent:.1f}%宽度)")
            
            line_distance = result['line_distance']
            distance_percent = line_distance / img.shape[0] * 100
            print(f"  两线间距: {line_distance:.0f}像素 ({distance_percent:.1f}%高度)")
            
        else:
            print(f"  失败原因: {result['reason']}")
            
            # 显示检测到的线条（如果有）
            if result['detected_lines'] > 0 and 'long_lines' in result:
                print(f"  检测到的线条:")
                for i, line in enumerate(result['long_lines']):
                    y_pos = line['y_center']
                    length = line['length']
                    y_percent = y_pos / img.shape[0] * 100
                    length_percent = line['width_ratio'] * 100
                    print(f"    线条{i+1}: y={y_pos:.0f} ({y_percent:.1f}%高度), 长度={length:.0f} ({length_percent:.1f}%宽度)")
        
        # 创建可视化
        create_adaptive_visualization(img, result, img_name)
    
    print(f"\n{'='*60}")
    print("测试完成")

def create_adaptive_visualization(image, result, image_name):
    """创建自适应检测的可视化图像"""
    
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    height, width = image.shape[:2]
    
    # 绘制检测到的线条
    if 'long_lines' in result and result['long_lines']:
        for i, line in enumerate(result['long_lines']):
            coords = line['coords']
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            
            # 绘制红色线条
            draw.line([(x1, y1), (x2, y2)], fill='red', width=4)
            
            # 添加标签
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / height * 100
            length_percent = line['width_ratio'] * 100
            
            label = f"线条{i+1}: y={y_pos:.0f}({y_percent:.1f}%) L={length_percent:.0f}%"
            label_x = int((x1 + x2) / 2) - 100
            label_y = int(y_pos) + (15 if i == 0 else -25)  # 错开标签位置
            
            draw.text((label_x, label_y), label, fill='red', font=font)
    
    # 添加结果信息
    if result['has_second_feature']:
        line_distance = result['line_distance']
        distance_percent = line_distance / height * 100
        info_text = f"{image_name} 自适应检测: ✓ 成功\n{result['detected_lines']}条长横线\n间距: {line_distance:.0f}px ({distance_percent:.1f}%高度)"
        color = 'green'
    else:
        info_text = f"{image_name} 自适应检测: ✗ 失败\n检测到{result['detected_lines']}条线\n原因: {result['reason'][:30]}..."  # 截断长原因
        color = 'red'
    
    draw.text((10, 10), info_text, fill=color, font=font)
    
    # 保存结果
    output_path = f"{image_name.replace('.png', '')}_adaptive_result.png"
    pil_image.save(output_path)
    print(f"  ✓ 可视化结果已保存到: {output_path}")

if __name__ == "__main__":
    print("测试自适应长横线检测算法")
    test_adaptive_detection()
