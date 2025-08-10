# Tests目录导入路径修复说明

## 问题描述

tests目录下的代码很多都是从根目录move过来的，存在以下问题：

1. **导入路径问题**：使用 `sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))` 来导入根目录模块
2. **相对路径问题**：模板文件路径使用 `../../templates/` 这样的相对路径
3. **日志文件路径问题**：日志文件路径指向 `tests/logs/`
4. **数据文件路径问题**：数据文件路径使用 `tests/data/` 等相对路径

## 解决方案

### 1. 创建统一的包配置

在 `tests/__init__.py` 中创建了统一的路径配置：

```python
# 获取项目根目录路径
def get_project_root():
    """获取项目根目录路径"""
    current_file = Path(__file__)
    return current_file.parent.parent

# 添加项目根目录到Python路径
PROJECT_ROOT = get_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 设置模板和数据的相对路径
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DATA_DIR = PROJECT_ROOT / "data"
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"
LOGS_DIR = PROJECT_ROOT / "tests" / "logs"
```

### 2. 统一导入方式

所有测试文件现在都使用统一的导入方式：

```python
# 导入测试包配置
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR

from main import PDFFeatureExtractor
from pdf_analyzer import UnifiedPDFAnalyzer
```

### 3. 路径引用修复

- **模板文件**：`str(TEMPLATES_DIR / 'mb.png')`
- **日志文件**：`str(LOGS_DIR / 'pdf_validation.log')`
- **数据文件**：`str(TEST_DATA_DIR / 'analysis.json')`

## 修复的文件列表

### 已修复的文件（17个）

#### adaptive_detection/
- `test_corrected_detection.py`
- `test_new_detection.py`
- `test_new_parameters.py`

#### feature_analysis/
- `analyze_mb10_upper.py`
- `scan_mb_full.py`
- `test_energy_storage.py`
- `test_mb9_detection.py`
- `usage_example.py`

#### line_detection/
- `analyze_correct_lines.py`
- `analyze_mb9_lines.py`
- `enhance_mb10_lines.py`

#### recursive_classify/
- `demo_recursive_classify.py`
- `quick_start.py`

#### validation/
- `batch_detect_charging_pdfs.py`
- `detect_energy_storage_first_pages.py`

#### visualization/
- `visualize_morphology_result.py`

### 无需修复的文件（9个）

这些文件在之前的修复中已经处理过了：
- `test_adaptive_detection.py`
- `analyze_additional_pdfs.py`
- `analyze_specified_pdfs.py`
- `analyze_standard_pdfs.py`
- `test_feature_extraction.py`
- `test_line_detection.py`
- `test_recursive_classify.py`
- `batch_validate_pdfs.py`
- `detect_charging_first_pages.py`

## 使用方法

### 1. 导入测试包配置

```python
from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR
```

### 2. 引用模板文件

```python
# 加载模板图片
template_img = np.array(Image.open(str(TEMPLATES_DIR / 'mb.png')).convert('RGB'))
```

### 3. 引用日志文件

```python
# 设置日志文件
logging.FileHandler(str(LOGS_DIR / 'pdf_validation.log'), encoding='utf-8')
```

### 4. 引用数据文件

```python
# 保存分析结果
output_path = TEST_DATA_DIR / 'analysis_result.json'
```

## 优势

1. **统一管理**：所有路径配置集中在一个地方
2. **跨平台兼容**：使用 `pathlib.Path` 确保跨平台兼容性
3. **易于维护**：修改路径只需要修改 `__init__.py` 文件
4. **清晰明确**：路径引用更加清晰明确，避免相对路径的混乱

## 注意事项

1. 确保在运行测试前已经正确设置了 `tests/__init__.py`
2. 所有测试文件都应该从 `tests` 包导入路径配置
3. 避免使用硬编码的相对路径
4. 使用 `str()` 转换 `Path` 对象，因为某些函数需要字符串路径

## 验证

可以通过以下命令验证修复是否成功：

```bash
# 测试包导入
python -c "from tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR; print('✓ 测试包导入成功')"

# 测试具体文件导入
python -c "from tests.feature_analysis.test_feature_extraction import load_template_image; print('✓ 测试文件导入成功')"
```
