# -*- coding: utf-8 -*-
import os
import time
import json
from datetime import datetime
from pdf_processor import PDFProcessor

def monitor_processing():
    """监控处理状态"""
    print("PDF处理监控系统启动...")
    
    while True:
        # 检查输入目录
        input_dir = "input_pdfs"
        if os.path.exists(input_dir):
            pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
            print(f"待处理PDF文件数: {len(pdf_files)}")
            
            if pdf_files:
                print("发现新文件，开始自动处理...")
                processor = PDFProcessor()
                results = processor.batch_process(input_dir, "jc")
                
                # 记录处理结果
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "total_files": results['total_files'],
                    "successful_files": results['successful_files'],
                    "failed_files": results['failed_files']
                }
                
                with open(f"reports/processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                    json.dump(report, f, indent=2)
                
                print(f"处理完成: {results['successful_files']}/{results['total_files']} 成功")
        
        time.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    monitor_processing()
