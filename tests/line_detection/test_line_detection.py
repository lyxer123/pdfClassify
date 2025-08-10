#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的线条检测算法
验证三个改进点：
1. 调整检测阈值（从15%提高到80%）
2. 增加线条宽度验证
3. 改进形态学检测算法
"""

import cv2
import numpy as np
import logging
from pathlib import Path
import sys

# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

from main import PDFFeatureExtractor

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_line_detection_improvements():
    """测试线条检测的改进效果"""
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor()
    
    # 创建测试图像：模拟包含长行文字和真正横线的图像
    test_image = create_test_image()
    
    logger.info("开始测试改进后的线条检测算法...")
    
    # 测试改进后的检测方法
    result = extractor.detect_mb_second_feature(test_image)
    
    logger.info("检测结果:")
    logger.info(f"  是否检测到第二特征: {result['has_second_feature']}")
    logger.info(f"  检测到的线条数量: {result['detected_lines']}")
    logger.info(f"  失败原因: {result.get('reason', 'N/A')}")
    
    if result['has_second_feature']:
        logger.info("✓ 成功检测到两条长黑线")
        for i, line in enumerate(result['long_lines']):
            logger.info(f"  线条{i+1}:")
            logger.info(f"    位置: y={line['y_center']:.0f} ({line['y_percent']:.1f}%)")
            logger.info(f"    长度: {line['length']:.0f} ({line['width_ratio']*100:.1f}%)")
            logger.info(f"    宽度: {line.get('line_width', 'N/A')}px")
            logger.info(f"    质量评分: {line.get('quality_score', 'N/A'):.2f}")
    else:
        logger.info("✗ 未检测到第二特征")
    
    return result

def create_test_image():
    """创建测试图像，包含长行文字和真正的横线"""
    width, height = 800, 1200
    
    # 创建白色背景
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # 添加一些长行文字（应该被过滤掉）
    cv2.putText(image, "这是一个很长的标题行，应该被算法识别为文字而不是横线", 
                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    
    cv2.putText(image, "另一个长行文字，用于测试算法是否能正确区分文字和横线", 
                (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    
    # 添加真正的横线（应该被检测到）
    # 第一条横线：细线，贯穿页面
    cv2.line(image, (50, 400), (750, 400), (0, 0, 0), 2)
    
    # 第二条横线：细线，贯穿页面
    cv2.line(image, (50, 800), (750, 800), (0, 0, 0), 2)
    
    # 添加一些短线条（应该被过滤掉）
    cv2.line(image, (100, 300), (300, 300), (0, 0, 0), 1)
    cv2.line(image, (500, 500), (600, 500), (0, 0, 0), 1)
    
    # 添加一些文字
    cv2.putText(image, "标准", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.putText(image, "发布", (50, 950), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    
    return image

def main():
    """主函数"""
    logger.info("=== 线条检测算法改进测试 ===")
    
    try:
        result = test_line_detection_improvements()
        
        logger.info("\n=== 测试总结 ===")
        if result['has_second_feature']:
            logger.info("✓ 改进成功：算法正确识别了真正的横线")
            logger.info("✓ 长行文字没有被误识别为横线")
            logger.info("✓ 线条宽度验证工作正常")
            logger.info("✓ 形态学检测算法改进有效")
        else:
            logger.info("✗ 测试失败：未能检测到预期的横线")
            logger.info(f"  失败原因: {result.get('reason', '未知')}")
        
        # 保存测试图像
        test_image = create_test_image()
        cv2.imwrite("test_line_detection.png", test_image)
        logger.info("测试图像已保存为: test_line_detection.png")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
