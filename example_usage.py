# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统使用示例
演示基本的使用方法和API调用
"""

import os
from pdf_processor import PDFProcessor

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 1. 初始化PDF处理器
    processor = PDFProcessor(template_path="mb6.png")
    print("✓ PDF处理器初始化完成")
    
    # 2. 检查模板特征
    if os.path.exists("mb6.png"):
        import cv2
        template_image = cv2.imread("mb6.png")
        features = processor._extract_features(template_image)
        is_valid = processor._validate_features(features)
        print(f"✓ 模板特征验证: {'通过' if is_valid else '失败'}")
    
    # 3. 批量处理示例（如果有PDF文件）
    test_dir = "."  # 当前目录
    output_dir = "jc"
    
    results = processor.batch_process(test_dir, output_dir)
    print(f"✓ 批量处理完成:")
    print(f"  - 总文件数: {results['total_files']}")
    print(f"  - 成功匹配: {results['successful_files']}")
    print(f"  - 匹配失败: {results['failed_files']}")

def example_single_pdf():
    """单个PDF处理示例"""
    print("\n=== 单个PDF处理示例 ===")
    
    # 查找第一个PDF文件
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("未找到PDF文件，跳过单个PDF处理示例")
        return
    
    pdf_path = pdf_files[0]
    print(f"处理文件: {pdf_path}")
    
    processor = PDFProcessor()
    result = processor.process_pdf(pdf_path)
    
    print(f"处理结果: {'成功' if result['success'] else '失败'}")
    print(f"处理时间: {result['processing_time']:.2f} 秒")
    print(f"结果说明: {result['reason']}")

def example_feature_extraction():
    """特征提取示例"""
    print("\n=== 特征提取示例 ===")
    
    if not os.path.exists("mb6.png"):
        print("模板文件不存在，跳过特征提取示例")
        return
    
    import cv2
    
    # 加载模板图像
    template_image = cv2.imread("mb6.png")
    print(f"模板图像尺寸: {template_image.shape}")
    
    # 提取特征
    processor = PDFProcessor()
    features = processor._extract_features(template_image)
    
    # 显示主要特征
    print(f"白色背景占比: {features.get('white_ratio', 0)*100:.1f}%")
    print(f"黑色文字占比: {features.get('black_ratio', 0)*100:.1f}%")
    print(f"检测到的区域数: {len(features.get('regions', {}))}")
    print(f"检测到的关键框数: {len(features.get('key_boxes', {}))}")
    
    # 关键词检测
    keywords = features.get('keywords', {})
    for keyword, found in keywords.items():
        print(f"{keyword}: {'✓' if found else '✗'}")

if __name__ == "__main__":
    print("PDF标准文档分类系统 - 使用示例")
    print("="*50)
    
    try:
        example_basic_usage()
        example_single_pdf()
        example_feature_extraction()
        
        print("\n=== 示例运行完成 ===")
        print("更多使用方法请参考 README.md")
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        print("请检查依赖项是否正确安装")
