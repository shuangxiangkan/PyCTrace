import os
import shutil
from pathlib import Path
from typing import List, Tuple


def collect_files(folder_path: str) -> Tuple[List[str], List[str]]:
    python_files = []
    c_files = []
    
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    if not folder.is_dir():
        raise NotADirectoryError(f"不是一个有效的文件夹: {folder_path}")
    
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            if suffix == '.py':
                python_files.append(str(file_path))
            elif suffix in ['.c', '.h']:
                c_files.append(str(file_path))
    
    return python_files, c_files


def merge_all_python_files(source_python_files: list[str], output_dir: str) -> str:
    all_py_dir = os.path.join(output_dir, "all_py")
    generated_py_dir = os.path.join(output_dir, "py")
    
    if os.path.exists(all_py_dir):
        shutil.rmtree(all_py_dir)
    os.makedirs(all_py_dir, exist_ok=True)
    
    copied_count = 0
    
    for py_file in source_python_files:
        src_path = Path(py_file)
        if src_path.exists() and src_path.is_file():
            dest_name = src_path.name
            counter = 1
            dest_path = os.path.join(all_py_dir, dest_name)
            
            while os.path.exists(dest_path):
                name_without_ext = src_path.stem
                ext = src_path.suffix
                dest_name = f"{name_without_ext}_{counter}{ext}"
                dest_path = os.path.join(all_py_dir, dest_name)
                counter += 1
            
            shutil.copy2(py_file, dest_path)
            copied_count += 1
    
    if os.path.exists(generated_py_dir):
        for py_file in Path(generated_py_dir).glob('*.py'):
            dest_name = py_file.name
            counter = 1
            dest_path = os.path.join(all_py_dir, dest_name)
            
            while os.path.exists(dest_path):
                name_without_ext = py_file.stem
                ext = py_file.suffix
                dest_name = f"{name_without_ext}_{counter}{ext}"
                dest_path = os.path.join(all_py_dir, dest_name)
                counter += 1
            
            shutil.copy2(str(py_file), dest_path)
            copied_count += 1
    
    return all_py_dir