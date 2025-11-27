# PyCTrace

PyCTrace 是一个用于大模型辅助的，分析 Python-C 混合代码的静态分析工具。它将 C 代码中的 Python 模块注册和 API 调用逻辑用大模型翻译成等价的 Python 代码，通过静态检查发现 Python-C 交互中的潜在错误。

## 快速开始

### 1. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件（根据使用的模型配置）：

```bash
ANTHROPIC_API_KEY=your_anthropic_key  # Claude 模型
OPENAI_API_KEY=your_openai_key        # OpenAI 模型（可选）
GEMINI_API_KEY=your_gemini_key        # Gemini 模型（可选）
```

### 3. 运行分析，以PyCTrace的example为例

```bash
python main.py /path-to-PyCTrace/example
```

### 4. 查看结果

分析完成后，输出目录默认是最有一个文件夹名称+output, 比如 `example_output/` 包含以下内容：

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

---

## 输出文件详解

### 📁 目录结构
```
example_output/
├── py/                                    # 生成的 Python 代码（独立文件）
│   ├── host.py                            # C 扩展模块接口
│   └── python_call_in_c.py                # C 中调用的 Python 代码
├── all_py/                                # 合并后的 Python 代码（用于检查）
│   ├── host.py                            # 同 py/host.py
│   └── python_call_in_c.py                # 同 py/python_call_in_c.py
├── c_python_module_registrations.*        # C 模块注册分析
├── c_python_call_extraction.*             # Python 调用提取
├── type_check_report.*                    # 类型检查报告
├── call_check_report.*                    # 调用检查报告
└── *_prompt.txt / *_response.txt          # LLM 交互记录
```

### 📋 文件说明

#### 1. C 模块注册分析（Module Registration）
| 文件 | 格式 | 内容 |
|------|------|------|
| `c_python_module_registrations.txt` | 文本 | C 模块注册的原始代码片段（`PyMethodDef`、`PyModuleDef` 等） |
| `c_python_module_registrations.json` | JSON | 模块注册代码 + 元数据（文件路径、行号） |
| `c_python_module_registrations_llm.json` | JSON | LLM 解析后的结构化信息（模块名、函数签名、参数类型） |

**示例**：`c_python_module_registrations_llm.json`
```json
{
  "modules": [{
    "module_name": "host",
    "functions": [{
      "python_name": "tick",
      "c_function_name": "py_tick",
      "param_format": "l",
      "param_types": ["long"],
      "return_type": "None"
    }]
  }]
}
```

#### 2. Python 调用提取（Call Extraction）
| 文件 | 格式 | 内容 |
|------|------|------|
| `c_python_call_extraction.txt` | 文本 | C 中 Python API 调用的代码片段（`PyRun_String`、`PyObject_CallObject` 等） |
| `c_python_call_extraction.json` | JSON | 调用代码 + 元数据 |
| `c_python_call_extraction_llm.json` | JSON | LLM 翻译后的等价 Python 代码 |

**关键**：LLM 会推断 C 代码的执行逻辑，例如：
- `snprintf(fname, 32, "add_%s", choose_suffix())` → 推断出 `fname = "add_v1"`
- `PyDict_GetItemString(g, fname)` → 翻译为 `add_v1` 函数查找
- `Py_BuildValue("(iii)", 10, 20, 3)` → 翻译为参数 `(10, 20, 3)`

#### 3. 生成的 Python 代码
| 目录/文件 | 作用 |
|-----------|------|
| `py/host.py` | C 扩展模块 `host` 的 Python stub，包含函数签名和类型标注 |
| `py/python_call_in_c.py` | 从 C 字符串中提取的 Python 代码 + LLM 翻译的调用逻辑 |
| `all_py/` | 将 `py/` 中的所有文件合并到同一目录，供 mypy/pylint 分析 |

**为什么需要两个目录？**
- `py/`：独立文件，便于查看和理解
- `all_py/`：所有文件在同一目录下，模拟运行时的 import 环境，确保 `import host` 能正确解析

#### 4. 静态检查报告
| 文件 | 工具 | 检测内容 |
|------|------|----------|
| `type_check_report.txt/json` | Mypy | 类型错误、未定义变量、导入错误 |
| `call_check_report.txt/json` | Pylint | 函数调用错误、参数不匹配、代码质量问题 |

#### 5. LLM 交互记录（调试用）
| 文件 | 内容 |
|------|------|
| `module_registration_prompt.txt` | 发送给 LLM 的模块注册分析 prompt |
| `module_registration_response.txt` | LLM 返回的原始 JSON |
| `python_call_prompt.txt` | 发送给 LLM 的 Python 调用翻译 prompt |
| `python_call_response.txt` | LLM 返回的翻译结果 |

