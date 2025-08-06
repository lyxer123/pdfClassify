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
    def __init__(self, source_drive="E:\\1T硬盘D\\2个项目资料\\充电控制器\\办公\\国网控制器\\国网2.0控制器\\国网六统一\\发布版", target_folder="jc"):
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
        
        print(f"处理第一页")
        image = images[0]  # 只处理第一页
        features = self.analyze_page(image, 1)
        
        if features:
            detected = features['detected_features']
            feature_details = features['features']
            print(f"  第一页: {detected}/7 特征")
            
            # 显示所有特征的检测结果
            print(f"  详细特征检测结果:")
            for feature_name, feature_data in feature_details.items():
                status = "✅" if feature_data['detected'] else "❌"
                confidence = feature_data.get('confidence', 0.0)
                print(f"    {feature_name}: {status} (置信度: {confidence:.2f})")
            
            # 检查特征4、5、6是否同时满足
            feature_4_detected = feature_details['feature_4_first_horizontal_line']['detected']
            feature_5_detected = feature_details['feature_5_standard_names']['detected']
            feature_6_detected = feature_details['feature_6_publication_time']['detected']
            
            # 调整后的标准：特征数>=4个，且关键特征至少满足2个
            total_features_ok = detected >= 4  # 降低特征数要求
            critical_features_count = sum([feature_4_detected, feature_5_detected, feature_6_detected])
            critical_features_ok = critical_features_count >= 2  # 只需要2个关键特征
            
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
            
            print(f"  检测条件评估:")
            print(f"    总特征数>=4: {'✅' if total_features_ok else '❌'} ({detected}/7)")
            print(f"    关键特征>=2个: {'✅' if critical_features_ok else '❌'} ({critical_features_count}/3)")
            print(f"    位置符合度>0.6: {'✅' if position_confidence > 0.6 else '❌'} ({position_confidence:.2f})")
            print(f"    模板相似度>0.2: {'✅' if template_similarity > 0.2 else '❌'} ({template_similarity:.3f})")
            
            # 检查是否满足调整后的条件：特征数>=4个，关键特征>=2个，位置符合度>0.6，模板相似度>0.2
            if total_features_ok and critical_features_ok and position_confidence > 0.6 and template_similarity > 0.2:
                print(f"  ✅ 第一页满足条件（特征数{detected}>=4，关键特征{critical_features_count}/3，位置符合度{position_confidence:.2f}，模板相似度{template_similarity:.3f}）")
                return {"success": True, "copied": True, "features": detected, "confidence": position_confidence, "template_similarity": template_similarity}
            else:
                # 显示详细信息
                print(f"  ❌ 第一页不满足条件")
                print(f"    特征4（第一横线）: {'✅' if feature_4_detected else '❌'}")
                print(f"    特征5（标准名称）: {'✅' if feature_5_detected else '❌'}")
                print(f"    特征6（发布时间）: {'✅' if feature_6_detected else '❌'}")
                print(f"    总特征数>=4: {'✅' if total_features_ok else '❌'} ({detected}/7)")
                print(f"    关键特征>=2个: {'✅' if critical_features_ok else '❌'} ({critical_features_count}/3)")
                print(f"    位置符合度: {position_confidence:.2f}")
                print(f"    模板相似度: {template_similarity:.3f}")
        
        return {"success": True, "copied": False, "features": detected if features else 0}
    
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
        print("PDF 文件批量处理 - E:盘扫描（仅第一页）")
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
        print(f"注意: 仅处理了每个PDF文件的第一页")

def main():
    processor = PDFProcessor()
    processor.process_all()

if __name__ == "__main__":
    main() 