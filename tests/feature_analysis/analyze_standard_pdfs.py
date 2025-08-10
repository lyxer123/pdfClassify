#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析标准PDF特征分布，用于优化算法参数
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

from main import PDFFeatureExtractor

def load_analysis_results(file_path):
    """加载分析结果"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_features_statistics(data):
    """提取所有PDF第一页的特征统计"""
    features_list = []
    
    for result in data['results']:
        if result['success'] and result['page_results']:
            # 只分析第一页，因为都是标准页面
            first_page = result['page_results'][0]
            if first_page['features']:
                features = first_page['features']
                features_list.append({
                    'file_name': result['file_name'],
                    'white_bg_ratio': features['white_bg_ratio'],
                    'black_text_ratio': features['black_text_ratio'],
                    'contrast': features['contrast'],
                    'mean_rgb': features['mean_rgb'],
                    'brightness': np.mean(features['mean_rgb']),
                    'compliance': first_page.get('compliance', False)
                })
    
    return features_list

def analyze_feature_distributions(features_list):
    """分析特征分布"""
    print("=== 标准PDF特征分布分析 ===\n")
    
    # 提取各项特征
    white_ratios = [f['white_bg_ratio'] for f in features_list]
    black_ratios = [f['black_text_ratio'] for f in features_list]
    contrasts = [f['contrast'] for f in features_list]
    brightness_values = [f['brightness'] for f in features_list]
    
    print(f"总共分析了 {len(features_list)} 个标准PDF文件\n")
    
    # 白色背景比例统计
    print("📊 白色背景比例分析:")
    print(f"  最小值: {min(white_ratios):.3f} ({min(white_ratios)*100:.1f}%)")
    print(f"  最大值: {max(white_ratios):.3f} ({max(white_ratios)*100:.1f}%)")
    print(f"  平均值: {np.mean(white_ratios):.3f} ({np.mean(white_ratios)*100:.1f}%)")
    print(f"  中位数: {np.median(white_ratios):.3f} ({np.median(white_ratios)*100:.1f}%)")
    print(f"  标准差: {np.std(white_ratios):.3f}")
    print(f"  5%分位数: {np.percentile(white_ratios, 5):.3f} ({np.percentile(white_ratios, 5)*100:.1f}%)")
    print(f"  95%分位数: {np.percentile(white_ratios, 95):.3f} ({np.percentile(white_ratios, 95)*100:.1f}%)")
    
    # 黑色文字比例统计
    print(f"\n📊 黑色文字比例分析:")
    print(f"  最小值: {min(black_ratios):.3f} ({min(black_ratios)*100:.1f}%)")
    print(f"  最大值: {max(black_ratios):.3f} ({max(black_ratios)*100:.1f}%)")
    print(f"  平均值: {np.mean(black_ratios):.3f} ({np.mean(black_ratios)*100:.1f}%)")
    print(f"  中位数: {np.median(black_ratios):.3f} ({np.median(black_ratios)*100:.1f}%)")
    print(f"  标准差: {np.std(black_ratios):.3f}")
    print(f"  5%分位数: {np.percentile(black_ratios, 5):.3f} ({np.percentile(black_ratios, 5)*100:.1f}%)")
    print(f"  95%分位数: {np.percentile(black_ratios, 95):.3f} ({np.percentile(black_ratios, 95)*100:.1f}%)")
    
    # 对比度统计
    print(f"\n📊 图像对比度分析:")
    print(f"  最小值: {min(contrasts):.1f}")
    print(f"  最大值: {max(contrasts):.1f}")
    print(f"  平均值: {np.mean(contrasts):.1f}")
    print(f"  中位数: {np.median(contrasts):.1f}")
    print(f"  标准差: {np.std(contrasts):.1f}")
    print(f"  5%分位数: {np.percentile(contrasts, 5):.1f}")
    print(f"  95%分位数: {np.percentile(contrasts, 95):.1f}")
    
    # 亮度统计
    print(f"\n📊 整体亮度分析:")
    print(f"  最小值: {min(brightness_values):.1f}")
    print(f"  最大值: {max(brightness_values):.1f}")
    print(f"  平均值: {np.mean(brightness_values):.1f}")
    print(f"  中位数: {np.median(brightness_values):.1f}")
    print(f"  标准差: {np.std(brightness_values):.1f}")
    print(f"  5%分位数: {np.percentile(brightness_values, 5):.1f}")
    print(f"  95%分位数: {np.percentile(brightness_values, 95):.1f}")
    
    return {
        'white_ratios': white_ratios,
        'black_ratios': black_ratios,
        'contrasts': contrasts,
        'brightness_values': brightness_values
    }

def suggest_optimal_thresholds(stats):
    """基于统计数据建议最佳阈值"""
    print(f"\n🎯 基于标准PDF数据的参数建议:")
    
    # 白色背景比例：使用5%分位数作为最低要求
    white_bg_threshold = np.percentile(stats['white_ratios'], 5)
    print(f"  white_bg_ratio_min: {white_bg_threshold:.3f} (当前: 0.6)")
    
    # 黑色文字比例：使用5%分位数作为最低要求
    black_text_threshold = np.percentile(stats['black_ratios'], 5)
    print(f"  black_text_ratio_min: {black_text_threshold:.3f} (当前: 0.02)")
    
    # 对比度：使用5%分位数作为最低要求
    contrast_threshold = np.percentile(stats['contrasts'], 5)
    print(f"  contrast_min: {contrast_threshold:.1f} (当前: 30)")
    
    # 亮度：使用5%分位数作为最低要求
    brightness_threshold = np.percentile(stats['brightness_values'], 5)
    print(f"  brightness_min: {brightness_threshold:.1f} (当前: 180)")
    
    return {
        'bg_ratio_min': max(0.5, white_bg_threshold),  # 不低于50%
        'text_ratio_min': max(0.005, black_text_threshold),  # 不低于0.5%
        'contrast_min': max(15, contrast_threshold),  # 不低于15
        'brightness_min': max(150, brightness_threshold)  # 不低于150
    }

def analyze_current_compliance(features_list):
    """分析当前算法的符合率"""
    compliant_count = sum(1 for f in features_list if f['compliance'])
    total_count = len(features_list)
    compliance_rate = compliant_count / total_count * 100
    
    print(f"\n📈 当前算法性能:")
    print(f"  符合标准: {compliant_count}/{total_count} ({compliance_rate:.1f}%)")
    print(f"  不符合标准: {total_count - compliant_count}/{total_count} ({100-compliance_rate:.1f}%)")
    
    # 分析不符合标准的原因
    non_compliant = [f for f in features_list if not f['compliance']]
    if non_compliant:
        print(f"\n❌ 不符合标准的PDF特征分析:")
        
        # 检查各项指标的分布
        extractor = PDFFeatureExtractor()
        
        issues = {
            'white_bg_low': 0,
            'black_text_low': 0,
            'contrast_low': 0,
            'brightness_low': 0
        }
        
        for f in non_compliant:
            if f['white_bg_ratio'] < extractor.color_thresholds['bg_ratio_min']:
                issues['white_bg_low'] += 1
            if f['black_text_ratio'] < extractor.color_thresholds['text_ratio_min']:
                issues['black_text_low'] += 1
            if f['contrast'] < extractor.color_thresholds['contrast_min']:
                issues['contrast_low'] += 1
            if f['brightness'] < 180:
                issues['brightness_low'] += 1
        
        print(f"  白色背景比例不足: {issues['white_bg_low']} 个文件")
        print(f"  黑色文字比例不足: {issues['black_text_low']} 个文件")
        print(f"  对比度不足: {issues['contrast_low']} 个文件")
        print(f"  亮度不足: {issues['brightness_low']} 个文件")

def create_visualization(stats):
    """创建特征分布可视化图表"""
    # 配置matplotlib使用英文标签避免中文字体问题
    plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Standard PDF Feature Distribution Analysis', fontsize=16, fontweight='bold')
    
    # 白色背景比例分布
    axes[0, 0].hist(stats['white_ratios'], bins=30, alpha=0.7, color='lightblue', edgecolor='black')
    axes[0, 0].set_title('White Background Ratio Distribution', fontsize=12)
    axes[0, 0].set_xlabel('White Background Ratio', fontsize=10)
    axes[0, 0].set_ylabel('Number of Files', fontsize=10)
    axes[0, 0].axvline(np.median(stats['white_ratios']), color='red', linestyle='--', 
                       label=f'Median: {np.median(stats["white_ratios"]):.3f}')
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 黑色文字比例分布
    axes[0, 1].hist(stats['black_ratios'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 1].set_title('Black Text Ratio Distribution', fontsize=12)
    axes[0, 1].set_xlabel('Black Text Ratio', fontsize=10)
    axes[0, 1].set_ylabel('Number of Files', fontsize=10)
    axes[0, 1].axvline(np.median(stats['black_ratios']), color='red', linestyle='--', 
                       label=f'Median: {np.median(stats["black_ratios"]):.3f}')
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    
    # 对比度分布
    axes[1, 0].hist(stats['contrasts'], bins=30, alpha=0.7, color='lightcoral', edgecolor='black')
    axes[1, 0].set_title('Image Contrast Distribution', fontsize=12)
    axes[1, 0].set_xlabel('Contrast Value', fontsize=10)
    axes[1, 0].set_ylabel('Number of Files', fontsize=10)
    axes[1, 0].axvline(np.median(stats['contrasts']), color='red', linestyle='--', 
                       label=f'Median: {np.median(stats["contrasts"]):.1f}')
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3)
    
    # 亮度分布
    axes[1, 1].hist(stats['brightness_values'], bins=30, alpha=0.7, color='lightyellow', edgecolor='black')
    axes[1, 1].set_title('Overall Brightness Distribution', fontsize=12)
    axes[1, 1].set_xlabel('Brightness Value', fontsize=10)
    axes[1, 1].set_ylabel('Number of Files', fontsize=10)
    axes[1, 1].axvline(np.median(stats['brightness_values']), color='red', linestyle='--', 
                       label=f'Median: {np.median(stats["brightness_values"]):.1f}')
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3)
    
    # 添加统计信息
    stats_text = f"""Key Statistics (104 Standard PDFs):
