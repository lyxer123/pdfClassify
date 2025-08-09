# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统主程序
基于mb6.png模板的企业标准特征识别
"""

import os
import sys
import argparse
import logging
from pdf_processor import PDFProcessor
import cv2

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pdf_classify.log', encoding='utf-8')
        ]
    )

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PDF标准文档分类系统')
    parser.add_argument(
        'input_dir',
        nargs='?',
        default='.',
        help='输入目录路径（默认为当前目录）'
    )
    parser.add_argument(
        '--output-dir',
        default='jc',
        help='输出目录路径（默认为jc）'
    )
    parser.add_argument(
        '--template',
        default='mb6.png',
        help='模板图片路径（默认为mb6.png）'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=15,
        help='单PDF处理超时时间（秒，默认为15）'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='递归搜索子目录中的PDF文件'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='运行演示模式，展示系统功能'
    )
    
    return parser.parse_args()

def check_dependencies():
    """检查依赖项"""
    try:
        import cv2
        import numpy
        import pytesseract
        from pdf2image import convert_from_path
        print("✓ 所有依赖项已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖项: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_tesseract():
    """检查Tesseract OCR"""
    try:
        import pytesseract
        # 测试Tesseract是否可用
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR 可用")
        return True
    except Exception as e:
        print(f"✗ Tesseract OCR 不可用: {e}")
        print("请安装Tesseract OCR和中文语言包")
        return False

def demo_template_analysis():
    """演示模板分析功能"""
    print("\n" + "="*60)
    print("【演示1】模板特征分析")
    print("="*60)
    
    template_path = "mb6.png"
    if not os.path.exists(template_path):
        template_path = "templates/mb6.png"
        if not os.path.exists(template_path):
            print(f"❌ 模板文件 mb6.png 不存在（已检查当前目录和templates目录）")
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

def demo_batch_processing(test_dir="input_pdfs", output_dir="jc"):
    """演示批量处理功能"""
    print("\n" + "="*60)
    print("【演示3】批量处理功能")
    print("="*60)
    
    # 检查测试目录
    if not os.path.exists(test_dir):
        print(f"📁 创建测试目录: {test_dir}")
        os.makedirs(test_dir, exist_ok=True)
    
    # 统计PDF文件
    pdf_files = [f for f in os.listdir(test_dir) if f.lower().endswith('.pdf')]
    print(f"📄 在 {test_dir} 目录中找到 {len(pdf_files)} 个PDF文件")
    
    if len(pdf_files) == 0:
        print("💡 提示: 将PDF文件放入 input_pdfs 目录来测试批量处理功能")
        print("   示例: python main.py input_pdfs")
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

def run_demo_mode():
    """运行演示模式"""
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
    print("创建测试环境...")
    test_dirs = ['input_pdfs', 'jc', 'templates', 'data']
    for dir_name in test_dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ 创建目录: {dir_name}")
    
    # 运行演示
    try:
        # 演示1: 模板分析
        if demo_template_analysis():
            # 演示2: 特征可视化
            demo_feature_visualization()
            
            # 演示3: 批量处理
            demo_batch_processing()
            
            # 显示使用示例
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
            print("")
            print("   # 运行演示模式")
            print("   python main.py --demo")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        print("请检查环境配置和依赖项安装")
    
    print("\n🎯 演示完成！")
    print("如需处理实际PDF文件，请使用: python main.py [输入目录]")

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 解析参数
    args = parse_arguments()
    
    # 如果是演示模式，直接运行演示
    if args.demo:
        run_demo_mode()
        return
    
    # 检查依赖项
    if not check_dependencies():
        sys.exit(1)
    
    if not check_tesseract():
        sys.exit(1)
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        sys.exit(1)
    
    # 检查模板文件
    if not os.path.exists(args.template):
        logger.error(f"模板文件不存在: {args.template}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 初始化PDF处理器
    try:
        processor = PDFProcessor(template_path=args.template)
        logger.info("PDF处理器初始化成功")
    except Exception as e:
        logger.error(f"PDF处理器初始化失败: {e}")
        sys.exit(1)
    
    # 统计PDF文件数量
    if args.recursive:
        pdf_files = []
        for root, dirs, files in os.walk(args.input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        pdf_files = [f for f in os.listdir(args.input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        search_type = "递归搜索" if args.recursive else "搜索"
        logger.warning(f"{search_type}目录 {args.input_dir} 中未找到PDF文件")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 批量处理
    if args.recursive:
        logger.info(f"开始递归搜索并处理 {args.input_dir} 目录下的所有PDF文件...")
    else:
        logger.info("开始批量处理PDF文件...")
    
    results = processor.batch_process(args.input_dir, args.output_dir, recursive=args.recursive)
    
    # 输出结果统计
    logger.info("=" * 50)
    logger.info("处理结果统计:")
    logger.info(f"总文件数: {results['total_files']}")
    logger.info(f"成功匹配: {results['successful_files']}")
    logger.info(f"匹配失败: {results['failed_files']}")
    logger.info(f"成功率: {results['successful_files']/results['total_files']*100:.1f}%" if results['total_files'] > 0 else "成功率: 0%")
    
    # 输出成功文件列表
    if results['successful_paths']:
        logger.info("\n成功匹配的文件:")
        for path in results['successful_paths']:
            logger.info(f"  ✓ {os.path.basename(path)}")
    
    # 输出失败原因
    if results['failed_reasons']:
        logger.info("\n失败原因:")
        for filename, reason in results['failed_reasons'].items():
            logger.info(f"  ✗ {filename}: {reason}")
    
    logger.info("=" * 50)
    logger.info(f"处理完成！匹配成功的文件已复制到 {args.output_dir} 目录")

if __name__ == "__main__":
    main()

