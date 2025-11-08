"""
Python 外部调用示例
包含3种类型的外部调用：C扩展、标准库、第三方库
"""

# ========== 1. C 扩展模块调用 ==========
try:
    import host  # C 扩展模块（来自 sample3）
    HAS_HOST = True
except ImportError:
    HAS_HOST = False

def call_c_extension_1():
    """调用 C 扩展的 tick 函数"""
    if HAS_HOST:
        host.tick(100)
        return "C extension called"
    return "C extension not available"

def call_c_extension_2():
    """多次调用 C 扩展"""
    if HAS_HOST:
        for i in range(5):
            host.tick(i)
    return "Multiple C calls"


# ========== 2. 标准库调用 ==========
import os
import json
import time

def call_stdlib_1():
    """调用 os 和 json 标准库"""
    current_dir = os.getcwd()
    data = {"path": current_dir, "count": 42}
    json_str = json.dumps(data)
    return json_str

def call_stdlib_2():
    """调用 time 标准库"""
    start = time.time()
    time.sleep(0.001)
    end = time.time()
    return end - start

def call_stdlib_3():
    """调用 os.path 标准库"""
    exists = os.path.exists(".")
    abs_path = os.path.abspath(".")
    return abs_path


# ========== 3. 第三方库调用 ==========
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def call_thirdparty_1():
    """调用 requests 库"""
    if HAS_REQUESTS:
        response = requests.get("https://api.github.com", timeout=5)
        return response.status_code
    return None

def call_thirdparty_2():
    """调用 numpy 库"""
    if HAS_NUMPY:
        arr = np.array([1, 2, 3, 4, 5])
        mean = np.mean(arr)
        return mean
    return None