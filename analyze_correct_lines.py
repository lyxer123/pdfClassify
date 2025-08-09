#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析mb88.png中标注的正确长横线位置
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

# 启用DEBUG日志
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def analyze_red_lines_in_mb88():
    """分析mb88.png中的红色长横线标注"""
    
    # 加载原始图片和标注图片
    original_img = np.array(Image.open('templates/mb.png').convert('RGB'))
    annotated_img = np.array(Image.open('templates/mb88.png').convert('RGB'))
    
    print(f"原始图片尺寸: {original_img.shape}")
    print(f"标注图片尺寸: {annotated_img.shape}")
    
    height, width = original_img.shape[:2]
    
    # 检测红色区域（红色标注线）
    # 红色像素：R值高，G和B值低
    red_mask = (annotated_img[:, :, 0] > 200) & (annotated_img[:, :, 1] < 100) & (annotated_img[:, :, 2] < 100)
    
    print(f"红色像素数量: {np.sum(red_mask)}")
    
    if np.sum(red_mask) == 0:
        print("❌ 没有检测到红色标注")
        return
    
    # 使用连通组件分析来识别红色线条
    result = cv2.connectedComponents(red_mask.astype(np.uint8))
    if isinstance(result, tuple) and len(result) == 2:
        num_labels, labels = result
    else:
        print("connectedComponents返回格式异常")
        return
    
    print(f"红色连通组件数量: {num_labels-1}")
    
    # 分析每个红色连通组件
    red_lines = []
    
    for label in range(1, num_labels):
        component_mask = (labels == label)
        
        # 计算连通组件的边界框
        y_coords, x_coords = np.where(component_mask)
        if len(y_coords) == 0:
            continue
            
        min_y, max_y = int(y_coords.min()), int(y_coords.max())
        min_x, max_x = int(x_coords.min()), int(x_coords.max())
        
        component_width = max_x - min_x + 1
        component_height = max_y - min_y + 1
        component_area = int(np.sum(component_mask))
        
        # 计算特征
        width_ratio = float(component_width) / float(width)
        aspect_ratio = float(component_width) / float(max(component_height, 1))
        y_center = float(min_y + max_y) / 2.0
        y_percent = y_center / float(height) * 100.0
        
        # 只考虑较长的红色区域作为线条标注
        if component_width >= width * 0.3:  # 至少30%宽度
            red_lines.append({
                'y_center': y_center,
                'y_percent': y_percent,
                'width': component_width,
                'height': component_height,
                'width_ratio': width_ratio,
                'aspect_ratio': aspect_ratio,
                'bbox': (min_x, min_y, max_x, max_y),
                'area': component_area
            })
            
            print(f"红色线条{len(red_lines)}: y={y_center:.0f}({y_percent:.1f}%), 宽度={component_width}({width_ratio:.1%}), 高度={component_height}, 宽高比={aspect_ratio:.1f}")
    
    # 按y坐标排序
    red_lines.sort(key=lambda x: x['y_center'])
    
    print(f"\n检测到 {len(red_lines)} 条红色标注线:")
    for i, line in enumerate(red_lines):
        print(f"  线条{i+1}: y={line['y_center']:.0f} ({line['y_percent']:.1f}%高度), 宽度={line['width']} ({line['width_ratio']:.1%})")
    
    # 分析原始图片在这些位置的黑色内容
    print(f"\n分析原始图片在红色标注位置的黑色内容:")
    
    original_gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
    black_mask_original = original_gray < 80
    
    correct_black_lines = []
    
    for i, red_line in enumerate(red_lines):
        y_center = red_line['y_center']
        bbox = red_line['bbox']
        min_x, min_y, max_x, max_y = bbox
        
        # 在红色标注区域查找黑色像素
        roi_black = black_mask_original[min_y:max_y+1, min_x:max_x+1]
        black_pixel_count = np.sum(roi_black)
        
        if black_pixel_count > 0:
            # 在ROI中找到黑色像素的精确位置
            roi_y_coords, roi_x_coords = np.where(roi_black)
            if len(roi_y_coords) > 0:
                # 转换回全图坐标
                global_y_coords = roi_y_coords + min_y
                global_x_coords = roi_x_coords + min_x
                
                actual_min_y = int(global_y_coords.min())
                actual_max_y = int(global_y_coords.max())
                actual_min_x = int(global_x_coords.min())
                actual_max_x = int(global_x_coords.max())
                
                actual_width = actual_max_x - actual_min_x + 1
                actual_height = actual_max_y - actual_min_y + 1
                actual_y_center = float(actual_min_y + actual_max_y) / 2.0
                actual_y_percent = actual_y_center / float(height) * 100.0
                actual_width_ratio = float(actual_width) / float(width)
                
                correct_black_lines.append({
                    'y_center': actual_y_center,
                    'y_percent': actual_y_percent,
                    'width': actual_width,
                    'height': actual_height,
                    'width_ratio': actual_width_ratio,
                    'bbox': (actual_min_x, actual_min_y, actual_max_x, actual_max_y),
                    'pixel_count': black_pixel_count
                })
                
                print(f"  对应黑色线条{i+1}: y={actual_y_center:.0f}({actual_y_percent:.1f}%), 宽度={actual_width}({actual_width_ratio:.1%}), 高度={actual_height}, 黑色像素={black_pixel_count}")
        else:
            print(f"  红色标注区域{i+1}中没有找到黑色像素")
    
    # 生成新的判断标准
    if len(correct_black_lines) >= 2:
        print(f"\n基于标注的新判断标准建议:")
        
        min_y_center = min(line['y_center'] for line in correct_black_lines)
        max_y_center = max(line['y_center'] for line in correct_black_lines)
        min_width = min(line['width'] for line in correct_black_lines)
        max_height = max(line['height'] for line in correct_black_lines)
        min_width_ratio = min(line['width_ratio'] for line in correct_black_lines)
        
        distance_between = max_y_center - min_y_center
        distance_percent = distance_between / float(height) * 100.0
        
        print(f"  两条线y位置: {min_y_center:.0f} 和 {max_y_center:.0f}")
        print(f"  两条线间距: {distance_between:.0f}像素 ({distance_percent:.1f}%高度)")
        print(f"  最小宽度: {min_width} ({min_width_ratio:.1%})")
        print(f"  最大高度: {max_height}")
        
        print(f"\n建议的长横线检测标准:")
        print(f"  1. 宽度至少: {min_width_ratio*0.8:.1%} (当前最小宽度的80%)")
        print(f"  2. 高度最多: {max_height + 10} 像素")
        print(f"  3. 两线间距至少: {distance_percent*0.5:.1f}% 高度")
        print(f"  4. y位置范围: {min_y_center/height*100:.1f}% - {max_y_center/height*100:.1f}% 高度")
    
    return correct_black_lines

