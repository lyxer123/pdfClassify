#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 使用示例
"""

from pdf_processor import PDFProcessor
import os

def main():
    """
    使用示例主函数
    """
    print("PDF标准文档分类系统 - 使用示例")
    print("=" * 50)
    
    # 示例1：基本使用
    print("\n1. 基本使用示例")
    print("-" * 30)
    
    # 创建处理器实例（使用默认设置）
    processor = PDFProcessor()
    
    # 检查E盘是否存在
    if not processor.source_drive.exists():
        print(f"警告: 驱动器 {processor.source_drive} 不存在")
        print("请修改源代码中的source_drive参数")
        return
    
    # 执行批量处理
    print("开始处理PDF文件...")
    processor.process_all()
    
    # 示例2：自定义配置
    print("\n2. 自定义配置示例")
    print("-" * 30)
    
    # 创建自定义配置的处理器
    custom_processor = PDFProcessor(
        source_drive="D:",  # 修改源驱动器
        target_folder="standard_docs"  # 修改目标文件夹
    )
    
    print(f"源驱动器: {custom_processor.source_drive}")
    print(f"目标文件夹: {custom_processor.target_folder}")
    
    # 示例3：处理单个文件
    print("\n3. 处理单个文件示例")
    print("-" * 30)
    
    # 假设有一个测试PDF文件
    test_pdf = "test_document.pdf"
    if os.path.exists(test_pdf):
        result = processor.process_pdf(test_pdf)
        if result["success"]:
            if result["copied"]:
                print(f"✅ 文件 {test_pdf} 被识别为标准文档")
                print(f"   检测到的特征数: {result['features']}")
                if 'confidence' in result:
                    print(f"   位置符合度: {result['confidence']:.2f}")
                if 'template_similarity' in result:
                    print(f"   模板相似度: {result['template_similarity']:.3f}")
            else:
                print(f"❌ 文件 {test_pdf} 不符合标准文档要求")
        else:
            print(f"❌ 处理文件 {test_pdf} 时出现错误")
    else:
        print(f"测试文件 {test_pdf} 不存在")
    
    # 示例4：检查输出文件夹
    print("\n4. 检查输出结果")
    print("-" * 30)
    
    output_folder = processor.target_folder
    if output_folder.exists():
        pdf_files = list(output_folder.glob("*.pdf"))
        print(f"输出文件夹: {output_folder.absolute()}")
        print(f"找到 {len(pdf_files)} 个标准文档")
        
        if pdf_files:
            print("标准文档列表:")
            for i, pdf_file in enumerate(pdf_files[:5], 1):  # 只显示前5个
                print(f"  {i}. {pdf_file.name}")
            if len(pdf_files) > 5:
                print(f"  ... 还有 {len(pdf_files) - 5} 个文件")
        else:
            print("暂无标准文档")
    else:
        print("输出文件夹不存在")
    
    print("\n示例运行完成!")

if __name__ == "__main__":
    main() 