"""
Python调用提取器
用于从C代码中提取调用Python函数的代码和解析调用信息
专注于真正的Python函数调用，而非所有Python API
"""

import re

class PythonCallExtractor:
    def __init__(self):
        """初始化Python调用提取器"""
        pass
    
    def extract_python_calls_from_ast(self, tree_root_node, source_code):
        """
        从已解析的AST中提取Python函数调用信息
        
        Args:
            tree_root_node: tree-sitter解析后的根节点
            source_code: 源代码字符串
            
        Returns:
            dict: 包含原始代码片段和解析后的调用信息
        """
        # 提取原始代码片段
        raw_snippets = self._extract_raw_code_snippets(tree_root_node, source_code)
        
        # 解析Python函数调用信息
        parsed_calls = self._parse_python_calls(raw_snippets, source_code)
        
        return {
            'raw_code_snippets': raw_snippets,
            'parsed_calls': parsed_calls
        }
    
    def _extract_raw_code_snippets(self, node, source_code):
        """提取与Python函数调用相关的原始代码片段"""
        snippets = {
            'function_calls': [],      # PyObject_CallObject等真正的函数调用
            'function_lookup': [],     # PyDict_GetItemString等函数查找
            'argument_building': [],   # Py_BuildValue等参数构建
        }
        
        def traverse(current_node):
            # 检查函数调用
            if current_node.type == 'call_expression':
                call_text = self._get_node_text(current_node, source_code)
                
                # 只提取与Python函数调用直接相关的API
                if self._is_python_function_call(call_text):
                    snippets['function_calls'].append(call_text)
                elif self._is_function_lookup(call_text):
                    snippets['function_lookup'].append(call_text)
                elif self._is_argument_building(call_text):
                    snippets['argument_building'].append(call_text)
            
            # 递归遍历子节点
            for child in current_node.children:
                traverse(child)
        
        traverse(node)
        return snippets
    
    def _parse_python_calls(self, raw_snippets, source_code):
        """解析Python函数调用信息，构建完整的调用信息"""
        parsed_calls = []
        
        # 解析PyObject_CallObject调用
        for call in raw_snippets['function_calls']:
            if 'PyObject_CallObject' in call:
                parsed_call = self._parse_pyobject_call(call, source_code, raw_snippets)
                if parsed_call:
                    parsed_calls.append(parsed_call)
        
        return parsed_calls
    
    def _parse_pyobject_call(self, call_text, source_code, raw_snippets):
        """解析PyObject_CallObject调用，构建完整的Python函数调用信息"""
        # 匹配PyObject_CallObject(function, args)模式
        match = re.search(r'PyObject_CallObject\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', call_text)
        if not match:
            return None
        
        function_var = match.group(1).strip()
        args_var = match.group(2).strip()
        
        # 找到函数名
        function_name = self._find_function_name(function_var, source_code, raw_snippets)
        
        # 找到参数信息
        arguments = self._find_arguments(args_var, source_code, raw_snippets)
        
        # 构建完整的Python调用表示
        python_call = self._build_python_call_representation(function_name, arguments)
        
        return {
            'call_type': 'PyObject_CallObject',
            'function_name': function_name,
            'arguments': arguments,
            'python_call': python_call,  # 如 "add(1, 2, 7)"
            'raw_code': call_text
        }
    
    def _find_function_name(self, function_var, source_code, raw_snippets):
        """从源代码中找到函数名"""
        # 首先在function_lookup中查找
        for lookup in raw_snippets['function_lookup']:
            if function_var in lookup and 'PyDict_GetItemString' in lookup:
                match = re.search(rf'{re.escape(function_var)}\s*=\s*PyDict_GetItemString\s*\([^,]+,\s*"([^"]+)"\s*\)', lookup)
                if match:
                    return match.group(1)
        
        # 在整个源代码中查找
        pattern = rf'{re.escape(function_var)}\s*=\s*PyDict_GetItemString\s*\([^,]+,\s*"([^"]+)"\s*\)'
        match = re.search(pattern, source_code)
        if match:
            return match.group(1)
        return None
    
    def _find_arguments(self, args_var, source_code, raw_snippets):
        """从源代码中找到参数信息"""
        # 首先在argument_building中查找
        for arg_build in raw_snippets['argument_building']:
            if args_var in arg_build and 'Py_BuildValue' in arg_build:
                match = re.search(rf'{re.escape(args_var)}\s*=\s*Py_BuildValue\s*\(\s*"[^"]*"\s*,\s*([^)]+)\s*\)', arg_build)
                if match:
                    args_str = match.group(1)
                    # 解析参数
                    args = [arg.strip() for arg in args_str.split(',')]
                    return args
        
        # 在整个源代码中查找
        pattern = rf'{re.escape(args_var)}\s*=\s*Py_BuildValue\s*\(\s*"[^"]*"\s*,\s*([^)]+)\s*\)'
        match = re.search(pattern, source_code)
        if match:
            args_str = match.group(1)
            args = [arg.strip() for arg in args_str.split(',')]
            return args
        return []
    
    def _build_python_call_representation(self, function_name, arguments):
        """构建Python调用的字符串表示"""
        if not function_name:
            return None
        
        if arguments:
            args_str = ', '.join(str(arg) for arg in arguments)
            return f"{function_name}({args_str})"
        else:
            return f"{function_name}()"
    
    def _get_node_text(self, node, source_code):
        """获取节点对应的文本"""
        return source_code[node.start_byte:node.end_byte]
    
    def _is_python_function_call(self, call_text):
        """判断是否为Python函数调用API"""
        function_call_apis = [
            'PyObject_CallObject', 'PyObject_Call', 'PyObject_CallFunction',
            'PyObject_CallMethod', 'PyObject_CallFunctionObjArgs'
        ]
        return any(api in call_text for api in function_call_apis)
    
    def _is_function_lookup(self, call_text):
        """判断是否为函数查找API"""
        lookup_apis = [
            'PyDict_GetItemString', 'PyObject_GetAttrString',
            'PyModule_GetDict', 'PyImport_AddModule'
        ]
        return any(api in call_text for api in lookup_apis)
    
    def _is_argument_building(self, call_text):
        """判断是否为参数构建API"""
        arg_building_apis = [
            'Py_BuildValue', 'PyTuple_New', 'PyTuple_SetItem',
            'PyList_New', 'PyList_SetItem'
        ]
        return any(api in call_text for api in arg_building_apis)


# 便捷函数已移除，请使用 c_parser.py 中的统一API
# 例如：CCodeParser().extract_python_calls(file_path)