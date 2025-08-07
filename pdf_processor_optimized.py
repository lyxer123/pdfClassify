#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文件处理脚本 - 优化版标准文档检测和分类
基于mb5.png的优化版本
"""

import cv2
import numpy as np
import os
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
from main_optimized import OptimizedStandardDocumentFeatureExtractor

class OptimizedPDFProcessor:
    def __init__(self, source_drive="I:", target_folder="jc"):
        self.source_drive = Path(source_drive)
        self.target_folder = Path(target_folder)
        self.target_folder.mkdir(exist_ok=True)
        
    def get_pdf_files(self):
        """递归搜索指定驱动器下的所有PDF文件"""
        if not self.source_drive.exists():
            print(f"错误: 驱动器 {self.source_drive} 不存在")
            return []
        
        pdf_files = []
        print(f"正在搜索 {self.source_drive} 盘下的所有PDF文件...")
        
        try:
            # 递归搜索所有PDF文件
            for pdf_file in self.source_drive.rglob("*.pdf"):
                pdf_files.append(pdf_file)
                if len(pdf_files) % 100 == 0:  # 每找到100个文件显示一次进度
                    print(f"已找到 {len(pdf_files)} 个PDF文件...")
        except PermissionError as e:
            print(f"警告: 某些文件夹访问被拒绝: {e}")
        except Exception as e:
            print(f"搜索过程中出现错误: {e}")
        
        print(f"总共找到 {len(pdf_files)} 个PDF文件")
        return pdf_files
    
    def pdf_to_images(self, pdf_path):
        """将PDF转换为图像"""
        try:
            doc = fitz.open(str(pdf_path))
            images = []
            # 只处理第一页
            if len(doc) > 0:
                page = doc.load_page(0)  # 只获取第一页
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                images.append(opencv_image)
            doc.close()
            return images
        except Exception as e:
            print(f"转换PDF失败: {e}")
            return []
    
    def analyze_page_optimized(self, image, page_num):
        """使用优化版特征提取器分析页面"""
        temp_path = f"temp_page_{page_num}.png"
        cv2.imwrite(temp_path, image)
        try:
            extractor = OptimizedStandardDocumentFeatureExtractor(temp_path)
            result = extractor.extract_features()
            os.remove(temp_path)
            return result
        except Exception as e:
            print(f"分析页面时出错: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
    
    def process_pdf(self, pdf_path):
        """处理单个PDF文件"""
        print(f"\n处理: {pdf_path.name}")
        print(f"路径: {pdf_path}")
        
        images = self.pdf_to_images(pdf_path)
        if not images:
            return {"success": False, "copied": False, "reason": "无法转换PDF"}
        
        print(f"处理第一页")
        image = images[0]  # 只处理第一页
        result = self.analyze_page_optimized(image, 1)
        
        if result and 'error' not in result:
            is_standard = result['is_standard_document']
            overall_score = result['overall_score']
            mb4_similarity = result['mb4_similarity']
            
            print(f"  优化版分析结果:")
            print(f"    标准文档判断: {'✅ 是' if is_standard else '❌ 否'}")
            print(f"    综合评分: {overall_score:.3f}")
            print(f"    mb4相似度: {mb4_similarity:.3f}")
            
            # 显示区域分析结果
            region_analysis = result['region_analysis']
            print(f"  区域分析:")
            for region_name, analysis in region_analysis.items():
                region_name_cn = {'upper': '上部', 'middle': '中部', 'lower': '下部'}[region_name]
                print(f"    {region_name_cn}: 留白{analysis['whitespace_ratio']:.3f}, "
                      f"关键词{'✅' if analysis['has_keywords'] else '❌'}")
            
            # 判断是否满足条件
            if is_standard:
                print(f"  ✅ 满足标准文档条件")
                copied = self.copy_file(pdf_path)
                return {"success": True, "copied": copied, "is_standard": True}
            else:
                print(f"  ❌ 不满足标准文档条件")
                return {"success": True, "copied": False, "is_standard": False}
        else:
            error_msg = result.get('error', '未知错误') if result else '分析失败'
            print(f"  ❌ 分析失败: {error_msg}")
            return {"success": False, "copied": False, "reason": error_msg}
    
    def copy_file(self, pdf_path):
        """拷贝文件到目标文件夹"""
        try:
            target_path = self.target_folder / pdf_path.name
            shutil.copy2(pdf_path, target_path)
            print(f"  📋 已拷贝到: {target_path}")
            return True
        except Exception as e:
            print(f"  ❌ 拷贝失败: {e}")
            return False
    
    def process_all(self):
        """批量处理所有PDF文件"""
        print("PDF 文件批量处理 - 优化版（基于mb5.png）")
        print("=" * 60)
        
        pdf_files = self.get_pdf_files()
        if not pdf_files:
            print("没有找到PDF文件")
            return
        
        successful_copies = 0
        total_files = len(pdf_files)
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{total_files}] {pdf_path.name}")
            
            result = self.process_pdf(pdf_path)
            
            if result.get("copied", False):
                successful_copies += 1
        
        print(f"\n{'='*60}")
        print("处理完成!")
        print(f"总文件数: {total_files}")
        print(f"成功拷贝: {successful_copies}")
        print(f"拷贝的文件保存在: {self.target_folder.absolute()}")
        print("注意: 仅处理了每个PDF文件的第一页")
        print("优化版特点:")
        print("- 基于mb5.png的3个蓝色框区域分析")
        print("- 统计各区域留白比例")
        print("- 上部和下部文字识别（包含'标准'和'发布'）")
        print("- 结合mb4.png的文字分布特征")

def main():
    """主函数"""
    print("PDF标准文档分类系统 - 优化版")
    print("基于mb5.png的3个蓝色框区域分析")
    print("=" * 60)
    
    # 创建处理器实例
    processor = OptimizedPDFProcessor(source_drive="I:", target_folder="jc")
    
    # 执行批量处理
    processor.process_all()

if __name__ == "__main__":
    main()
