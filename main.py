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
            
            # 提取Python函数注册信息
            print("\n正在提取Python函数注册信息...")
            print("=" * 50)
            
            try:
                for c_file in c_files:
                    try:
                        print(f"\n分析文件: {c_file}")
                        print("-" * 30)
                        
                        # 提取Python函数注册信息
                        registration_info = c_parser.extract_python_function_registrations(c_file)
                        
                        # 获取结构化信息
                        structured_info = registration_info['structured_info']
                        raw_code_snippets = registration_info['raw_code_snippets']
                        
                        # 显示原始代码片段统计
                        if args.verbose:
                            print("📄 原始代码片段统计:")
                            print(f"  • PyMethodDef数组: {len(raw_code_snippets['pymethoddef_arrays'])} 个")
                            print(f"  • PyModuleDef结构体: {len(raw_code_snippets['pymoduledef_structs'])} 个")
                            print(f"  • PyInit函数: {len(raw_code_snippets['pyinit_functions'])} 个")
                            print(f"  • 相关函数: {len(raw_code_snippets['related_functions'])} 个")
                        
                        # 显示模块定义信息
                        if structured_info['module_definitions']:
                            print("📦 模块定义:")
                            for module_def in structured_info['module_definitions']:
                                print(f"  • 结构体名称: {module_def['struct_name']}")
                                print(f"  • 模块名称: {module_def['module_name']}")
                                print(f"  • 方法数组: {module_def['methods_array']}")
                        
                        # 显示初始化函数信息
                        if structured_info['init_functions']:
                            print("🔧 初始化函数:")
                            for init_func in structured_info['init_functions']:
                                print(f"  • 函数名: {init_func['function_name']}")
                                print(f"  • 模块名: {init_func['module_name']}")
                                print(f"  • 模块结构体: {init_func['module_struct']}")
                        
                        # 显示方法定义信息
                        if structured_info['method_definitions']:
                            print("🐍 注册的Python函数:")
                            for method_array in structured_info['method_definitions']:
                                print(f"  数组名称: {method_array['array_name']}")
                                for method in method_array['methods']:
                                    print(f"    • Python函数名: '{method['python_name']}'")
                                    print(f"      C函数名: {method['c_function']}")
                                    print(f"      标志: {method['flags']}")
                                    if method['doc']:
                                        print(f"      文档: '{method['doc']}'")
                        
                        # 在verbose模式下显示原始代码片段
                        if args.verbose and any(raw_code_snippets.values()):
                            print("\n📝 原始代码片段:")
                            
                            if raw_code_snippets['pymethoddef_arrays']:
                                print("\n  PyMethodDef数组:")
                                for i, snippet in enumerate(raw_code_snippets['pymethoddef_arrays'], 1):
                                    print(f"    片段 {i}:")
                                    print("    " + "\n    ".join(snippet.split('\n')))
                            
                            if raw_code_snippets['pymoduledef_structs']:
                                print("\n  PyModuleDef结构体:")
                                for i, snippet in enumerate(raw_code_snippets['pymoduledef_structs'], 1):
                                    print(f"    片段 {i}:")
                                    print("    " + "\n    ".join(snippet.split('\n')))
                            
                            if raw_code_snippets['pyinit_functions']:
                                print("\n  PyInit函数:")
                                for i, snippet in enumerate(raw_code_snippets['pyinit_functions'], 1):
                                    print(f"    片段 {i}:")
                                    print("    " + "\n    ".join(snippet.split('\n')))
                            
                            if raw_code_snippets['related_functions']:
                                print("\n  相关函数:")
                                for i, snippet in enumerate(raw_code_snippets['related_functions'], 1):
                                    print(f"    片段 {i}:")
                                    print("    " + "\n    ".join(snippet.split('\n')))
                                    print()
                        
                        # 检查是否有注册信息
                        has_registration = (structured_info['module_definitions'] or 
                                          structured_info['init_functions'] or 
                                          structured_info['method_definitions'])
                        
                        if not has_registration:
                            print("  未找到Python函数注册信息")
                            
                    except Exception as e:
                        print(f"提取Python函数注册信息时出错: {e}")
                        
            except Exception as e:
                print(f"分析Python函数注册信息时出错: {e}")
            
            # 提取C代码中的Python函数调用
            print("\n正在提取C代码中的Python函数调用...")
            print("=" * 50)
            
            try:
                # 创建C代码解析器
                c_parser = CCodeParser()
                
                for c_file in c_files:
                    try:
                        print(f"\n分析文件: {c_file}")
                        print("-" * 30)
                        
                        # 提取Python调用信息
                        call_info = c_parser.extract_python_calls(c_file)
                        
                        # 获取原始代码片段和解析后的调用信息
                        raw_snippets = call_info['raw_code_snippets']
                        parsed_calls = call_info['parsed_calls']
                        
                        # 显示原始代码片段统计
                        if args.verbose:
                            print("📄 Python函数调用相关代码统计:")
                            print(f"  • 函数调用: {len(raw_snippets['function_calls'])} 个")
                            print(f"  • 函数查找: {len(raw_snippets['function_lookup'])} 个")
                            print(f"  • 参数构建: {len(raw_snippets['argument_building'])} 个")
                        
                        # 显示解析后的调用信息
                        if parsed_calls:
                            print("🐍 解析的Python函数调用:")
                            for call in parsed_calls:
                                if call['python_call']:
                                    print(f"  • Python调用: {call['python_call']}")
                                    print(f"    调用类型: {call['call_type']}")
                                    print(f"    原始代码: {call['raw_code']}")
                                else:
                                    print(f"  • 调用类型: {call['call_type']}")
                                    print(f"    原始代码: {call['raw_code']}")
                        
                        # 在verbose模式下显示原始代码片段
                        if args.verbose and any(raw_snippets.values()):
                            print("\n📝 原始Python函数调用相关代码:")
                            
                            if raw_snippets['function_calls']:
                                print("\n  函数调用:")
                                for i, snippet in enumerate(raw_snippets['function_calls'], 1):
                                    print(f"    片段 {i}: {snippet}")
                            
                            if raw_snippets['function_lookup']:
                                print("\n  函数查找:")
                                for i, snippet in enumerate(raw_snippets['function_lookup'], 1):
                                    print(f"    片段 {i}: {snippet}")
                            
                            if raw_snippets['argument_building']:
                                print("\n  参数构建:")
                                for i, snippet in enumerate(raw_snippets['argument_building'], 1):
                                    print(f"    片段 {i}: {snippet}")
                        
                        # 检查是否有Python调用
                        has_calls = (raw_snippets['function_calls'] or 
                                   raw_snippets['function_lookup'] or 
                                   raw_snippets['argument_building'])
                        
                        if not has_calls:
                            print("  未找到Python函数调用")
                            
                    except Exception as e:
                        print(f"提取Python调用信息时出错: {e}")
                        
            except Exception as e:
                print(f"分析Python调用时出错: {e}")
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