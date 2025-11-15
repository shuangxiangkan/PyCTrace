import os
import sys
import json
from pathlib import Path

try:
    from .llm_client import ClaudeClient
    from .module_registration_prompts import (
        SYSTEM_PROMPT_MODULE_REGISTRATION, 
        get_module_registration_analysis_prompt
    )
except ImportError:
    from llm_client import ClaudeClient
    from module_registration_prompts import (
        SYSTEM_PROMPT_MODULE_REGISTRATION, 
        get_module_registration_analysis_prompt
    )


def save_prompt_and_response(prompt: str, response: str, output_dir: Path):
    prompt_file = output_dir / "module_registration_prompt.txt"
    response_file = output_dir / "module_registration_response.txt"
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    with open(response_file, 'w', encoding='utf-8') as f:
        f.write(response)
    
    print(f"  Saved prompt to: {prompt_file}")
    print(f"  Saved response to: {response_file}")


def clean_json_response(response_text: str) -> str:
    response_text = response_text.strip()
    
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    return response_text.strip()


def parse_module_with_llm(code: str, client: ClaudeClient, output_dir: Path = None) -> dict:
    prompt = get_module_registration_analysis_prompt(code)
    
    try:
        response = client.generate_with_system(
            system_prompt=SYSTEM_PROMPT_MODULE_REGISTRATION,
            user_prompt=prompt,
            max_tokens=8192,
            temperature=0
        )
        
        if output_dir:
            save_prompt_and_response(prompt, response, output_dir)
        
        cleaned_response = clean_json_response(response)
        result = json.loads(cleaned_response)
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response}")
        return {
            "error": "JSON parsing failed",
            "raw_response": response
        }
    except Exception as e:
        print(f"LLM call error: {e}")
        return {
            "error": str(e)
        }

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


def save_python_stubs(json_data: dict, output_dir: Path):
    modules = json_data.get('modules', [])
    
    if not modules:
        return
    
    py_output_dir = output_dir / "py"
    py_output_dir.mkdir(exist_ok=True)
    
    for module_info in modules:
        module_name = module_info['module_name']
        stub_code = generate_module_stub(module_info)
        
        output_file = py_output_dir / f"{module_name}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(stub_code)
        
        print(f"✓ Python 接口文件已生成: {output_file}")


def parse_registration_file(input_file: str, output_file: str, model: str = "claude-sonnet-4-20250514"):
    print(f"Reading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    client = ClaudeClient(model=model)
    
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    module_codes = []
    current_module = []
    in_module = False
    
    for line in content.split('\n'):
        if 'C中的python注册模块 #' in line or '模块链 #' in line:
            if current_module:
                module_codes.append('\n'.join(current_module))
                current_module = []
            in_module = True
        elif in_module and line.strip():
            if not line.startswith('='):
                current_module.append(line)
    
    if current_module:
        module_codes.append('\n'.join(current_module))
    
    all_modules = []
    for idx, code in enumerate(module_codes, 1):
        print(f"\nParsing module #{idx}...")
        result = parse_module_with_llm(code, client, output_dir)
        
        if 'modules' in result and isinstance(result['modules'], list):
            all_modules.extend(result['modules'])
        elif 'error' not in result:
            all_modules.append(result)
    
    output_data = {
        "total_modules": len(all_modules),
        "modules": all_modules
    }
    
    print(f"\nSaving result to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully parsed {len(all_modules)} modules")
    print(f"✓ Result saved to: {output_file}")
    
    print(f"\n正在生成 Python 接口文件...")
    save_python_stubs(output_data, output_dir)
    
    return output_data