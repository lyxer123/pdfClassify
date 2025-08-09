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

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 解析参数
    args = parse_arguments()
    
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

