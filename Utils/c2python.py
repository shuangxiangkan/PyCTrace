import json
import sys
from pathlib import Path


def generate_function_stub(func_info: dict) -> str:
    python_name = func_info['python_name']
    param_types = func_info.get('param_types', [])
    return_type = func_info.get('return_type', 'None')
    
    params_list = []
    for i, param_type in enumerate(param_types):
        params_list.append(f"arg{i}: {param_type}")
    
    params_str = ', '.join(params_list) if params_list else ''
    
    return f"def {python_name}({params_str}) -> {return_type}:\n    pass\n"


def generate_module_stub(module_info: dict) -> str:
    functions = module_info.get('functions', [])
    
    lines = []
    
    for func_info in functions:
        lines.append(generate_function_stub(func_info))
        lines.append('\n')
    
    return ''.join(lines)


def convert_json_to_stubs(json_file: str, output_dir: str = None):
    json_path = Path(json_file)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if output_dir is None:
        output_dir = json_path.parent
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    modules = data.get('modules', [])
    
    for module_info in modules:
        module_name = module_info['module_name']
        stub_code = generate_module_stub(module_info)
        
        output_file = output_dir / f"{module_name}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(stub_code)
        
        print(f"✓ Python 接口文件已生成: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python c2python.py <json_file> [output_dir]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_json_to_stubs(json_file, output_dir)


if __name__ == "__main__":
    main()