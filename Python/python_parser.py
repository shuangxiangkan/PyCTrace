"""
Python代码解析器
使用tree-sitter解析Python代码，提取函数名和调用关系
"""

import tree_sitter_python as tspy
import tree_sitter
from typing import List, Dict, Any, Optional, Tuple
import os


class PythonCodeParser:
    """Python代码解析器"""
    
    def __init__(self):
        # 初始化tree-sitter解析器
        self.python_language = tree_sitter.Language(tspy.language())
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析Python文件，提取函数名和调用关系
        
        Args:
            file_path: Python文件路径
            
        Returns:
            Dict: 解析结果，包含函数名列表、调用关系和调用图
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # 使用parse_code_string进行解析，避免代码重复
        result = self.parse_code_string(source_code)
        
        # 添加文件路径信息
        result['file_path'] = file_path
        
        return result
    
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
            # 在function_definition中查找identifier
            for child in node.children:
                if child.type == 'identifier':
                    return self._get_node_text(child, source_code)
            return None
        except Exception:
            return None
    
    def _get_node_text(self, node: tree_sitter.Node, source_code: str) -> str:
        """获取节点对应的源代码文本"""
        return source_code[node.start_byte:node.end_byte]
    
    def parse_code_string(self, code_string: str) -> Dict[str, Any]:
        """
        解析Python代码字符串，提取函数名和调用关系
        
        Args:
            code_string: Python代码字符串
            
        Returns:
            Dict: 解析结果，包含函数名列表和调用关系
        """
        if not code_string.strip():
            return {'functions': [], 'calls': [], 'call_graph': {}}
        
        # 创建解析器
        parser = tree_sitter.Parser(self.python_language)
        
        # 解析代码
        tree = parser.parse(bytes(code_string, 'utf8'))
        
        # 提取函数名和调用关系
        functions = self._extract_functions(tree.root_node, code_string)
        calls = self._extract_function_calls(tree.root_node, code_string)
        call_graph = self._build_call_graph(functions, calls)
        
        return {
            'functions': functions,
            'calls': calls,
            'call_graph': call_graph
        }
    
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
            if node.type == 'call':
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
            # 查找函数名（可能是简单的identifier或attribute）
            for child in call_node.children:
                if child.type == 'identifier':
                    return self._get_node_text(child, source_code)
                elif child.type == 'attribute':
                    # 处理 obj.method() 形式的调用
                    return self._get_attribute_name(child, source_code)
            return None
        except Exception:
            return None
    
    def _get_attribute_name(self, attr_node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """获取属性调用的名称"""
        try:
            # 查找最后一个identifier（方法名）
            for child in reversed(attr_node.children):
                if child.type == 'identifier':
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


def parse_python_file(file_path: str) -> List[str]:
    """
    便捷函数：解析单个Python文件，返回函数名列表
    
    Args:
        file_path: Python文件路径
        
    Returns:
        List[str]: 函数名列表
    """
    parser = PythonCodeParser()
    result = parser.parse_file(file_path)
    return result['functions']