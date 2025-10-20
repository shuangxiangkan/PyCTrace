"""
Python代码解析器
使用tree-sitter解析Python代码，提取函数名
"""

import tree_sitter_python as tspy
import tree_sitter
from typing import List, Dict, Any, Optional
import os


class PythonCodeParser:
    """Python代码解析器"""
    
    def __init__(self):
        # 初始化tree-sitter解析器
        self.python_language = tree_sitter.Language(tspy.language())
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析Python文件，提取函数名
        
        Args:
            file_path: Python文件路径
            
        Returns:
            Dict: 解析结果，包含函数名列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # 创建解析器
        parser = tree_sitter.Parser(self.python_language)
        
        # 解析代码
        tree = parser.parse(bytes(source_code, 'utf8'))
        
        # 提取函数名
        functions = self._extract_functions(tree.root_node, source_code)
        
        return {
            'file_path': file_path,
            'functions': functions
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