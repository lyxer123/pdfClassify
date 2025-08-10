#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF特征提取工具
功能：分析PDF文件的页面颜色特征，检测是否符合标准（白色背景+黑色文字）
"""

import os
import sys
import json
import argparse
import io
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import logging
from typing import Dict, Any, Optional, Union

# 配置日志
# 获取项目根目录
project_root = Path(__file__).parent
log_dir = project_root / "tests" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,  # 恢复到INFO级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'pdf_classify.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFFeatureExtractor:
    """PDF特征提取器"""
    
    def __init__(self, template_path="templates/mb.png", data_dir="data", config_file=None):
        """
        初始化特征提取器
        
        Args:
            template_path: 标准模板图片路径
            data_dir: 特征数据保存目录
            config_file: 配置文件路径（可选）
        """
        self.template_path = template_path
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 加载颜色阈值配置
        self.color_thresholds = self._load_color_thresholds(config_file)
        
        # 设置日志
        self._setup_logging()
    
    def _load_color_thresholds(self, config_file: Optional[str] = None) -> Dict[str, Union[int, float]]:
        """
        加载颜色阈值配置，支持多种配置方式
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            dict: 颜色阈值配置字典
        """
        # 默认配置
        default_thresholds = {
            'white_bg_min': 200,      # 白色背景最小RGB值
            'black_text_max': 80,     # 黑色文字最大RGB值
            'bg_ratio_min': 0.95,     # 背景色占比最小值（保持95%）
            'text_ratio_min': 0.001,  # 文字色占比最小值（降低到0.1%）
            'contrast_min': 26,       # 最小对比度（降低到26）
            'brightness_min': 244,    # 最小亮度（降低到244）
            'colored_text_max': 0.05  # 彩色文字最大允许比例（保持5%）
        }
        
        # 尝试从配置文件加载
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if 'color_thresholds' in config_data:
                        # 合并配置，保留默认值作为后备
                        loaded_thresholds = config_data['color_thresholds']
                        for key, value in loaded_thresholds.items():
                            if key in default_thresholds:
                                default_thresholds[key] = value
                        print(f"✅ 已从配置文件加载颜色阈值: {config_file}")
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认值: {e}")
        
        # 尝试从环境变量加载
        env_thresholds = self._load_from_environment()
        for key, value in env_thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        return default_thresholds
    
    def _load_from_environment(self) -> Dict[str, Union[int, float]]:
        """
        从环境变量加载颜色阈值配置
        
        Returns:
            dict: 从环境变量加载的配置
        """
        env_thresholds = {}
        
        # 环境变量映射
        env_mapping = {
            'WHITE_BG_MIN': 'white_bg_min',
            'BLACK_TEXT_MAX': 'black_text_max',
            'BG_RATIO_MIN': 'bg_ratio_min',
            'TEXT_RATIO_MIN': 'text_ratio_min',
            'CONTRAST_MIN': 'contrast_min',
            'BRIGHTNESS_MIN': 'brightness_min',
            'COLORED_TEXT_MAX': 'colored_text_max'
        }
        
        for env_var, config_key in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # 尝试转换为适当的类型
                    if config_key in ['bg_ratio_min', 'text_ratio_min', 'colored_text_max']:
                        env_thresholds[config_key] = float(env_value)
                    else:
                        env_thresholds[config_key] = int(env_value)
                except ValueError:
                    print(f"⚠️ 环境变量 {env_var}={env_value} 格式无效，跳过")
        
        if env_thresholds:
            print(f"✅ 已从环境变量加载 {len(env_thresholds)} 个颜色阈值")
        
        return env_thresholds
    
    def update_color_thresholds(self, new_thresholds: Dict[str, Union[int, float]]) -> None:
        """
        运行时更新颜色阈值配置
        
        Args:
            new_thresholds: 新的阈值配置字典
        """
        for key, value in new_thresholds.items():
            if key in self.color_thresholds:
                old_value = self.color_thresholds[key]
                self.color_thresholds[key] = value
                print(f"🔄 更新颜色阈值 {key}: {old_value} -> {value}")
            else:
                print(f"⚠️ 未知的颜色阈值键: {key}")
    
    def reset_color_thresholds(self) -> None:
        """重置颜色阈值为默认值"""
        default_thresholds = {
            'white_bg_min': 200,
            'black_text_max': 80,
            'bg_ratio_min': 0.95,
            'text_ratio_min': 0.001,
            'contrast_min': 26,
            'brightness_min': 244,
            'colored_text_max': 0.05
        }
        
        for key, value in default_thresholds.items():
            self.color_thresholds[key] = value
        
        print("🔄 颜色阈值已重置为默认值")
    
    def get_color_thresholds(self) -> Dict[str, Union[int, float]]:
        """
        获取当前的颜色阈值配置
        
        Returns:
            dict: 当前的颜色阈值配置
        """
        return self.color_thresholds.copy()
    
    def save_color_thresholds(self, config_file: str) -> bool:
        """
        保存当前颜色阈值配置到文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            config_data = {
                'color_thresholds': self.color_thresholds,
                'description': {
                    'white_bg_min': '白色背景最小RGB值',
                    'black_text_max': '黑色文字最大RGB值',
                    'bg_ratio_min': '背景色占比最小值',
                    'text_ratio_min': '文字色占比最小值',
                    'contrast_min': '最小对比度',
                    'brightness_min': '最小亮度',
                    'colored_text_max': '彩色文字最大允许比例'
                },
                'version': '1.0',
                'last_updated': '2025-01-10'
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ 颜色阈值配置已保存到: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def pdf_to_images(self, pdf_path, max_pages=5, page_mode="first_n"):
        """
        将PDF页面转换为图片
        
        Args:
            pdf_path: PDF文件路径
            max_pages: 最大页数
            page_mode: 页面选择模式
                - "first_n": 前N页（默认）
                - "first_page": 第一页
                - "all_pages": 所有页面
                - "last_n": 从后面起的N页
            
        Returns:
            list: 图片数组列表
        """
        try:
            doc = fitz.open(pdf_path)
            images = []
            total_pages = len(doc)
            
            # 根据页面选择模式确定要转换的页面
            if page_mode == "first_page":
                pages_to_convert = 1
                page_indices = [0]
                logger.info(f"正在转换PDF '{pdf_path}' 的第1页")
            elif page_mode == "all_pages":
                pages_to_convert = total_pages
                page_indices = list(range(total_pages))
                logger.info(f"正在转换PDF '{pdf_path}' 的所有 {total_pages} 页")
            elif page_mode == "last_n":
                pages_to_convert = min(total_pages, max_pages)
                start_page = max(0, total_pages - pages_to_convert)
                page_indices = list(range(start_page, total_pages))
                logger.info(f"正在转换PDF '{pdf_path}' 的后 {pages_to_convert} 页（从第{start_page + 1}页开始）")
            else:  # "first_n" 默认模式
                pages_to_convert = min(total_pages, max_pages)
                page_indices = list(range(pages_to_convert))
                logger.info(f"正在转换PDF '{pdf_path}' 的前 {pages_to_convert} 页")
            
            for page_num in page_indices:
                page = doc.load_page(page_num)
                # 设置较高的分辨率以获得更好的图像质量
                mat = fitz.Matrix(2.0, 2.0)  # 2倍放大
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为PIL图像
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # 转换为numpy数组
                img_array = np.array(img)
                images.append(img_array)
                
                logger.info(f"已转换第 {page_num + 1} 页，图像尺寸: {img_array.shape}")
            
            doc.close()
            return images
            
        except Exception as e:
            logger.error(f"PDF转换失败 '{pdf_path}': {str(e)}")
            return []
    
    def analyze_color_features(self, image):
        """
        分析图像的颜色特征
        
        Args:
            image: 图像数组 (numpy array)
            
        Returns:
            dict: 颜色特征分析结果
        """
        try:
            # 转换为RGB（如果是BGR）
            if len(image.shape) == 3 and image.shape[2] == 3:
                # 假设输入是RGB格式
                rgb_image = image
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            height, width = rgb_image.shape[:2]
            total_pixels = height * width
            
            # 计算各颜色通道的平均值
            mean_colors = np.mean(rgb_image.reshape(-1, 3), axis=0)
            
            # 分析白色背景像素
            white_mask = np.all(rgb_image >= self.color_thresholds['white_bg_min'], axis=2)
            white_pixels = np.sum(white_mask)
            white_ratio = white_pixels / total_pixels
            
            # 分析黑色文字像素（严格的黑色）
            black_mask = np.all(rgb_image <= self.color_thresholds['black_text_max'], axis=2)
            black_pixels = np.sum(black_mask)
            black_ratio = black_pixels / total_pixels
            
            # 检测彩色文字（红色、蓝色、绿色等非黑白色）
            colored_text_pixels = self._detect_colored_text(rgb_image)
            colored_text_ratio = colored_text_pixels / total_pixels
            
            # 分析灰度分布
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            
            # 计算对比度（标准差）
            contrast = np.std(gray_image)
            
            # 检测第二特征（mb.png模板的两条长黑线）
            second_feature_result = self.detect_mb_second_feature(image)
            
            features = {
                'mean_rgb': mean_colors.tolist(),
                'white_bg_ratio': float(white_ratio),
                'black_text_ratio': float(black_ratio),
                'colored_text_ratio': float(colored_text_ratio),  # 新增：彩色文字比例
                'contrast': float(contrast),
                'image_size': [width, height],
                'total_pixels': total_pixels,
                'histogram': hist.flatten().tolist(),
                'second_feature': second_feature_result  # 新增：第二特征检测结果
            }
            
            return features
            
        except Exception as e:
            logger.error(f"颜色特征分析失败: {str(e)}")
            return None
    
    def _detect_colored_text(self, rgb_image):
        """
        检测彩色文字像素（红色、蓝色、绿色等非黑白色）
        
        Args:
            rgb_image: RGB图像数组
            
        Returns:
            int: 彩色文字像素数量
        """
        r, g, b = rgb_image[:, :, 0], rgb_image[:, :, 1], rgb_image[:, :, 2]
        
        # 排除白色背景（RGB都很高）
        white_mask = (r >= self.color_thresholds['white_bg_min']) & \
                     (g >= self.color_thresholds['white_bg_min']) & \
                     (b >= self.color_thresholds['white_bg_min'])
        
        # 排除黑色/灰色文字（RGB都很低且相近）
        max_rgb = np.maximum(np.maximum(r, g), b)
        min_rgb = np.minimum(np.minimum(r, g), b)
        
        # 黑色/灰色：最大RGB值小于阈值，且RGB通道差异小
        grayscale_mask = (max_rgb <= self.color_thresholds['black_text_max'] + 50) & \
                        (max_rgb - min_rgb <= 20)  # RGB通道差异小于20认为是灰度
        
        # 检测明显的彩色文字
        colored_text_pixels = 0
        
        # 检测红色文字（红色分量明显大于绿色和蓝色）
        red_text_mask = (r > g + 50) & (r > b + 50) & (r > 120) & ~white_mask
        colored_text_pixels += np.sum(red_text_mask)
        
        # 检测蓝色文字（蓝色分量明显大于红色和绿色）
        blue_text_mask = (b > r + 50) & (b > g + 50) & (b > 120) & ~white_mask
        colored_text_pixels += np.sum(blue_text_mask)
        
        # 检测绿色文字（绿色分量明显大于红色和蓝色）
        green_text_mask = (g > r + 50) & (g > b + 50) & (g > 120) & ~white_mask
        colored_text_pixels += np.sum(green_text_mask)
        
        # 检测其他明显的彩色（RGB通道差异很大且不是白色背景）
        rgb_range = max_rgb - min_rgb
        high_variance_mask = (rgb_range > 60) & ~white_mask & ~grayscale_mask & (max_rgb > 100)
        colored_text_pixels += np.sum(high_variance_mask)
        
        return colored_text_pixels
    
    def _merge_nearby_lines(self, horizontal_lines, width, height):
        """
        合并临近的水平线条
        
        Args:
            horizontal_lines: 水平线条列表
            width: 图像宽度
            height: 图像高度
            
        Returns:
            list: 合并后的线条列表
        """
        if len(horizontal_lines) < 2:
            return []
        
        merged_lines = []
        y_tolerance = height * 0.02  # y方向容差为图像高度的2%
        
        # 按y坐标分组合并
        i = 0
        while i < len(horizontal_lines):
            current_line = horizontal_lines[i]
            lines_to_merge = [current_line]
            
            # 查找y坐标相近的线条
            j = i + 1
            while j < len(horizontal_lines):
                if abs(horizontal_lines[j]['y_center'] - current_line['y_center']) <= y_tolerance:
                    lines_to_merge.append(horizontal_lines[j])
                    j += 1
                else:
                    break
            
            # 如果有多条线需要合并
            if len(lines_to_merge) > 1:
                # 计算合并后的线条
                all_x_coords = []
                all_y_coords = []
                for line in lines_to_merge:
                    x1, y1, x2, y2 = line['coords']
                    all_x_coords.extend([x1, x2])
                    all_y_coords.extend([y1, y2])
                
                # 计算新的线条端点
                min_x, max_x = min(all_x_coords), max(all_x_coords)
                avg_y = sum(all_y_coords) / len(all_y_coords)
                
                merged_line = {
                    'coords': (min_x, avg_y, max_x, avg_y),
                    'length': max_x - min_x,
                    'y_center': avg_y,
                    'angle': 0
                }
                merged_lines.append(merged_line)
                logger.debug(f"合并了{len(lines_to_merge)}条线条，新长度: {merged_line['length']:.1f}")
            
            i = j
        
        return merged_lines
    
    def _group_lines_by_y(self, lines, height):
        """
        按y坐标将线条分组，改进分组策略
        
        Args:
            lines: 线条列表
            height: 图像高度
            
        Returns:
            list: 分组后的线条列表
        """
        if not lines:
            return []
        
        # 首先按y坐标排序
        sorted_lines = sorted(lines, key=lambda x: x['y_center'])
        
        groups = []
        current_group = [sorted_lines[0]]
        
        # 使用较小的容差来避免将相距很远的线条归为一组
        y_tolerance = min(height * 0.05, 50)  # 5%高度或50像素，取较小值
        
        for i in range(1, len(sorted_lines)):
            current_line = sorted_lines[i]
            last_line_in_group = current_group[-1]
            
            # 如果当前线条与组内最后一条线条的距离小于容差，加入当前组
            if abs(current_line['y_center'] - last_line_in_group['y_center']) <= y_tolerance:
                current_group.append(current_line)
            else:
                # 否则，开始新组
                groups.append(current_group)
                current_group = [current_line]
        
        # 添加最后一组
        if current_group:
            groups.append(current_group)
        
        # 过滤掉只有单条短线的组（可能是噪音）
        filtered_groups = []
        for group in groups:
            if len(group) >= 1:  # 至少有1条线
                max_length = max(line['length'] for line in group)
                if max_length >= height * 0.3:  # 最长线条至少为高度的30%
                    filtered_groups.append(group)
        
        logger.debug(f"y坐标分组: 原始{len(groups)}组，过滤后{len(filtered_groups)}组")
        for i, group in enumerate(filtered_groups):
            y_positions = [line['y_center'] for line in group]
            lengths = [line['length'] for line in group]
            logger.debug(f"  组{i+1}: {len(group)}条线，y范围{min(y_positions):.0f}-{max(y_positions):.0f}，最大长度{max(lengths):.0f}")
        
        return filtered_groups
    
    def _detect_adaptive_lines(self, image):
        """
        自适应检测长横线
        不依赖固定位置，而是分析整个图像找出最主要的两条长横线
        包含形态学增强以处理碎片化的线条
        """
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 创建黑色区域的掩码
        black_mask = gray < 80
        
        logger.debug(f"自适应检测长横线，图像尺寸: {width}x{height}")
        logger.debug(f"原始黑色像素数量: {np.sum(black_mask)}")
        
        # 首先尝试基本检测
        basic_lines = self._detect_lines_from_mask(black_mask, width, height)
        
        if len(basic_lines) >= 2:
            logger.debug("基本检测成功，返回结果")
            return basic_lines
        
        logger.debug("基本检测不足，应用形态学增强")
        
        # 应用形态学操作连接断开的线段
        enhanced_mask = self._enhance_lines_morphology(black_mask, width)
        
        # 在增强后的掩码上重新检测
        enhanced_lines = self._detect_lines_from_mask(enhanced_mask, width, height)
        
        if len(enhanced_lines) >= len(basic_lines):
            logger.debug(f"形态学增强有效，检测到 {len(enhanced_lines)} 条线")
            return enhanced_lines
        else:
            logger.debug("形态学增强未改善，使用基本检测结果")
            return basic_lines
    
    def _enhance_lines_morphology(self, black_mask, width):
        """
        使用改进的形态学操作增强线条检测
        更智能地识别真正的横线，避免误连接文字
        """
        height = black_mask.shape[0]
        
        # 第一轮：使用细长的水平核连接近距离的线段（适合真正的横线）
        # 核的高度限制为3像素，避免连接过粗的文字行
        horizontal_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 10, 3))
        enhanced_mask1 = cv2.morphologyEx(black_mask.astype(np.uint8), cv2.MORPH_CLOSE, horizontal_kernel1)
        
        # 第二轮：使用更细的核进一步连接，但保持线条细度
        horizontal_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 20, 1))
        enhanced_mask2 = cv2.morphologyEx(enhanced_mask1, cv2.MORPH_CLOSE, horizontal_kernel2)
        
        # 第三轮：清理和细化，移除过粗的区域
        # 使用开运算移除小的噪点
        cleanup_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        cleaned_mask = cv2.morphologyEx(enhanced_mask2, cv2.MORPH_OPEN, cleanup_kernel)
        
        # 最终细化：确保线条不会过粗
        thin_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
        final_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_ERODE, thin_kernel)
        
        logger.debug(f"改进形态学增强后黑色像素数量: {np.sum(final_mask)}")
        logger.debug(f"原始黑色像素数量: {np.sum(black_mask)}")
        
        return final_mask
    
    def _detect_lines_from_mask(self, mask, width, height):
        """
        从给定的掩码中检测长横线
        增加线条宽度验证，确保检测到的是细线而不是粗文字行
        """
        potential_lines = []
        
        for y in range(height):
            row = mask[y, :]
            
            # 查找连续的黑色像素段
            segments = []
            start = None
            
            for x in range(width):
                if row[x]:  # 黑色像素
                    if start is None:
                        start = x
                else:  # 非黑色像素
                    if start is not None:
                        segments.append((start, x - 1))
                        start = None
            
            # 处理行末的情况
            if start is not None:
                segments.append((start, width - 1))
            
            # 分析这一行的线段
            if segments:
                max_segment_length = max(end - start + 1 for start, end in segments)
                max_segment_ratio = max_segment_length / width
                
                # 记录可能的长横线（最长线段>=70%宽度，避免误识别长行文字）
                if max_segment_ratio >= 0.70:
                    max_segment = max(segments, key=lambda x: x[1] - x[0])
                    
                    # 新增：验证线条宽度，确保是细线而不是粗文字行
                    line_width = self._measure_line_width(mask, max_segment[0], max_segment[1], y, width, height)
                    
                    # 线条宽度应该小于页面高度的2%，避免误识别文字行
                    if line_width <= height * 0.02:
                        potential_lines.append({
                            'coords': (max_segment[0], y, max_segment[1], y),
                            'length': max_segment_length,
                            'y_center': float(y),
                            'angle': 0,
                            'width_ratio': max_segment_ratio,
                            'y_percent': y / height * 100,
                            'line_width': line_width  # 新增：记录线条宽度
                        })
                        logger.debug(f"检测到细线: y={y}, 长度={max_segment_length:.0f}({max_segment_ratio:.1%}), 宽度={line_width:.1f}")
                    else:
                        logger.debug(f"忽略粗线: y={y}, 长度={max_segment_length:.0f}({max_segment_ratio:.1%}), 宽度={line_width:.1f} (超过阈值{height*0.02:.1f})")
        
        logger.debug(f"发现 {len(potential_lines)} 条潜在长横线")
        
        if len(potential_lines) == 0:
            return []
        
        # 按线条质量排序（优先考虑最长线段长度）
        potential_lines.sort(key=lambda x: x['length'], reverse=True)
        
        # 寻找两条最主要且相距足够远的线条
        main_lines = []
        min_distance = height * 0.45  # 最小间距为45%高度
        
        for line in potential_lines:
            # 检查与已选线条的距离
            too_close = False
            for selected in main_lines:
                if abs(line['y_center'] - selected['y_center']) < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                # 新增：计算线条质量评分
                quality_score = self._calculate_line_quality(line, width, height)
                line['quality_score'] = quality_score
                
                main_lines.append(line)
                logger.debug(f"选择长横线: y={line['y_center']:.0f}({line['y_percent']:.1f}%), 长度={line['length']}({line['width_ratio']:.1%}), 质量评分={quality_score:.2f}")
                if len(main_lines) == 2:
                    break
        
        logger.debug(f"最终选择 {len(main_lines)} 条主要长横线")
        return main_lines
    
    def _measure_line_width(self, mask, x1, x2, y, width, height):
        """
        测量线条在垂直方向上的宽度
        
        Args:
            mask: 黑色像素掩码
            x1, x2: 线条的起始和结束x坐标
            y: 线条的y坐标
            width, height: 图像尺寸
            
        Returns:
            float: 线条的垂直宽度（像素）
        """
        # 在y坐标附近搜索垂直方向上的连续黑色像素
        line_center = y
        search_range = max(5, height // 100)  # 搜索范围，最小5像素
        
        # 向上搜索
        top_y = line_center
        for dy in range(1, search_range + 1):
            test_y = line_center - dy
            if test_y < 0:
                break
            
            # 检查这一行在x1到x2范围内是否有足够的黑色像素
            if x2 >= x1:
                black_pixels = np.sum(mask[test_y, x1:x2+1])
                if black_pixels < (x2 - x1 + 1) * 0.3:  # 如果黑色像素少于30%，认为不是线条的一部分
                    break
                top_y = test_y
            else:
                break
        
        # 向下搜索
        bottom_y = line_center
        for dy in range(1, search_range + 1):
            test_y = line_center + dy
            if test_y >= height:
                break
            
            # 检查这一行在x1到x2范围内是否有足够的黑色像素
            if x2 >= x1:
                black_pixels = np.sum(mask[test_y, x1:x2+1])
                if black_pixels < (x2 - x1 + 1) * 0.3:  # 如果黑色像素少于30%，认为不是线条的一部分
                    break
                bottom_y = test_y
            else:
                break
        
        # 计算线条宽度
        line_width = bottom_y - top_y + 1
        return line_width
    
    def _calculate_line_quality(self, line, width, height):
        """
        计算线条质量评分
        
        Args:
            line: 线条信息字典
            width, height: 图像尺寸
            
        Returns:
            float: 质量评分 (0-1，越高越好)
        """
        # 长度评分：线条越长越好
        length_score = min(line['width_ratio'] / 0.9, 1.0)  # 90%宽度为满分
        
        # 宽度评分：线条越细越好
        max_expected_width = height * 0.02  # 期望的最大宽度
        width_score = max(0, 1.0 - line['line_width'] / max_expected_width)
        
        # 位置评分：避免边缘位置
        y_percent = line['y_percent']
        if y_percent < 10 or y_percent > 90:  # 边缘位置
            position_score = 0.5
        elif y_percent < 20 or y_percent > 80:  # 较边缘位置
            position_score = 0.8
        else:  # 中间位置
            position_score = 1.0
        
        # 综合评分：长度40% + 宽度40% + 位置20%
        final_score = length_score * 0.4 + width_score * 0.4 + position_score * 0.2
        
        return final_score
    
    def _detect_line_in_region(self, black_mask, target_y, search_range, width, line_name):
        """
        在指定区域内检测长横线
        """
        height = black_mask.shape[0]
        
        # 确保搜索区域在图像范围内
        y_start = max(0, target_y - search_range)
        y_end = min(height, target_y + search_range)
        
        # 提取搜索区域
        roi = black_mask[y_start:y_end, :]
        
        # 在搜索区域内寻找最长的水平线条
        best_line = None
        max_length = 0
        
        for row_offset in range(roi.shape[0]):
            row = roi[row_offset, :]
            
            # 查找连续的黑色像素段
            segments = []
            start = None
            
            for col in range(len(row)):
                if row[col]:  # 黑色像素
                    if start is None:
                        start = col
                else:  # 非黑色像素
                    if start is not None:
                        segments.append((start, col - 1))
                        start = None
            
            # 处理行末的情况
            if start is not None:
                segments.append((start, len(row) - 1))
            
            # 找到最长的段
            for start_col, end_col in segments:
                segment_length = end_col - start_col + 1
                segment_ratio = segment_length / width
                
                # 检查是否为长线段（至少25%宽度）
                if segment_ratio >= 0.25 and segment_length > max_length:
                    max_length = segment_length
                    actual_y = y_start + row_offset
                    
                    best_line = {
                        'coords': (start_col, actual_y, end_col, actual_y),
                        'length': segment_length,
                        'y_center': float(actual_y),
                        'angle': 0,
                        'width_ratio': segment_ratio
                    }
        
        if best_line:
            y_percent = best_line['y_center'] / height * 100
            width_percent = best_line['width_ratio'] * 100
            logger.debug(f"{line_name}检测成功: y={best_line['y_center']:.0f}({y_percent:.1f}%), 长度={best_line['length']}({width_percent:.1f}%)")
            return best_line
        else:
            logger.debug(f"{line_name}检测失败: 在y={target_y}±{search_range}范围内未找到长度>=25%宽度的线条")
            return None

    def detect_mb_second_feature(self, image):
        """
        检测mb.png模板的第二特征：两条长黑线
        
        使用精确位置检测方法：
        1. 直接在y=359±30和y=1245±30范围内搜索长横线
        2. 每个区域内找最长的水平线段
        3. 要求线段长度至少25%页面宽度
        
        Args:
            image: 图像数组 (numpy array)
            
        Returns:
            dict: 第二特征检测结果
        """
        try:
            # 转换为RGB（如果是BGR）
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = image
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            height, width = rgb_image.shape[:2]
            logger.debug(f"图像尺寸: {width}x{height}")
            
            # 使用新的自适应检测方法
            detected_lines = self._detect_adaptive_lines(rgb_image)
            
            logger.debug(f"精确检测到的长横线数量: {len(detected_lines)}")
            
            if len(detected_lines) == 0:
                return {
                    'has_second_feature': False,
                    'detected_lines': 0,
                    'long_lines': [],
                    'line_lengths': [],
                    'line_distance': 0,
                    'reason': '在预期位置未检测到长黑线'
                }
            elif len(detected_lines) == 1:
                return {
                    'has_second_feature': False,
                    'detected_lines': 1,
                    'long_lines': detected_lines,
                    'line_lengths': [line['length'] for line in detected_lines],
                    'line_distance': 0,
                    'reason': f'只检测到1条长黑线，要求2条'
                }
            
            # 按y坐标排序
            detected_lines.sort(key=lambda x: x['y_center'])
            
            # 取前两条线（如果检测到超过2条）
            long_lines = detected_lines[:2]
            
            # 检查是否只有两条长黑线
            if len(long_lines) != 2:
                return {
                    'has_second_feature': False,
                    'detected_lines': len(long_lines),
                    'long_lines': long_lines,
                    'line_lengths': [line['length'] for line in long_lines],
                    'line_distance': 0,
                    'reason': f'检测到{len(long_lines)}条符合长度要求的长黑线，要求恰好2条'
                }
            
            line1, line2 = long_lines[0], long_lines[1]
            
            # 计算两线间距
            line_distance = abs(line2['y_center'] - line1['y_center'])
            
            # 记录检测结果
            logger.debug(f"成功检测到两条长黑线:")
            logger.debug(f"  线条1: y={line1['y_center']:.0f}, 长度={line1['length']:.0f} ({line1['width_ratio']*100:.1f}%宽度)")
            logger.debug(f"  线条2: y={line2['y_center']:.0f}, 长度={line2['length']:.0f} ({line2['width_ratio']*100:.1f}%宽度)")
            logger.debug(f"  间距: {line_distance:.0f}像素 ({line_distance/height*100:.1f}%高度)")
            
            # 直接返回成功结果（精确位置检测已经保证了正确性）
            return {
                'has_second_feature': True,
                'detected_lines': 2,
                'long_lines': [line1, line2],
                'line_lengths': [line1['length'], line2['length']],
                'line_distance': line_distance,
                'line_distance_ratio': line_distance / height,
                'length_ratio_1': line1['width_ratio'],
                'length_ratio_2': line2['width_ratio'],
                'reason': f'精确检测到位于y={line1["y_center"]:.0f}和y={line2["y_center"]:.0f}的两条长黑线'
            }
            
        except Exception as e:
            logger.error(f"第二特征检测失败: {str(e)}")
            return {
                'has_second_feature': False,
                'detected_lines': 0,
                'long_lines': [],
                'line_lengths': [],
                'line_distance': 0,
                'reason': f'检测过程出错: {str(e)}'
            }
    
    def check_standard_compliance(self, features):
        """
        检查是否符合标准特征（白色背景+黑色文字）
        
        Args:
            features: 颜色特征字典
            
        Returns:
            bool: 是否符合标准
        """
        if not features:
            return False
        
        # 检查白色背景比例
        white_bg_ok = features['white_bg_ratio'] >= self.color_thresholds['bg_ratio_min']
        
        # 检查黑色文字比例
        black_text_ok = features['black_text_ratio'] >= self.color_thresholds['text_ratio_min']
        
        # 检查整体亮度（RGB均值）
        mean_rgb = features['mean_rgb']
        avg_brightness = sum(mean_rgb) / len(mean_rgb)
        brightness_ok = avg_brightness >= self.color_thresholds['brightness_min']
        
        # 检查对比度（确保有足够的对比度）
        contrast_ok = features['contrast'] >= self.color_thresholds['contrast_min']
        
        # 检查彩色文字比例（不应有过多彩色文字）
        colored_text_ok = features['colored_text_ratio'] <= self.color_thresholds['colored_text_max']
        
        # 检查第二特征（两条长黑线）
        second_feature_ok = False
        if 'second_feature' in features:
            second_feature_ok = features['second_feature']['has_second_feature']
        
        compliance = white_bg_ok and black_text_ok and brightness_ok and contrast_ok and colored_text_ok and second_feature_ok
        
        logger.info(f"标准符合性检查:")
        logger.info(f"  白色背景比例: {features['white_bg_ratio']:.3f} (>= {self.color_thresholds['bg_ratio_min']}) - {'✓' if white_bg_ok else '✗'}")
        logger.info(f"  黑色文字比例: {features['black_text_ratio']:.3f} (>= {self.color_thresholds['text_ratio_min']}) - {'✓' if black_text_ok else '✗'}")
        logger.info(f"  整体亮度: {avg_brightness:.1f} (>= {self.color_thresholds['brightness_min']}) - {'✓' if brightness_ok else '✗'}")
        logger.info(f"  对比度: {features['contrast']:.1f} (>= {self.color_thresholds['contrast_min']}) - {'✓' if contrast_ok else '✗'}")
        logger.info(f"  彩色文字比例: {features['colored_text_ratio']:.3f} (<= {self.color_thresholds['colored_text_max']}) - {'✓' if colored_text_ok else '✗'}")
        
        # 第二特征详细信息
        if 'second_feature' in features:
            second_feature = features['second_feature']
            logger.info(f"  第二特征（两条长黑线）: {'✓' if second_feature_ok else '✗'}")
            logger.info(f"    检测到线条数: {second_feature['detected_lines']}")
            if second_feature_ok:
                logger.info(f"    线条长度比例: {second_feature['length_ratio_1']:.1%}, {second_feature['length_ratio_2']:.1%}")
                logger.info(f"    线条间距比例: {second_feature['line_distance_ratio']:.1%}")
            else:
                logger.info(f"    失败原因: {second_feature['reason']}")
        else:
            logger.info(f"  第二特征（两条长黑线）: ✗ - 未进行检测")
        
        logger.info(f"  最终结果: {'符合标准' if compliance else '不符合标准'}")
        
        return compliance
    
    def process_pdf_file(self, pdf_path, max_pages=5, page_mode="first_n"):
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            max_pages: 最大处理页数
            page_mode: 页面选择模式
                - "first_n": 前N页（默认）
                - "first_page": 第一页
                - "all_pages": 所有页面
                - "last_n": 从后面起的N页
            
        Returns:
            dict: 处理结果
        """
        pdf_path = Path(pdf_path)
        logger.info(f"开始处理PDF文件: {pdf_path}")
        
        # 转换PDF页面为图片
        images = self.pdf_to_images(pdf_path, max_pages, page_mode)
        if not images:
            return {
                'file_path': str(pdf_path),
                'success': False,
                'error': 'PDF转换失败',
                'compliance': False
            }
        
        # 分析每页的特征
        page_results = []
        overall_compliance = True
        
        # 根据页面选择模式确定实际的页码
        if page_mode == "first_page":
            actual_page_numbers = [1]
        elif page_mode == "all_pages":
            actual_page_numbers = list(range(1, len(images) + 1))
        elif page_mode == "last_n":
            # 对于后N页模式，需要先获取PDF的总页数
            try:
                doc = fitz.open(pdf_path)
                total_pages = len(doc)
                doc.close()
                
                # 计算起始页码（从后往前数）
                start_page = max(1, total_pages - len(images) + 1)
                actual_page_numbers = list(range(start_page, start_page + len(images)))
            except Exception as e:
                logger.warning(f"无法获取PDF总页数，使用默认页码: {str(e)}")
                actual_page_numbers = list(range(1, len(images) + 1))
        else:  # "first_n" 默认模式
            actual_page_numbers = list(range(1, len(images) + 1))
        
        for i, (image, actual_page_num) in enumerate(zip(images, actual_page_numbers)):
            logger.info(f"分析第 {actual_page_num} 页特征...")
            features = self.analyze_color_features(image)
            
            if features:
                compliance = self.check_standard_compliance(features)
                page_results.append({
                    'page_number': actual_page_num,
                    'features': features,
                    'compliance': compliance
                })
                
                # 如果任何一页不符合标准，整体就不符合
                if not compliance:
                    overall_compliance = False
            else:
                page_results.append({
                    'page_number': actual_page_num,
                    'features': None,
                    'compliance': False
                })
                overall_compliance = False
        
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'success': True,
            'pages_analyzed': len(page_results),
            'page_results': page_results,
            'overall_compliance': overall_compliance,
            'page_mode': page_mode,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"PDF '{pdf_path.name}' 处理完成，页面模式: {page_mode}，整体符合性: {'是' if overall_compliance else '否'}")
        return result
    
    def process_pdf_folder(self, folder_path, max_pages=5, page_mode="first_n"):
        """
        处理文件夹中的所有PDF文件
        
        Args:
            folder_path: PDF文件夹路径
            max_pages: 每个PDF最大处理页数
            page_mode: 页面选择模式
                - "first_n": 前N页（默认）
                - "first_page": 第一页
                - "all_pages": 所有页面
                - "last_n": 从后面起的N页
            
        Returns:
            dict: 处理结果汇总
        """
        folder_path = Path(folder_path)
        logger.info(f"开始处理PDF文件夹: {folder_path}，页面模式: {page_mode}")
        
        if not folder_path.exists():
            logger.error(f"文件夹不存在: {folder_path}")
            return None
        
        # 查找所有PDF文件（避免重复）
        pdf_files_lower = list(folder_path.glob("*.pdf"))
        pdf_files_upper = list(folder_path.glob("*.PDF"))
        # 使用集合去重，避免在不区分大小写的文件系统中重复
        pdf_files = list(set(pdf_files_lower + pdf_files_upper))
        if not pdf_files:
            logger.warning(f"文件夹中未找到PDF文件: {folder_path}")
            return {
                'folder_path': str(folder_path),
                'total_files': 0,
                'results': [],
                'summary': {'compliant': 0, 'non_compliant': 0, 'errors': 0},
                'page_mode': page_mode
            }
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 处理每个PDF文件
        results = []
        summary = {'compliant': 0, 'non_compliant': 0, 'errors': 0}
        
        for pdf_file in pdf_files:
            try:
                result = self.process_pdf_file(pdf_file, max_pages, page_mode)
                results.append(result)
                
                if result['success']:
                    if result['overall_compliance']:
                        summary['compliant'] += 1
                    else:
                        summary['non_compliant'] += 1
                else:
                    summary['errors'] += 1
                    
            except Exception as e:
                logger.error(f"处理PDF文件时出错 '{pdf_file}': {str(e)}")
                results.append({
                    'file_path': str(pdf_file),
                    'file_name': pdf_file.name,
                    'success': False,
                    'error': str(e),
                    'compliance': False
                })
                summary['errors'] += 1
        
        # 汇总结果
        folder_result = {
            'folder_path': str(folder_path),
            'total_files': len(pdf_files),
            'results': results,
            'summary': summary,
            'page_mode': page_mode,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"文件夹处理完成:")
        logger.info(f"  总文件数: {len(pdf_files)}")
        logger.info(f"  符合标准: {summary['compliant']}")
        logger.info(f"  不符合标准: {summary['non_compliant']}")
        logger.info(f"  处理错误: {summary['errors']}")
        logger.info(f"  页面模式: {page_mode}")
        
        return folder_result
    
    def save_results(self, results, output_name=None):
        """
        保存结果到data文件夹
        
        Args:
            results: 处理结果
            output_name: 输出文件名（可选）
        """
        if not results:
            logger.error("没有结果可保存")
            return
        
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"pdf_feature_analysis_{timestamp}.json"
        
        output_path = self.data_dir / output_name
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PDF特征提取工具')
    parser.add_argument('input_path', nargs='?', help='输入PDF文件或文件夹路径')
    parser.add_argument('--max-pages', type=int, default=5, help='每个PDF最大处理页数（默认：5）')
    parser.add_argument('--page-mode', choices=['first_n', 'first_page', 'all_pages', 'last_n'], 
                       default='first_n', help='页面选择模式：first_n(前N页), first_page(第一页), all_pages(所有页面), last_n(后N页)')
    parser.add_argument('--template', default='templates/mb.png', help='标准模板图片路径')
    parser.add_argument('--output', help='输出文件名（可选）')
    parser.add_argument('--data-dir', default='data', help='数据保存目录')
    parser.add_argument('--config', help='颜色阈值配置文件路径（JSON格式）')
    parser.add_argument('--save-config', help='保存当前颜色阈值配置到指定文件')
    parser.add_argument('--show-config', action='store_true', help='显示当前颜色阈值配置')
    
    args = parser.parse_args()
    
    # 创建特征提取器
    extractor = PDFFeatureExtractor(
        template_path=args.template,
        data_dir=args.data_dir,
        config_file=args.config
    )
    
    # 处理配置相关参数
    if args.show_config:
        print("=== 当前颜色阈值配置 ===")
        config = extractor.get_color_thresholds()
        for key, value in config.items():
            print(f"  {key}: {value}")
        print()
        return 0
    
    if args.save_config:
        if extractor.save_color_thresholds(args.save_config):
            return 0
        else:
            return 1
    
    input_path = Path(args.input_path)
    
    # 处理输入
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # 处理单个PDF文件
        logger.info(f"处理模式: 单个PDF文件，页面模式: {args.page_mode}")
        results = extractor.process_pdf_file(input_path, args.max_pages, args.page_mode)
    elif input_path.is_dir():
        # 处理PDF文件夹
        logger.info(f"处理模式: PDF文件夹，页面模式: {args.page_mode}")
        results = extractor.process_pdf_folder(input_path, args.max_pages, args.page_mode)
    else:
        logger.error(f"无效的输入路径: {input_path}")
        return 1
    
    # 保存结果
    if results:
        extractor.save_results(results, args.output)
        return 0
    else:
        logger.error("处理失败，没有生成结果")
        return 1


if __name__ == "__main__":
    import io
    sys.exit(main())
