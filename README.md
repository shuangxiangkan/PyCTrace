# PyCTrace

PyCTrace 是一个用于分析 Python-C 混合代码的静态分析工具，能够从 C 扩展代码中提取 Python 接口、嵌入的 Python 代码，并检测潜在的运行时错误。

## 快速开始

### 1. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. 运行分析

```bash
python main.py example
```

### 4. 查看结果

分析完成后，输出目录 `example_output/` 包含以下内容：

#### 📄 C 模块接口提取
- **`py/host.py`** - 自动生成的 Python 接口声明：
  ```python
  def tick(arg0: int) -> None:
      pass
  ```

#### 🐍 嵌入的 Python 代码提取
- **`py/python_call_in_c.py`** - 从 C 代码中提取的 Python 代码：
  ```python
  import host
  def add_v2(a,b,k):
      print('P')
      host.tick(k)
      return a+b
  def metrics_probe(): return 0
  
  add_v1(10, 20, 3)  # ⚠️ NameError: add_v1 未定义
  ```

#### 🔍 静态检查报告
- **`type_check_report.txt`** - Mypy 类型检查：
  ```
  python_call_in_c.py:9:1: error: Name "add_v1" is not defined
  ```
- **`call_check_report.txt`** - Pylint 调用检查：
  ```
  python_call_in_c.py:9:0: E0602: Undefined variable 'add_v1'
  ```

#### 📊 结构化分析数据
- **`c_python_module_registrations_llm.json`** - 模块注册信息
- **`c_python_call_extraction_llm.json`** - Python 调用提取
- **`type_check_report.json`** / **`call_check_report.json`** - 机器可读的检查报告

---

## 原理说明

PyCTrace 通过 **四步流程** 实现 Python-C 混合代码的静态分析：

### 1️⃣ C 代码解析（Tree-sitter）
使用 Tree-sitter 解析 C 源码，定位两类关键信息：
- **模块注册** - `PyModule_Create`、`PyMethodDef` 等模块定义代码
- **Python 调用** - `PyRun_String`、`PyObject_CallObject` 等 Python C API 调用

### 2️⃣ LLM 辅助提取（Claude API）
将提取的 C 代码片段发送给 Claude，结构化解析：
- **函数签名** - 从 `PyArg_ParseTuple` 的格式字符串推断参数类型
- **Python 代码** - 提取字符串常量中的 Python 代码并补全上下文

### 3️⃣ Python 接口生成
根据 C 模块定义自动生成 Python stub 文件：
- 参数类型标注（`l` → `int`, `s` → `str`）
- 返回类型推断（`Py_RETURN_NONE` → `None`）

### 4️⃣ 静态分析检查
对生成的 Python 代码执行：
- **Mypy** 类型检查 - 检测类型错误、未定义变量
- **Pylint** 调用检查 - 检测函数调用错误、参数不匹配

### 示例分析

对于 C 代码：
```c
const char *py = "import host\n"
                 "def add_v2(a,b,k):\n"
                 "    host.tick(k)\n"
                 "    return a+b\n";
PyRun_String(py, Py_file_input, g, g);

snprintf(fname, 32, "add_%s", choose_suffix());  // -> "add_v1"
PyObject *fn = PyDict_GetItemString(g, fname);   // 查找 add_v1
PyObject_CallObject(fn, args);                    // 调用 add_v1
```

PyCTrace 能够：
1. ✅ 提取 `host` 模块的 `tick` 函数定义
2. ✅ 提取嵌入的 `add_v2` 函数代码
3. ✅ 推断出运行时会调用 `add_v1(10, 20, 3)`
4. ⚠️ **检测到错误**：`add_v1` 未定义（实际定义的是 `add_v2`）

这类错误在编译期无法发现，但会导致运行时 `NameError`。

---

## 命令行选项

```bash
python main.py <目录路径> [输出目录]
```

**示例**：
```bash
# 使用默认输出目录 (example_output/)
python main.py example

# 指定输出目录
python main.py example my_output
```

---

## 依赖说明

| 依赖 | 用途 |
|------|------|
| `tree-sitter` | C/Python 代码解析 |
| `anthropic` | Claude API 调用 |
| `mypy` | Python 类型检查 |
| `pylint` | Python 代码质量检查 |
| `networkx` | 调用图生成 |

---

## 许可证

MIT License