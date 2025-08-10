#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复tests目录下Python文件的导入和路径问题
合并了fix_imports.py和fix_remaining_paths.py的功能
"""

import os
import re
from pathlib import Path

def fix_file_paths(file_path):
    """修复单个文件的导入和路径问题"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # ===== 修复导入路径问题 =====
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
    
    # ===== 修复路径问题 =====
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
    
    # 9. 修复 'str(TEMPLATES_DIR / 'mb.png') 格式
    content = re.sub(
        r"'str\(TEMPLATES_DIR / '([^']+)'\)",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 10. 修复 'str(TEMPLATES_DIR / 'mb.png') 格式（没有引号的情况）
    content = re.sub(
        r"'str\(TEMPLATES_DIR / ([^']+)'\)",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 11. 修复日志文件路径
    content = re.sub(
        r"'tests/logs/([^']+)'",
        r"str(LOGS_DIR / '\1')",
        content
    )
    
    # 12. 修复相对路径的模板引用
    content = re.sub(
        r"'\.\./\.\./templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 13. 修复相对路径的模板引用（没有引号的情况）
    content = re.sub(
        r"'\.\./\.\./templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 14. 修复 'templates/mb.png' 格式
    content = re.sub(
        r"'templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 15. 修复 tests/data/ 路径
    content = re.sub(
        r"'tests/data/([^']+)'",
        r"str(TEST_DATA_DIR / '\1')",
        content
    )
    
    # 16. 修复 jc/ 路径（如果需要的话）
    content = re.sub(
        r"'jc/([^']+)'",
        r"str(PROJECT_ROOT / 'jc' / '\1')",
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
    print("开始批量修复tests目录下的导入和路径问题...")
    print("此脚本合并了fix_imports.py和fix_remaining_paths.py的功能")
    
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
        if fix_file_paths(file_path):
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")
    print("提示：此脚本已合并了之前两个fix文件的所有功能")

if __name__ == "__main__":
    main()

