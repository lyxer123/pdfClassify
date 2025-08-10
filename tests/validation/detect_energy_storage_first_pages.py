#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测 F:\标准规范要求\储能 目录下PDF文件的第一页
结合第一特征（白色背景+黑色文字）和第二特征（两条长黑横线）进行综合检测
"""

import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
from main import PDFFeatureExtractor
import logging
import json
from datetime import datetime

# 设置日志级别为WARNING，减少输出信息
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def detect_energy_storage_first_pages():
    """检测储能目录下PDF文件的第一页，结合第一特征和第二特征"""
    
    energy_storage_dir = r"F:\标准规范要求\储能"
    
    print(f"扫描目录: {energy_storage_dir}")
    print("🔍 结合第一特征（白色背景+黑色文字）和第二特征（两条长黑横线）进行综合检测")
    
    # 检查目录是否存在
    if not os.path.exists(energy_storage_dir):
        print(f"❌ 目录不存在: {energy_storage_dir}")
        return
    
    # 查找所有PDF文件
    pdf_files = []
    for root, dirs, files in os.walk(energy_storage_dir):
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
    both_features_count = 0  # 同时具有两个特征
    first_feature_only_count = 0  # 仅第一特征
    second_feature_only_count = 0  # 仅第二特征
    no_features_count = 0  # 无特征
    
    print(f"\n开始综合检测第一页...")
    print(f"{'='*120}")
    print(f"{'序号':<4} {'文件名':<45} {'第一特征':<10} {'第二特征':<10} {'综合结果':<10} {'详细信息'}")
    print(f"{'-'*4} {'-'*45} {'-'*10} {'-'*10} {'-'*10} {'-'*40}")
    
    for i, pdf_path in enumerate(pdf_files):
        file_name = os.path.basename(pdf_path)
        if len(file_name) > 42:
            display_name = file_name[:39] + "..."
        else:
            display_name = file_name
        
        try:
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                print(f"{i+1:<4} {display_name:<45} {'--':<10} {'--':<10} {'空文件':<10} 无页面")
                results.append({
                    'file_path': pdf_path,
                    'file_name': file_name,
                    'has_first_feature': False,
                    'has_second_feature': False,
                    'has_both_features': False,
                    'error': '空文件'
                })
                doc.close()
                no_features_count += 1
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
            
            # 检测第一特征（颜色特征）
            color_features = extractor.analyze_color_features(image_rgb)
            has_first_feature = extractor.check_standard_compliance(color_features)
            
            # 检测第二特征（两条长黑横线）
            second_feature_result = extractor.detect_mb_second_feature(image_rgb)
            has_second_feature = second_feature_result['has_second_feature']
            
            # 综合判断
            has_both_features = has_first_feature and has_second_feature
            
            # 更新统计
            if has_both_features:
                both_features_count += 1
                overall_result = "✅ 双特征"
            elif has_first_feature:
                first_feature_only_count += 1
                overall_result = "🔵 仅第一"
            elif has_second_feature:
                second_feature_only_count += 1
                overall_result = "🔴 仅第二"
            else:
                no_features_count += 1
                overall_result = "❌ 无特征"
            
            # 显示状态
            first_status = "✅ 通过" if has_first_feature else "❌ 失败"
            second_status = "✅ 通过" if has_second_feature else "❌ 失败"
            
            # 详细信息
            if has_both_features:
                line1, line2 = second_feature_result['long_lines'][0], second_feature_result['long_lines'][1]
                if line1['y_center'] > line2['y_center']:
                    line1, line2 = line2, line1
                y1_percent = line1['y_center'] / image_rgb.shape[0] * 100
                y2_percent = line2['y_center'] / image_rgb.shape[0] * 100
                detail_info = f"白底:{color_features['white_bg_ratio']:.2f} 横线:{y1_percent:.0f}%,{y2_percent:.0f}%"
            elif has_first_feature:
                detail_info = f"白底:{color_features['white_bg_ratio']:.2f} 黑字:{color_features['black_text_ratio']:.3f}"
            elif has_second_feature:
                line1, line2 = second_feature_result['long_lines'][0], second_feature_result['long_lines'][1]
                if line1['y_center'] > line2['y_center']:
                    line1, line2 = line2, line1
                y1_percent = line1['y_center'] / image_rgb.shape[0] * 100
                y2_percent = line2['y_center'] / image_rgb.shape[0] * 100
                detail_info = f"横线位置:{y1_percent:.0f}%,{y2_percent:.0f}%"
            else:
                detail_info = f"白底:{color_features['white_bg_ratio']:.2f} 线条:{second_feature_result['detected_lines']}"
            
            print(f"{i+1:<4} {display_name:<45} {first_status:<10} {second_status:<10} {overall_result:<10} {detail_info[:35]}")
            
            # 记录完整结果
            file_result = {
                'file_path': pdf_path,
                'file_name': file_name,
                'has_first_feature': has_first_feature,
                'has_second_feature': has_second_feature,
                'has_both_features': has_both_features,
                'first_feature_details': {
                    'white_bg_ratio': float(color_features['white_bg_ratio']),
                    'black_text_ratio': float(color_features['black_text_ratio']),
                    'contrast': float(color_features['contrast']),
                    'brightness': float(sum(color_features['mean_rgb']) / 3),
                    'colored_text_ratio': float(color_features['colored_text_ratio'])
                },
                'second_feature_details': second_feature_result
            }
            
            # 如果有第二特征，添加线条详细信息
            if has_second_feature:
                line1, line2 = second_feature_result['long_lines'][0], second_feature_result['long_lines'][1]
                if line1['y_center'] > line2['y_center']:
                    line1, line2 = line2, line1
                
                file_result['line_details'] = {
                    'line1': {
                        'y_center': float(line1['y_center']),
                        'y_percent': float(line1['y_center'] / image_rgb.shape[0] * 100),
                        'width_ratio': float(line1['width_ratio']),
                        'length': int(line1['length'])
                    },
                    'line2': {
                        'y_center': float(line2['y_center']),
                        'y_percent': float(line2['y_center'] / image_rgb.shape[0] * 100),
                        'width_ratio': float(line2['width_ratio']),
                        'length': int(line2['length'])
                    },
                    'distance': float(second_feature_result['line_distance']),
                    'distance_ratio': float(second_feature_result['line_distance_ratio'])
                }
            
            results.append(file_result)
            doc.close()
            
        except Exception as e:
            error_msg = str(e)[:30] + "..." if len(str(e)) > 30 else str(e)
            print(f"{i+1:<4} {display_name:<45} {'❌ 错误':<10} {'❌ 错误':<10} {'❌ 错误':<10} {error_msg}")
            
            results.append({
                'file_path': pdf_path,
                'file_name': file_name,
                'has_first_feature': False,
                'has_second_feature': False,
                'has_both_features': False,
                'error': str(e)
            })
            no_features_count += 1
            continue
    
    # 生成综合检测报告
    print(f"\n{'='*120}")
    print(f"储能PDF综合特征检测完成!")
    print(f"{'='*120}")
    
    print(f"\n📊 综合检测统计:")
    print(f"  总文件数: {len(pdf_files)}")
    print(f"  双特征（第一+第二）: {both_features_count} ({both_features_count/len(pdf_files)*100:.1f}%)")
    print(f"  仅第一特征（白底黑字）: {first_feature_only_count} ({first_feature_only_count/len(pdf_files)*100:.1f}%)")
    print(f"  仅第二特征（双横线）: {second_feature_only_count} ({second_feature_only_count/len(pdf_files)*100:.1f}%)")
    print(f"  无特征: {no_features_count} ({no_features_count/len(pdf_files)*100:.1f}%)")
    
    # 显示双特征文件
    both_features_files = [r for r in results if r.get('has_both_features', False)]
    if both_features_files:
        print(f"\n🎉 同时具有双特征的标准文档 ({len(both_features_files)}个):")
        print(f"{'序号':<4} {'文件名':<50} {'白底比例':<10} {'横线位置':<15} {'综合评分'}")
        print(f"{'-'*4} {'-'*50} {'-'*10} {'-'*15} {'-'*10}")
        
        for i, result in enumerate(both_features_files):
            file_name = result['file_name']
            if len(file_name) > 47:
                file_name = file_name[:44] + "..."
            
            white_ratio = result['first_feature_details']['white_bg_ratio']
            line1_y = result['line_details']['line1']['y_percent']
            line2_y = result['line_details']['line2']['y_percent']
            line_info = f"{line1_y:.0f}%,{line2_y:.0f}%"
            
            # 综合评分（白底比例*0.4 + 横线质量*0.6）
            line_quality = (result['line_details']['line1']['width_ratio'] + result['line_details']['line2']['width_ratio']) / 2
            score = white_ratio * 0.4 + line_quality * 0.6
            
            print(f"{i+1:<4} {file_name:<50} {white_ratio:.2f:<10} {line_info:<15} {score:.2f}")
    else:
        print(f"\n❌ 没有文件同时具有双特征")
    
    # 显示仅第一特征文件
    first_only_files = [r for r in results if r.get('has_first_feature', False) and not r.get('has_second_feature', False)]
    if first_only_files:
        print(f"\n🔵 仅具有第一特征（颜色特征）的文件 ({len(first_only_files)}个):")
        print(f"{'序号':<4} {'文件名':<55} {'白底比例':<10} {'黑字比例':<10} {'对比度'}")
        print(f"{'-'*4} {'-'*55} {'-'*10} {'-'*10} {'-'*8}")
        
        for i, result in enumerate(first_only_files):
            file_name = result['file_name']
            if len(file_name) > 52:
                file_name = file_name[:49] + "..."
            
            white_ratio = result['first_feature_details']['white_bg_ratio']
            black_ratio = result['first_feature_details']['black_text_ratio']
            contrast = result['first_feature_details']['contrast']
            
            print(f"{i+1:<4} {file_name:<55} {white_ratio:.2f:<10} {black_ratio:.3f:<10} {contrast:.1f}")
    
    # 显示仅第二特征文件
    second_only_files = [r for r in results if not r.get('has_first_feature', False) and r.get('has_second_feature', False)]
    if second_only_files:
        print(f"\n🔴 仅具有第二特征（横线特征）的文件 ({len(second_only_files)}个):")
        print(f"{'序号':<4} {'文件名':<55} {'横线位置':<15} {'横线长度'}")
        print(f"{'-'*4} {'-'*55} {'-'*15} {'-'*10}")
        
        for i, result in enumerate(second_only_files):
            file_name = result['file_name']
            if len(file_name) > 52:
                file_name = file_name[:49] + "..."
            
            line1_y = result['line_details']['line1']['y_percent']
            line2_y = result['line_details']['line2']['y_percent']
            line_info = f"{line1_y:.0f}%,{line2_y:.0f}%"
            line1_w = result['line_details']['line1']['width_ratio']
            line2_w = result['line_details']['line2']['width_ratio']
            width_info = f"{line1_w:.1%},{line2_w:.1%}"
            
            print(f"{i+1:<4} {file_name:<55} {line_info:<15} {width_info}")
    
    # 显示无特征文件
    no_features_files = [r for r in results if not r.get('has_first_feature', False) and not r.get('has_second_feature', False)]
    if no_features_files:
        print(f"\n❌ 无特征文件 ({len(no_features_files)}个):")
        
        # 按失败原因分组
        failure_reasons = {}
        for result in no_features_files:
            if 'error' in result:
                reason = "文件错误"
            else:
                # 分析具体失败原因
                white_ratio = result['first_feature_details']['white_bg_ratio']
                second_reason = result['second_feature_details']['reason']
                
                if white_ratio < 0.95:
                    reason = f"白底不足({white_ratio:.2f})"
                elif '只检测到1条长黑线' in second_reason:
                    reason = "仅1条横线"
                elif '未检测到长黑线' in second_reason:
                    reason = "无横线"
                else:
                    reason = "其他原因"
            
            if reason not in failure_reasons:
                failure_reasons[reason] = []
            failure_reasons[reason].append(result['file_name'])
        
        # 显示失败原因统计
        print(f"\n失败原因统计:")
        for reason, files in failure_reasons.items():
            print(f"  {reason}: {len(files)}个文件")
    
    # 保存结果到JSON文件
    # 确保tests/data目录存在
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = data_dir / f"energy_storage_combined_features_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    summary_data = {
        'scan_time': datetime.now().isoformat(),
        'source_directory': energy_storage_dir,
        'detection_type': 'combined_features',
        'total_files': len(pdf_files),
        'statistics': {
            'both_features': both_features_count,
            'first_feature_only': first_feature_only_count,
            'second_feature_only': second_feature_only_count,
            'no_features': no_features_count
        },
        'success_rates': {
            'both_features_rate': both_features_count/len(pdf_files)*100 if len(pdf_files) > 0 else 0,
            'first_feature_rate': (both_features_count + first_feature_only_count)/len(pdf_files)*100 if len(pdf_files) > 0 else 0,
            'second_feature_rate': (both_features_count + second_feature_only_count)/len(pdf_files)*100 if len(pdf_files) > 0 else 0
        },
        'files': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    print("🔍 综合检测储能目录下PDF文件第一页特征")
    print("📋 检测内容：第一特征（白色背景+黑色文字）+ 第二特征（两条长黑横线）")
    results = detect_energy_storage_first_pages()
