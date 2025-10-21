"""
CallGraph 模块
用于处理和合并调用图
"""

from .merger import merge_python_c_call_graph

__all__ = ['merge_python_c_call_graph']

