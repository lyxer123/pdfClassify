#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块 - 显示检测到的9个特征
"""

import cv2
import numpy as np
from main import StandardDocumentFeatureExtractor
import os

class FeatureVisualizer:
    """
    特征可视化器
    """
    
    def __init__(self, image_path: str):
        """
        初始化可视化器
        
        Args:
            image_path: 图片文件路径
        """
        self.image_path = image_path
        self.extractor = StandardDocumentFeatureExtractor(image_path)
        self.image = None
        
    def load_image(self):
        """
        加载图片
        """
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            print(f"无法加载图片: {self.image_path}")
            return False
        return True
    
    def draw_features(self, features: dict):
        """
        在图片上绘制检测到的特征
        
        Args:
            features: 检测到的特征字典
        """
        if self.image is None:
            if not self.load_image():
                return
        
        # 创建副本用于绘制
        display_image = self.image.copy()
        
        # 颜色定义
        colors = {
            'feature_1_standard_logo': (0, 255, 0),      # 绿色
            'feature_2_standard_category': (255, 0, 0),  # 蓝色
            'feature_3_standard_code': (0, 0, 255),  # 红色
            'feature_4_first_horizontal_line': (255, 255, 0),  # 青色
            'feature_5_standard_names': (255, 0, 255),  # 洋红色
            'feature_6_publication_time': (0, 255, 255),  # 黄色
            'feature_7_publishing_unit': (128, 0, 128)  # 紫色
        }
        
        feature_labels = {
            'feature_1_standard_logo': "1. 标准logo",
            'feature_2_standard_category': "2. 标准类别",
            'feature_3_standard_code': "3. 标准号",
            'feature_4_first_horizontal_line': "4. 第一横线",
            'feature_5_standard_names': "5. 标准的中文和英文名称",
            'feature_6_publication_time': "6. 发布和实施时间",
            'feature_7_publishing_unit': "7. 发布单位"
        }
        
        # 绘制每个检测到的特征
        for feature_key, feature_info in features.items():
            if feature_info['detected'] and feature_info['position'] is not None:
                position = feature_info['position']
                color = colors.get(feature_key, (255, 255, 255))
                label = feature_labels.get(feature_key, feature_key)
                
                if len(position) >= 4:
                    x, y, w, h = position[:4]
                    
                    # 绘制边界框
                    cv2.rectangle(display_image, (x, y), (x + w, y + h), color, 2)
                    
                    # 绘制标签
                    cv2.putText(display_image, label, (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return display_image
    
    def save_visualization(self, output_path: str = "detected_features.png"):
        """
        保存可视化结果
        
        Args:
            output_path: 输出文件路径
        """
        # 提取特征
        features_result = self.extractor.extract_features()
        
        if not features_result:
            print("特征提取失败")
            return
        
        # 绘制特征
        visualized_image = self.draw_features(features_result['features'])
        
        # 保存图片
        cv2.imwrite(output_path, visualized_image)
        print(f"可视化结果已保存到: {output_path}")
        
        # 打印检测统计
        print(f"\n检测统计:")
        print(f"总特征数: {features_result['total_features']}")
        print(f"检测到的特征数: {features_result['detected_features']}")
        print(f"检测率: {features_result['detection_rate']:.2%}")

def main():
    """
    主函数
    """
    print("特征可视化工具")
    print("=" * 50)
    
    # 检查图片文件是否存在
    image_path = "mb.png"
    if not os.path.exists(image_path):
        print(f"错误: 找不到图片文件 {image_path}")
        return
    
    # 创建可视化器
    visualizer = FeatureVisualizer(image_path)
    
    # 生成并保存可视化结果
    visualizer.save_visualization()

if __name__ == "__main__":
    main() 