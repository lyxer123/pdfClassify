#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用形态学操作增强mb10.png的线条检测
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def enhance_mb10_line_detection():
    """使用形态学操作增强mb10.png的线条检测"""
    
    # 加载mb10.png
    mb10_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb10.png').convert('RGB'))
    print(f"mb10.png尺寸: {mb10_img.shape}")
    
    height, width = mb10_img.shape[:2]
    gray = cv2.cvtColor(mb10_img, cv2.COLOR_RGB2GRAY)
    
    # 创建黑色区域的掩码
    black_mask = gray < 80
    print(f"原始黑色像素数量: {np.sum(black_mask)}")
    
    # 应用强力的水平形态学操作来连接断开的长横线
    print(f"\n🔧 应用形态学操作连接断开的线条...")
    
    # 第一轮：使用大的水平核连接远距离的线段
    horizontal_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 8, 1))  # 1/8宽度的水平核
    enhanced_mask1 = cv2.morphologyEx(black_mask.astype(np.uint8), cv2.MORPH_CLOSE, horizontal_kernel1)
    print(f"第一轮连接后黑色像素数量: {np.sum(enhanced_mask1)}")
    
    # 第二轮：使用中等核进一步连接
    horizontal_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 3))
    enhanced_mask2 = cv2.morphologyEx(enhanced_mask1, cv2.MORPH_CLOSE, horizontal_kernel2)
    print(f"第二轮连接后黑色像素数量: {np.sum(enhanced_mask2)}")
    
    # 第三轮：最终清理
    horizontal_kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    final_mask = cv2.morphologyEx(enhanced_mask2, cv2.MORPH_CLOSE, horizontal_kernel3)
    print(f"最终处理后黑色像素数量: {np.sum(final_mask)}")
    
    # 重新分析增强后的线条
    print(f"\n🔍 重新分析增强后的线条分布:")
    
    enhanced_lines = []
    
    for y in range(height):
        row = final_mask[y, :]
        
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
            
            # 记录长度>=10%宽度的线条
            if max_segment_ratio >= 0.1:
                y_percent = y / height * 100
                max_segment = max(segments, key=lambda x: x[1] - x[0])
                
                enhanced_lines.append({
                    'y': y,
                    'y_percent': y_percent,
                    'max_length': max_segment_length,
                    'max_ratio': max_segment_ratio,
                    'coords': (max_segment[0], y, max_segment[1], y),
                    'segment_count': len(segments)
                })
    
    print(f"增强后发现 {len(enhanced_lines)} 条长度>=10%宽度的线条")
    
    if enhanced_lines:
        # 按长度排序
        enhanced_lines.sort(key=lambda x: x['max_length'], reverse=True)
        
        print(f"\n增强后的线条列表:")
        for i, line in enumerate(enhanced_lines):
            print(f"  {i+1}. y={line['y']}({line['y_percent']:.1f}%): 长度={line['max_length']}({line['max_ratio']:.1%}), {line['segment_count']}段")
        
        # 寻找两条最主要且相距足够远的线条
        main_lines = []
        min_distance = height * 0.1  # 最小间距为10%高度
        
        for line in enhanced_lines:
            # 检查与已选线条的距离
            too_close = False
            for selected in main_lines:
                if abs(line['y'] - selected['y']) < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                main_lines.append(line)
                print(f"✅ 选择主要线条: y={line['y']}({line['y_percent']:.1f}%), 长度={line['max_length']}({line['max_ratio']:.1%})")
                if len(main_lines) == 2:
                    break
        
        # 创建可视化
        create_enhanced_visualization(mb10_img, black_mask, final_mask, main_lines)
        
        return main_lines
    
    return []

