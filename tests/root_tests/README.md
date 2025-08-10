# Root Tests 目录

这个目录包含了从项目根目录移动过来的测试和使用示例文件。

## 文件说明

### 测试文件
- **test_simple.py** - 基本功能测试脚本，验证项目的基本功能是否正常
- **test_unified_analyzer.py** - 专门测试统一PDF分析器的功能

### 使用示例文件
- **usage_example.py** - PDF分析器的使用示例，展示如何使用各种功能

## 使用方法

### 运行基本测试
```bash
cd tests/root_tests
python test_simple.py
```

### 运行统一分析器测试
```bash
cd tests/root_tests
python test_unified_analyzer.py
```

### 查看使用示例
```bash
cd tests/root_tests
python usage_example.py
```

## 路径修复说明

这些文件已经从项目根目录移动到tests目录下，并已修复了所有路径问题：

1. **导入路径** - 使用 `from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR` 替代相对路径
2. **文件路径** - 使用 `PROJECT_ROOT / "input_pdfs"` 等绝对路径
3. **模板路径** - 使用 `TEMPLATES_DIR` 常量

## 注意事项

- 运行这些文件时，确保在tests目录下执行
- 所有路径都使用tests包提供的常量，确保跨平台兼容性
- 这些文件主要用于开发和测试，生产环境请使用主程序

