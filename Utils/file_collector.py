"""
文件收集工具
用于收集指定文件夹中的所有C文件和Python文件
"""

import os
from typing import List, Tuple


class FileCollector:
    """文件收集器类"""
    
    def __init__(self):
        # 支持的文件扩展名
        self.c_extensions = {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx'}
        self.python_extensions = {'.py', '.pyx', '.pyi'}
    
    def collect_files(self, directory: str) -> Tuple[List[str], List[str]]:
        """
        收集指定目录中的所有C文件和Python文件
        
        Args:
            directory: 要扫描的目录路径
            
        Returns:
            Tuple[List[str], List[str]]: (C文件列表, Python文件列表)
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"路径不是目录: {directory}")
        
        c_files = []
        python_files = []
        
        # 递归遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in self.c_extensions:
                    c_files.append(file_path)
                elif file_ext in self.python_extensions:
                    python_files.append(file_path)
        
        return c_files, python_files
    
    def print_file_summary(self, c_files: List[str], python_files: List[str]) -> None:
        """
        打印文件收集结果摘要
        
        Args:
            c_files: C文件列表
            python_files: Python文件列表
        """
        print(f"找到 {len(c_files)} 个C文件:")
        for file in c_files:
            print(f"  - {file}")
        
        print(f"\n找到 {len(python_files)} 个Python文件:")
        for file in python_files:
            print(f"  - {file}")
        
        print(f"\n总计: {len(c_files) + len(python_files)} 个文件")


def collect_project_files(directory: str) -> Tuple[List[str], List[str]]:
    """
    便捷函数：收集项目文件
    
    Args:
        directory: 项目目录路径
        
    Returns:
        Tuple[List[str], List[str]]: (C文件列表, Python文件列表)
    """
    collector = FileCollector()
    return collector.collect_files(directory)