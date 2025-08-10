#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
递归批量验证PDF文件是否符合标准
使用第一特征（颜色特征）和第二特征（两条长黑线）进行检验
将符合标准的PDF文件复制到jc文件夹下
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from main import PDFFeatureExtractor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFBatchValidator:
    """PDF批量验证器"""
    
    def __init__(self, source_folder, target_folder="jc"):
        self.source_folder = Path(source_folder)
        self.target_folder = Path(target_folder)
        self.extractor = PDFFeatureExtractor()
        
        # 确保目标文件夹存在
        self.target_folder.mkdir(exist_ok=True)
        
        # 验证结果统计
        self.stats = {
            'total_files': 0,
            'compliant_files': 0,
            'non_compliant_files': 0,
            'error_files': 0,
            'copied_files': 0
        }
    
    def validate_path(self):
        """验证源文件夹路径"""
        try:
            if not self.source_folder.exists():
                logger.error(f"源文件夹不存在: {self.source_folder}")
                return False
            
            if not self.source_folder.is_dir():
                logger.error(f"源路径不是文件夹: {self.source_folder}")
                return False
            
            # 尝试访问文件夹
            try:
                test_file = next(self.source_folder.iterdir(), None)
                logger.info(f"源文件夹验证成功: {self.source_folder}")
                return True
            except PermissionError:
                logger.error(f"没有权限访问文件夹: {self.source_folder}")
                return False
            except Exception as e:
                logger.error(f"访问文件夹时出错: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"路径验证失败: {str(e)}")
            return False
    
    def find_all_pdfs_recursively(self):
        """递归查找所有PDF文件"""
        pdf_files = []
        
        logger.info(f"正在递归搜索PDF文件...")
        
        try:
            # 递归搜索所有PDF文件
            for root, dirs, files in os.walk(self.source_folder):
                # 跳过某些系统文件夹
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$')]
                
                for file in files:
                    if file.lower().endswith('.pdf'):
                        try:
                            pdf_path = Path(root) / file
                            # 验证文件是否可读
                            if pdf_path.is_file() and os.access(pdf_path, os.R_OK):
                                pdf_files.append(pdf_path)
                        except Exception as e:
                            logger.warning(f"跳过文件 {file}: {str(e)}")
                            continue
                
                # 每处理100个文件夹显示一次进度
                if len(pdf_files) % 100 == 0 and len(pdf_files) > 0:
                    logger.info(f"已找到 {len(pdf_files)} 个PDF文件...")
        
        except PermissionError as e:
            logger.error(f"权限不足，无法访问某些文件夹: {str(e)}")
        except Exception as e:
            logger.error(f"递归搜索时出错: {str(e)}")
        
        # 去重（避免大小写重复）
        unique_pdfs = []
        seen_names = set()
        for pdf_path in pdf_files:
            if pdf_path.name.lower() not in seen_names:
                unique_pdfs.append(pdf_path)
                seen_names.add(pdf_path.name.lower())
        
        logger.info(f"递归搜索完成，找到 {len(unique_pdfs)} 个唯一PDF文件")
        return unique_pdfs
    
    def validate_pdf_file(self, pdf_path):
        """验证单个PDF文件是否符合标准"""
        try:
            logger.info(f"正在验证: {pdf_path.name}")
            
            # 转换PDF页面为图片
            images = self.extractor.pdf_to_images(pdf_path, max_pages=3)
            if not images:
                logger.error(f"PDF转换失败: {pdf_path.name}")
                return False, "PDF转换失败"
            
            # 分析每页的特征
            page_results = []
            overall_compliance = True
            
            for i, image in enumerate(images):
                logger.info(f"  分析第 {i+1} 页特征...")
                
                # 第一特征：颜色特征分析
                color_features = self.extractor.analyze_color_features(image)
                if not color_features:
                    logger.warning(f"  第 {i+1} 页颜色特征分析失败")
                    continue
                
                # 第二特征：两条长黑线检测
                second_feature = self.extractor.detect_mb_second_feature(image)
                if second_feature:
                    color_features['second_feature'] = second_feature
                
                # 检查是否符合标准
                compliance = self.extractor.check_standard_compliance(color_features)
                
                page_results.append({
                    'page_number': i + 1,
                    'color_features': color_features,
                    'second_feature': second_feature,
                    'compliance': compliance
                })
                
                if not compliance:
                    overall_compliance = False
                
                # 输出详细检测结果
                logger.info(f"  第 {i+1} 页检测结果:")
                logger.info(f"    颜色特征: {'✓' if color_features else '✗'}")
                if second_feature:
                    logger.info(f"    第二特征: {'✓' if second_feature['has_second_feature'] else '✗'}")
                    if not second_feature['has_second_feature']:
                        logger.info(f"      失败原因: {second_feature['reason']}")
                logger.info(f"    整体符合性: {'✓' if compliance else '✗'}")
            
            if not page_results:
                return False, "所有页面分析失败"
            
            # 检查是否所有页面都符合标准
            if overall_compliance:
                logger.info(f"✓ {pdf_path.name}: 所有页面都符合标准")
                return True, "符合标准"
            else:
                logger.info(f"✗ {pdf_path.name}: 部分页面不符合标准")
                return False, "部分页面不符合标准"
                
        except Exception as e:
            logger.error(f"验证文件时出错 {pdf_path.name}: {str(e)}")
            return False, f"验证错误: {str(e)}"
    
    def copy_compliant_file(self, pdf_path):
        """将符合标准的PDF文件复制到目标文件夹"""
        try:
            # 生成目标文件名（避免重名）
            target_filename = pdf_path.name
            target_path = self.target_folder / target_filename
            
            # 如果文件已存在，添加序号
            counter = 1
            while target_path.exists():
                name_without_ext = pdf_path.stem
                ext = pdf_path.suffix
                target_filename = f"{name_without_ext}_{counter}{ext}"
                target_path = self.target_folder / target_filename
                counter += 1
            
            # 复制文件
            shutil.copy2(pdf_path, target_path)
            logger.info(f"已复制到: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"复制文件失败 {pdf_path.name}: {str(e)}")
            return False
    
    def process_folder(self):
        """处理整个文件夹的PDF文件"""
        logger.info(f"开始处理文件夹: {self.source_folder}")
        logger.info(f"目标文件夹: {self.target_folder}")
        
        # 验证源文件夹路径
        if not self.validate_path():
            return
        
        # 递归查找所有PDF文件
        pdf_files = self.find_all_pdfs_recursively()
        
        if not pdf_files:
            logger.warning(f"在文件夹中未找到PDF文件: {self.source_folder}")
            return
        
        self.stats['total_files'] = len(pdf_files)
        
        # 处理每个PDF文件
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"\n[{i}/{len(pdf_files)}] 处理文件: {pdf_file.name}")
            logger.info(f"文件路径: {pdf_file}")
            
            # 验证PDF文件
            is_compliant, reason = self.validate_pdf_file(pdf_file)
            
            result = {
                'file_name': pdf_file.name,
                'file_path': str(pdf_file),
                'is_compliant': is_compliant,
                'reason': reason,
                'copied': False
            }
            
            # 如果符合标准，复制到目标文件夹
            if is_compliant:
                self.stats['compliant_files'] += 1
                if self.copy_compliant_file(pdf_file):
                    result['copied'] = True
                    self.stats['copied_files'] += 1
                    logger.info(f"✓ 文件已复制: {pdf_file.name}")
                else:
                    logger.error(f"✗ 文件复制失败: {pdf_file.name}")
            else:
                self.stats['non_compliant_files'] += 1
            
            results.append(result)
        
        # 输出统计结果
        self.print_summary(results)
        
        # 保存详细结果
        self.save_detailed_results(results)
    
    def print_summary(self, results):
        """打印处理结果摘要"""
        logger.info("\n" + "="*60)
        logger.info("PDF验证结果摘要")
        logger.info("="*60)
        logger.info(f"总文件数: {self.stats['total_files']}")
        logger.info(f"符合标准: {self.stats['compliant_files']}")
        logger.info(f"不符合标准: {self.stats['non_compliant_files']}")
        logger.info(f"处理错误: {self.stats['error_files']}")
        logger.info(f"成功复制: {self.stats['copied_files']}")
        
        if self.stats['total_files'] > 0:
            compliance_rate = self.stats['compliant_files'] / self.stats['total_files'] * 100
            logger.info(f"符合标准比例: {compliance_rate:.1f}%")
        
        # 显示符合标准的文件列表
        if self.stats['compliant_files'] > 0:
            logger.info("\n符合标准的文件:")
            for result in results:
                if result['is_compliant']:
                    status = "✓ 已复制" if result['copied'] else "✗ 复制失败"
                    logger.info(f"  {result['file_name']} - {status}")
        
        # 显示不符合标准的文件列表
        if self.stats['non_compliant_files'] > 0:
            logger.info("\n不符合标准的文件:")
            for result in results:
                if not result['is_compliant']:
                    logger.info(f"  {result['file_name']} - {result['reason']}")
    
    def save_detailed_results(self, results):
        """保存详细结果到JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"pdf_validation_results_{timestamp}.json"
        output_path = Path(output_filename)
        
        # 准备保存的数据
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'source_folder': str(self.source_folder),
            'target_folder': str(self.target_folder),
            'statistics': self.stats,
            'results': results
        }
        
        try:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            logger.info(f"详细结果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")

def main():
    """主函数"""
    # 设置源文件夹路径（用户指定的路径）
    source_folder = r"I:\1T硬盘D"
    target_folder = "jc"
    
    logger.info(f"PDF递归批量验证工具")
    logger.info(f"源文件夹: {source_folder}")
    logger.info(f"目标文件夹: {target_folder}")
    logger.info(f"将使用第一特征（颜色特征）和第二特征（两条长黑线）进行验证")
    
    # 创建验证器并处理文件夹
    validator = PDFBatchValidator(source_folder, target_folder)
    validator.process_folder()
    
    logger.info("\n处理完成！")

if __name__ == "__main__":
    main()
