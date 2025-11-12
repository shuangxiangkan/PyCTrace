#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from C.py_module_extractor import (
    format_registration_info,
    CCodeParser
)


def print_separator(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def analyze_c_file(file_path):
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return None
    
    print_separator(f"分析文件: {os.path.basename(file_path)}")
    
    parser = CCodeParser()
    result = parser.parse_files([file_path])
    
    print(f"文件路径: {file_path}")
    print(f"检测到的模块数量: {len(result.get('module_chains', []))}")
    print(f"检测到的PyMethodDef数量: {len(result.get('py_method_defs', []))}")
    print(f"检测到的PyModuleDef数量: {len(result.get('py_module_defs', []))}")
    print(f"检测到的PyInit函数数量: {len(result.get('py_init_funcs', []))}")
    print(f"检测到的C函数数量: {len(result.get('py_c_functions', []))}")
    
    if result.get('module_chains'):
        print("\n模块链路信息:")
        for i, chain in enumerate(result['module_chains'], 1):
            print(f"\n  模块 {i}:")
            print(f"    - Init函数: {chain['init_function']}")
            if chain.get('method_def_info'):
                print(f"    - PyMethodDef: {chain['method_def_info']['name']}")
            if chain.get('module_def_info'):
                print(f"    - PyModuleDef: {chain['module_def_info']['name']}")
            print(f"    - 注册的C函数数量: {len(chain.get('c_functions', []))}")
            if chain.get('c_functions'):
                print(f"    - 函数名: {[func['name'] for func in chain['c_functions']]}")
    
    print("\n" + "=" * 80)
    print("提取的注册代码:")
    print("=" * 80 + "\n")
    formatted = format_registration_info(result)
    if formatted:
        print(formatted)
    else:
        print("(没有提取到注册代码)")
    
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python test_all_cases.py <C文件1> [C文件2] [C文件3] ...")
        print("\n示例:")
        print("  python test_all_cases.py case1_1module_1func.c")
        print("  python test_all_cases.py case5_file1.c case5_file2.c")
        print("  python test_all_cases.py /path/to/your/file.c")
        print("\n可用的测试文件:")
        test_dir = os.path.dirname(__file__)
        c_files = [f for f in os.listdir(test_dir) if f.endswith('.c')]
        for f in sorted(c_files):
            print(f"  - {f}")
        return 1
    
    print("\n" + "=" * 80)
    print("  Python模块注册提取器 - 测试工具")
    print("=" * 80)
    
    file_paths = []
    for file_arg in sys.argv[1:]:
        if not os.path.isabs(file_arg):
            file_path = os.path.join(os.path.dirname(__file__), file_arg)
        else:
            file_path = file_arg
        file_paths.append(file_path)
    
    if len(file_paths) == 1:
        result = analyze_c_file(file_paths[0])
    else:
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"错误: 文件不存在 - {file_path}")
                return 1
        
        print_separator("多文件合并分析")
        print(f"正在分析 {len(file_paths)} 个文件:")
        for i, fp in enumerate(file_paths, 1):
            print(f"  {i}. {os.path.basename(fp)}")
        print()
        
        parser = CCodeParser()
        merged_result = parser.parse_files(file_paths)
        
        print(f"合并结果统计:")
        print(f"  - 总模块数: {len(merged_result.get('module_chains', []))}")
        print(f"  - 总PyMethodDef数: {len(merged_result.get('py_method_defs', []))}")
        print(f"  - 总PyModuleDef数: {len(merged_result.get('py_module_defs', []))}")
        print(f"  - 总PyInit函数数: {len(merged_result.get('py_init_funcs', []))}")
        print(f"  - 总C函数数: {len(merged_result.get('py_c_functions', []))}")
        
        if merged_result.get('module_chains'):
            print("\n模块链路信息:")
            for i, chain in enumerate(merged_result['module_chains'], 1):
                print(f"\n  模块 {i}: {chain['init_function']}")
                if chain.get('method_def_info'):
                    print(f"    - PyMethodDef: {chain['method_def_info']['name']}")
                if chain.get('module_def_info'):
                    print(f"    - PyModuleDef: {chain['module_def_info']['name']}")
                if chain.get('init_function_info'):
                    print(f"    - PyInit函数: {chain['init_function_info']['name']}")
                print(f"    - 注册的C函数数量: {len(chain.get('c_functions', []))}")
                if chain.get('c_functions'):
                    for func in chain['c_functions']:
                        print(f"      * {func['name']}")
        
        print("\n" + "=" * 80)
        print("合并后的注册代码:")
        print("=" * 80 + "\n")
        formatted = format_registration_info(merged_result)
        if formatted:
            print(formatted)
        else:
            print("(没有提取到注册代码)")
    
    print("\n✓ 分析完成\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())