#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证基本功能
"""

# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

def test_imports():
    """测试导入功能"""
    print("🔍 测试导入功能...")
    
    try:
        from pdf_analyzer import UnifiedPDFAnalyzer
        print("✅ UnifiedPDFAnalyzer 导入成功")
    except ImportError as e:
        print(f"❌ UnifiedPDFAnalyzer 导入失败: {e}")
        return False
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        print("✅ PDFFeatureExtractor 导入成功")
    except ImportError as e:
        print(f"❌ PDFFeatureExtractor 导入失败: {e}")
        return False
    
    print()
    return True

def test_analyzer_creation():
    """测试分析器创建"""
    print("🔧 测试分析器创建...")
    
    try:
        from pdf_analyzer import UnifiedPDFAnalyzer
        
        # 创建分析器
        analyzer = UnifiedPDFAnalyzer("input_pdfs", "jc")
        print("✅ 分析器创建成功")
        
        # 检查属性
        print(f"  - 源文件夹: {analyzer.source_folder}")
        print(f"  - 目标文件夹: {analyzer.target_folder}")
        print(f"  - 统计信息: {analyzer.stats}")
        
        print()
        return analyzer
        
    except Exception as e:
        print(f"❌ 分析器创建失败: {e}")
        print()
        return None

def test_feature_extractor():
    """测试特征提取器"""
    print("🔬 测试特征提取器...")
    
    try:
        from pdf_feature_extractor import PDFFeatureExtractor
        
        # 创建特征提取器
        extractor = PDFFeatureExtractor()
        print("✅ 特征提取器创建成功")
        
        # 检查配置
        print(f"  - 模板路径: {extractor.template_path}")
        print(f"  - 数据目录: {extractor.data_dir}")
        print(f"  - 阈值配置: {len(extractor.color_thresholds)} 项")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 特征提取器创建失败: {e}")
        print()
        return False

def test_directory_structure():
    """测试目录结构"""
    print("📁 测试目录结构...")
    
    required_dirs = ["input_pdfs", "jc", "templates", "data"]
    required_files = ["pdf_analyzer.py", "pdf_feature_extractor.py", "requirements.txt"]
    
    # 检查目录
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录缺失: {dir_name}")
    
    # 检查文件
    for file_name in required_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"✅ 文件存在: {file_name}")
        else:
            print(f"❌ 文件缺失: {file_name}")
    
    print()

def test_template_images():
    """测试模板图片"""
    print("🖼️ 测试模板图片...")
    
    if TEMPLATES_DIR.exists():
        image_files = list(TEMPLATES_DIR.glob("*.png"))
        if image_files:
            print(f"✅ 找到 {len(image_files)} 个模板图片")
            for img in image_files[:5]:  # 只显示前5个
                print(f"  - {img.name}")
            if len(image_files) > 5:
                print(f"  ... 还有 {len(image_files) - 5} 个文件")
        else:
            print("❌ 模板目录中没有图片文件")
    else:
        print("❌ 模板目录不存在")
    
    print()

def main():
    """主函数"""
    print("🧪 简单功能测试")
    print("=" * 40)
    
    # 运行测试
    success = True
    
    if not test_imports():
        success = False
    
    if not test_analyzer_creation():
        success = False
    
    if not test_feature_extractor():
        success = False
    
    test_directory_structure()
    test_template_images()
    
    # 总结
    print("=" * 40)
    if success:
        print("🎉 所有基本功能测试通过！")
        print("\n下一步:")
        print("1. 将PDF文件放入 input_pdfs 文件夹")
        print("2. 运行: python pdf_analyzer.py input_pdfs --mode recursive")
        print("3. 或运行: python usage_example.py")
    else:
        print("❌ 部分功能测试失败，请检查错误信息")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
