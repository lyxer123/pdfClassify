#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器 - 9个特征检测结果
"""

import os
from main import StandardDocumentFeatureExtractor
from datetime import datetime

class TestReportGenerator:
    """
    测试报告生成器
    """
    
    def __init__(self):
        """
        初始化报告生成器
        """
        self.results = {}
        
    def test_image(self, image_path: str) -> dict:
        """
        测试单个图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            dict: 测试结果
        """
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f"文件不存在: {image_path}"
            }
        
        try:
            extractor = StandardDocumentFeatureExtractor(image_path)
            features = extractor.extract_features()
            
            if features:
                return {
                    'success': True,
                    'image_path': image_path,
                    'image_size': features.get('image_size'),
                    'total_features': features.get('total_features'),
                    'detected_features': features.get('detected_features'),
                    'detection_rate': features.get('detection_rate'),
                    'features': features.get('features', {}),
                    'horizontal_lines_count': features.get('horizontal_lines_count')
                }
            else:
                return {
                    'success': False,
                    'error': "特征提取失败"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"处理出错: {str(e)}"
            }
    
    def generate_report(self, image_paths: list) -> str:
        """
        生成测试报告
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            str: 报告内容
        """
        report = []
        report.append("=" * 80)
        report.append("标准文档9个特征检测测试报告")
        report.append("=" * 80)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试图片数量: {len(image_paths)}")
        report.append("")
        
        total_success = 0
        total_images = len(image_paths)
        
        for i, image_path in enumerate(image_paths, 1):
            report.append(f"【测试 {i}】: {image_path}")
            report.append("-" * 60)
            
            result = self.test_image(image_path)
            self.results[image_path] = result
            
            if result['success']:
                total_success += 1
                report.append(f"✓ 测试成功")
                report.append(f"  图片尺寸: {result['image_size']}")
                report.append(f"  横线数量: {result['horizontal_lines_count']}")
                report.append(f"  检测到的特征: {result['detected_features']}/{result['total_features']}")
                report.append(f"  检测率: {result['detection_rate']:.2%}")
                
                # 详细特征检测结果
                features = result['features']
                feature_names = [
                    ("feature_1_gb_icon", "1. GB图标"),
                    ("feature_2_national_standard_text", "2. 中华人民共和国国家标准"),
                    ("feature_3_standard_code", "3. 标准文号"),
                    ("feature_4_first_horizontal_line", "4. 第一横线"),
                    ("feature_5_standard_name", "5. 标准名称"),
                    ("feature_6_english_translation", "6. 英文翻译"),
                    ("feature_7_publication_date", "7. 发布日期"),
                    ("feature_8_second_horizontal_line", "8. 第二横线"),
                    ("feature_9_publishing_organization", "9. 发布机构")
                ]
                
                report.append("  详细检测结果:")
                for feature_key, feature_name in feature_names:
                    feature = features.get(feature_key, {})
                    status = "✓" if feature.get('detected', False) else "✗"
                    position = feature.get('position', '未检测到')
                    report.append(f"    {feature_name}: {status} {position}")
                
            else:
                report.append(f"✗ 测试失败: {result['error']}")
            
            report.append("")
        
        # 总结
        report.append("=" * 80)
        report.append("测试总结")
        report.append("=" * 80)
        report.append(f"总图片数: {total_images}")
        report.append(f"成功检测: {total_success}")
        report.append(f"失败数量: {total_images - total_success}")
        report.append(f"成功率: {total_success/total_images:.2%}")
        
        if total_success > 0:
            avg_detection_rate = sum(
                r['detection_rate'] for r in self.results.values() 
                if r['success']
            ) / total_success
            report.append(f"平均检测率: {avg_detection_rate:.2%}")
        
        report.append("")
        report.append("结论:")
        if total_success == total_images:
            report.append("✓ 所有图片都成功检测到9个特征，系统表现优秀！")
        elif total_success > 0:
            report.append("⚠ 部分图片检测成功，系统需要进一步优化。")
        else:
            report.append("✗ 所有图片检测失败，系统需要重新设计。")
        
        return "\n".join(report)
    
    def save_report(self, report_content: str, filename: str = "test_report.txt"):
        """
        保存报告到文件
        
        Args:
            report_content: 报告内容
            filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"测试报告已保存到: {filename}")

def main():
    """
    主函数
    """
    print("标准文档9个特征检测测试")
    print("=" * 50)
    
    # 测试图片列表
    test_images = ["mb.png", "mb2.png"]
    
    # 创建报告生成器
    generator = TestReportGenerator()
    
    # 生成报告
    report = generator.generate_report(test_images)
    
    # 打印报告
    print(report)
    
    # 保存报告
    generator.save_report(report)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 