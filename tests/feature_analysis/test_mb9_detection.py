#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试mb9.png的长横线检测
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

def test_mb9_detection():
    """测试mb9.png的第二特征检测"""
    
    # 加载mb9.png
    mb9_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb9.png')).convert('RGB'))
    print(f"mb9.png尺寸: {mb9_img.shape}")
    
    extractor = PDFFeatureExtractor()
    
    print("\n🔍 使用当前方法检测mb9.png的第二特征...")
    result = extractor.detect_mb_second_feature(mb9_img)
    
    print(f"\n检测结果:")
    print(f"  是否有第二特征: {result['has_second_feature']}")
    print(f"  检测到的长横线数量: {result['detected_lines']}")
    
    if result['has_second_feature']:
        long_lines = result['long_lines']
        print(f"  检测到的长横线:")
        for i, line in enumerate(long_lines):
            y_pos = line['y_center']
            length = line['length']
            y_percent = y_pos / mb9_img.shape[0] * 100
            length_percent = line['width_ratio'] * 100
            print(f"    线条{i+1}: y={y_pos:.0f} ({y_percent:.1f}%高度), 长度={length:.0f} ({length_percent:.1f}%宽度)")
        
        line_distance = result['line_distance']
        distance_percent = line_distance / mb9_img.shape[0] * 100
        print(f"  两线间距: {line_distance:.0f}像素 ({distance_percent:.1f}%高度)")
        
        # 创建可视化
        create_mb9_visualization(mb9_img, result)
        
    else:
        print(f"  失败原因: {result['reason']}")
        
        # 即使失败，也创建可视化显示检测到的线条
        if result['detected_lines'] > 0:
            create_mb9_visualization(mb9_img, result)
    
    return result['has_second_feature']

def create_mb9_visualization(image, result):
    """创建mb9.png的可视化图像"""
    
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
            label_y = int(y_pos) + 15
            
            draw.text((label_x, label_y), label, fill='red', font=font)
    
    # 添加结果信息
    if result['has_second_feature']:
        line_distance = result['line_distance']
        distance_percent = line_distance / height * 100
        info_text = f"mb9.png检测结果: ✓ 成功\n{result['detected_lines']}条长横线\n间距: {line_distance:.0f}px ({distance_percent:.1f}%高度)"
        color = 'green'
    else:
        info_text = f"mb9.png检测结果: ✗ 失败\n检测到{result['detected_lines']}条线\n原因: {result['reason']}"
        color = 'red'
    
    draw.text((10, 10), info_text, fill=color, font=font)
    
    # 保存结果
    output_path = "mb9_detection_result.png"
    pil_image.save(output_path)
    print(f"\n✓ mb9.png检测可视化结果已保存到: {output_path}")

def debug_mb9_precise_detection():
    """调试mb9.png的精确检测过程"""
    
    print("\n" + "="*50)
    print("调试mb9.png的精确检测过程")
    print("="*50)
    
    # 加载mb9.png
    mb9_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb9.png').convert('RGB'))
    height, width = mb9_img.shape[:2]
    gray = cv2.cvtColor(mb9_img, cv2.COLOR_RGB2GRAY)
    
    # 创建黑色区域的掩码
    black_mask = gray < 80
    print(f"mb9.png黑色像素数量: {np.sum(black_mask)}")
    
    # 定义两个目标区域
    target_y1 = 359
    target_y2 = 1245
    search_range = 50  # 扩大搜索范围
    
    print(f"\n=== 检测mb9.png第一条线 (目标y={target_y1}) ===")
    result1 = debug_line_detection(black_mask, target_y1, search_range, width, height, "第一条线")
    
    print(f"\n=== 检测mb9.png第二条线 (目标y={target_y2}) ===")
    result2 = debug_line_detection(black_mask, target_y2, search_range, width, height, "第二条线")
    
    return result1, result2

def debug_line_detection(black_mask, target_y, search_range, width, height, line_name):
    """调试版本的线条检测"""
    
    y_start = max(0, target_y - search_range)
    y_end = min(height, target_y + search_range)
    
    print(f"搜索范围: y={y_start} 到 y={y_end}")
    
    roi = black_mask[y_start:y_end, :]
    roi_pixels = np.sum(roi)
    print(f"搜索区域黑色像素数量: {roi_pixels}")
    
    if roi_pixels == 0:
        print(f"❌ {line_name}: 搜索区域内没有黑色像素")
        return None
    
    # 寻找最长的线段
    best_line = None
    max_length = 0
    
    for row_offset in range(roi.shape[0]):
        row = roi[row_offset, :]
        actual_y = y_start + row_offset
        
        # 查找连续的黑色像素段
        segments = []
        start = None
        
        for col in range(len(row)):
            if row[col]:
                if start is None:
                    start = col
            else:
                if start is not None:
                    segments.append((start, col - 1))
                    start = None
        
        if start is not None:
            segments.append((start, len(row) - 1))
        
        # 检查这一行的最长线段
        if segments:
            for start_col, end_col in segments:
                segment_length = end_col - start_col + 1
                segment_ratio = segment_length / width
                
                if segment_ratio >= 0.1 and segment_length > max_length:  # 降低到10%阈值
                    max_length = segment_length
                    best_line = {
                        'coords': (start_col, actual_y, end_col, actual_y),
                        'length': segment_length,
                        'y_center': float(actual_y),
                        'width_ratio': segment_ratio
                    }
    
    if best_line:
        y_percent = best_line['y_center'] / height * 100
        width_percent = best_line['width_ratio'] * 100
        print(f"✓ {line_name}检测成功: y={best_line['y_center']:.0f}({y_percent:.1f}%), 长度={best_line['length']}({width_percent:.1f}%)")
        return best_line
    else:
        print(f"❌ {line_name}检测失败: 未找到长度>=10%宽度的线条")
        return None

if __name__ == "__main__":
    print("测试mb9.png的长横线检测")
    
    # 测试当前算法
    success = test_mb9_detection()
    
    # 调试精确检测过程
    debug_mb9_precise_detection()
    
    if success:
        print("\n🎉 mb9.png检测成功！")
    else:
        print("\n❌ mb9.png检测失败")
