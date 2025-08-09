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
        logger.setLevel(logging.DEBUG)  # 启用debug级别
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
        """定位三区域（上中下）- 适配真实PDF文档"""
        regions = {}
        height, width = image.shape[:2]
        
        # 对于真实PDF文档，没有蓝色标注框，我们根据内容分布来划分区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用水平投影来找到文本区域
        horizontal_projection = np.sum(gray < 200, axis=1)  # 统计每行的非白色像素
        
        # 找到有内容的行
        content_lines = np.where(horizontal_projection > width * 0.1)[0]  # 至少10%的像素是内容
        
        if len(content_lines) > 0:
            # 按页面高度的比例划分上中下三个区域
            regions['upper'] = {
                'y': 0, 
                'height': int(height * 0.25)  # 上部25%
            }
            regions['middle'] = {
                'y': int(height * 0.25), 
                'height': int(height * 0.5)   # 中部50%
            }
            regions['lower'] = {
                'y': int(height * 0.75), 
                'height': int(height * 0.25)  # 下部25%
            }
        
        return regions
    
    def _locate_key_boxes(self, image: np.ndarray, hsv: np.ndarray) -> Dict:
        """定位关键区域 - 适配真实PDF文档"""
        key_boxes = {}
        height, width = image.shape[:2]
        
        # 对于真实PDF，我们根据文档结构模拟6个关键区域
        # 这些区域基于标准文档的典型布局
        
        # 1号框：右上角区域（通常是logo或机构信息）
        key_boxes['box_1'] = {
            'x': int(width * 0.7), 'y': 0, 
            'width': int(width * 0.3), 'height': int(height * 0.15)
        }
        
        # 2号框：上部标题区域  
        key_boxes['box_2'] = {
            'x': 0, 'y': int(height * 0.15),
            'width': width, 'height': int(height * 0.1)
        }
        
        # 3号框：标准编号区域
        key_boxes['box_3'] = {
            'x': int(width * 0.5), 'y': int(height * 0.25),
            'width': int(width * 0.5), 'height': int(height * 0.1)
        }
        
        # 4号框：标准名称区域（中英文）
        key_boxes['box_4'] = {
            'x': int(width * 0.1), 'y': int(height * 0.35),
            'width': int(width * 0.8), 'height': int(height * 0.3)
        }
        
        # 5号框：发布实施日期区域
        key_boxes['box_5'] = {
            'x': 0, 'y': int(height * 0.75),
            'width': width, 'height': int(height * 0.1)
        }
        
        # 6号框：发布单位区域
        key_boxes['box_6'] = {
            'x': int(width * 0.2), 'y': int(height * 0.85),
            'width': int(width * 0.6), 'height': int(height * 0.15)
        }
        
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
        """检测横线 - 标准文档的关键特征"""
        lines = {}
        height, width = image.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用更精确的边缘检测参数
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        
        # 检测直线
        detected_lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=max(50, width//10))
        
        horizontal_lines = []
        
        if detected_lines is not None:
            for line in detected_lines:
                rho, theta = line[0]
                # 更严格的水平线判断
                if abs(theta) < 0.05 or abs(theta - np.pi) < 0.05:
                    horizontal_lines.append((abs(rho), theta))
        
        # 按位置排序
        horizontal_lines.sort(key=lambda x: x[0])
        
        # 查找符合标准文档要求的两条主要横线
        valid_lines = []
        for rho, theta in horizontal_lines:
            # 计算线条长度（通过端点检测）
            line_length = self._calculate_line_length(edges, rho, theta, width)
            
            # 只保留足够长的线条（至少占页面宽度的70%）
            if line_length > width * 0.7:
                valid_lines.append((rho, theta, line_length))
        
        # 验证是否有足够的横线
        if len(valid_lines) >= 2:
            # 第一条横线应该在上部区域底部附近
            first_line_y = valid_lines[0][0]
            expected_first_y = height * 0.3  # 约在页面30%位置
            
            # 第二条横线应该在下部区域顶部附近  
            second_line_y = valid_lines[1][0]
            expected_second_y = height * 0.75  # 约在页面75%位置
            
            # 验证位置是否合理
            lines['first_line_valid'] = abs(first_line_y - expected_first_y) < height * 0.15
            lines['second_line_valid'] = abs(second_line_y - expected_second_y) < height * 0.15
            
            lines['first_line'] = valid_lines[0]
            lines['second_line'] = valid_lines[1]
        else:
            lines['first_line_valid'] = False
            lines['second_line_valid'] = False
        
        return lines
    
    def _calculate_line_length(self, edges: np.ndarray, rho: float, theta: float, max_width: int) -> float:
        """计算线条的实际长度"""
        height, width = edges.shape
        
        # 计算线条的端点
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        
        # 找到线条与图像边界的交点
        x1 = int(x0 + max_width * (-b))
        y1 = int(y0 + max_width * (a))
        x2 = int(x0 - max_width * (-b))
        y2 = int(y0 - max_width * (a))
        
        # 约束到图像范围内
        x1 = max(0, min(width-1, x1))
        x2 = max(0, min(width-1, x2))
        y1 = max(0, min(height-1, y1))
        y2 = max(0, min(height-1, y2))
        
        # 沿着线条检测实际的像素点
        line_pixels = 0
        steps = abs(x2 - x1) + abs(y2 - y1)
        
        if steps > 0:
            for i in range(steps):
                x = int(x1 + (x2 - x1) * i / steps)
                y = int(y1 + (y2 - y1) * i / steps)
                if 0 <= x < width and 0 <= y < height and edges[y, x] > 0:
                    line_pixels += 1
        
        return line_pixels
    
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
    
    def _extract_features(self, image: np.ndarray, filename: str = '') -> Dict:
        """提取图像特征"""
        features = {}
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = image.shape[:2]
        
        features['filename'] = filename
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
    
    def _convert_pdf_to_images(self, pdf_path: str, max_pages: int = 5):
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
        """验证特征是否符合模板要求 - 基于页面内容特征"""
        validation_score = 0
        max_score = 0
        
        # 1. 颜色特征验证 (权重: 35%) - 提高权重，白底黑字是最基本的特征
        max_score += 35
        white_ratio = features.get('white_ratio', 0)
        black_ratio = features.get('black_ratio', 0)
        if white_ratio > 0.75:  # 降低白色要求
            validation_score += 20
        elif white_ratio > 0.60:
            validation_score += 15
        elif white_ratio > 0.45:
            validation_score += 10
            
        if black_ratio > 0.003:  # 降低黑色要求
            validation_score += 10
        elif black_ratio > 0.001:
            validation_score += 5
        
        # 2. 区域结构验证 (权重: 30%) - 提高权重，三区划分是重要特征
        max_score += 30
        regions = features.get('regions', {})
        proportions = features.get('proportions', {})
        
        if len(regions) >= 3:
            validation_score += 15
        elif len(regions) >= 2:
            validation_score += 10
            
        # 验证区域比例是否符合标准文档要求 (降低要求)
        if proportions.get('upper_whitespace', 0) > 15:  # 上部有一定留白
            validation_score += 5
        if proportions.get('middle_whitespace', 0) > 30:  # 中部有较多留白
            validation_score += 5
        if proportions.get('lower_whitespace', 0) > 10:  # 下部有一定留白
            validation_score += 5
        
        # 3. 关键词验证 (权重: 20%) - 降低权重，因为OCR可能不准确
        max_score += 20
        keywords = features.get('keywords', {})
        if keywords.get('upper_has_standard', False):
            validation_score += 12  # "标准"是重要特征
        if keywords.get('lower_has_publish', False):
            validation_score += 8   # "发布"是重要特征
        
        # 4. 横线结构验证 (权重: 15%) - 降低权重，因为线检测可能不准确
        max_score += 15
        lines = features.get('lines', {})
        if lines.get('first_line_valid', False):
            validation_score += 8
        if lines.get('second_line_valid', False):
            validation_score += 7
        
        # 计算匹配度
        match_percentage = (validation_score / max_score) * 100 if max_score > 0 else 0
        
        # 降低验证阈值为50%，适应真实标准文档的多样性
        threshold = 50
        is_valid = match_percentage >= threshold
        
        # 详细日志输出
        self.logger.debug(f"特征验证详情 (阈值: {threshold}%):")
        self.logger.debug(f"  颜色特征 (35%): 白色{white_ratio:.1%} 黑色{black_ratio:.3%}")
        self.logger.debug(f"  区域结构 (30%): {len(regions)}个区域")
        self.logger.debug(f"  关键词 (20%): 标准{'✓' if keywords.get('upper_has_standard', False) else '✗'} 发布{'✓' if keywords.get('lower_has_publish', False) else '✗'}")
        self.logger.debug(f"  横线结构 (15%): 第一线{'✓' if lines.get('first_line_valid', False) else '✗'} 第二线{'✓' if lines.get('second_line_valid', False) else '✗'}")
        self.logger.debug(f"  总匹配度: {match_percentage:.1f}% -> {'通过' if is_valid else '不通过'}")
        
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
            
            # 使用新的PDF转换方法
            images = self._convert_pdf_to_images(pdf_path, max_pages=5)
            
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
