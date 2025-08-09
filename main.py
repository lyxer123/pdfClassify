#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF特征提取工具
功能：分析PDF文件的页面颜色特征，检测是否符合标准（白色背景+黑色文字）
"""

import os
import sys
import json
import argparse
import io
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_classify.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFFeatureExtractor:
    """PDF特征提取器"""
    
    def __init__(self, template_path="templates/mb.png", data_dir="data"):
        """
        初始化特征提取器
        
        Args:
            template_path: 标准模板图片路径
            data_dir: 特征数据保存目录
        """
        self.template_path = template_path
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 颜色特征阈值配置（基于104个标准PDF分析结果优化）
        self.color_thresholds = {
            'white_bg_min': 200,      # 白色背景最小RGB值
            'black_text_max': 80,     # 黑色文字最大RGB值
            'bg_ratio_min': 0.95,     # 背景色占比最小值（基于标准PDF 5%分位数: 95.2%）
            'text_ratio_min': 0.011,  # 文字色占比最小值（基于标准PDF 5%分位数: 1.2%）
            'contrast_min': 29,       # 最小对比度（基于标准PDF 5%分位数: 29.5）
            'brightness_min': 246     # 最小亮度（基于标准PDF 5%分位数: 246.2）
        }
    
    def pdf_to_images(self, pdf_path, max_pages=5):
        """
        将PDF页面转换为图片
        
        Args:
            pdf_path: PDF文件路径
            max_pages: 最大页数
            
        Returns:
            list: 图片数组列表
        """
        try:
            doc = fitz.open(pdf_path)
            images = []
            
            pages_to_convert = min(len(doc), max_pages)
            logger.info(f"正在转换PDF '{pdf_path}' 的前 {pages_to_convert} 页")
            
            for page_num in range(pages_to_convert):
                page = doc.load_page(page_num)
                # 设置较高的分辨率以获得更好的图像质量
                mat = fitz.Matrix(2.0, 2.0)  # 2倍放大
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为PIL图像
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # 转换为numpy数组
                img_array = np.array(img)
                images.append(img_array)
                
                logger.info(f"已转换第 {page_num + 1} 页，图像尺寸: {img_array.shape}")
            
            doc.close()
            return images
            
        except Exception as e:
            logger.error(f"PDF转换失败 '{pdf_path}': {str(e)}")
            return []
    
    def analyze_color_features(self, image):
        """
        分析图像的颜色特征
        
        Args:
            image: 图像数组 (numpy array)
            
        Returns:
            dict: 颜色特征分析结果
        """
        try:
            # 转换为RGB（如果是BGR）
            if len(image.shape) == 3 and image.shape[2] == 3:
                # 假设输入是RGB格式
                rgb_image = image
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            height, width = rgb_image.shape[:2]
            total_pixels = height * width
            
            # 计算各颜色通道的平均值
            mean_colors = np.mean(rgb_image.reshape(-1, 3), axis=0)
            
            # 分析白色背景像素
            white_mask = np.all(rgb_image >= self.color_thresholds['white_bg_min'], axis=2)
            white_pixels = np.sum(white_mask)
            white_ratio = white_pixels / total_pixels
            
            # 分析黑色文字像素
            black_mask = np.all(rgb_image <= self.color_thresholds['black_text_max'], axis=2)
            black_pixels = np.sum(black_mask)
            black_ratio = black_pixels / total_pixels
            
            # 分析灰度分布
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            
            # 计算对比度（标准差）
            contrast = np.std(gray_image)
            
            features = {
                'mean_rgb': mean_colors.tolist(),
                'white_bg_ratio': float(white_ratio),
                'black_text_ratio': float(black_ratio),
                'contrast': float(contrast),
                'image_size': [width, height],
                'total_pixels': total_pixels,
                'histogram': hist.flatten().tolist()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"颜色特征分析失败: {str(e)}")
            return None
    
    def check_standard_compliance(self, features):
        """
        检查是否符合标准特征（白色背景+黑色文字）
        
        Args:
            features: 颜色特征字典
            
        Returns:
            bool: 是否符合标准
        """
        if not features:
            return False
        
        # 检查白色背景比例
        white_bg_ok = features['white_bg_ratio'] >= self.color_thresholds['bg_ratio_min']
        
        # 检查黑色文字比例
        black_text_ok = features['black_text_ratio'] >= self.color_thresholds['text_ratio_min']
        
        # 检查整体亮度（RGB均值）
        mean_rgb = features['mean_rgb']
        avg_brightness = sum(mean_rgb) / len(mean_rgb)
        brightness_ok = avg_brightness >= self.color_thresholds['brightness_min']
        
        # 检查对比度（确保有足够的对比度）
        contrast_ok = features['contrast'] >= self.color_thresholds['contrast_min']
        
        compliance = white_bg_ok and black_text_ok and brightness_ok and contrast_ok
        
        logger.info(f"标准符合性检查:")
        logger.info(f"  白色背景比例: {features['white_bg_ratio']:.3f} (>= {self.color_thresholds['bg_ratio_min']}) - {'✓' if white_bg_ok else '✗'}")
        logger.info(f"  黑色文字比例: {features['black_text_ratio']:.3f} (>= {self.color_thresholds['text_ratio_min']}) - {'✓' if black_text_ok else '✗'}")
        logger.info(f"  整体亮度: {avg_brightness:.1f} (>= {self.color_thresholds['brightness_min']}) - {'✓' if brightness_ok else '✗'}")
        logger.info(f"  对比度: {features['contrast']:.1f} (>= {self.color_thresholds['contrast_min']}) - {'✓' if contrast_ok else '✗'}")
        logger.info(f"  最终结果: {'符合标准' if compliance else '不符合标准'}")
        
        return compliance
    
    def process_pdf_file(self, pdf_path, max_pages=5):
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            max_pages: 最大处理页数
            
        Returns:
            dict: 处理结果
        """
        pdf_path = Path(pdf_path)
        logger.info(f"开始处理PDF文件: {pdf_path}")
        
        # 转换PDF页面为图片
        images = self.pdf_to_images(pdf_path, max_pages)
        if not images:
            return {
                'file_path': str(pdf_path),
                'success': False,
                'error': 'PDF转换失败',
                'compliance': False
            }
        
        # 分析每页的特征
        page_results = []
        overall_compliance = True
        
        for i, image in enumerate(images):
            logger.info(f"分析第 {i+1} 页特征...")
            features = self.analyze_color_features(image)
            
            if features:
                compliance = self.check_standard_compliance(features)
                page_results.append({
                    'page_number': i + 1,
                    'features': features,
                    'compliance': compliance
                })
                
                # 如果任何一页不符合标准，整体就不符合
                if not compliance:
                    overall_compliance = False
            else:
                page_results.append({
                    'page_number': i + 1,
                    'features': None,
                    'compliance': False
                })
                overall_compliance = False
        
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'success': True,
            'pages_analyzed': len(page_results),
            'page_results': page_results,
            'overall_compliance': overall_compliance,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"PDF '{pdf_path.name}' 处理完成，整体符合性: {'是' if overall_compliance else '否'}")
        return result
    
    def process_pdf_folder(self, folder_path, max_pages=5):
        """
        处理文件夹中的所有PDF文件
        
        Args:
            folder_path: PDF文件夹路径
            max_pages: 每个PDF最大处理页数
            
        Returns:
            dict: 处理结果汇总
        """
        folder_path = Path(folder_path)
        logger.info(f"开始处理PDF文件夹: {folder_path}")
        
        if not folder_path.exists():
            logger.error(f"文件夹不存在: {folder_path}")
            return None
        
        # 查找所有PDF文件（避免重复）
        pdf_files_lower = list(folder_path.glob("*.pdf"))
        pdf_files_upper = list(folder_path.glob("*.PDF"))
        # 使用集合去重，避免在不区分大小写的文件系统中重复
        pdf_files = list(set(pdf_files_lower + pdf_files_upper))
        if not pdf_files:
            logger.warning(f"文件夹中未找到PDF文件: {folder_path}")
            return {
                'folder_path': str(folder_path),
                'total_files': 0,
                'results': [],
                'summary': {'compliant': 0, 'non_compliant': 0, 'errors': 0}
            }
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 处理每个PDF文件
        results = []
        summary = {'compliant': 0, 'non_compliant': 0, 'errors': 0}
        
        for pdf_file in pdf_files:
            try:
                result = self.process_pdf_file(pdf_file, max_pages)
                results.append(result)
                
                if result['success']:
                    if result['overall_compliance']:
                        summary['compliant'] += 1
                    else:
                        summary['non_compliant'] += 1
                else:
                    summary['errors'] += 1
                    
            except Exception as e:
                logger.error(f"处理PDF文件时出错 '{pdf_file}': {str(e)}")
                results.append({
                    'file_path': str(pdf_file),
                    'file_name': pdf_file.name,
                    'success': False,
                    'error': str(e),
                    'compliance': False
                })
                summary['errors'] += 1
        
        # 汇总结果
        folder_result = {
            'folder_path': str(folder_path),
            'total_files': len(pdf_files),
            'results': results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"文件夹处理完成:")
        logger.info(f"  总文件数: {len(pdf_files)}")
        logger.info(f"  符合标准: {summary['compliant']}")
        logger.info(f"  不符合标准: {summary['non_compliant']}")
        logger.info(f"  处理错误: {summary['errors']}")
        
        return folder_result
    
    def save_results(self, results, output_name=None):
        """
        保存结果到data文件夹
        
        Args:
            results: 处理结果
            output_name: 输出文件名（可选）
        """
        if not results:
            logger.error("没有结果可保存")
            return
        
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"pdf_feature_analysis_{timestamp}.json"
        
        output_path = self.data_dir / output_name
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PDF特征提取工具')
    parser.add_argument('input_path', help='输入PDF文件或文件夹路径')
    parser.add_argument('--max-pages', type=int, default=5, help='每个PDF最大处理页数（默认：5）')
    parser.add_argument('--template', default='templates/mb.png', help='标准模板图片路径')
    parser.add_argument('--output', help='输出文件名（可选）')
    parser.add_argument('--data-dir', default='data', help='数据保存目录')
    
    args = parser.parse_args()
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor(
        template_path=args.template,
        data_dir=args.data_dir
    )
    
    input_path = Path(args.input_path)
    
    # 处理输入
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # 处理单个PDF文件
        logger.info("处理模式: 单个PDF文件")
        results = extractor.process_pdf_file(input_path, args.max_pages)
    elif input_path.is_dir():
        # 处理PDF文件夹
        logger.info("处理模式: PDF文件夹")
        results = extractor.process_pdf_folder(input_path, args.max_pages)
    else:
        logger.error(f"无效的输入路径: {input_path}")
        return 1
    
    # 保存结果
    if results:
        extractor.save_results(results, args.output)
        return 0
    else:
        logger.error("处理失败，没有生成结果")
        return 1


if __name__ == "__main__":
    import io
    sys.exit(main())
