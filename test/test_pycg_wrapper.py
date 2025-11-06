"""
测试 PyCG Wrapper
测试通过编码方式调用 PyCG 接口生成调用图
"""

import sys
import os
import json

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'Python'))

from pycg_wrapper import PyCGWrapper, generate_call_graph


def test_simple_call_graph():
    """测试生成简单格式的调用图"""
    print("\n" + "="*70)
    print("测试 1: 生成简单格式的调用图")
    print("="*70)
    
    # 使用测试样例文件
    test_file = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    package_dir = os.path.dirname(test_file)
    
    try:
        # 创建 wrapper 并分析
        wrapper = PyCGWrapper([test_file], package_dir)
        wrapper.analyze()
        
        # 获取简单格式的调用图
        call_graph = wrapper.get_simple_call_graph()
        
        print("\n✓ 成功生成简单格式的调用图")
        print(f"\n调用图内容:")
        print(json.dumps(call_graph, indent=2, ensure_ascii=False))
        
        # 获取函数列表
        functions = wrapper.get_functions()
        print(f"\n函数列表: {functions}")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fasten_call_graph():
    """测试生成 FASTEN 格式的调用图"""
    print("\n" + "="*70)
    print("测试 2: 生成 FASTEN 格式的调用图")
    print("="*70)
    
    # 使用测试样例文件
    test_file = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    package_dir = os.path.dirname(test_file)
    
    try:
        # 创建 wrapper 并分析
        wrapper = PyCGWrapper([test_file], package_dir)
        wrapper.analyze()
        
        # 获取 FASTEN 格式的调用图
        fasten_cg = wrapper.get_fasten_call_graph(
            product="test_sample",
            forge="PyPI",
            version="0.1.0",
            timestamp=1234567890
        )
        
        print("\n✓ 成功生成 FASTEN 格式的调用图")
        print(f"\n调用图内容（部分）:")
        # 只打印主要字段，避免输出过长
        print(f"  Product: {fasten_cg.get('product')}")
        print(f"  Forge: {fasten_cg.get('forge')}")
        print(f"  Generator: {fasten_cg.get('generator')}")
        print(f"  Version: {fasten_cg.get('version')}")
        print(f"  Timestamp: {fasten_cg.get('timestamp')}")
        print(f"  Total Nodes: {fasten_cg.get('nodes')}")
        
        if 'modules' in fasten_cg:
            internal_mods = fasten_cg['modules'].get('internal', {})
            external_mods = fasten_cg['modules'].get('external', {})
            print(f"  Internal Modules: {len(internal_mods)}")
            print(f"  External Modules: {len(external_mods)}")
        
        if 'graph' in fasten_cg:
            graph = fasten_cg['graph']
            print(f"  Internal Calls: {len(graph.get('internalCalls', []))}")
            print(f"  External Calls: {len(graph.get('externalCalls', []))}")
        
        print(f"\n完整 FASTEN 格式调用图:")
        print(json.dumps(fasten_cg, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """测试便捷函数"""
    print("\n" + "="*70)
    print("测试 3: 使用便捷函数生成调用图")
    print("="*70)
    
    # 使用测试样例文件
    test_file = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    
    try:
        # 测试简单格式
        print("\n使用便捷函数生成简单格式...")
        simple_cg = generate_call_graph(test_file, format_type='simple')
        print(f"✓ 简单格式生成成功，包含 {len(simple_cg)} 个节点")
        
        # 测试 FASTEN 格式
        print("\n使用便捷函数生成 FASTEN 格式...")
        fasten_cg = generate_call_graph(test_file, format_type='fasten')
        print(f"✓ FASTEN 格式生成成功，包含 {fasten_cg.get('nodes', 0)} 个节点")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_functions_and_classes():
    """测试获取函数和类信息"""
    print("\n" + "="*70)
    print("测试 4: 获取函数和类信息")
    print("="*70)
    
    # 使用测试样例文件
    test_file = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    package_dir = os.path.dirname(test_file)
    
    try:
        # 创建 wrapper 并分析
        wrapper = PyCGWrapper([test_file], package_dir)
        wrapper.analyze()
        
        # 获取函数列表
        functions = wrapper.get_functions()
        print(f"\n函数列表 ({len(functions)} 个):")
        for func in functions:
            print(f"  - {func}")
        
        # 获取类信息
        classes = wrapper.get_classes()
        print(f"\n类信息 ({len(classes)} 个):")
        for cls_name, cls_info in classes.items():
            print(f"  - {cls_name}")
            print(f"    模块: {cls_info.get('module')}")
            print(f"    MRO: {cls_info.get('mro')}")
        
        print("\n✓ 成功获取函数和类信息")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("PyCG Wrapper 测试套件")
    print("="*70)
    
    # 检查测试文件是否存在
    test_file = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    if not os.path.exists(test_file):
        print(f"\n错误: 测试文件不存在: {test_file}")
        print("请确保 sample_code.py 文件存在于 test 目录中")
        return
    
    # 运行所有测试
    results = []
    results.append(("简单格式调用图", test_simple_call_graph()))
    results.append(("FASTEN格式调用图", test_fasten_call_graph()))
    results.append(("便捷函数", test_convenience_function()))
    results.append(("函数和类信息", test_get_functions_and_classes()))
    
    # 打印测试结果摘要
    print("\n" + "="*70)
    print("测试结果摘要")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "-"*70)
    print(f"总计: {passed}/{total} 个测试通过")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

