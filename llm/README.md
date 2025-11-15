# LLM Parser for C/Python Code Analysis

Automatically parse Python module registration and Python call information from C code using Claude LLM.

## 📂 Project Structure

```
llm/
├── __init__.py                           # Package initialization
├── llm_client.py                         # Claude API client wrapper
├── module_registration_prompts.py        # Prompt templates for module registration
├── module_registration_schema.py         # Output format definition and parameter mapping
├── parse_module_registration.py          # Main program: Parse module registration
├── python_call_extraction_prompts.py     # Prompt templates for Python call extraction
├── parse_python_call_extraction.py       # Main program: Parse Python calls
└── README.md                             # This file
```

## 🎯 Features

### 1. Module Registration Parser

Extract from Python module registration code in C:
- **Module Name**
- **Python Function Name** → **C Function Name** mapping
- **Parameter Types** (extracted from `PyArg_ParseTuple`)
- **Parameter Count**
- **Return Type**
- **Prompt and Response Logging** (saved to output/ folder)

### 2. Python Call Extraction Parser

Extract from C code that calls Python functions:
- **Module Name**: The Python module being imported
- **Function Name**: The Python function being called
- **Arguments**: The arguments passed to the function (extracted from `Py_BuildValue`, `PyTuple_Pack`, etc.)
- **Prompt and Response Logging** (saved to output/ folder)

## ⚙️ Environment Setup

Create a `.env` file in the project root:

```bash
# Either one works
ANTHROPIC_API_KEY=your_api_key_here
# or
CLAUDE_API_KEY=your_api_key_here
```

## 🚀 Usage

### Automatic Usage (Recommended)

When you run the main analysis tool, both parsers are automatically invoked:

```bash
cd /home/kansx/Papers/Python-C/PyCTrace
python main.py /path/to/your/code
```

This will automatically:
1. Extract module registration info and parse with LLM
2. Extract Python call info and parse with LLM

### Manual Usage

#### Module Registration Parser

```bash
python llm/parse_module_registration.py [input_file] [output_file] [model]
```

**Parameters:**
- `input_file`: Default `output/c_python_module_registrations.txt`
- `output_file`: Default `output/c_python_module_registrations_llm.json`
- `model`: Default `claude-sonnet-4-20250514`

**Examples:**

```bash
# Use default paths
python llm/parse_module_registration.py

# Specify input and output
python llm/parse_module_registration.py input.txt output.json
```

#### Python Call Extraction Parser

```bash
python llm/parse_python_call_extraction.py [input_file] [output_file] [model]
```

**Parameters:**
- `input_file`: Default `output/c_python_call_extraction.txt`
- `output_file`: Default `output/c_python_call_extraction_llm.json`
- `model`: Default `claude-sonnet-4-20250514`

**Examples:**

```bash
# Use default paths
python llm/parse_python_call_extraction.py

# Specify input and output
python llm/parse_python_call_extraction.py input.txt output.json
```

## 📊 Output Format

### 1. Module Registration JSON Output

```json
{
  "total_modules": 1,
  "modules": [
    {
      "module_name": "host",
      "functions": [
        {
          "python_name": "tick",
          "c_function_name": "py_tick",
          "param_format": "l",
          "param_types": ["long"],
          "param_count": 1,
          "return_type": "None"
        }
      ]
    }
  ]
}
```

### 2. Python Call Extraction JSON Output

```json
{
  "python_calls": [
    {
      "module": "p1",
      "function": "combine",
      "arguments": ["4", "5", "7"]
    }
  ]
}
```

### Prompt and Response Files

The parsers automatically save prompts and responses:
- `output/module_registration_prompt.txt` / `output/module_registration_response.txt`
- `output/python_call_prompt.txt` / `output/python_call_response.txt`

## 📖 Field Description

### Module Registration Fields

| Field | Type | Description |
|------|------|------|
| `total_modules` | int | Total number of modules |
| `module_name` | string | Python module name |
| `python_name` | string | Function name in Python |
| `c_function_name` | string | Corresponding C function name |
| `param_format` | string | PyArg_ParseTuple format string |
| `param_types` | list[string] | List of parameter types |
| `param_count` | int | Number of parameters |
| `return_type` | string | Return type |