---

## 原理说明

PyCTrace 通过 **四步流程** 将 C 代码中的 Python 交互逻辑翻译为纯 Python 代码，实现静态分析：

### 1️⃣ C 代码解析与程序切片（Tree-sitter + DDG）

#### 第一步：AST 解析
使用 Tree-sitter 解析 C 源码，识别目标代码：
- **模块注册代码** - `PyMethodDef`、`PyModuleDef`、`PyModule_Create` 等
- **Python 调用代码** - `PyRun_String`、`PyObject_CallObject`、`PyDict_GetItemString` 等

#### 第二步：构建数据依赖图（DDG）
对每个包含 Python API 调用的函数构建 DDG：
- **DDG 节点**：函数中的每条语句（赋值、声明、表达式等）
- **DDG 边**：def-use 链（变量定义到变量使用的数据流）
- **def-use 信息**：每个节点记录其定义（def）和使用（use）的变量集合

#### 第三步：程序切片提取
基于 DDG 的 def-use 链，提取与 Python 调用相关的最小代码切片：

**切片算法**（递归追踪）：
1. **初始化**：从 Python API 调用语句开始，提取调用涉及的变量
   - 例如 `PyObject_CallObject(fn, args)` → 初始变量集 = `{fn, args, ret}`

2. **后向切片**：沿 def-use 链向上追踪
   - 遍历所有语句的 def/use 信息
   - 如果语句的 def 或 use 包含追踪变量，加入切片
   - 将该语句的所有 def/use 变量加入追踪集合

3. **递归扩展**：重复步骤 2，直到没有新语句被添加
   - 例如：`fn` 来自 `PyDict_GetItemString(g, fname)`
   - 继续追踪 `fname`，发现来自 `snprintf(fname, 32, "add_%s", choose_suffix())`
   - 继续追踪 `choose_suffix()`，找到函数定义

4. **跨函数追踪**：对于函数调用，从全局函数注册表中查找定义并递归分析

**切片结果**：只包含影响 Python 调用的代码，过滤无关的 C 逻辑（如日志、错误处理等）

### 2️⃣ LLM 翻译
将 C 代码片段发送给 LLM（默认 Claude，支持 OpenAI/Gemini 等），执行两项翻译任务：

**任务 1：解析模块注册**
- 从 `PyMethodDef` 提取函数名映射（`"tick"` → `py_tick`）
- 从 `PyArg_ParseTuple` 格式字符串推断参数类型（`"l"` → `int`）
- 生成 Python stub：`def tick(arg0: int) -> None: pass`

**任务 2：翻译 Python 调用逻辑**
- 提取 `PyRun_String` 中的 Python 代码字符串
- 推断 `PyObject_CallObject` 的调用逻辑：
  - 跟踪 C 变量（如 `snprintf` 生成的 `fname`）
  - 分析 `PyDict_GetItemString` 查找的函数名
  - 解析 `Py_BuildValue` 构造的参数
- 生成等价的 Python 调用：`add_v1(10, 20, 3)`

### 3️⃣ Python 代码合并
将两部分代码放在同一目录下：
- C 扩展模块的 stub（`host.py`）
- 翻译后的 Python 调用代码（`python_call_in_c.py`）

模拟真实运行时环境，使 `import host` 能够正确解析。

### 4️⃣ 静态检查
对生成的 Python 代码执行标准工具检查：
- **Mypy** - 类型检查、未定义变量检测
- **Pylint** - 函数调用检查、参数匹配验证

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
python main.py <目录路径> [-o 输出目录] [-m 模型名称]
```

**示例**：
```bash
# 使用默认模型 (claude-sonnet-4-20250514)
python main.py example

# 指定输出目录
python main.py example -o my_output

# 使用 OpenAI 模型
python main.py example --model gpt-4o

# 使用其他模型
python main.py example --model gemini-1.5-pro
```

**支持的模型**（使用 LiteLLM，支持 100+ 模型）：
- Claude: `claude-sonnet-4-20250514`, `claude-opus-4`, `claude-3-5-sonnet` 等
- OpenAI: `gpt-4o`, `gpt-4-turbo`, `o1`, `o3` 等
- Gemini: `gemini-1.5-pro`, `gemini-pro` 等
- 更多模型：https://docs.litellm.ai/docs/providers

---

## 依赖说明

| 依赖 | 用途 |
|------|------|
| `tree-sitter` | C/Python 代码解析 |
| `litellm` | 统一 LLM API 调用（支持 Claude/OpenAI/Gemini 等） |
| `mypy` | Python 类型检查 |
| `pylint` | Python 代码质量检查 |
| `networkx` | 调用图生成 |

---

## 许可证

MIT License