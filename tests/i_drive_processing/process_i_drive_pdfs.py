#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I盘PDF文件批量处理脚本
功能：
1. 递归扫描I:\1T硬盘D下的所有PDF文件
2. 使用项目的第一特征和第二特征进行验证
3. 符合条件的PDF文件复制到jc文件夹
4. 详细日志保存到tests/logs目录
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pdf_analyzer import UnifiedPDFAnalyzer

def setup_logging():
    """设置日志配置"""
    # 确保logs目录存在（相对于项目根目录）
    log_dir = project_root / "tests" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志文件名（包含时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"i_drive_processing_{timestamp}.log"
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"日志文件: {log_file}")
    
    return logger, log_file

def check_drive_access(drive_path):
    """检查驱动器访问权限"""
    try:
        if not os.path.exists(drive_path):
            return False, f"驱动器路径不存在: {drive_path}"
        
        # 尝试列出目录内容
        test_list = os.listdir(drive_path)
        return True, f"驱动器访问正常，根目录包含 {len(test_list)} 个项目"
        
    except PermissionError:
        return False, f"没有访问驱动器 {drive_path} 的权限"
    except Exception as e:
        return False, f"访问驱动器时出错: {str(e)}"

def main():
    """主函数"""
    print("🚀 I盘PDF文件批量处理工具")
    print("=" * 60)
    
    # 设置日志
    logger, log_file = setup_logging()
    
    # 定义路径（相对于项目根目录）
    source_drive = r"I:\1T硬盘D"
    target_folder = project_root / "jc"
    
    print(f"📁 源驱动器: {source_drive}")
    print(f"📁 目标文件夹: {target_folder}")
    print(f"📝 日志文件: {log_file}")
    print("-" * 60)
    
    # 检查驱动器访问权限
    logger.info(f"检查驱动器访问权限: {source_drive}")
    access_ok, access_msg = check_drive_access(source_drive)
    
    if not access_ok:
        print(f"❌ {access_msg}")
        logger.error(access_msg)
        return
    
    print(f"✅ {access_msg}")
    logger.info(access_msg)
    
    # 确保目标文件夹存在
    target_path = Path(target_folder)
    target_path.mkdir(exist_ok=True)
    logger.info(f"目标文件夹已准备: {target_path}")
    
    try:
        # 创建PDF分析器
        logger.info("创建PDF分析器")
        analyzer = UnifiedPDFAnalyzer(source_drive, str(target_folder))
        
        # 开始递归处理
        logger.info("开始递归处理PDF文件")
        print("\n🔄 开始处理PDF文件...")
        print("这可能需要一些时间，请耐心等待...")
        
        # 运行分析
        analyzer.run_analysis(mode="recursive")
        
        # 输出完成信息
        print("\n" + "=" * 60)
        print("🎉 处理完成!")
        print(f"📊 处理统计:")
        print(f"  总PDF文件数: {analyzer.stats['total_pdfs']}")
        print(f"  第一特征通过: {analyzer.stats['first_feature_passed']}")
        print(f"  第二特征通过: {analyzer.stats['second_feature_passed']}")
        print(f"  成功复制文件: {analyzer.stats['copied_files']}")
        print(f"  处理错误: {analyzer.stats['errors']}")
        
        if analyzer.stats['total_pdfs'] > 0:
            copy_rate = analyzer.stats['copied_files'] / analyzer.stats['total_pdfs'] * 100
            print(f"  最终复制率: {copy_rate:.1f}%")
        
        print(f"\n📁 符合条件的PDF文件已复制到: {target_folder}")
        print(f"📝 详细日志已保存到: {log_file}")
        
        logger.info("PDF处理任务完成")
        
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        
        # 尝试提供更多错误信息
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了处理过程")
        logging.info("用户中断了处理过程")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        logging.error(f"程序执行失败: {str(e)}", exc_info=True)
