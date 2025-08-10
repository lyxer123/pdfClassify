#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化形态学操作后的连通组件结果
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def visualize_morphology_components():
    """可视化形态学操作后的连通组件"""
    
    # 加载模板图片
    template_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb.png').convert('RGB'))
    print(f"图片尺寸: {template_img.shape}")
    
    height, width = template_img.shape[:2]
    gray = cv2.cvtColor(template_img, cv2.COLOR_RGB2GRAY)
    
    # 创建黑色区域的掩码
    black_mask = gray < 80
    
    # 进行形态学操作
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 10, 1))
    black_mask_connected = cv2.morphologyEx(black_mask.astype(np.uint8), cv2.MORPH_CLOSE, horizontal_kernel)
    
    horizontal_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 3))
    black_mask_connected = cv2.morphologyEx(black_mask_connected, cv2.MORPH_CLOSE, horizontal_kernel2)
    
    # 连通组件分析
    result = cv2.connectedComponents(black_mask_connected)
    if isinstance(result, tuple) and len(result) == 2:
        num_labels, labels = result
    else:
        print("connectedComponents返回格式异常")
        return
    
    print(f"连通组件数量: {num_labels-1}")
    
    # 创建PIL图像用于绘制
    pil_image = Image.fromarray(template_img)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 8)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 分析所有连通组件
    all_components = []
    
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
        
        width_ratio = float(component_width) / float(width)
        y_center = float(min_y + max_y) / 2.0
        y_percent = y_center / float(height) * 100.0
        aspect_ratio = float(component_width) / float(max(component_height, 1))
        
        # 只保存大组件（宽度≥10%）
        if width_ratio >= 0.1:
            all_components.append({
                'label': label,
                'bbox': (min_x, min_y, max_x, max_y),
                'y_center': y_center,
                'y_percent': y_percent,
                'width': component_width,
                'height': component_height,
                'width_ratio': width_ratio,
                'aspect_ratio': aspect_ratio,
                'area': component_area
            })
    
    print(f"大连通组件数量: {len(all_components)}")
    
    # 定义颜色
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    # 绘制所有大组件
    for i, comp in enumerate(all_components):
        min_x, min_y, max_x, max_y = comp['bbox']
        color = colors[i % len(colors)]
        
        # 检查是否满足当前的筛选条件
        in_upper_range = (20.0 <= comp['y_percent'] <= 35.0)
        in_lower_range = (80.0 <= comp['y_percent'] <= 95.0)
        
        meets_criteria = (
            comp['width_ratio'] >= 0.2 and
            comp['height'] <= 50 and
            comp['aspect_ratio'] >= 5 and
            (in_upper_range or in_lower_range)
        )
        
        # 如果满足条件，用粗线绘制；否则用细线
        line_width = 4 if meets_criteria else 2
        
        # 绘制边界框
        draw.rectangle([min_x, min_y, max_x, max_y], outline=color, width=line_width)
        
        # 添加标签
        y_pos = comp['y_center']
        width_pct = comp['width_ratio'] * 100
        
        label_text = f"C{i+1}: y={y_pos:.0f}({comp['y_percent']:.1f}%)"
        detail_text = f"W={width_pct:.1f}% H={comp['height']} AR={comp['aspect_ratio']:.1f}"
        status_text = "✓" if meets_criteria else "✗"
        
        # 标签位置
        label_x = min_x
        label_y = min_y - 35
        
        # 确保标签在图像范围内
        label_x = max(0, min(label_x, width - 200))
        label_y = max(0, label_y)
        
        draw.text((label_x, label_y), label_text, fill=color, font=font)
        draw.text((label_x, label_y + 12), detail_text, fill=color, font=small_font)
        draw.text((label_x, label_y + 22), status_text, fill=color, font=font)
        
        print(f"组件{i+1}: y={y_pos:.0f}({comp['y_percent']:.1f}%), 宽度={comp['width']}({width_pct:.1f}%), 高度={comp['height']}, 满足条件={meets_criteria}")
    
    # 添加期望线条位置（黄色虚线）
    expected_y1, expected_y2 = 359, 1245
    draw.line([(0, expected_y1), (width, expected_y1)], fill='yellow', width=2)
    draw.line([(0, expected_y2), (width, expected_y2)], fill='yellow', width=2)
    draw.text((10, expected_y1-20), f"期望线条1: y={expected_y1}", fill='yellow', font=font)
    draw.text((10, expected_y2-20), f"期望线条2: y={expected_y2}", fill='yellow', font=font)
    
    # 添加标题信息
    title_text = f"形态学操作后的连通组件分析\n{len(all_components)}个大组件，粗线=满足条件，细线=不满足条件\n黄色线=期望位置"
    draw.text((10, 10), title_text, fill='black', font=font)
    
    # 保存图像
    output_path = "hengxian5.png"
    pil_image.save(output_path)
    print(f"\n✓ 可视化结果已保存到: {output_path}")
    
    # 分析第二条线的问题
    print(f"\n第二条线分析:")
    print(f"期望位置: y≈{expected_y2} (86.7%高度)")
    
    components_near_second = []
    for comp in all_components:
        if abs(comp['y_center'] - expected_y2) <= 100:  # 在100像素范围内
            components_near_second.append(comp)
    
    if components_near_second:
        print(f"在期望位置附近找到 {len(components_near_second)} 个组件:")
        for comp in components_near_second:
            print(f"  y={comp['y_center']:.0f}, 宽度={comp['width_ratio']*100:.1f}%, 高度={comp['height']}")
        
        # 计算如果合并这些组件会怎样
        if len(components_near_second) > 1:
            all_x_coords = []
            all_y_coords = []
            for comp in components_near_second:
                min_x, min_y, max_x, max_y = comp['bbox']
                all_x_coords.extend([min_x, max_x])
                all_y_coords.extend([min_y, max_y])
            
            merged_width = max(all_x_coords) - min(all_x_coords) + 1
            merged_height = max(all_y_coords) - min(all_y_coords) + 1
            merged_width_ratio = merged_width / width * 100
            
            print(f"如果合并这些组件:")
            print(f"  合并后宽度: {merged_width} ({merged_width_ratio:.1f}%)")
            print(f"  合并后高度: {merged_height}")
    else:
        print("在期望位置附近没有找到组件")

if __name__ == "__main__":
    visualize_morphology_components()
