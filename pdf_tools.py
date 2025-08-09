# -*- coding: utf-8 -*-
"""
PDF标准文档分类系统 - 工具集合
基于mb81/82/83特征的标准文档智能识别
包含单文件测试、四步检查分析、批量清理、监控等功能
"""

import os
import sys
import time
import json
import shutil
import logging
import subprocess
import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pdf_processor import PDFProcessor

def setup_logging(log_file="pdf_tools.log"):
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

def test_single_pdf(pdf_path, verbose=True):
    """
    测试单个PDF文件
    
    Args:
        pdf_path: PDF文件路径
        verbose: 是否显示详细信息
    """
    if verbose:
        print(f"测试PDF文件: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 {pdf_path}")
        return None
    
    try:
        # 初始化处理器
        processor = PDFProcessor()
        if verbose:
            print("PDF处理器初始化成功")
        
        # 处理PDF
        result = processor.process_pdf(pdf_path, timeout=30)
        
        if verbose:
            print(f"\n处理结果:")
            print(f"  成功: {result['success']}")
            print(f"  原因: {result['reason']}")
            print(f"  处理时间: {result['processing_time']:.2f}秒")
            
            # 显示特征信息（用于调试）
            if hasattr(processor, '_last_features'):
                features = processor._last_features
                _print_feature_analysis(features)
            elif result['features']:
                _print_feature_analysis(result['features'])
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()
        return None

def _print_feature_analysis(features):
    """打印新的四步特征分析结果"""
    print(f"\n🔍 四步检查结果:")
    
    # 第一步：页面颜色
    step1 = features.get('step1_colors', {})
    step1_status = '✓' if step1.get('valid', False) else '✗'
    print(f"  第一步 (页面颜色): {step1_status}")
    if step1.get('details'):
        details = step1['details']
        print(f"    白背景: {details.get('white_ratio', 0)*100:.1f}%, 黑字: {details.get('black_ratio', 0)*100:.1f}%")
        print(f"    原因: {step1.get('reason', '未知')}")
    
    # 第二步：横线检测
    step2 = features.get('step2_lines', {})
    step2_status = '✓' if step2.get('valid', False) else '✗'
    print(f"  第二步 (横线检测): {step2_status}")
    if step2.get('details'):
        details = step2['details']
        print(f"    检测横线数: {details.get('total_lines', 0)}, 距离比例: {details.get('distance_ratio', 0)*100:.1f}%")
        print(f"    原因: {step2.get('reason', '未知')}")
    
    # 第三步：三区划分
    step3 = features.get('step3_regions', {})
    step3_status = '✓' if step3.get('valid', False) else '✗'
    print(f"  第三步 (三区划分): {step3_status}")
    if step3.get('ratios'):
        ratios = step3['ratios']
        print(f"    上部: {ratios.get('upper_ratio', 0)*100:.1f}%, 中部: {ratios.get('middle_ratio', 0)*100:.1f}%, 下部: {ratios.get('lower_ratio', 0)*100:.1f}%")
        print(f"    原因: {step3.get('reason', '未知')}")
    
    # 第四步：局部细节
    step4 = features.get('step4_details', {})
    step4_status = '✓' if step4.get('valid', False) else '✗'
    print(f"  第四步 (局部细节): {step4_status}")
    if step4.get('details'):
        details = step4['details']
        for region_name, region_detail in details.items():
            if region_detail.get('found_items'):
                print(f"    {region_name}: {', '.join(region_detail['found_items'])}")
        print(f"    原因: {step4.get('reason', '未知')}")
    
    # 总体结果
    final_result = features.get('final_result', False)
    if final_result:
        print(f"\n✅ 总体验证: 通过 - {features.get('success_reason', '')}")
    else:
        print(f"\n❌ 总体验证: 失败 - {features.get('failure_reason', '未知原因')}")