### Python Call Extraction Fields

| Field | Type | Description |
|------|------|------|
| `module` | string | Python module name (e.g., "p1", "host") |
| `function` | string | Python function name being called |
| `arguments` | list[string] | Arguments passed to the function |

## 🔧 Parameter Format Mapping

| Format | Type | Description |
|------|------|------|
| `s` | string (char*) | String |
| `i` | int | Integer |
| `l` | long | Long integer |
| `f` | float | Float |
| `d` | double | Double precision float |
| `O` | PyObject* | Python object |
| `O!` | PyObject* (with type check) | Specific type object |

See `PARAM_FORMAT_MAPPING` in `module_registration_schema.py` for the complete mapping.

## 🔌 API Usage Examples

### 1. Parse a Single Module

```python
from llm.llm_client import ClaudeClient
from llm.module_registration_prompts import (
    SYSTEM_PROMPT_MODULE_REGISTRATION,
    get_module_registration_analysis_prompt
)
import json

# Initialize client
client = ClaudeClient(model="claude-sonnet-4-20250514")

# C code
c_code = """
PyMODINIT_FUNC PyInit_host(void) { return PyModule_Create(&HostModule); }
static struct PyModuleDef HostModule = {PyModuleDef_HEAD_INIT, "host", NULL, -1, HostMethods};
static PyMethodDef HostMethods[] = {{"tick", py_tick, METH_VARARGS, "acc"}, {NULL, NULL, 0, NULL}};
static PyObject *py_tick(PyObject *self, PyObject *args) {
  long k = 0;
  if (!PyArg_ParseTuple(args, "l", &k))
    return NULL;
  Py_RETURN_NONE;
}
"""

# Generate prompt
prompt = get_module_registration_analysis_prompt(c_code)

# Call API
response = client.generate_with_system(
    SYSTEM_PROMPT_MODULE_REGISTRATION, 
    prompt
)

# Parse result
result = json.loads(response)
print(result)
```

### 2. General Code Analysis

```python
from llm.llm_client import ClaudeClient

client = ClaudeClient()
response = client.generate("Analyze this code functionality...")
print(response)
```

## 📐 Modular Design

### llm_client.py
Encapsulates Anthropic API calls:
- Automatically loads API Key from `.env`
- Provides simple `generate()` and `generate_with_system()` interfaces
- Unified error handling

### module_registration_prompts.py
Prompt template management for module registration analysis:
- `SYSTEM_PROMPT_MODULE_REGISTRATION`: System prompt for module registration
- `get_module_registration_analysis_prompt()`: Generate prompt for parsing module registration
- All prompts in English for better LLM comprehension

### module_registration_schema.py
Output format definitions for module registration:
- `OUTPUT_SCHEMA`: JSON output template
- `MODULE_SCHEMA`: Single module schema
- `PARAM_FORMAT_MAPPING`: Parameter format mapping table
- `get_schema_string()`: Get formatted schema string

### parse_module_registration.py
Main parser implementation:
- Reads C module registration code
- Calls Claude API for parsing
- Saves results to JSON
- **NEW**: Automatically saves prompts and responses to output folder

## 🎯 Future Applications

The parsed JSON can be used for:
1. **Cross-language Call Graph Analysis** - Connect Python and C call graphs
2. **Type Checking** - Verify Python call parameter types
3. **Documentation Generation** - Auto-generate API documentation
4. **Test Case Generation** - Generate tests based on parameter types
5. **Static Analysis** - Detect type mismatch issues

## 📝 Recent Changes

- ✅ All prompts converted to English for better LLM performance
- ✅ Renamed `prompts.py` to `module_registration_prompts.py` for task-specific naming
- ✅ Renamed `output_schema.py` to `module_registration_schema.py` with English comments
- ✅ Added automatic prompt and response saving functionality
- ✅ Removed example file `claude_analyzer.py`
- ✅ Updated all user-facing messages to English