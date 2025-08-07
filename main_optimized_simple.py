#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Pattern Recognition - Optimized Standard Document Feature Extraction (Simple Version)
基于mb5.png的优化版本，不依赖OCR，使用图像特征分析
"""

import cv2
import numpy as np
from PIL import Image
import re
from typing import Dict, List, Tuple, Optional
import os

class OptimizedStandardDocumentFeatureExtractor:
    """
    优化版标准文档特征抽取器（基于mb5.png，简化版）
    
    功能特点：
    1. 基于mb5.png的3个蓝色框进行区域分析（上部、中部、下部）
    2. 统计各区域留白比例作为判断依据
    3. 使用图像特征分析代替文字识别
    4. 结合mb4.png的文字分布特征
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
        
        # 区域定义（基于mb5.png的蓝色框）
        self.regions = {
            'upper': {'y_start': 0, 'y_end': 0.3, 'name': '上部'},
            'middle': {'y_start': 0.3, 'y_end': 0.7, 'name': '中部'},
            'lower': {'y_start': 0.7, 'y_end': 1.0, 'name': '下部'}
        }
        
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
    
    def detect_blue_boxes(self) -> Dict:
        """
        检测蓝色框区域（基于mb5.png的标注）
        
        Returns:
            Dict: 检测到的蓝色框区域
        """
        try:
            # 转换到HSV色彩空间
            hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            
            # 定义蓝色范围
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # 创建蓝色掩码
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # 查找轮廓
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            blue_boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # 过滤太小的区域
                if area > 1000:  # 最小面积阈值
                    blue_boxes.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'area': area,
                        'center_y': y + h // 2
                    })
            
            # 按y坐标排序，确定上中下区域
            blue_boxes.sort(key=lambda x: x['center_y'])
            
            detected_regions = {}
            if len(blue_boxes) >= 3:
                detected_regions['upper'] = blue_boxes[0]
                detected_regions['middle'] = blue_boxes[1]
                detected_regions['lower'] = blue_boxes[2]
            else:
                # 如果没有检测到足够的蓝色框，使用默认区域
                height = self.image.shape[0]
                detected_regions = {
                    'upper': {'y': 0, 'h': int(height * 0.3)},
                    'middle': {'y': int(height * 0.3), 'h': int(height * 0.4)},
                    'lower': {'y': int(height * 0.7), 'h': int(height * 0.3)}
                }
            
            return detected_regions
            
        except Exception as e:
            print(f"检测蓝色框时出错: {e}")
            # 返回默认区域
            height = self.image.shape[0]
            return {
                'upper': {'y': 0, 'h': int(height * 0.3)},
                'middle': {'y': int(height * 0.3), 'h': int(height * 0.4)},
                'lower': {'y': int(height * 0.7), 'h': int(height * 0.3)}
            }
    
    def calculate_whitespace_ratio(self, region: Dict) -> float:
        """
        计算区域留白比例
        
        Args:
            region: 区域信息
            
        Returns:
            float: 留白比例 (0-1)
        """
        try:
            y_start = region['y']
            y_end = region['y'] + region['h']
            x_start = 0
            x_end = self.image.shape[1]
            
            # 提取区域
            region_image = self.gray_image[y_start:y_end, x_start:x_end]
            
            # 二值化
            _, binary = cv2.threshold(region_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 计算白色像素比例（留白）
            total_pixels = binary.shape[0] * binary.shape[1]
            white_pixels = np.sum(binary == 255)
            whitespace_ratio = white_pixels / total_pixels
            
            return whitespace_ratio
            
        except Exception as e:
            print(f"计算留白比例时出错: {e}")
            return 0.5  # 默认值
    
    def analyze_text_features(self, region: Dict) -> Dict:
        """
        分析区域文本特征（不依赖OCR）
        
        Args:
            region: 区域信息
            
        Returns:
            Dict: 文本特征分析结果
        """
        try:
            y_start = region['y']
            y_end = region['y'] + region['h']
            x_start = 0
            x_end = self.image.shape[1]
            
            # 提取区域
            region_image = self.gray_image[y_start:y_end, x_start:x_end]
            
            # 二值化
            _, binary = cv2.threshold(region_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 分析文本特征
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # 过滤太小的区域
                if w > 10 and h > 5 and area > 50:
                    text_regions.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'area': area,
                        'aspect_ratio': w / h if h > 0 else 0
                    })
            
            # 计算特征
            total_text_area = sum(r['area'] for r in text_regions)
            region_area = region['h'] * (x_end - x_start)
            text_density = total_text_area / region_area if region_area > 0 else 0
            
            # 判断是否有足够的文本内容
            has_text_content = len(text_regions) >= 3 and text_density > 0.01
            
            return {
                'text_regions': text_regions,
                'text_density': text_density,
                'has_text_content': has_text_content,
                'region_count': len(text_regions)
            }
            
        except Exception as e:
            print(f"分析文本特征时出错: {e}")
            return {
                'text_regions': [],
                'text_density': 0.0,
                'has_text_content': False,
                'region_count': 0
            }
    
    def check_region_keywords(self, region_name: str, text_features: Dict) -> bool:
        """
        检查区域是否包含关键词特征
        
        Args:
            region_name: 区域名称
            text_features: 文本特征
            
        Returns:
            bool: 是否包含关键词特征
        """
        # 基于文本密度和区域特征判断
        if region_name == 'upper':
            # 上部应该有中等密度的文本
            return 0.01 <= text_features['text_density'] <= 0.3 and text_features['region_count'] >= 2
        elif region_name == 'lower':
            # 下部应该有中等密度的文本
            return 0.01 <= text_features['text_density'] <= 0.3 and text_features['region_count'] >= 2
        else:
            # 中部应该有较高密度的文本
            return text_features['text_density'] > 0.02 and text_features['region_count'] >= 3
    
    def analyze_regions(self) -> Dict:
        """
        分析三个区域
        
        Returns:
            Dict: 区域分析结果
        """
        # 检测蓝色框
        blue_regions = self.detect_blue_boxes()
        
        analysis_results = {}
        
        for region_name, region_info in blue_regions.items():
            # 计算留白比例
            whitespace_ratio = self.calculate_whitespace_ratio(region_info)
            
            # 分析文本特征
            text_features = self.analyze_text_features(region_info)
            
            # 检查关键词特征
            has_keywords = self.check_region_keywords(region_name, text_features)
            
            analysis_results[region_name] = {
                'whitespace_ratio': whitespace_ratio,
                'text_features': text_features,
                'has_keywords': has_keywords,
                'region_info': region_info
            }
        
        return analysis_results
    
    def compare_with_mb4(self) -> float:
        """
        与mb4.png进行比对
        
        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            if not os.path.exists("mb4.png"):
                print("mb4.png文件不存在")
                return 0.0
            
            # 加载mb4.png
            mb4_image = cv2.imread("mb4.png")
            if mb4_image is None:
                print("无法加载mb4.png")
                return 0.0
            
            # 转换为灰度图
            mb4_gray = cv2.cvtColor(mb4_image, cv2.COLOR_BGR2GRAY)
            image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            
            # 调整大小以进行比较
            height, width = image_gray.shape
            mb4_resized = cv2.resize(mb4_gray, (width, height))
            
            # 计算相似度
            similarity = cv2.matchTemplate(image_gray, mb4_resized, cv2.TM_CCOEFF_NORMED)
            max_similarity = np.max(similarity)
            
            return max_similarity
            
        except Exception as e:
            print(f"与mb4.png比对时出错: {e}")
            return 0.0
    
    def extract_features(self) -> Dict:
        """
        提取所有特征
        
        Returns:
            Dict: 特征提取结果
        """
        if not self.load_image():
            return {'error': '无法加载图片'}
        
        # 分析区域
        region_analysis = self.analyze_regions()
        
        # 与mb4.png比对
        mb4_similarity = self.compare_with_mb4()
        
        # 计算综合评分
        scores = []
        
        # 上部评分
        upper_score = 0.0
        if region_analysis['upper']['has_keywords']:
            upper_score += 0.4
        if 0.3 <= region_analysis['upper']['whitespace_ratio'] <= 0.7:
            upper_score += 0.3
        else:
            upper_score += 0.1
        scores.append(upper_score)
        
        # 中部评分
        middle_score = 0.0
        if 0.2 <= region_analysis['middle']['whitespace_ratio'] <= 0.6:
            middle_score += 0.5
        else:
            middle_score += 0.2
        scores.append(middle_score)
        
        # 下部评分
        lower_score = 0.0
        if region_analysis['lower']['has_keywords']:
            lower_score += 0.4
        if 0.3 <= region_analysis['lower']['whitespace_ratio'] <= 0.7:
            lower_score += 0.3
        else:
            lower_score += 0.1
        scores.append(lower_score)
        
        # 综合评分
        overall_score = sum(scores) / len(scores)
        
        # 判断是否为标准文档
        is_standard_document = (
            region_analysis['upper']['has_keywords'] and
            region_analysis['lower']['has_keywords'] and
            overall_score >= 0.6 and
            mb4_similarity >= 0.3
        )
        
        return {
            'is_standard_document': is_standard_document,
            'overall_score': overall_score,
            'mb4_similarity': mb4_similarity,
            'region_analysis': region_analysis,
            'scores': {
                'upper': scores[0],
                'middle': scores[1],
                'lower': scores[2]
            }
        }
    
    def print_analysis(self):
        """
        打印分析结果
        """
        result = self.extract_features()
        
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"\n{'='*50}")
        print("优化版标准文档分析结果（简化版）")
        print(f"{'='*50}")
        
        print(f"\n📋 总体判断:")
        status = "✅ 是标准文档" if result['is_standard_document'] else "❌ 不是标准文档"
        print(f"  {status}")
        print(f"  综合评分: {result['overall_score']:.3f}")
        print(f"  mb4相似度: {result['mb4_similarity']:.3f}")
        
        print(f"\n📊 区域分析:")
        for region_name, analysis in result['region_analysis'].items():
            region_name_cn = {'upper': '上部', 'middle': '中部', 'lower': '下部'}[region_name]
            print(f"\n  {region_name_cn}:")
            print(f"    留白比例: {analysis['whitespace_ratio']:.3f}")
            print(f"    关键词检测: {'✅' if analysis['has_keywords'] else '❌'}")
            print(f"    文本密度: {analysis['text_features']['text_density']:.3f}")
            print(f"    文本区域数: {analysis['text_features']['region_count']}")
            print(f"    区域评分: {result['scores'][region_name]:.3f}")
        
        print(f"\n{'='*50}")

def main():
    """
    主函数 - 测试优化版特征提取
    """
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python main_optimized_simple.py <image_path>")
        return
    
    image_path = sys.argv[1]
    
    extractor = OptimizedStandardDocumentFeatureExtractor(image_path)
    extractor.print_analysis()

if __name__ == "__main__":
    main()
