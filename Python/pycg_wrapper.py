"""
PyCG 包装器
封装 PyCG 的调用接口，提供简单易用的 API 来生成 Python 代码的调用图
"""

import sys
import os
from typing import Dict, Any, List, Optional

# 添加 PyCG 到 Python 路径
PYCG_PATH = os.path.join(os.path.dirname(__file__), 'PyCG')
if PYCG_PATH not in sys.path:
    sys.path.insert(0, PYCG_PATH)

from pycg.pycg import CallGraphGenerator
from pycg import formats
from pycg.utils.constants import CALL_GRAPH_OP, KEY_ERR_OP


class PyCGWrapper:
    """PyCG 包装器，提供简单的接口来生成调用图"""
    
    def __init__(self, entry_points: List[str], package: Optional[str] = None, 
                 max_iter: int = -1, operation: str = CALL_GRAPH_OP):
        """
        初始化 PyCG 包装器
        
        Args:
            entry_points: 入口点文件列表，可以是单个文件或多个文件
            package: 包含待分析代码的包路径
            max_iter: 最大迭代次数，-1 表示固定点迭代
            operation: 操作类型，'call-graph' 或 'key-error'
        """
        self.entry_points = entry_points if isinstance(entry_points, list) else [entry_points]
        self.package = package
        self.max_iter = max_iter
        self.operation = operation
        self.cg = None
        
    def analyze(self):
        """执行分析，生成调用图"""
        self.cg = CallGraphGenerator(
            self.entry_points, 
            self.package, 
            self.max_iter, 
            self.operation
        )
        self.cg.analyze()
        return self
    
    def get_simple_call_graph(self) -> Dict[str, List[str]]:
        """
        获取简单格式的调用图
        
        Returns:
            Dict: 调用图的字典表示，键为函数名，值为被调用函数列表
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        formatter = formats.Simple(self.cg)
        return formatter.generate()
    
    def get_fasten_call_graph(self, product: str = "", forge: str = "PyPI", 
                              version: str = "0.1.0", timestamp: int = 0) -> Dict[str, Any]:
        """
        获取 FASTEN 格式的调用图
        
        Args:
            product: 包名
            forge: 来源（如 PyPI）
            version: 版本号
            timestamp: 时间戳
            
        Returns:
            Dict: FASTEN 格式的调用图
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        formatter = formats.Fasten(
            self.cg, 
            self.package, 
            product, 
            forge, 
            version, 
            timestamp
        )
        return formatter.generate()
    
    def get_raw_output(self) -> Dict[str, set]:
        """
        获取原始调用图输出
        
        Returns:
            Dict: 原始调用图
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        return self.cg.output()
    
    def get_functions(self) -> List[str]:
        """
        获取所有函数列表
        
        Returns:
            List[str]: 函数名列表
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        return self.cg.output_functions()
    
    def get_classes(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有类信息
        
        Returns:
            Dict: 类信息字典
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        return self.cg.output_classes()
    
    def get_external_calls(self, include_builtin: bool = True,
                          product: str = "", forge: str = "PyPI",
                          version: str = "0.1.0", timestamp: int = 0) -> Dict[str, Any]:
        """
        获取所有外部调用信息（基于 FASTEN 格式，更精确）
        
        使用 FASTEN 格式来获取外部调用信息，明确区分 internal 和 external modules。
        
        Args:
            include_builtin: 是否包含内置函数，默认为 True
            product: 包名（用于 FASTEN 格式）
            forge: 来源（用于 FASTEN 格式）
            version: 版本号（用于 FASTEN 格式）
            timestamp: 时间戳（用于 FASTEN 格式）
            
        Returns:
            Dict: 完整的外部调用信息
                {
                    'undefined_functions': [函数名列表],
                    'callers': {函数名: [调用者列表]},
                    'by_module': {模块: [函数列表]},
                    'statistics': {统计信息},
                    'call_edges': [(caller, callee), ...],
                    'fasten_details': {FASTEN格式的详细信息}
                }
        """
        if self.cg is None:
            raise RuntimeError("需要先调用 analyze() 方法进行分析")
        
        # 获取 FASTEN 格式的调用图
        fasten_cg = self.get_fasten_call_graph(product, forge, version, timestamp)
        
        # 提取模块信息
        external_modules_raw = fasten_cg.get('modules', {}).get('external', {})
        internal_modules = fasten_cg.get('modules', {}).get('internal', {})
        
        # 提取调用信息
        graph = fasten_cg.get('graph', {})
        internal_calls = graph.get('internalCalls', [])
        external_calls_raw = graph.get('externalCalls', [])
        
        # 构建节点ID到函数名的映射
        id_to_func = {}
        
        # 处理内部模块
        for module_uri, module_info in internal_modules.items():
            namespaces = module_info.get('namespaces', {})
            for node_id, ns_info in namespaces.items():
                namespace = ns_info.get('namespace', '')
                id_to_func[node_id] = namespace
        
        # 处理外部模块，提取函数名
        external_functions_list = []  # 外部函数名列表
        by_module = {}  # 按模块分组
        
        for module_name, module_info in external_modules_raw.items():
            namespaces = module_info.get('namespaces', {})
            for node_id, ns_info in namespaces.items():
                namespace = ns_info.get('namespace', '')
                id_to_func[node_id] = namespace
                
                # 提取函数名（从 namespace 中）
                if '//' in namespace:
                    # 格式: //module//function 或 //module//module.function
                    parts = namespace.split('//')
                    if len(parts) >= 2:
                        module = parts[1]
                        func_name = parts[2] if len(parts) > 2 else ''
                        
                        # 处理函数名（可能包含模块前缀）
                        if func_name and '.' in func_name:
                            # 如 host.tick，去掉模块前缀
                            func_name = func_name.split('.')[-1]
                        
                        # 构建完整的函数名
                        if module == '.builtin':
                            full_name = f'<builtin>.{func_name}' if func_name else '<builtin>'
                        else:
                            full_name = f'{module}.{func_name}' if func_name else module
                        
                        external_functions_list.append(full_name)
                        
                        # 按模块分组
                        if module not in by_module:
                            by_module[module] = []
                        if full_name not in by_module[module]:
                            by_module[module].append(full_name)
        
        # 过滤内置函数（如果需要）
        if not include_builtin:
            external_functions_list = [f for f in external_functions_list 
                                       if not f.startswith('<builtin>.')]
            # 也从 by_module 中移除内置模块
            by_module = {k: v for k, v in by_module.items() 
                        if k != '.builtin'}
        
        # 解析外部调用，构建调用边和调用者映射
        call_edges = []
        callers_map = {}
        
        for call in external_calls_raw:
            caller_id = str(call[0])
            callee_id = str(call[1])
            caller_name = id_to_func.get(caller_id, f"node_{caller_id}")
            callee_name = id_to_func.get(callee_id, f"node_{callee_id}")
            
            # 转换 callee_name 为标准格式
            if '//' in callee_name:
                parts = callee_name.split('//')
                if len(parts) >= 2:
                    module = parts[1]
                    func_name = parts[2] if len(parts) > 2 else ''
                    
                    # 处理函数名（可能包含模块前缀）
                    if func_name and '.' in func_name:
                        # 如 host.tick，去掉模块前缀
                        func_name = func_name.split('.')[-1]
                    
                    if module == '.builtin':
                        callee_standard = f'<builtin>.{func_name}' if func_name else '<builtin>'
                    else:
                        callee_standard = f'{module}.{func_name}' if func_name else module
                else:
                    callee_standard = callee_name
            else:
                callee_standard = callee_name
            
            # 过滤内置函数（如果需要）
            if not include_builtin and callee_standard.startswith('<builtin>.'):
                continue
            
            # 添加调用边
            call_edges.append((caller_name, callee_standard))
            
            # 构建 callers 映射
            if callee_standard not in callers_map:
                callers_map[callee_standard] = []
            if caller_name not in callers_map[callee_standard]:
                callers_map[callee_standard].append(caller_name)
        
        # 统计信息
        statistics = {
            'total_undefined': len(set(external_functions_list)),
            'modules_count': len(by_module),
            'modules': list(by_module.keys()),
            'by_module': {mod: len(funcs) for mod, funcs in by_module.items()},
            'total_call_edges': len(call_edges),
            'total_external_calls': len(external_calls_raw),
            'total_internal_calls': len(internal_calls)
        }
        
        return {
            'undefined_functions': sorted(list(set(external_functions_list))),
            'callers': callers_map,
            'by_module': by_module,
            'statistics': statistics,
            'call_edges': call_edges,
            'fasten_details': {
                'external_modules': external_modules_raw,
                'internal_modules': internal_modules,
                'id_to_func_map': id_to_func,
                'graph': graph
            }
        }


def generate_call_graph(file_path: str, package: Optional[str] = None, 
                       format_type: str = 'simple') -> Dict[str, Any]:
    """
    便捷函数：生成单个文件的调用图
    
    Args:
        file_path: Python 文件路径
        package: 包路径，如果不提供则使用文件所在目录
        format_type: 格式类型，'simple' 或 'fasten'
        
    Returns:
        Dict: 调用图
    """
    if package is None:
        package = os.path.dirname(os.path.abspath(file_path))
    
    wrapper = PyCGWrapper([file_path], package)
    wrapper.analyze()
    
    if format_type == 'simple':
        return wrapper.get_simple_call_graph()
    elif format_type == 'fasten':
        product = os.path.basename(package)
        return wrapper.get_fasten_call_graph(product=product)
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


def generate_call_graph_for_package(package_path: str, entry_points: Optional[List[str]] = None,
                                     format_type: str = 'simple') -> Dict[str, Any]:
    """
    便捷函数：生成整个包的调用图
    
    Args:
        package_path: 包路径
        entry_points: 入口点列表，如果不提供则自动查找所有 .py 文件
        format_type: 格式类型，'simple' 或 'fasten'
        
    Returns:
        Dict: 调用图
    """
    if entry_points is None:
        # 自动查找所有 Python 文件
        entry_points = []
        for root, dirs, files in os.walk(package_path):
            for file in files:
                if file.endswith('.py'):
                    entry_points.append(os.path.join(root, file))
    
    wrapper = PyCGWrapper(entry_points, package_path)
    wrapper.analyze()
    
    if format_type == 'simple':
        return wrapper.get_simple_call_graph()
    elif format_type == 'fasten':
        product = os.path.basename(package_path)
        return wrapper.get_fasten_call_graph(product=product)
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


if __name__ == "__main__":
    # 示例用法
    import json
    
    # 示例 1: 生成简单格式的调用图
    print("示例 1: 生成简单格式的调用图")
    print("-" * 50)
    
    # 这里需要一个实际的 Python 文件路径
    # cg = generate_call_graph("example.py", format_type='simple')
    # print(json.dumps(cg, indent=2))
    
    # 示例 2: 使用面向对象的接口
    print("\n示例 2: 使用面向对象的接口")
    print("-" * 50)
    
    # wrapper = PyCGWrapper(["example.py"], ".")
    # wrapper.analyze()
    # simple_cg = wrapper.get_simple_call_graph()
    # fasten_cg = wrapper.get_fasten_call_graph(product="example", version="1.0.0")
    # print("Simple format:", json.dumps(simple_cg, indent=2))
    # print("FASTEN format:", json.dumps(fasten_cg, indent=2))
    
    print("PyCG Wrapper 已准备就绪！")
    print("请参考上面的注释代码来使用此包装器。")

