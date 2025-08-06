#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Pattern Recognition - Standard Document Feature Extraction
针对标准文档的6个特征抽取系统（基于mb4.png）
"""

import cv2
import numpy as np
from PIL import Image
import re
from typing import Dict, List, Tuple, Optional
import os

class StandardDocumentFeatureExtractor:
    """
    标准文档6个特征抽取器（基于mb4.png）
    
    6个特征（从上往下）：
    1. 标准logo - 页面上部靠右
    2. 标准类别 - 页面上部，左右贯穿
    3. 标准号和横线 - 上部靠右，标准号在横线上方，横线左右贯穿
    4. 标准的中文和英文名称 - 页面正中间，2行以上
    5. 发布和实施时间 - 页面下部，横线贯穿左右，横线上方左右各有一排字
    6. 发布单位 - 页面下部，至少一行字
    """
    
    def __init__(self, image_path: str):
        """
        初始化抽取器
        
        Args:
            image_path: 图片文件路径
        """
        self.image_path = image_path
        self.image = None
        self.gray_image = None
        self.features = {}
        
    def load_image(self) -> bool:
        """
        加载图片
        
        Returns:
            bool: 是否成功加载
        """
        try:
            self.image = cv2.imread(self.image_path)
            if self.image is None:
                print(f"无法加载图片: {self.image_path}")
                return False
                
            self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            print(f"成功加载图片: {self.image_path}")
            print(f"图片尺寸: {self.image.shape}")
            return True
        except Exception as e:
            print(f"加载图片时出错: {e}")
            return False
    
    def detect_horizontal_lines(self) -> List[Tuple[int, int, int, int]]:
        """
        检测水平横线
        
        Returns:
            List[Tuple]: 横线坐标列表 (x1, y1, x2, y2)
        """
        # 使用霍夫变换检测直线
        edges = cv2.Canny(self.gray_image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, 
                               minLineLength=80, maxLineGap=15)
        
        horizontal_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 判断是否为水平线（y坐标相近）
                if abs(y1 - y2) < 10 and abs(x1 - x2) > 50:
                    horizontal_lines.append((x1, y1, x2, y2))
        
        return horizontal_lines
    
    def detect_text_regions(self) -> List[Tuple[int, int, int, int, float]]:
        """
        检测文本区域（基于连通组件分析）
        
        Returns:
            List[Tuple]: 文本区域列表 (x, y, w, h, density)
        """
        # 二值化
        _, binary = cv2.threshold(self.gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 过滤太小的区域
            if w < 15 or h < 8:
                continue
                
            # 计算区域密度
            roi = binary[y:y+h, x:x+w]
            density = np.sum(roi == 255) / (w * h)
            
            # 过滤密度过低的区域
            if density > 0.08:
                text_regions.append((x, y, w, h, density))
        
        return text_regions
    
    def analyze_document_structure(self) -> Dict:
        """
        分析文档结构
        
        Returns:
            Dict: 文档结构信息
        """
        height, width = self.gray_image.shape
        
        # 定义页面区域
        top_region = int(height * 0.2)      # 上部20%
        middle_region = int(height * 0.6)   # 中部60%
        bottom_region = int(height * 0.2)   # 下部20%
        
        # 定义左右区域
        left_region = int(width * 0.3)      # 左侧30%
        right_region = int(width * 0.7)     # 右侧70%
        
        # 检测文本区域
        text_regions = self.detect_text_regions()
        
        # 检测横线
        horizontal_lines = self.detect_horizontal_lines()
        
        # 按区域分类文本
        regions = {
            'top_left': [],
            'top_middle': [],
            'top_right': [],
            'middle': [],
            'bottom_left': [],
            'bottom_middle': [],
            'bottom_right': []
        }
        
        for x, y, w, h, density in text_regions:
            center_x = x + w // 2
            center_y = y + h // 2
            
            # 上部区域
            if center_y < top_region:
                if center_x < left_region:
                    regions['top_left'].append((x, y, w, h, density))
                elif center_x > right_region:
                    regions['top_right'].append((x, y, w, h, density))
                else:
                    regions['top_middle'].append((x, y, w, h, density))
            # 中部区域
            elif center_y < top_region + middle_region:
                regions['middle'].append((x, y, w, h, density))
            # 下部区域
            else:
                if center_x < left_region:
                    regions['bottom_left'].append((x, y, w, h, density))
                elif center_x > right_region:
                    regions['bottom_right'].append((x, y, w, h, density))
                else:
                    regions['bottom_middle'].append((x, y, w, h, density))
        
        return {
            'regions': regions,
            'horizontal_lines': horizontal_lines,
            'width': width,
            'height': height
        }
    
    def _extract_six_features(self, regions: Dict, horizontal_lines: List, width: int, height: int) -> Dict:
        """
        提取6个特征
        
        Args:
            regions: 文本区域
            horizontal_lines: 横线列表
            width: 图片宽度
            height: 图片高度
            
        Returns:
            Dict: 特征检测结果
        """
        features = {}
        
        # 1. 标准logo - 页面上部靠右
        top_right_regions = regions['top_right']
        logo_detected = len(top_right_regions) > 0
        logo_confidence = min(1.0, len(top_right_regions) * 0.3) if logo_detected else 0.0
        features['feature_1_standard_logo'] = {
            'detected': logo_detected,
            'confidence': logo_confidence,
            'description': '标准logo - 页面上部靠右'
        }
        
        # 2. 标准类别 - 页面上部，左右贯穿
        top_middle_regions = regions['top_middle']
        category_detected = len(top_middle_regions) > 0
        # 检查是否有跨越宽度的区域
        wide_regions = [r for r in top_middle_regions if r[2] > width * 0.6]
        if wide_regions:
            category_confidence = 0.8
        else:
            category_confidence = min(1.0, len(top_middle_regions) * 0.4) if category_detected else 0.0
        features['feature_2_standard_category'] = {
            'detected': category_detected,
            'confidence': category_confidence,
            'description': '标准类别 - 页面上部，左右贯穿'
        }
        
        # 3. 标准号和横线 - 上部靠右，标准号在横线上方，横线左右贯穿
        # 检查上部横线
        upper_lines = [line for line in horizontal_lines if line[1] < height * 0.4]
        upper_line_detected = len(upper_lines) > 0
        
        # 检查上部右侧文本（标准号）
        top_right_text = regions['top_right']
        standard_number_detected = len(top_right_text) > 0
        
        # 综合判断
        standard_number_line_detected = upper_line_detected and standard_number_detected
        standard_number_line_confidence = 0.0
        if standard_number_line_detected:
            # 检查标准号是否在横线上方
            if upper_lines and top_right_text:
                line_y = upper_lines[0][1]
                text_y = min([r[1] for r in top_right_text])
                if text_y < line_y:
                    standard_number_line_confidence = 0.8
                else:
                    standard_number_line_confidence = 0.5
            else:
                standard_number_line_confidence = 0.6
        
        features['feature_3_standard_number_line'] = {
            'detected': standard_number_line_detected,
            'confidence': standard_number_line_confidence,
            'description': '标准号和横线 - 上部靠右，标准号在横线上方，横线左右贯穿'
        }
        
        # 4. 标准的中文和英文名称 - 页面正中间，2行以上
        middle_regions = regions['middle']
        # 检查是否有多个文本区域（多行）
        multi_line_detected = len(middle_regions) >= 2
        middle_confidence = min(1.0, len(middle_regions) * 0.3) if multi_line_detected else 0.0
        features['feature_4_standard_names'] = {
            'detected': multi_line_detected,
            'confidence': middle_confidence,
            'description': '标准的中文和英文名称 - 页面正中间，2行以上'
        }
        
        # 5. 发布和实施时间 - 页面下部，横线贯穿左右，横线上方左右各有一排字
        # 检查下部横线
        lower_lines = [line for line in horizontal_lines if line[1] > height * 0.6]
        lower_line_detected = len(lower_lines) > 0
        
        # 检查下部左右文本
        bottom_left_text = regions['bottom_left']
        bottom_right_text = regions['bottom_right']
        bottom_text_detected = len(bottom_left_text) > 0 and len(bottom_right_text) > 0
        
        # 综合判断
        publication_time_detected = lower_line_detected and bottom_text_detected
        publication_time_confidence = 0.0
        if publication_time_detected:
            if lower_lines and bottom_left_text and bottom_right_text:
                # 检查文本是否在横线上方
                line_y = lower_lines[0][1]
                left_text_y = min([r[1] for r in bottom_left_text])
                right_text_y = min([r[1] for r in bottom_right_text])
                if left_text_y < line_y and right_text_y < line_y:
                    publication_time_confidence = 0.8
                else:
                    publication_time_confidence = 0.5
            else:
                publication_time_confidence = 0.6
        
        features['feature_5_publication_time'] = {
            'detected': publication_time_detected,
            'confidence': publication_time_confidence,
            'description': '发布和实施时间 - 页面下部，横线贯穿左右，横线上方左右各有一排字'
        }
        
        # 6. 发布单位 - 页面下部，至少一行字
        bottom_middle_regions = regions['bottom_middle']
        publishing_unit_detected = len(bottom_middle_regions) > 0
        publishing_unit_confidence = min(1.0, len(bottom_middle_regions) * 0.4) if publishing_unit_detected else 0.0
        features['feature_6_publishing_unit'] = {
            'detected': publishing_unit_detected,
            'confidence': publishing_unit_confidence,
            'description': '发布单位 - 页面下部，至少一行字'
        }
        
        return features
    
    def compare_with_template(self, template_path: str = "mb4.png") -> float:
        """
        与模板图片进行比对（优化版本）
        
        Args:
            template_path: 模板图片路径
            
        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            if not os.path.exists(template_path):
                print(f"模板文件不存在: {template_path}")
                return 0.0
            
            # 加载模板图片
            template = cv2.imread(template_path)
            if template is None:
                print(f"无法加载模板图片: {template_path}")
                return 0.0
            
            # 预处理：转换为灰度图
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            
            # 多尺度模板匹配
            best_similarity = 0.0
            scales = [0.8, 0.9, 1.0, 1.1, 1.2]  # 尝试不同的缩放比例
            
            for scale in scales:
                # 计算新的尺寸
                new_width = int(template.shape[1] * scale)
                new_height = int(template.shape[0] * scale)
                
                # 调整模板大小
                resized_template = cv2.resize(template_gray, (new_width, new_height))
                
                # 确保调整后的模板不大于原图
                if new_width > image_gray.shape[1] or new_height > image_gray.shape[0]:
                    continue
                
                # 使用多种匹配方法
                methods = [
                    cv2.TM_CCOEFF_NORMED,
                    cv2.TM_CCORR_NORMED,
                    cv2.TM_SQDIFF_NORMED
                ]
                
                for method in methods:
                    try:
                        result = cv2.matchTemplate(image_gray, resized_template, method)
                        
                        if method == cv2.TM_SQDIFF_NORMED:
                            # TM_SQDIFF_NORMED 越小越好，需要转换
                            similarity = 1.0 - np.min(result)
                        else:
                            similarity = np.max(result)
                        
                        best_similarity = max(best_similarity, similarity)
                    except:
                        continue
            
            # 如果模板匹配失败，使用基于特征的相似度计算
            if best_similarity < 0.1:
                best_similarity = self._calculate_feature_based_similarity()
            
            return best_similarity
            
        except Exception as e:
            print(f"模板比对时出错: {e}")
            return self._calculate_feature_based_similarity()
    
    def _calculate_feature_based_similarity(self) -> float:
        """
        基于特征计算的相似度（备用方案）
        
        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            # 分析文档结构
            structure = self.analyze_document_structure()
            features = self._extract_six_features(
                structure['regions'],
                structure['horizontal_lines'],
                structure['width'],
                structure['height']
            )
            
            # 计算特征相似度
            detected_count = sum(1 for feature in features.values() if feature['detected'])
            feature_similarity = detected_count / 6.0
            
            # 计算位置相似度
            position_scores = []
            for feature_name, feature_data in features.items():
                if feature_data['detected']:
                    position_scores.append(feature_data.get('confidence', 0.0))
            
            position_similarity = sum(position_scores) / len(position_scores) if position_scores else 0.0
            
            # 综合相似度
            overall_similarity = (feature_similarity * 0.6 + position_similarity * 0.4)
            
            return min(overall_similarity, 0.8)  # 限制最大值为0.8
            
        except Exception as e:
            print(f"特征相似度计算出错: {e}")
            return 0.3  # 默认相似度
    
    def extract_features(self) -> Dict:
        """
        提取所有特征
        
        Returns:
            Dict: 特征提取结果
        """
        if not self.load_image():
            return {'error': '无法加载图片'}
        
        # 分析文档结构
        structure = self.analyze_document_structure()
        
        # 提取6个特征
        features = self._extract_six_features(
            structure['regions'],
            structure['horizontal_lines'],
            structure['width'],
            structure['height']
        )
        
        # 计算检测到的特征数量
        detected_features = sum(1 for feature in features.values() if feature['detected'])
        
        # 模板比对
        template_similarity = self.compare_with_template("mb4.png")
        
        # 返回结果
        result = {
            'detected_features': detected_features,
            'total_features': 6,
            'features': features,
            'template_similarity': template_similarity,
            'image_size': (structure['width'], structure['height'])
        }
        
        return result
    
    def print_features(self):
        """
        打印特征检测结果
        """
        result = self.extract_features()
        
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"\n特征检测结果:")
        print(f"检测到的特征数: {result['detected_features']}/6")
        print(f"模板相似度: {result['template_similarity']:.3f}")
        
        print(f"\n详细特征:")
        for feature_name, feature_data in result['features'].items():
            status = "✅" if feature_data['detected'] else "❌"
            confidence = feature_data['confidence']
            description = feature_data['description']
            print(f"  {status} {feature_name}: {description} (置信度: {confidence:.2f})")

def main():
    """
    主函数 - 测试特征提取
    """
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python main_new.py <image_path>")
        return
    
    image_path = sys.argv[1]
    
    extractor = StandardDocumentFeatureExtractor(image_path)
    extractor.print_features()

if __name__ == "__main__":
    main() 