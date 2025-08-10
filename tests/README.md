# 测试代码分类说明

本文件夹包含了按功能分类的测试代码和中间测试脚本。

## 文件夹结构

### 📏 `line_detection/` - 线条检测测试
包含线条检测算法的测试和改进代码：
- `test_line_detection.py` - 测试改进后的线条检测算法
- `analyze_mb9_lines.py` - 分析mb9.png的线条分布
- `analyze_correct_lines.py` - 分析正确线条的检测结果
- `enhance_mb10_lines.py` - 增强mb10线条检测

### 🔄 `adaptive_detection/` - 自适应检测测试
包含自适应检测算法的测试代码：
- `test_adaptive_detection.py` - 测试自适应长横线检测算法
- `test_corrected_detection.py` - 测试修正后的检测算法
- `test_new_detection.py` - 测试新的检测算法
- `test_new_parameters.py` - 测试新参数的检测效果

### 🔍 `feature_analysis/` - 特征分析测试
包含PDF特征分析的测试代码：
- `test_feature_extraction.py` - 测试特征提取功能
- `analyze_standard_pdfs.py` - 分析标准PDF特征
- `analyze_mb10_upper.py` - 分析mb10上部特征
- `analyze_additional_pdfs.py` - 分析额外PDF文件
- `analyze_specified_pdfs.py` - 分析指定PDF文件
- `analyze_non_compliant.py` - 分析不符合标准的PDF
- `scan_mb_full.py` - 扫描mb完整特征
- `test_mb9_detection.py` - 测试mb9检测
- `test_energy_storage.py` - 测试储能检测
- `usage_example.py` - 使用示例

### 🔄 `recursive_classify/` - 递归分类测试
包含递归PDF分类的测试代码：
- `test_recursive_classify.py` - 测试递归分类功能
- `demo_recursive_classify.py` - 递归分类演示
- `quick_start.py` - 快速启动脚本

### ✅ `validation/` - 验证测试
包含PDF验证的测试代码：
- `batch_validate_pdfs.py` - 批量验证PDF
- `detect_charging_first_pages.py` - 检测充电桩第一页
- `detect_energy_storage_first_pages.py` - 检测储能第一页
- `batch_detect_charging_pdfs.py` - 批量检测充电桩PDF

### 🎨 `visualization/` - 可视化测试
包含结果可视化的测试代码：
- `visualize_morphology_result.py` - 可视化形态学结果

## 使用说明

每个子文件夹都包含特定功能的测试代码。建议按需使用：

1. **开发新功能时**：在相应的功能文件夹中添加测试代码
2. **调试问题时**：使用对应的测试脚本验证功能
3. **性能优化时**：运行相关测试脚本对比改进效果

## 注意事项

- 这些测试代码主要用于开发和调试，生产环境请使用主程序
- 部分测试脚本可能需要特定的测试数据或模板文件
- 运行测试前请确保已安装所有依赖包