def create_analysis_visualization(correct_lines):
    """创建分析可视化图像"""
    
    original_img = np.array(Image.open('templates/mb.png').convert('RGB'))
    pil_image = Image.fromarray(original_img)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # 绘制检测到的正确黑色线条
    for i, line in enumerate(correct_lines):
        bbox = line['bbox']
        min_x, min_y, max_x, max_y = bbox
        
        # 绘制绿色边界框表示正确的黑色线条位置
        draw.rectangle([min_x, min_y, max_x, max_y], outline='green', width=4)
        
        # 添加标签
        y_percent = line['y_percent']
        width_ratio = line['width_ratio']
        label_text = f"正确线条{i+1}: y={line['y_center']:.0f}({y_percent:.1f}%) W={width_ratio:.1%}"
        draw.text((min_x, min_y-20), label_text, fill='green', font=font)
    
    # 添加信息
    if len(correct_lines) >= 2:
        distance = abs(correct_lines[1]['y_center'] - correct_lines[0]['y_center'])
        distance_percent = distance / original_img.shape[0] * 100
        info_text = f"正确的两条长横线位置\n间距: {distance:.0f}px ({distance_percent:.1f}%高度)"
        draw.text((10, 10), info_text, fill='green', font=font)
    
    # 保存图像
    output_path = "correct_lines_analysis.png"
    pil_image.save(output_path)
    print(f"\n✓ 分析结果已保存到: {output_path}")

if __name__ == "__main__":
    print("🔍 分析mb88.png中的红色标注线...")
    correct_lines = analyze_red_lines_in_mb88()
    
    if correct_lines:
        create_analysis_visualization(correct_lines)
        print("\n🎉 分析完成！请查看生成的新判断标准建议。")
    else:
        print("\n❌ 分析失败，无法确定正确的长横线位置。")
