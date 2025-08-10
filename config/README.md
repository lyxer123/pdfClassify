# 颜色阈值配置说明

本文档介绍如何使用PDF特征提取器的灵活颜色阈值配置功能。

## 概述

PDF特征提取器现在支持多种方式来配置颜色阈值参数，不再需要修改代码中的硬编码值。这提供了更大的灵活性和可维护性。

## 配置方式

### 1. 配置文件方式（推荐）

创建一个JSON配置文件来管理颜色阈值：

```json
{
    "color_thresholds": {
        "white_bg_min": 200,
        "black_text_max": 80,
        "bg_ratio_min": 0.95,
        "text_ratio_min": 0.001,
        "contrast_min": 26,
        "brightness_min": 244,
        "colored_text_max": 0.05
    },
    "description": {
        "white_bg_min": "白色背景最小RGB值",
        "black_text_max": "黑色文字最大RGB值",
        "bg_ratio_min": "背景色占比最小值",
        "text_ratio_min": "文字色占比最小值",
        "contrast_min": "最小对比度",
        "brightness_min": "最小亮度",
        "colored_text_max": "彩色文字最大允许比例"
    }
}
```

**使用方法：**
```bash
python pdf_feature_extractor.py input.pdf --config config/color_thresholds.json
```

### 2. 环境变量方式

通过设置环境变量来覆盖默认配置：

```bash
# Windows
set WHITE_BG_MIN=180
set BLACK_TEXT_MAX=100
set CONTRAST_MIN=20

# Linux/Mac
export WHITE_BG_MIN=180
export BLACK_TEXT_MAX=100
export CONTRAST_MIN=20
```

**支持的环境变量：**
- `WHITE_BG_MIN`: 白色背景最小RGB值
- `BLACK_TEXT_MAX`: 黑色文字最大RGB值
- `BG_RATIO_MIN`: 背景色占比最小值
- `TEXT_RATIO_MIN`: 文字色占比最小值
- `CONTRAST_MIN`: 最小对比度
- `BRIGHTNESS_MIN`: 最小亮度
- `COLORED_TEXT_MAX`: 彩色文字最大允许比例

### 3. 运行时更新

在Python代码中动态更新配置：

```python
from pdf_feature_extractor import PDFFeatureExtractor

# 创建特征提取器
extractor = PDFFeatureExtractor()

# 运行时更新配置
extractor.update_color_thresholds({
    'white_bg_min': 190,
    'black_text_max': 90,
    'contrast_min': 25
})

# 获取当前配置
current_config = extractor.get_color_thresholds()

# 重置为默认配置
extractor.reset_color_thresholds()

# 保存配置到文件
extractor.save_color_thresholds('my_config.json')
```

## 命令行参数

新增的命令行参数：

```bash
# 使用配置文件
python pdf_feature_extractor.py input.pdf --config config.json

# 显示当前配置
python pdf_feature_extractor.py --show-config

# 保存当前配置到文件
python pdf_feature_extractor.py --save-config my_config.json

# 组合使用
python pdf_feature_extractor.py input.pdf --config config.json --save-config backup.json
```

## 配置优先级

配置的优先级顺序（从高到低）：

1. **运行时更新** - `update_color_thresholds()` 方法
2. **环境变量** - 系统环境变量
3. **配置文件** - JSON配置文件
4. **默认值** - 代码中的硬编码默认值

## 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `white_bg_min` | int | 200 | 白色背景最小RGB值（0-255） |
| `black_text_max` | int | 80 | 黑色文字最大RGB值（0-255） |
| `bg_ratio_min` | float | 0.95 | 背景色占比最小值（0-1） |
| `text_ratio_min` | float | 0.001 | 文字色占比最小值（0-1） |
| `contrast_min` | int | 26 | 最小对比度 |
| `brightness_min` | int | 244 | 最小亮度（0-255） |
| `colored_text_max` | float | 0.05 | 彩色文字最大允许比例（0-1） |

## 使用建议

1. **开发环境**：使用环境变量快速调整参数
2. **测试环境**：使用配置文件管理不同的测试场景
3. **生产环境**：使用配置文件确保参数的一致性和可追溯性
4. **调试**：使用 `--show-config` 查看当前使用的参数值

## 示例文件

- `color_thresholds.json`: 标准配置文件
- `color_thresholds.env`: 环境变量示例文件
- `tests/root_tests/color_thresholds_example.py`: 完整使用示例

## 注意事项

1. 配置文件必须是有效的JSON格式
2. 环境变量值会被自动转换为适当的类型（int或float）
3. 无效的配置值会被忽略，使用默认值
4. 配置文件不存在时不会报错，会使用默认值
5. 运行时更新只影响当前实例，不会影响其他实例
