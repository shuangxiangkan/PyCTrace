#!/usr/bin/env python3
"""
PyCTrace - Python-C跨语言调用图错误检测工具
主程序入口
"""

import sys
import os
import argparse
from Utils import FileCollector
from C.c_parser import extract_python_strings


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="PyCTrace - Python-C跨语言调用图错误检测工具"
    )
    parser.add_argument(
        "directory", 
        help="要分析的项目目录路径"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在 - {args.directory}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"错误: 路径不是目录 - {args.directory}")
        sys.exit(1)
    
    print(f"正在分析目录: {os.path.abspath(args.directory)}")
    print("=" * 50)
    
    try:
        # 创建文件收集器
        collector = FileCollector()
        
        # 收集C和Python文件
        c_files, python_files = collector.collect_files(args.directory)
        
        # 显示结果
        if args.verbose:
            collector.print_file_summary(c_files, python_files)
        else:
            print(f"找到 {len(c_files)} 个C文件, {len(python_files)} 个Python文件")
        
        # 如果没有找到任何相关文件，给出提示
        if len(c_files) == 0 and len(python_files) == 0:
            print("警告: 未找到任何C或Python文件")
            return
        
        print("\n文件收集完成!")
        
        # 提取C文件中的字符串（特别是Python代码片段）
        if c_files:
            print("\n正在提取C文件中的Python代码片段...")
            print("=" * 50)
            
            for c_file in c_files:
                try:
                    python_snippets = extract_python_strings(c_file)
                    if python_snippets:
                        print(f"\n文件: {c_file}")
                        print("-" * 30)
                        print(f"提取的Python代码片段 ({len(python_snippets)} 个):")
                        for i, snippet in enumerate(python_snippets, 1):
                            print(f"\n{i}. Python代码片段:")
                            print("```python")
                            print(snippet)
                            print("```")
                    else:
                        print(f"\n文件: {c_file} - 未找到Python代码片段")
                        
                except Exception as e:
                    print(f"处理文件 {c_file} 时出错: {e}")
        
        print("\n字符串提取完成!")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()