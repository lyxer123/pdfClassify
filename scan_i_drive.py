# -*- coding: utf-8 -*-
"""
I盘PDF标准文档递归扫描脚本
"""

import os
import sys
import time
from pdf_processor import PDFProcessor
import logging

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('i_drive_scan.log', encoding='utf-8')
        ]
    )

def count_pdf_files(root_dir):
    """统计PDF文件数量"""
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                count += 1
    return count

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # I盘路径
    i_drive = "I:\\"
    output_dir = "jc"
    
    print("🔍 I盘PDF标准文档递归扫描系统")
    print("="*50)
    
    # 检查I盘是否存在
    if not os.path.exists(i_drive):
        logger.error("I盘不存在或无法访问")
        print("❌ I盘不存在或无法访问")
        return
    
    print(f"📁 扫描目录: {i_drive}")
    print("🔄 正在统计PDF文件数量...")
    
    # 统计PDF文件总数
    total_pdfs = count_pdf_files(i_drive)
    print(f"📊 发现 {total_pdfs} 个PDF文件")
    
    if total_pdfs == 0:
        print("⚠️  未找到PDF文件")
        return
    
    # 确认是否继续
    confirm = input(f"\n是否继续处理 {total_pdfs} 个PDF文件？这可能需要很长时间。(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    # 初始化PDF处理器
    print("\n🚀 初始化PDF处理器...")
    try:
        processor = PDFProcessor()
        logger.info("PDF处理器初始化成功")
        print("✅ PDF处理器初始化成功")
    except Exception as e:
        logger.error(f"PDF处理器初始化失败: {e}")
        print(f"❌ PDF处理器初始化失败: {e}")
        return
    
    # 开始批量处理
    start_time = time.time()
    print(f"\n📋 开始递归处理I盘所有PDF文件...")
    print(f"📂 输出目录: {output_dir}")
    print("⏱️  处理开始时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        results = processor.batch_process(i_drive, output_dir, recursive=True)
        
        # 处理完成
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n" + "="*50)
        print("🎯 处理完成！")
        print("="*50)
        print(f"📊 处理结果统计:")
        print(f"   总文件数: {results['total_files']}")
        print(f"   匹配成功: {results['successful_files']}")
        print(f"   匹配失败: {results['failed_files']}")
        print(f"   成功率: {results['successful_files']/results['total_files']*100:.1f}%" if results['total_files'] > 0 else "   成功率: 0%")
        print(f"   总处理时间: {processing_time/60:.1f} 分钟")
        
        # 显示成功文件
        if results['successful_paths']:
            print(f"\n✅ 匹配成功的文件 ({len(results['successful_paths'])} 个):")
            for i, path in enumerate(results['successful_paths'][:10], 1):  # 只显示前10个
                print(f"   {i}. {os.path.basename(path)}")
            
            if len(results['successful_paths']) > 10:
                print(f"   ... 还有 {len(results['successful_paths']) - 10} 个文件")
            
            print(f"\n📁 所有匹配的文件已复制到: {output_dir}")
        else:
            print("\n⚠️  没有文件匹配标准模板")
        
        # 显示失败统计
        if results['failed_reasons']:
            print(f"\n❌ 常见失败原因:")
            reason_count = {}
            for reason in results['failed_reasons'].values():
                reason_count[reason] = reason_count.get(reason, 0) + 1
            
            for reason, count in sorted(reason_count.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {reason}: {count} 个文件")
        
        logger.info(f"I盘扫描完成，成功匹配 {results['successful_files']} 个文件")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断处理")
        logger.info("用户中断I盘扫描")
    except Exception as e:
        print(f"\n❌ 处理过程中发生错误: {e}")
        logger.error(f"I盘扫描失败: {e}")
    
    print(f"\n📋 详细日志保存在: i_drive_scan.log")

if __name__ == "__main__":
    main()
