"""
Python函数注册信息提取器

该模块专门用于从C/C++代码中提取Python扩展模块的函数注册信息，
包括PyMethodDef数组、PyModuleDef结构体和PyInit函数的解析。
"""

import tree_sitter
from typing import List, Dict, Any, Optional
import os
import sys

# 添加父目录到路径以导入Utils模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PythonRegistrationExtractor:
    """Python函数注册信息提取器"""
    
    def __init__(self):
        """初始化提取器"""
        pass
    
    def _get_node_text(self, node: tree_sitter.Node, source_code: str) -> str:
        """获取节点对应的源代码文本"""
        return source_code[node.start_byte:node.end_byte]
    
    def _get_function_name(self, node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """从函数定义节点中提取函数名"""
        try:
            # 查找函数声明器
            declarator = node.child_by_field_name('declarator')
            if not declarator:
                return None
            
            # 处理不同类型的声明器
            if declarator.type == 'function_declarator':
                # 直接的函数声明器
                func_name_node = declarator.child_by_field_name('declarator')
                if func_name_node and func_name_node.type == 'identifier':
                    return self._get_node_text(func_name_node, source_code)
            elif declarator.type == 'identifier':
                # 简单的标识符
                return self._get_node_text(declarator, source_code)
            elif declarator.type == 'pointer_declarator':
                # 指针声明器，递归查找
                inner_declarator = declarator.child_by_field_name('declarator')
                if inner_declarator:
                    return self._get_function_name(
                        type('MockNode', (), {'child_by_field_name': lambda _, field: inner_declarator if field == 'declarator' else None})(),
                        source_code
                    )
        except Exception:
            pass
        
        return None
    
    def _get_called_function_name(self, call_node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """从函数调用节点中提取被调用的函数名"""
        try:
            function_node = call_node.child_by_field_name('function')
            if not function_node:
                return None
            
            if function_node.type == 'identifier':
                return self._get_node_text(function_node, source_code)
            elif function_node.type == 'field_expression':
                field_node = function_node.child_by_field_name('field')
                if field_node:
                    return self._get_node_text(field_node, source_code)
        except Exception:
            pass
        
        return None
    
    def extract_python_function_registrations_from_ast(self, tree_root_node, source_code, file_path: str = None) -> Dict[str, Any]:
        """
        从已解析的AST中提取Python函数注册信息
        
        Args:
            tree_root_node: tree-sitter解析后的根节点
            source_code: 源代码字符串
            file_path: 文件路径（可选，用于记录）
            
        Returns:
            Dict: 包含两部分数据：
                1. raw_code_snippets: 原始代码片段，供大模型处理
                2. structured_info: 结构化信息，用于构造调用图
        """
        # 提取PyMethodDef数组信息
        method_defs = self._extract_pymethoddef_arrays(tree_root_node, source_code)
        
        # 提取模块定义信息
        module_defs = self._extract_pymoduledef_structs(tree_root_node, source_code)
        
        # 提取PyInit函数信息
        init_functions = self._extract_pyinit_functions(tree_root_node, source_code)
        
        # 提取原始代码片段
        raw_code_snippets = self._extract_raw_code_snippets(tree_root_node, source_code)
        
        return {
            'file_path': file_path,
            'raw_code_snippets': raw_code_snippets,
            'structured_info': {
                'method_definitions': method_defs,
                'module_definitions': module_defs,
                'init_functions': init_functions
            }
        }
    
    def _extract_raw_code_snippets(self, node: tree_sitter.Node, source_code: str) -> Dict[str, List[str]]:
        """
        提取Python函数注册相关的原始代码片段
        
        Args:
            node: AST节点
            source_code: 源代码字符串
            
        Returns:
            Dict: 包含各类代码片段的字典
        """
        code_snippets = {
            'pymethoddef_arrays': [],
            'pymoduledef_structs': [],
            'pyinit_functions': [],
            'related_functions': []  # 与Python注册相关的其他函数
        }
        
        def traverse_node(current_node):
            # 提取声明节点中的PyMethodDef数组和PyModuleDef结构体
            if current_node.type == 'declaration':
                # 检查是否是PyMethodDef数组
                if self._is_pymethoddef_array(current_node, source_code):
                    snippet = self._get_node_text(current_node, source_code)
                    code_snippets['pymethoddef_arrays'].append(snippet)
                # 检查是否是PyModuleDef结构体
                elif self._is_pymoduledef_struct(current_node, source_code):
                    snippet = self._get_node_text(current_node, source_code)
                    code_snippets['pymoduledef_structs'].append(snippet)
            
            # 提取PyInit函数代码片段
            elif current_node.type == 'function_definition':
                func_name = self._get_function_name(current_node, source_code)
                if func_name and func_name.startswith('PyInit_'):
                    snippet = self._get_node_text(current_node, source_code)
                    code_snippets['pyinit_functions'].append(snippet)
                # 提取其他与Python相关的函数（如py_开头的函数）
                elif func_name and func_name.startswith('py_'):
                    snippet = self._get_node_text(current_node, source_code)
                    code_snippets['related_functions'].append(snippet)
            
            # 递归遍历子节点
            for child in current_node.children:
                traverse_node(child)
        
        traverse_node(node)
        return code_snippets
    
    def _extract_pymethoddef_arrays(self, node: tree_sitter.Node, source_code: str) -> List[Dict[str, Any]]:
        """提取PyMethodDef数组定义"""
        method_arrays = []
        
        def traverse(node):
            # 查找变量声明
            if node.type == 'declaration':
                # 检查是否是PyMethodDef类型的数组
                if self._is_pymethoddef_array(node, source_code):
                    array_info = self._parse_pymethoddef_array(node, source_code)
                    if array_info:
                        method_arrays.append(array_info)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return method_arrays
    
    def _is_pymethoddef_array(self, node: tree_sitter.Node, source_code: str) -> bool:
        """检查是否是PyMethodDef数组声明"""
        node_text = self._get_node_text(node, source_code)
        return 'PyMethodDef' in node_text and '{' in node_text
    
    def _parse_pymethoddef_array(self, node: tree_sitter.Node, source_code: str) -> Optional[Dict[str, Any]]:
        """解析PyMethodDef数组内容"""
        try:
            # 获取数组名称
            array_name = None
            methods = []
            
            # 遍历节点查找数组名和初始化列表
            for child in node.children:
                if child.type == 'init_declarator':
                    # 获取数组名
                    declarator = child.child_by_field_name('declarator')
                    if declarator:
                        array_name = self._get_node_text(declarator, source_code).split('[')[0]
                    
                    # 获取初始化列表
                    initializer = child.child_by_field_name('value')
                    if initializer and initializer.type == 'initializer_list':
                        methods = self._parse_method_entries(initializer, source_code)
            
            if array_name and methods:
                return {
                    'array_name': array_name,
                    'methods': methods
                }
        except Exception as e:
            print(f"解析PyMethodDef数组时出错: {e}")
        
        return None
    
    def _parse_method_entries(self, initializer_node: tree_sitter.Node, source_code: str) -> List[Dict[str, str]]:
        """解析方法条目"""
        methods = []
        
        for child in initializer_node.children:
            if child.type == 'initializer_list':
                # 解析单个方法条目 {"name", function, flags, "doc"}
                method_info = self._parse_single_method_entry(child, source_code)
                if method_info:
                    methods.append(method_info)
        
        return methods
    
    def _parse_single_method_entry(self, entry_node: tree_sitter.Node, source_code: str) -> Optional[Dict[str, str]]:
        """解析单个方法条目"""
        try:
            elements = []
            for child in entry_node.children:
                if child.type in ['string_literal', 'identifier', 'field_expression']:
                    element_text = self._get_node_text(child, source_code)
                    elements.append(element_text.strip())
            
            # 过滤掉NULL条目
            if len(elements) >= 2 and 'NULL' not in elements[0]:
                return {
                    'python_name': elements[0].strip('"'),  # Python中的函数名
                    'c_function': elements[1],              # C函数名
                    'flags': elements[2] if len(elements) > 2 else '',
                    'doc': elements[3].strip('"') if len(elements) > 3 else ''
                }
        except Exception as e:
            print(f"解析方法条目时出错: {e}")
        
        return None
    
    def _extract_pymoduledef_structs(self, node: tree_sitter.Node, source_code: str) -> List[Dict[str, str]]:
        """提取PyModuleDef结构体定义"""
        module_defs = []
        
        def traverse(node):
            if node.type == 'declaration':
                if self._is_pymoduledef_struct(node, source_code):
                    module_info = self._parse_pymoduledef_struct(node, source_code)
                    if module_info:
                        module_defs.append(module_info)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return module_defs
    
    def _is_pymoduledef_struct(self, node: tree_sitter.Node, source_code: str) -> bool:
        """检查是否是PyModuleDef结构体声明"""
        node_text = self._get_node_text(node, source_code)
        return 'PyModuleDef' in node_text and '{' in node_text
    
    def _parse_pymoduledef_struct(self, node: tree_sitter.Node, source_code: str) -> Optional[Dict[str, str]]:
        """解析PyModuleDef结构体"""
        try:
            struct_name = None
            module_name = None
            methods_array = None
            
            # 获取结构体名称
            for child in node.children:
                if child.type == 'init_declarator':
                    declarator = child.child_by_field_name('declarator')
                    if declarator:
                        struct_name = self._get_node_text(declarator, source_code)
                    
                    # 获取初始化列表
                    initializer = child.child_by_field_name('value')
                    if initializer and initializer.type == 'initializer_list':
                        # 解析结构体字段
                        fields = []
                        for field_child in initializer.children:
                            if field_child.type in ['string_literal', 'identifier', 'field_expression']:
                                field_text = self._get_node_text(field_child, source_code)
                                fields.append(field_text.strip())
                        
                        # 通常PyModuleDef的结构是: {PyModuleDef_HEAD_INIT, "module_name", NULL, -1, methods}
                        if len(fields) >= 2:
                            module_name = fields[1].strip('"')
                        if len(fields) >= 5:
                            methods_array = fields[4]
            
            if struct_name and module_name:
                return {
                    'struct_name': struct_name,
                    'module_name': module_name,
                    'methods_array': methods_array or ''
                }
        except Exception as e:
            print(f"解析PyModuleDef结构体时出错: {e}")
        
        return None
    
    def _extract_pyinit_functions(self, node: tree_sitter.Node, source_code: str) -> List[Dict[str, str]]:
        """提取PyInit函数"""
        init_functions = []
        
        def traverse(node):
            if node.type == 'function_definition':
                func_name = self._get_function_name(node, source_code)
                if func_name and func_name.startswith('PyInit_'):
                    # 提取模块名（去掉PyInit_前缀）
                    module_name = func_name[7:]  # 去掉"PyInit_"
                    
                    # 查找函数体中的PyModule_Create调用
                    module_struct = self._find_pymodule_create_arg(node, source_code)
                    
                    init_functions.append({
                        'function_name': func_name,
                        'module_name': module_name,
                        'module_struct': module_struct or ''
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return init_functions
    
    def _find_pymodule_create_arg(self, func_node: tree_sitter.Node, source_code: str) -> Optional[str]:
        """在函数中查找PyModule_Create的参数"""
        def traverse(node):
            if node.type == 'call_expression':
                func_name = self._get_called_function_name(node, source_code)
                if func_name == 'PyModule_Create':
                    # 获取第一个参数
                    args = node.child_by_field_name('arguments')
                    if args and args.children:
                        for arg in args.children:
                            if arg.type in ['identifier', 'unary_expression']:
                                return self._get_node_text(arg, source_code).strip('&')
            
            for child in node.children:
                result = traverse(child)
                if result:
                    return result
            return None
        
        return traverse(func_node)
