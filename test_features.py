# -*- coding: utf-8 -*-
"""
特征提取测试脚本
基于mb6.png模板的特征提取和可视化
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pdf_processor import PDFProcessor
import os

def visualize_features(image, features, output_path="feature_visualization.png"):
    """
    可视化特征提取结果
    
    Args:
        image: 原始图像
        features: 提取的特征
        output_path: 输出路径
    """
    # 创建图像副本用于标注
    vis_image = image.copy()
    height, width = image.shape[:2]
    
    # 标注区域
    regions = features.get('regions', {})
    if 'upper' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['upper']['y']), 
                     (width, regions['upper']['y'] + regions['upper']['height']), 
                     (255, 0, 0), 2)
        cv2.putText(vis_image, 'Upper Region', 
                   (10, regions['upper']['y'] + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    if 'middle' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['middle']['y']), 
                     (width, regions['middle']['y'] + regions['middle']['height']), 
                     (0, 255, 0), 2)
        cv2.putText(vis_image, 'Middle Region', 
                   (10, regions['middle']['y'] + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    if 'lower' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['lower']['y']), 
                     (width, regions['lower']['y'] + regions['lower']['height']), 
                     (0, 0, 255), 2)
        cv2.putText(vis_image, 'Lower Region', 
                   (10, regions['lower']['y'] + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # 标注关键框
    key_boxes = features.get('key_boxes', {})
    for box_name, box_info in key_boxes.items():
        x, y, w, h = box_info['x'], box_info['y'], box_info['width'], box_info['height']
        cv2.rectangle(vis_image, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(vis_image, box_name, 
                   (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    # 标注检测到的线条
    lines = features.get('lines', {})
    if 'first_line' in lines:
        rho, theta = lines['first_line']
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(vis_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(vis_image, 'First Line', (x1 + 10, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    if 'second_line' in lines:
        rho, theta = lines['second_line']
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(vis_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.putText(vis_image, 'Second Line', (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
    
    # 保存可视化结果
    cv2.imwrite(output_path, vis_image)
    print(f"可视化结果已保存到: {output_path}")

def print_feature_analysis(features):
    """
    打印特征分析结果
    
    Args:
        features: 提取的特征
    """
    print("=" * 60)
    print("特征提取分析结果")
    print("=" * 60)
    
    # 颜色特征
    print("\n【颜色特征】")
    print(f"白色背景占比: {features.get('white_ratio', 0):.3f} ({features.get('white_ratio', 0)*100:.1f}%)")
    print(f"黑色文字占比: {features.get('black_ratio', 0):.3f} ({features.get('black_ratio', 0)*100:.1f}%)")
    
    # 区域信息
    print("\n【区域信息】")
    regions = features.get('regions', {})
    for region_name, region_info in regions.items():
        print(f"{region_name}: y={region_info['y']}, height={region_info['height']}")
    
    # 关键框信息
    print("\n【关键框信息】")
    key_boxes = features.get('key_boxes', {})
    for box_name, box_info in key_boxes.items():
        print(f"{box_name}: x={box_info['x']}, y={box_info['y']}, w={box_info['width']}, h={box_info['height']}")
    
    # 关键词验证
    print("\n【关键词验证】")
    keywords = features.get('keywords', {})
    for keyword, found in keywords.items():
        status = "✓" if found else "✗"
        print(f"{keyword}: {status}")
    
    # 线条检测
    print("\n【线条检测】")
    lines = features.get('lines', {})
    for line_name, line_info in lines.items():
        if isinstance(line_info, tuple):
            print(f"{line_name}: rho={line_info[0]:.2f}, theta={line_info[1]:.2f}")
        else:
            status = "✓" if line_info else "✗"
            print(f"{line_name}: {status}")
    
    # 比例信息
    print("\n【区域比例】")
    proportions = features.get('proportions', {})
    for prop_name, prop_value in proportions.items():
        print(f"{prop_name}: {prop_value:.1f}%")
    
    # 位置关系
    print("\n【位置关系】")
    positions = features.get('positions', {})
    for pos_name, pos_value in positions.items():
        status = "✓" if pos_value else "✗"
        print(f"{pos_name}: {status}")
    
    # 内容约束
    print("\n【内容约束】")
    content_constraints = features.get('content_constraints', {})
    for constraint_name, constraint_value in content_constraints.items():
        status = "✓" if constraint_value else "✗"
        print(f"{constraint_name}: {status}")

def main():
    """主函数"""
    print("开始测试特征提取功能...")
    
    # 检查模板文件
    template_path = "mb6.png"
    if not os.path.exists(template_path):
        print(f"错误: 模板文件 {template_path} 不存在")
        return
    
    # 初始化PDF处理器
    try:
        processor = PDFProcessor(template_path=template_path)
        print("PDF处理器初始化成功")
    except Exception as e:
        print(f"PDF处理器初始化失败: {e}")
        return
    
    # 加载模板图像
    template_image = cv2.imread(template_path)
    if template_image is None:
        print(f"错误: 无法读取模板图像 {template_path}")
        return
    
    print(f"模板图像大小: {template_image.shape[1]}x{template_image.shape[0]}")
    
    # 提取特征
    print("\n正在提取特征...")
    features = processor._extract_features(template_image)
    
    # 打印特征分析
    print_feature_analysis(features)
    
    # 验证特征
    print("\n【模板验证】")
    is_valid = processor._validate_features(features)
    status = "✓ 通过" if is_valid else "✗ 不通过"
    print(f"模板特征验证: {status}")
    
    # 计算详细匹配度
    print("\n【详细匹配度分析】")
    validation_score = 0
    max_score = 0
    
    # 颜色特征
    max_score += 20
    white_ratio = features.get('white_ratio', 0)
    black_ratio = features.get('black_ratio', 0)
    color_score = 0
    if white_ratio > 0.85:
        color_score += 10
    if black_ratio > 0.005:
        color_score += 10
    validation_score += color_score
    print(f"颜色特征 ({color_score}/20): 白底{white_ratio*100:.1f}% 黑字{black_ratio*100:.1f}%")
    
    # 区域检测
    max_score += 15
    regions = features.get('regions', {})
    region_score = 15 if len(regions) >= 3 else (10 if len(regions) >= 2 else 0)
    validation_score += region_score
    print(f"区域检测 ({region_score}/15): 检测到{len(regions)}/3个区域")
    
    # 关键框检测
    max_score += 15
    key_boxes = features.get('key_boxes', {})
    box_count = len(key_boxes)
    box_score = 15 if box_count >= 6 else (10 if box_count >= 4 else (5 if box_count >= 2 else 0))
    validation_score += box_score
    print(f"关键框检测 ({box_score}/15): 检测到{box_count}/6个关键框")
    
    # 关键词验证
    max_score += 20
    keywords = features.get('keywords', {})
    keyword_score = 0
    if keywords.get('upper_has_standard', False):
        keyword_score += 10
    if keywords.get('lower_has_publish', False):
        keyword_score += 10
    validation_score += keyword_score
    print(f"关键词验证 ({keyword_score}/20): 标准{'✓' if keywords.get('upper_has_standard', False) else '✗'} 发布{'✓' if keywords.get('lower_has_publish', False) else '✗'}")
    
    # 位置关系
    max_score += 15
    positions = features.get('positions', {})
    position_score = 0
    if positions.get('box1_right_aligned', False):
        position_score += 5
    if positions.get('box3_right_aligned', False):
        position_score += 5
    if positions.get('box6_centered', False):
        position_score += 5
    validation_score += position_score
    print(f"位置关系 ({position_score}/15): 符合标准的位置关系")
    
    # 内容约束
    max_score += 15
    content_constraints = features.get('content_constraints', {})
    content_score = 15 if content_constraints.get('box4_multiple_lines', False) else 0
    validation_score += content_score
    print(f"内容约束 ({content_score}/15): 多行文本检测")
    
    # 总体匹配度
    match_percentage = (validation_score / max_score) * 100 if max_score > 0 else 0
    print(f"\n总体匹配度: {validation_score}/{max_score} = {match_percentage:.1f}%")
    print(f"验证阈值: 70% {'(通过)' if match_percentage >= 70 else '(不通过)'}")
    
    # 可视化特征
    print("\n正在生成可视化结果...")
    visualize_features(template_image, features)
    
    print("\n特征提取测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
