# -*- coding: utf-8 -*-
"""
清理误判文件脚本
移除不符合标准文档要求的PDF文件
"""

import os
import shutil

def main():
    """主函数"""
    
    # 误判文件列表
    misclassified_files = [
        "南京市地下电动汽车库防火设计导则.pdf",
        "电动汽车充换电设施标准体系2016.pdf", 
        "电动汽车直流充电通信协议GB-T 27930-2015解读.pdf",
        "研发项目招采实施细则（试行）0630.pdf",
        "研发项目技术与决策评审实施细则（试行）0630.pdf",
        "解读国内首个电动汽车换电安全标准.pdf",
        "GB-T 34657－2017 电动汽车传导充电互操作性测试解决方案.pdf"
    ]
    
    # 检查目录
    target_dirs = ["jc", "jc_test", "jc_recursive"]
    
    print("🧹 清理误判的文件")
    print("="*50)
    
    total_removed = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
            
        print(f"\n📁 检查目录: {target_dir}")
        
        for filename in misclassified_files:
            file_path = os.path.join(target_dir, filename)
            if os.path.exists(file_path):
                try:
                    # 移动到误判文件夹而不是直接删除
                    misclassified_dir = "misclassified"
                    os.makedirs(misclassified_dir, exist_ok=True)
                    
                    # 生成唯一文件名
                    base_name, ext = os.path.splitext(filename)
                    counter = 1
                    new_filename = filename
                    while os.path.exists(os.path.join(misclassified_dir, new_filename)):
                        new_filename = f"{base_name}_{counter}{ext}"
                        counter += 1
                    
                    destination = os.path.join(misclassified_dir, new_filename)
                    shutil.move(file_path, destination)
                    print(f"  ✓ 移除: {filename}")
                    total_removed += 1
                except Exception as e:
                    print(f"  ✗ 移除失败 {filename}: {e}")
    
    print(f"\n📊 清理完成，共移除 {total_removed} 个误判文件")
    print(f"📁 误判文件已移动到 misclassified 目录")
    
    # 统计剩余的正确文件
    for target_dir in target_dirs:
        if os.path.exists(target_dir):
            remaining_files = [f for f in os.listdir(target_dir) if f.endswith('.pdf')]
            print(f"📋 {target_dir} 目录剩余 {len(remaining_files)} 个文件")

if __name__ == "__main__":
    main()
