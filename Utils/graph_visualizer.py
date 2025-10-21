"""
图形可视化工具
用于生成和可视化Python调用图
"""

from typing import Dict, List
import os
import subprocess
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


class CallGraphVisualizer:
    """调用图可视化器"""
    
    def __init__(self):
        pass
    
    def generate_dot_graph(self, call_graph: Dict[str, List[str]], title: str = "Python Call Graph") -> str:
        """
        生成DOT格式的调用图
        
        Args:
            call_graph: 调用图字典，格式为 {caller: [callee1, callee2, ...]}
            title: 图的标题
            
        Returns:
            str: DOT格式的图形描述
        """
        dot_content = []
        dot_content.append("digraph CallGraph {")
        dot_content.append(f'    label="{title}";')
        dot_content.append("    rankdir=TB;")
        dot_content.append("    node [shape=box, style=filled, fillcolor=lightblue];")
        dot_content.append("")
        
        # 添加所有节点
        all_functions = set(call_graph.keys())
        for callers in call_graph.values():
            all_functions.update(callers)
        
        for func in sorted(all_functions):
            dot_content.append(f'    "{func}";')
        
        dot_content.append("")
        
        # 添加边（调用关系）
        for caller, callees in call_graph.items():
            for callee in callees:
                dot_content.append(f'    "{caller}" -> "{callee}";')
        
        dot_content.append("}")
        
        return "\n".join(dot_content)
    
    def save_dot_file(self, call_graph: Dict[str, List[str]], output_path: str, title: str = "Python Call Graph") -> str:
        """
        保存DOT格式的调用图到文件
        
        Args:
            call_graph: 调用图字典
            output_path: 输出文件路径
            title: 图的标题
            
        Returns:
            str: 保存的文件路径
        """
        dot_content = self.generate_dot_graph(call_graph, title)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        
        return output_path
    
    def save_pdf_file(self, call_graph: Dict[str, List[str]], output_path: str, title: str = "Python Call Graph") -> str:
        """
        保存PDF格式的调用图到文件
        
        Args:
            call_graph: 调用图字典
            output_path: 输出文件路径
            title: 图的标题
            
        Returns:
            str: 保存的文件路径，如果生成失败返回None
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if GRAPHVIZ_AVAILABLE:
                # 优先使用Python graphviz包
                return self._save_pdf_with_graphviz_package(call_graph, output_path, title)
            else:
                # fallback到subprocess调用
                return self._save_pdf_with_subprocess(call_graph, output_path, title)
                
        except Exception as e:
            print(f"警告: 生成PDF时出错: {e}")
            return None
    
    def _save_pdf_with_graphviz_package(self, call_graph: Dict[str, List[str]], output_path: str, title: str) -> str:
        """使用Python graphviz包生成PDF"""
        try:
            # 创建Graphviz对象
            dot = graphviz.Digraph(comment=title)
            dot.attr(rankdir='TB', label=title)
            dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
            
            # 添加所有节点
            all_functions = set(call_graph.keys())
            for callers in call_graph.values():
                all_functions.update(callers)
            
            for func in sorted(all_functions):
                dot.node(func, func)
            
            # 添加边（调用关系）
            for caller, callees in call_graph.items():
                for callee in callees:
                    dot.edge(caller, callee)
            
            # 生成PDF文件
            output_path_without_ext = output_path.rsplit('.', 1)[0]
            dot.render(output_path_without_ext, format='pdf', cleanup=True)
            
            return output_path
            
        except Exception as e:
            print(f"警告: 使用graphviz包生成PDF失败: {e}")
            # fallback到subprocess方法
            return self._save_pdf_with_subprocess(call_graph, output_path, title)
    
    def _save_pdf_with_subprocess(self, call_graph: Dict[str, List[str]], output_path: str, title: str) -> str:
        """使用subprocess调用系统dot命令生成PDF"""
        try:
            # 生成DOT内容
            dot_content = self.generate_dot_graph(call_graph, title)
            
            # 使用subprocess调用dot命令生成PDF
            process = subprocess.Popen(
                ['dot', '-Tpdf', '-o', output_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=dot_content)
            
            if process.returncode == 0:
                return output_path
            else:
                print(f"警告: 生成PDF失败: {stderr}")
                return None
                
        except FileNotFoundError:
            print("警告: 未找到Graphviz工具，无法生成PDF。请安装Graphviz: sudo apt-get install graphviz")
            return None
    
    def generate_simple_text_graph(self, call_graph: Dict[str, List[str]]) -> str:
        """
        生成简单的文本格式调用图
        
        Args:
            call_graph: 调用图字典
            
        Returns:
            str: 文本格式的调用图
        """
        if not call_graph:
            return "No function calls found."
        
        lines = []
        lines.append("Python Call Graph:")
        lines.append("=" * 50)
        
        for caller, callees in sorted(call_graph.items()):
            if callees:
                lines.append(f"\n{caller}:")
                for callee in sorted(callees):
                    lines.append(f"  └── {callee}")
            else:
                lines.append(f"\n{caller}: (no calls)")
        
        return "\n".join(lines)
    
    def print_call_graph(self, call_graph: Dict[str, List[str]]) -> None:
        """
        打印调用图到控制台
        
        Args:
            call_graph: 调用图字典
        """
        print(self.generate_simple_text_graph(call_graph))
    
    def generate_mermaid_graph(self, call_graph: Dict[str, List[str]], title: str = "Python Call Graph") -> str:
        """
        生成Mermaid格式的调用图
        
        Args:
            call_graph: 调用图字典
            title: 图的标题
            
        Returns:
            str: Mermaid格式的图形描述
        """
        mermaid_content = []
        mermaid_content.append("graph TD")
        mermaid_content.append(f"    title[{title}]")
        mermaid_content.append("")
        
        # 为函数名生成安全的ID
        func_to_id = {}
        for i, func in enumerate(sorted(set(call_graph.keys()) | 
                                      set(callee for callees in call_graph.values() for callee in callees))):
            func_to_id[func] = f"F{i}"
            mermaid_content.append(f"    {func_to_id[func]}[{func}]")
        
        mermaid_content.append("")
        
        # 添加调用关系
        for caller, callees in call_graph.items():
            for callee in callees:
                if caller in func_to_id and callee in func_to_id:
                    mermaid_content.append(f"    {func_to_id[caller]} --> {func_to_id[callee]}")
        
        return "\n".join(mermaid_content)
    
    def save_mermaid_file(self, call_graph: Dict[str, List[str]], output_path: str, title: str = "Python Call Graph") -> str:
        """
        保存Mermaid格式的调用图到文件
        
        Args:
            call_graph: 调用图字典
            output_path: 输出文件路径
            title: 图的标题
            
        Returns:
            str: 保存的文件路径
        """
        mermaid_content = self.generate_mermaid_graph(call_graph, title)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
        
        return output_path


def visualize_call_graph(call_graph: Dict[str, List[str]], 
                        output_dir: str = "output", 
                        filename_prefix: str = "call_graph",
                        title: str = "Python Call Graph") -> Dict[str, str]:
    """
    便捷函数：生成多种格式的调用图可视化
    
    Args:
        call_graph: 调用图字典
        output_dir: 输出目录
        filename_prefix: 文件名前缀
        title: 图的标题
        
    Returns:
        Dict[str, str]: 生成的文件路径字典
    """
    visualizer = CallGraphVisualizer()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # 生成DOT文件
    dot_path = os.path.join(output_dir, f"{filename_prefix}.dot")
    results['dot'] = visualizer.save_dot_file(call_graph, dot_path, title)
    
    # 生成PDF文件
    pdf_path = os.path.join(output_dir, f"{filename_prefix}.pdf")
    pdf_result = visualizer.save_pdf_file(call_graph, pdf_path, title)
    if pdf_result:
        results['pdf'] = pdf_result
    
    # 生成Mermaid文件
    mermaid_path = os.path.join(output_dir, f"{filename_prefix}.mmd")
    results['mermaid'] = visualizer.save_mermaid_file(call_graph, mermaid_path, title)
    
    # 生成文本文件
    text_path = os.path.join(output_dir, f"{filename_prefix}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(visualizer.generate_simple_text_graph(call_graph))
    results['text'] = text_path
    
    # 打印到控制台
    visualizer.print_call_graph(call_graph)
    
    return results


def generate_call_graph_visualization(call_graph, filename_prefix, title, verbose=False):
    """
    统一的调用图生成函数
    
    Args:
        call_graph: 调用图字典
        filename_prefix: 文件名前缀
        title: 图标题
        verbose: 是否显示详细信息
    """
    if call_graph and any(call_graph.values()):
        if verbose:
            print("生成调用图可视化文件...")
        
        output_files = visualize_call_graph(
            call_graph,
            output_dir="output",
            filename_prefix=filename_prefix,
            title=title
        )
        
        if verbose:
            print(f"调用图文件已生成:")
            for format_type, file_path in output_files.items():
                print(f"  {format_type.upper()}: {file_path}")
        
        return output_files
    else:
        if verbose:
            print("未发现函数调用关系")
        return None


def generate_merged_call_graph_visualization(
    call_graph: Dict[str, List[str]],
    node_types: Dict[str, str],
    c_to_python_calls: List[tuple],
    python_to_c_calls: List[tuple],
    filename_prefix: str = "merged_call_graph",
    title: str = "Merged Python-C Call Graph",
    verbose: bool = False
):
    """
    生成带颜色的合并调用图可视化
    
    Args:
        call_graph: 调用图字典
        node_types: 节点类型字典 {node: type}
        c_to_python_calls: C->Python调用列表
        python_to_c_calls: Python->C调用列表
        filename_prefix: 文件名前缀
        title: 图标题
        verbose: 是否显示详细信息
    """
    if verbose:
        print("生成带颜色的合并调用图...")
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成DOT格式文件
    dot_content = _generate_colored_dot_graph(
        call_graph, 
        node_types, 
        c_to_python_calls, 
        python_to_c_calls, 
        title
    )
    
    # 保存DOT文件
    dot_path = os.path.join(output_dir, f"{filename_prefix}.dot")
    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    
    results = {'dot': dot_path}
    
    # 生成PDF（如果graphviz可用）
    if GRAPHVIZ_AVAILABLE:
        try:
            src = graphviz.Source(dot_content)
            pdf_path = os.path.join(output_dir, filename_prefix)
            src.render(pdf_path, format='pdf', cleanup=True)
            results['pdf'] = f"{pdf_path}.pdf"
        except Exception as e:
            if verbose:
                print(f"生成PDF失败: {e}")
    
    # 生成Mermaid格式
    mermaid_content = _generate_colored_mermaid_graph(
        call_graph, 
        node_types, 
        c_to_python_calls, 
        python_to_c_calls
    )
    mmd_path = os.path.join(output_dir, f"{filename_prefix}.mmd")
    with open(mmd_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_content)
    results['mermaid'] = mmd_path
    
    # 生成文本格式
    visualizer = CallGraphVisualizer()
    text_content = visualizer.generate_simple_text_graph(call_graph)
    text_path = os.path.join(output_dir, f"{filename_prefix}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    results['text'] = text_path
    
    # 打印到控制台
    visualizer.print_call_graph(call_graph)
    
    if verbose:
        print(f"调用图文件已生成:")
        for format_type, file_path in results.items():
            print(f"  {format_type.upper()}: {file_path}")
    
    return results


def _generate_colored_dot_graph(
    call_graph: Dict[str, List[str]],
    node_types: Dict[str, str],
    c_to_python_calls: List[tuple],
    python_to_c_calls: List[tuple],
    title: str
) -> str:
    """生成带颜色的DOT格式调用图"""
    dot_lines = []
    dot_lines.append("digraph CallGraph {")
    dot_lines.append(f'    label="{title}";')
    dot_lines.append("    rankdir=TB;")
    dot_lines.append("    node [shape=box, style=filled];")
    dot_lines.append("")
    
    # 定义颜色
    colors = {
        'c_function': 'lightblue',
        'registered_c_function': 'lightgreen',
        'python_function': 'lightyellow'
    }
    
    # 添加所有节点（带颜色）
    all_functions = set(call_graph.keys())
    for callees in call_graph.values():
        all_functions.update(callees)
    
    for func in sorted(all_functions):
        node_type = node_types.get(func, 'python_function')
        color = colors.get(node_type, 'white')
        dot_lines.append(f'    "{func}" [fillcolor={color}];')
    
    dot_lines.append("")
    
    # 创建跨语言调用集合（用于着色）
    c_to_py_set = set(c_to_python_calls)
    py_to_c_set = set(python_to_c_calls)
    
    # 添加边（带颜色）
    for caller, callees in call_graph.items():
        for callee in callees:
            edge = (caller, callee)
            
            # 确定边的颜色
            if edge in c_to_py_set:
                # C->Python调用：蓝色粗线
                dot_lines.append(f'    "{caller}" -> "{callee}" [color=blue, penwidth=2.0];')
            elif edge in py_to_c_set:
                # Python->C调用：红色粗线
                dot_lines.append(f'    "{caller}" -> "{callee}" [color=red, penwidth=2.0];')
            else:
                # 同语言调用：默认黑色
                dot_lines.append(f'    "{caller}" -> "{callee}";')
    
    # 添加图例
    dot_lines.append("")
    dot_lines.append("    // Legend")
    dot_lines.append('    subgraph cluster_legend {')
    dot_lines.append('        label="Legend";')
    dot_lines.append('        style=filled;')
    dot_lines.append('        fillcolor=white;')
    dot_lines.append('        "C Function" [fillcolor=lightblue];')
    dot_lines.append('        "Registered C\\n(Python name)" [fillcolor=lightgreen];')
    dot_lines.append('        "Python Function" [fillcolor=lightyellow];')
    dot_lines.append('        "C Function" -> "Registered C\\n(Python name)" [style=invis];')
    dot_lines.append('        "Registered C\\n(Python name)" -> "Python Function" [style=invis];')
    dot_lines.append('    }')
    
    dot_lines.append("}")
    
    return "\n".join(dot_lines)


def _generate_colored_mermaid_graph(
    call_graph: Dict[str, List[str]],
    node_types: Dict[str, str],
    c_to_python_calls: List[tuple],
    python_to_c_calls: List[tuple]
) -> str:
    """生成带颜色的Mermaid格式调用图"""
    mermaid_lines = []
    mermaid_lines.append("graph TB")
    
    # 添加节点样式定义
    mermaid_lines.append("    classDef cFunc fill:#add8e6;")  # lightblue
    mermaid_lines.append("    classDef regCFunc fill:#90ee90;")  # lightgreen
    mermaid_lines.append("    classDef pyFunc fill:#ffffe0;")  # lightyellow
    mermaid_lines.append("")
    
    # 为节点创建ID映射（移除特殊字符）
    node_ids = {}
    counter = 0
    for func in call_graph.keys():
        node_ids[func] = f"node{counter}"
        counter += 1
    
    # 添加节点定义
    for func, node_id in node_ids.items():
        # 转义特殊字符
        label = func.replace('"', '\\"')
        node_type = node_types.get(func, 'python_function')
        
        # 确定样式类
        if node_type == 'c_function':
            style_class = "cFunc"
        elif node_type == 'registered_c_function':
            style_class = "regCFunc"
        else:
            style_class = "pyFunc"
        
        mermaid_lines.append(f'    {node_id}["{label}"]:::{style_class}')
    
    mermaid_lines.append("")
    
    # 创建跨语言调用集合
    c_to_py_set = set(c_to_python_calls)
    py_to_c_set = set(python_to_c_calls)
    
    # 添加边
    for caller, callees in call_graph.items():
        caller_id = node_ids.get(caller, caller)
        for callee in callees:
            callee_id = node_ids.get(callee, callee)
            edge = (caller, callee)
            
            # 确定边的样式
            if edge in c_to_py_set:
                # C->Python: 蓝色粗线
                mermaid_lines.append(f'    {caller_id} ==>|C-&gt;Py| {callee_id}')
            elif edge in py_to_c_set:
                # Python->C: 红色粗线
                mermaid_lines.append(f'    {caller_id} ==>|Py-&gt;C| {callee_id}')
            else:
                # 同语言调用
                mermaid_lines.append(f'    {caller_id} --> {callee_id}')
    
    return "\n".join(mermaid_lines)