#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量检测 F:\标准规范要求\充电 目录下PDF文件的长黑横线
"""

import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
from pdf_feature_extractor import PDFFeatureExtractor
import logging
import json
from datetime import datetime

# 设置日志级别为INFO，减少DEBUG信息
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def batch_detect_charging_pdfs():
    """批量检测充电目录下的PDF文件"""
    
    charging_dir = r"F:\标准规范要求\充电"
    
    print(f"扫描目录: {charging_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(charging_dir):
        print(f"❌ 目录不存在: {charging_dir}")
        return
    
    # 查找所有PDF文件
    pdf_files = []
    for root, dirs, files in os.walk(charging_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                pdf_files.append(pdf_path)
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    if len(pdf_files) == 0:
        print("❌ 未找到PDF文件")
        return
    
    # 初始化特征提取器
    extractor = PDFFeatureExtractor()
    
    # 统计结果
    results = []
    success_count = 0
    total_pages = 0
    
    print(f"\n开始批量检测...")
    print(f"{'='*80}")
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n处理第 {i+1}/{len(pdf_files)} 个文件:")
        print(f"文件: {os.path.basename(pdf_path)}")
        
        try:
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            pages_with_feature = []
            
            # 检测每一页
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    
                    # 转换为图像
                    mat = fitz.Matrix(2.0, 2.0)  # 2倍缩放提高质量
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("ppm")
                    
                    # 转换为numpy数组
                    nparr = np.frombuffer(img_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # 检测第二特征
                    result = extractor.detect_mb_second_feature(image_rgb)
                    
                    total_pages += 1
                    
                    if result['has_second_feature']:
                        success_count += 1
                        pages_with_feature.append({
                            'page': page_num + 1,
                            'lines': result['long_lines'],
                            'distance': result['line_distance'],
                            'distance_ratio': result['line_distance_ratio']
                        })
                        print(f"  📄 第{page_num + 1}页: ✅ 检测到2条长黑横线")
                        
                        # 显示线条信息
                        for j, line in enumerate(result['long_lines']):
                            y_pos = line['y_center']
                            length_percent = line['width_ratio'] * 100
                            y_percent = y_pos / image_rgb.shape[0] * 100
                            print(f"    线条{j+1}: y={y_pos:.0f}({y_percent:.1f}%), 长度={length_percent:.1f}%宽度")
                        
                        distance_percent = result['line_distance_ratio'] * 100
                        print(f"    间距: {result['line_distance']:.0f}像素 ({distance_percent:.1f}%高度)")
                    
                except Exception as e:
                    print(f"  ❌ 第{page_num + 1}页处理失败: {str(e)}")
                    continue
            
            # 记录文件结果
            file_result = {
                'file_path': pdf_path,
                'file_name': os.path.basename(pdf_path),
                'total_pages': len(doc),
                'pages_with_feature': len(pages_with_feature),
                'success_pages': pages_with_feature,
                'success_rate': len(pages_with_feature) / len(doc) * 100 if len(doc) > 0 else 0
            }
            results.append(file_result)
            
            if pages_with_feature:
                print(f"✅ 文件总结: {len(pages_with_feature)}/{len(doc)} 页符合第二特征 ({file_result['success_rate']:.1f}%)")
            else:
                print(f"❌ 文件总结: 0/{len(doc)} 页符合第二特征")
            
            doc.close()
            
        except Exception as e:
            print(f"❌ 文件处理失败: {str(e)}")
            continue
    
    # 生成总结报告
    print(f"\n{'='*80}")
    print(f"批量检测完成!")
    print(f"{'='*80}")
    
    print(f"\n📊 总体统计:")
    print(f"  处理文件数: {len(pdf_files)}")
    print(f"  总页数: {total_pages}")
    print(f"  成功页数: {success_count}")
    print(f"  成功率: {success_count/total_pages*100:.1f}%" if total_pages > 0 else "  成功率: 0%")
    
    # 按成功页数排序显示文件结果
    results.sort(key=lambda x: x['pages_with_feature'], reverse=True)
    
    print(f"\n📋 文件检测结果 (按成功页数排序):")
    print(f"{'序号':<4} {'文件名':<40} {'成功页数':<8} {'总页数':<6} {'成功率':<8}")
    print(f"{'-'*4} {'-'*40} {'-'*8} {'-'*6} {'-'*8}")
    
    for i, result in enumerate(results):
        file_name = result['file_name']
        if len(file_name) > 37:
            file_name = file_name[:34] + "..."
        
        print(f"{i+1:<4} {file_name:<40} {result['pages_with_feature']:<8} {result['total_pages']:<6} {result['success_rate']:<7.1f}%")
    
    # 显示有成功检测的文件详情
    successful_files = [r for r in results if r['pages_with_feature'] > 0]
    
    if successful_files:
        print(f"\n🎉 有成功检测的文件详情:")
        for result in successful_files:
            print(f"\n📁 {result['file_name']}:")
            print(f"   总页数: {result['total_pages']}, 成功页数: {result['pages_with_feature']}")
            for page_info in result['success_pages']:
                print(f"   第{page_info['page']}页: 间距{page_info['distance']:.0f}像素 ({page_info['distance_ratio']*100:.1f}%高度)")
    else:
        print(f"\n❌ 没有文件检测到符合第二特征的页面")
    
    # 保存详细结果到JSON文件
    # 确保tests/data目录存在
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = data_dir / f"charging_pdfs_detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 准备JSON数据（去除不能序列化的numpy类型）
    json_results = []
    for result in results:
        json_result = {
            'file_path': result['file_path'],
            'file_name': result['file_name'],
            'total_pages': result['total_pages'],
            'pages_with_feature': result['pages_with_feature'],
            'success_rate': result['success_rate'],
            'success_pages': []
        }
        
        for page_info in result['success_pages']:
            json_page = {
                'page': page_info['page'],
                'distance': float(page_info['distance']),
                'distance_ratio': float(page_info['distance_ratio']),
                'lines': []
            }
            
            for line in page_info['lines']:
                json_line = {
                    'y_center': float(line['y_center']),
                    'length': int(line['length']),
                    'width_ratio': float(line['width_ratio']),
                    'y_percent': float(line['y_center']) / 1000 * 100  # 近似计算
                }
                json_page['lines'].append(json_line)
            
            json_result['success_pages'].append(json_page)
        
        json_results.append(json_result)
    
    # 保存结果
    summary_data = {
        'scan_time': datetime.now().isoformat(),
        'source_directory': charging_dir,
        'total_files': len(pdf_files),
        'total_pages': total_pages,
        'successful_pages': success_count,
        'success_rate': success_count/total_pages*100 if total_pages > 0 else 0,
        'files': json_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    print("批量检测充电目录下PDF文件的长黑横线")
    results = batch_detect_charging_pdfs()
