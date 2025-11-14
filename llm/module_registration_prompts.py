try:
    from .module_registration_schema import get_schema_string, PARAM_FORMAT_MAPPING
except ImportError:
    from module_registration_schema import get_schema_string, PARAM_FORMAT_MAPPING


SYSTEM_PROMPT_MODULE_REGISTRATION = """You are a professional C/Python code analysis expert. Your task is to analyze Python module registration information in C code and extract key interface details.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_module_registration_analysis_prompt(code: str) -> str:
    param_format_desc = "\n".join([f"  '{k}': {v}" for k, v in PARAM_FORMAT_MAPPING.items()])
    
    prompt = f"""Please analyze the Python module registration information in the following C code and extract:

1. **Module Name**: Extract from PyModuleDef structure
2. **Registered Python Functions List**, each function includes:
   - **python_name**: Function name used in Python (from PyMethodDef array)
   - **c_function_name**: Corresponding C function implementation name (from PyMethodDef array)
   - **param_format**: Parameter format string (extracted from PyArg_ParseTuple call in C function, e.g., "l", "si", "O")
   - **param_types**: Parameter type list (inferred from param_format, refer to the mapping table below)
   - **param_count**: Number of parameters (length of param_types array)
   - **return_type**: Return type (inferred from C function return statements, e.g., Py_RETURN_NONE means "None")

## Parameter Format Mapping Reference

{param_format_desc}

## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{get_schema_string()}
```

## Notes

1. If there are multiple modules in the code, the modules array contains multiple module objects
2. If a function has no parameters, param_format is an empty string "", param_types is an empty array [], param_count is 0
3. Common return type values:
   - "None" (Py_RETURN_NONE or Py_INCREF(Py_None))
   - "int" (PyLong_FromLong)
   - "float" (PyFloat_FromDouble)
   - "string" (PyUnicode_FromString)
   - "PyObject*" (returns other Python objects)
4. Only return JSON, do not add any explanatory text

## C Code

```c
{code}
```

Please output the analysis result in JSON format:"""
    
    return prompt


def get_batch_module_registration_analysis_prompt(modules_code_list: list) -> str:
    code_sections = []
    for idx, code in enumerate(modules_code_list, 1):
        code_sections.append(f"### Module #{idx}\n\n```c\n{code}\n```")
    
    all_code = "\n\n".join(code_sections)
    
    param_format_desc = "\n".join([f"  '{k}': {v}" for k, v in PARAM_FORMAT_MAPPING.items()])
    
    prompt = f"""Please analyze the Python module registration information in the following multiple C code snippets.

## Parameter Format Mapping Reference

{param_format_desc}

## Output Format

```json
{get_schema_string()}
```

## C Code Snippets

{all_code}

Please output the JSON format result containing all module information:"""
    
    return prompt