def create_enhanced_visualization(original_image, original_mask, enhanced_mask, main_lines):
    """创建增强效果的可视化对比"""
    
    height, width = original_image.shape[:2]
    
    # 创建三列对比图
    comparison_width = width * 3
    comparison_image = Image.new('RGB', (comparison_width, height), 'white')
    
    # 第一列：原始图像
    pil_original = Image.fromarray(original_image)
    comparison_image.paste(pil_original, (0, 0))
    
    # 第二列：原始掩码
    original_mask_rgb = np.stack([original_mask * 255] * 3, axis=-1)
    pil_original_mask = Image.fromarray(original_mask_rgb.astype(np.uint8))
    comparison_image.paste(pil_original_mask, (width, 0))
    
    # 第三列：增强后的掩码
    enhanced_mask_rgb = np.stack([enhanced_mask * 255] * 3, axis=-1)
    pil_enhanced_mask = Image.fromarray(enhanced_mask_rgb.astype(np.uint8))
    comparison_image.paste(pil_enhanced_mask, (width * 2, 0))
    
    draw = ImageDraw.Draw(comparison_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 添加标题
    draw.text((10, 10), "原始图像", fill='black', font=font)
    draw.text((width + 10, 10), "原始掩码", fill='black', font=font)
    draw.text((width * 2 + 10, 10), "增强后掩码", fill='black', font=font)
    
    # 在增强后的掩码上绘制检测到的主要线条
    for i, line in enumerate(main_lines):
        y = line['y']
        x1, y1, x2, y2 = line['coords']
        
        # 在第三列绘制红色线条
        draw.line([(width * 2 + x1, y1), (width * 2 + x2, y2)], fill='red', width=4)
        
        # 添加标签
        y_percent = line['y_percent']
        max_ratio = line['max_ratio'] * 100
        label = f"线条{i+1}: y={y}({y_percent:.1f}%) L={max_ratio:.1f}%"
        label_x = width * 2 + 10
        label_y = y + (15 if i == 0 else -25)
        
        draw.text((label_x, label_y), label, fill='red', font=small_font)
    
    # 添加结果总结
    result_text = f"检测结果: {len(main_lines)}条主要长横线"
    if len(main_lines) == 2:
        distance = abs(main_lines[1]['y'] - main_lines[0]['y'])
        distance_percent = distance / height * 100
        result_text += f"\n间距: {distance}px ({distance_percent:.1f}%高度)"
        result_color = 'green'
    else:
        result_color = 'red'
    
    draw.text((width * 2 + 10, height - 60), result_text, fill=result_color, font=small_font)
    
    # 保存结果
    output_path = "mb10_enhanced_comparison.png"
    comparison_image.save(output_path)
    print(f"\n✓ 增强效果对比图已保存到: {output_path}")

if __name__ == "__main__":
    print("使用形态学操作增强mb10.png的线条检测")
    
    main_lines = enhance_mb10_line_detection()
    
    print(f"\n{'='*60}")
    print("增强检测结果总结:")
    
    if len(main_lines) == 2:
        print(f"🎉 成功检测到两条主要长横线！")
        
        line1, line2 = main_lines[0], main_lines[1]
        if line1['y'] > line2['y']:
            line1, line2 = line2, line1
        
        print(f"  第一条线: y={line1['y']}({line1['y_percent']:.1f}%), 长度={line1['max_length']}({line1['max_ratio']:.1%})")
        print(f"  第二条线: y={line2['y']}({line2['y_percent']:.1f}%), 长度={line2['max_length']}({line2['max_ratio']:.1%})")
        
        distance = line2['y'] - line1['y']
        distance_percent = distance / 1360 * 100  # height
        print(f"  间距: {distance}像素 ({distance_percent:.1f}%高度)")
        
        # 检查是否符合第二特征要求
        line1_ok = line1['max_ratio'] >= 0.8  # >=80%宽度
        line2_ok = line2['max_ratio'] >= 0.8  # >=80%宽度
        distance_ok = distance_percent >= 60  # >=60%高度间距
        
        print(f"\n第二特征检查:")
        print(f"  第一条线长度>=80%: {'✅' if line1_ok else '❌'} ({line1['max_ratio']:.1%})")
        print(f"  第二条线长度>=80%: {'✅' if line2_ok else '❌'} ({line2['max_ratio']:.1%})")
        print(f"  间距>=60%高度: {'✅' if distance_ok else '❌'} ({distance_percent:.1f}%)")
        
        if line1_ok and line2_ok and distance_ok:
            print(f"🎉 mb10.png符合第二特征要求！")
        else:
            print(f"⚠️  mb10.png接近但不完全符合第二特征要求")
            
    elif len(main_lines) == 1:
        print(f"⚠️  仍然只检测到1条主要长横线")
        line = main_lines[0]
        print(f"  线条: y={line['y']}({line['y_percent']:.1f}%), 长度={line['max_length']}({line['max_ratio']:.1%})")
    else:
        print(f"❌ 增强后仍未检测到足够的长横线")
    
    print(f"{'='*60}")
