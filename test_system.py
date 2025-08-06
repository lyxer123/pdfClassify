#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 系统测试脚本
"""

import os
import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("1. 测试模块导入...")
    
    try:
        import cv2
        print("   ✅ OpenCV 导入成功")
    except ImportError:
        print("   ❌ OpenCV 导入失败")
        return False
    
    try:
        import numpy as np
        print("   ✅ NumPy 导入成功")
    except ImportError:
        print("   ❌ NumPy 导入失败")
        return False
    
    try:
        from PIL import Image
        print("   ✅ Pillow 导入成功")
    except ImportError:
        print("   ❌ Pillow 导入失败")
        return False
    
    try:
        import fitz
        print("   ✅ PyMuPDF 导入成功")
    except ImportError:
        print("   ❌ PyMuPDF 导入失败")
        return False
    
    try:
        from main import StandardDocumentFeatureExtractor
        print("   ✅ StandardDocumentFeatureExtractor 导入成功")
    except ImportError:
        print("   ❌ StandardDocumentFeatureExtractor 导入失败")
        return False
    
    try:
        from pdf_processor import PDFProcessor
        print("   ✅ PDFProcessor 导入成功")
    except ImportError:
        print("   ❌ PDFProcessor 导入失败")
        return False
    
    return True

def test_files():
    """测试必要文件"""
    print("\n2. 测试必要文件...")
    
    required_files = [
        "main.py",
        "pdf_processor.py",
        "config.py"
    ]
    
    optional_files = [
        "mb3.png",
        "requirements.txt"
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} 存在")
        else:
            print(f"   ❌ {file} 不存在")
            all_good = False
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"   ✅ {file} 存在（可选）")
        else:
            print(f"   ⚠️   {file} 不存在（可选）")
    
    return all_good

def test_config():
    """测试配置"""
    print("\n3. 测试配置...")
    
    try:
        from config import DETECTION_CONFIG, CRITICAL_FEATURES, PAGE_REGIONS
        
        print(f"   ✅ 检测配置加载成功")
        print(f"      最小特征数: {DETECTION_CONFIG['min_features']}")
        print(f"      总特征数: {DETECTION_CONFIG['total_features']}")
        print(f"      位置符合度阈值: {DETECTION_CONFIG['position_confidence_threshold']}")
        print(f"      模板相似度阈值: {DETECTION_CONFIG['template_similarity_threshold']}")
        
        print(f"   ✅ 关键特征配置: {len(CRITICAL_FEATURES)} 个")
        for feature in CRITICAL_FEATURES:
            print(f"      - {feature}")
        
        print(f"   ✅ 页面区域配置加载成功")
        for region, ratio in PAGE_REGIONS.items():
            print(f"      {region}: {ratio*100}%")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 配置加载失败: {e}")
        return False

def test_feature_extractor():
    """测试特征提取器"""
    print("\n4. 测试特征提取器...")
    
    try:
        from main import StandardDocumentFeatureExtractor
        
        # 检查是否有测试图片
        test_images = ["mb3.png", "jc.png", "mb.png", "mb2.png"]
        test_image = None
        
        for img in test_images:
            if os.path.exists(img):
                test_image = img
                break
        
        if test_image:
            print(f"   📷 使用测试图片: {test_image}")
            
            extractor = StandardDocumentFeatureExtractor(test_image)
            
            # 测试图片加载
            if extractor.load_image():
                print("   ✅ 图片加载成功")
                
                # 测试特征提取
                features = extractor.extract_features()
                if features:
                    print("   ✅ 特征提取成功")
                    print(f"      检测到的特征数: {features['detected_features']}/7")
                    print(f"      检测率: {features['detection_rate']:.2%}")
                    
                    if 'template_similarity' in features:
                        print(f"      模板相似度: {features['template_similarity']:.3f}")
                    
                    return True
                else:
                    print("   ❌ 特征提取失败")
                    return False
            else:
                print("   ❌ 图片加载失败")
                return False
        else:
            print("   ⚠️  没有找到测试图片，跳过特征提取测试")
            return True
            
    except Exception as e:
        print(f"   ❌ 特征提取器测试失败: {e}")
        return False

def test_pdf_processor():
    """测试PDF处理器"""
    print("\n5. 测试PDF处理器...")
    
    try:
        from pdf_processor import PDFProcessor
        
        # 创建处理器实例
        processor = PDFProcessor()
        
        print(f"   ✅ PDF处理器创建成功")
        print(f"      源驱动器: {processor.source_drive}")
        print(f"      目标文件夹: {processor.target_folder}")
        
        # 检查目标文件夹
        if processor.target_folder.exists():
            print("   ✅ 目标文件夹存在")
        else:
            print("   ⚠️  目标文件夹不存在，将自动创建")
        
        # 检查源驱动器
        if processor.source_drive.exists():
            print("   ✅ 源驱动器存在")
        else:
            print("   ⚠️  源驱动器不存在，请检查配置")
        
        return True
        
    except Exception as e:
        print(f"   ❌ PDF处理器测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库版本"""
    print("\n6. 测试依赖库版本...")
    
    try:
        import cv2
        print(f"   OpenCV 版本: {cv2.__version__}")
        
        import numpy as np
        print(f"   NumPy 版本: {np.__version__}")
        
        from PIL import Image
        print(f"   Pillow 版本: {Image.__version__}")
        
        import fitz
        print(f"   PyMuPDF 版本: {fitz.version}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 版本检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("PDF标准文档分类系统 - 系统测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_files,
        test_config,
        test_feature_extractor,
        test_pdf_processor,
        test_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 