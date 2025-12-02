SYSTEM_PROMPT_PYTHON_CALL = """You are a professional C/Python code analysis expert. Your task is to faithfully translate C code with Python C API calls into equivalent Python code.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_python_call_analysis_prompt(code: str) -> str:
    prompt = f"""Please analyze the following C code and convert it into the equivalent Python code.

## Important: About the C Code
The C code below is **program-sliced** – it contains only statements relevant to Python C API calls. This means:
The code may have incomplete or syntactically invalid fragments for example, missing braces or other structural elements), due to slicing, However, the **semantics are complete** for understanding the Python behavior. You only need to perform a faithful, mechanical translation of the sliced Python-related C code into Python. Do not attempt to repair or complete the translated Python code, even if it results in incorrect or non-functional Python.


## Examples

### Example 1: Without function signature
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

### Example 2: With function signature (program-sliced code)
```c
long run_task(int a, int b, int k) {{
PyRun_SimpleString("import sys; sys.path.insert(0, '.')");
PyObject *m = PyImport_ImportModule("p1");
PyObject *f = PyObject_GetAttrString(m, "combine");
PyObject *args = Py_BuildValue("(iii)", a, b, k);
PyObject *r = PyObject_CallObject(f, args);
long v = PyLong_AsLong(r);
return v;
}}
```

Output:
```json
{{
  "python_code": "def run_task(a, b, k):\\n    import sys\\n    sys.path.insert(0, '.')\\n    import p1\\n    v = p1.combine(a, b, k)\\n    return v"
}}
```
   
   
## C Code

```c
{code}
```

## CRITICAL REQUIREMENTS

1. **FAITHFUL TRANSLATION - DO NOT modify, fix, or optimize**:
   - Translate Python API calls literally and mechanically
   - Keep function names, module names, attribute names exactly as they appear in C
   - Keep argument counts exactly as specified in `Py_BuildValue` format strings
   - DO NOT infer, add, or remove any objects or parameters
   - DO NOT create instances unless C code explicitly calls the class (e.g., `PyObject_CallObject(cls, NULL)`)
   - Resolve dynamic names from C logic (e.g., snprintf) only if the value is determinable
   - If C code has issues, translate them as-is - your job is translation, not correction

2. **SCOPE**:
   - ONLY translate Python C API calls
   - IGNORE pure C code: printf, fprintf, malloc, C variables like g_counter, etc.
   
## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{{
  "python_code": "complete Python code here"
}}
```

Please output the equivalent Python code in JSON format:"""
    
    return prompt