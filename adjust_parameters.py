#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据标准文件检测结果调整参数
"""

from pdf_processor import PDFProcessor
from pathlib import Path
import json

def analyze_test_results():
    """分析测试结果并调整参数"""
    print("PDF标准文档参数调整工具")
    print("=" * 50)
    
    # 创建处理器
    processor = PDFProcessor()
    
    # 获取PDF文件列表
    pdf_files = processor.get_pdf_files()
    
    if not pdf_files:
        print("未找到PDF文件，请检查路径设置")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 测试前10个文件
    test_files = pdf_files[:10]
    
    results = []
    
    for i, pdf_path in enumerate(test_files, 1):
        print(f"\n测试文件 {i}/{len(test_files)}: {pdf_path.name}")
        
        result = processor.process_pdf(pdf_path)
        results.append({
            'file': pdf_path.name,
            'success': result['success'],
            'copied': result['copied'],
            'features': result.get('features', 0),
            'confidence': result.get('confidence', 0.0),
            'template_similarity': result.get('template_similarity', 0.0)
        })
    
    # 分析结果
    total_files = len(results)
    copied_files = sum(1 for r in results if r['copied'])
    success_rate = copied_files / total_files * 100
    
    print(f"\n{'='*60}")
    print("分析结果")
    print(f"{'='*60}")
    print(f"总文件数: {total_files}")
    print(f"成功识别: {copied_files}")
    print(f"识别率: {success_rate:.1f}%")
    
    # 收集统计数据
    feature_counts = [r['features'] for r in results]
    confidences = [r['confidence'] for r in results if r['confidence'] > 0]
    template_similarities = [r['template_similarity'] for r in results if r['template_similarity'] > 0]
    
    print(f"\n特征数统计:")
    print(f"  平均特征数: {sum(feature_counts)/len(feature_counts):.1f}")
    print(f"  最小特征数: {min(feature_counts)}")
    print(f"  最大特征数: {max(feature_counts)}")
    
    if confidences:
        print(f"\n置信度统计:")
        print(f"  平均置信度: {sum(confidences)/len(confidences):.2f}")
        print(f"  最小置信度: {min(confidences):.2f}")
        print(f"  最大置信度: {max(confidences):.2f}")
    
    if template_similarities:
        print(f"\n模板相似度统计:")
        print(f"  平均相似度: {sum(template_similarities)/len(template_similarities):.3f}")
        print(f"  最小相似度: {min(template_similarities):.3f}")
        print(f"  最大相似度: {max(template_similarities):.3f}")
    
    # 建议参数调整
    print(f"\n{'='*60}")
    print("参数调整建议")
    print(f"{'='*60}")
    
    if success_rate < 80:
        print("⚠️  识别率较低，建议调整以下参数:")
        
        # 基于特征数统计调整
        avg_features = sum(feature_counts)/len(feature_counts)
        if avg_features < 5:
            suggested_min_features = max(3, int(avg_features - 1))
            print(f"  1. 降低最小特征数要求: 5 → {suggested_min_features}")
        
        # 基于置信度统计调整
        if confidences:
            avg_confidence = sum(confidences)/len(confidences)
            if avg_confidence < 0.7:
                suggested_confidence = max(0.5, avg_confidence - 0.1)
                print(f"  2. 降低位置符合度阈值: 0.7 → {suggested_confidence:.2f}")
        
        # 基于模板相似度统计调整
        if template_similarities:
            avg_similarity = sum(template_similarities)/len(template_similarities)
            if avg_similarity < 0.3:
                suggested_similarity = max(0.1, avg_similarity - 0.1)
                print(f"  3. 降低模板相似度阈值: 0.3 → {suggested_similarity:.2f}")
        
        # 生成调整后的配置
        generate_adjusted_config(results)
    else:
        print("✅ 识别率良好，当前参数设置合适")

def generate_adjusted_config(results):
    """生成调整后的配置"""
    print(f"\n生成调整后的配置...")
    
    # 分析数据
    feature_counts = [r['features'] for r in results]
    confidences = [r['confidence'] for r in results if r['confidence'] > 0]
    template_similarities = [r['template_similarity'] for r in results if r['template_similarity'] > 0]
    
    # 计算建议参数
    avg_features = sum(feature_counts)/len(feature_counts)
    suggested_min_features = max(3, int(avg_features - 1))
    
    suggested_confidence = 0.7
    if confidences:
        avg_confidence = sum(confidences)/len(confidences)
        suggested_confidence = max(0.5, avg_confidence - 0.1)
    
    suggested_similarity = 0.3
    if template_similarities:
        avg_similarity = sum(template_similarities)/len(template_similarities)
        suggested_similarity = max(0.1, avg_similarity - 0.1)
    
    # 生成新的配置
    adjusted_config = {
        "min_features": suggested_min_features,
        "position_confidence_threshold": suggested_confidence,
        "template_similarity_threshold": suggested_similarity
    }
    
    # 保存配置
    with open("adjusted_config.json", "w", encoding="utf-8") as f:
        json.dump(adjusted_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 调整后的配置已保存到 adjusted_config.json")
    print(f"  建议最小特征数: {suggested_min_features}")
    print(f"  建议位置符合度阈值: {suggested_confidence:.2f}")
    print(f"  建议模板相似度阈值: {suggested_similarity:.3f}")

if __name__ == "__main__":
    analyze_test_results() 