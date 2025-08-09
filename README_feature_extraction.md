# PDF特征提取工具

## 功能描述

这个工具用于分析PDF文件的页面颜色特征，特别是检测PDF页面是否符合标准格式（白色背景+黑色文字）。工具以`templates/mb.png`作为标准模板参考。

## 主要特征

**第（1）个特征：页面整体颜色特征**
- 背景颜色：白色
- 文字颜色：黑色
- 如果不满足要求，则判定为不符合标准

## 文件结构

```
pdfClassify/
├── main.py                    # 主程序文件
├── usage_example.py           # 使用示例
├── templates/
│   └── mb.png                 # 标准模板图片
├── data/                      # 特征数据保存目录
├── input_pdfs/                # 输入PDF文件目录
└── requirements.txt           # 依赖包列表
```

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括：
- opencv-python: 图像处理
- numpy: 数值计算
- Pillow: 图像处理
- PyMuPDF: PDF处理
- pytesseract: OCR功能
- pdf2image: PDF转图片
- matplotlib: 可视化

## 使用方法

### 命令行使用

1. **处理单个PDF文件：**
```bash
python main.py path/to/your/file.pdf
```

2. **处理PDF文件夹：**
```bash
python main.py path/to/pdf/folder/
```

3. **自定义参数：**
```bash
python main.py input_pdfs/ --max-pages 3 --output my_analysis.json
```

### 命令行参数

- `input_path`: 输入PDF文件或文件夹路径（必需）
- `--max-pages`: 每个PDF最大处理页数（默认：5）
- `--template`: 标准模板图片路径（默认：templates/mb.png）
- `--output`: 输出文件名（可选）
- `--data-dir`: 数据保存目录（默认：data）

### Python代码使用

```python
from main import PDFFeatureExtractor

# 创建提取器实例
extractor = PDFFeatureExtractor()

# 处理单个PDF
result = extractor.process_pdf_file("sample.pdf", max_pages=3)
print(f"符合标准: {result['overall_compliance']}")

# 处理PDF文件夹
results = extractor.process_pdf_folder("input_pdfs/", max_pages=5)
print(f"符合标准的文件数: {results['summary']['compliant']}")

# 保存结果
extractor.save_results(results, "analysis_result.json")
```

## 特征检测算法

### 颜色特征分析

1. **白色背景检测**
   - 检测RGB值 >= 200的像素
   - 要求白色像素占比 >= 60%

2. **黑色文字检测**
   - 检测RGB值 <= 80的像素
   - 要求黑色像素占比 >= 10%

3. **整体亮度检查**
   - 要求RGB平均值 >= 180

4. **对比度检查**
   - 要求图像对比度 >= 50

### 符合性判定

只有当所有以下条件都满足时，才判定为符合标准：
- ✓ 白色背景比例充足
- ✓ 黑色文字比例适当
- ✓ 整体亮度达标
- ✓ 对比度充足

## 输出结果

### JSON格式结果

处理结果将保存为JSON格式，包含以下信息：

```json
{
  "folder_path": "input_pdfs/",
  "total_files": 3,
  "summary": {
    "compliant": 2,
    "non_compliant": 1,
    "errors": 0
  },
  "results": [
    {
      "file_name": "document1.pdf",
      "overall_compliance": true,
      "pages_analyzed": 3,
      "page_results": [
        {
          "page_number": 1,
          "compliance": true,
          "features": {
            "white_bg_ratio": 0.75,
            "black_text_ratio": 0.15,
            "contrast": 85.2,
            "mean_rgb": [230, 235, 240]
          }
        }
      ]
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### 特征数据

所有特征数据将自动保存到`data/`文件夹下，文件名格式为：
- `pdf_feature_analysis_YYYYMMDD_HHMMSS.json`

## 日志记录

程序运行过程中的详细日志将记录在：
- 控制台输出
- `pdf_classify.log`文件

## 使用示例

参考`usage_example.py`文件中的完整使用示例。

## 注意事项

1. 确保输入的PDF文件可以正常访问和读取
2. 程序会分析PDF的前几页（默认5页），可通过参数调整
3. 图像质量会影响特征检测准确性
4. 结果文件会自动保存到data目录，确保有写入权限

## 故障排除

如果遇到问题，请检查：
1. 是否正确安装了所有依赖包
2. PDF文件是否损坏或受密码保护
3. 文件路径是否正确
4. 是否有足够的磁盘空间和权限

查看日志文件`pdf_classify.log`获取详细错误信息。
