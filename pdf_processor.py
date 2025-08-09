# -*- coding: utf-8 -*-
"""
PDF处理器和特征提取器
基于mb6.png模板的企业标准特征识别
"""

import cv2
import numpy as np
import pytesseract
import os
import logging
from typing import Dict
import time

# 尝试导入多种PDF处理库
PDF_BACKEND = None
try:
    from pdf2image import convert_from_path
    PDF_BACKEND = 'pdf2image'
except ImportError:
    pass

try:
    import fitz  # PyMuPDF
    if PDF_BACKEND is None:
        PDF_BACKEND = 'pymupdf'
except ImportError:
    pass

try:
    from PIL import Image
    import io
except ImportError:
    pass

class PDFProcessor:
    """PDF处理器类 - 基于mb81/82/83特征的标准文档识别"""
    
    def __init__(self, template_path: str = "templates/mb81.png"):
        self.template_path = template_path
        self.logger = self._setup_logger()
        
        # 颜色范围定义（HSV色彩空间）
        self.color_ranges = {
            'white': {
                'lower': np.array([0, 0, 200]),    # 更严格的白色定义
                'upper': np.array([180, 25, 255])
            },
            'black': {
                'lower': np.array([0, 0, 0]),      # 黑色文字
                'upper': np.array([180, 255, 50])
            },
            'red': {
                'lower1': np.array([0, 50, 50]),   # 红色标注（排除）
                'upper1': np.array([10, 255, 255]),
                'lower2': np.array([170, 50, 50]),
                'upper2': np.array([180, 255, 255])
            }
        }
        
        # 判断阈值配置
        self.thresholds = {
            'white_bg_min': 0.70,          # 白色背景最低占比
            'black_text_min': 0.005,       # 黑色文字最低占比
            'line_distance_min': 0.65,     # 两横线间距最小占比
            'line_width_min': 0.70,        # 横线宽度最小占比
            'upper_height_max': 0.30,      # 上部最大高度占比
            'middle_height_min': 0.50,     # 中部最小高度占比
            'lower_height_max': 0.30,      # 下部最大高度占比
            'logo_x_min': 0.40             # logo X位置最小占比
        }
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('PDFProcessor')
        logger.setLevel(logging.DEBUG)  # 启用debug级别
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _get_color_ratio(self, hsv: np.ndarray, color: str) -> float:
        """获取指定颜色占比（排除红色标注）"""
        if color == 'red':
            mask1 = cv2.inRange(hsv, self.color_ranges['red']['lower1'], self.color_ranges['red']['upper1'])
            mask2 = cv2.inRange(hsv, self.color_ranges['red']['lower2'], self.color_ranges['red']['upper2'])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, self.color_ranges[color]['lower'], self.color_ranges[color]['upper'])
        
        total_pixels = hsv.shape[0] * hsv.shape[1]
        color_pixels = cv2.countNonZero(mask)
        return color_pixels / total_pixels
    
    def _get_red_annotation_mask(self, hsv: np.ndarray) -> np.ndarray:
        """获取红色标注区域的掩码（包括红框和红色数字）"""
        # 红色在HSV空间有两个范围（0-10度和170-180度）
        mask1 = cv2.inRange(hsv, self.color_ranges['red']['lower1'], self.color_ranges['red']['upper1'])
        mask2 = cv2.inRange(hsv, self.color_ranges['red']['lower2'], self.color_ranges['red']['upper2'])
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # 使用形态学操作连接红色区域，更好地识别红框和数字
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        
        return red_mask
    
    def _calculate_white_black_ratio_excluding_red(self, hsv: np.ndarray, non_red_mask: np.ndarray) -> tuple:
        """在排除红色区域后计算白底黑字占比"""
        # 获取白色和黑色的掩码
        white_mask = cv2.inRange(hsv, self.color_ranges['white']['lower'], self.color_ranges['white']['upper'])
        black_mask = cv2.inRange(hsv, self.color_ranges['black']['lower'], self.color_ranges['black']['upper'])
        
        # 应用非红色掩码，排除红色区域
        white_mask_filtered = cv2.bitwise_and(white_mask, non_red_mask)
        black_mask_filtered = cv2.bitwise_and(black_mask, non_red_mask)
        
        # 计算非红色区域的总像素数
        non_red_pixels = cv2.countNonZero(non_red_mask)
        
        if non_red_pixels == 0:
            return 0.0, 0.0
        
        # 计算排除红色后的白底黑字占比
        white_pixels = cv2.countNonZero(white_mask_filtered)
        black_pixels = cv2.countNonZero(black_mask_filtered)
        
        white_ratio = white_pixels / non_red_pixels
        black_ratio = black_pixels / non_red_pixels
        
        return white_ratio, black_ratio
    
    def _check_page_colors(self, image: np.ndarray) -> Dict:
        """检查页面整体颜色和字体颜色（第一步判断）
        页面背景为白色，字体为黑色（需要排除画的红框和标注的红色数字）
        """
        result = {'valid': False, 'reason': '', 'details': {}}
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 1. 先识别红色区域（红框和红色数字）
        red_mask = self._get_red_annotation_mask(hsv)
        
        # 2. 创建排除红色区域的掩码
        non_red_mask = cv2.bitwise_not(red_mask)
        
        # 3. 在排除红色区域后计算白底黑字占比
        white_ratio, black_ratio = self._calculate_white_black_ratio_excluding_red(hsv, non_red_mask)
        red_ratio = cv2.countNonZero(red_mask) / (hsv.shape[0] * hsv.shape[1])
        
        result['details'] = {
            'white_ratio': white_ratio,
            'black_ratio': black_ratio,
            'red_ratio': red_ratio,
            'red_excluded': True  # 标记已排除红色区域
        }
        
        # 验证白底黑字特征（已排除红色干扰）
        if white_ratio < self.thresholds['white_bg_min']:
            result['reason'] = f'排除红色标注后，白色背景占比不足：{white_ratio:.1%} < {self.thresholds["white_bg_min"]:.1%}'
            return result
        
        if black_ratio < self.thresholds['black_text_min']:
            result['reason'] = f'排除红色标注后，黑色文字占比不足：{black_ratio:.1%} < {self.thresholds["black_text_min"]:.1%}'
            return result
        
        result['valid'] = True
        result['reason'] = f'页面颜色符合要求（已排除{red_ratio:.1%}红色标注）：白底{white_ratio:.1%}，黑字{black_ratio:.1%}'
        return result
    
    def _detect_horizontal_lines(self, image: np.ndarray) -> Dict:
        """检测2条黑色长横线（第二步判断）
        黑色长横线定义：
        - 左右长度一般>=70%页面宽度
        - 两横线相等长度
        - 高度一般就几个像素
        - 两横线间距离>=65%页面高度
        """
        result = {'valid': False, 'reason': '', 'lines': [], 'details': {}}
        
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 更严格的边缘检测，以检测细线条
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        
        # 霍夫直线检测 - 针对细线条调整参数
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=max(width//6, 100))
        
        horizontal_lines = []
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                # 更严格的水平线判断（角度误差小于2度）
                if abs(theta) < np.pi/90 or abs(theta - np.pi) < np.pi/90:
                    # 计算线条在图像中的y坐标
                    y_pos = abs(rho * np.sin(theta))
                    # 验证线条长度（至少是页面宽度的70%）
                    line_length = self._calculate_line_length(edges, rho, theta)
                    if line_length >= width * self.thresholds['line_width_min']:
                        # 检查线条高度（应该是几个像素）
                        line_thickness = self._calculate_line_thickness(edges, rho, theta)
                        if line_thickness <= 5:  # 高度不超过5个像素
                            horizontal_lines.append({
                                'y': y_pos,
                                'length': line_length,
                                'thickness': line_thickness,
                                'rho': rho,
                                'theta': theta
                            })
        
        # 按y坐标排序
        horizontal_lines.sort(key=lambda x: x['y'])
        
        result['details']['total_lines'] = len(horizontal_lines)
        result['lines'] = horizontal_lines
        
        # 如果检测到的横线太多，选择最重要的两条
        if len(horizontal_lines) == 0:
            result['reason'] = '未检测到符合要求的横线'
            return result
        elif len(horizontal_lines) == 1:
            result['reason'] = '只检测到1条横线，要求2条'
            return result
        elif len(horizontal_lines) > 2:
            # 保存原始检测到的横线数量
            original_count = len(horizontal_lines)
            
            # 选择间距最大的两条线（最可能是主要分割线）
            max_distance = 0
            best_pair = None
            for i in range(len(horizontal_lines)):
                for j in range(i+1, len(horizontal_lines)):
                    distance = abs(horizontal_lines[j]['y'] - horizontal_lines[i]['y'])
                    if distance > max_distance:
                        max_distance = distance
                        best_pair = (i, j)
            
            if best_pair and max_distance > height * 0.2:  # 降低要求到20%的间距
                selected_lines = [horizontal_lines[best_pair[0]], horizontal_lines[best_pair[1]]]
                selected_lines.sort(key=lambda x: x['y'])  # 重新按y坐标排序
                horizontal_lines = selected_lines
                self.logger.debug(f"从{original_count}条线中选择了间距最大的两条：y={horizontal_lines[0]['y']:.0f}, y={horizontal_lines[1]['y']:.0f}")
            else:
                # 如果找不到合适的线对，尝试选择最长的两条线
                lines_by_length = sorted(horizontal_lines, key=lambda x: x['length'], reverse=True)
                if len(lines_by_length) >= 2:
                    top_two = lines_by_length[:2]
                    top_two.sort(key=lambda x: x['y'])  # 按y坐标排序
                    distance = abs(top_two[1]['y'] - top_two[0]['y'])
                    if distance > height * 0.15:  # 至少15%的间距
                        horizontal_lines = top_two
                        self.logger.debug(f"选择了最长的两条线：长度={horizontal_lines[0]['length']:.0f}, {horizontal_lines[1]['length']:.0f}")
                    else:
                        result['reason'] = f'检测到{original_count}条横线，但无法找到合适的两条主线（间距或长度不足）'
                        return result
                else:
                    result['reason'] = f'检测到{original_count}条横线，但无法找到合适的两条主线'
                    return result
        
        # 现在应该有恰好2条横线
        if len(horizontal_lines) != 2:
            result['reason'] = f'处理后仍有{len(horizontal_lines)}条横线，要求恰好2条'
            return result
        
        # 验证两条横线间距（必须>=65%页面高度）
        line1_y, line2_y = horizontal_lines[0]['y'], horizontal_lines[1]['y']
        line_distance = abs(line2_y - line1_y)
        distance_ratio = line_distance / height
        
        if distance_ratio < self.thresholds['line_distance_min']:
            result['reason'] = f'两横线间距不足：{distance_ratio:.1%} < {self.thresholds["line_distance_min"]:.1%}'
            return result
        
        # 验证横线长度是否相等（允许5%误差）
        len1, len2 = horizontal_lines[0]['length'], horizontal_lines[1]['length']
        length_diff_ratio = abs(len1 - len2) / max(len1, len2)
        if length_diff_ratio > 0.05:
            result['reason'] = f'两横线长度差异过大：{len1:.0f}px vs {len2:.0f}px（差异{length_diff_ratio:.1%}）'
            return result
        
        # 验证线条高度（应该都是几个像素）
        thick1, thick2 = horizontal_lines[0]['thickness'], horizontal_lines[1]['thickness']
        if thick1 > 5 or thick2 > 5:
            result['reason'] = f'横线高度过大：{thick1:.0f}px, {thick2:.0f}px（应<=5px）'
            return result
        
        result['valid'] = True
        result['reason'] = f'检测到2条符合要求的横线，间距{distance_ratio:.1%}'
        result['details'].update({
            'line1_y': line1_y,
            'line2_y': line2_y,
            'distance_ratio': distance_ratio,
            'line1_length': len1,
            'line2_length': len2
        })
        
        return result
    
    def _divide_three_regions(self, image: np.ndarray, lines_info: Dict) -> Dict:
        """基于横线划分三个部分（第三步判断）"""
        result = {'valid': False, 'reason': '', 'regions': {}}
        
        if not lines_info['valid'] or len(lines_info['lines']) != 2:
            result['reason'] = '横线检测未通过，无法划分区域'
            return result
        
        height, width = image.shape[:2]
        line1_y = lines_info['lines'][0]['y']
        line2_y = lines_info['lines'][1]['y']
        
        # 定义三个区域
        regions = {
            'upper': {'y': 0, 'height': int(line1_y), 'name': '上部'},
            'middle': {'y': int(line1_y), 'height': int(line2_y - line1_y), 'name': '中部'},
            'lower': {'y': int(line2_y), 'height': int(height - line2_y), 'name': '下部'}
        }
        
        # 验证各区域高度比例
        upper_ratio = regions['upper']['height'] / height
        middle_ratio = regions['middle']['height'] / height
        lower_ratio = regions['lower']['height'] / height
        
        # 检查上部高度（<=30%页面高度）
        if upper_ratio > self.thresholds['upper_height_max']:
            result['reason'] = f'上部高度超标：{upper_ratio:.1%} > {self.thresholds["upper_height_max"]:.1%}页面高度'
            return result
        
        # 检查中部高度（>=50%页面高度）
        if middle_ratio < self.thresholds['middle_height_min']:
            result['reason'] = f'中部高度不足：{middle_ratio:.1%} < {self.thresholds["middle_height_min"]:.1%}页面高度'
            return result
        
        # 检查下部高度（<=30%页面高度）
        if lower_ratio > self.thresholds['lower_height_max']:
            result['reason'] = f'下部高度超标：{lower_ratio:.1%} > {self.thresholds["lower_height_max"]:.1%}页面高度'
            return result
        
        # 验证留白比例
        whitespace_check = self._check_region_whitespace(image, regions)
        if not whitespace_check['valid']:
            result['reason'] = whitespace_check['reason']
            return result
        
        result['valid'] = True
        result['reason'] = f'三区域划分合理：上{upper_ratio:.1%}页面高度，中{middle_ratio:.1%}页面高度，下{lower_ratio:.1%}页面高度'
        result['regions'] = regions
        result['ratios'] = {
            'upper_ratio': upper_ratio,
            'middle_ratio': middle_ratio,
            'lower_ratio': lower_ratio
        }
        
        return result
    
    def _check_region_whitespace(self, image: np.ndarray, regions: Dict) -> Dict:
        """检查各区域留白比例"""
        result = {'valid': True, 'reason': '', 'whitespace_ratios': {}}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        for region_name, region_info in regions.items():
            y_start = region_info['y']
            y_end = y_start + region_info['height']
            region_image = gray[y_start:y_end, :]
            
            # 计算白色像素比例（阈值200以上认为是白色）
            white_pixels = np.sum(region_image > 200)
            total_pixels = region_image.shape[0] * region_image.shape[1]
            whitespace_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
            
            result['whitespace_ratios'][region_name] = whitespace_ratio
            
            # 根据区域要求验证留白
            if region_name == 'upper' and whitespace_ratio < 0.30:
                result['valid'] = False
                result['reason'] = f'上部留白不足：{whitespace_ratio:.1%} < 30%'
                break
            elif region_name == 'middle' and whitespace_ratio < 0.50:
                result['valid'] = False
                result['reason'] = f'中部留白不足：{whitespace_ratio:.1%} < 50%'
                break
            elif region_name == 'lower' and whitespace_ratio < 0.30:
                result['valid'] = False
                result['reason'] = f'下部留白不足：{whitespace_ratio:.1%} < 30%'
                break
        
        return result
    

    
    def _check_local_details(self, image: np.ndarray, regions: Dict) -> Dict:
        """检查每个部分局部细节（第四步判断）"""
        result = {'valid': False, 'reason': '', 'details': {}}
        
        if not regions:
            result['reason'] = '区域信息缺失'
            return result
        
        # OCR配置
        ocr_configs = [
            '--psm 6 -l chi_sim+eng',
            '--psm 7 -l chi_sim+eng',
            '--psm 8 -l chi_sim+eng',
            '--psm 13 -l chi_sim+eng'
        ]
        
        height, width = image.shape[:2]
        checks_passed = []
        
        # 检查上部细节（标准logo、标准分类、标准号）
        upper_check = self._check_upper_details(image, regions['upper'], ocr_configs, width)
        result['details']['upper'] = upper_check
        if upper_check['valid']:
            checks_passed.append('上部检查通过')
        
        # 检查中部细节（发布、实施）
        middle_check = self._check_middle_details(image, regions['middle'], ocr_configs)
        result['details']['middle'] = middle_check
        if middle_check['valid']:
            checks_passed.append('中部检查通过')
        
        # 检查下部细节（发布）
        lower_check = self._check_lower_details(image, regions['lower'], ocr_configs)
        result['details']['lower'] = lower_check
        if lower_check['valid']:
            checks_passed.append('下部检查通过')
        
        # 所有三个部分都必须通过
        if len(checks_passed) == 3:
            result['valid'] = True
            result['reason'] = '所有区域局部细节检查通过'
        else:
            failed_parts = []
            if not upper_check['valid']:
                failed_parts.append(f"上部: {upper_check['reason']}")
            if not middle_check['valid']:
                failed_parts.append(f"中部: {middle_check['reason']}")
            if not lower_check['valid']:
                failed_parts.append(f"下部: {lower_check['reason']}")
            result['reason'] = '局部细节检查失败: ' + '; '.join(failed_parts)
        
        return result
    
    def _check_upper_details(self, image: np.ndarray, upper_region: Dict, ocr_configs: list, page_width: int) -> Dict:
        """检查上部细节：只需要找到"标准"二字"""
        result = {'valid': False, 'reason': '', 'found_items': []}
        
        y_start = upper_region['y']
        y_end = y_start + upper_region['height']
        region_image = image[y_start:y_end, :]
        
        # 图像预处理
        gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # OCR检测"标准"二字（这是唯一的要求）
        standard_found = False
        for config in ocr_configs:
            try:
                text = pytesseract.image_to_string(enhanced, config=config)
                if '标准' in text:
                    standard_found = True
                    result['found_items'].append('标准')
                    break
            except:
                continue
        
        
        # 只需要找到"标准"二字
        if standard_found:
            result['valid'] = True
            result['reason'] = "上部找到必需的'标准'关键词"
        else:
            result['reason'] = "上部未找到'标准'关键词"
        
        return result
    
    def _check_middle_details(self, image: np.ndarray, middle_region: Dict, ocr_configs: list) -> Dict:
        """检查中部细节：只需要找到"发布"二字"""
        result = {'valid': False, 'reason': '', 'found_items': []}
        
        y_start = middle_region['y']
        y_end = y_start + middle_region['height']
        region_image = image[y_start:y_end, :]
        
        # 图像预处理
        gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # OCR检测"发布"二字（这是唯一的要求）
        publish_found = False
        
        for config in ocr_configs:
            try:
                text = pytesseract.image_to_string(enhanced, config=config)
                if '发布' in text:
                    publish_found = True
                    result['found_items'].append('发布')
                    break
            except:
                continue
        
        
        # 只需要找到"发布"二字
        if publish_found:
            result['valid'] = True
            result['reason'] = "中部找到必需的'发布'关键词"
        else:
            result['reason'] = "中部未找到'发布'关键词"
        
        return result
    
    def _check_lower_details(self, image: np.ndarray, lower_region: Dict, ocr_configs: list) -> Dict:
        """检查下部细节：只需要找到“发布”二字"""
        result = {'valid': False, 'reason': '', 'found_items': []}
        
        y_start = lower_region['y']
        y_end = y_start + lower_region['height']
        region_image = image[y_start:y_end, :]
        
        # 图像预处理
        gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # OCR检测“发布”二字
        publish_found = False
        for config in ocr_configs:
            try:
                text = pytesseract.image_to_string(enhanced, config=config)
                if '发布' in text:
                    publish_found = True
                    result['found_items'].append('发布')
                    break
            except:
                continue
        
        
        if publish_found:
            result['valid'] = True
            result['reason'] = "下部找到必需的'发布'关键词"
        else:
            result['reason'] = "下部未找到'发布'关键词"
        
        return result
    
    def _detect_logo_position(self, region_image: np.ndarray, page_width: int) -> bool:
        """检测logo位置是否在x>=40%的位置"""
        # 简化检测：寻找右侧区域是否有图案/文字集中
        gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
        
        # 分析右半部分（x >= 40%）的内容密度
        right_start = int(page_width * self.thresholds['logo_x_min'])
        right_region = gray[:, right_start:]
        
        if right_region.size == 0:
            return False
        
        # 计算非白色像素密度
        non_white_pixels = np.sum(right_region < 200)
        total_pixels = right_region.shape[0] * right_region.shape[1]
        density = non_white_pixels / total_pixels if total_pixels > 0 else 0
        
        # 如果右侧区域有一定的内容密度，认为可能有logo
        return density > 0.02
    
    def _detect_standard_number(self, enhanced_image: np.ndarray, ocr_configs: list) -> bool:
        """检测标准号格式：横杠+年份(19xx或20xx)"""
        import re
        
        for config in ocr_configs:
            try:
                text = pytesseract.image_to_string(enhanced, config=config)
                # 查找格式：横杠后跟19xx或20xx年份
                pattern = r'[-—–]\s*(19|20)\d{2}'
                if re.search(pattern, text):
                    return True
            except:
                continue
        
        return False
    
    
    def _calculate_line_length(self, edges: np.ndarray, rho: float, theta: float) -> float:
        """计算线条的实际长度"""
        height, width = edges.shape
        
        # 计算线条的端点
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        
        # 找到线条与图像边界的交点
        if abs(b) > 0.001:  # 不是垂直线
            # 与左右边界的交点
            y_left = y0 - x0 * a / b
            y_right = y0 + (width - x0) * a / b
        
        # 约束到图像范围内
            x_start = 0 if 0 <= y_left <= height else (width if 0 <= y_right <= height else None)
            x_end = width if 0 <= y_right <= height else (0 if 0 <= y_left <= height else None)
            
            if x_start is not None and x_end is not None:
                return abs(x_end - x_start)
        
        return width  # 默认返回图像宽度
    
    def _calculate_line_thickness(self, edges: np.ndarray, rho: float, theta: float) -> float:
        """计算线条的高度（厚度）"""
        height, width = edges.shape
        
        # 计算线条的中心点
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        
        # 在线条中心附近检查垂直方向的厚度
        center_x = int(x0)
        center_y = int(y0)
        
        if 0 <= center_x < width and 0 <= center_y < height:
            # 在垂直方向上检查线条厚度
            thickness = 0
            for dy in range(-10, 11):  # 检查上下10个像素
                y = center_y + dy
                if 0 <= y < height and edges[y, center_x] > 0:
                    thickness += 1
            return thickness
        
        return 1  # 默认厚度
    

    

    

    
    def _extract_features(self, image: np.ndarray, filename: str = '') -> Dict:
        """按照新的四步法提取图像特征"""
        features = {
            'filename': filename,
            'step1_colors': {},
            'step2_lines': {},
            'step3_regions': {},
            'step4_details': {},
            'final_result': False
        }
        
        # 第一步：页面整体颜色和字体颜色
        step1_result = self._check_page_colors(image)
        features['step1_colors'] = step1_result
        
        if not step1_result['valid']:
            features['final_result'] = False
            features['failure_reason'] = f"第一步失败: {step1_result['reason']}"
            return features
        
        # 第二步：2条黑色长横线
        step2_result = self._detect_horizontal_lines(image)
        features['step2_lines'] = step2_result
        
        if not step2_result['valid']:
            features['final_result'] = False
            features['failure_reason'] = f"第二步失败: {step2_result['reason']}"
            return features
        
        # 第三步：三个部分（基于横线划分）
        step3_result = self._divide_three_regions(image, step2_result)
        features['step3_regions'] = step3_result
        
        if not step3_result['valid']:
            features['final_result'] = False
            features['failure_reason'] = f"第三步失败: {step3_result['reason']}"
            return features
        
        # 第四步：每个部分局部细节
        step4_result = self._check_local_details(image, step3_result['regions'])
        features['step4_details'] = step4_result
        
        if not step4_result['valid']:
            features['final_result'] = False
            features['failure_reason'] = f"第四步失败: {step4_result['reason']}"
            return features
        
        # 所有步骤都通过
        features['final_result'] = True
        features['success_reason'] = '所有四步检查均通过，确认为标准文件'
        
        return features
    
    def _convert_pdf_to_images(self, pdf_path: str, max_pages: int = 3):
        """
        将PDF转换为图像，支持多种后端
        
        Args:
            pdf_path: PDF文件路径
            max_pages: 最大页数
            
        Returns:
            图像列表
        """
        images = []
        
        # 先尝试PyMuPDF（更稳定）
        try:
            import fitz
            self.logger.debug(f"使用PyMuPDF处理: {pdf_path}")
            doc = fitz.open(pdf_path)
            
            for page_num in range(min(max_pages, len(doc))):
                page = doc.load_page(page_num)
                # 设置缩放比例，相当于300 DPI
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为numpy数组
                img_data = pix.samples
                img_array = np.frombuffer(img_data, dtype=np.uint8)
                img_array = img_array.reshape(pix.height, pix.width, pix.n)
                
                # 转换颜色空间
                if pix.n == 4:  # RGBA
                    opencv_image = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                elif pix.n == 3:  # RGB
                    opencv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:  # 灰度图
                    opencv_image = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
                
                images.append(opencv_image)
            
            doc.close()
            self.logger.debug(f"PyMuPDF成功转换了{len(images)}页")
            return images
            
        except Exception as e:
            self.logger.warning(f"PyMuPDF失败: {e}")
        
        # 备用：尝试pdf2image
        if PDF_BACKEND == 'pdf2image':
            try:
                self.logger.debug(f"使用pdf2image处理: {pdf_path}")
                images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=max_pages)
                opencv_images = [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in images]
                self.logger.debug(f"pdf2image成功转换了{len(opencv_images)}页")
                return opencv_images
            except Exception as e:
                self.logger.warning(f"pdf2image也失败: {e}")
        
        # 如果所有方法都失败
        raise Exception(f"无法转换PDF文件: {pdf_path}，请检查文件是否损坏或PDF处理库安装")
    
    def _validate_features(self, features: Dict) -> bool:
        """基于新的四步法验证特征 - 严格按照逐步判断"""
        # 新的验证逻辑：必须四步全部通过
        is_valid = features.get('final_result', False)
        
        # 详细日志输出
        if is_valid:
            self.logger.info("✅ 标准文件验证通过 - 所有四步检查均通过")
            self.logger.info(f"   第一步: {features['step1_colors']['reason']}")
            self.logger.info(f"   第二步: {features['step2_lines']['reason']}")
            self.logger.info(f"   第三步: {features['step3_regions']['reason']}")
            self.logger.info(f"   第四步: {features['step4_details']['reason']}")
        else:
            failure_reason = features.get('failure_reason', '未知原因')
            self.logger.info(f"❌ 标准文件验证失败: {failure_reason}")
        
        return is_valid
    

    
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
            
            # 使用新的PDF转换方法（最多检索前3页）
            images = self._convert_pdf_to_images(pdf_path, max_pages=3)
            
            for page_num, opencv_image in enumerate(images):
                if time.time() - start_time > timeout:
                    result['reason'] = '处理超时'
                    return result
                
                filename = os.path.basename(pdf_path)
                features = self._extract_features(opencv_image, filename)
                
                # 保存最后一次特征用于调试
                self._last_features = features
                
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
    
    def batch_process(self, input_dir: str, output_dir: str = "jc", recursive: bool = False) -> Dict:
        """批量处理PDF文件"""
        results = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'successful_paths': [],
            'failed_reasons': {}
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取PDF文件列表
        pdf_files = self._find_pdf_files(input_dir, recursive)
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            results['total_files'] += 1
            
            self.logger.info(f"处理文件: {pdf_path}")
            
            result = self.process_pdf(pdf_path)
            
            if result['success']:
                # 生成唯一的输出文件名（防止重名）
                output_filename = self._generate_unique_filename(output_dir, filename)
                output_path = os.path.join(output_dir, output_filename)
                try:
                    import shutil
                    shutil.copy2(pdf_path, output_path)
                    results['successful_files'] += 1
                    results['successful_paths'].append(pdf_path)
                    self.logger.info(f"✓ {pdf_path} 匹配成功，已复制到 {output_dir}/{output_filename}")
                except Exception as e:
                    self.logger.error(f"复制文件 {filename} 失败: {str(e)}")
                    results['failed_files'] += 1
                    results['failed_reasons'][pdf_path] = f"复制失败: {str(e)}"
            else:
                results['failed_files'] += 1
                results['failed_reasons'][pdf_path] = result['reason']
                self.logger.info(f"✗ {pdf_path} 不匹配: {result['reason']}")
        
        return results
    
    def _find_pdf_files(self, root_dir: str, recursive: bool = False) -> list:
        """查找PDF文件"""
        pdf_files = []
        
        if recursive:
            # 递归搜索所有子目录
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        else:
            # 只搜索当前目录
            if os.path.exists(root_dir):
                for filename in os.listdir(root_dir):
                    if filename.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root_dir, filename))
        
        return pdf_files
    
    def _generate_unique_filename(self, output_dir: str, filename: str) -> str:
        """生成唯一的文件名"""
        base_name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        
        while os.path.exists(os.path.join(output_dir, new_filename)):
            new_filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        return new_filename
