#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析用户指定的PDF文件，使用改进后的线条检测算法
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

def analyze_additional_pdfs():
    """分析用户指定的PDF文件"""
    
    # 用户指定的PDF文件列表
    target_files = [
        '山地城市电动汽车分时租赁模式及支撑技术研究与示范应用-任务书.pdf',
        '山东青州格鲁科电力咨询设计有限公司（报价文件、资质）.pdf',
        '备份（未删掉项目、未更改专利）科技成果鉴定证书-基于钛酸锂电池的电动公交快充商业模式及关键技术研究与应用.pdf'
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
        logger.info(f"开始分析文件: {filename}")
        
        try:
            # 查找PDF文件
            pdf_path = None
            for pdf_file in jc_dir.glob("*.pdf"):
                if filename in pdf_file.name:
                    pdf_path = pdf_file
                    break
            
            if not pdf_path:
                logger.warning(f"未找到文件: {filename}")
                continue
            
            # 转换为图像
            image = feature_extractor.pdf_to_image(pdf_path)
            if image is None:
                logger.error(f"PDF转换失败: {filename}")
                continue
            
            # 检测长黑线并可视化
            result = feature_extractor.detect_mb_second_feature(image)
            
            # 生成输出文件名
            output_filename = f"{Path(filename).stem}_analysis.png"
            output_path = jc_dir / output_filename
            
            # 保存图片（这里需要重新实现可视化功能）
            logger.info(f"检测结果: {result}")
                
        except Exception as e:
            logger.error(f"分析文件 {filename} 时发生错误: {e}")
            continue
    
    logger.info("所有指定文件分析完成")

if __name__ == "__main__":
    analyze_additional_pdfs()
