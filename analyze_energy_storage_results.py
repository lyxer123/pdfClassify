#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析储能PDF检测结果
"""

import json
import glob

def analyze_energy_storage_results():
    """分析储能PDF检测结果"""
    
    # 查找最新的结果文件
    result_files = glob.glob("energy_storage_first_pages_results_*.json")
    if not result_files:
        print("❌ 未找到储能检测结果文件")
        return
    
    # 使用最新的文件
    json_file = sorted(result_files)[-1]
    print(f"分析文件: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {json_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return
    
    # 基本统计信息
    print(f"\n📊 储能PDF检测统计:")
    print(f"  扫描时间: {data['scan_time']}")
    print(f"  源目录: {data['source_directory']}")
    print(f"  总文件数: {data['total_files']}")
    print(f"  成功文件数: {data['successful_files']}")
    print(f"  成功率: {data['success_rate']:.1f}%")
    
    # 分析每个文件的结果
    files = data['files']
    
    successful_files = []
    failed_files = []
    
    for file_info in files:
        if file_info.get('has_feature', False):
            successful_files.append(file_info)
        else:
            failed_files.append(file_info)
    
    print(f"\n🔍 详细分析:")
    print(f"  实际成功文件数: {len(successful_files)}")
    print(f"  实际失败文件数: {len(failed_files)}")
    print(f"  实际成功率: {len(successful_files)/len(files)*100:.1f}%")
    
    # 如果有失败的文件，分析失败原因
    if failed_files:
        print(f"\n❌ 未检测到两条长黑横线的文件 ({len(failed_files)}个):")
        print(f"{'序号':<4} {'文件名':<60} {'失败原因'}")
        print(f"{'-'*4} {'-'*60} {'-'*30}")
        
        failure_reasons = {}
        
        for i, file_info in enumerate(failed_files):
            file_name = file_info['file_name']
            if len(file_name) > 57:
                display_name = file_name[:54] + "..."
            else:
                display_name = file_name
            
            if 'error' in file_info:
                reason = f"错误: {file_info['error'][:20]}..."
            elif 'reason' in file_info:
                reason = file_info['reason']
                if len(reason) > 25:
                    reason = reason[:22] + "..."
            else:
                reason = "未知原因"
            
            print(f"{i+1:<4} {display_name:<60} {reason}")
            
            # 统计失败原因
            if 'error' in file_info:
                failure_type = "文件错误"
            elif 'reason' in file_info:
                if '只检测到1条长黑线' in file_info['reason']:
                    failure_type = "只有1条长黑线"
                elif '未检测到长黑线' in file_info['reason']:
                    failure_type = "无长黑线"
                elif '检测到0条长黑线' in file_info['reason']:
                    failure_type = "无长黑线"
                else:
                    failure_type = "其他原因"
            else:
                failure_type = "未知原因"
            
            if failure_type not in failure_reasons:
                failure_reasons[failure_type] = 0
            failure_reasons[failure_type] += 1
        
        print(f"\n📋 失败原因统计:")
        for reason, count in failure_reasons.items():
            print(f"  {reason}: {count}个文件")
    else:
        print(f"\n🎉 所有文件都成功检测到两条长黑横线！")
    
    # 分析成功文件的特征
    if successful_files:
        print(f"\n✅ 成功检测的文件分析:")
        
        # 统计线条位置分布
        first_line_positions = []
        second_line_positions = []
        distances = []
        width_ratios_1 = []
        width_ratios_2 = []
        
        for file_info in successful_files:
            first_line_positions.append(file_info['line1']['y_percent'])
            second_line_positions.append(file_info['line2']['y_percent'])
            distances.append(file_info['distance_ratio'] * 100)
            width_ratios_1.append(file_info['line1']['width_ratio'] * 100)
            width_ratios_2.append(file_info['line2']['width_ratio'] * 100)
        
        print(f"  第一条线位置: 平均{sum(first_line_positions)/len(first_line_positions):.1f}% (范围{min(first_line_positions):.1f}%-{max(first_line_positions):.1f}%)")
        print(f"  第二条线位置: 平均{sum(second_line_positions)/len(second_line_positions):.1f}% (范围{min(second_line_positions):.1f}%-{max(second_line_positions):.1f}%)")
        print(f"  间距: 平均{sum(distances)/len(distances):.1f}%高度 (范围{min(distances):.1f}%-{max(distances):.1f}%)")
        print(f"  第一条线宽度: 平均{sum(width_ratios_1)/len(width_ratios_1):.1f}%宽度 (范围{min(width_ratios_1):.1f}%-{max(width_ratios_1):.1f}%)")
        print(f"  第二条线宽度: 平均{sum(width_ratios_2)/len(width_ratios_2):.1f}%宽度 (范围{min(width_ratios_2):.1f}%-{max(width_ratios_2):.1f}%)")
        
        print(f"\n🎯 成功检测的文件 (共{len(successful_files)}个):")
        print(f"{'序号':<4} {'文件名':<60} {'第一条线':<15} {'第二条线':<15} {'间距'}")
        print(f"{'-'*4} {'-'*60} {'-'*15} {'-'*15} {'-'*10}")
        
        for i, file_info in enumerate(successful_files):
            file_name = file_info['file_name']
            if len(file_name) > 57:
                display_name = file_name[:54] + "..."
            else:
                display_name = file_name
            
            line1_info = f"{file_info['line1']['y_percent']:.0f}%({file_info['line1']['width_ratio']*100:.0f}%w)"
            line2_info = f"{file_info['line2']['y_percent']:.0f}%({file_info['line2']['width_ratio']*100:.0f}%w)"
            distance_info = f"{file_info['distance_ratio']*100:.0f}%h"
            
            print(f"{i+1:<4} {display_name:<60} {line1_info:<15} {line2_info:<15} {distance_info}")
    
    # 与充电PDF结果对比
    print(f"\n📈 与充电PDF对比:")
    print(f"  充电PDF: 117个文件，成功率100.0%")
    print(f"  储能PDF: {len(files)}个文件，成功率{len(successful_files)/len(files)*100:.1f}%")
    
    if len(successful_files)/len(files) < 1.0:
        print(f"  储能PDF的成功率较低，主要失败原因需要分析")
    else:
        print(f"  储能PDF也达到了100%成功率！")
    
    return successful_files, failed_files

if __name__ == "__main__":
    print("分析储能PDF文件检测结果")
    successful_files, failed_files = analyze_energy_storage_results()
