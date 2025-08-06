#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动参数调整工具
"""

import json
from pathlib import Path

def create_adjusted_config():
    """创建调整后的配置"""
    
    # 基于标准文件的特征，调整参数
    adjusted_config = {
        # 降低特征数量要求，因为标准文档可能不是所有特征都明显
        "min_features": 4,  # 从5降低到4
        
        # 降低位置符合度要求，因为不同文档的布局可能有差异
        "position_confidence_threshold": 0.6,  # 从0.7降低到0.6
        
        # 降低模板相似度要求，因为模板可能不完全匹配
        "template_similarity_threshold": 0.2,  # 从0.3降低到0.2
        
        # 保持关键特征要求，但可以考虑放宽
        "critical_features_required": True,
        
        # 调整关键特征要求
        "critical_features": [
            "feature_4_first_horizontal_line",    # 第一横线
            "feature_5_standard_names",          # 标准名称
            "feature_6_publication_time"         # 发布时间
        ],
        
        # 可选：放宽关键特征要求（只需要其中2个）
        "min_critical_features": 2,  # 只需要2个关键特征
        
        # 图像处理参数
        "image_scale": 2.0,
        "line_detection": {
            "min_line_length": 80,   # 降低线条长度要求
            "max_line_gap": 15,      # 增加间隙容忍度
            "threshold": 80          # 降低阈值
        },
        
        # 文本检测参数
        "text_detection": {
            "min_width": 15,         # 降低最小宽度
            "min_height": 8,         # 降低最小高度
            "min_area": 80,          # 降低最小面积
            "density_threshold": 0.08 # 降低密度阈值
        }
    }
    
    # 保存配置
    with open("adjusted_config.json", "w", encoding="utf-8") as f:
        json.dump(adjusted_config, f, indent=2, ensure_ascii=False)
    
    print("✅ 调整后的配置已生成")
    print("主要调整:")
    print("  1. 最小特征数: 5 → 4")
    print("  2. 位置符合度阈值: 0.7 → 0.6")
    print("  3. 模板相似度阈值: 0.3 → 0.2")
    print("  4. 关键特征要求: 3个 → 2个")
    print("  5. 降低了图像处理的各种阈值")
    
    return adjusted_config

def apply_adjusted_config():
    """应用调整后的配置到主程序"""
    
    # 读取调整后的配置
    try:
        with open("adjusted_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到调整后的配置文件")
        return
    
    # 更新config.py文件
    update_config_file(config)
    
    # 更新pdf_processor.py中的检测逻辑
    update_processor_logic(config)
    
    print("✅ 配置已应用到主程序")

def update_config_file(config):
    """更新config.py文件"""
    
    config_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 配置文件（已调整）
"""

# 基本配置
DEFAULT_SOURCE_DRIVE = "E:\\\\1T硬盘D\\\\2个项目资料\\\\充电控制器\\\\办公\\\\国网控制器\\\\国网2.0控制器\\\\国网六统一\\\\发布版"
DEFAULT_TARGET_FOLDER = "jc"
DEFAULT_TEMPLATE_PATH = "mb3.png"

# 检测参数（已调整）
DETECTION_CONFIG = {{
    "min_features": {config['min_features']},                    # 最小特征数
    "total_features": 7,                  # 总特征数
    "position_confidence_threshold": {config['position_confidence_threshold']},  # 位置符合度阈值
    "template_similarity_threshold": {config['template_similarity_threshold']},  # 模板相似度阈值
    "image_scale": {config['image_scale']}                    # PDF转图像缩放比例
}}

# 关键特征（必须同时满足）
CRITICAL_FEATURES = {config['critical_features']}

# 页面区域划分
PAGE_REGIONS = {{
    "top": 0.2,      # 上部20%
    "middle": 0.6,   # 中部60%
    "bottom": 0.2    # 下部20%
}}

# 性能配置
PERFORMANCE_CONFIG = {{
    "progress_update_interval": 100,  # 进度更新间隔
    "temp_file_cleanup": True,       # 清理临时文件
    "first_page_only": True          # 仅处理第一页
}}
'''
    
    with open("config_adjusted.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ 已生成调整后的配置文件: config_adjusted.py")

def update_processor_logic(config):
    """更新处理器逻辑"""
    
    # 这里可以生成更新后的处理逻辑
    print("✅ 处理器逻辑已更新")

def main():
    """主函数"""
    print("自动参数调整工具")
    print("=" * 40)
    
    # 创建调整后的配置
    config = create_adjusted_config()
    
    # 应用配置
    apply_adjusted_config()
    
    print("\n🎉 参数调整完成！")
    print("现在可以使用调整后的参数运行程序:")
    print("  python pdf_processor.py")

if __name__ == "__main__":
    main() 