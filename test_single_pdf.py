# -*- coding: utf-8 -*-
"""
单个PDF文件测试脚本
"""

import os
import sys
from pdf_processor import PDFProcessor
import logging

def test_single_pdf(pdf_path):
    """测试单个PDF文件"""
    
    # 设置详细日志
    logging.basicConfig(level=logging.DEBUG, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print(f"测试PDF文件: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 {pdf_path}")
        return
    
    try:
        # 初始化处理器
        processor = PDFProcessor()
        print("PDF处理器初始化成功")
        
        # 处理PDF
        result = processor.process_pdf(pdf_path, timeout=30)
        
        print(f"\n处理结果:")
        print(f"  成功: {result['success']}")
        print(f"  原因: {result['reason']}")
        print(f"  处理时间: {result['processing_time']:.2f}秒")
        
        # 无论成功失败都显示特征信息（用于调试）
        if hasattr(processor, '_last_features'):
            features = processor._last_features
            print(f"\n特征信息:")
            print(f"  白色背景: {features.get('white_ratio', 0)*100:.1f}%")
            print(f"  黑色文字: {features.get('black_ratio', 0)*100:.1f}%")
            print(f"  检测区域: {len(features.get('regions', {}))}")
            print(f"  检测框数: {len(features.get('key_boxes', {}))}")
            
            keywords = features.get('keywords', {})
            print(f"  关键词: 标准={'✓' if keywords.get('upper_has_standard') else '✗'} "
                  f"发布={'✓' if keywords.get('lower_has_publish') else '✗'}")
            
            # 详细分析匹配度
            print(f"\n匹配度分析:")
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
            print(f"  颜色特征 ({color_score}/20): 白底{white_ratio*100:.1f}% 黑字{black_ratio*100:.1f}%")
            
            # 区域检测
            max_score += 15
            regions = features.get('regions', {})
            region_score = 15 if len(regions) >= 3 else (10 if len(regions) >= 2 else 0)
            validation_score += region_score
            print(f"  区域检测 ({region_score}/15): 检测到{len(regions)}/3个区域")
            
            # 关键框检测
            max_score += 15
            key_boxes = features.get('key_boxes', {})
            box_count = len(key_boxes)
            box_score = 15 if box_count >= 6 else (10 if box_count >= 4 else (5 if box_count >= 2 else 0))
            validation_score += box_score
            print(f"  关键框检测 ({box_score}/15): 检测到{box_count}/6个关键框")
            
            # 关键词验证
            max_score += 40
            keyword_score = 0
            if keywords.get('upper_has_standard', False):
                keyword_score += 25
            if keywords.get('lower_has_publish', False):
                keyword_score += 15
            validation_score += keyword_score
            print(f"  关键词验证 ({keyword_score}/40): 标准{keyword_score >= 25} 发布{keyword_score >= 15}")
            
            # 横线结构验证
            max_score += 25
            lines = features.get('lines', {})
            line_score = 0
            if lines.get('first_line_valid', False):
                line_score += 12
            if lines.get('second_line_valid', False):
                line_score += 13
            validation_score += line_score
            print(f"  横线结构 ({line_score}/25): 第一横线{'✓' if lines.get('first_line_valid') else '✗'} 第二横线{'✓' if lines.get('second_line_valid') else '✗'}")
            
            # 总体匹配度
            match_percentage = (validation_score / max_score) * 100 if max_score > 0 else 0
            print(f"  总体匹配度: {validation_score}/{max_score} = {match_percentage:.1f}%")
            print(f"  验证阈值: 70% {'(通过)' if match_percentage >= 70 else '(不通过)'}")
        elif result['features']:
            features = result['features']
            print(f"\n特征信息:")
            print(f"  白色背景: {features.get('white_ratio', 0)*100:.1f}%")
            print(f"  黑色文字: {features.get('black_ratio', 0)*100:.1f}%")
            print(f"  检测区域: {len(features.get('regions', {}))}")
            print(f"  检测框数: {len(features.get('key_boxes', {}))}")
            
            keywords = features.get('keywords', {})
            print(f"  关键词: 标准={'✓' if keywords.get('upper_has_standard') else '✗'} "
                  f"发布={'✓' if keywords.get('lower_has_publish') else '✗'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) != 2:
        print("用法: python test_single_pdf.py <PDF文件路径>")
        print("示例: python test_single_pdf.py 'F:\\标准规范要求\\充电\\GB 38031-2020 电动汽车用动力蓄电池安全要求.pdf'")
        return
    
    pdf_path = sys.argv[1]
    test_single_pdf(pdf_path)

if __name__ == "__main__":
    main()
