#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
递归PDF分类工具 - 快速启动脚本
提供交互式界面，让用户选择要扫描的文件夹
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recursive_pdf_classify import RecursivePDFClassifier

def get_user_input():
    """获取用户输入"""
    print("🚀 递归PDF分类工具 - 快速启动")
    print("=" * 60)
    
    # 获取源文件夹
    while True:
        source_folder = input("\n📁 请输入要扫描的文件夹路径 (或按回车使用默认的input_pdfs): ").strip()
        
        if not source_folder:
            source_folder = "input_pdfs"
            print(f"✅ 使用默认文件夹: {source_folder}")
        
        if os.path.exists(source_folder):
            break
        else:
            print(f"❌ 文件夹不存在: {source_folder}")
            print("💡 请检查路径是否正确，或按回车使用默认文件夹")
    
    # 获取目标文件夹
    target_folder = input("\n🎯 请输入目标文件夹路径 (或按回车使用默认的jc): ").strip()
    if not target_folder:
        target_folder = "jc"
        print(f"✅ 使用默认目标文件夹: {target_folder}")
    
    # 是否启用详细模式
    verbose = input("\n🔍 是否启用详细输出模式? (y/N): ").strip().lower()
    verbose_mode = verbose in ['y', 'yes', '是']
    
    return source_folder, target_folder, verbose_mode

def confirm_scan(source_folder, target_folder):
    """确认扫描设置"""
    print(f"\n📋 扫描设置确认:")
    print(f"  源文件夹: {source_folder}")
    print(f"  目标文件夹: {target_folder}")
    
    # 统计源文件夹中的PDF文件数量
    pdf_count = 0
    if os.path.exists(source_folder):
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_count += 1
    
    print(f"  预计PDF文件数: {pdf_count}")
    
    if pdf_count == 0:
        print("⚠️  警告: 源文件夹中未找到PDF文件!")
        return False
    
    confirm = input(f"\n🚀 确认开始扫描 {pdf_count} 个PDF文件? (Y/n): ").strip().lower()
    return confirm not in ['n', 'no', '否']

def main():
    """主函数"""
    try:
        # 检查依赖
        print("🔍 检查依赖包...")
        try:
            import fitz
            import cv2
            import numpy as np
            from PIL import Image
            print("✅ 所有依赖包已安装")
        except ImportError as e:
            print(f"❌ 缺少依赖包: {e}")
            print("💡 请运行: pip install -r requirements.txt")
            return
        
        # 获取用户输入
        source_folder, target_folder, verbose_mode = get_user_input()
        
        # 确认设置
        if not confirm_scan(source_folder, target_folder):
            print("❌ 用户取消操作")
            return
        
        # 设置日志级别
        if verbose_mode:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            print("🔍 已启用详细输出模式")
        
        # 创建分类器
        print(f"\n🔄 创建分类器...")
        classifier = RecursivePDFClassifier(source_folder, target_folder)
        
        # 开始扫描和处理
        print(f"🚀 开始扫描和处理...")
        classifier.scan_and_process()
        
        print(f"\n🎉 处理完成!")
        print(f"📁 符合条件的PDF文件已复制到: {target_folder}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n💡 使用提示:")
        print(f"1. 直接运行: python recursive_pdf_classify.py \"{source_folder}\"")
        print(f"2. 查看详细结果: 检查生成的JSON文件和日志文件")
        print(f"3. 查看使用说明: usage_recursive_classify.md")
        print(f"4. 查看项目详情: README_recursive_classify.md")

if __name__ == "__main__":
    main()
