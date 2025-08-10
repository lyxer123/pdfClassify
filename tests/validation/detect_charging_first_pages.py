#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测 F:\标准规范要求\充电 目录下PDF文件的第一页长黑横线
"""

import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from main import PDFFeatureExtractor
import logging
import json
from datetime import datetime

# 设置日志级别为WARNING，减少输出信息
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def detect_charging_first_pages():
    """检测充电目录下PDF文件的第一页"""
    
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
    
    print(f"\n开始检测第一页...")
    print(f"{'='*100}")
    print(f"{'序号':<4} {'文件名':<50} {'检测结果':<10} {'详细信息'}")
    print(f"{'-'*4} {'-'*50} {'-'*10} {'-'*30}")
    
    for i, pdf_path in enumerate(pdf_files):
        file_name = os.path.basename(pdf_path)
        if len(file_name) > 47:
            display_name = file_name[:44] + "..."
        else:
            display_name = file_name
        
        try:
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                print(f"{i+1:<4} {display_name:<50} {'空文件':<10} 无页面")
                doc.close()
                continue
            
            # 只处理第一页
            page = doc.load_page(0)
            
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
            
            if result['has_second_feature']:
                success_count += 1
                
                # 获取线条信息
                line1, line2 = result['long_lines'][0], result['long_lines'][1]
                # 按y坐标排序
                if line1['y_center'] > line2['y_center']:
                    line1, line2 = line2, line1
                
                y1_percent = line1['y_center'] / image_rgb.shape[0] * 100
                y2_percent = line2['y_center'] / image_rgb.shape[0] * 100
                width1_percent = line1['width_ratio'] * 100
                width2_percent = line2['width_ratio'] * 100
                distance_percent = result['line_distance_ratio'] * 100
                
                detail_info = f"y1={y1_percent:.0f}%({width1_percent:.0f}%w) y2={y2_percent:.0f}%({width2_percent:.0f}%w) 间距{distance_percent:.0f}%"
                
                print(f"{i+1:<4} {display_name:<50} {'✅ 成功':<10} {detail_info}")
                
                # 记录结果
                file_result = {
                    'file_path': pdf_path,
                    'file_name': file_name,
                    'has_feature': True,
                    'line1': {
                        'y_center': float(line1['y_center']),
                        'y_percent': float(y1_percent),
                        'width_ratio': float(line1['width_ratio']),
                        'length': int(line1['length'])
                    },
                    'line2': {
                        'y_center': float(line2['y_center']),
                        'y_percent': float(y2_percent),
                        'width_ratio': float(line2['width_ratio']),
                        'length': int(line2['length'])
                    },
                    'distance': float(result['line_distance']),
                    'distance_ratio': float(result['line_distance_ratio'])
                }
            else:
                detail_info = f"原因: {result['reason'][:25]}..." if len(result['reason']) > 25 else result['reason']
                print(f"{i+1:<4} {display_name:<50} {'❌ 失败':<10} {detail_info}")
                
                # 记录结果
                file_result = {
                    'file_path': pdf_path,
                    'file_name': file_name,
                    'has_feature': False,
                    'detected_lines': result['detected_lines'],
                    'reason': result['reason']
                }
            
            results.append(file_result)
            doc.close()
            
        except Exception as e:
            error_msg = str(e)[:30] + "..." if len(str(e)) > 30 else str(e)
            print(f"{i+1:<4} {display_name:<50} {'❌ 错误':<10} {error_msg}")
            
            results.append({
                'file_path': pdf_path,
                'file_name': file_name,
                'has_feature': False,
                'error': str(e)
            })
            continue
    
    # 生成总结报告
    print(f"\n{'='*100}")
    print(f"检测完成!")
    print(f"{'='*100}")
    
    print(f"\n📊 检测统计:")
    print(f"  总文件数: {len(pdf_files)}")
    print(f"  成功检测到2条长黑横线: {success_count}")
    print(f"  成功率: {success_count/len(pdf_files)*100:.1f}%")
    
    # 显示成功的文件
    successful_files = [r for r in results if r.get('has_feature', False)]
    
    if successful_files:
        print(f"\n🎉 成功检测到2条长黑横线的文件 ({len(successful_files)}个):")
        print(f"{'序号':<4} {'文件名':<60} {'第一条线':<20} {'第二条线':<20} {'间距'}")
        print(f"{'-'*4} {'-'*60} {'-'*20} {'-'*20} {'-'*10}")
        
        for i, result in enumerate(successful_files):
            file_name = result['file_name']
            if len(file_name) > 57:
                file_name = file_name[:54] + "..."
            
            line1_info = f"y={result['line1']['y_percent']:.0f}%({result['line1']['width_ratio']*100:.0f}%w)"
            line2_info = f"y={result['line2']['y_percent']:.0f}%({result['line2']['width_ratio']*100:.0f}%w)"
            distance_info = f"{result['distance_ratio']*100:.0f}%h"
            
            print(f"{i+1:<4} {file_name:<60} {line1_info:<20} {line2_info:<20} {distance_info}")
    else:
        print(f"\n❌ 没有文件检测到符合第二特征的长黑横线")
    
    # 显示失败的文件统计
    failed_files = [r for r in results if not r.get('has_feature', False)]
    
    if failed_files:
        print(f"\n📋 未检测到长黑横线的文件分析:")
        
        # 按失败原因分组
        failure_reasons = {}
        for result in failed_files:
            if 'error' in result:
                reason = "文件错误"
            else:
                reason = result.get('reason', '未知原因')
                # 简化原因描述
                if '只检测到1条长黑线' in reason:
                    reason = "只有1条长黑线"
                elif '在预期位置未检测到长黑线' in reason:
                    reason = "未检测到长黑线"
                elif '检测到0条长黑线' in reason:
                    reason = "无长黑线"
            
            if reason not in failure_reasons:
                failure_reasons[reason] = []
            failure_reasons[reason].append(result['file_name'])
        
        for reason, files in failure_reasons.items():
            print(f"\n  {reason}: {len(files)}个文件")
            if len(files) <= 5:  # 如果文件不多，显示文件名
                for file_name in files:
                    display_name = file_name if len(file_name) <= 50 else file_name[:47] + "..."
                    print(f"    - {display_name}")
            else:
                print(f"    (文件数量较多，不逐一显示)")
    
    # 保存结果到JSON文件
    output_file = f"charging_first_pages_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    summary_data = {
        'scan_time': datetime.now().isoformat(),
        'source_directory': charging_dir,
        'total_files': len(pdf_files),
        'successful_files': success_count,
        'success_rate': success_count/len(pdf_files)*100 if len(pdf_files) > 0 else 0,
        'files': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    print("检测充电目录下PDF文件第一页的长黑横线")
    results = detect_charging_first_pages()
