# PDF特征提取器 - 页面选择模式功能

## 概述

PDF特征提取器现在支持多种页面选择模式，可以根据需要灵活选择要分析的PDF页面。

## 支持的页面选择模式

### 1. 前N页模式 (first_n) - 默认模式
- **功能**: 分析PDF的前N页
- **参数**: `--max-pages N` 指定页数
- **示例**: `--page-mode first_n --max-pages 5`

### 2. 第一页模式 (first_page)
- **功能**: 只分析PDF的第一页
- **参数**: 不需要 `--max-pages` 参数
- **示例**: `--page-mode first_page`

### 3. 所有页面模式 (all_pages)
- **功能**: 分析PDF的所有页面
- **参数**: 不需要 `--max-pages` 参数
- **示例**: `--page-mode all_pages`

### 4. 后N页模式 (last_n) - 新增功能
- **功能**: 分析PDF的后N页（从末尾开始）
- **参数**: `--max-pages N` 指定页数
- **示例**: `--page-mode last_n --max-pages 3`

## 使用方法

### 命令行使用

```bash
# 分析前5页
python pdf_feature_extractor.py input.pdf --page-mode first_n --max-pages 5

# 只分析第一页
python pdf_feature_extractor.py input.pdf --page-mode first_page

# 分析所有页面
python pdf_feature_extractor.py input.pdf --page-mode all_pages

# 分析后3页
python pdf_feature_extractor.py input.pdf --page-mode last_n --max-pages 3

# 处理文件夹中的所有PDF，每份分析后2页
python pdf_feature_extractor.py input_folder/ --page-mode last_n --max-pages 2
```

### 编程接口使用

```python
from pdf_feature_extractor import PDFFeatureExtractor

extractor = PDFFeatureExtractor()

# 分析前N页
result = extractor.process_pdf_file("input.pdf", max_pages=5, page_mode="first_n")

# 只分析第一页
result = extractor.process_pdf_file("input.pdf", page_mode="first_page")

# 分析所有页面
result = extractor.process_pdf_file("input.pdf", page_mode="all_pages")

# 分析后N页
result = extractor.process_pdf_file("input.pdf", max_pages=3, page_mode="last_n")
```

## 输出结果

每种模式都会在结果中包含以下信息：
- `page_mode`: 使用的页面选择模式
- `pages_analyzed`: 实际分析的页数
- `page_results`: 每页的分析结果，包含正确的页码信息

### 页码说明

- **first_n**: 页码从1开始递增 (1, 2, 3, ...)
- **first_page**: 页码为1
- **all_pages**: 页码从1开始递增 (1, 2, 3, ...)
- **last_n**: 页码从后往前计算，例如对于10页PDF的后3页，页码为8, 9, 10

## 注意事项

1. **后N页模式**: 如果PDF总页数少于指定的N页，会分析所有可用页面
2. **性能考虑**: 所有页面模式会处理整个PDF，对于大型PDF文件可能需要较长时间
3. **内存使用**: 处理更多页面会消耗更多内存
4. **错误处理**: 如果某页处理失败，会记录错误但继续处理其他页面

## 测试

可以使用提供的测试脚本验证功能：

```bash
python test_page_modes.py
```

确保 `input_pdfs/test.pdf` 文件存在。

## 兼容性

新功能完全向后兼容，如果不指定 `--page-mode` 参数，默认使用 `first_n` 模式，行为与之前版本一致。
