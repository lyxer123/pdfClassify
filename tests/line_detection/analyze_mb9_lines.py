#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析mb9.png的线条分布，找出真实的长横线位置
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def analyze_mb9_lines():
    """分析mb9.png的线条分布"""
    
    # 加载mb9.png
    mb9_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb9.png').convert('RGB'))
    print(f"mb9.png尺寸: {mb9_img.shape}")
    
    height, width = mb9_img.shape[:2]
    gray = cv2.cvtColor(mb9_img, cv2.COLOR_RGB2GRAY)
    
    # 创建黑色区域的掩码
    black_mask = gray < 80
    print(f"黑色像素数量: {np.sum(black_mask)}")
    
    # 逐行分析，寻找长横线
    print(f"\n分析每一行的黑色像素分布:")
    
    potential_lines = []
    
    for y in range(height):
        row = black_mask[y, :]
        
        # 查找连续的黑色像素段
        segments = []
        start = None
        
        for x in range(width):
            if row[x]:  # 黑色像素
                if start is None:
                    start = x
            else:  # 非黑色像素
                if start is not None:
                    segments.append((start, x - 1))
                    start = None
        
        # 处理行末的情况
        if start is not None:
            segments.append((start, width - 1))
        
        # 分析这一行的线段
        if segments:
            total_length = sum(end - start + 1 for start, end in segments)
            max_segment_length = max(end - start + 1 for start, end in segments)
            max_segment_ratio = max_segment_length / width
            total_ratio = total_length / width
            
            # 记录可能的长横线（最长线段>=20%宽度 或 总长度>=30%宽度）
            if max_segment_ratio >= 0.2 or total_ratio >= 0.3:
                y_percent = y / height * 100
                potential_lines.append({
                    'y': y,
                    'y_percent': y_percent,
                    'segments': segments,
                    'max_length': max_segment_length,
                    'max_ratio': max_segment_ratio,
                    'total_length': total_length,
                    'total_ratio': total_ratio,
                    'segment_count': len(segments)
                })
                
                print(f"  y={y}({y_percent:.1f}%): {len(segments)}段, 最长={max_segment_length}({max_segment_ratio:.1%}), 总长={total_length}({total_ratio:.1%})")
    
    print(f"\n发现 {len(potential_lines)} 条潜在的长横线")
    
    # 按线条质量排序（优先考虑最长线段长度）
    potential_lines.sort(key=lambda x: x['max_length'], reverse=True)
    
    print(f"\n按最长线段长度排序的前10条线:")
    for i, line in enumerate(potential_lines[:10]):
        print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 最长={line['max_length']}({line['max_ratio']:.1%}), 总长={line['total_length']}({line['total_ratio']:.1%}), {line['segment_count']}段")
    
    # 寻找两条最主要的线条
    print(f"\n寻找两条最主要的长横线:")
    
    if len(potential_lines) >= 2:
        # 选择最长的两条，但要确保它们有足够的间距
        main_lines = []
        
        for line in potential_lines:
            # 检查与已选线条的距离
            too_close = False
            for selected in main_lines:
                if abs(line['y'] - selected['y']) < height * 0.1:  # 距离小于10%高度
                    too_close = True
                    break
            
            if not too_close:
                main_lines.append(line)
                if len(main_lines) == 2:
                    break
        
        if len(main_lines) == 2:
            line1, line2 = main_lines[0], main_lines[1]
            # 按y坐标排序
            if line1['y'] > line2['y']:
                line1, line2 = line2, line1
            
            distance = line2['y'] - line1['y']
            distance_percent = distance / height * 100
            
            print(f"  主要线条1: y={line1['y']}({line1['y_percent']:.1f}%), 最长线段={line1['max_length']}({line1['max_ratio']:.1%})")
            print(f"  主要线条2: y={line2['y']}({line2['y_percent']:.1f}%), 最长线段={line2['max_length']}({line2['max_ratio']:.1%})")
            print(f"  间距: {distance}像素 ({distance_percent:.1f}%高度)")
            
            # 创建可视化
            create_mb9_analysis_visualization(mb9_img, main_lines, potential_lines)
            
            return main_lines
        else:
            print(f"  只找到 {len(main_lines)} 条相距足够远的主要线条")
    else:
        print(f"  潜在线条数量不足: {len(potential_lines)}")
    
    # 即使没有找到理想的两条线，也创建可视化
    create_mb9_analysis_visualization(mb9_img, potential_lines[:2] if len(potential_lines) >= 2 else potential_lines, potential_lines)
    
    return potential_lines[:2] if len(potential_lines) >= 2 else potential_lines

def create_mb9_analysis_visualization(image, main_lines, all_lines):
    """创建mb9.png分析的可视化图像"""
    
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 8)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    height, width = image.shape[:2]
    
    # 绘制所有潜在线条（灰色）
    for line in all_lines:
        y = line['y']
        draw.line([(0, y), (width, y)], fill='lightgray', width=1)
    
    # 绘制主要线条（红色）
    for i, line in enumerate(main_lines):
        y = line['y']
        draw.line([(0, y), (width, y)], fill='red', width=3)
        
        # 标记主要线条
        label = f"主线{i+1}: y={y}({line['y_percent']:.1f}%)"
        draw.text((10, y - 20), label, fill='red', font=font)
        
        # 标记最长的线段
        max_segment = max(line['segments'], key=lambda x: x[1] - x[0])
        segment_start, segment_end = max_segment
        draw.line([(segment_start, y), (segment_end, y)], fill='blue', width=5)
    
    # 添加分析信息
    info_lines = [
        f"mb9.png线条分析",
        f"图像尺寸: {width}x{height}",
        f"潜在线条: {len(all_lines)}条",
        f"主要线条: {len(main_lines)}条"
    ]
    
    if len(main_lines) == 2:
        distance = abs(main_lines[1]['y'] - main_lines[0]['y'])
        distance_percent = distance / height * 100
        info_lines.append(f"间距: {distance}px ({distance_percent:.1f}%)")
    
    info_text = "\n".join(info_lines)
    draw.text((10, 10), info_text, fill='black', font=font)
    
    # 保存结果
    output_path = "mb9_analysis.png"
    pil_image.save(output_path)
    print(f"\n✓ mb9.png分析可视化已保存到: {output_path}")

if __name__ == "__main__":
    print("分析mb9.png的线条分布")
    main_lines = analyze_mb9_lines()
    
    if len(main_lines) == 2:
        print(f"\n🎉 成功识别mb9.png的两条主要长横线！")
    else:
        print(f"\n⚠️  mb9.png可能不符合两条长横线的模式")
