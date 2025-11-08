"""
分析 python_external_calls.py 的外部调用
使用 PyCG Wrapper 生成 FASTEN 格式调用图并保存结果
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'Python'))

from pycg_wrapper import PyCGWrapper


def ensure_output_dir(output_dir):
    """确保输出目录存在"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")


def analyze_and_save():
    """分析 python_external_calls.py 并保存结果"""
    print("="*70)
    print("分析 Python 外部调用")
    print("="*70)
    
    # 文件路径
    test_file = os.path.join(os.path.dirname(__file__), 'python_external_calls.py')
    package_dir = os.path.dirname(test_file)
    output_dir = os.path.join(os.path.dirname(test_file), 'python_output')
    
    # 确保输出目录存在
    ensure_output_dir(output_dir)
    
    print(f"\n分析文件: {test_file}")
    print(f"输出目录: {output_dir}")
    
    # 创建 PyCG Wrapper 并分析
    print("\n正在分析...")
    wrapper = PyCGWrapper([test_file], package_dir)
    wrapper.analyze()
    
    # 获取 FASTEN 格式调用图
    print("生成 FASTEN 格式调用图...")
    fasten_cg = wrapper.get_fasten_call_graph(
        product="python_external_calls",
        forge="Local",
        version="1.0.0",
        timestamp=int(datetime.now().timestamp())
    )
    
    # 获取外部调用信息
    print("获取外部调用信息...")
    external_calls = wrapper.get_external_calls(
        include_builtin=False,
        product="python_external_calls",
        forge="Local",
        version="1.0.0",
        timestamp=int(datetime.now().timestamp())
    )
    
    # 保存结果
    print("\n保存结果...")
    
    # 1. 保存 FASTEN 格式调用图
    output_file_1 = os.path.join(output_dir, 'fasten_call_graph.json')
    with open(output_file_1, 'w', encoding='utf-8') as f:
        json.dump(fasten_cg, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {output_file_1}")
    
    # 2. 保存外部调用信息
    output_file_2 = os.path.join(output_dir, 'external_calls.json')
    with open(output_file_2, 'w', encoding='utf-8') as f:
        json.dump(external_calls, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存: {output_file_2}")
    
    # 打印摘要
    print("\n" + "="*70)
    print("分析摘要")
    print("="*70)
    stats = external_calls['statistics']
    print(f"外部函数总数: {stats['total_undefined']}")
    print(f"外部模块数量: {stats['modules_count']}")
    print(f"外部调用总数: {stats['total_call_edges']}")
    print("\n" + "="*70)
    print("✓ 分析完成！结果已保存到 python_output/ 目录")
    print("="*70)


if __name__ == "__main__":
    try:
        analyze_and_save()
    except Exception as e:
        print(f"\n✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

