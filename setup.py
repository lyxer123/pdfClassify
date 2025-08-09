# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统安装脚本
"""

import os
import sys
import subprocess

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python依赖包安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python依赖包安装失败")
        return False

def check_tesseract():
    """检查Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR版本: {version}")
        return True
    except Exception as e:
        print("❌ Tesseract OCR未正确安装")
        print("请手动安装Tesseract OCR:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("  macOS: brew install tesseract")
        return False

def create_directories():
    """创建必要目录"""
    directories = ["jc", "input_pdfs", "templates", "data"]
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 创建目录: {dir_name}")

def check_pdf_backends():
    """检查PDF处理后端"""
    print("\n🔧 检查PDF处理后端...")
    
    backends = []
    
    # 检查pdf2image和poppler
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image 可用")
        backends.append("pdf2image")
    except ImportError:
        print("❌ pdf2image 未安装")
    
    # 检查PyMuPDF
    try:
        import fitz
        print("✅ PyMuPDF 可用")
        backends.append("PyMuPDF")
    except ImportError:
        print("❌ PyMuPDF 未安装")
    
    if not backends:
        print("❌ 没有可用的PDF处理后端")
        print("请安装: pip install PyMuPDF 或安装poppler")
        return False
    else:
        print(f"✅ 可用的PDF后端: {', '.join(backends)}")
        return True

def test_installation():
    """测试安装"""
    print("\n🔧 测试安装...")
    
    try:
        from pdf_processor import PDFProcessor
        print("✅ PDF处理器模块导入成功")
        
        if os.path.exists("templates/mb6.png"):
            processor = PDFProcessor()
            print("✅ PDF处理器初始化成功")
        elif os.path.exists("mb6.png"):
            processor = PDFProcessor()
            print("✅ PDF处理器初始化成功")
        else:
            print("⚠️  模板文件templates/mb6.png不存在，某些功能可能无法使用")
        
        return True
    except Exception as e:
        print(f"❌ 安装测试失败: {e}")
        return False

def main():
    """主安装函数"""
    print("🚀 PDF标准文档分类系统安装向导")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_requirements():
        print("请手动运行: pip install -r requirements.txt")
        return
    
    # 检查Tesseract
    check_tesseract()
    
    # 检查PDF后端
    check_pdf_backends()
    
    # 创建目录
    create_directories()
    
    # 测试安装
    if test_installation():
        print("\n🎉 安装完成！")
        print("\n📖 使用方法:")
        print("  python main.py              # 处理当前目录PDF")
        print("  python test_features.py     # 测试特征提取")
        print("  python main.py --demo       # 运行演示")
        print("  python pdf_tools.py examples # 查看使用示例")
    else:
        print("\n❌ 安装未完全成功，请检查错误信息并重新安装")

if __name__ == "__main__":
    main()
