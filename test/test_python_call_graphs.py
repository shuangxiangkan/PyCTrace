#!/usr/bin/env python3
"""
生成 python_external_calls.py 的调用图
支持简单 JSON 格式和 FASTEN 格式
"""

import sys
import os
import json
from pathlib import Path

# 添加 PyCG 包装器路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Python'))
from pycg_wrapper import PyCGWrapper

def main():
    # 文件路径
    script_dir = Path(__file__).parent
    target_file = script_dir / "python_external_calls.py"
    output_dir = script_dir / "python_output"
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 包路径（文件所在目录）
    package_path = str(script_dir)
    
    print(f"分析文件: {target_file}")
    print(f"包路径: {package_path}")
    print("-" * 60)
    
    # 创建包装器并分析
    wrapper = PyCGWrapper(
        entry_points=[str(target_file)],
        package=package_path
    )
    wrapper.analyze()
    
    # 1. 生成简单 JSON 格式
    print("\n生成简单 JSON 格式调用图...")
    simple_cg = wrapper.get_simple_call_graph()
    simple_output = output_dir / "simple_call_graph.json"
    with open(simple_output, 'w', encoding='utf-8') as f:
        json.dump(simple_cg, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存到: {simple_output}")
    print(f"  包含 {len(simple_cg)} 个函数节点")
    
    # 2. 生成 FASTEN 格式
    print("\n生成 FASTEN 格式调用图...")
    fasten_cg = wrapper.get_fasten_call_graph(
        product="python_external_calls",
        forge="Local",
        version="1.0.0",
        timestamp=0
    )
    fasten_output = output_dir / "fasten_call_graph_external_calls.json"
    with open(fasten_output, 'w', encoding='utf-8') as f:
        json.dump(fasten_cg, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存到: {fasten_output}")
    
    # 显示 FASTEN 格式的统计信息
    if 'graph' in fasten_cg:
        graph = fasten_cg['graph']
        internal_calls = len(graph.get('internalCalls', []))
        external_calls = len(graph.get('externalCalls', []))
        print(f"  内部调用: {internal_calls} 条")
        print(f"  外部调用: {external_calls} 条")
    
    if 'modules' in fasten_cg:
        modules = fasten_cg['modules']
        internal_modules = len(modules.get('internal', {}))
        external_modules = len(modules.get('external', {}))
        print(f"  内部模块: {internal_modules} 个")
        print(f"  外部模块: {external_modules} 个")
    
    print("\n" + "=" * 60)
    print("调用图生成完成！")
    print(f"简单格式: {simple_output}")
    print(f"FASTEN 格式: {fasten_output}")

if __name__ == "__main__":
    main()

