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
        if file_ext in ['.cpp', '.cc', '.cxx', '.hpp']:
            parser.set_language(self.cpp_language)
        else:
            parser.set_language(self.c_language)
        
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