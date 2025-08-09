# PDF标准文档分类系统 - 使用指南

## 🚀 快速开始

### 1. 环境检查
```bash
python setup.py
```
此命令会自动检查和安装所有依赖项。

### 2. 验证系统功能
```bash
python test_features.py
```
测试模板特征提取功能，生成可视化结果。

### 3. 运行演示
```bash
python demo.py
```
查看完整的系统功能演示。

## 📂 处理PDF文件

### 基本使用
```bash
# 处理当前目录的PDF文件
python main.py

# 处理指定目录
python main.py C:\path\to\pdf\files

# 指定输出目录
python main.py --output-dir results C:\path\to\pdf\files
```

### 高级选项
```bash
# 设置处理超时时间（秒）
python main.py --timeout 30

# 使用自定义模板
python main.py --template my_template.png

# 详细输出模式
python main.py --verbose
```

## 📊 系统输出

### 1. 控制台输出
- 实时处理进度
- 每个文件的匹配结果
- 详细的失败原因
- 最终统计信息

### 2. 文件输出
- **jc/** 目录：匹配成功的PDF文件
- **pdf_classify.log**：详细处理日志
- **feature_visualization.png**：特征可视化图像

### 3. 匹配标准
系统使用评分机制（满分100分，及格线70分）：
- **颜色特征**（20分）：白底≥85%，黑字≥0.5%
- **区域检测**（15分）：检测到上/中/下三区域
- **关键框检测**（15分）：检测到6个红色标注框
- **关键词验证**（20分）：识别"标准"和"发布"关键字
- **位置关系**（15分）：框体位置符合模板要求
- **内容约束**（15分）：多行文本等格式要求

## 🔧 故障排除

### 常见问题

#### 1. Tesseract OCR错误
**问题**：提示Tesseract未找到
**解决**：
- Windows：下载安装 [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux：`sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- macOS：`brew install tesseract`

#### 2. 中文识别不准确
**问题**：关键词"标准"、"发布"识别失败
**解决**：
- 确保安装了中文语言包 `chi_sim`
- 检查PDF图像质量，建议300DPI以上
- 系统会自动尝试多种OCR配置

#### 3. 依赖包安装失败
**问题**：pip install失败
**解决**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 4. 内存不足
**问题**：处理大量PDF文件时内存溢出
**解决**：
- 分批处理PDF文件
- 调低超时时间：`--timeout 10`
- 关闭其他应用程序

### 性能优化

#### 1. 提高处理速度
- 只处理PDF前5页（系统默认）
- 使用SSD存储提高I/O速度
- 确保足够的内存（推荐8GB以上）

#### 2. 提高识别准确率
- 确保PDF清晰度足够（300DPI以上）
- 避免扫描件有倾斜或变形
- 检查PDF是否包含文本层

## 📈 系统监控

### 日志分析
查看 `pdf_classify.log` 文件了解详细处理信息：
```bash
# Windows
type pdf_classify.log

# Linux/macOS
cat pdf_classify.log
```

### 处理统计
系统会显示：
- 总处理文件数
- 成功匹配数量和文件列表
- 失败文件及具体原因
- 整体成功率

## 🎯 最佳实践

### 1. 文件组织
```
project/
├── input_pdfs/          # 待处理PDF文件
├── jc/                 # 匹配成功的文件（自动生成）
├── logs/               # 日志文件
└── templates/          # 自定义模板
```

### 2. 批量处理流程
1. 将PDF文件放入专用目录
2. 运行处理命令
3. 检查输出日志
4. 查看结果统计
5. 处理失败文件（可选）

### 3. 模板自定义
如需使用自定义模板：
1. 准备标注图像（参考mb6.png格式）
2. 确保包含蓝色区域框和红色关键框
3. 使用 `--template` 参数指定

## 📞 技术支持

### 系统信息
- Python版本要求：3.7+
- 主要依赖：OpenCV, Tesseract, pdf2image
- 支持平台：Windows, Linux, macOS

### 获取帮助
```bash
# 查看命令行帮助
python main.py --help

# 运行诊断
python demo.py

# 查看示例代码
python example_usage.py
```

### 版本信息
- 当前版本：2.0.0
- 模板版本：mb6.png
- 更新日期：2024年

## 🔄 更新升级

### 获取最新代码
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 迁移数据
升级时保留的文件：
- PDF文件和处理结果
- 自定义模板
- 配置文件

---

**注意**：首次使用建议先运行 `python demo.py` 熟悉系统功能。
