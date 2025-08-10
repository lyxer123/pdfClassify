#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分析mb10.png，特别关注25%高度附近的长黑横线
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def analyze_mb10_upper_region():
    """分析mb10.png上部区域寻找第二条长横线"""
    
    # 加载mb10.png
    mb10_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb10.png').convert('RGB'))
    print(f"mb10.png尺寸: {mb10_img.shape}")
    
    height, width = mb10_img.shape[:2]
    gray = cv2.cvtColor(mb10_img, cv2.COLOR_RGB2GRAY)
    black_mask = gray < 80
    
    print(f"总黑色像素数量: {np.sum(black_mask)}")
    
    # 重点分析25%高度附近的区域 (15% - 35%)
    target_y_percent = 25
    target_y = int(height * target_y_percent / 100)
    search_range_percent = 10  # ±10%
    
    y_start = max(0, int(height * (target_y_percent - search_range_percent) / 100))
    y_end = min(height, int(height * (target_y_percent + search_range_percent) / 100))
    
    print(f"\n🎯 重点分析25%高度附近区域:")
    print(f"目标位置: y={target_y} ({target_y_percent}%高度)")
    print(f"搜索范围: y={y_start}({y_start/height*100:.1f}%) 到 y={y_end}({y_end/height*100:.1f}%)")
    
    lines_in_range = []
    
    for y in range(y_start, y_end):
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
            total_length = sum(end - start + 1 for start, end in segments)
            max_segment_length = max(end - start + 1 for start, end in segments)
            max_segment_ratio = max_segment_length / width
            total_ratio = total_length / width
            
            # 记录所有有意义的线条（最长线段>=3%宽度）
            if max_segment_ratio >= 0.03:
                y_percent = y / height * 100
                lines_in_range.append({
                    'y': y,
                    'y_percent': y_percent,
                    'max_length': max_segment_length,
                    'max_ratio': max_segment_ratio,
                    'total_length': total_length,
                    'total_ratio': total_ratio,
                    'segment_count': len(segments),
                    'segments': segments
                })
    
    print(f"\n在目标区域发现 {len(lines_in_range)} 行有线条 (>=3%宽度)")
    
    if lines_in_range:
        # 按最长线段长度排序
        lines_in_range.sort(key=lambda x: x['max_length'], reverse=True)
        
        print(f"\n按最长线段长度排序的前20行:")
        for i, line in enumerate(lines_in_range[:20]):
            print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 最长={line['max_length']}({line['max_ratio']:.1%}), 总长={line['total_length']}({line['total_ratio']:.1%}), {line['segment_count']}段")
        
        # 寻找可能的长横线候选（>=10%宽度）
        strong_candidates = [line for line in lines_in_range if line['max_ratio'] >= 0.1]
        print(f"\n长度>=10%宽度的强候选: {len(strong_candidates)}条")
        
        for i, line in enumerate(strong_candidates):
            print(f"  强候选{i+1}: y={line['y']}({line['y_percent']:.1f}%): 最长={line['max_length']}({line['max_ratio']:.1%})")
        
        # 寻找可能的中等候选（>=5%宽度）
        medium_candidates = [line for line in lines_in_range if 0.05 <= line['max_ratio'] < 0.1]
        print(f"\n长度5%-10%宽度的中等候选: {len(medium_candidates)}条")
        
        for i, line in enumerate(medium_candidates[:10]):
            print(f"  中候选{i+1}: y={line['y']}({line['y_percent']:.1f}%): 最长={line['max_length']}({line['max_ratio']:.1%})")
        
        # 尝试合并相邻的行
        print(f"\n🔧 尝试合并相邻行形成更强的线条:")
        merged_candidates = merge_adjacent_lines(lines_in_range, width, height)
        
        return lines_in_range, merged_candidates
    
    return [], []

def merge_adjacent_lines(lines, width, height):
    """合并相邻的行来形成更强的线条"""
    
    # 按y坐标排序
    lines_by_y = sorted(lines, key=lambda x: x['y'])
    
    merged_candidates = []
    current_group = []
    
    for line in lines_by_y:
        if not current_group:
            current_group = [line]
        else:
            # 如果与当前组的最后一行相邻（差距<=5像素）
            if line['y'] - current_group[-1]['y'] <= 5:
                current_group.append(line)
            else:
                # 处理当前组
                if len(current_group) >= 2:  # 至少2行才认为是一个合并的线条
                    process_merged_group(current_group, merged_candidates, width, height)
                
                current_group = [line]
    
    # 处理最后一组
    if len(current_group) >= 2:
        process_merged_group(current_group, merged_candidates, width, height)
    
    # 按合并后的最大长度排序
    merged_candidates.sort(key=lambda x: x['max_length'], reverse=True)
    
    print(f"发现 {len(merged_candidates)} 个合并线条候选:")
    for i, candidate in enumerate(merged_candidates):
        y_percent = candidate['y_center'] / height * 100
        max_ratio = candidate['max_length'] / width * 100
        print(f"  合并候选{i+1}: y={candidate['y_center']:.0f}({y_percent:.1f}%), 高度={candidate['height']}, 最长={candidate['max_length']}({max_ratio:.1%}), {candidate['line_count']}行")
    
    return merged_candidates

