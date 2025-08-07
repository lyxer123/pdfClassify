#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Pattern Recognition - Simple Version (No OCR)
基于mb5.png的简化版本，不依赖OCR
"""

import cv2
import numpy as np
import os

class SimpleStandardDocumentFeatureExtractor:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = None
        self.gray_image = None
        
    def load_image(self) -> bool:
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
    
    def detect_blue_boxes(self) -> dict:
        try:
            hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            blue_boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                if area > 1000:
                    blue_boxes.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'area': area, 'center_y': y + h // 2
                    })
            
            blue_boxes.sort(key=lambda x: x['center_y'])
            
            if len(blue_boxes) >= 3:
                return {
                    'upper': blue_boxes[0],
                    'middle': blue_boxes[1], 
                    'lower': blue_boxes[2]
                }
            else:
                height = self.image.shape[0]
                return {
                    'upper': {'y': 0, 'h': int(height * 0.3)},
                    'middle': {'y': int(height * 0.3), 'h': int(height * 0.4)},
                    'lower': {'y': int(height * 0.7), 'h': int(height * 0.3)}
                }
        except Exception as e:
            print(f"检测蓝色框时出错: {e}")
            height = self.image.shape[0]
            return {
                'upper': {'y': 0, 'h': int(height * 0.3)},
                'middle': {'y': int(height * 0.3), 'h': int(height * 0.4)},
                'lower': {'y': int(height * 0.7), 'h': int(height * 0.3)}
            }
    
    def calculate_whitespace_ratio(self, region: dict) -> float:
        try:
            y_start = region['y']
            y_end = region['y'] + region['h']
            region_image = self.gray_image[y_start:y_end, :]
            _, binary = cv2.threshold(region_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            total_pixels = binary.shape[0] * binary.shape[1]
            white_pixels = np.sum(binary == 255)
            return white_pixels / total_pixels
        except Exception as e:
            print(f"计算留白比例时出错: {e}")
            return 0.5
    
    def analyze_text_features(self, region: dict) -> dict:
        try:
            y_start = region['y']
            y_end = region['y'] + region['h']
            region_image = self.gray_image[y_start:y_end, :]
            _, binary = cv2.threshold(region_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 5 and w * h > 50:
                    text_regions.append({'x': x, 'y': y, 'w': w, 'h': h, 'area': w * h})
            
            total_text_area = sum(r['area'] for r in text_regions)
            region_area = region['h'] * self.image.shape[1]
            text_density = total_text_area / region_area if region_area > 0 else 0
            
            return {
                'text_density': text_density,
                'region_count': len(text_regions),
                'has_text_content': len(text_regions) >= 3 and text_density > 0.01
            }
        except Exception as e:
            print(f"分析文本特征时出错: {e}")
            return {'text_density': 0.0, 'region_count': 0, 'has_text_content': False}
    
    def check_region_keywords(self, region_name: str, text_features: dict) -> bool:
        if region_name == 'upper':
            return 0.01 <= text_features['text_density'] <= 0.3 and text_features['region_count'] >= 2
        elif region_name == 'lower':
            return 0.01 <= text_features['text_density'] <= 0.3 and text_features['region_count'] >= 2
        else:
            return text_features['text_density'] > 0.02 and text_features['region_count'] >= 3
    
    def compare_with_mb4(self) -> float:
        try:
            if not os.path.exists("mb4.png"):
                return 0.0
            
            mb4_image = cv2.imread("mb4.png")
            if mb4_image is None:
                return 0.0
            
            mb4_gray = cv2.cvtColor(mb4_image, cv2.COLOR_BGR2GRAY)
            image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            height, width = image_gray.shape
            mb4_resized = cv2.resize(mb4_gray, (width, height))
            
            similarity = cv2.matchTemplate(image_gray, mb4_resized, cv2.TM_CCOEFF_NORMED)
            return np.max(similarity)
        except Exception as e:
            print(f"与mb4.png比对时出错: {e}")
            return 0.0
    
    def extract_features(self) -> dict:
        if not self.load_image():
            return {'error': '无法加载图片'}
        
        blue_regions = self.detect_blue_boxes()
        analysis_results = {}
        
        for region_name, region_info in blue_regions.items():
            whitespace_ratio = self.calculate_whitespace_ratio(region_info)
            text_features = self.analyze_text_features(region_info)
            has_keywords = self.check_region_keywords(region_name, text_features)
            
            analysis_results[region_name] = {
                'whitespace_ratio': whitespace_ratio,
                'text_features': text_features,
                'has_keywords': has_keywords
            }
        
        mb4_similarity = self.compare_with_mb4()
        
        # 计算评分
        scores = []
        
        # 上部评分
        upper_score = 0.0
        if analysis_results['upper']['has_keywords']:
            upper_score += 0.4
        if 0.3 <= analysis_results['upper']['whitespace_ratio'] <= 0.7:
            upper_score += 0.3
        else:
            upper_score += 0.1
        scores.append(upper_score)
        
        # 中部评分
        middle_score = 0.0
        if 0.2 <= analysis_results['middle']['whitespace_ratio'] <= 0.6:
            middle_score += 0.5
        else:
            middle_score += 0.2
        scores.append(middle_score)
        
        # 下部评分
        lower_score = 0.0
        if analysis_results['lower']['has_keywords']:
            lower_score += 0.4
        if 0.3 <= analysis_results['lower']['whitespace_ratio'] <= 0.7:
            lower_score += 0.3
        else:
            lower_score += 0.1
        scores.append(lower_score)
        
        overall_score = sum(scores) / len(scores)
        
        is_standard_document = (
            analysis_results['upper']['has_keywords'] and
            analysis_results['lower']['has_keywords'] and
            overall_score >= 0.6 and
            mb4_similarity >= 0.3
        )
        
        return {
            'is_standard_document': is_standard_document,
            'overall_score': overall_score,
            'mb4_similarity': mb4_similarity,
            'region_analysis': analysis_results,
            'scores': {'upper': scores[0], 'middle': scores[1], 'lower': scores[2]}
        }
    
    def print_analysis(self):
        result = self.extract_features()
        
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"\n{'='*50}")
        print("简化版标准文档分析结果")
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
    import sys
    if len(sys.argv) != 2:
        print("用法: python main_simple.py <image_path>")
        return
    
    image_path = sys.argv[1]
    extractor = SimpleStandardDocumentFeatureExtractor(image_path)
    extractor.print_analysis()

if __name__ == "__main__":
    main()
