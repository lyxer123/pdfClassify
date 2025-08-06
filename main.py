#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Pattern Recognition - Standard Document Feature Extraction
针对标准文档的9个特征抽取系统
"""

import cv2
import numpy as np
from PIL import Image
import re
from typing import Dict, List, Tuple, Optional
import os

class StandardDocumentFeatureExtractor:
    """
    标准文档7个特征抽取器
    
    7个特征（从上往下）：
    1. 标准logo
    2. 标准类别（国家标准、行业标准、企业标准或团体标准）
    3. 标准号
    4. 第一横线
    5. 标准的中文和英文名称
    6. 发布和实施时间
    7. 发布单位
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
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                               minLineLength=100, maxLineGap=10)
        
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
            area = cv2.contourArea(contour)
            
            # 过滤太小的区域
            if w > 20 and h > 10 and area > 100:
                # 计算文本密度
                roi = binary[y:y+h, x:x+w]
                density = np.sum(roi > 0) / (w * h)
                
                if density > 0.1:  # 文本密度阈值
                    text_regions.append((x, y, w, h, density))
        
        return text_regions
    
    def analyze_document_structure(self) -> Dict:
        """
        分析文档结构，识别9个特征
        
        Returns:
            Dict: 文档结构分析结果
        """
        if not self.load_image():
            return {}
        
        print("开始分析标准文档结构...")
        
        # 检测横线
        horizontal_lines = self.detect_horizontal_lines()
        print(f"检测到 {len(horizontal_lines)} 条横线")
        
        # 检测文本区域
        text_regions = self.detect_text_regions()
        print(f"检测到 {len(text_regions)} 个文本区域")
        
        # 获取图片尺寸
        height, width = self.gray_image.shape
        
        # 按垂直位置划分区域
        regions = {
            'top': [],      # 顶部区域（特征1-4）
            'middle': [],   # 中部区域（特征5-6）
            'bottom': []    # 底部区域（特征7-9）
        }
        
        # 划分区域
        top_height = height // 3
        bottom_start = 2 * height // 3
        
        for x, y, w, h, density in text_regions:
            if y < top_height:
                regions['top'].append((x, y, w, h, density))
            elif y < bottom_start:
                regions['middle'].append((x, y, w, h, density))
            else:
                regions['bottom'].append((x, y, w, h, density))
        
        # 分析特征
        features = self._extract_seven_features(regions, horizontal_lines, width, height)
        
        return features
    
    def _extract_seven_features(self, regions: Dict, horizontal_lines: List, width: int, height: int) -> Dict:
        """
        提取7个特征（基于位置和布局关系）
        
        Args:
            regions: 区域划分
            horizontal_lines: 横线列表
            width: 图片宽度
            height: 图片高度
            
        Returns:
            Dict: 7个特征
        """
        features = {
            'feature_1_standard_logo': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_2_standard_category': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_3_standard_code': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_4_first_horizontal_line': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_5_standard_names': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_6_publication_time': {'detected': False, 'position': None, 'confidence': 0.0},
            'feature_7_publishing_unit': {'detected': False, 'position': None, 'confidence': 0.0}
        }
        
        # 获取所有文本区域，按y坐标排序
        all_regions = []
        for region_type, region_list in regions.items():
            all_regions.extend(region_list)
        
        # 按y坐标排序，从上往下
        sorted_regions = sorted(all_regions, key=lambda x: x[1])
        
        # 定义页面区域（按高度比例）
        top_region = height * 0.2  # 上部20%
        middle_region = height * 0.6  # 中部60%
        bottom_region = height * 0.2  # 下部20%
        
        # 定义左右区域（按宽度比例）
        left_region = width * 0.3  # 左侧30%
        right_region = width * 0.7  # 右侧70%
        
        # 特征1: 标准logo（页面上部靠右）
        for region in sorted_regions:
            x, y, w, h = region[:4]
            region_center_x = x + w // 2
            region_center_y = y + h // 2
            
            # 检查是否在上部靠右
            if (y < top_region and region_center_x > width * 0.6):
                features['feature_1_standard_logo']['detected'] = True
                features['feature_1_standard_logo']['position'] = (x, y, w, h)
                features['feature_1_standard_logo']['confidence'] = 0.9
                break
        
        # 特征2: 标准类别（上部，左右贯穿）
        for region in sorted_regions:
            x, y, w, h = region[:4]
            region_center_y = y + h // 2
            
            # 检查是否在上部且宽度较大（左右贯穿）
            if (y < top_region and w > width * 0.7):
                features['feature_2_standard_category']['detected'] = True
                features['feature_2_standard_category']['position'] = (x, y, w, h)
                features['feature_2_standard_category']['confidence'] = 0.9
                break
        
        # 特征3: 标准号（上部靠右）
        for region in sorted_regions:
            x, y, w, h = region[:4]
            region_center_x = x + w // 2
            region_center_y = y + h // 2
            
            # 检查是否在上部靠右
            if (y < top_region and region_center_x > width * 0.6):
                # 避免与logo重复
                if not features['feature_1_standard_logo']['detected'] or \
                   abs(region_center_y - features['feature_1_standard_logo']['position'][1]) > 20:
                    features['feature_3_standard_code']['detected'] = True
                    features['feature_3_standard_code']['position'] = (x, y, w, h)
                    features['feature_3_standard_code']['confidence'] = 0.9
                    break
        
        # 特征4: 第一横线（左右贯穿的横线）
        if horizontal_lines:
            # 按y坐标排序，取最上面的横线
            sorted_lines = sorted(horizontal_lines, key=lambda x: x[1])
            for line in sorted_lines:
                x1, y1, x2, y2 = line
                line_length = abs(x2 - x1)
                
                # 检查是否是左右贯穿的横线
                if line_length > width * 0.8:
                    features['feature_4_first_horizontal_line']['detected'] = True
                    features['feature_4_first_horizontal_line']['position'] = line
                    features['feature_4_first_horizontal_line']['confidence'] = 0.9
                    break
        
        # 特征5: 标准的中文和英文名称（页面正中间，2行以上）
        middle_regions = regions['middle']
        if middle_regions:
            # 按y坐标排序
            sorted_middle = sorted(middle_regions, key=lambda x: x[1])
            
            # 检查是否有多个文本区域在中间位置
            middle_text_count = 0
            for region in sorted_middle:
                x, y, w, h = region[:4]
                region_center_y = y + h // 2
                
                # 检查是否在页面中间区域
                if (region_center_y > height * 0.3 and region_center_y < height * 0.7):
                    middle_text_count += 1
            
            if middle_text_count >= 2:
                # 取中间区域的第一个作为主要特征
                for region in sorted_middle:
                    x, y, w, h = region[:4]
                    region_center_y = y + h // 2
                    if (region_center_y > height * 0.3 and region_center_y < height * 0.7):
                        features['feature_5_standard_names']['detected'] = True
                        features['feature_5_standard_names']['position'] = (x, y, w, h)
                        features['feature_5_standard_names']['confidence'] = 0.9
                        break
        
        # 特征6: 发布和实施时间（页面下部，有横线贯穿，横线上方左右有字）
        bottom_regions = regions['bottom']
        if bottom_regions and horizontal_lines:
            # 找到下部的横线
            bottom_lines = [line for line in horizontal_lines if line[1] > height * 0.7]
            
            if bottom_lines:
                # 按y坐标排序，取最下面的横线
                sorted_bottom_lines = sorted(bottom_lines, key=lambda x: x[1])
                bottom_line = sorted_bottom_lines[-1]
                x1, y1, x2, y2 = bottom_line
                
                # 检查横线是否贯穿左右
                if abs(x2 - x1) > width * 0.8:
                    # 检查横线上方是否有文本区域
                    text_above_line = False
                    text_left_right = False
                    
                    for region in bottom_regions:
                        rx, ry, rw, rh = region[:4]
                        region_center_x = rx + rw // 2
                        
                        # 检查是否在横线上方
                        if ry < y1:
                            text_above_line = True
                            # 检查是否在左右两侧
                            if rx < width * 0.3 or (rx + rw) > width * 0.7:
                                text_left_right = True
                    
                    if text_above_line and text_left_right:
                        features['feature_6_publication_time']['detected'] = True
                        features['feature_6_publication_time']['position'] = bottom_line
                        features['feature_6_publication_time']['confidence'] = 0.9
        
        # 特征7: 发布单位（页面下部，至少一行字）
        if bottom_regions:
            # 按y坐标排序，取最下面的文本区域
            sorted_bottom = sorted(bottom_regions, key=lambda x: x[1])
            for region in sorted_bottom:
                x, y, w, h = region[:4]
                region_center_y = y + h // 2
                
                # 检查是否在页面下部
                if region_center_y > height * 0.8:
                    features['feature_7_publishing_unit']['detected'] = True
                    features['feature_7_publishing_unit']['position'] = (x, y, w, h)
                    features['feature_7_publishing_unit']['confidence'] = 0.9
                    break
        
        return features
    
    def compare_with_template(self, template_path: str = "mb3.png") -> float:
        """
        与模板图片进行蒙版比对
        
        Args:
            template_path: 模板图片路径
            
        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            # 加载模板图片
            template = cv2.imread(template_path)
            if template is None:
                print(f"无法加载模板图片: {template_path}")
                return 0.0
            
            # 调整模板图片大小以匹配当前图片
            template_resized = cv2.resize(template, (self.image.shape[1], self.image.shape[0]))
            
            # 转换为灰度图
            template_gray = cv2.cvtColor(template_resized, cv2.COLOR_BGR2GRAY)
            current_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            
            # 使用模板匹配
            result = cv2.matchTemplate(current_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 返回相似度分数
            similarity = max_val
            print(f"模板比对相似度: {similarity:.3f}")
            
            return similarity
            
        except Exception as e:
            print(f"模板比对出错: {e}")
            return 0.0
    
    def extract_features(self) -> Dict:
        """
        抽取7个特征
        
        Returns:
            Dict: 7个特征
        """
        features = self.analyze_document_structure()
        
        # 计算检测到的特征数量
        detected_count = sum(1 for feature in features.values() if feature['detected'])
        
        # 进行模板比对
        template_similarity = self.compare_with_template()
        
        result = {
            'total_features': 7,
            'detected_features': detected_count,
            'detection_rate': detected_count / 7.0,
            'features': features,
            'template_similarity': template_similarity
        }
        
        self.features = result
        return result
    
    def print_features(self):
        """
        打印抽取的特征
        """
        if not self.features:
            print("没有可用的特征数据")
            return
        
        print("\n" + "="*80)
        print("标准文档7个特征抽取结果")
        print("="*80)
        
        print(f"检测到的特征数量: {self.features['detected_features']}/7")
        print(f"检测率: {self.features['detection_rate']:.2%}")
        
        features = self.features['features']
        
        feature_names = [
            ("feature_1_standard_logo", "1. 标准logo"),
            ("feature_2_standard_category", "2. 标准类别"),
            ("feature_3_standard_code", "3. 标准号"),
            ("feature_4_first_horizontal_line", "4. 第一横线"),
            ("feature_5_standard_names", "5. 标准的中文和英文名称"),
            ("feature_6_publication_time", "6. 发布和实施时间"),
            ("feature_7_publishing_unit", "7. 发布单位")
        ]
        
        for feature_key, feature_name in feature_names:
            feature = features[feature_key]
            status = "✓" if feature['detected'] else "✗"
            position = feature['position'] if feature['position'] else "未检测到"
            print(f"{feature_name}: {status} {position}")
        
        print("\n" + "="*80)

def main():
    """
    主函数
    """
    print("PDF Pattern Recognition - 7-Feature Standard Document Extraction")
    print("=" * 80)
    
    # 检查图片文件是否存在
    image_path = "jc.png"
    if not os.path.exists(image_path):
        print(f"错误: 找不到图片文件 {image_path}")
        return
    
    # 创建抽取器并执行特征抽取
    extractor = StandardDocumentFeatureExtractor(image_path)
    features = extractor.extract_features()
    
    if features:
        extractor.print_features()
    else:
        print("特征抽取失败")

if __name__ == "__main__":
    main() 