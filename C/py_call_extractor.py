"""
Python调用提取器
"""

from typing import Dict, List, Optional, Set
from tree_sitter import Language, Parser, Node
try:
    from .analysis import DDG
except ImportError:
    from analysis import DDG
import tree_sitter_c
import json    

class PythonCallExtractor:
    """
    Python调用提取器 - 简化算法
    
    核心思路:
    1. 找到调用语句 (如 PyObject *ret = PyObject_CallObject(fn, args);)
    2. 提取调用涉及的变量 (fn, args, ret)
    3. 获取函数所有语句的 def/use
    4. 逐条比对：如果语句的 def/use 包含追踪变量，则添加
    5. 从新添加的语句中发现新变量，继续追踪
    6. 循环直到没有新变量
    """
    
    def __init__(self):
        self.c_language = Language(tree_sitter_c.language())
        self.parser = Parser(self.c_language)
        self.ddg_builder = DDG()
        self.all_functions = {}
        self.file_contents = {}
    
    def parse_files(self, file_paths: List[str]) -> Dict:
        """
        两阶段处理多文件（优化性能）：
        阶段1：遍历所有文件，提取所有函数定义，构建全局函数注册表
        阶段2：遍历每个函数，如果包含Python调用则构建DDG并深度分析
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        parsed_files = {}
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            parsed_files[file_path] = code
        
        self.file_contents = parsed_files
        self._get_all_functions(parsed_files)
        
        all_calls = self._analyze_all_functions()
        
        return {
            'python_calls': all_calls,
            'total_calls': len(all_calls),
            'global_functions': list(self.all_functions.keys()),
            'total_functions': sum(len(funcs) for funcs in self.all_functions.values())
        }
    
    def _get_all_functions(self, parsed_files: Dict[str, str]):
        """
        阶段1：获取所有文件中的函数
        
        遍历所有文件，提取所有函数定义，建立函数名到函数信息的映射
        这样在分析Python调用时，可以跨文件查找函数定义
        
        Args:
            parsed_files: {file_path: code} 字典
        """
        self.all_functions = {}
        
        for file_path, code in parsed_files.items():
            tree = self.parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node
            
            functions = self._find_functions(root_node, code)
            
            for func_node in functions:
                func_name = self._get_function_name_from_definition(func_node, code)
                if func_name:
                    func_code = func_node.text.decode('utf-8')
                    func_line = func_node.start_point[0] + 1
                    
                    if func_name not in self.all_functions:
                        self.all_functions[func_name] = []
                    
                    self.all_functions[func_name].append({
                        'function_name': func_name,
                        'file': file_path,
                        'line': func_line,
                        'code': func_code,
                        'node': func_node,
                        'parsed_tree': tree
                    })
    
    def _analyze_all_functions(self) -> List[Dict]:
        """
        阶段2：分析所有函数中的Python调用
        
        遍历全局函数注册表中的每个函数：
        1. 检查是否包含Python C API调用（轻量级AST遍历）
        2. 如果包含，则构建DDG并进行深度分析
        3. 提取调用上下文和相关函数定义
        
        优势：按需构建DDG，避免浪费
        """
        all_calls = []
        
        for func_name, func_infos in self.all_functions.items():
            for func_info in func_infos:
                func_code = func_info['code']
                file_path = func_info['file']
                
                func_tree = self.parser.parse(bytes(func_code, "utf8"))
                func_root = func_tree.root_node
                
                call_nodes = self._find_python_call_expressions(func_root, func_code)
                
                if not call_nodes:
                    continue
                
                ddg = self.ddg_builder.construct_ddg(func_code)
                if not ddg:
                    continue
                
                for call_node in call_nodes:
                    call_info = self._extract_python_call_context(call_node, func_code, ddg, 0)
                    if call_info:
                        call_info['file'] = file_path
                        call_info['containing_function'] = func_name
                        call_info['function_definitions'] = self._extract_function_definitions_from_global(
                            call_info['context_statements']
                        )
                        all_calls.append(call_info)
        
        return all_calls
    
    def _find_functions(self, node: Node, code: str) -> List[Node]:
        functions = []
        if node.type == 'function_definition':
            functions.append(node)
        for child in node.children:
            functions.extend(self._find_functions(child, code))
        return functions
    
    def _find_python_call_expressions(self, node: Node, code: str) -> List[Node]:
        """
        查找Python C API调用表达式
        
        递归遍历AST，查找所有Python C API调用节点
        只返回Python相关调用，不包括普通C函数调用
        
        Args:
            node: AST节点
            code: 代码字符串（用于提取函数名）
            
        Returns:
            Python C API调用节点列表
        """
        calls = []
        if node.type == 'call_expression':
            function_name = self._get_function_name(node, code)
            if self._is_python_call_function(function_name):
                calls.append(node)
        for child in node.children:
            calls.extend(self._find_python_call_expressions(child, code))
        return calls
    
    def _get_function_name(self, call_node: Node, code: str) -> str:
        for child in call_node.children:
            if child.type in ['identifier', 'field_expression']:
                func_name = child.text.decode('utf-8')
                return func_name
        return ""
    
    def _is_python_call_function(self, function_name: str) -> bool:
        python_call_funcs = [
            'PyObject_CallObject',
            'PyObject_CallFunction',
            'PyObject_CallMethod',
            'PyObject_Call',
            'PyObject_CallFunctionObjArgs',
            'PyObject_CallMethodObjArgs',
            'PyEval_CallObject',
            'PyEval_CallFunction',
            'PyEval_CallMethod'
        ]
        return function_name in python_call_funcs
    
    def _extract_python_call_context(self, call_node: Node, code: str, ddg, func_start_line: int = 0) -> Optional[Dict]:
        """
        提取Python C API调用的完整上下文
        
        通过数据依赖图(DDG)分析，追踪与调用相关的所有变量和语句，
        构建从函数对象获取、参数构建、实际调用到返回值使用的完整调用链。
        
        Args:
            call_node: Python C API调用的AST节点
            code: 函数代码字符串
            ddg: 数据依赖图
            func_start_line: 函数起始行号（用于计算绝对行号）
            
        Returns:
            调用上下文信息字典，包含：
            - call_function: 调用的API函数名
            - call_line: 调用行号
            - call_code: 调用代码字符串
            - context_statements: 与调用相关的语句列表
        """
        function_name = self._get_function_name(call_node, code)
        call_line = call_node.start_point[0] + 1
        call_code = call_node.text.decode('utf-8')
        
        vars_to_track = set()
        for node in ddg.nodes:
            if node.line == call_line:
                defs = ddg.defs.get(node.id, set())
                uses = ddg.uses.get(node.id, set())
                vars_to_track = defs | uses
                break
        
        context_statements = self._extract_related_statements(ddg, vars_to_track)
        
        context_statements.sort(key=lambda x: x['line'])
        
        return {
            'call_function': function_name,
            'call_line': call_line,
            'call_code': call_code,
            'context_statements': context_statements
        }
    
    def _extract_related_statements(self, ddg, initial_vars: Set[str]) -> List[Dict]:
        """
        递归追踪 - 核心算法
        
        步骤：
        1. 初始化：vars_to_track = {fn, args, ret}
        2. 遍历所有语句，检查其 def/use 是否包含 vars_to_track 中的变量
        3. 如果包含，添加该语句，并将该语句的所有 def/use 变量加入 vars_to_track
        4. 重复步骤 2-3，直到没有新语句被添加
        """
        vars_to_track = set(initial_vars)
        added_statements = set()
        context = []
        
        changed = True
        while changed:
            changed = False
            
            for node in ddg.nodes:
                node_id = node.id
                
                if node.line in added_statements:
                    continue
                
                defs = ddg.defs.get(node_id, set())
                uses = ddg.uses.get(node_id, set())
                all_vars = defs | uses
                
                if all_vars & vars_to_track:
                    context.append({
                        'line': node.line,
                        'text': node.text,
                        'type': node.type,
                        'defs': defs,
                        'uses': uses
                    })
                    added_statements.add(node.line)
                    
                    old_size = len(vars_to_track)
                    vars_to_track.update(all_vars)
                    
                    if len(vars_to_track) > old_size:
                        changed = True
        
        context.sort(key=lambda x: x['line'])
        return context
    
    def _extract_function_definitions_from_global(self, context_statements: List[Dict]) -> List[Dict]:
        """
        从全局函数注册表中提取被调用的函数定义（支持跨文件）
        
        Args:
            context_statements: 上下文语句列表
            
        Returns:
            函数定义列表，包含跨文件的所有匹配函数
        """
        function_defs = []
        found_functions = set()
        
        for stmt in context_statements:
            stmt_calls = self._find_function_calls_in_stmt(stmt['text'])
            for func_name in stmt_calls:
                if func_name in self.all_functions and func_name not in found_functions:
                    found_functions.add(func_name)
                    for func_info in self.all_functions[func_name]:
                        function_defs.append({
                            'function_name': func_info['function_name'],
                            'file': func_info['file'],
                            'line': func_info['line'],
                            'code': func_info['code']
                        })
        
        return function_defs
    
    def _find_function_calls_in_stmt(self, text: str) -> List[str]:
        """
        从调用语句中提取函数名称
        """
        tree = self.parser.parse(bytes(text, "utf8"))
        root = tree.root_node
        
        function_calls = []
        
        def extract_calls(node):
            if node.type == 'call_expression':
                func_name = self._get_function_name(node, text)
                if func_name:
                    function_calls.append(func_name)
            for child in node.children:
                extract_calls(child)
        
        extract_calls(root)
        return function_calls
    
    def _get_function_name_from_definition(self, func_node: Node, code: str) -> str:
        """
        从函数定义节点中提取函数名
        支持多种声明形式：
        - function_declarator: void func()
        - pointer_declarator: char *func() 或 PyObject *func()
        """
        def extract_from_node(node):
            if node.type == 'function_declarator':
                for child in node.children:
                    if child.type == 'identifier':
                        return child.text.decode('utf-8')
            elif node.type == 'pointer_declarator':
                for child in node.children:
                    result = extract_from_node(child)
                    if result:
                        return result
            return ""
        
        for child in func_node.children:
            result = extract_from_node(child)
            if result:
                return result
        return ""


def format_call_info_json(result: Dict) -> str:
    """
    格式化输出Python C API调用的完整上下文（JSON格式）
    格式与模块注册保持一致，包含type, name, code等元数据
    """
    python_calls = result.get('python_calls', [])
    
    formatted_calls = []
    for call in python_calls:
        call_entry = {
            "call_info": {
                "type": "Python_C_API_Call",
                "function": call.get('call_function', ''),
                "code": call.get('call_code', ''),
                "line": call.get('call_line', 0),
                "file": call.get('file', ''),
                "containing_function": call.get('containing_function', '')
            },
            "context_statements": [
                {
                    "line": stmt['line'],
                    "code": stmt['text'],
                    "type": stmt['type']
                }
                for stmt in call.get('context_statements', [])
            ]
        }
        
        if call.get('function_definitions'):
            call_entry["function_definitions"] = [
                {
                    "type": "Helper_Function",
                    "name": func_def.get('function_name', ''),
                    "code": func_def.get('code', ''),
                    "line": func_def.get('line', 0),
                    "file": func_def.get('file', '')
                }
                for func_def in call['function_definitions']
            ]
        
        formatted_calls.append(call_entry)
    
    output = {"python_api_calls": formatted_calls}
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_call_info_text(result: Dict) -> str:
    """
    格式化输出Python C API调用的完整代码片段（文本格式）
    格式与模块注册保持一致，使用分隔线和标题
    """
    lines = []
    python_calls = result.get('python_calls', [])
    
    for i, call in enumerate(python_calls, 1):
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"C中的Python API调用 #{i}")
        lines.append("=" * 80)
        lines.append("")
        
        if call.get('context_statements'):
            for stmt in call['context_statements']:
                lines.append(stmt['text'])
            lines.append("")
        
        if call.get('function_definitions'):
            for func_def in call['function_definitions']:
                lines.append(func_def['code'])
                lines.append("")
    
    return "\n".join(lines)


if __name__ == '__main__':
    extractor = PythonCallExtractor()
    
    test_file = '//home/kansx/Papers/Python-C/C_with_Python/DynamicNameError/sample2/DynamicNameError_True.c'
    
    result = extractor.parse_files(test_file)
    
    print("========== 文本格式输出 ==========")
    print(format_call_info_text(result))
    print("\n\n")
    print("========== JSON格式输出 ==========")
    print(format_call_info_json(result))