import os
import sys
import json
from pathlib import Path

try:
    from .llm_client import ClaudeClient
    from .python_call_extraction_prompts import (
        SYSTEM_PROMPT_PYTHON_CALL,
        get_python_call_analysis_prompt
    )
except ImportError:
    from llm_client import ClaudeClient
    from python_call_extraction_prompts import (
        SYSTEM_PROMPT_PYTHON_CALL,
        get_python_call_analysis_prompt
    )


def save_prompt_and_response(prompt: str, response: str, output_dir: Path):
    prompt_file = output_dir / "python_call_prompt.txt"
    response_file = output_dir / "python_call_response.txt"
    
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


def parse_call_with_llm(code: str, client: ClaudeClient, output_dir: Path = None) -> dict:
    prompt = get_python_call_analysis_prompt(code)
    
    try:
        response = client.generate_with_system(
            system_prompt=SYSTEM_PROMPT_PYTHON_CALL,
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
            "raw_response": response,
            "python_calls": []
        }
    except Exception as e:
        print(f"LLM call error: {e}")
        return {
            "error": str(e),
            "python_calls": []
        }


def parse_python_call_file(input_file: str, output_file: str, model: str = "claude-sonnet-4-20250514"):
    print(f"Reading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    client = ClaudeClient(model=model)
    
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    call_codes = []
    current_call = []
    in_call = False
    
    for line in content.split('\n'):
        if 'C中的Python API调用 #' in line:
            if current_call:
                call_codes.append('\n'.join(current_call))
                current_call = []
            in_call = True
        elif in_call and line.strip() and not line.startswith('='):
            current_call.append(line)
    
    if current_call:
        call_codes.append('\n'.join(current_call))
    
    all_results = []
    
    for idx, code in enumerate(call_codes, 1):
        print(f"\nParsing call block #{idx}...")
        result = parse_call_with_llm(code, client, output_dir)
        
        if "error" not in result:
            all_results.extend(result.get("python_calls", []))
        else:
            print(f"  Error parsing call block #{idx}: {result.get('error')}")
    
    final_result = {
        "python_calls": all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaving result to: {output_file}")
    print(f"✓ Successfully parsed {len(call_codes)} call blocks")
    print(f"✓ Extracted {len(all_results)} Python calls")
    print(f"✓ Result saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_python_call_extraction.py <input_file> [output_file]")
        print("\nExample:")
        print("  python parse_python_call_extraction.py output/c_python_call_extraction.txt output/c_python_call_extraction_llm.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "c_python_call_extraction_llm.json"
    
    parse_python_call_file(input_file, output_file)