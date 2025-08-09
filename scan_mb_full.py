#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面扫描mb.png寻找所有可能的长横线
"""

import cv2
import numpy as np
from PIL import Image

def scan_mb_full():
    """全面扫描mb.png寻找所有长横线"""
    
    # 加载mb.png
    mb_img = np.array(Image.open('templates/mb.png').convert('RGB'))
    print(f"mb.png尺寸: {mb_img.shape}")
    
    height, width = mb_img.shape[:2]
    gray = cv2.cvtColor(mb_img, cv2.COLOR_RGB2GRAY)
    black_mask = gray < 80
    
    print(f"总黑色像素数量: {np.sum(black_mask)}")
    
    # 扫描整个图像
    print(f"\n扫描整个图像寻找长横线 (阈值>=5%宽度):")
    
    all_lines = []
    
    for y in range(height):
        row = black_mask[y, :]
        
        # 查找连续的黑色像素段
        segments = []
        start = None
        
        for x in range(width):
            if row[x]:
                if start is None:
                    start = x
            else:
                if start is not None:
                    segments.append((start, x - 1))
                    start = None
        
        if start is not None:
            segments.append((start, width - 1))
        
        # 分析这一行的线段
        if segments:
            max_segment_length = max(end - start + 1 for start, end in segments)
            max_segment_ratio = max_segment_length / width
            
            # 记录所有有意义的线条（最长线段>=5%宽度）
            if max_segment_ratio >= 0.05:
                y_percent = y / height * 100
                all_lines.append({
                    'y': y,
                    'y_percent': y_percent,
                    'max_length': max_segment_length,
                    'max_ratio': max_segment_ratio,
                    'segment_count': len(segments)
                })
    
    print(f"发现 {len(all_lines)} 行有>=5%宽度的线条")
    
    # 按位置分组显示
    print(f"\n按位置区间分组:")
    
    # 分成几个区间
    ranges = [
        (0, height * 0.2, "上部 (0-20%)"),
        (height * 0.2, height * 0.4, "中上 (20-40%)"), 
        (height * 0.4, height * 0.6, "中部 (40-60%)"),
        (height * 0.6, height * 0.8, "中下 (60-80%)"),
        (height * 0.8, height, "下部 (80-100%)")
    ]
    
    for start_y, end_y, name in ranges:
        lines_in_range = [line for line in all_lines if start_y <= line['y'] < end_y]
        print(f"\n{name}: {len(lines_in_range)} 条线")
        
        if lines_in_range:
            # 显示最长的几条线
            lines_in_range.sort(key=lambda x: x['max_length'], reverse=True)
            for i, line in enumerate(lines_in_range[:5]):  # 显示前5条
                print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 长度={line['max_length']}({line['max_ratio']:.1%}), {line['segment_count']}段")
    
    # 找出最长的几条线
    print(f"\n全图最长的10条线:")
    all_lines.sort(key=lambda x: x['max_length'], reverse=True)
    
    for i, line in enumerate(all_lines[:10]):
        print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 长度={line['max_length']}({line['max_ratio']:.1%}), {line['segment_count']}段")
    
    # 寻找可能的第二条主线
    print(f"\n寻找可能的第二条主线 (除了第一条线y=359):")
    
    # 排除y=359附近的线条
    exclude_range = 30  # 排除±30像素范围
    potential_second_lines = []
    
    for line in all_lines:
        if abs(line['y'] - 359) > exclude_range:
            potential_second_lines.append(line)
    
    # 按长度排序
    potential_second_lines.sort(key=lambda x: x['max_length'], reverse=True)
    
    print(f"排除第一条线后，剩余 {len(potential_second_lines)} 条候选线:")
    for i, line in enumerate(potential_second_lines[:10]):
        print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 长度={line['max_length']}({line['max_ratio']:.1%}), {line['segment_count']}段")
    
    return all_lines

if __name__ == "__main__":
    print("全面扫描mb.png寻找所有长横线")
    all_lines = scan_mb_full()
