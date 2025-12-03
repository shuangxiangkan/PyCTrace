SYSTEM_PROMPT_PYTHON_CALL = """You are a professional C/Python code analysis expert. Your task is to faithfully translate C code with Python C API calls into equivalent Python code.

Please output strictly in the specified JSON format without any additional explanations or comments."""


def get_python_call_analysis_prompt(code: str) -> str:
    prompt = f"""Please analyze the following C code and convert it into the equivalent Python code.

## Important: About the C Code
The C code below is **program-sliced** – it contains only statements relevant to Python C API calls. This means:
The code may have incomplete or syntactically invalid fragments for example, missing braces or other structural elements), due to slicing, However, the **semantics are complete** for understanding the Python behavior. You only need to perform a faithful, mechanical translation of the sliced Python-related C code into Python. Do not attempt to repair or complete the translated Python code, even if it results in incorrect or non-functional Python.


## Example
```c
PyObject *g = PyModule_GetDict(PyImport_AddModule("__main__"));
const char *py = "import host\\n"
                   "class Service:\\n"
                   "    def run(self, a, k):\\n"
                   "        print('P')\\n"
                   "        host.tick(k)\\n"
                   "        return a*3\\n";
PyRun_String(py, Py_file_input, g, g);
PyObject *cls = PyDict_GetItemString(g, "Service");
PyObject *fn = PyObject_GetAttrString(cls, "run");
PyObject *args = Py_BuildValue("(ii)", 9, 4);
PyObject *ret = PyObject_CallObject(fn, args);
if(!ret)
long v = PyLong_AsLong(ret);
printf("OK:%ld COUNT:%lu\\n", v, g_counter);
Py_DECREF(ret);
```

Output:
```json
{{
  "python_code": "import host\\nclass Service:\\n    def run(self, a, k):\\n        print('P')\\n        host.tick(k)\\n        return a*3\\n\\ncls = Service\\nfn = cls.run\\nret = fn(9, 4)\\nv = ret"
}}
```

**Translation correctness:**
- PyRun_String → defines Service class
- PyDict_GetItemString/PyObject_GetAttrString → cls = Service, fn = cls.run
- Py_BuildValue("(ii)", 9, 4) + PyObject_CallObject → fn(9, 4) (**preserves bug: missing self**)
- Ignores pure C code: printf, Py_DECREF, g_counter, if(!ret)
   
   
## C Code

```c
{code}
```

## CRITICAL REQUIREMENTS

1. **SCOPE**:
   - ONLY translate Python C API calls
   - IGNORE pure C code: printf, fprintf, malloc，,etc.
   - IGNORE C-side logging or debugging code that doesn't affect Python behavior
   
2. **FAITHFUL TRANSLATION - DO NOT modify, fix, or optimize**:
   - Translate Python API calls literally and mechanically
   - Keep function names, module names, attribute names exactly as they appear in C
   - Keep argument counts exactly as specified in `Py_BuildValue` format strings
   - DO NOT infer, add, or remove any objects or parameters
   - DO NOT create instances unless C code explicitly calls the class (e.g., `PyObject_CallObject(cls, NULL)`)
   - Resolve dynamic names from C logic (e.g., snprintf) only if the value is determinable
   - If translated Python code uses parameters from a C function signature, translate the C function signature to a Python function definition (e.g., `long run_task(int a, int b)` → `def run_task(a, b):` with corresponding `return`)
   
## Output Format Requirements

**MUST strictly follow the JSON format below, DO NOT include any other text:**

```json
{{
  "python_code": "complete Python code here"
}}
```

Please output the equivalent Python code in JSON format:"""
    
    return prompt