def process_merged_group(group, merged_candidates, width, height):
    """处理一个合并组"""
    
    group_max_length = max(line['max_length'] for line in group)
    group_total_length = sum(line['total_length'] for line in group)
    group_y_start = group[0]['y']
    group_y_end = group[-1]['y']
    group_y_center = (group_y_start + group_y_end) / 2
    
    # 计算合并后的实际连续长度（在y_center行）
    center_y = int(group_y_center)
    if 0 <= center_y < height:
        # 这里可以进一步分析center_y行的实际连续长度
        pass
    
    merged_candidates.append({
        'y_center': group_y_center,
        'y_start': group_y_start,
        'y_end': group_y_end,
        'height': group_y_end - group_y_start + 1,
        'max_length': group_max_length,
        'total_length': group_total_length,
        'line_count': len(group),
        'max_ratio': group_max_length / width
    })

def create_analysis_visualization(image, lines_in_range, merged_candidates):
    """创建分析可视化"""
    
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 8)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    height, width = image.shape[:2]
    
    # 绘制已知的第二条线（y=1177）
    y_known = 1177
    draw.line([(0, y_known), (width, y_known)], fill='blue', width=3)
    draw.text((10, y_known - 25), "已知线条: y=1177 (80.8%宽)", fill='blue', font=font)
    
    # 绘制25%目标区域
    target_y = int(height * 0.25)
    draw.line([(0, target_y), (width, target_y)], fill='green', width=1)
    draw.text((10, target_y + 5), "目标25%高度", fill='green', font=small_font)
    
    # 绘制搜索范围
    y_start = int(height * 0.15)
    y_end = int(height * 0.35)
    draw.rectangle([(0, y_start), (width, y_end)], outline='lightgreen', width=2, fill=None)
    
    # 绘制找到的最强候选线条
    if merged_candidates:
        best_candidate = merged_candidates[0]
        y_center = int(best_candidate['y_center'])
        draw.line([(0, y_center), (width, y_center)], fill='red', width=3)
        
        y_percent = best_candidate['y_center'] / height * 100
        max_ratio = best_candidate['max_ratio'] * 100
        label = f"最佳候选: y={y_center}({y_percent:.1f}%) L={max_ratio:.1f}%"
        draw.text((10, y_center - 20), label, fill='red', font=font)
    
    # 添加分析信息
    info_lines = [
        "mb10.png上部区域分析",
        f"搜索范围: 15%-35%高度",
        f"找到候选: {len(merged_candidates)}个",
        f"已知下线: y=1177 (86.5%)"
    ]
    
    info_text = "\n".join(info_lines)
    draw.text((10, 10), info_text, fill='black', font=font)
    
    # 保存结果
    output_path = "mb10_upper_analysis.png"
    pil_image.save(output_path)
    print(f"\n✓ 上部区域分析可视化已保存到: {output_path}")

if __name__ == "__main__":
    print("重新分析mb10.png，寻找25%高度附近的第二条长横线")
    
    lines_in_range, merged_candidates = analyze_mb10_upper_region()
    
    # 加载图像用于可视化
    mb10_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb10.png').convert('RGB'))
    create_analysis_visualization(mb10_img, lines_in_range, merged_candidates)
    
    print(f"\n{'='*60}")
    print("分析总结:")
    
    if merged_candidates:
        best_candidate = merged_candidates[0]
        y_percent = best_candidate['y_center'] / mb10_img.shape[0] * 100
        max_ratio = best_candidate['max_ratio'] * 100
        
        print(f"🎯 最有希望的候选线条:")
        print(f"   位置: y={best_candidate['y_center']:.0f} ({y_percent:.1f}%高度)")
        print(f"   最长线段: {best_candidate['max_length']}像素 ({max_ratio:.1f}%宽度)")
        print(f"   高度跨度: {best_candidate['height']}像素")
        
        if max_ratio >= 15:
            print(f"✅ 发现足够长的候选线条！可能符合第二特征要求")
        else:
            print(f"⚠️  候选线条较短，可能需要进一步优化检测算法")
    else:
        print(f"❌ 在25%高度附近未发现明显的长横线候选")
    
    print(f"{'='*60}")
