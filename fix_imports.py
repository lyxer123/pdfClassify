#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复tests目录下Python文件的导入问题
"""

import os
import re
from pathlib import Path

def fix_file_imports(file_path):
    """修复单个文件的导入问题"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修复导入路径问题
    # 1. 替换sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    content = re.sub(
        r'import sys\s*\nimport os\s*\nsys\.path\.append\(os\.path\.join\(os\.path\.dirname\(__file__\), \'\.\.\', \'\.\.\'\)\)',
        '# 导入测试包配置\nfrom tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR',
        content
    )
    
    # 2. 替换sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    content = re.sub(
        r'sys\.path\.append\(os\.path\.join\(os\.path\.dirname\(__file__\), \'\.\.\', \'\.\.\'\)\)',
        '# 导入测试包配置\nfrom tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR',
        content
    )
    
    # 3. 替换sys.path.insert(0, str(project_root))
    content = re.sub(
        r'# 添加项目根目录到Python路径\s*project_root = Path\(__file__\)\.parent\s*sys\.path\.insert\(0, str\(project_root\)\)',
        '# 导入测试包配置\nfrom tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR',
        content
    )
    
    # 4. 替换sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    content = re.sub(
        r'# 添加当前目录到路径\s*sys\.path\.insert\(0, os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)',
        '# 导入测试包配置\nfrom tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR',
        content
    )
    
    # 5. 替换sys.path.append(str(Path(__file__).parent))
    content = re.sub(
        r'# 添加项目根目录到路径\s*sys\.path\.append\(str\(Path\(__file__\)\.parent\)\)',
        '# 导入测试包配置\nfrom tests import PROJECT_ROOT, TEMPLATES_DIR, DATA_DIR',
        content
    )
    
    # 6. 替换tests/logs/路径
    content = re.sub(
        r'tests/logs/',
        'str(LOGS_DIR / \'',
        content
    )
    
    # 7. 替换../../templates/路径
    content = re.sub(
        r'\.\./\.\./templates/',
        'str(TEMPLATES_DIR / \'',
        content
    )
    
    # 8. 替换templates/路径（如果前面没有str(LOGS_DIR / '）
    content = re.sub(
        r'(?<!str\(LOGS_DIR / \')templates/',
        'str(TEMPLATES_DIR / \'',
        content
    )
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已修复")
        return True
    else:
        print(f"  - 无需修复")
        return False

def main():
    """主函数"""
    print("开始批量修复tests目录下的导入问题...")
    
    # 获取tests目录
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ tests目录不存在")
        return
    
    # 查找所有Python文件
    python_files = []
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(Path(root) / file)
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    # 修复每个文件
    fixed_count = 0
    for file_path in python_files:
        if fix_file_imports(file_path):
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main()
