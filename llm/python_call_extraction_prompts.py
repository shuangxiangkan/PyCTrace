SYSTEM_PROMPT_PYTHON_CALL = """You are a professional C/Python code analysis expert. Your task is to analyze C code and convert embedded Python code to executable Python format.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_python_call_analysis_prompt(code: str) -> str:
    prompt = f"""Please analyze the following C code and convert it into executable Python code.

## Task: Convert to Python Code

Convert the C code into equivalent Python code:
1. Extract Python code strings from PyRun_String, PyRun_SimpleString, etc.
2. Extract function calls from PyDict_GetItemString, PyObject_CallObject, etc.
3. Combine them into complete, executable Python code
4. Resolve dynamic function names (e.g., from snprintf, string concatenation)

## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{{
  "python_code": "complete Python code here"
}}
```

## Example

For C code:
```c
const char *py = "def add(a,b):\\n    return a+b\\n";
PyRun_String(py, Py_file_input, g, g);
PyObject *fn = PyDict_GetItemString(g, "add");
PyObject *args = Py_BuildValue("(ii)", 10, 20);
PyObject *ret = PyObject_CallObject(fn, args);
```

Output:
```json
{{
  "python_code": "def add(a, b):\\n    return a + b\\n\\nadd(10, 20)"
}}
```

## C Code

```c
{code}
```

Please output the analysis result in JSON format:"""
    
    return prompt