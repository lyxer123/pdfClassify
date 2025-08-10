#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一PDF分析工具
功能：
1. 递归扫描指定文件夹下的所有PDF文件，进行两阶段特征验证
2. 分析指定的PDF文件，生成带有长黑线标识的图片
3. 支持多种分析模式和输出格式
"""

import os
import shutil
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from main import PDFFeatureExtractor
import logging
import json
from datetime import datetime
from pathlib import Path
import argparse
import io

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/pdf_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedPDFAnalyzer:
    """统一PDF分析器"""
    
    def __init__(self, source_folder, target_folder="jc"):
        """
        初始化分析器
        
        Args:
            source_folder: 源文件夹路径
            target_folder: 目标文件夹路径（默认为jc）
        """
        self.source_folder = Path(source_folder)
        self.target_folder = Path(target_folder)
        self.extractor = PDFFeatureExtractor()
        
        # 确保目标文件夹存在
        self.target_folder.mkdir(exist_ok=True)
        
        # 统计结果
        self.stats = {
            'total_pdfs': 0,
            'first_feature_passed': 0,
            'second_feature_passed': 0,
            'copied_files': 0,
            'errors': 0,
            'specific_files_analyzed': 0
        }
        
        # 详细结果记录
        self.results = []
    
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
    
    def check_first_feature(self, image):
        """
        检查第一特征：白色背景+黑色文字
        
        Args:
            image: 图像数组
            
        Returns:
            dict: 第一特征检查结果
        """
        try:
            # 转换为RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = image
            else:
                rgb_image = cv2.cvtColor(image, cv2.IMREAD_COLOR)
                rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            
            height, width = rgb_image.shape[:2]
            total_pixels = height * width
            
            # 分析白色背景像素
            white_mask = np.all(rgb_image >= 200, axis=2)  # RGB >= 200
            white_pixels = np.sum(white_mask)
            white_ratio = white_pixels / total_pixels
            
            # 分析黑色文字像素
            black_mask = np.all(rgb_image <= 80, axis=2)  # RGB <= 80
            black_pixels = np.sum(black_mask)
            black_ratio = black_pixels / total_pixels
            
            # 计算整体亮度
            mean_rgb = np.mean(rgb_image.reshape(-1, 3), axis=0)
            avg_brightness = np.mean(mean_rgb)
            
            # 计算对比度
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            contrast = np.std(gray_image)
            
            # 检查是否符合第一特征要求
            first_feature_ok = (
                white_ratio >= 0.95 and      # 白色背景占比 >= 95%
                black_ratio >= 0.001 and     # 黑色文字占比 >= 0.1%
                avg_brightness >= 244 and    # 整体亮度 >= 244
                contrast >= 26               # 对比度 >= 26
            )
            
            return {
                'passed': first_feature_ok,
                'white_ratio': white_ratio,
                'black_ratio': black_ratio,
                'brightness': avg_brightness,
                'contrast': contrast,
                'details': {
                    'white_ratio_ok': white_ratio >= 0.95,
                    'black_ratio_ok': black_ratio >= 0.001,
                    'brightness_ok': avg_brightness >= 244,
                    'contrast_ok': contrast >= 26
                }
            }
            
        except Exception as e:
            logger.error(f"第一特征检查失败: {str(e)}")
            return {
                'passed': False,
                'error': str(e)
            }
    
    def check_second_feature(self, image):
        """
        检查第二特征：两条长黑横线
        
        Args:
            image: 图像数组
            
        Returns:
            dict: 第二特征检查结果
        """
        try:
            # 使用现有的第二特征检测方法
            result = self.extractor.detect_mb_second_feature(image)
            return result
            
        except Exception as e:
            logger.error(f"第二特征检查失败: {str(e)}")
            return {
                'has_second_feature': False,
                'error': str(e)
            }
    
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
            vis_image, result = self.detectAnd_visualize_lines(image, filename)
            
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
            
            self.stats['specific_files_analyzed'] += 1
        
        return results
    
    def process_pdf_file(self, pdf_path):
        """
        处理单个PDF文件（用于递归分类）
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            dict: 处理结果
        """
        try:
            file_name = pdf_path.name
            logger.info(f"处理文件: {file_name}")
            
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                logger.warning(f"空PDF文件: {file_name}")
                doc.close()
                return {
                    'file_path': str(pdf_path),
                    'file_name': file_name,
                    'success': False,
                    'error': '空PDF文件',
                    'first_feature': False,
                    'second_feature': False,
                    'copied': False
                }
            
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
            
            doc.close()
            
            # 第一阶段：检查第一特征
            logger.info(f"检查第一特征: {file_name}")
            first_feature_result = self.check_first_feature(image_rgb)
            
            if not first_feature_result['passed']:
                logger.info(f"第一特征检查失败: {file_name}")
                return {
                    'file_path': str(pdf_path),
                    'file_name': file_name,
                    'success': True,
                    'first_feature': False,
                    'second_feature': False,
                    'copied': False,
                    'first_feature_details': first_feature_result
                }
            
            # 第一特征通过，更新统计
            self.stats['first_feature_passed'] += 1
            logger.info(f"第一特征检查通过: {file_name}")
            
            # 第二阶段：检查第二特征
            logger.info(f"检查第二特征: {file_name}")
            second_feature_result = self.check_second_feature(image_rgb)
            
            if not second_feature_result['has_second_feature']:
                logger.info(f"第二特征检查失败: {file_name}")
                return {
                    'file_path': str(pdf_path),
                    'file_name': file_name,
                    'success': True,
                    'first_feature': True,
                    'second_feature': False,
                    'copied': False,
                    'first_feature_details': first_feature_result,
                    'second_feature_details': second_feature_result
                }
            
            # 第二特征通过，更新统计
            self.stats['second_feature_passed'] += 1
            logger.info(f"第二特征检查通过: {file_name}")
            
            # 复制文件到jc文件夹
            target_path = self.target_folder / file_name
            
            # 如果目标文件已存在，添加序号
            counter = 1
            original_target_path = target_path
            while target_path.exists():
                name_without_ext = original_target_path.stem
                ext = original_target_path.suffix
                target_path = self.target_folder / f"{name_without_ext}_{counter}{ext}"
                counter += 1
            
            # 复制文件
            shutil.copy2(pdf_path, target_path)
            self.stats['copied_files'] += 1
            
            logger.info(f"文件已复制到: {target_path}")
            
            return {
                'file_path': str(pdf_path),
                'file_name': file_name,
                'success': True,
                'first_feature': True,
                'second_feature': True,
                'copied': True,
                'target_path': str(target_path),
                'first_feature_details': first_feature_result,
                'second_feature_details': second_feature_result
            }
            
        except Exception as e:
            logger.error(f"处理文件失败 {pdf_path}: {str(e)}")
            self.stats['errors'] += 1
            return {
                'file_path': str(pdf_path),
                'file_name': pdf_path.name if hasattr(pdf_path, 'name') else str(pdf_path),
                'success': False,
                'error': str(e),
                'first_feature': False,
                'second_feature': False,
                'copied': False
            }
    
    def recursive_classify(self):
        """
        递归扫描源文件夹并处理所有PDF文件
        """
        logger.info(f"开始扫描文件夹: {self.source_folder}")
        
        # 递归查找所有PDF文件
        pdf_files = []
        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = Path(root) / file
                    pdf_files.append(pdf_path)
        
        self.stats['total_pdfs'] = len(pdf_files)
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        if len(pdf_files) == 0:
            logger.warning("未找到PDF文件")
            return
        
        # 处理每个PDF文件
        print(f"\n开始处理PDF文件...")
        print(f"{'='*120}")
        print(f"{'序号':<4} {'文件名':<50} {'第一特征':<10} {'第二特征':<10} {'复制状态':<10} {'详细信息'}")
        print(f"{'-'*4} {'-'*50} {'-'*10} {'-'*10} {'-'*10} {'-'*30}")
        
        for i, pdf_path in enumerate(pdf_files):
            file_name = pdf_path.name
            if len(file_name) > 47:
                display_name = file_name[:44] + "..."
            else:
                display_name = file_name
            
            # 处理文件
            result = self.process_pdf_file(pdf_path)
            self.results.append(result)
            
            # 显示处理结果
            first_status = "✅ 通过" if result.get('first_feature', False) else "❌ 失败"
            second_status = "✅ 通过" if result.get('second_feature', False) else "❌ 失败"
            copy_status = "✅ 已复制" if result.get('copied', False) else "❌ 未复制"
            
            # 详细信息
            if result.get('success', False):
                if result.get('first_feature', False) and result.get('second_feature', False):
                    detail = "符合标准，已复制"
                elif result.get('first_feature', False):
                    detail = f"第一特征通过，第二特征失败: {result.get('second_feature_details', {}).get('reason', '未知原因')}"
                else:
                    detail = f"第一特征失败: 白={result.get('first_feature_details', {}).get('white_ratio', 0):.1%}, 黑={result.get('first_feature_details', {}).get('black_ratio', 0):.1%}"
            else:
                detail = f"处理错误: {result.get('error', '未知错误')}"
            
            print(f"{i+1:<4} {display_name:<50} {first_status:<10} {second_status:<10} {copy_status:<10} {detail}")
        
        # 生成总结报告
        self._generate_summary()
    
    def _generate_summary(self):
        """生成总结报告"""
        print(f"\n{'='*120}")
        print(f"处理完成!")
        print(f"{'='*120}")
        
        print(f"\n📊 处理统计:")
        print(f"  总PDF文件数: {self.stats['total_pdfs']}")
        print(f"  第一特征通过: {self.stats['first_feature_passed']}")
        print(f"  第二特征通过: {self.stats['second_feature_passed']}")
        print(f"  成功复制文件: {self.stats['copied_files']}")
        print(f"  处理错误: {self.stats['errors']}")
        print(f"  特定文件分析: {self.stats['specific_files_analyzed']}")
        
        if self.stats['total_pdfs'] > 0:
            first_pass_rate = self.stats['first_feature_passed'] / self.stats['total_pdfs'] * 100
            second_pass_rate = self.stats['second_feature_passed'] / self.stats['total_pdfs'] * 100
            copy_rate = self.stats['copied_files'] / self.stats['total_pdfs'] * 100
            
            print(f"\n📈 通过率:")
            print(f"  第一特征通过率: {first_pass_rate:.1f}%")
            print(f"  第二特征通过率: {second_pass_rate:.1f}%")
            print(f"  最终复制率: {copy_rate:.1f}%")
        
        # 显示成功复制的文件
        copied_files = [r for r in self.results if r.get('copied', False)]
        if copied_files:
            print(f"\n🎉 成功复制的文件 ({len(copied_files)}个):")
            print(f"{'序号':<4} {'文件名':<60} {'目标路径'}")
            print(f"{'-'*4} {'-'*60} {'-'*50}")
            
            for i, result in enumerate(copied_files):
                file_name = result['file_name']
                if len(file_name) > 57:
                    file_name = file_name[:54] + "..."
                
                target_path = result.get('target_path', '未知')
                if len(target_path) > 47:
                    target_path = target_path[:44] + "..."
                
                print(f"{i+1:<4} {file_name:<60} {target_path}")
        
        # 保存详细结果到JSON文件
        output_file = f"unified_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary_data = {
            'scan_time': datetime.now().isoformat(),
            'source_directory': str(self.source_folder),
            'target_directory': str(self.target_folder),
            'statistics': self.stats,
            'files': self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细结果已保存到: {output_file}")
        print(f"📁 符合条件的PDF文件已复制到: {self.target_folder}")
    
    def run_analysis(self, mode="recursive", specific_files=None):
        """
        运行分析的主入口
        
        Args:
            mode: 分析模式 ("recursive" 或 "specific")
            specific_files: 指定文件列表（仅在specific模式下使用）
        """
        if mode == "recursive":
            logger.info("运行递归分类模式")
            self.recursive_classify()
        elif mode == "specific":
            logger.info("运行特定文件分析模式")
            if specific_files:
                # 可以传入自定义文件列表
                pass
            return self.analyze_specific_files()
        else:
            raise ValueError(f"不支持的分析模式: {mode}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='统一PDF分析工具')
    parser.add_argument('source_folder', help='源文件夹路径')
    parser.add_argument('--target', '-t', default='jc', help='目标文件夹路径（默认为jc）')
    parser.add_argument('--mode', '-m', choices=['recursive', 'specific'], default='recursive',
                       help='分析模式：recursive(递归分类) 或 specific(特定文件分析)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查源文件夹是否存在
    if not os.path.exists(args.source_folder):
        print(f"❌ 源文件夹不存在: {args.source_folder}")
        return
    
    # 创建分析器并开始处理
    analyzer = UnifiedPDFAnalyzer(args.source_folder, args.target)
    
    if args.mode == "recursive":
        analyzer.run_analysis(mode="recursive")
    elif args.mode == "specific":
        results = analyzer.run_analysis(mode="specific")
        # 输出特定文件分析结果
        print(f"\n=== 特定文件分析完成 ===")
        print(f"分析了 {len(results)} 个文件")
        print(f"结果图片已保存到: {args.target} 文件夹")
    else:
        print(f"❌ 不支持的分析模式: {args.mode}")

if __name__ == "__main__":
    main()
