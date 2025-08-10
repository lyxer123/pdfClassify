#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复tests目录下Python文件中剩余的路径问题
"""

import os
import re
from pathlib import Path

def fix_remaining_paths(file_path):
    """修复单个文件中剩余的路径问题"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修复模板路径问题
    # 1. 修复 'str(TEMPLATES_DIR / 'mb.png') 格式
    content = re.sub(
        r"'str\(TEMPLATES_DIR / '([^']+)'\)",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 2. 修复 'str(TEMPLATES_DIR / 'mb.png') 格式（没有引号的情况）
    content = re.sub(
        r"'str\(TEMPLATES_DIR / ([^']+)'\)",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 3. 修复日志文件路径
    content = re.sub(
        r"'tests/logs/([^']+)'",
        r"str(LOGS_DIR / '\1')",
        content
    )
    
    # 4. 修复相对路径的模板引用
    content = re.sub(
        r"'\.\./\.\./templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 5. 修复相对路径的模板引用（没有引号的情况）
    content = re.sub(
        r"'\.\./\.\./templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 6. 修复 'templates/mb.png' 格式
    content = re.sub(
        r"'templates/([^']+)'",
        r"str(TEMPLATES_DIR / '\1')",
        content
    )
    
    # 7. 修复 tests/data/ 路径
    content = re.sub(
        r"'tests/data/([^']+)'",
        r"str(TEST_DATA_DIR / '\1')",
        content
    )
    
    # 8. 修复 jc/ 路径（如果需要的话）
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
    print("开始修复tests目录下Python文件中剩余的路径问题...")
    
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
        if fix_remaining_paths(file_path):
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main()
