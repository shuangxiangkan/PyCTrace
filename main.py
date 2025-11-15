import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

from C.py_module_extractor import CCodeParser, format_registration_info_json, format_registration_info_text
from C.py_call_extractor import PythonCallExtractor, format_call_info_json, format_call_info_text
from Python.pycg_wrapper import PyCGWrapper
from llm.parse_module_registration import parse_registration_file
from llm.parse_python_call_extraction import parse_python_call_file
from Utils.c2python import convert_json_to_stubs


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


def process_python_files(python_files: List[str], output_dir: str) -> Dict[str, Any]:
    if not python_files:
        print("未找到 Python 文件")
        return {}
    
    print(f"\n找到 {len(python_files)} 个 Python 文件:")
    for f in python_files:
        print(f"  - {f}")
    
    print("\n正在生成 Python FASTEN call graph...")
    
    try:
        wrapper = PyCGWrapper(entry_points=python_files)
        wrapper.analyze()
        
        call_graph = wrapper.get_fasten_call_graph(
            product="analyzed_code",
            forge="local",
            version="1.0.0",
            timestamp=0
        )
        
        output_file = os.path.join(output_dir, "python_fasten_callgraph.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(call_graph, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Python FASTEN call graph 已保存到: {output_file}")
        
        return call_graph
        
    except Exception as e:
        print(f"✗ 处理 Python 文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}


def process_c_files(c_files: List[str], output_dir: str) -> Dict[str, Any]:
    if not c_files:
        print("未找到 C/C++ 文件")
        return {}
    
    print(f"\n找到 {len(c_files)} 个 C/C++ 文件:")
    for f in c_files:
        print(f"  - {f}")
    
    print("\n正在提取 C 代码中的 Python 模块注册信息...")
    
    try:
        parser = CCodeParser()
        result = parser.parse_files(c_files)
        
        json_output_file = os.path.join(output_dir, "c_python_module_registrations.json")
        with open(json_output_file, 'w', encoding='utf-8') as f:
            f.write(format_registration_info_json(result))
        
        print(f"✓ C 模块注册信息（JSON格式，含元数据）已保存到: {json_output_file}")
        
        txt_output_file = os.path.join(output_dir, "c_python_module_registrations.txt")
        with open(txt_output_file, 'w', encoding='utf-8') as f:
            f.write(format_registration_info_text(result))
        
        print(f"✓ C 模块注册信息（TXT格式，纯代码）已保存到: {txt_output_file}")
        
        return result
        
    except Exception as e:
        print(f"✗ 处理 C 文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}


def process_python_calls(c_files: List[str], output_dir: str) -> Dict[str, Any]:
    if not c_files:
        print("未找到 C/C++ 文件")
        return {}
    
    print(f"\n正在提取 C 代码中的 Python C API 调用信息...")
    
    try:
        extractor = PythonCallExtractor()
        result = extractor.parse_files(c_files)
        
        json_output_file = os.path.join(output_dir, "c_python_call_extraction.json")
        with open(json_output_file, 'w', encoding='utf-8') as f:
            f.write(format_call_info_json(result))
        
        print(f"✓ Python C API 调用信息（JSON格式）已保存到: {json_output_file}")
        
        txt_output_file = os.path.join(output_dir, "c_python_call_extraction.txt")
        with open(txt_output_file, 'w', encoding='utf-8') as f:
            f.write(format_call_info_text(result))
        
        print(f"✓ Python C API 调用信息（TXT格式）已保存到: {txt_output_file}")
        
        return result
        
    except Exception as e:
        print(f"✗ 提取 Python C API 调用信息时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <文件夹路径> [输出目录]")
        print("\n示例:")
        print("  python main.py /path/to/code")
        print("  python main.py /path/to/code /path/to/output")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        folder_name = os.path.basename(os.path.abspath(folder_path))
        output_dir = f"{folder_name}_output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("PyCTrace - Python-C 跨语言函数调用分析工具")
    print("=" * 80)
    print(f"\n分析目标: {folder_path}")
    print(f"输出目录: {output_dir}")
    
    print("\n正在收集文件...")
    python_files, c_files = collect_files(folder_path)
    
    print(f"\n统计信息:")
    print(f"  Python 文件: {len(python_files)} 个")
    print(f"  C/C++ 文件: {len(c_files)} 个")
    
    if not python_files and not c_files:
        print("\n未找到任何 Python 或 C/C++ 文件")
        return
    
    if python_files:
        process_python_files(python_files, output_dir)
    
    if c_files:
        c_result = process_c_files(c_files, output_dir)
        
        process_python_calls(c_files, output_dir)
        
        if c_result and c_result.get('module_chains'):
            print("\n正在使用 LLM 解析模块注册信息...")
            try:
                txt_file = os.path.join(output_dir, "c_python_module_registrations.txt")
                json_file = os.path.join(output_dir, "c_python_module_registrations_llm.json")
                
                parse_registration_file(txt_file, json_file)
                
                print("\n正在转换为 Python 代码...")
                py_output_dir = os.path.join(output_dir, "py")
                convert_json_to_stubs(json_file, py_output_dir)
                
            except Exception as e:
                print(f"✗ LLM 解析出错: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n正在使用 LLM 解析 Python 调用信息...")
        try:
            call_txt_file = os.path.join(output_dir, "c_python_call_extraction.txt")
            call_json_file = os.path.join(output_dir, "c_python_call_extraction_llm.json")
            
            parse_python_call_file(call_txt_file, call_json_file)
            
        except Exception as e:
            print(f"✗ LLM 解析 Python 调用出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()