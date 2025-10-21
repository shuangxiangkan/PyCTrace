"""
C/C++代码解析器
使用tree-sitter解析C/C++代码，提取函数名和字符串
"""

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter
from typing import List, Dict, Any, Optional, Tuple
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.python_string import (
    clean_string_literal, 
    extract_python_from_strings
)
from .python_registration_extractor import PythonRegistrationExtractor
from .python_call_extractor import PythonCallExtractor


class CCodeParser:
    """C/C++代码解析器"""
    
    def __init__(self):
        # 初始化tree-sitter解析器
        try:
            # 新版API（不需要name参数）
            self.c_language = tree_sitter.Language(tsc.language())
            self.cpp_language = tree_sitter.Language(tscpp.language())
        except TypeError:
            # 旧版API（需要name参数）
            self.c_language = tree_sitter.Language(tsc.language(), "c")
            self.cpp_language = tree_sitter.Language(tscpp.language(), "cpp")
    
    def _parse_source_code(self, file_path: str) -> Tuple[tree_sitter.Tree, str]:
        """
        解析C/C++源代码文件，返回AST和源代码
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            tuple: (AST树, 源代码字符串)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # 根据文件扩展名选择解析器
        file_ext = os.path.splitext(file_path)[1].lower()
        parser = tree_sitter.Parser()
        
        # 兼容新旧API
        if file_ext in ['.cpp', '.cc', '.cxx', '.hpp']:
            language = self.cpp_language
        else:
            language = self.c_language
        
        try:
            # 新版API
            parser.language = language
        except AttributeError:
            # 旧版API
            parser.set_language(language)
        
        # 解析代码
        tree = parser.parse(bytes(source_code, 'utf8'))
        
        return tree, source_code
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析C/C++文件，提取函数名和调用关系
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            Dict: 解析结果，包含函数名列表、调用关系和调用图
        """
        tree, source_code = self._parse_source_code(file_path)
        
        # 提取函数名和调用关系
        functions = self._extract_functions(tree.root_node, source_code)
        calls = self._extract_function_calls(tree.root_node, source_code)
        call_graph = self._build_call_graph(functions, calls)
        
        return {
            'file_path': file_path,
            'functions': functions,
            'calls': calls,
            'call_graph': call_graph
        }
    
    def _extract_functions(self, node: tree_sitter.Node, source_code: str) -> List[str]:
        """提取函数名"""
        functions = []
        
        def traverse(node):
            if node.type == 'function_definition':
                func_name = self._get_function_name(node, source_code)
                if func_name:
                    functions.append(func_name)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return functions
    
    def _get_function_name(self, node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """从函数定义节点中提取函数名"""
        try:
            # 递归查找function_declarator或pointer_declarator中的identifier
            def find_function_name(node):
                if node.type == 'identifier':
                    return self._get_node_text(node, source_code)
                
                # 在function_declarator中查找
                if node.type == 'function_declarator':
                    for child in node.children:
                        if child.type == 'identifier':
                            return self._get_node_text(child, source_code)
                
                # 在pointer_declarator中查找（用于返回指针的函数）
                if node.type == 'pointer_declarator':
                    for child in node.children:
                        result = find_function_name(child)
                        if result:
                            return result
                
                # 递归查找子节点
                for child in node.children:
                    result = find_function_name(child)
                    if result:
                        return result
                
                return None
            
            return find_function_name(node)
        except Exception:
            return None
    
    def _get_node_text(self, node: tree_sitter.Node, source_code: str) -> str:
        """获取节点对应的源代码文本"""
        return source_code[node.start_byte:node.end_byte]
    
    def _extract_function_calls(self, node: tree_sitter.Node, source_code: str) -> List[Tuple[str, str]]:
        """提取函数调用关系"""
        calls = []
        current_function = None
        
        def traverse(node, parent_function=None):
            nonlocal current_function
            
            # 如果进入函数定义，更新当前函数
            if node.type == 'function_definition':
                func_name = self._get_function_name(node, source_code)
                if func_name:
                    current_function = func_name
                    # 递归处理函数体
                    for child in node.children:
                        traverse(child, current_function)
                    current_function = parent_function  # 恢复上级函数
                return
            
            # 如果是函数调用
            if node.type == 'call_expression':
                called_function = self._get_called_function_name(node, source_code)
                if called_function and current_function:
                    calls.append((current_function, called_function))
            
            # 递归处理子节点
            for child in node.children:
                traverse(child, current_function)
        
        traverse(node)
        return calls
    
    def _get_called_function_name(self, call_node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """从函数调用节点中提取被调用的函数名"""
        try:
            # 查找函数名（可能是简单的identifier或field_expression）
            for child in call_node.children:
                if child.type == 'identifier':
                    return self._get_node_text(child, source_code)
                elif child.type == 'field_expression':
                    # 处理 obj.method() 或 struct->field() 形式的调用
                    return self._get_field_name(child, source_code)
            return None
        except Exception:
            return None
    
    def _get_field_name(self, field_node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """获取字段表达式的名称"""
        try:
            # 查找最后一个identifier（方法名或字段名）
            for child in reversed(field_node.children):
                if child.type == 'field_identifier':
                    return self._get_node_text(child, source_code)
            return None
        except Exception:
            return None
    
    def _build_call_graph(self, functions: List[str], calls: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """构建调用图"""
        call_graph = {func: [] for func in functions}
        
        for caller, callee in calls:
            if caller in call_graph:
                if callee not in call_graph[caller]:
                    call_graph[caller].append(callee)
        
        return call_graph

    def extract_strings(self, file_path: str) -> List[str]:
        """
        从C/C++文件中提取Python代码片段
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            List[str]: 提取的Python代码片段列表
        """
        tree, source_code = self._parse_source_code(file_path)
        
        # 提取所有字符串
        raw_strings = self._extract_strings(tree.root_node, source_code)
        
        # 使用Utils中的字符串处理功能
        return extract_python_from_strings(raw_strings)
    
    def extract_python_function_registrations(self, file_path: str) -> Dict[str, Any]:
        """
        提取C代码中注册的Python函数信息
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            Dict: 包含模块信息和注册的Python函数信息
        """
        # 解析源代码
        tree, source_code = self._parse_source_code(file_path)
        
        # 委托给专门的提取器
        extractor = PythonRegistrationExtractor()
        return extractor.extract_python_function_registrations_from_ast(tree.root_node, source_code, file_path)
    
    def extract_python_calls(self, file_path: str) -> Dict[str, Any]:
        """
        提取C代码中调用Python函数的信息
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            Dict: 包含原始代码片段和解析后的调用信息
        """
        # 解析源代码
        tree, source_code = self._parse_source_code(file_path)
        
        # 委托给专门的提取器
        extractor = PythonCallExtractor()
        return extractor.extract_python_calls_from_ast(tree.root_node, source_code)
    
    def _extract_strings(self, node: tree_sitter.Node, source_code: str) -> List[str]:
        """提取字符串字面量"""
        strings = []
        
        def traverse(node):
            if node.type == 'string_literal':
                string_content = self._get_node_text(node, source_code)
                # 去掉引号并处理转义字符
                cleaned_string = clean_string_literal(string_content)
                if cleaned_string:
                    strings.append(cleaned_string)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return strings
    
    def build_python_related_call_graph(self, file_path: str) -> Dict[str, Any]:
        """
        构建Python相关的调用图
        只包含与Python交互相关的C函数和Python函数调用
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            Dict: 包含以下信息：
                - python_related_functions: 与Python相关的C函数列表
                - registered_c_functions: 注册到Python的C函数映射 {c_function: python_name}
                - python_calls: Python函数调用信息列表
                - call_graph: 调用图 {caller: [callees]}
                - visualization_data: 用于可视化的数据
        """
        # 解析源代码
        tree, source_code = self._parse_source_code(file_path)
        
        # 1. 获取注册到Python的C函数信息（使用PythonRegistrationExtractor）
        registration_info = self.extract_python_function_registrations(file_path)
        registered_c_functions = {}  # {c_function: python_name}
        
        for method_array in registration_info['structured_info']['method_definitions']:
            for method in method_array['methods']:
                c_func = method['c_function']
                py_name = method['python_name']
                registered_c_functions[c_func] = py_name
        
        # 2. 获取Python函数调用信息（使用PythonCallExtractor）
        call_info = self.extract_python_calls(file_path)
        python_calls = call_info['parsed_calls']
        calling_c_functions = set(call_info['functions_with_calls'])  # 直接使用提取器的结果
        
        # 3. 合并所有Python相关的C函数
        python_related_functions = set(registered_c_functions.keys()) | calling_c_functions
        
        # 4. 构建调用图（只包含Python相关的函数和调用）
        call_graph = {}
        
        # 初始化调用图节点
        for func in python_related_functions:
            call_graph[func] = []
        
        # 添加Python函数作为节点
        python_function_nodes = set()
        for call in python_calls:
            if call.get('function_name'):
                python_function_nodes.add(call['function_name'])
        
        # 提取C函数之间的调用关系（只保留Python相关的）
        all_calls = self._extract_function_calls(tree.root_node, source_code)
        for caller, callee in all_calls:
            if caller in python_related_functions:
                if callee in python_related_functions:
                    # C函数调用C函数
                    if callee not in call_graph[caller]:
                        call_graph[caller].append(callee)
        
        # 添加C函数调用Python函数的关系（使用PythonCallExtractor来查找调用者）
        call_extractor = PythonCallExtractor()
        for call in python_calls:
            # 使用PythonCallExtractor的方法找到调用者
            c_caller = call_extractor.find_caller_for_python_call(tree.root_node, source_code, call['raw_code'])
            if c_caller and c_caller in python_related_functions:
                if c_caller not in call_graph:
                    call_graph[c_caller] = []
                
                # 添加Python函数调用
                python_call_repr = call.get('python_call', call.get('function_name', 'Unknown'))
                if python_call_repr and python_call_repr not in call_graph[c_caller]:
                    call_graph[c_caller].append(python_call_repr)
        
        # 5. 构建可视化数据
        visualization_data = self._build_visualization_data(
            python_related_functions,
            registered_c_functions,
            python_calls,
            call_graph
        )
        
        return {
            'file_path': file_path,
            'python_related_functions': list(python_related_functions),
            'registered_c_functions': registered_c_functions,
            'python_calls': python_calls,
            'call_graph': call_graph,
            'visualization_data': visualization_data
        }
    
    def _build_visualization_data(self, python_related_functions, registered_c_functions, 
                                   python_calls, call_graph) -> Dict[str, Any]:
        """构建用于可视化的数据结构"""
        nodes = []
        edges = []
        
        # 添加C函数节点
        for func in python_related_functions:
            node_type = 'registered_c_function' if func in registered_c_functions else 'c_function'
            python_name = registered_c_functions.get(func, None)
            
            node = {
                'id': func,
                'label': func,
                'type': node_type,
                'python_name': python_name
            }
            nodes.append(node)
        
        # 添加Python函数节点
        python_funcs = set()
        for call in python_calls:
            if call.get('function_name'):
                python_funcs.add(call['function_name'])
        
        for py_func in python_funcs:
            node = {
                'id': py_func,
                'label': py_func,
                'type': 'python_function'
            }
            nodes.append(node)
        
        # 添加边（调用关系）
        for caller, callees in call_graph.items():
            for callee in callees:
                edge = {
                    'from': caller,
                    'to': callee,
                    'type': 'python_call' if callee in python_funcs or '(' in callee else 'c_call'
                }
                edges.append(edge)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def generate_python_related_call_graph_file(self, file_path: str, output_prefix: str = "python_related_call_graph") -> Dict[str, Any]:
        """
        生成Python相关调用图并保存为文件
        
        Args:
            file_path: C/C++文件路径
            output_prefix: 输出文件前缀
            
        Returns:
            Dict: 调用图数据
        """
        result = self.build_python_related_call_graph(file_path)
        
        # 生成调用图可视化
        from Utils.graph_visualizer import generate_call_graph_visualization
        
        file_basename = os.path.splitext(os.path.basename(file_path))[0]
        filename_prefix = f"{output_prefix}_{file_basename}"
        title = f"Python-Related Call Graph - {os.path.basename(file_path)}"
        
        generate_call_graph_visualization(
            result['call_graph'],
            filename_prefix=filename_prefix,
            title=title,
            verbose=True
        )
        
        return result
    
def parse_c_file(file_path: str) -> List[str]:
    """
    便捷函数：解析单个C文件，返回函数名列表
    
    Args:
        file_path: C文件路径
        
    Returns:
        List[str]: 函数名列表
    """
    parser = CCodeParser()
    result = parser.parse_file(file_path)
    return result['functions']


def extract_python_strings(file_path: str) -> List[str]:
    """
    便利函数：从C/C++文件中提取Python代码片段
    
    Args:
        file_path: C/C++文件路径
        
    Returns:
        List[str]: Python代码片段列表
    """
    parser = CCodeParser()
    return parser.extract_strings(file_path)