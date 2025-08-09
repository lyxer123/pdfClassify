#!/bin/bash
echo "PDF标准文档分类系统"
echo "===================="

echo "检查环境..."
python3 setup.py

echo ""
echo "开始处理PDF文件..."
python3 main.py input_pdfs --output-dir jc

echo ""
echo "处理完成！"
echo "结果文件位于 jc 目录"
echo "日志文件：pdf_classify.log"
