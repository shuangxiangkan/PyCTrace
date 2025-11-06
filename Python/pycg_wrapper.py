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

