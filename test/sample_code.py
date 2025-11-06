"""
测试样例代码
用于测试 PyCG 调用图生成功能
"""


def hello():
    """简单的问候函数"""
    print("Hello, World!")


def greet(name):
    """带参数的问候函数"""
    message = f"Hello, {name}!"
    print(message)
    return message


def main():
    """主函数，调用其他函数"""
    hello()
    greet("Alice")
    greet("Bob")
    
    # 调用类方法
    calc = Calculator()
    result = calc.add(10, 20)
    print(f"Result: {result}")
    
    # 调用嵌套函数
    process_data([1, 2, 3, 4, 5])


def process_data(data):
    """处理数据，包含嵌套函数"""
    def filter_even(x):
        return x % 2 == 0
    
    def double(x):
        return x * 2
    
    filtered = [x for x in data if filter_even(x)]
    doubled = [double(x) for x in filtered]
    return doubled


class Calculator:
    """计算器类"""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        """加法"""
        self.result = a + b
        return self.result
    
    def subtract(self, a, b):
        """减法"""
        self.result = a - b
        return self.result
    
    def multiply(self, a, b):
        """乘法"""
        self.result = self._calculate_multiply(a, b)
        return self.result
    
    def _calculate_multiply(self, a, b):
        """内部计算乘法"""
        return a * b


class AdvancedCalculator(Calculator):
    """高级计算器，继承自 Calculator"""
    
    def power(self, base, exponent):
        """幂运算"""
        result = 1
        for _ in range(exponent):
            result = self.multiply(result, base)
        return result
    
    def factorial(self, n):
        """阶乘"""
        if n <= 1:
            return 1
        return self.multiply(n, self.factorial(n - 1))


def external_function():
    """调用外部模块的函数"""
    import os
    import json
    
    # 调用 os 模块的函数
    current_dir = os.getcwd()
    
    # 调用 json 模块的函数
    data = {"name": "test", "value": 123}
    json_str = json.dumps(data)
    
    return json_str


if __name__ == "__main__":
    main()
    
    # 测试高级计算器
    adv_calc = AdvancedCalculator()
    print(f"2^3 = {adv_calc.power(2, 3)}")
    print(f"5! = {adv_calc.factorial(5)}")
    
    # 测试外部函数调用
    result = external_function()
    print(f"JSON result: {result}")

