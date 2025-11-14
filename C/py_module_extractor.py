"""
C代码解析器
使用tree-sitter解析C代码，提取Python模块注册相关代码
"""

from typing import Dict, List, Optional
from tree_sitter import Language, Parser
import tree_sitter_c
import json


class CCodeParser:
    def __init__(self):
        self.c_language = Language(tree_sitter_c.language())
        self.parser = Parser(self.c_language)
    
    def parse_files(self, file_paths: List[str]) -> Dict:
        """
        解析多个C文件并合并提取Python模块注册信息
        
        Args:
            file_paths: C文件路径列表
            
        Returns:
            Dict: 合并后的Python模块注册信息
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        all_results = []
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            result = self._parse_single_code(code, file_path)
            all_results.append(result)
        
        return self._merge_results(all_results)
    
    def _parse_single_code(self, code: str, file_path: str) -> Dict:
        """
        解析单个C代码并提取组件（不构建链路）
        
        Args:
            code: C代码字符串
            file_path: 文件路径
            
        Returns:
            Dict: 包含提取的组件
        """
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        result = {
            'py_method_defs': self._extract_py_method_defs(root_node, code, file_path),
            'py_module_defs': self._extract_py_module_defs(root_node, code, file_path),
            'py_init_funcs': self._extract_py_init_funcs(root_node, code, file_path),
            'py_c_functions': self._extract_all_py_c_functions(root_node, code, file_path)
        }
        
        return result
    
    def _merge_results(self, results: List[Dict]) -> Dict:
        """
        合并多个解析结果并构建模块链路
        
        Args:
            results: 解析结果列表
            
        Returns:
            Dict: 合并后的结果
        """
        import re
        
        merged = {
            'py_method_defs': [],
            'py_module_defs': [],
            'py_init_funcs': [],
            'py_c_functions': [],
            'all_registrations': [],
            'module_chains': []
        }
        
        for result in results:
            merged['py_method_defs'].extend(result['py_method_defs'])
            merged['py_module_defs'].extend(result['py_module_defs'])
            merged['py_init_funcs'].extend(result['py_init_funcs'])
            merged['py_c_functions'].extend(result['py_c_functions'])
        
        method_def_map = {item['name']: item for item in merged['py_method_defs']}
        module_def_map = {item['name']: item for item in merged['py_module_defs']}
        c_function_map = {item['name']: item for item in merged['py_c_functions']}
        
        for init_func in merged['py_init_funcs']:
            chain = {
                'init_function': init_func['name'],
                'init_function_info': init_func,
                'method_def_info': None,
                'module_def_info': None,
                'c_functions': []
            }
            
            module_def_pattern = r'PyModule_Create\s*\(\s*&\s*(\w+)\s*\)'
            match = re.search(module_def_pattern, init_func['code'])
            module_def_name = match.group(1) if match else None
            
            if module_def_name and module_def_name in module_def_map:
                module_def = module_def_map[module_def_name]
                chain['module_def_info'] = module_def
                
                method_def_pattern = r',\s*(\w+)\s*\}'
                matches = re.findall(method_def_pattern, module_def['code'])
                method_def_name = matches[-1] if matches else None
                
                if method_def_name and method_def_name in method_def_map:
                    method_def = method_def_map[method_def_name]
                    chain['method_def_info'] = method_def
                    
                    func_pattern = r'\{\s*"[^"]+"\s*,\s*(\w+)\s*,\s*METH_'
                    func_matches = re.findall(func_pattern, method_def['code'])
                    
                    for func_name in func_matches:
                        if func_name in c_function_map:
                            chain['c_functions'].append(c_function_map[func_name])
            
            merged['module_chains'].append(chain)
        
        merged['all_registrations'] = (merged['py_method_defs'] + merged['py_module_defs'] + 
                                       merged['py_init_funcs'] + merged['py_c_functions'])
        
        return merged
    
    def _extract_py_method_defs(self, root_node, code: str, file_path: str) -> List[Dict]:
        """提取PyMethodDef数组定义"""
        method_defs = []
        
        # 查找所有变量声明
        for node in self._traverse_tree(root_node):
            if node.type == 'declaration':
                # 检查是否是PyMethodDef类型
                decl_text = code[node.start_byte:node.end_byte]
                if 'PyMethodDef' in decl_text:
                    # 提取变量名
                    var_name = self._extract_variable_name(node, code)
                    
                    method_defs.append({
                        'type': 'PyMethodDef',
                        'name': var_name,
                        'code': decl_text,
                        'file_path': file_path,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte
                    })
        
        return method_defs
    
    def _extract_py_module_defs(self, root_node, code: str, file_path: str) -> List[Dict]:
        """提取PyModuleDef结构定义"""
        module_defs = []
        
        for node in self._traverse_tree(root_node):
            if node.type == 'declaration':
                decl_text = code[node.start_byte:node.end_byte]
                if 'PyModuleDef' in decl_text:
                    var_name = self._extract_variable_name(node, code)
                    
                    module_defs.append({
                        'type': 'PyModuleDef',
                        'name': var_name,
                        'code': decl_text,
                        'file_path': file_path,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte
                    })
        
        return module_defs
    
    def _extract_py_init_funcs(self, root_node, code: str, file_path: str) -> List[Dict]:
        """提取PyInit_*函数定义"""
        init_funcs = []
        
        for node in self._traverse_tree(root_node):
            if node.type == 'function_definition':
                func_text = code[node.start_byte:node.end_byte]
                func_name = self._extract_function_name(node, code)
                
                # 检查是否是PyInit_开头的函数或包含PyMODINIT_FUNC
                if func_name and (func_name.startswith('PyInit_') or 'PyMODINIT_FUNC' in func_text):
                    init_funcs.append({
                        'type': 'PyInit_Function',
                        'name': func_name,
                        'code': func_text,
                        'file_path': file_path,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte
                    })
        
        return init_funcs
    
    def _extract_registered_function_names(self, py_method_defs: List[Dict], code: str) -> set:
        """
        从PyMethodDef数组中提取注册的C函数名
        
        PyMethodDef格式: {"python_name", c_function_name, METH_VARARGS, "doc"}
        """
        import re
        
        func_names = set()
        
        for method_def in py_method_defs:
            method_code = method_def['code']
            # 匹配 {"name", func_name, ...} 格式
            # 查找所有类似 {"...", identifier, METH_...} 的模式
            pattern = r'\{\s*"[^"]+"\s*,\s*(\w+)\s*,\s*METH_'
            matches = re.findall(pattern, method_code)
            func_names.update(matches)
        
        return func_names
    
    def _extract_all_py_c_functions(self, root_node, code: str, file_path: str) -> List[Dict]:
        """
        提取所有符合Python/C API签名的函数
        """
        c_functions = []
        
        for node in self._traverse_tree(root_node):
            if node.type == 'function_definition':
                func_text = code[node.start_byte:node.end_byte]
                func_name = self._extract_function_name(node, code)
                
                # 检查是否符合Python C API签名
                # 1. 返回类型是 PyObject *
                # 2. 参数是 (PyObject *self, PyObject *args) 或类似形式
                if func_name and self._is_python_c_api_function(node, code):
                    c_functions.append({
                        'type': 'Python_C_Function',
                        'name': func_name,
                        'code': func_text,
                        'file_path': file_path,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte
                    })
        
        return c_functions
    
    def _is_python_c_api_function(self, function_node, code: str) -> bool:
        """
        检查函数是否符合Python C API签名
        
        典型签名:
        - static PyObject *func_name(PyObject *self, PyObject *args)
        - PyObject *func_name(PyObject *self, PyObject *args)
        """
        func_text = code[function_node.start_byte:function_node.end_byte]
        
        # 检查返回类型是否包含 PyObject
        if 'PyObject' not in func_text[:200]:  # 只检查函数开头
            return False
        
        # 检查参数列表
        # 寻找 parameter_list 节点
        for child in function_node.children:
            if child.type == 'pointer_declarator':
                for subchild in child.children:
                    if subchild.type == 'function_declarator':
                        return self._check_parameter_list(subchild, code)
            elif child.type == 'function_declarator':
                return self._check_parameter_list(child, code)
        
        return False
    
    def _check_parameter_list(self, declarator_node, code: str) -> bool:
        """检查参数列表是否符合Python C API格式"""
        for child in declarator_node.children:
            if child.type == 'parameter_list':
                param_text = code[child.start_byte:child.end_byte]
                # 检查是否包含两个 PyObject 参数
                # 典型形式: (PyObject *self, PyObject *args)
                if param_text.count('PyObject') >= 2:
                    return True
        return False
    
    def _build_module_chains(self, py_init_funcs: List[Dict], py_module_defs: List[Dict], 
                            py_method_defs: List[Dict], py_c_functions: List[Dict], code: str) -> List[Dict]:
        """
        构建完整的模块注册链路
        
        链路: PyInit_xxx -> PyModuleDef -> PyMethodDef -> C函数
        
        Returns:
            List[Dict]: 每个字典包含一个完整的注册链路
        """
        import re
        
        chains = []
        
        # 为每个PyInit函数构建链路
        for init_func in py_init_funcs:
            chain = {
                'init_function': init_func['name'],
                'init_function_info': init_func,
                'module_def': None,
                'module_def_info': None,
                'method_def': None,
                'method_def_info': None,
                'c_functions': []
            }
            
            # 从PyInit函数中提取PyModuleDef变量名
            # 匹配 PyModule_Create(&VariableName) 或 PyModule_Create(&VariableName)
            module_def_pattern = r'PyModule_Create\s*\(\s*&\s*(\w+)\s*\)'
            match = re.search(module_def_pattern, init_func['code'])
            
            if match:
                module_def_name = match.group(1)
                chain['module_def'] = module_def_name
                
                # 查找对应的PyModuleDef定义
                for module_def in py_module_defs:
                    if module_def['name'] == module_def_name:
                        chain['module_def_info'] = module_def
                        
                        # 从PyModuleDef中提取PyMethodDef变量名
                        # PyModuleDef格式: {PyModuleDef_HEAD_INIT, "name", NULL, -1, MethodsName}
                        # 提取最后一个逗号后、右花括号前的标识符
                        method_def_pattern = r',\s*(\w+)\s*\}'
                        matches = re.findall(method_def_pattern, module_def['code'])
                        
                        if matches:
                            method_def_name = matches[-1]
                            chain['method_def'] = method_def_name
                            
                            # 查找对应的PyMethodDef定义
                            for method_def in py_method_defs:
                                if method_def['name'] == method_def_name:
                                    chain['method_def_info'] = method_def
                                    
                                    # 从PyMethodDef中提取注册的C函数
                                    registered_funcs = self._extract_registered_function_names([method_def], code)
                                    
                                    # 查找对应的C函数定义
                                    for func_name in registered_funcs:
                                        for c_func in py_c_functions:
                                            if c_func['name'] == func_name:
                                                chain['c_functions'].append(c_func)
                                    
                                    break
                        
                        break
            
            chains.append(chain)
        
        return chains
    
    def _traverse_tree(self, node):
        """遍历语法树的所有节点"""
        cursor = node.walk()
        
        visited_children = False
        while True:
            if not visited_children:
                yield cursor.node
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break
    
    def _extract_variable_name(self, declaration_node, code: str) -> Optional[str]:
        """从声明节点中提取变量名"""
        for child in declaration_node.children:
            if child.type == 'init_declarator':
                for subchild in child.children:
                    if subchild.type == 'array_declarator':
                        for identifier_node in subchild.children:
                            if identifier_node.type == 'identifier':
                                return code[identifier_node.start_byte:identifier_node.end_byte]
                    elif subchild.type == 'identifier':
                        return code[subchild.start_byte:subchild.end_byte]
            elif child.type == 'identifier':
                return code[child.start_byte:child.end_byte]
        return None
    
    def _extract_function_name(self, function_node, code: str) -> Optional[str]:
        """从函数定义节点中提取函数名"""
        for child in function_node.children:
            if child.type == 'function_declarator':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        return code[subchild.start_byte:subchild.end_byte]
            elif child.type == 'pointer_declarator':
                # 处理指针返回类型的函数，如 PyObject *func_name(...)
                for subchild in child.children:
                    if subchild.type == 'function_declarator':
                        for identifier_node in subchild.children:
                            if identifier_node.type == 'identifier':
                                return code[identifier_node.start_byte:identifier_node.end_byte]
        return None



def format_registration_info(result: Dict, verbose: bool = True) -> str:
    """
    格式化输出注册信息（简化版，适合LLM使用）
    
    Args:
        result: parse_file或parse_code返回的结果
        verbose: 是否显示详细代码（默认True）
        
    Returns:
        str: 格式化的字符串，包含所有注册相关的代码
    """
    lines = []
    
    # 按模块输出所有注册代码
    if result.get('module_chains'):
        for i, chain in enumerate(result['module_chains'], 1):
            if len(result['module_chains']) > 1:
                lines.append(f"# Module {i}: {chain['init_function']}")
                lines.append("")
            
            # PyMethodDef
            if chain.get('method_def_info'):
                lines.append(chain['method_def_info']['code'])
                lines.append("")
            
            # PyModuleDef
            if chain.get('module_def_info'):
                lines.append(chain['module_def_info']['code'])
                lines.append("")
            
            # PyInit函数
            if chain.get('init_function_info'):
                lines.append(chain['init_function_info']['code'])
                lines.append("")
            
            # 注册的C函数
            if chain.get('c_functions'):
                for func in chain['c_functions']:
                    lines.append(func['code'])
                    lines.append("")
    else:
        # 降级方案：按顺序输出所有组件
        for item in result.get('py_method_defs', []):
            lines.append(item['code'])
            lines.append("")
        
        for item in result.get('py_module_defs', []):
            lines.append(item['code'])
            lines.append("")
        
        for item in result.get('py_init_funcs', []):
            lines.append(item['code'])
            lines.append("")
        
        for item in result.get('py_c_functions', []):
            lines.append(item['code'])
            lines.append("")
    
    return "\n".join(lines).strip()


def format_registration_info_json(result: Dict) -> str:
    """
    格式化输出模块注册信息（JSON格式）
    与c_python_call_extraction.json保持一致的格式
    
    Args:
        result: parse_files返回的结果
        
    Returns:
        str: JSON格式的字符串
    """
    json_data = {
        "module_chains": result.get('module_chains', [])
    }
    return json.dumps(json_data, indent=2, ensure_ascii=False)


def format_registration_info_text(result: Dict) -> str:
    """
    格式化输出模块注册信息（文本格式）
    与c_python_call_extraction.txt保持一致的格式
    
    Args:
        result: parse_files返回的结果
        
    Returns:
        str: 文本格式的字符串
    """
    lines = []
    
    if result.get('module_chains'):
        for idx, chain in enumerate(result['module_chains'], 1):
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"C中的python注册模块 #{idx}")
            lines.append("=" * 80)
            lines.append("")
            
            if chain.get('init_function_info'):
                lines.append(f"{chain['init_function_info']['code']}")
                lines.append("")
            
            if chain.get('module_def_info'):
                lines.append(f"{chain['module_def_info']['code']}")
                lines.append("")
            
            if chain.get('method_def_info'):
                lines.append(f"{chain['method_def_info']['code']}")
                lines.append("")
            
            if chain.get('c_functions'):
                for func in chain['c_functions']:
                    lines.append(f"{func['code']}")
                    lines.append("")
    
    return "\n".join(lines)