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

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import PDFFeatureExtractor
from analyze_specific_files import SpecificFileAnalyzer

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
    
    # 创建分析器实例，使用jc文件夹作为源文件夹
    analyzer = SpecificFileAnalyzer("jc")
    
    # 分析每个文件
    for filename in target_files:
        logger.info(f"开始分析文件: {filename}")
        
        try:
            # 查找PDF文件
            pdf_path = analyzer.find_pdf_file(filename)
            if not pdf_path:
                logger.warning(f"未找到文件: {filename}")
                continue
            
            # 转换为图像
            image = analyzer.pdf_to_image(pdf_path)
            if image is None:
                logger.error(f"PDF转换失败: {filename}")
                continue
            
            # 检测长黑线并可视化
            vis_image, result = analyzer.detect_and_visualize_lines(image, filename)
            
            # 生成输出文件名
            output_filename = f"{Path(filename).stem}_analysis.png"
            output_path = jc_dir / output_filename
            
            # 保存图片
            import cv2
            success = cv2.imwrite(str(output_path), vis_image)
            if success:
                logger.info(f"分析图片已保存: {output_path}")
                if result:
                    logger.info(f"检测结果: {result}")
                else:
                    logger.warning(f"没有检测到特征")
            else:
                logger.error(f"图片保存失败: {output_path}")
                
        except Exception as e:
            logger.error(f"分析文件 {filename} 时发生错误: {e}")
            continue
    
    logger.info("所有指定文件分析完成")

if __name__ == "__main__":
    analyze_additional_pdfs()
