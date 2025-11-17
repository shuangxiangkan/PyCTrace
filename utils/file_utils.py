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