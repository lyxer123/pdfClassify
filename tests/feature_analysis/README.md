# 特征分析测试

本文件夹包含PDF特征分析的测试代码，用于分析和提取PDF文档的各种特征。

## 文件说明

### `test_feature_extraction.py`
测试PDF特征提取功能，验证特征提取的准确性和完整性。

**功能**：
- 测试文本特征提取
- 测试图像特征提取
- 测试表格特征提取
- 验证特征提取质量

**使用方法**：
```bash
python test_feature_extraction.py
```

### `analyze_standard_pdfs.py`
分析标准PDF文档的特征，建立特征基准。

**功能**：
- 分析标准PDF的结构特征
- 提取关键信息特征
- 建立特征数据库
- 生成特征分析报告

**使用方法**：
```bash
python analyze_standard_pdfs.py
```

### `analyze_mb10_upper.py`
分析mb10文档上部的特征，专注于特定区域的特征提取。

**功能**：
- 分析文档上部区域
- 提取关键特征信息
- 识别重要内容区域
- 生成区域特征报告

**使用方法**：
```bash
python analyze_mb10_upper.py
```

### `analyze_additional_pdfs.py`
分析额外的PDF文档，扩展特征数据库。

**功能**：
- 分析新的PDF文档
- 提取新的特征类型
- 更新特征数据库
- 对比不同文档的特征

**使用方法**：
```bash
python analyze_additional_pdfs.py
```

### `analyze_specified_pdfs.py`
分析指定的PDF文档，针对特定需求进行特征分析。

**功能**：
- 分析用户指定的PDF
- 提取特定类型的特征
- 生成定制化分析报告
- 满足特定分析需求

**使用方法**：
```bash
python analyze_specified_pdfs.py
```

### `analyze_non_compliant.py`
分析不符合标准的PDF文档，识别问题特征。

**功能**：
- 识别非标准PDF
- 分析问题特征
- 生成问题报告
- 提供改进建议

**使用方法**：
```bash
python analyze_non_compliant.py
```

### `scan_mb_full.py`
扫描mb文档的完整特征，进行全面分析。

**功能**：
- 全面扫描文档特征
- 提取所有相关信息
- 生成完整特征报告
- 建立文档特征档案

**使用方法**：
```bash
python scan_mb_full.py
```

### `test_mb9_detection.py`
测试mb9文档的检测功能，验证检测算法。

**功能**：
- 测试mb9检测算法
- 验证检测准确性
- 分析检测结果
- 优化检测参数

**使用方法**：
```bash
python test_mb9_detection.py
```

### `test_energy_storage.py`
测试能源存储相关PDF的检测和分析。

**功能**：
- 测试能源存储PDF检测
- 提取能源存储特征
- 分析存储系统信息
- 生成能源分析报告

**使用方法**：
```bash
python test_energy_storage.py
```

### `usage_example.py`
提供特征分析的使用示例，展示各种功能。

**功能**：
- 展示特征提取用法
- 提供代码示例
- 演示分析流程
- 帮助用户快速上手

**使用方法**：
```bash
python usage_example.py
```

## 特征类型

### 文本特征
- 标题和章节结构
- 关键词和术语
- 文本内容和格式
- 语言和编码信息

### 图像特征
- 图片和图表
- 线条和形状
- 颜色和纹理
- 图像质量信息

### 结构特征
- 页面布局
- 表格结构
- 列表和编号
- 文档层次结构

### 元数据特征
- 文档属性
- 创建和修改信息
- 作者和版本信息
- 安全设置

## 依赖要求

- PyPDF2 或 pdfplumber
- PIL (Pillow)
- NumPy
- matplotlib (可视化)
- pandas (数据分析)

## 输出格式

分析结果以JSON格式保存，包含：
- 特征提取结果
- 分析统计信息
- 问题识别报告
- 可视化图表

## 注意事项

- 确保PDF文档可访问且格式正确
- 大型文档分析可能需要较长时间
- 特征提取结果会保存到data文件夹
- 建议定期清理临时文件