def clean_misclassified_files(target_dirs=None, misclassified_files=None):
    """
    清理误判文件
    
    Args:
        target_dirs: 目标目录列表
        misclassified_files: 误判文件列表
    """
    if target_dirs is None:
        target_dirs = ["jc", "jc_test", "jc_recursive", "jc_improved"]
    
    if misclassified_files is None:
        # 默认误判文件列表
        misclassified_files = [
            "南京市地下电动汽车库防火设计导则.pdf",
            "电动汽车充换电设施标准体系2016.pdf", 
            "电动汽车直流充电通信协议GB-T 27930-2015解读.pdf",
            "研发项目招采实施细则（试行）0630.pdf",
            "研发项目技术与决策评审实施细则（试行）0630.pdf",
            "解读国内首个电动汽车换电安全标准.pdf",
            "GB-T 34657－2017 电动汽车传导充电互操作性测试解决方案.pdf"
        ]
    
    print("🧹 清理误判的文件")
    print("="*50)
    
    total_removed = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
            
        print(f"\n📁 检查目录: {target_dir}")
        
        for filename in misclassified_files:
            file_path = os.path.join(target_dir, filename)
            if os.path.exists(file_path):
                try:
                    # 移动到误判文件夹而不是直接删除
                    misclassified_dir = "misclassified"
                    os.makedirs(misclassified_dir, exist_ok=True)
                    
                    # 生成唯一文件名
                    base_name, ext = os.path.splitext(filename)
                    counter = 1
                    new_filename = filename
                    while os.path.exists(os.path.join(misclassified_dir, new_filename)):
                        new_filename = f"{base_name}_{counter}{ext}"
                        counter += 1
                    
                    destination = os.path.join(misclassified_dir, new_filename)
                    shutil.move(file_path, destination)
                    print(f"  ✓ 移除: {filename}")
                    total_removed += 1
                except Exception as e:
                    print(f"  ✗ 移除失败 {filename}: {e}")
    
    print(f"\n📊 清理完成，共移除 {total_removed} 个误判文件")
    print(f"📁 误判文件已移动到 misclassified 目录")
    
    # 统计剩余的正确文件
    for target_dir in target_dirs:
        if os.path.exists(target_dir):
            remaining_files = [f for f in os.listdir(target_dir) if f.endswith('.pdf')]
            print(f"📋 {target_dir} 目录剩余 {len(remaining_files)} 个文件")

def count_pdf_files(root_dir):
    """统计PDF文件数量"""
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                count += 1
    return count

