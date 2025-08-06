#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 配置文件
"""

# 基本配置
DEFAULT_SOURCE_DRIVE = "E:"
DEFAULT_TARGET_FOLDER = "jc"
DEFAULT_TEMPLATE_PATH = "mb3.png"

# 检测参数（基于mb4.png的6个特征）
DETECTION_CONFIG = {
    "min_features": 5,                    # 最小特征数（6个特征中至少5个）
    "total_features": 6,                  # 总特征数
    "position_confidence_threshold": 0.6,  # 位置符合度阈值
    "template_similarity_threshold": 0.15, # 模板相似度阈值（优化后）
    "image_scale": 2.0                    # PDF转图像缩放比例
}

# 关键特征（必须同时满足）
CRITICAL_FEATURES = [
    "feature_3_standard_number_line",     # 标准号和横线
    "feature_4_standard_names",          # 标准名称
    "feature_5_publication_time"         # 发布时间
]

# 页面区域划分
PAGE_REGIONS = {
    "top": 0.2,      # 上部20%
    "middle": 0.6,   # 中部60%
    "bottom": 0.2    # 下部20%
}

# 性能配置
PERFORMANCE_CONFIG = {
    "progress_update_interval": 100,  # 进度更新间隔
    "temp_file_cleanup": True,       # 清理临时文件
    "first_page_only": True          # 仅处理第一页
} 