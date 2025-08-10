#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试I盘PDF处理脚本的功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 全局导入
try:
    from pdf_analyzer import UnifiedPDFAnalyzer
    PDF_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PDF分析器导入失败: {e}")
    PDF_ANALYZER_AVAILABLE = False

def test_imports():
    """测试必要的导入"""
    print("🔍 测试必要的导入...")
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) 导入成功")
    except ImportError as e:
        print(f"❌ PyMuPDF (fitz) 导入失败: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV (cv2) 导入成功")
    except ImportError as e:
        print(f"❌ OpenCV (cv2) 导入失败: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL (Pillow) 导入成功")
    except ImportError as e:
        print(f"❌ PIL (Pillow) 导入失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy 导入成功")
    except ImportError as e:
        print(f"❌ NumPy 导入失败: {e}")
        return False
    
    if PDF_ANALYZER_AVAILABLE:
        print("✅ PDF分析器导入成功")
    else:
        print("❌ PDF分析器导入失败")
        return False
    
    return True

def test_paths():
    """测试路径设置"""
    print("\n🔍 测试路径设置...")
    
    # 检查jc文件夹（相对于项目根目录）
    jc_path = project_root / "jc"
    if jc_path.exists():
        print(f"✅ jc文件夹存在: {jc_path}")
    else:
        print(f"⚠️ jc文件夹不存在，将自动创建")
    
    # 检查tests/logs文件夹（相对于项目根目录）
    logs_path = project_root / "tests" / "logs"
    if logs_path.exists():
        print(f"✅ logs文件夹存在: {logs_path}")
    else:
        print(f"⚠️ logs文件夹不存在，将自动创建")
    
    # 检查I盘路径
    i_drive = r"I:\1T硬盘D"
    if os.path.exists(i_drive):
        print(f"✅ I盘路径存在: {i_drive}")
        
        # 尝试列出内容
        try:
            items = os.listdir(i_drive)
            print(f"   I盘根目录包含 {len(items)} 个项目")
        except PermissionError:
            print("   ⚠️ 没有访问I盘的权限")
        except Exception as e:
            print(f"   ⚠️ 访问I盘时出错: {e}")
    else:
        print(f"❌ I盘路径不存在: {i_drive}")
        print("   请检查驱动器是否已连接")

def test_pdf_analyzer():
    """测试PDF分析器功能"""
    print("\n🔍 测试PDF分析器功能...")
    
    if not PDF_ANALYZER_AVAILABLE:
        print("❌ PDF分析器不可用，跳过测试")
        return False
    
    try:
        # 创建临时测试目录（相对于项目根目录）
        test_source = project_root / "test_temp"
        test_source.mkdir(exist_ok=True)
        
        # 创建分析器实例
        analyzer = UnifiedPDFAnalyzer(str(test_source), str(project_root / "test_jc"))
        
        print("✅ PDF分析器创建成功")
        print(f"   源文件夹: {analyzer.source_folder}")
        print(f"   目标文件夹: {analyzer.target_folder}")
        
        # 清理测试目录
        import shutil
        shutil.rmtree(test_source, ignore_errors=True)
        shutil.rmtree(project_root / "test_jc", ignore_errors=True)
        
    except Exception as e:
        print(f"❌ PDF分析器测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🧪 I盘PDF处理脚本功能测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖包安装")
        return False
    
    # 测试路径
    test_paths()
    
    # 测试PDF分析器
    if not test_pdf_analyzer():
        print("\n❌ PDF分析器测试失败")
        return False
    
    print("\n✅ 所有测试通过！")
    print("🎉 脚本可以正常运行")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🚀 可以开始运行主脚本了！")
            print("运行命令: python process_i_drive_pdfs.py")
        else:
            print("\n❌ 测试失败，请检查问题后重试")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
