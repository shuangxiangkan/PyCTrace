#!/usr/bin/env python3
"""
Python C API 调用提取测试脚本
手动输入 C 文件路径进行测试
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'C'))

from py_call_extractor import PythonCallExtractor, format_call_info_text, format_call_info_json


def analyze_c_file(file_path, show_json=False):
    """分析单个或多个 C 文件"""
    print("="*80)
    print("  Python C API 调用提取")
    print("="*80)
    
    if isinstance(file_path, str):
        file_paths = [file_path]
    else:
        file_paths = file_path
    
    print(f"\n分析文件:")
    for fp in file_paths:
        if not os.path.exists(fp):
            print(f"  ❌ 文件不存在: {fp}")
            return
        print(f"  - {fp}")
    
    print("\n正在分析...")
    extractor = PythonCallExtractor()
    result = extractor.parse_files(file_paths)
    
    print("\n" + "="*80)
    print("  分析摘要")
    print("="*80)
    print(f"总调用数: {result['total_calls']}")
    print(f"总函数数: {result['total_functions']}")
    print(f"全局函数: {', '.join(result['global_functions']) if result['global_functions'] else '无'}")
    
    print("\n" + "="*80)
    print("  提取结果（文本格式）")
    print("="*80)
    print(format_call_info_text(result))
    
    if show_json:
        print("\n" + "="*80)
        print("  提取结果（JSON格式）")
        print("="*80)
        print(format_call_info_json(result))
    
    print("="*80)
    print("✓ 分析完成！")
    print("="*80)


def interactive_mode():
    """交互式输入模式"""
    print("="*80)
    print("  Python C API 调用提取 - 交互模式")
    print("="*80)
    print()
    print("提示:")
    print("  - 输入单个 C 文件路径，例如: /path/to/file.c")
    print("  - 输入多个 C 文件路径（用空格分隔），例如: file1.c file2.c")
    print("  - 输入 'q' 退出")
    print()
    
    while True:
        user_input = input("请输入 C 文件路径: ").strip()
        
        if user_input.lower() == 'q':
            print("退出测试")
            break
        
        if not user_input:
            print("❌ 请输入有效的文件路径")
            continue
        
        file_paths = user_input.split()
        
        show_json = input("是否显示 JSON 格式? (y/n, 默认 n): ").strip().lower() == 'y'
        
        if len(file_paths) == 1:
            analyze_c_file(file_paths[0], show_json)
        else:
            analyze_c_file(file_paths, show_json)
        
        print()
        cont = input("继续测试? (y/n): ").strip().lower()
        if cont != 'y':
            print("退出测试")
            break
        print()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
        show_json = '--json' in file_paths
        
        if show_json:
            file_paths.remove('--json')
        
        if len(file_paths) == 1:
            analyze_c_file(file_paths[0], show_json)
        else:
            analyze_c_file(file_paths, show_json)
    else:
        interactive_mode()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()