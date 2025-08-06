#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文件处理脚本 - 检测标准文档特征并分类
"""

import cv2
import numpy as np
import os
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
from main import StandardDocumentFeatureExtractor

class PDFProcessor:
    def __init__(self, source_drive="E:", target_folder="jc"):
        self.source_drive = Path(source_drive)
        self.target_folder = Path(target_folder)
        self.target_folder.mkdir(exist_ok=True)
        
    def get_pdf_files(self):
        """递归搜索E:盘下的所有PDF文件"""
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
        try:
            doc = fitz.open(str(pdf_path))
            images = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
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
    
    def analyze_page(self, image, page_num):
        temp_path = f"temp_page_{page_num}.png"
        cv2.imwrite(temp_path, image)
        try:
            extractor = StandardDocumentFeatureExtractor(temp_path)
            features = extractor.extract_features()
            os.remove(temp_path)
            return features
        except:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
    
    def process_pdf(self, pdf_path):
        print(f"\n处理: {pdf_path.name}")
        print(f"路径: {pdf_path}")
        images = self.pdf_to_images(pdf_path)
        if not images:
            return {"success": False, "copied": False}
        
        print(f"共 {len(images)} 页")
        max_features = 0
        best_page = 0
        best_features = None
        
        for page_num, image in enumerate(images):
            features = self.analyze_page(image, page_num + 1)
            if features:
                detected = features['detected_features']
                feature_details = features['features']
                print(f"  第{page_num + 1}页: {detected}/7 特征")
                
                # 检查特征4、5、6是否同时满足
                feature_4_detected = feature_details['feature_4_first_horizontal_line']['detected']
                feature_5_detected = feature_details['feature_5_standard_names']['detected']
                feature_6_detected = feature_details['feature_6_publication_time']['detected']
                
                # 新标准：特征数>=5个，且相对位置比较符合
                total_features_ok = detected >= 5
                critical_features_ok = feature_4_detected and feature_5_detected and feature_6_detected
                
                # 计算位置符合度（基于confidence值）
                position_confidence = 0.0
                if feature_details:
                    confidences = []
                    for feature_name, feature_data in feature_details.items():
                        if feature_data['detected'] and 'confidence' in feature_data:
                            confidences.append(feature_data['confidence'])
                    if confidences:
                        position_confidence = sum(confidences) / len(confidences)
                
                # 获取模板比对相似度
                template_similarity = features.get('template_similarity', 0.0)
                
                # 检查是否满足新条件：特征数>=5个，且相对位置比较符合，且模板相似度较高
                if total_features_ok and critical_features_ok and position_confidence > 0.7 and template_similarity > 0.3:
                    print(f"  ✅ 第{page_num + 1}页满足条件（特征数{detected}>=5，关键特征齐全，位置符合度{position_confidence:.2f}，模板相似度{template_similarity:.3f}）")
                    return {"success": True, "copied": True, "features": detected, "confidence": position_confidence, "template_similarity": template_similarity}
                
                # 记录最佳结果（即使不满足条件）
                if detected > max_features:
                    max_features = detected
                    best_page = page_num + 1
                    best_features = feature_details
                
                # 第一页满足条件，直接返回
                if page_num == 0 and total_features_ok and critical_features_ok and position_confidence > 0.7 and template_similarity > 0.3:
                    print(f"  ✅ 第一页满足条件，拷贝文件")
                    return {"success": True, "copied": True, "features": detected, "confidence": position_confidence, "template_similarity": template_similarity}
        
        # 如果没有页面满足条件，显示详细信息
        if best_features:
            feature_4_detected = best_features['feature_4_first_horizontal_line']['detected']
            feature_5_detected = best_features['feature_5_standard_names']['detected']
            feature_6_detected = best_features['feature_6_publication_time']['detected']
            
            # 计算最佳页面的位置符合度和模板相似度
            best_confidences = []
            for feature_name, feature_data in best_features.items():
                if feature_data['detected'] and 'confidence' in feature_data:
                    best_confidences.append(feature_data['confidence'])
            best_position_confidence = sum(best_confidences) / len(best_confidences) if best_confidences else 0.0
            
            # 获取最佳页面的模板相似度（如果有的话）
            best_template_similarity = 0.0
            if hasattr(features, 'get') and features.get('template_similarity'):
                best_template_similarity = features.get('template_similarity', 0.0)
            
            print(f"  ❌ 无页面满足条件")
            print(f"    最佳页面（第{best_page}页）: {max_features}/7 特征")
            print(f"    特征4（第一横线）: {'✅' if feature_4_detected else '❌'}")
            print(f"    特征5（标准名称）: {'✅' if feature_5_detected else '❌'}")
            print(f"    特征6（发布时间）: {'✅' if feature_6_detected else '❌'}")
            print(f"    总特征数>=5: {'✅' if max_features >= 5 else '❌'}")
            print(f"    位置符合度: {best_position_confidence:.2f}")
            print(f"    模板相似度: {best_template_similarity:.3f}")
        
        return {"success": True, "copied": False, "features": max_features}
    
    def copy_file(self, pdf_path):
        try:
            target_path = self.target_folder / pdf_path.name
            # 如果目标文件已存在，添加序号
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = self.target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(pdf_path, target_path)
            print(f"  📋 已拷贝到: {target_path}")
            return True
        except Exception as e:
            print(f"  ❌ 拷贝失败: {e}")
            return False
    
    def process_all(self):
        print("PDF 文件批量处理 - E:盘扫描")
        print("=" * 50)
        
        pdf_files = self.get_pdf_files()
        if not pdf_files:
            print("未找到任何PDF文件")
            return
        
        copied_count = 0
        total_count = len(pdf_files)
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{total_count}] {pdf_path.name}")
            result = self.process_pdf(pdf_path)
            
            if result["success"] and result["copied"]:
                if self.copy_file(pdf_path):
                    copied_count += 1
        
        print(f"\n处理完成!")
        print(f"总文件数: {total_count}")
        print(f"成功拷贝: {copied_count}")
        print(f"拷贝的文件保存在: {self.target_folder.absolute()}")

def main():
    processor = PDFProcessor()
    processor.process_all()

if __name__ == "__main__":
    main() 