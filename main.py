"""
PyCTrace - Python和C代码分析工具
从C/C++代码中提取Python代码片段并分析调用关系
"""

import sys
import os
import argparse
from Utils import FileCollector
from Utils.graph_visualizer import generate_call_graph_visualization
from C.c_parser import extract_python_strings, CCodeParser
from Python.python_parser import PythonCodeParser


def main():
    parser = argparse.ArgumentParser(description="PyCTrace - Python和C代码分析工具")
    parser.add_argument("directory", help="要分析的目录路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)
    
    try:
        # 收集文件
        collector = FileCollector()
        c_files, python_files = collector.collect_files(args.directory)
        
        print(f"在目录 '{args.directory}' 中找到 {len(c_files)} 个C/C++文件，{len(python_files)} 个Python文件")
        
        if args.verbose:
            print("\nC/C++文件列表:")
            for file in c_files:
                print(f"  - {file}")
            print("\nPython文件列表:")
            for file in python_files:
                print(f"  - {file}")
        
        # 首先分析C文件并生成调用图
        if c_files:
            print("\n正在分析C文件并生成调用图...")
            print("=" * 50)
            
            try:
                # 创建C代码解析器
                c_parser = CCodeParser()
                
                # 分析每个C文件
                for c_file in c_files:
                    try:
                        print(f"\n分析文件: {c_file}")
                        print("-" * 30)
                        
                        # 解析C文件
                        parse_result = c_parser.parse_file(c_file)
                        
                        if args.verbose:
                            print(f"发现的函数: {parse_result['functions']}")
                            print(f"函数调用关系: {parse_result['calls']}")
                        
                        # 生成调用图可视化
                        file_basename = os.path.splitext(os.path.basename(c_file))[0]
                        filename_prefix = f"c_call_graph_{file_basename}"
                        title = f"C Call Graph - {os.path.basename(c_file)}"
                        
                        generate_call_graph_visualization(
                            parse_result['call_graph'],
                            filename_prefix=filename_prefix,
                            title=title,
                            verbose=args.verbose
                        )
                            
                    except Exception as e:
                        print(f"处理文件 {c_file} 时出错: {e}")
                        
            except Exception as e:
                print(f"分析C文件时出错: {e}")
        else:
            print("\n未找到C文件，跳过C调用图分析")

        # 然后处理Python文件
        if python_files:
            print(f"\n正在分析 {len(python_files)} 个独立的Python文件...")
            print("=" * 50)
            
            try:
                # 创建Python代码解析器
                python_parser = PythonCodeParser()
                
                # 分析每个Python文件
                for python_file in python_files:
                    try:
                        print(f"\n分析Python文件: {python_file}")
                        print("-" * 30)
                        
                        # 解析Python文件
                        parse_result = python_parser.parse_file(python_file)
                        
                        if args.verbose:
                            print(f"发现的函数: {parse_result['functions']}")
                            print(f"函数调用关系: {parse_result['calls']}")
                        
                        # 生成调用图可视化
                        file_basename = os.path.splitext(os.path.basename(python_file))[0]
                        filename_prefix = f"python_call_graph_{file_basename}"
                        title = f"Python Call Graph - {os.path.basename(python_file)}"
                        
                        generate_call_graph_visualization(
                            parse_result['call_graph'],
                            filename_prefix=filename_prefix,
                            title=title,
                            verbose=args.verbose
                        )
                            
                    except Exception as e:
                        print(f"处理Python文件 {python_file} 时出错: {e}")
                        
            except Exception as e:
                print(f"分析Python文件时出错: {e}")
        else:
            # 只有在没有独立Python文件时才从C文件中提取Python代码片段
            print("\n未找到独立的Python文件，正在从C文件中提取Python代码片段...")
            print("=" * 50)
            
            all_python_snippets = []
            
            for c_file in c_files:
                try:
                    python_snippets = extract_python_strings(c_file)
                    if python_snippets:
                        print(f"\n从 {c_file} 中提取到 {len(python_snippets)} 个Python代码片段")
                        if args.verbose:
                            for i, snippet in enumerate(python_snippets, 1):
                                print(f"  片段 {i}:")
                                print(f"    {snippet[:100]}{'...' if len(snippet) > 100 else ''}")
                        all_python_snippets.extend(python_snippets)
                    else:
                        if args.verbose:
                            print(f"\n从 {c_file} 中未找到Python代码片段")
                except Exception as e:
                    print(f"处理文件 {c_file} 时出错: {e}")
            
            print(f"\n总共提取到 {len(all_python_snippets)} 个Python代码片段")
            
            # 分析Python代码片段
            if all_python_snippets:
                print("\n正在分析Python代码片段...")
                print("=" * 50)
                
                try:
                    # 创建Python代码解析器
                    python_parser = PythonCodeParser()
                    
                    # 合并所有Python代码片段
                    combined_code = "\n\n".join(all_python_snippets)
                    
                    # 解析代码并生成调用图
                    parse_result = python_parser.parse_code_string(combined_code)
                    
                    if args.verbose:
                        print(f"\n发现的函数: {parse_result['functions']}")
                        print(f"函数调用关系: {parse_result['calls']}")
                    
                    # 生成调用图可视化
                    generate_call_graph_visualization(
                        parse_result['call_graph'],
                        filename_prefix="python_call_graph",
                        title="Python Call Graph from C Code",
                        verbose=args.verbose
                    )
                        
                except Exception as e:
                    print(f"分析Python代码时出错: {e}")
            else:
                print("\n未找到Python代码片段，跳过调用图分析")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()