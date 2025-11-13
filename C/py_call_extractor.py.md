# Python C API 调用提取器

## 功能概述

从 C 代码中提取 Python C API 调用的完整上下文，包括函数调用链、参数构建、返回值处理以及相关的辅助函数定义。支持单文件和跨文件分析。

## 核心原理

### 1. 数据依赖追踪算法

基于数据流分析（DDG - Data Dependence Graph），递归追踪与 Python 调用相关的所有变量和语句。

**算法流程：**

```
1. 定位 Python C API 调用语句（如 PyObject_CallObject(fn, args)）
2. 提取调用涉及的初始变量集合（如 {fn, args, ret}）
3. 遍历函数所有语句，检查其定义(def)和使用(use)变量
4. 若语句的 def/use 与追踪变量集合有交集，则：
   - 将该语句加入上下文
   - 将该语句的所有 def/use 变量加入追踪集合
5. 重复步骤 3-4，直到没有新语句加入
```

**示例：**

```c
PyObject *pModule = PyImport_ImportModule("sys");        // use: {}, def: {pModule}
PyObject *pFunc = PyObject_GetAttrString(pModule, ...);  // use: {pModule}, def: {pFunc}
PyObject *pArgs = Py_BuildValue("(i)", 0);               // use: {}, def: {pArgs}
PyObject *ret = PyObject_CallObject(pFunc, pArgs);       // use: {pFunc, pArgs}, def: {ret} ← 起点
Py_XDECREF(ret);                                         // use: {ret}, def: {}
```

从调用语句开始反向追踪：`ret → pFunc, pArgs → pModule`，直到构建完整的调用链。

### 2. 两阶段处理架构

**阶段 1：全局函数注册**
- 遍历所有文件，提取所有函数定义
- 构建函数名到函数信息的全局映射表
- 支持跨文件函数查找

**阶段 2：按需分析**
- 轻量级遍历：检查函数是否包含 Python C API 调用
- 仅对包含调用的函数构建 DDG（避免浪费）
- 提取调用上下文和相关函数定义

### 3. 跨文件依赖解析

通过全局函数注册表，识别并提取在其他文件中定义的辅助函数：

```c
// file1.c
const char* get_module_name() { return "sys"; }

// file2.c
const char *name = get_module_name();  // 跨文件调用
PyObject *pModule = PyImport_ImportModule(name);
```

提取器会自动找到 `get_module_name` 在 `file1.c` 中的完整定义。

## 支持的 Python C API

```python
PyObject_CallObject       # 主要支持
PyObject_CallFunction
PyObject_CallMethod
PyObject_Call
PyObject_CallFunctionObjArgs
PyObject_CallMethodObjArgs
PyEval_CallObject
PyEval_CallFunction
PyEval_CallMethod
```

## 输出格式

### 文本格式（人类可读）
```
# Call 1: PyObject_CallObject at file.c:10

PyObject *pModule = PyImport_ImportModule("sys");
PyObject *pFunc = PyObject_GetAttrString(pModule, "exit");
PyObject *pResult = PyObject_CallObject(pFunc, pArgs);
Py_DECREF(pModule);

# Related function definitions:
const char* get_module_name() {
    return "sys";
}
```

### JSON 格式（机器可读）
```json
{
  "python_calls": [
    {
      "call_function": "PyObject_CallObject",
      "call_line": 10,
      "file": "file.c",
      "context_statements": [...],
      "function_definitions": [...]
    }
  ],
  "total_calls": 1,
  "total_functions": 3
}
```

## 使用场景

- 提取 Python C API 调用的完整代码片段用于大模型分析
- 分析 C 扩展模块的 Python 调用模式
- 跨文件追踪函数依赖关系
- 生成调用上下文用于漏洞分析或代码理解

## 技术栈

- **tree-sitter**：C 代码 AST 解析
- **DDG（Data Dependence Graph）**：数据流分析
- **递归变量追踪**：上下文提取核心算法