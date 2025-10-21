"""
调用图合并模块

该模块负责合并Python相关的C调用图和Python代码调用图，
构建一个完整的Python-C交互调用图。
"""

from typing import Dict, Any, List, Set
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def merge_python_c_call_graph(
    c_call_graph_data: Dict[str, Any],
    python_call_graph_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    合并Python相关的C调用图和Python代码调用图
    
    Args:
        c_call_graph_data: C调用图数据（来自 build_python_related_call_graph）
        python_call_graph_data: Python调用图数据（来自 PythonCodeParser）
        
    Returns:
        Dict: 合并后的调用图数据，包含：
            - merged_call_graph: 合并后的完整调用图
            - all_functions: 所有函数列表
            - c_functions: C函数列表
            - python_functions: Python函数列表
            - registered_c_functions: 注册到Python的C函数映射
            - cross_language_calls: 跨语言调用关系
    """
    # 1. 提取基础数据
    c_call_graph = c_call_graph_data.get('call_graph', {})
    python_call_graph = python_call_graph_data.get('call_graph', {})
    
    c_functions = set(c_call_graph_data.get('python_related_functions', []))
    python_functions = set(python_call_graph_data.get('functions', []))
    
    registered_c_functions = c_call_graph_data.get('registered_c_functions', {})
    python_calls_from_c = c_call_graph_data.get('python_calls', [])
    
    # 创建Python名称到C函数的映射
    py_name_to_c_func = {py_name: c_func for c_func, py_name in registered_c_functions.items()}
    
    # 2. 创建统一的节点名称映射
    # 对于注册到Python的C函数，使用 "c_func(py_name)" 格式
    unified_node_names = {}
    for c_func, py_name in registered_c_functions.items():
        unified_node_names[c_func] = f"{c_func}({py_name})"
        unified_node_names[py_name] = f"{c_func}({py_name})"
    
    # 3. 初始化合并后的调用图
    merged_call_graph = {}
    
    # 添加C函数节点（使用统一名称）
    for func in c_functions:
        node_name = unified_node_names.get(func, func)
        if node_name not in merged_call_graph:
            merged_call_graph[node_name] = []
    
    # 添加Python函数节点（排除已经合并的）
    for func in python_functions:
        if func not in py_name_to_c_func:  # 如果不是C函数的Python名称
            if func not in merged_call_graph:
                merged_call_graph[func] = []
    
    # 4. 添加C函数的调用关系（规范化调用目标）
    for caller, callees in c_call_graph.items():
        caller_name = unified_node_names.get(caller, caller)
        if caller_name not in merged_call_graph:
            merged_call_graph[caller_name] = []
        
        for callee in callees:
            # 规范化callee - 提取函数名（去掉参数）
            callee_func_name = callee.split('(')[0] if '(' in callee else callee
            
            # 检查是否是Python函数调用
            if callee_func_name in python_functions:
                # 连接到Python函数节点
                target_name = unified_node_names.get(callee_func_name, callee_func_name)
                if target_name not in merged_call_graph[caller_name]:
                    merged_call_graph[caller_name].append(target_name)
            else:
                # C函数调用
                target_name = unified_node_names.get(callee, callee)
                if target_name not in merged_call_graph[caller_name]:
                    merged_call_graph[caller_name].append(target_name)
    
    # 5. 添加Python函数之间的调用关系
    for caller, callees in python_call_graph.items():
        # 如果caller是C函数的Python名称，使用统一名称
        caller_name = unified_node_names.get(caller, caller)
        
        if caller_name not in merged_call_graph:
            merged_call_graph[caller_name] = []
        
        for callee in callees:
            # 检查callee是否是注册的C函数的Python名称
            if callee in py_name_to_c_func:
                # 连接到统一的C函数节点
                target_name = unified_node_names[callee]
            elif '.' in callee:
                # 处理模块调用，如 host.tick
                parts = callee.split('.')
                func_name = parts[-1]
                if func_name in py_name_to_c_func:
                    target_name = unified_node_names[func_name]
                else:
                    target_name = callee
            else:
                target_name = unified_node_names.get(callee, callee)
            
            if target_name not in merged_call_graph[caller_name]:
                merged_call_graph[caller_name].append(target_name)
    
    # 6. 统计跨语言调用和构建节点信息
    c_to_python_calls = []
    python_to_c_calls = []
    
    # 创建节点类型映射
    node_types = {}
    actual_c_functions = set()
    actual_python_functions = set()
    
    for node in merged_call_graph.keys():
        # 提取基本名称（去掉括号中的内容）
        base_name = node.split('(')[0] if '(' in node else node
        
        # 检查是否是注册的C函数（统一节点格式: "c_func(py_name)"）
        if base_name in registered_c_functions:
            node_types[node] = 'registered_c_function'
            actual_c_functions.add(node)
        elif base_name in c_functions or node in c_functions:
            # 纯C函数
            node_types[node] = 'c_function'
            actual_c_functions.add(node)
        elif base_name in python_functions or node in python_functions:
            # 纯Python函数
            node_types[node] = 'python_function'
            actual_python_functions.add(node)
        else:
            # 默认为Python函数（如print等内置函数）
            node_types[node] = 'python_function'
            actual_python_functions.add(node)
    
    # 统计跨语言调用
    for caller, callees in merged_call_graph.items():
        caller_type = node_types.get(caller)
        
        for callee in callees:
            callee_type = node_types.get(callee)
            
            if caller_type in ['c_function', 'registered_c_function'] and callee_type == 'python_function':
                c_to_python_calls.append((caller, callee))
            elif caller_type == 'python_function' and callee_type in ['c_function', 'registered_c_function']:
                python_to_c_calls.append((caller, callee))
    
    return {
        'merged_call_graph': merged_call_graph,
        'all_functions': list(merged_call_graph.keys()),
        'c_functions': list(actual_c_functions),
        'python_functions': list(actual_python_functions),
        'registered_c_functions': registered_c_functions,
        'c_to_python_calls': c_to_python_calls,
        'python_to_c_calls': python_to_c_calls,
        'node_types': node_types,
        'unified_node_names': unified_node_names,
        'c_only_graph': c_call_graph,
        'python_only_graph': python_call_graph
    }


def _identify_python_to_c_calls(
    python_call_graph: Dict[str, List[str]],
    registered_c_functions: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    识别Python代码中调用C函数的关系
    
    Args:
        python_call_graph: Python调用图
        registered_c_functions: 注册的C函数映射 {c_function: python_name}
        
    Returns:
        Dict: Python函数调用C函数的映射 {python_func: [c_func1, c_func2, ...]}
    """
    python_to_c = {}
    
    # 创建反向映射：python_name -> c_function
    py_name_to_c_func = {py_name: c_func for c_func, py_name in registered_c_functions.items()}
    
    for caller, callees in python_call_graph.items():
        c_callees = []
        
        for callee in callees:
            # 处理模块调用，如 host.tick
            if '.' in callee:
                parts = callee.split('.')
                func_name = parts[-1]  # 获取函数名部分
                
                # 查找对应的C函数
                if func_name in py_name_to_c_func:
                    c_callees.append(py_name_to_c_func[func_name])
            # 处理直接调用
            elif callee in py_name_to_c_func:
                c_callees.append(py_name_to_c_func[callee])
        
        if c_callees:
            python_to_c[caller] = c_callees
    
    return python_to_c


def generate_merged_visualization(
    merged_data: Dict[str, Any],
    output_prefix: str = "merged_call_graph",
    title: str = "Merged Python-C Call Graph",
    verbose: bool = False
):
    """
    生成合并后的调用图可视化
    
    Args:
        merged_data: 合并后的调用图数据
        output_prefix: 输出文件名前缀
        title: 图表标题
        verbose: 是否显示详细信息
    """
    from Utils.graph_visualizer import generate_merged_call_graph_visualization
    
    if verbose:
        print("\n📊 合并后的调用图统计:")
        print(f"  总函数数: {len(merged_data['all_functions'])}")
        print(f"  C函数数: {len(merged_data['c_functions'])}")
        print(f"  Python函数数: {len(merged_data['python_functions'])}")
        print(f"  C->Python调用: {len(merged_data['c_to_python_calls'])}")
        print(f"  Python->C调用: {len(merged_data['python_to_c_calls'])}")
        
        if merged_data['c_to_python_calls']:
            print("\n  C->Python调用详情:")
            for caller, callee in merged_data['c_to_python_calls']:
                print(f"    {caller} -> {callee}")
        
        if merged_data['python_to_c_calls']:
            print("\n  Python->C调用详情:")
            for caller, callee in merged_data['python_to_c_calls']:
                print(f"    {caller} -> {callee}")
    
    # 生成带颜色的合并可视化
    generate_merged_call_graph_visualization(
        merged_data['merged_call_graph'],
        node_types=merged_data['node_types'],
        c_to_python_calls=merged_data['c_to_python_calls'],
        python_to_c_calls=merged_data['python_to_c_calls'],
        filename_prefix=output_prefix,
        title=title,
        verbose=verbose
    )


def extract_and_merge_from_c_file(
    c_file_path: str,
    python_code_string: str = None,
    output_prefix: str = "merged_call_graph",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    从C文件提取Python代码并合并调用图的便捷函数
    
    Args:
        c_file_path: C/C++文件路径
        python_code_string: Python代码字符串（可选，如果不提供则从C代码中提取）
        output_prefix: 输出文件前缀
        verbose: 是否显示详细信息
        
    Returns:
        Dict: 合并后的调用图数据
    """
    from C.c_parser import CCodeParser
    from Python.python_parser import PythonCodeParser
    
    # 1. 构建Python相关的C调用图
    c_parser = CCodeParser()
    c_result = c_parser.build_python_related_call_graph(c_file_path)
    
    # 2. 获取或提取Python代码
    if python_code_string is None:
        # 从C代码中提取Python代码片段
        python_snippets = c_parser.extract_strings(c_file_path)
        if python_snippets:
            python_code_string = "\n\n".join(python_snippets)
        else:
            python_code_string = ""
    
    # 3. 解析Python代码
    python_parser = PythonCodeParser()
    python_result = python_parser.parse_code_string(python_code_string)
    
    # 4. 合并调用图
    merged_data = merge_python_c_call_graph(c_result, python_result)
    
    # 5. 生成可视化（如果指定）
    if output_prefix:
        file_basename = os.path.splitext(os.path.basename(c_file_path))[0]
        full_prefix = f"{output_prefix}_{file_basename}"
        title = f"Merged Python-C Call Graph - {os.path.basename(c_file_path)}"
        
        generate_merged_visualization(
            merged_data,
            output_prefix=full_prefix,
            title=title,
            verbose=verbose
        )
    
    return merged_data