• White BG: {np.mean(stats['white_ratios']):.1%} ± {np.std(stats['white_ratios']):.1%}
• Black Text: {np.mean(stats['black_ratios']):.1%} ± {np.std(stats['black_ratios']):.1%}
• Contrast: {np.mean(stats['contrasts']):.1f} ± {np.std(stats['contrasts']):.1f}
• Brightness: {np.mean(stats['brightness_values']):.1f} ± {np.std(stats['brightness_values']):.1f}"""
    
    fig.text(0.02, 0.02, stats_text, fontsize=9, family='monospace', 
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # 为统计信息留出空间
    # 确保tests/data目录存在
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(data_dir / 'standard_pdfs_feature_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 特征分布图表已保存到: {data_dir / 'standard_pdfs_feature_distribution.png'}")

def main():
    """主函数"""
    print("开始分析标准PDF特征分布...\n")
    
    # 加载分析结果
    data_dir = Path(__file__).parent.parent / "data"
    data = load_analysis_results(data_dir / 'standard_pdfs_analysis.json')
    print(f"✓ 成功加载分析结果")
    print(f"  文件夹: {data['folder_path']}")
    print(f"  总文件数: {data['total_files']}")
    print(f"  当前符合标准: {data['summary']['compliant']}")
    print(f"  当前不符合标准: {data['summary']['non_compliant']}")
    print(f"  处理错误: {data['summary']['errors']}")
    
    # 提取特征统计
    features_list = extract_features_statistics(data)
    print(f"✓ 成功提取 {len(features_list)} 个PDF的特征数据\n")
    
    # 分析特征分布
    stats = analyze_feature_distributions(features_list)
    
    # 分析当前符合率
    analyze_current_compliance(features_list)
    
    # 建议最佳阈值
    optimal_thresholds = suggest_optimal_thresholds(stats)
    
    # 创建可视化图表
    try:
        create_visualization(stats)
    except Exception as e:
        print(f"⚠️ 创建图表时出错: {e}")
    
    # 保存分析结果
    analysis_result = {
        'total_pdfs': len(features_list),
        'current_compliance_rate': sum(1 for f in features_list if f['compliance']) / len(features_list),
        'feature_statistics': {
            'white_bg_ratio': {
                'min': float(min(stats['white_ratios'])),
                'max': float(max(stats['white_ratios'])),
                'mean': float(np.mean(stats['white_ratios'])),
                'median': float(np.median(stats['white_ratios'])),
                'std': float(np.std(stats['white_ratios'])),
                'percentile_5': float(np.percentile(stats['white_ratios'], 5)),
                'percentile_95': float(np.percentile(stats['white_ratios'], 95))
            },
            'black_text_ratio': {
                'min': float(min(stats['black_ratios'])),
                'max': float(max(stats['black_ratios'])),
                'mean': float(np.mean(stats['black_ratios'])),
                'median': float(np.median(stats['black_ratios'])),
                'std': float(np.std(stats['black_ratios'])),
                'percentile_5': float(np.percentile(stats['black_ratios'], 5)),
                'percentile_95': float(np.percentile(stats['black_ratios'], 95))
            },
            'contrast': {
                'min': float(min(stats['contrasts'])),
                'max': float(max(stats['contrasts'])),
                'mean': float(np.mean(stats['contrasts'])),
                'median': float(np.median(stats['contrasts'])),
                'std': float(np.std(stats['contrasts'])),
                'percentile_5': float(np.percentile(stats['contrasts'], 5)),
                'percentile_95': float(np.percentile(stats['contrasts'], 95))
            },
            'brightness': {
                'min': float(min(stats['brightness_values'])),
                'max': float(max(stats['brightness_values'])),
                'mean': float(np.mean(stats['brightness_values'])),
                'median': float(np.median(stats['brightness_values'])),
                'std': float(np.std(stats['brightness_values'])),
                'percentile_5': float(np.percentile(stats['brightness_values'], 5)),
                'percentile_95': float(np.percentile(stats['brightness_values'], 95))
            }
        },
        'suggested_thresholds': optimal_thresholds,
        'timestamp': data['timestamp']
    }
    
    with open(data_dir / 'standard_pdfs_feature_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细分析结果已保存到: {data_dir / 'standard_pdfs_feature_analysis.json'}")
    
    return optimal_thresholds

if __name__ == "__main__":
    optimal_thresholds = main()
