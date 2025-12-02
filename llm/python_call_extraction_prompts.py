SYSTEM_PROMPT_PYTHON_CALL = """You are a professional C/Python code analysis expert. Your task is to analyze C code and convert embedded Python code to executable Python format.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_python_call_analysis_prompt(code: str) -> str:
    prompt = f"""Please analyze the following C code and convert it into executable Python code.

## Important: About the C Code

The C code below is **program-sliced** - it contains only statements relevant to Python C API calls. This means:
- The code may have incomplete syntax (e.g., missing variable declarations, incomplete control flow)
- However, the **semantics are complete** for understanding the Python behavior
- Focus on translating the Python-related operations, not fixing C syntax

## Task: Convert to Python Code

Convert the C code into equivalent Python code:
1. Extract Python code strings from PyRun_String, PyRun_SimpleString, etc.
2. Extract function calls from PyDict_GetItemString, PyObject_CallObject, PyObject_GetAttrString, PyImport_ImportModule, etc.
3. Combine them into complete, executable Python code
4. Resolve dynamic function names (e.g., from snprintf, string concatenation) - compute their actual values
5. **If C function signature is present** (e.g., `long run_stage1(int a, int b, int k) {{ ... }}`), translate it to a Python function definition with the same parameters
6. **DO NOT translate C-only code**: Ignore C language statements like printf, fprintf, g_counter, or any C variables. Only translate Python C API calls.

## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{{
  "python_code": "complete Python code here"
}}
```

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

1. **FUNCTION SIGNATURE HANDLING**:
   - If the C code includes a function signature (e.g., `long func(int a, int b)`), translate it to a Python function definition
   - Extract parameter names from the signature and use them in the function body
   - Preserve the function name and parameters
   - If no function signature is present, generate standalone Python code

2. **PRESERVE EXACT SEMANTICS**: You MUST preserve the exact semantics of the original C code. If the C code calls a non-existent function or contains errors, keep them exactly as-is in your output. DO NOT auto-correct, fix, or modify any errors. Your job is to faithfully translate, not to fix bugs.

3. **ONLY TRANSLATE PYTHON C API CALLS**: DO NOT translate pure C code (printf, fprintf, C variables like g_counter, etc.). Only extract and translate:
   - Python code strings embedded in the C code (from PyRun_String, etc.)
   - Python function calls (PyObject_CallObject, PyObject_Call, etc.)
   - Python imports (PyImport_ImportModule, etc.)
   - Python attribute access (PyObject_GetAttrString, etc.)

Please output the analysis result in JSON format:"""
    
    return prompt