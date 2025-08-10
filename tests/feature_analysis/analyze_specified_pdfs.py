#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析指定的PDF文件，使用改进后的线条检测算法
生成分析PNG图片保存到jc文件夹中
"""

import os
import sys
from pathlib import Path
import logging

# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

from pdf_feature_extractor import PDFFeatureExtractor
from pdf_analyzer import UnifiedPDFAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_specified_pdfs():
    """分析指定的PDF文件"""
    
    # 指定的PDF文件列表
    target_files = [
        '十三五中国充电桩行业发展分析及投资可行性研究报告12.pdf',  # 去掉引号
        '《电动汽车充电设施标准体系项目表(2015年版》 (1).pdf',
        '《关于电力交易机构组建和规范运行的实施意见》.pdf',
        '《关于加强和规范燃煤自备电厂监督管理的指导意见》.pdf',
        '《关于推进电力市场建设的实施意见》.pdf'
    ]
    
    # 检查jc文件夹
    jc_dir = Path('jc')
    if not jc_dir.exists():
        logger.error("jc文件夹不存在")
        return
    
    # 创建分析器实例
    analyzer = UnifiedPDFAnalyzer()
    feature_extractor = PDFFeatureExtractor()
    
    # 分析每个文件
    for filename in target_files:
        pdf_path = jc_dir / filename
        
        if not pdf_path.exists():
            logger.warning(f"文件不存在: {filename}")
            continue
            
        logger.info(f"开始分析文件: {filename}")
        
        try:
            # 转换为图像
            image = feature_extractor.pdf_to_image(pdf_path)
            if image is None:
                logger.error(f"PDF转换失败: {filename}")
                continue
            
            # 检测长黑线
            result = feature_extractor.detect_mb_second_feature(image)
            
            # 生成输出文件名
            output_filename = f"{Path(filename).stem}_analysis.png"
            output_path = jc_dir / output_filename
            
            # 记录检测结果
            logger.info(f"检测结果: {result}")
                
        except Exception as e:
            logger.error(f"分析文件 {filename} 时发生错误: {e}")
            continue
    
    logger.info("所有指定文件分析完成")

if __name__ == "__main__":
    analyze_specified_pdfs()
