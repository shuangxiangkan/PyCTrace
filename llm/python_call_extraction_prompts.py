SYSTEM_PROMPT_PYTHON_CALL = """You are a professional C/Python code analysis expert. Your task is to analyze C code and extract Python function call information.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_python_call_analysis_prompt(code: str) -> str:
    prompt = f"""Please analyze the following C code and extract all Python function calls.

For each Python function call, extract:

1. **module**: The Python module name (e.g., from PyImport_AddModule, or from the code context like "host.tick(k)")
2. **function**: The Python function name being called (e.g., from PyDict_GetItemString, PyObject_GetAttrString, or code strings)
3. **arguments**: The arguments passed to the function (extracted from Py_BuildValue or PyTuple_Pack, etc.)
   - Format as a list of strings representing the argument values or descriptions
   - If arguments are variables, use the variable name; if they are literals, use the literal value

## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{{
  "python_calls": [
    {{
      "module": "module_name",
      "function": "function_name",
      "arguments": ["arg1", "arg2", "arg3"]
    }}
  ]
}}
```

## Notes

1. Focus on extracting calls to Python functions, not C API functions
2. Look for patterns like:
   - PyDict_GetItemString(dict, "function_name")
   - PyObject_GetAttrString(module, "function_name")
   - PyObject_CallObject(function, args)
   - Dynamic code execution via PyRun_String that contains Python calls
3. For arguments:
   - From Py_BuildValue("(iii)", 10, 20, 3) extract ["10", "20", "3"]
   - From PyTuple_Pack(2, a, b) extract ["a", "b"]
   - From dynamic code strings, extract the arguments used in the call
4. If module name cannot be determined, use "unknown"
5. Only return JSON, do not add any explanatory text

## C Code

```c
{code}
```

Please output the analysis result in JSON format:"""
    
    return prompt