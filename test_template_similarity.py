#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模板相似度优化效果
"""

from pathlib import Path
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_new import StandardDocumentFeatureExtractor

def test_template_similarity():
    """测试模板相似度优化效果"""
    print("测试模板相似度优化效果")
    print("=" * 60)
    
    # 指定路径
    target_path = "E:\\1T硬盘D\\2个项目资料\\充电控制器\\办公\\国网控制器\\国网2.0控制器\\国网六统一\\发布版"
    
    print(f"目标路径: {target_path}")
    
    # 检查路径是否存在
    path = Path(target_path)
    if not path.exists():
        print(f"❌ 路径不存在: {target_path}")
        return
    
    print(f"✅ 路径存在")
    
    # 查找PDF文件
    try:
        pdf_files = list(path.rglob("*.pdf"))
        print(f"✅ 找到 {len(pdf_files)} 个PDF文件")
        
        if not pdf_files:
            print("❌ 未找到PDF文件")
            return
        
        # 显示前几个文件
        print("\n前5个PDF文件:")
        for i, pdf_file in enumerate(pdf_files[:5], 1):
            print(f"  {i}. {pdf_file.name}")
        
        # 测试前3个文件
        test_files = pdf_files[:3]
        results = []
        
        print(f"\n{'='*60}")
        print("开始测试模板相似度优化效果")
        print(f"{'='*60}")
        
        for i, pdf_path in enumerate(test_files, 1):
            print(f"\n测试文件 {i}/{len(test_files)}: {pdf_path.name}")
            print(f"完整路径: {pdf_path}")
            
            try:
                # 转换PDF第一页为图像
                import fitz
                import cv2
                import numpy as np
                from PIL import Image
                import io
                
                # 读取PDF第一页
                doc = fitz.open(str(pdf_path))
                if len(doc) > 0:
                    page = doc.load_page(0)
                    mat = fitz.Matrix(2.0, 2.0)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    
                    # 保存临时图像
                    temp_path = f"temp_test_{i}.png"
                    cv2.imwrite(temp_path, opencv_image)
                    
                    # 测试模板相似度
                    extractor = StandardDocumentFeatureExtractor(temp_path)
                    result = extractor.extract_features()
                    
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    doc.close()
                    
                    if 'error' not in result:
                        template_similarity = result.get('template_similarity', 0.0)
                        detected_features = result.get('detected_features', 0)
                        
                        results.append({
                            'file': pdf_path.name,
                            'template_similarity': template_similarity,
                            'detected_features': detected_features
                        })
                        
                        print(f"  模板相似度: {template_similarity:.3f}")
                        print(f"  检测特征数: {detected_features}/6")
                        
                        if template_similarity > 0.15:
                            print(f"  ✅ 模板相似度通过")
                        else:
                            print(f"  ❌ 模板相似度未通过")
                    else:
                        print(f"  ❌ 处理失败: {result['error']}")
                else:
                    print(f"  ❌ PDF文件为空")
                    
            except Exception as e:
                print(f"❌ 处理文件时出错: {e}")
        
        # 统计结果
        print(f"\n{'='*60}")
        print("模板相似度测试结果统计")
        print(f"{'='*60}")
        
        total_files = len(results)
        passed_files = sum(1 for r in results if r['template_similarity'] > 0.15)
        success_rate = passed_files / total_files * 100 if total_files > 0 else 0
        
        print(f"总文件数: {total_files}")
        print(f"模板相似度通过: {passed_files}")
        print(f"通过率: {success_rate:.1f}%")
        
        print(f"\n详细结果:")
        for result in results:
            status = "✅" if result['template_similarity'] > 0.15 else "❌"
            print(f"  {status} {result['file']} - 相似度: {result['template_similarity']:.3f}, 特征数: {result['detected_features']}/6")
        
        if success_rate >= 80:
            print(f"\n🎉 模板相似度优化效果良好！通过率: {success_rate:.1f}%")
        elif success_rate >= 50:
            print(f"\n⚠️  模板相似度优化效果一般，通过率: {success_rate:.1f}%")
        else:
            print(f"\n❌ 模板相似度优化效果较差，通过率: {success_rate:.1f}%")
            print("建议进一步调整模板匹配算法")
        
        print(f"\n优化说明:")
        print(f"  - 使用多尺度模板匹配")
        print(f"  - 采用多种匹配方法")
        print(f"  - 添加基于特征的备用相似度计算")
        print(f"  - 降低相似度阈值到0.15")
        
    except Exception as e:
        print(f"❌ 搜索PDF文件时出错: {e}")

if __name__ == "__main__":
    test_template_similarity() 