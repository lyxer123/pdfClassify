# PDF特征提取器测试说明

## 📋 测试概述

本测试套件用于验证 `pdf_feature_extractor.py` 的各项功能是否正常工作，包括：

1. **基本初始化功能** - 测试类的创建和基本参数设置
2. **颜色阈值管理功能** - 测试阈值的获取、更新、重置和保存
3. **PDF转换功能** - 测试PDF页面转换为图像的各种模式
4. **特征分析功能** - 测试颜色特征和第二特征（长黑线）的检测
5. **标准符合性检查** - 测试完整的标准符合性验证流程
6. **PDF文件处理功能** - 测试完整的PDF文件处理流程
7. **配置文件加载功能** - 测试从环境变量和JSON文件加载配置

## 🚀 运行测试

### 方法1: 使用批处理文件（Windows）
```bash
# 双击运行
tests\run_feature_extractor_test.bat

# 或在命令行中运行
cd tests
run_feature_extractor_test.bat
```

### 方法2: 使用PowerShell脚本（Windows）
```powershell
# 在PowerShell中运行
cd tests
.\run_feature_extractor_test.ps1
```

### 方法3: 直接运行Python脚本
```bash
cd tests
python test_pdf_feature_extractor.py
```

## 📁 测试文件结构

```
tests/
├── test_pdf_feature_extractor.py      # 主测试脚本
├── run_feature_extractor_test.bat     # Windows批处理文件
├── run_feature_extractor_test.ps1     # PowerShell脚本
├── FEATURE_EXTRACTOR_TEST_README.md   # 本说明文档
└── logs/                              # 测试日志目录
```

## 🔧 测试前准备

### 1. 确保Python环境
- Python 3.7+
- 已添加到PATH环境变量

### 2. 安装依赖包
```bash
pip install -r requirements.txt
```

主要依赖包：
- `opencv-python` - 图像处理和计算机视觉
- `numpy` - 数值计算
- `pillow` - 图像处理
- `PyMuPDF` - PDF文件处理

### 3. 准备测试PDF文件
确保在 `input_pdfs/` 文件夹中有 `test.pdf` 文件用于测试。

## 📊 测试结果解读

### 测试通过 ✅
- 所有功能模块正常工作
- 可以正常处理PDF文件
- 特征检测算法运行正常

### 测试失败 ❌
- 某个功能模块存在问题
- 可能需要检查依赖包安装
- 可能需要检查测试文件

### 测试警告 ⚠️
- 功能基本正常，但有小问题
- 可能需要调整参数设置

## 🐛 常见问题排查

### 1. 导入错误
```
ModuleNotFoundError: No module named 'cv2'
```
**解决方案**: 安装OpenCV
```bash
pip install opencv-python
```

### 2. PDF转换失败
```
PDF转换失败: 文件不存在
```
**解决方案**: 确保 `input_pdfs/test.pdf` 文件存在

### 3. 内存不足
```
MemoryError: 无法分配内存
```
**解决方案**: 减少测试的页面数量或降低图像分辨率

### 4. 权限错误
```
PermissionError: 拒绝访问
```
**解决方案**: 以管理员身份运行或检查文件权限

## 🔍 测试详细说明

### 测试1: 基本初始化功能
- 测试默认构造函数
- 测试自定义参数构造函数
- 测试基本属性访问

### 测试2: 颜色阈值管理功能
- 测试阈值获取和显示
- 测试阈值更新和验证
- 测试阈值重置
- 测试配置保存

### 测试3: PDF转换功能
- 测试不同页面模式：`first_n`, `first_page`, `all_pages`
- 验证图像转换质量
- 检查页面数量限制

### 测试4: 特征分析功能
- 测试颜色特征分析（白色背景、黑色文字、彩色文字、对比度）
- 测试第二特征检测（长黑线检测）
- 验证检测结果的准确性

### 测试5: 标准符合性检查
- 测试完整的标准验证流程
- 验证所有特征的组合判断
- 检查日志输出的完整性

### 测试6: PDF文件处理功能
- 测试完整的PDF处理流程
- 验证结果数据的完整性
- 检查错误处理机制

### 测试7: 配置文件加载功能
- 测试环境变量配置加载
- 测试JSON配置文件加载
- 验证配置合并逻辑

## 📈 性能指标

测试过程中会显示以下性能指标：
- 图像转换速度
- 特征检测时间
- 内存使用情况
- 处理成功率

## 🔄 持续测试

建议在以下情况下运行测试：
1. 安装新的依赖包后
2. 修改代码后
3. 更换环境后
4. 定期验证功能

## 📞 技术支持

如果遇到测试问题，请：
1. 检查错误日志
2. 验证环境配置
3. 查看依赖包版本
4. 提交Issue描述问题

---

**注意**: 测试过程中会生成临时文件，测试完成后会自动清理。
