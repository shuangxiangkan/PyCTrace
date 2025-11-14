# PyCTrace

PyCTrace 是一个用于分析 C 代码中嵌入的 Python 代码的工具，能够提取 Python 代码片段并生成函数调用图。

## 功能特性

- 🔍 **C 代码解析**: 使用 Tree-sitter 解析 C 代码，提取其中的 Python 字符串
- 🐍 **Python 代码分析**: 解析提取的 Python 代码，识别函数定义和调用关系
- 📊 **调用图生成**: 生成多种格式的调用图可视化
  - DOT 格式 (Graphviz)
  - PDF 格式 (可直接查看)
  - Mermaid 格式 (支持在线渲染)
  - 文本格式 (简单易读)

## 安装要求

### Python 依赖
```bash
pip install -r requirements.txt
```

### 系统依赖
为了生成 PDF 格式的调用图，需要安装 Graphviz：

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
从 [Graphviz 官网](https://graphviz.org/download/) 下载并安装

## 使用方法

### 基本用法
```bash
python main.py <目录路径>
```

### 详细输出
```bash
python main.py <目录路径> -v
```

### 高级选项

#### 只生成Python相关的C调用图
```bash
python main.py <目录路径> --python-only
```
只包含与Python交互相关的C函数，过滤掉纯C函数调用，使Python-C交互更清晰。

#### 生成合并的Python-C调用图
```bash
python main.py <目录路径> --merge
```
合并C代码中的Python相关调用图和Python代码的调用图，展示完整的Python-C交互关系。

### 示例
```bash
# 分析单个目录
python main.py /path/to/c_code_directory

# 分析并显示详细信息
python main.py /path/to/c_code_directory -v

# 只生成Python相关的调用图
python main.py /path/to/c_code_directory --python-only -v

# 生成合并的Python-C调用图
python main.py /path/to/c_code_directory --merge -v
```

## 输出文件

程序会在 `output/` 目录下生成以下文件：

### Python 分析结果
- `python_fasten_callgraph.json` - Python FASTEN 格式调用图

### C 模块注册信息
- `c_python_module_registrations.json` - C 模块注册信息（JSON 格式，含元数据）
- `c_python_module_registrations.txt` - C 模块注册信息（TXT 格式，纯代码）

### LLM 解析结果
- `c_python_module_registrations_llm.json` - LLM 解析后的结构化模块信息
- `module_registration_prompt.txt` - 发送给 LLM 的 prompt
- `module_registration_response.txt` - LLM 的原始响应

文件说明：
- FASTEN 格式：标准化的软件依赖分析格式
- LLM 解析：使用 Claude 自动提取模块名、函数映射、参数类型等信息

## 项目结构

```
PyCTrace/
├── C/                                   # C 代码解析模块
│   └── py_module_extractor.py          # C 模块注册信息提取器
├── Python/                              # Python 代码解析模块
│   └── pycg_wrapper.py                  # PyCG 包装器（FASTEN 调用图生成）
├── llm/                                 # LLM 解析模块
│   ├── __init__.py                      # 包初始化
│   ├── llm_client.py                    # Claude API 客户端
│   ├── module_registration_prompts.py   # 模块注册 prompt 模板
│   ├── module_registration_schema.py    # 输出格式定义
│   ├── parse_module_registration.py     # LLM 解析器
│   └── README.md                        # LLM 模块文档
├── output/                              # 输出目录
├── main.py                              # 主程序入口
├── requirements.txt                     # Python 依赖
└── README.md                            # 项目说明
```

## 依赖说明

- **tree-sitter**: 代码解析引擎
- **pycg**: Python 调用图生成器
- **anthropic**: Claude API 客户端
- **python-dotenv**: 环境变量管理

## 环境配置

需要在项目根目录创建 `.env` 文件来配置 Claude API Key：

```bash
# 二选一即可
ANTHROPIC_API_KEY=your_api_key_here
# 或
CLAUDE_API_KEY=your_api_key_here
```

## 许可证

本项目采用 MIT 许可证。