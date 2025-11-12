# py_module_extractor.py 说明文档

## 功能概述

从C代码中提取Python模块注册信息，支持单文件和多文件分析，能够识别跨文件注册的情况。

## 核心原理

使用**tree-sitter**解析C代码的抽象语法树(AST)，通过模式匹配提取Python C API相关的注册代码。

## 工作流程

```
C文件 → tree-sitter解析 → 提取4类组件 → 合并结果 → 构建模块链路
```

### 1. 提取4类组件

从C代码中识别以下组件：

- **PyMethodDef**: 方法定义数组
  ```c
  static PyMethodDef methods[] = {
      {"func_name", c_func, METH_VARARGS, "doc"},
      ...
  };
  ```

- **PyModuleDef**: 模块定义结构
  ```c
  static struct PyModuleDef module = {
      PyModuleDef_HEAD_INIT,
      "module_name",
      "doc",
      -1,
      methods
  };
  ```

- **PyInit_***: 模块初始化函数
  ```c
  PyMODINIT_FUNC PyInit_module(void) {
      return PyModule_Create(&module);
  }
  ```

- **C函数**: 被注册为Python方法的C函数
  ```c
  static PyObject* c_func(PyObject* self, PyObject* args) {
      ...
  }
  ```

### 2. 构建模块链路

通过正则表达式分析组件间的引用关系，构建完整的注册链路：

```
PyInit_module → PyModuleDef → PyMethodDef → C函数
```

**匹配规则**：
- 从`PyInit_*`函数代码中提取`PyModule_Create(&module_def_name)`
- 从`PyModuleDef`代码中提取`methods_array_name`
- 从`PyMethodDef`数组中提取`c_function_name`

### 3. 跨文件支持

多个C文件的组件会被合并到同一个字典中，根据名称匹配构建跨文件的注册链路。

## 使用示例

```python
from C.py_module_extractor import CCodeParser

# 创建解析器
parser = CCodeParser()

# 单文件分析
result = parser.parse_files(["module.c"])

# 多文件分析（支持跨文件注册）
result = parser.parse_files(["file1.c", "file2.c"])
```

## 返回结果

```python
{
    'py_method_defs': [...],      # PyMethodDef数组列表
    'py_module_defs': [...],      # PyModuleDef结构列表
    'py_init_funcs': [...],       # PyInit函数列表
    'py_c_functions': [...],      # C函数列表
    'module_chains': [            # 模块注册链路
        {
            'init_function': 'PyInit_xxx',
            'module_def_info': {...},
            'method_def_info': {...},
            'c_functions': [...]
        }
    ]
}
```

## 技术特点

1. **AST解析**: 基于tree-sitter，比正则表达式更准确
2. **跨文件识别**: 支持函数、数组、结构体分散在多个文件
3. **链路构建**: 自动关联PyInit → ModuleDef → MethodDef → C函数
4. **代码提取**: 保留完整的原始代码片段