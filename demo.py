# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统演示脚本
基于mb6.png模板的企业标准特征识别演示
"""

import os
import sys
import cv2
import numpy as np
from pdf_processor import PDFProcessor
import matplotlib.pyplot as plt

def create_sample_test():
    """创建样本测试数据"""
    print("创建测试环境...")
    
    # 确保测试目录存在
    test_dirs = ['test_pdfs', 'jc']
    for dir_name in test_dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ 创建目录: {dir_name}")

def demo_template_analysis():
    """演示模板分析功能"""
    print("\n" + "="*60)
    print("【演示1】模板特征分析")
    print("="*60)
    
    template_path = "mb6.png"
    if not os.path.exists(template_path):
        print(f"❌ 模板文件 {template_path} 不存在")
        return False
    
    # 初始化处理器
    processor = PDFProcessor(template_path=template_path)
    
    # 加载模板图像
    template_image = cv2.imread(template_path)
    print(f"📄 模板图像尺寸: {template_image.shape[1]}×{template_image.shape[0]} 像素")
    
    # 提取特征
    features = processor._extract_features(template_image)
    
    # 显示关键指标
    print(f"\n📊 颜色分析:")
    print(f"   白色背景占比: {features.get('white_ratio', 0)*100:.1f}%")
    print(f"   黑色文字占比: {features.get('black_ratio', 0)*100:.1f}%")
    
    print(f"\n📐 区域检测:")
    regions = features.get('regions', {})
    for region_name in ['upper', 'middle', 'lower']:
        if region_name in regions:
            print(f"   {region_name}区域: ✓")
        else:
            print(f"   {region_name}区域: ❌")
    
    print(f"\n🎯 关键框检测:")
    key_boxes = features.get('key_boxes', {})
    detected_boxes = len(key_boxes)
    print(f"   检测到 {detected_boxes}/6 个关键框")
    
    print(f"\n📝 关键词验证:")
    keywords = features.get('keywords', {})
    standard_found = keywords.get('upper_has_standard', False)
    publish_found = keywords.get('lower_has_publish', False)
    print(f"   上部'标准': {'✓' if standard_found else '❌'}")
    print(f"   下部'发布': {'✓' if publish_found else '❌'}")
    
    print(f"\n📏 横线检测:")
    lines = features.get('lines', {})
    first_line = lines.get('first_line_valid', False)
    second_line = lines.get('second_line_valid', False)
    print(f"   第一横线: {'✓' if first_line else '❌'}")
    print(f"   第二横线: {'✓' if second_line else '❌'}")
    
    # 模板验证
    is_valid = processor._validate_features(features)
    print(f"\n🔍 模板验证结果: {'✅ 通过' if is_valid else '❌ 不通过'}")
    
    return True

def demo_feature_visualization():
    """演示特征可视化功能"""
    print("\n" + "="*60)
    print("【演示2】特征可视化")
    print("="*60)
    
    # 检查是否有test_features.py
    if os.path.exists('test_features.py'):
        print("🎨 运行特征可视化...")
        os.system('python test_features.py')
        
        if os.path.exists('feature_visualization.png'):
            print("✅ 特征可视化图像已生成: feature_visualization.png")
        else:
            print("❌ 特征可视化生成失败")
    else:
        print("❌ test_features.py 文件不存在")

def demo_batch_processing():
    """演示批量处理功能"""
    print("\n" + "="*60)
    print("【演示3】批量处理功能")
    print("="*60)
    
    test_dir = "test_pdfs"
    output_dir = "jc"
    
    # 检查测试目录
    if not os.path.exists(test_dir):
        print(f"📁 创建测试目录: {test_dir}")
        os.makedirs(test_dir, exist_ok=True)
    
    # 统计PDF文件
    pdf_files = [f for f in os.listdir(test_dir) if f.lower().endswith('.pdf')]
    print(f"📄 在 {test_dir} 目录中找到 {len(pdf_files)} 个PDF文件")
    
    if len(pdf_files) == 0:
        print("💡 提示: 将PDF文件放入 test_pdfs 目录来测试批量处理功能")
        print("   示例: python main.py test_pdfs")
        return
    
    # 初始化处理器
    processor = PDFProcessor()
    
    # 执行批量处理
    print("🔄 开始批量处理...")
    results = processor.batch_process(test_dir, output_dir)
    
    # 显示结果
    print(f"\n📊 处理结果:")
    print(f"   总文件数: {results['total_files']}")
    print(f"   成功匹配: {results['successful_files']}")
    print(f"   匹配失败: {results['failed_files']}")
    
    if results['total_files'] > 0:
        success_rate = results['successful_files'] / results['total_files'] * 100
        print(f"   成功率: {success_rate:.1f}%")
    
    # 显示成功文件
    if results['successful_paths']:
        print(f"\n✅ 成功匹配的文件:")
        for path in results['successful_paths']:
            print(f"   📄 {os.path.basename(path)}")
    
    # 显示失败原因
    if results['failed_reasons']:
        print(f"\n❌ 失败文件及原因:")
        for filename, reason in results['failed_reasons'].items():
            print(f"   📄 {filename}: {reason}")

def demo_single_pdf_processing():
    """演示单个PDF处理功能"""
    print("\n" + "="*60)
    print("【演示4】单PDF处理功能")
    print("="*60)
    
    # 查找第一个PDF文件进行演示
    test_dir = "test_pdfs"
    pdf_files = []
    
    if os.path.exists(test_dir):
        pdf_files = [f for f in os.listdir(test_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("💡 未找到PDF文件进行演示")
        print("   请将PDF文件放入 test_pdfs 目录")
        return
    
    # 选择第一个PDF文件
    pdf_file = pdf_files[0]
    pdf_path = os.path.join(test_dir, pdf_file)
    
    print(f"📄 处理文件: {pdf_file}")
    
    # 初始化处理器
    processor = PDFProcessor()
    
    # 处理PDF
    print("🔄 正在处理...")
    result = processor.process_pdf(pdf_path)
    
    # 显示结果
    print(f"\n📊 处理结果:")
    print(f"   文件路径: {result['pdf_path']}")
    print(f"   处理状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"   处理时间: {result['processing_time']:.2f} 秒")
    print(f"   结果说明: {result['reason']}")
    
    if result['success'] and result['features']:
        features = result['features']
        print(f"\n📝 特征摘要:")
        print(f"   白色背景: {features.get('white_ratio', 0)*100:.1f}%")
        print(f"   检测区域: {len(features.get('regions', {}))}/3")
        print(f"   检测框数: {len(features.get('key_boxes', {}))}/6")
        
        keywords = features.get('keywords', {})
        keyword_count = sum(1 for v in keywords.values() if v)
        print(f"   关键词匹配: {keyword_count}/{len(keywords)}")

def show_usage_examples():
    """显示使用示例"""
    print("\n" + "="*60)
    print("【使用示例】")
    print("="*60)
    
    print("💻 命令行使用:")
    print("   # 处理当前目录的PDF文件")
    print("   python main.py")
    print("")
    print("   # 处理指定目录的PDF文件")
    print("   python main.py /path/to/pdf/files")
    print("")
    print("   # 指定输出目录")
    print("   python main.py --output-dir classified_pdfs")
    print("")
    print("   # 使用自定义模板")
    print("   python main.py --template my_template.png")
    print("")
    print("   # 设置处理超时时间")
    print("   python main.py --timeout 30")
    
    print("\n🔧 测试功能:")
    print("   # 测试特征提取")
    print("   python test_features.py")
    print("")
    print("   # 运行演示")
    print("   python demo.py")

def main():
    """主演示函数"""
    print("🚀 PDF标准文档分类系统演示")
    print("基于mb6.png模板的企业标准特征识别")
    print("="*60)
    
    # 检查依赖
    try:
        import cv2, numpy, pytesseract
        from pdf2image import convert_from_path
        print("✅ 所有依赖项已正确安装")
    except ImportError as e:
        print(f"❌ 缺少依赖项: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 创建测试环境
    create_sample_test()
    
    # 运行演示
    try:
        # 演示1: 模板分析
        if demo_template_analysis():
            # 演示2: 特征可视化
            demo_feature_visualization()
            
            # 演示3: 批量处理
            demo_batch_processing()
            
            # 演示4: 单PDF处理
            demo_single_pdf_processing()
            
            # 显示使用示例
            show_usage_examples()
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        print("请检查环境配置和依赖项安装")
    
    print("\n🎯 演示完成！")
    print("如需处理实际PDF文件，请使用: python main.py [输入目录]")

if __name__ == "__main__":
    main()
