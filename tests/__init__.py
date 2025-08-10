#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF分类测试包
统一管理测试代码的导入路径和配置
"""

import os
import sys
from pathlib import Path

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

# 确保必要的目录存在
for dir_path in [TEMPLATES_DIR, DATA_DIR, TEST_DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# 导出常用路径
__all__ = [
    'PROJECT_ROOT',
    'TEMPLATES_DIR', 
    'DATA_DIR',
    'TEST_DATA_DIR',
    'LOGS_DIR'
]
