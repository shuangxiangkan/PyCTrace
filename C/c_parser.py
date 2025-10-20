"""
C/C++代码解析器
使用tree-sitter解析C/C++代码，提取函数名
"""

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter
from typing import List, Dict, Any, Optional
import os


class CCodeParser:
    """C/C++代码解析器"""
    
    def __init__(self):
        # 初始化tree-sitter解析器
        self.c_language = tree_sitter.Language(tsc.language())
        self.cpp_language = tree_sitter.Language(tscpp.language())
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析C/C++文件，提取函数名
        
        Args:
            file_path: C/C++文件路径
            
        Returns:
            Dict: 解析结果，包含函数名列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # 根据文件扩展名选择解析器
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.cpp', '.cc', '.cxx', '.hpp']:
            parser = tree_sitter.Parser(self.cpp_language)
        else:
            parser = tree_sitter.Parser(self.c_language)
        
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