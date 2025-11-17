import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import logger

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
    
    logger.info(f"  Saved prompt to: {prompt_file}")
    logger.info(f"  Saved response to: {response_file}")


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
        logger.error(f"JSON parsing error: {e}")
        logger.info(f"Raw response: {response}")
        return {
            "error": "JSON parsing failed",
            "raw_response": response
        }
    except Exception as e:
        logger.error(f"LLM call error: {e}")
        return {
            "error": str(e)
        }

def parse_python_call_file(input_file: str, output_file: str, model: str = "claude-sonnet-4-20250514"):
    logger.info(f"Reading file: {input_file}")
    
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
    
    all_python_code = []
    all_results = []
    
    for idx, code in enumerate(call_codes, 1):
        logger.info(f"Parsing call block #{idx}...")
        result = parse_call_with_llm(code, client, output_dir)
        
        if "error" not in result:
            python_code = result.get("python_code", "")
            if python_code:
                all_python_code.append(f"# Block {idx}\n{python_code}\n")
                all_results.append({
                    "block_id": idx,
                    "python_code": python_code
                })
        else:
            logger.error(f"Error parsing call block #{idx}: {result.get('error')}")
    
    final_result = {
        "total_blocks": len(all_results),
        "blocks": all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    logger.success(f"JSON result saved to: {output_file}")
    
    if all_python_code:
        py_output_dir = output_dir / "py"
        py_output_dir.mkdir(exist_ok=True)
        py_output_file = py_output_dir / "python_call_in_c.py"
        
        with open(py_output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_python_code))
        
        logger.success(f"Python code saved to: {py_output_file}")
    
    logger.success(f"Successfully parsed {len(call_codes)} call blocks")
    logger.success(f"Extracted {len(all_python_code)} Python code blocks")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python parse_python_call_extraction.py <input_file> [output_file]")
        logger.info("\nExample:")
        logger.info("  python parse_python_call_extraction.py output/c_python_call_extraction.txt output/c_python_call_extraction_llm.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "c_python_call_extraction_llm.json"
    
    parse_python_call_file(input_file, output_file)