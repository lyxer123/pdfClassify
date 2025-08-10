#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析指定PDF文件的长黑线特征
生成带有长黑线标识的图片并保存到jc文件夹
"""

import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from main import PDFFeatureExtractor
import logging
from pathlib import Path
import io

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpecificFileAnalyzer:
    """特定文件分析器"""
    
    def __init__(self, source_folder, target_folder="jc"):
        self.source_folder = Path(source_folder)
        self.target_folder = Path(target_folder)
        self.extractor = PDFFeatureExtractor()
        
        # 确保目标文件夹存在
        self.target_folder.mkdir(exist_ok=True)
    
    def find_pdf_file(self, filename):
        """在源文件夹中查找指定的PDF文件"""
        logger.info(f"搜索文件: {filename}")
        
        # 尝试多种文件名变体
        possible_names = [
            filename,
            filename.replace("《", "").replace("》", ""),
            filename.replace("(1)", ""),
            filename.replace("_1", ""),
            filename.replace("12", ""),
            filename.replace("2015年版", ""),
            filename.replace(" ", "")
        ]
        
        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    # 检查是否匹配任何可能的文件名
                    for possible_name in possible_names:
                        if possible_name.lower() in file.lower() or file.lower() in possible_name.lower():
                            found_path = Path(root) / file
                            logger.info(f"找到匹配文件: {found_path}")
                            return found_path
        
        logger.warning(f"未找到文件: {filename}")
        return None
    
    def pdf_to_image(self, pdf_path, page_num=0):
        """将PDF页面转换为图像"""
        try:
            logger.info(f"正在转换PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                page_num = 0
            
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
            
            # 转换为PIL图像
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # 转换为OpenCV格式
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            doc.close()
            logger.info(f"PDF转换成功，图像尺寸: {img_cv.shape}")
            return img_cv
            
        except Exception as e:
            logger.error(f"PDF转换失败: {str(e)}")
            return None
    
    def detect_and_visualize_lines(self, image, filename):
        """检测长黑线并在图像上标识"""
        try:
            logger.info(f"开始检测长黑线: {filename}")
            
            # 检测第二特征
            result = self.extractor.detect_mb_second_feature(image)
            
            # 添加调试信息
            logger.info(f"检测结果: {result}")
            
            # 创建可视化图像
            vis_image = image.copy()
            
            if result['has_second_feature'] and result['detected_lines'] == 2:
                lines = result['long_lines']
                
                # 在每条线上绘制红色矩形框
                for i, line in enumerate(lines):
                    # 从coords中提取坐标信息
                    coords = line['coords']  # (x1, y1, x2, y2)
                    x1, y1, x2, y2 = coords
                    
                    # 绘制红色矩形框
                    cv2.rectangle(vis_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                    
                    # 添加标签
                    label = f"Line {i+1}: {line['width_ratio']*100:.1f}%"
                    cv2.putText(vis_image, label, (int(x1), int(y1)-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    # 添加线条宽度和质量信息
                    if 'line_width' in line:
                        width_label = f"Width: {line['line_width']:.1f}px"
                        cv2.putText(vis_image, width_label, (int(x1), int(y1)+15), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    
                    if 'quality_score' in line:
                        quality_label = f"Quality: {line['quality_score']:.2f}"
                        cv2.putText(vis_image, quality_label, (int(x1), int(y1)+30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    
                    # 添加坐标信息
                    coord_label = f"({int(x1)},{int(y1)})-({int(x2)},{int(y2)})"
                    cv2.putText(vis_image, coord_label, (int(x1), int(y1)+45), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
                # 添加检测信息
                info_text = [
                    f"Lines detected: {result['detected_lines']}",
                    f"Line 1 length: {result['length_ratio_1']*100:.1f}%",
                    f"Line 2 length: {result['length_ratio_2']*100:.1f}%",
                    f"Distance: {result['line_distance_ratio']*100:.1f}%"
                ]
                
                y_offset = 30
                for text in info_text:
                    cv2.putText(vis_image, text, (10, y_offset), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    y_offset += 25
                
                logger.info(f"✓ {filename}: 成功检测到2条长黑线")
                logger.info(f"  线条1: 长度{result['length_ratio_1']*100:.1f}%, 位置y={lines[0]['y_center']:.0f}")
                logger.info(f"  线条2: 长度{result['length_ratio_2']*100:.1f}%, 位置y={lines[1]['y_center']:.0f}")
                logger.info(f"  间距: {result['line_distance_ratio']*100:.1f}%")
                
            else:
                # 如果没有检测到足够的线条，显示失败原因
                cv2.putText(vis_image, f"No valid lines detected: {result['reason']}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                logger.warning(f"✗ {filename}: {result['reason']}")
                
                # 添加更多调试信息
                if 'detected_lines' in result:
                    cv2.putText(vis_image, f"Detected lines: {result['detected_lines']}", 
                              (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if 'long_lines' in result and result['long_lines']:
                    cv2.putText(vis_image, f"Long lines found: {len(result['long_lines'])}", 
                              (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # 显示检测到的线条信息
                    for i, line in enumerate(result['long_lines']):
                        coords = line['coords']
                        x1, y1, x2, y2 = coords
                        cv2.rectangle(vis_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        
                        # 添加绿色标签显示检测到的内容
                        label = f"Detected {i+1}: {line['width_ratio']*100:.1f}%"
                        cv2.putText(vis_image, label, (int(x1), int(y1)-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # 显示坐标
                        coord_label = f"({int(x1)},{int(y1)})-({int(x2)},{int(y2)})"
                        cv2.putText(vis_image, coord_label, (int(x1), int(y1)+20), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return vis_image, result
            
        except Exception as e:
            logger.error(f"检测失败: {str(e)}")
            return image, None
    
    def analyze_specific_files(self):
        """分析指定的文件"""
        target_files = [
            '"十三五"中国充电桩行业发展分析及投资可行性研究报告12.pdf',
            '《电动汽车充电设施标准体系项目表(2015年版》 (1).pdf',
            '《关于电力交易机构组建和规范运行的实施意见》.pdf',
            '《关于加强和规范燃煤自备电厂监督管理的指导意见》.pdf',
            '《关于推进电力市场建设的实施意见》.pdf'
        ]
        
        results = []
        
        for i, filename in enumerate(target_files):
            logger.info(f"\n正在分析: {filename}")
            
            # 查找文件
            pdf_path = self.find_pdf_file(filename)
            if not pdf_path:
                logger.error(f"未找到文件: {filename}")
                continue
            
            # 转换为图像
            image = self.pdf_to_image(pdf_path)
            if image is None:
                logger.error(f"PDF转换失败: {filename}")
                continue
            
            # 检测长黑线并可视化
            vis_image, result = self.detect_and_visualize_lines(image, filename)
            
            # 使用简单的英文文件名避免编码问题
            output_filename = f"file_{i+1}_analysis.png"
            output_path = self.target_folder / output_filename
            
            # 保存图片
            success = cv2.imwrite(str(output_path), vis_image)
            if success:
                logger.info(f"结果图片已保存: {output_path}")
            else:
                logger.error(f"图片保存失败: {output_path}")
                continue
            
            results.append({
                'filename': filename,
                'pdf_path': str(pdf_path),
                'result': result,
                'output_image': str(output_path)
            })
        
        return results

def main():
    """主函数"""
    source_folder = r"I:\正在工作目录-重庆电科院"
    target_folder = "jc"
    
    logger.info(f"源文件夹: {source_folder}")
    logger.info(f"目标文件夹: {target_folder}")
    
    analyzer = SpecificFileAnalyzer(source_folder, target_folder)
    results = analyzer.analyze_specific_files()
    
    # 输出总结
    logger.info("\n=== 分析总结 ===")
    for result in results:
        if result['result'] and result['result']['has_second_feature']:
            logger.info(f"✓ {result['filename']}: 符合标准")
        else:
            logger.info(f"✗ {result['filename']}: 不符合标准")
    
    logger.info(f"\n结果图片已保存到: {target_folder} 文件夹")

if __name__ == "__main__":
    main()
