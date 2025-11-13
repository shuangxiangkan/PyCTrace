# Python C API 调用提取测试用例

本目录包含6个测试用例，用于测试 Python C API 调用提取功能。

## 测试用例说明

### Test 1: 单个 Python 函数调用
**文件**: `test1_single_call.c`
- **描述**: 最简单的测试用例，只包含一个 `PyObject_CallObject` 调用
- **Python 调用数**: 1
- **外部函数调用**: 无
- **特点**: 基础测试，验证单个调用的提取

### Test 2: 两个 Python 函数调用
**文件**: `test2_two_calls.c`
- **描述**: 包含两个独立的 Python 函数调用（`math.sqrt` 和 `math.pow`）
- **Python 调用数**: 2
- **外部函数调用**: 无
- **特点**: 测试多个调用的提取和区分

### Test 3: 单个 Python 函数调用 + 同文件辅助函数
**文件**: `test3_call_with_helper.c`
- **描述**: 一个 Python 调用，涉及同文件中的辅助函数
- **Python 调用数**: 1
- **外部函数调用**: 
  - `get_module_name()` - 获取模块名
  - `build_args()` - 构建参数
- **特点**: 测试同文件内函数依赖的提取

### Test 4: 两个 Python 函数调用 + 各自的同文件辅助函数
**文件**: `test4_two_calls_with_helpers.c`
- **描述**: 两个 Python 调用，每个都使用不同的辅助函数
- **Python 调用数**: 2
- **外部函数调用**:
  - 第一个调用: `get_first_function_name()`, `create_list()`
  - 第二个调用: `get_second_function_name()`, `create_tuple()`
- **特点**: 测试多个调用各自依赖的正确关联

### Test 5: 单个 Python 函数调用 + 跨文件辅助函数
**文件**: `test5_cross_file_call.c` (主文件)
**辅助文件**: `test5_helpers.c`, `test5_helpers.h`
- **描述**: 一个 Python 调用，其辅助函数定义在另一个 C 文件中
- **Python 调用数**: 1
- **外部函数调用**:
  - `get_datetime_module_name()` - 定义在 test5_helpers.c
  - `get_datetime_class_name()` - 定义在 test5_helpers.c
  - `create_datetime_args()` - 定义在 test5_helpers.c
- **特点**: 测试跨文件函数依赖的提取能力

### Test 6: 两个 Python 函数调用 + 各自的跨文件辅助函数
**文件**: `test6_two_cross_file_calls.c` (主文件)
**辅助文件**: 
- `test6_helpers_json.c`, `test6_helpers_json.h` (JSON 相关)
- `test6_helpers_base64.c`, `test6_helpers_base64.h` (Base64 相关)
- **描述**: 两个 Python 调用，辅助函数分别在不同的 C 文件中
- **Python 调用数**: 2
- **外部函数调用**:
  - 第一个调用 (JSON): 
    - `get_json_module_name()` - 定义在 test6_helpers_json.c
    - `get_json_loads_name()` - 定义在 test6_helpers_json.c
    - `create_json_string()` - 定义在 test6_helpers_json.c
  - 第二个调用 (Base64):
    - `get_base64_module_name()` - 定义在 test6_helpers_base64.c
    - `get_base64_encode_name()` - 定义在 test6_helpers_base64.c
    - `create_bytes_to_encode()` - 定义在 test6_helpers_base64.c
- **特点**: 测试复杂的跨文件、多调用场景

## 测试覆盖范围

- ✅ 单个/多个 Python 调用提取
- ✅ 同文件内函数依赖识别
- ✅ 跨文件函数依赖识别
- ✅ 多个调用的上下文隔离
- ✅ 复杂依赖关系的正确关联

## 使用方法

```python
from C.py_call_extractor import PythonCallExtractor

extractor = PythonCallExtractor()

# 测试单文件
result = extractor.parse_files('test1_single_call.c')

# 测试多文件（跨文件调用）
result = extractor.parse_files([
    'test5_cross_file_call.c',
    'test5_helpers.c'
])

# 测试复杂跨文件场景
result = extractor.parse_files([
    'test6_two_cross_file_calls.c',
    'test6_helpers_json.c',
    'test6_helpers_base64.c'
])
```