def scan_drive_recursive(drive_path, output_dir="jc", confirm_required=True):
    """
    递归扫描指定驱动器的PDF文件
    
    Args:
        drive_path: 驱动器路径，如 "I:\\"
        output_dir: 输出目录
        confirm_required: 是否需要用户确认
    """
    setup_logging("drive_scan.log")
    logger = logging.getLogger(__name__)
    
    print(f"🔍 {drive_path} PDF标准文档递归扫描系统")
    print("="*50)
    
    # 检查驱动器是否存在
    if not os.path.exists(drive_path):
        logger.error(f"{drive_path} 不存在或无法访问")
        print(f"❌ {drive_path} 不存在或无法访问")
        return None
    
    print(f"📁 扫描目录: {drive_path}")
    print("🔄 正在统计PDF文件数量...")
    
    # 统计PDF文件总数
    total_pdfs = count_pdf_files(drive_path)
    print(f"📊 发现 {total_pdfs} 个PDF文件")
    
    if total_pdfs == 0:
        print("⚠️  未找到PDF文件")
        return None
    
    # 确认是否继续
    if confirm_required:
        confirm = input(f"\n是否继续处理 {total_pdfs} 个PDF文件？这可能需要很长时间。(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return None
    
    # 初始化PDF处理器
    print("\n🚀 初始化PDF处理器...")
    try:
        processor = PDFProcessor()
        logger.info("PDF处理器初始化成功")
        print("✅ PDF处理器初始化成功")
    except Exception as e:
        logger.error(f"PDF处理器初始化失败: {e}")
        print(f"❌ PDF处理器初始化失败: {e}")
        return None
    
    # 开始批量处理
    start_time = time.time()
    print(f"\n📋 开始递归处理 {drive_path} 所有PDF文件...")
    print(f"📂 输出目录: {output_dir}")
    print("⏱️  处理开始时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        results = processor.batch_process(drive_path, output_dir, recursive=True)
        
        # 处理完成
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n" + "="*50)
        print("🎯 处理完成！")
        print("="*50)
        print(f"📊 处理结果统计:")
        print(f"   总文件数: {results['total_files']}")
        print(f"   匹配成功: {results['successful_files']}")
        print(f"   匹配失败: {results['failed_files']}")
        print(f"   成功率: {results['successful_files']/results['total_files']*100:.1f}%" if results['total_files'] > 0 else "   成功率: 0%")
        print(f"   总处理时间: {processing_time/60:.1f} 分钟")
        
        # 显示成功文件
        if results['successful_paths']:
            print(f"\n✅ 匹配成功的文件 ({len(results['successful_paths'])} 个):")
            for i, path in enumerate(results['successful_paths'][:10], 1):  # 只显示前10个
                print(f"   {i}. {os.path.basename(path)}")
            
            if len(results['successful_paths']) > 10:
                print(f"   ... 还有 {len(results['successful_paths']) - 10} 个文件")
            
            print(f"\n📁 所有匹配的文件已复制到: {output_dir}")
        else:
            print("\n⚠️  没有文件匹配标准模板")
        
        # 显示失败统计
        if results['failed_reasons']:
            print(f"\n❌ 常见失败原因:")
            reason_count = {}
            for reason in results['failed_reasons'].values():
                reason_count[reason] = reason_count.get(reason, 0) + 1
            
            for reason, count in sorted(reason_count.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {reason}: {count} 个文件")
        
        logger.info(f"扫描完成，成功匹配 {results['successful_files']} 个文件")
        return results
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断处理")
        logger.info("用户中断扫描")
        return None
    except Exception as e:
        print(f"\n❌ 处理过程中发生错误: {e}")
        logger.error(f"扫描失败: {e}")
        return None

def monitor_processing(input_dir="input_pdfs", output_dir="jc", check_interval=30, reports_dir="data"):
    """
    监控处理系统
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        check_interval: 检查间隔（秒）
        reports_dir: 报告目录（存储在data目录中）
    """
    print("PDF处理监控系统启动...")
    
    # 确保报告目录存在
    os.makedirs(reports_dir, exist_ok=True)
    
    while True:
        try:
            # 检查输入目录
            if os.path.exists(input_dir):
                pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 待处理PDF文件数: {len(pdf_files)}")
                
                if pdf_files:
                    print("发现新文件，开始自动处理...")
                    processor = PDFProcessor()
                    results = processor.batch_process(input_dir, output_dir)
                    
                    # 记录处理结果
                    report = {
                        "timestamp": datetime.now().isoformat(),
                        "total_files": results['total_files'],
                        "successful_files": results['successful_files'],
                        "failed_files": results['failed_files'],
                        "successful_paths": results['successful_paths'],
                        "failed_reasons": results['failed_reasons']
                    }
                    
                    report_file = os.path.join(reports_dir, f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    with open(report_file, "w", encoding="utf-8") as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                    
                    print(f"处理完成: {results['successful_files']}/{results['total_files']} 成功")
                    print(f"报告已保存: {report_file}")
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n监控系统已停止")
            break
        except Exception as e:
            print(f"监控过程中发生错误: {e}")
            time.sleep(check_interval)

def create_deployment_config(config_file="deployment_config.json"):
    """
    创建部署配置文件
    
    Args:
        config_file: 配置文件名
    """
    config = {
        "version": "2.0.0",
        "deployment_date": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": {
            "input_directory": "./input_pdfs",
            "output_directory": "./jc", 
            "template_file": "./templates/mb6.png",
            "log_file": "./pdf_classify.log"
        },
        "processing_settings": {
            "timeout_seconds": 15,
            "max_pages_per_pdf": 5,
            "dpi_resolution": 300,
            "validation_threshold": 50
        },
        "ocr_settings": {
            "language": "chi_sim",
            "configs": [
                "--psm 6 -l chi_sim",
                "--psm 7 -l chi_sim", 
                "--psm 8 -l chi_sim",
                "--psm 13 -l chi_sim"
            ]
        }
    }
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 部署配置文件已创建: {config_file}")
    return config

def create_directory_structure():
    """创建标准目录结构"""
    directories = [
        "input_pdfs",      # 输入PDF目录
        "jc",              # 匹配成功输出目录
        "templates",       # 自定义模板目录
        "data"             # 数据目录（包含日志、报告、备份等）
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 复制模板文件
    # 如果mb6.png在根目录，移动到templates目录
    if os.path.exists("mb6.png") and not os.path.exists("templates/mb6.png"):
        shutil.copy2("mb6.png", "templates/mb6.png")
        print("✅ 模板文件已复制到templates目录")

def create_batch_scripts():
    """创建批处理脚本"""
    
    # 增强版Windows批处理脚本
    windows_script = """@echo off
chcp 65001 >nul

echo ========================================
echo    PDF标准文档分类系统 - 部署版
echo ========================================
echo.

echo [1/3] 检查环境配置...
python setup.py
if errorlevel 1 (
    echo 错误：环境检查失败，请检查Python和依赖包安装
    pause
    exit /b 1
)
echo ✓ 环境检查完成
echo.

echo [2/3] 开始处理PDF文件...
echo 输入目录：input_pdfs
echo 输出目录：jc
echo.
python main.py input_pdfs --output-dir jc --verbose
if errorlevel 1 (
    echo 错误：PDF处理失败
    pause
    exit /b 1
)

echo.
echo [3/3] 处理完成！
echo ========================================
echo ✓ 匹配成功的PDF文件已复制到 jc 目录
echo ✓ 详细日志请查看 pdf_classify.log
echo ✓ 可视化结果：feature_visualization.png
echo ========================================
echo.
echo 按任意键退出...
pause >nul
"""
    
    with open("run_classification_deploy.bat", "w", encoding="utf-8") as f:
        f.write(windows_script)
    
    # Linux/macOS脚本
    unix_script = """#!/bin/bash
echo "========================================"
echo "   PDF标准文档分类系统 - 部署版"
echo "========================================"
echo

echo "[1/3] 检查环境..."
python3 setup.py
if [ $? -ne 0 ]; then
    echo "错误：环境检查失败"
    exit 1
fi
echo "✓ 环境检查完成"
echo

echo "[2/3] 开始处理PDF文件..."
echo "输入目录：input_pdfs"
echo "输出目录：jc"
echo
python3 main.py input_pdfs --output-dir jc --verbose
if [ $? -ne 0 ]; then
    echo "错误：PDF处理失败"
    exit 1
fi

echo
echo "[3/3] 处理完成！"
echo "========================================"
echo "✓ 匹配成功的PDF文件已复制到 jc 目录"
echo "✓ 详细日志请查看 pdf_classify.log"
echo "✓ 可视化结果：feature_visualization.png"
echo "========================================"
"""
    
    with open("run_classification_deploy.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)
    
    # 设置执行权限（Linux/macOS）
    try:
        os.chmod("run_classification_deploy.sh", 0o755)
    except:
        pass
    
    print("✅ 部署批处理脚本已创建:")
    print("   Windows: run_classification_deploy.bat")
    print("   Linux/macOS: run_classification_deploy.sh")

def deploy_production_environment():
    """
    一键部署到生产环境
    """
    print("🚀 PDF标准文档分类系统 - 快速部署")
    print("="*50)
    
    print("\n📦 创建部署配置...")
    config = create_deployment_config()
    
    print("\n📁 创建目录结构...")
    create_directory_structure()
    
    print("\n📝 创建批处理脚本...")
    create_batch_scripts()
    
    print("\n🎉 部署完成！")
    print("="*50)
    print("📋 下一步操作：")
    print("1. 将PDF文件放入 input_pdfs/ 目录")
    print("2. 运行批处理脚本开始处理")
    print("3. 查看 jc/ 目录中的结果文件")
    print("4. 查看 pdf_classify.log 了解处理详情")
    
    print("\n💡 快速开始：")
    if sys.platform.startswith('win'):
        print("双击运行: run_classification_deploy.bat")
    else:
        print("命令行运行: ./run_classification_deploy.sh")
    
    print(f"\n⚙️ 配置文件：deployment_config.json")
    print(f"📅 部署时间：{config['deployment_date']}")
    print(f"🐍 Python版本：{config['python_version']}")
    
    return config

def install_service(service_name="pdf-classifier"):
    """
    安装系统服务
    
    Args:
        service_name: 服务名称
    """
    if sys.platform.startswith('win'):
        print("正在安装Windows服务...")
        print("服务安装功能需要管理员权限")
        print("请手动创建计划任务或使用任务计划程序")
        print("命令示例:")
        print(f"  schtasks /create /tn \"{service_name}\" /tr \"python {os.path.join(os.getcwd(), 'pdf_tools.py')} monitor\" /sc minute /mo 1")
    else:
        print("创建Linux systemd服务...")
        service_content = f"""[Unit]
Description=PDF Standard Document Classification Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'your_username')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} pdf_tools.py monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = f"{service_name}.service"
        with open(service_file, "w") as f:
            f.write(service_content)
        
        print(f"✅ systemd服务文件已创建: {service_file}")
        print("安装命令:")
        print(f"  sudo cp {service_file} /etc/systemd/system/")
        print(f"  sudo systemctl enable {service_name}")
        print(f"  sudo systemctl start {service_name}")

def load_deployment_config(config_file="deployment_config.json"):
    """
    加载部署配置文件
    
    Args:
        config_file: 配置文件名
        
    Returns:
        配置字典
    """
    if not os.path.exists(config_file):
        print(f"⚠️  配置文件 {config_file} 不存在，创建默认配置...")
        return create_deployment_config(config_file)
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"✅ 已加载配置文件: {config_file}")
        return config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        print("创建默认配置...")
        return create_deployment_config(config_file)

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 1. 初始化PDF处理器
    try:
        # 尝试找到模板文件
        template_path = "templates/mb6.png" if os.path.exists("templates/mb6.png") else "mb6.png"
        processor = PDFProcessor(template_path=template_path)
        print("✓ PDF处理器初始化完成")
    except Exception as e:
        print(f"✗ PDF处理器初始化失败: {e}")
        return False
    
    # 2. 检查模板特征
    if os.path.exists(template_path):
        try:
            import cv2
            template_image = cv2.imread(template_path)
            features = processor._extract_features(template_image)
            is_valid = processor._validate_features(features)
            print(f"✓ 模板特征验证: {'通过' if is_valid else '失败'}")
        except Exception as e:
            print(f"✗ 模板特征验证失败: {e}")
    else:
        print("⚠️  模板文件不存在")
    
    # 3. 批量处理示例（如果有PDF文件）
    test_dir = "."  # 当前目录
    output_dir = "jc"
    
    try:
        results = processor.batch_process(test_dir, output_dir)
        print(f"✓ 批量处理完成:")
        print(f"  - 总文件数: {results['total_files']}")
        print(f"  - 成功匹配: {results['successful_files']}")
        print(f"  - 匹配失败: {results['failed_files']}")
        return True
    except Exception as e:
        print(f"✗ 批量处理失败: {e}")
        return False

def example_single_pdf():
    """单个PDF处理示例"""
    print("\n=== 单个PDF处理示例 ===")
    
    # 查找第一个PDF文件
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("未找到PDF文件，跳过单个PDF处理示例")
        return
    
    pdf_path = pdf_files[0]
    print(f"处理文件: {pdf_path}")
    
    try:
        processor = PDFProcessor()
        result = processor.process_pdf(pdf_path)
        
        print(f"处理结果: {'成功' if result['success'] else '失败'}")
        print(f"处理时间: {result['processing_time']:.2f} 秒")
        print(f"结果说明: {result['reason']}")
        
        # 如果处理成功，显示特征摘要
        if result['success'] and result['features']:
            features = result['features']
            print(f"\n📝 特征摘要:")
            print(f"   白色背景: {features.get('white_ratio', 0)*100:.1f}%")
            print(f"   检测区域: {len(features.get('regions', {}))}/3")
            print(f"   检测框数: {len(features.get('key_boxes', {}))}/6")
            
            keywords = features.get('keywords', {})
            keyword_count = sum(1 for v in keywords.values() if v)
            print(f"   关键词匹配: {keyword_count}/{len(keywords)}")
            
    except Exception as e:
        print(f"✗ 单个PDF处理失败: {e}")

def example_feature_extraction():
    """特征提取示例"""
    print("\n=== 特征提取示例 ===")
    
    # 检查模板文件
    template_path = "templates/mb6.png" if os.path.exists("templates/mb6.png") else "mb6.png"
    if not os.path.exists(template_path):
        print("模板文件不存在，跳过特征提取示例")
        return
    
    try:
        import cv2
        
        # 加载模板图像
        template_image = cv2.imread(template_path)
        print(f"模板图像尺寸: {template_image.shape}")
        
        # 提取特征
        processor = PDFProcessor()
        features = processor._extract_features(template_image)
        
        # 显示主要特征
        print(f"白色背景占比: {features.get('white_ratio', 0)*100:.1f}%")
        print(f"黑色文字占比: {features.get('black_ratio', 0)*100:.1f}%")
        print(f"检测到的区域数: {len(features.get('regions', {}))}")
        print(f"检测到的关键框数: {len(features.get('key_boxes', {}))}")
        
        # 关键词检测
        keywords = features.get('keywords', {})
        if keywords:
            print(f"\n关键词检测结果:")
            for keyword, found in keywords.items():
                print(f"  {keyword}: {'✓' if found else '✗'}")
        
        # 模板验证
        is_valid = processor._validate_features(features)
        print(f"\n模板验证结果: {'✅ 通过' if is_valid else '❌ 不通过'}")
        
    except Exception as e:
        print(f"✗ 特征提取失败: {e}")

def run_examples():
    """运行所有使用示例"""
    print("PDF标准文档分类系统 - 使用示例")
    print("="*50)
    
    success_count = 0
    total_examples = 3
    
    try:
        # 基本使用示例
        if example_basic_usage():
            success_count += 1
        
        # 单个PDF处理示例
        example_single_pdf()
        success_count += 1
        
        # 特征提取示例
        example_feature_extraction()
        success_count += 1
        
        print(f"\n=== 示例运行完成 ===")
        print(f"成功运行: {success_count}/{total_examples} 个示例")
        print("更多使用方法请参考 README.md")
        
        return success_count == total_examples
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        print("请检查依赖项是否正确安装")
        return False

# ==================== 环境检查功能 (来自setup.py) ====================

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python依赖包安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python依赖包安装失败")
        return False

def check_tesseract():
    """检查Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR版本: {version}")
        return True
    except Exception as e:
        print("❌ Tesseract OCR未正确安装")
        print("请手动安装Tesseract OCR:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("  macOS: brew install tesseract")
        return False

def check_pdf_backends():
    """检查PDF处理后端"""
    print("\n🔧 检查PDF处理后端...")
    
    backends = []
    
    # 检查pdf2image和poppler
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image 可用")
        backends.append("pdf2image")
    except ImportError:
        print("❌ pdf2image 未安装")
    
    # 检查PyMuPDF
    try:
        import fitz
        print("✅ PyMuPDF 可用")
        backends.append("PyMuPDF")
    except ImportError:
        print("❌ PyMuPDF 未安装")
    
    if not backends:
        print("❌ 没有可用的PDF处理后端")
        print("请安装: pip install PyMuPDF 或安装poppler")
        return False
    else:
        print(f"✅ 可用的PDF后端: {', '.join(backends)}")
        return True

def test_installation():
    """测试安装"""
    print("\n🔧 测试安装...")
    
    try:
        from pdf_processor import PDFProcessor
        print("✅ PDF处理器模块导入成功")
        
        # 检查模板文件
        template_path = "templates/mb6.png" if os.path.exists("templates/mb6.png") else "mb6.png"
        if os.path.exists(template_path):
            processor = PDFProcessor()
            print("✅ PDF处理器初始化成功")
        else:
            print("⚠️  模板文件templates/mb6.png不存在，某些功能可能无法使用")
        
        return True
    except Exception as e:
        print(f"❌ 安装测试失败: {e}")
        return False

def setup_environment():
    """环境安装和检查"""
    print("🚀 PDF标准文档分类系统安装向导")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_requirements():
        print("请手动运行: pip install -r requirements.txt")
        return
    
    # 检查Tesseract
    check_tesseract()
    
    # 检查PDF后端
    check_pdf_backends()
    
    # 创建目录
    directories = ["jc", "input_pdfs", "templates", "data"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 测试安装
    if test_installation():
        print("\n🎉 安装完成！")
        print("\n📖 使用方法:")
        print("  python main.py              # 处理当前目录PDF")
        print("  python pdf_tools.py test-features # 测试特征提取")
        print("  python main.py --demo       # 运行演示")
        print("  python pdf_tools.py examples # 查看使用示例")
    else:
        print("\n❌ 安装未完全成功，请检查错误信息并重新安装")

# ==================== 特征可视化功能 (来自test_features.py) ====================

def visualize_features(image, features, output_path="feature_visualization.png"):
    """
    可视化特征提取结果
    
    Args:
        image: 原始图像
        features: 提取的特征
        output_path: 输出路径
    """
    # 创建图像副本用于标注
    vis_image = image.copy()
    height, width = image.shape[:2]
    
    # 标注区域
    regions = features.get('regions', {})
    if 'upper' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['upper']['y']), 
                     (width, regions['upper']['y'] + regions['upper']['height']),
                     (255, 0, 0), 3)  # 蓝色
        cv2.putText(vis_image, 'UPPER', (10, regions['upper']['y'] + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    if 'middle' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['middle']['y']), 
                     (width, regions['middle']['y'] + regions['middle']['height']),
                     (0, 255, 0), 3)  # 绿色
        cv2.putText(vis_image, 'MIDDLE', (10, regions['middle']['y'] + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    if 'lower' in regions:
        cv2.rectangle(vis_image, 
                     (0, regions['lower']['y']), 
                     (width, regions['lower']['y'] + regions['lower']['height']),
                     (0, 0, 255), 3)  # 红色
        cv2.putText(vis_image, 'LOWER', (10, regions['lower']['y'] + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # 标注关键框
    key_boxes = features.get('key_boxes', {})
    colors = [(255, 255, 0), (255, 0, 255), (0, 255, 255), 
              (128, 255, 128), (255, 128, 128), (128, 128, 255)]
    
    for i, (box_name, box_info) in enumerate(key_boxes.items()):
        if i < len(colors):
            color = colors[i]
            x, y, w, h = box_info['x'], box_info['y'], box_info['w'], box_info['h']
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(vis_image, box_name.upper(), (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # 保存可视化结果
    cv2.imwrite(output_path, vis_image)
    print(f"可视化结果已保存到: {output_path}")

def test_features_extraction():
    """测试特征提取功能（来自test_features.py的功能）"""
    print("开始测试特征提取功能...")
    
    # 检查模板文件
    template_path = "templates/mb6.png" if os.path.exists("templates/mb6.png") else "mb6.png"
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在（已检查 templates/mb6.png 和 mb6.png）")
        return
    
    # 初始化PDF处理器
    try:
        processor = PDFProcessor(template_path=template_path)
        print("PDF处理器初始化成功")
    except Exception as e:
        print(f"PDF处理器初始化失败: {e}")
        return
    
    # 加载模板图像
    template_image = cv2.imread(template_path)
    if template_image is None:
        print("模板图像加载失败")
        return
    
    print(f"模板图像大小: {template_image.shape[1]}x{template_image.shape[0]}")
    
    # 提取特征
    print("\n正在提取特征...")
    features = processor._extract_features(template_image)
    
    # 详细显示新的四步特征信息
    print("="*60)
    print("新的四步特征提取分析结果")
    print("="*60)
    
    # 使用新的四步特征分析
    _print_feature_analysis(features)
    
    # 详细的四步分析
    print("\n【详细四步分析】")
    
    # 第一步详细信息
    step1 = features.get('step1_colors', {})
    print(f"第一步 (页面颜色检查): {'✓ 通过' if step1.get('valid', False) else '✗ 失败'}")
    print(f"原因: {step1.get('reason', '未知')}")
    if step1.get('details'):
        details = step1['details']
        print(f"白色背景占比: {details.get('white_ratio', 0)*100:.1f}%")
        print(f"黑色文字占比: {details.get('black_ratio', 0)*100:.1f}%")
        print(f"红色标注占比: {details.get('red_ratio', 0)*100:.1f}%")
    
    # 第二步详细信息
    step2 = features.get('step2_lines', {})
    print(f"\n第二步 (2条黑色长横线检测): {'✓ 通过' if step2.get('valid', False) else '✗ 失败'}")
    print(f"原因: {step2.get('reason', '未知')}")
    if step2.get('details'):
        details = step2['details']
        print(f"检测到的横线数: {details.get('total_lines', 0)}")
        if details.get('line1_length') and details.get('line2_length'):
            print(f"第一条线长度: {details['line1_length']:.0f}px")
            print(f"第二条线长度: {details['line2_length']:.0f}px")
            print(f"两横线间距占比: {details.get('distance_ratio', 0)*100:.1f}%")
    
    # 第三步详细信息
    step3 = features.get('step3_regions', {})
    print(f"\n第三步 (三个部分划分): {'✓ 通过' if step3.get('valid', False) else '✗ 失败'}")
    print(f"原因: {step3.get('reason', '未知')}")
    if step3.get('regions'):
        regions = step3['regions']
        for region_name, region_info in regions.items():
            print(f"{region_name}部: y={region_info['y']}, 高度={region_info['height']}px")
    if step3.get('ratios'):
        ratios = step3['ratios']
        print(f"上部高度占比: {ratios.get('upper_ratio', 0)*100:.1f}%")
        print(f"中部高度占比: {ratios.get('middle_ratio', 0)*100:.1f}%")
        print(f"下部高度占比: {ratios.get('lower_ratio', 0)*100:.1f}%")
    
    # 第四步详细信息
    step4 = features.get('step4_details', {})
    print(f"\n第四步 (每个部分局部细节): {'✓ 通过' if step4.get('valid', False) else '✗ 失败'}")
    print(f"原因: {step4.get('reason', '未知')}")
    if step4.get('details'):
        details = step4['details']
        for region_name, region_detail in details.items():
            print(f"\n{region_name}部检查:")
            print(f"  状态: {'✓ 通过' if region_detail.get('valid', False) else '✗ 失败'}")
            print(f"  原因: {region_detail.get('reason', '未知')}")
            if region_detail.get('found_items'):
                print(f"  找到的项目: {', '.join(region_detail['found_items'])}")
    
    # 总体验证
    print(f"\n【总体验证结果】")
    final_result = features.get('final_result', False)
    if final_result:
        print(f"总体验证: ✓ 通过")
        print(f"成功原因: {features.get('success_reason', '所有四步检查均通过')}")
    else:
        print(f"总体验证: ✗ 失败")
        print(f"失败原因: {features.get('failure_reason', '未知原因')}")
    
    # 显示新的验证逻辑说明
    print("\n【验证逻辑说明】")
    print("新的验证方法采用四步逐次判断：")
    print("1. 页面颜色检查：白底黑字，排除红色标注")
    print("2. 2条黑色长横线：横线数量=2，间距>=65%，长度>=70%")
    print("3. 三个部分划分：上部<=30%，中部>=50%，下部<=30%")
    print("4. 局部细节检查：上部有标准，中部有发布+实施，下部有发布")
    print("必须四步全部通过才被认定为标准文件。")
    
    # 生成可视化结果
    print("\n正在生成可视化结果...")
    visualize_features(template_image, features)
    
    print("\n特征提取测试完成！")
    print("="*60)

def main():
    """主函数 - 命令行工具"""
    if len(sys.argv) < 2:
        print("🚀 PDF标准文档分类系统 - 工具集 (mb81/82/83版本)")
        print("="*60)
        print("使用方法:")
        print("  python pdf_tools.py test <PDF文件路径>          # 测试单个PDF")
        print("  python pdf_tools.py clean                       # 清理误判文件")
        print("  python pdf_tools.py scan <驱动器路径>           # 递归扫描驱动器")
        print("  python pdf_tools.py monitor                     # 启动监控服务")
        print("  python pdf_tools.py deploy                      # 一键部署到生产环境")
        print("  python pdf_tools.py config                      # 创建/加载配置文件")
        print("  python pdf_tools.py examples                    # 运行使用示例")
        print("  python pdf_tools.py install-service             # 安装系统服务")
        print("  python pdf_tools.py setup                       # 环境检查和安装")
        print("  python pdf_tools.py test-features               # 测试新的四步特征提取")
        print("\n新特性: 四步逐次判断 - 颜色→横线→三区→细节")
        return
    
    command = sys.argv[1].lower()
    
    if command == "test":
        if len(sys.argv) != 3:
            print("用法: python pdf_tools.py test <PDF文件路径>")
            print("示例: python pdf_tools.py test 'example.pdf'")
            return
        test_single_pdf(sys.argv[2])
    
    elif command == "clean":
        clean_misclassified_files()
    
    elif command == "scan":
        if len(sys.argv) != 3:
            print("用法: python pdf_tools.py scan <驱动器路径>")
            print("示例: python pdf_tools.py scan I:\\")
            return
        scan_drive_recursive(sys.argv[2])
    
    elif command == "monitor":
        print("启动监控服务...")
        print("按 Ctrl+C 停止监控")
        monitor_processing()
    
    elif command == "deploy":
        deploy_production_environment()
    
    elif command == "config":
        config_file = sys.argv[2] if len(sys.argv) > 2 else "deployment_config.json"
        config = load_deployment_config(config_file)
        print(f"\n📋 当前配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    elif command == "examples":
        run_examples()
    
    elif command == "install-service":
        install_service()
    
    elif command == "setup":
        setup_environment()
    
    elif command == "test-features":
        test_features_extraction()
    
    else:
        print(f"未知命令: {command}")
        print("运行 'python pdf_tools.py' 查看可用命令")

if __name__ == "__main__":
    main()
