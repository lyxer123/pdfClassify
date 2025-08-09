# -*- coding: utf-8 -*-
"""
PDF处理器和特征提取器
基于mb6.png模板的企业标准特征识别
"""

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import os
import logging
from typing import Dict
import time

class PDFProcessor:
    """PDF处理器类"""
    
    def __init__(self, template_path: str = "mb6.png"):
        self.template_path = template_path
        self.logger = self._setup_logger()
        
        # 颜色范围定义
        self.color_ranges = {
            'blue': {
                'lower': np.array([100, 50, 50]),
                'upper': np.array([130, 255, 255])
            },
            'red': {
                'lower1': np.array([0, 50, 50]),
                'upper1': np.array([10, 255, 255]),
                'lower2': np.array([170, 50, 50]),
                'upper2': np.array([180, 255, 255])
            },
            'white': {
                'lower': np.array([0, 0, 230]),
                'upper': np.array([180, 30, 255])
            },
            'black': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 255, 30])
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('PDFProcessor')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _get_color_ratio(self, hsv: np.ndarray, color: str) -> float:
        """获取指定颜色占比"""
        if color == 'red':
            mask1 = cv2.inRange(hsv, self.color_ranges['red']['lower1'], self.color_ranges['red']['upper1'])
            mask2 = cv2.inRange(hsv, self.color_ranges['red']['lower2'], self.color_ranges['red']['upper2'])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, self.color_ranges[color]['lower'], self.color_ranges[color]['upper'])
        
        total_pixels = hsv.shape[0] * hsv.shape[1]
        color_pixels = cv2.countNonZero(mask)
        return color_pixels / total_pixels
    
    def _locate_regions(self, image: np.ndarray, hsv: np.ndarray) -> Dict:
        """定位三区域（上中下）"""
        regions = {}
        blue_mask = cv2.inRange(hsv, self.color_ranges['blue']['lower'], self.color_ranges['blue']['upper'])
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        blue_boxes = []
        for contour in blue_contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                blue_boxes.append((y, x, w, h))
        
        blue_boxes.sort(key=lambda x: x[0])
        
        if len(blue_boxes) >= 3:
            regions['upper'] = {'y': blue_boxes[0][0], 'height': blue_boxes[0][3]}
            regions['middle'] = {'y': blue_boxes[1][0], 'height': blue_boxes[1][3]}
            regions['lower'] = {'y': blue_boxes[2][0], 'height': blue_boxes[2][3]}
        
        return regions
    
    def _locate_key_boxes(self, image: np.ndarray, hsv: np.ndarray) -> Dict:
        """定位6个关键框（1-6号）"""
        key_boxes = {}
        red_mask1 = cv2.inRange(hsv, self.color_ranges['red']['lower1'], self.color_ranges['red']['upper1'])
        red_mask2 = cv2.inRange(hsv, self.color_ranges['red']['lower2'], self.color_ranges['red']['upper2'])
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        red_boxes = []
        for contour in red_contours:
            if cv2.contourArea(contour) > 50:
                x, y, w, h = cv2.boundingRect(contour)
                red_boxes.append((x, y, w, h))
        
        if len(red_boxes) >= 6:
            red_boxes.sort(key=lambda x: (x[1], x[0]))
            for i, (x, y, w, h) in enumerate(red_boxes[:6]):
                key_boxes[f'box_{i+1}'] = {'x': x, 'y': y, 'width': w, 'height': h}
        
        return key_boxes
    
    def _verify_keywords(self, image: np.ndarray, regions: Dict) -> Dict:
        """验证关键文字"""
        keywords = {}
        
        # 多种OCR配置尝试
        configs = [
            '--psm 6 -l chi_sim',
            '--psm 7 -l chi_sim',
            '--psm 8 -l chi_sim',
            '--psm 13 -l chi_sim'
        ]
        
        if 'upper' in regions:
            upper_region = image[regions['upper']['y']:regions['upper']['y']+regions['upper']['height'], :]
            # 图像预处理增强OCR识别
            upper_gray = cv2.cvtColor(upper_region, cv2.COLOR_BGR2GRAY)
            upper_enhanced = cv2.adaptiveThreshold(upper_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            standard_found = False
            for config in configs:
                try:
                    upper_text = pytesseract.image_to_string(upper_enhanced, config=config)
                    if '标准' in upper_text or 'standard' in upper_text.lower():
                        standard_found = True
                        break
                except:
                    continue
            keywords['upper_has_standard'] = standard_found
        
        if 'lower' in regions:
            lower_region = image[regions['lower']['y']:regions['lower']['y']+regions['lower']['height'], :]
            # 图像预处理增强OCR识别
            lower_gray = cv2.cvtColor(lower_region, cv2.COLOR_BGR2GRAY)
            lower_enhanced = cv2.adaptiveThreshold(lower_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            publish_found = False
            for config in configs:
                try:
                    lower_text = pytesseract.image_to_string(lower_enhanced, config=config)
                    if '发布' in lower_text or 'publish' in lower_text.lower():
                        publish_found = True
                        break
                except:
                    continue
            keywords['lower_has_publish'] = publish_found
        
        return keywords
    
    def _detect_lines(self, image: np.ndarray, regions: Dict) -> Dict:
        """检测横线"""
        lines = {}
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        detected_lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if detected_lines is not None:
            horizontal_lines = []
            height, width = image.shape[:2]
            
            for line in detected_lines:
                rho, theta = line[0]
                if abs(theta) < 0.1 or abs(theta - np.pi) < 0.1:
                    horizontal_lines.append((rho, theta))
            
            horizontal_lines.sort(key=lambda x: x[0])
            
            if len(horizontal_lines) >= 2:
                lines['first_line'] = horizontal_lines[0]
                lines['second_line'] = horizontal_lines[1]
                
                if 'upper' in regions and 'lower' in regions:
                    first_line_y = horizontal_lines[0][0]
                    second_line_y = horizontal_lines[1][0]
                    
                    lines['first_line_valid'] = abs(first_line_y - (regions['upper']['y'] + regions['upper']['height'])) < height * 0.05
                    lines['second_line_valid'] = abs(second_line_y - regions['lower']['y']) < height * 0.05
        
        return lines
    
    def _calculate_proportions(self, image: np.ndarray, regions: Dict) -> Dict:
        """计算区域比例"""
        proportions = {}
        height, width = image.shape[:2]
        
        if 'upper' in regions:
            upper_height = regions['upper']['height']
            proportions['upper_whitespace'] = (upper_height / height) * 100
        
        if 'middle' in regions:
            middle_height = regions['middle']['height']
            proportions['middle_whitespace'] = (middle_height / height) * 100
        
        if 'lower' in regions:
            lower_height = regions['lower']['height']
            proportions['lower_whitespace'] = (lower_height / height) * 100
        
        return proportions
    
    def _calculate_positions(self, image: np.ndarray, key_boxes: Dict) -> Dict:
        """计算位置关系"""
        positions = {}
        height, width = image.shape[:2]
        
        if 'box_1' in key_boxes:
            box1_x = key_boxes['box_1']['x'] + key_boxes['box_1']['width']
            positions['box1_right_aligned'] = (box1_x / width) > 0.85
        
        if 'box_3' in key_boxes:
            box3_x = key_boxes['box_3']['x'] + key_boxes['box_3']['width']
            positions['box3_right_aligned'] = (box3_x / width) > 0.80
        
        if 'box_6' in key_boxes:
            box6_center = key_boxes['box_6']['x'] + key_boxes['box_6']['width'] / 2
            center_error = abs(box6_center - width / 2) / width
            positions['box6_centered'] = center_error < 0.05
        
        return positions
    
    def _check_content_constraints(self, image: np.ndarray, key_boxes: Dict) -> Dict:
        """检查内容约束"""
        constraints = {}
        
        if 'box_4' in key_boxes:
            box4_region = image[
                key_boxes['box_4']['y']:key_boxes['box_4']['y']+key_boxes['box_4']['height'],
                key_boxes['box_4']['x']:key_boxes['box_4']['x']+key_boxes['box_4']['width']
            ]
            
            gray = cv2.cvtColor(box4_region, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            horizontal_projection = np.sum(binary, axis=1)
            lines = np.where(horizontal_projection > np.max(horizontal_projection) * 0.1)[0]
            
            if len(lines) > 0:
                line_count = 1
                for i in range(1, len(lines)):
                    if lines[i] - lines[i-1] > 5:
                        line_count += 1
                
                constraints['box4_multiple_lines'] = line_count >= 2
        
        return constraints
    
    def _extract_features(self, image: np.ndarray) -> Dict:
        """提取图像特征"""
        features = {}
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = image.shape[:2]
        
        features['white_ratio'] = self._get_color_ratio(hsv, 'white')
        features['black_ratio'] = self._get_color_ratio(hsv, 'black')
        features['regions'] = self._locate_regions(image, hsv)
        features['key_boxes'] = self._locate_key_boxes(image, hsv)
        features['keywords'] = self._verify_keywords(image, features['regions'])
        features['lines'] = self._detect_lines(image, features['regions'])
        features['proportions'] = self._calculate_proportions(image, features['regions'])
        features['positions'] = self._calculate_positions(image, features['key_boxes'])
        features['content_constraints'] = self._check_content_constraints(image, features['key_boxes'])
        
        return features
    
    def _validate_features(self, features: Dict) -> bool:
        """验证特征是否符合模板要求"""
        validation_score = 0
        max_score = 0
        
        # 1. 颜色特征验证 (权重: 20%)
        max_score += 20
        white_ratio = features.get('white_ratio', 0)
        black_ratio = features.get('black_ratio', 0)
        if white_ratio > 0.85:  # 降低白色背景要求到85%
            validation_score += 10
        if black_ratio > 0.005:  # 降低黑色文字要求到0.5%
            validation_score += 10
        
        # 2. 区域检测验证 (权重: 15%)
        max_score += 15
        regions = features.get('regions', {})
        if len(regions) >= 3:
            validation_score += 15
        elif len(regions) >= 2:
            validation_score += 10
        
        # 3. 关键框检测验证 (权重: 15%)
        max_score += 15
        key_boxes = features.get('key_boxes', {})
        box_count = len(key_boxes)
        if box_count >= 6:
            validation_score += 15
        elif box_count >= 4:
            validation_score += 10
        elif box_count >= 2:
            validation_score += 5
        
        # 4. 关键词验证 (权重: 20%)
        max_score += 20
        keywords = features.get('keywords', {})
        if keywords.get('upper_has_standard', False):
            validation_score += 10
        if keywords.get('lower_has_publish', False):
            validation_score += 10
        
        # 5. 位置关系验证 (权重: 15%)
        max_score += 15
        positions = features.get('positions', {})
        position_score = 0
        if positions.get('box1_right_aligned', False):
            position_score += 5
        if positions.get('box3_right_aligned', False):
            position_score += 5
        if positions.get('box6_centered', False):
            position_score += 5
        validation_score += position_score
        
        # 6. 内容约束验证 (权重: 15%)
        max_score += 15
        content_constraints = features.get('content_constraints', {})
        if content_constraints.get('box4_multiple_lines', False):
            validation_score += 15
        
        # 计算匹配度
        match_percentage = (validation_score / max_score) * 100 if max_score > 0 else 0
        
        # 降低验证阈值到70%
        return match_percentage >= 70
    
    def process_pdf(self, pdf_path: str, timeout: int = 15) -> Dict:
        """处理单个PDF文件"""
        start_time = time.time()
        result = {
            'pdf_path': pdf_path,
            'success': False,
            'reason': '',
            'features': None,
            'processing_time': 0
        }
        
        try:
            if time.time() - start_time > timeout:
                result['reason'] = '处理超时'
                return result
            
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=5)
            
            for page_num, image in enumerate(images):
                if time.time() - start_time > timeout:
                    result['reason'] = '处理超时'
                    return result
                
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                features = self._extract_features(opencv_image)
                
                if self._validate_features(features):
                    result['success'] = True
                    result['features'] = features
                    result['reason'] = f'第{page_num + 1}页匹配成功'
                    break
            
            if not result['success']:
                result['reason'] = '所有页面都不匹配模板特征'
            
        except Exception as e:
            result['reason'] = f'处理异常: {str(e)}'
            self.logger.error(f"处理PDF {pdf_path} 时发生异常: {str(e)}")
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def batch_process(self, input_dir: str, output_dir: str = "jc") -> Dict:
        """批量处理PDF文件"""
        results = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'successful_paths': [],
            'failed_reasons': {}
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(input_dir, filename)
                results['total_files'] += 1
                
                self.logger.info(f"处理文件: {filename}")
                
                result = self.process_pdf(pdf_path)
                
                if result['success']:
                    output_path = os.path.join(output_dir, filename)
                    try:
                        import shutil
                        shutil.copy2(pdf_path, output_path)
                        results['successful_files'] += 1
                        results['successful_paths'].append(pdf_path)
                        self.logger.info(f"文件 {filename} 匹配成功，已复制到 {output_dir}")
                    except Exception as e:
                        self.logger.error(f"复制文件 {filename} 失败: {str(e)}")
                        results['failed_files'] += 1
                        results['failed_reasons'][filename] = f"复制失败: {str(e)}"
                else:
                    results['failed_files'] += 1
                    results['failed_reasons'][filename] = result['reason']
                    self.logger.info(f"文件 {filename} 不匹配: {result['reason']}")
        
        return results
