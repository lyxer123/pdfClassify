#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的第二特征参数设置
验证两条长黑线的长度要求（>=70%页面宽度）和间距要求（>=45%页面高度）
"""

import cv2
import numpy as np
import logging
from pathlib import Path
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
from main import PDFFeatureExtractor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_new_parameters():
    """测试新的第二特征参数"""
    logger.info("开始测试新的第二特征参数设置")
    logger.info("新的参数要求：")
    logger.info("  1. 两条长黑线长度 >= 70% 页面宽度")
    logger.info("  2. 两条长黑线间距 >= 45% 页面高度")
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 检查jc文件夹中的PDF文件
    jc_folder = Path("jc")
    if not jc_folder.exists():
        logger.error("jc文件夹不存在，请先运行批量验证脚本")
        return
    
    pdf_files = list(jc_folder.glob("*.pdf"))
    if not pdf_files:
        logger.warning("jc文件夹中没有PDF文件")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件进行测试")
    
    # 测试前几个文件
    for i, pdf_file in enumerate(pdf_files[:3], 1):
        logger.info(f"\n[{i}/{min(3, len(pdf_files))}] 测试文件: {pdf_file.name}")
        
        try:
            # 转换PDF页面为图片
            images = extractor.pdf_to_images(pdf_file, max_pages=1)
            if not images:
                logger.warning(f"  PDF转换失败: {pdf_file.name}")
                continue
            
            # 分析第一页
            image = images[0]
            height, width = image.shape[:2]
            logger.info(f"  图像尺寸: {width}x{height}")
            
            # 检测第二特征
            second_feature = extractor.detect_mb_second_feature(image)
            
            if second_feature and second_feature['has_second_feature']:
                logger.info(f"  ✓ 第二特征检测成功")
                
                # 检查长度要求
                length_ratio_1 = second_feature['length_ratio_1']
                length_ratio_2 = second_feature['length_ratio_2']
                length_ok_1 = length_ratio_1 >= 0.70
                length_ok_2 = length_ratio_2 >= 0.70
                
                logger.info(f"    线条1长度比例: {length_ratio_1:.1%} {'✓' if length_ok_1 else '✗'} (>= 70%)")
                logger.info(f"    线条2长度比例: {length_ratio_2:.1%} {'✓' if length_ok_2 else '✗'} (>= 70%)")
                
                # 检查间距要求
                distance_ratio = second_feature['line_distance_ratio']
                distance_ok = distance_ratio >= 0.45
                
                logger.info(f"    线条间距比例: {distance_ratio:.1%} {'✓' if distance_ok else '✗'} (>= 45%)")
                
                # 总体评估
                overall_ok = length_ok_1 and length_ok_2 and distance_ok
                logger.info(f"    总体评估: {'✓ 符合新标准' if overall_ok else '✗ 不符合新标准'}")
                
            else:
                logger.info(f"  ✗ 第二特征检测失败")
                if second_feature:
                    logger.info(f"    失败原因: {second_feature['reason']}")
        
        except Exception as e:
            logger.error(f"  测试文件时出错: {str(e)}")
    
    logger.info("\n测试完成！")

if __name__ == "__main__":
    test_new_parameters()
