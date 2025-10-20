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

### 示例
```bash
# 分析单个目录
python main.py /path/to/c_code_directory

# 分析并显示详细信息
python main.py /path/to/c_code_directory -v
```

## 输出文件

程序会在 `output/` 目录下生成以下文件：

- `python_call_graph.dot` - Graphviz DOT 格式
- `python_call_graph.pdf` - PDF 格式调用图
- `python_call_graph.mmd` - Mermaid 格式
- `python_call_graph.txt` - 文本格式

## 项目结构

```
PyCTrace/
├── C/                  # C 代码解析模块
│   └── c_parser.py
├── Python/             # Python 代码解析模块
│   └── python_parser.py
├── Utils/              # 工具模块
│   ├── file_collector.py
│   ├── graph_visualizer.py
│   └── string_utils.py
├── main.py             # 主程序入口
├── requirements.txt    # Python 依赖
└── README.md          # 项目说明
```

## 依赖说明

- **tree-sitter**: 代码解析引擎
- **graphviz**: Python Graphviz 接口
- **networkx**: 图数据结构处理
- **click**: 命令行界面

## 许可证

本项目采用 MIT 许可证。