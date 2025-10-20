"""
字符串处理工具模块
包含字符串清理、合并、Python代码识别等功能
"""

from typing import List
import re


def clean_string_literal(raw_string: str) -> str:
    """
    清理字符串字面量，去掉引号并处理转义字符
    
    Args:
        raw_string: 原始字符串（包含引号）
        
    Returns:
        str: 清理后的字符串内容
    """
    if not raw_string:
        return ""
    
    # 去掉首尾的引号
    if raw_string.startswith('"') and raw_string.endswith('"'):
        content = raw_string[1:-1]
    else:
        content = raw_string
    
    # 处理常见的转义字符
    content = content.replace('\\n', '\n')
    content = content.replace('\\t', '\t')
    content = content.replace('\\r', '\r')
    content = content.replace('\\"', '"')
    content = content.replace('\\\\', '\\')
    
    return content


def is_python_code(code: str) -> bool:
    """
    判断字符串是否为Python代码片段
    
    Args:
        code: 要检查的字符串
        
    Returns:
        bool: 是否为Python代码
    """
    if not code or len(code.strip()) < 3:
        return False
    
    code = code.strip()
    lines = code.split('\n')
    
    # Python关键字和模式
    python_keywords = {
        'import', 'from', 'def', 'class', 'if', 'elif', 'else', 'for', 'while',
        'try', 'except', 'finally', 'with', 'return', 'yield', 'lambda',
        'and', 'or', 'not', 'in', 'is', 'pass', 'break', 'continue',
        'global', 'nonlocal', 'assert', 'del', 'raise', 'async', 'await'
    }
    
    python_patterns = [
        r'^\s*import\s+\w+',           # import statements
        r'^\s*from\s+\w+\s+import',    # from import statements  
        r'^\s*def\s+\w+\s*\(',         # function definitions
        r'^\s*class\s+\w+',            # class definitions
        r'^\s*if\s+.*:',               # if statements
        r'^\s*for\s+.*:',              # for loops
        r'^\s*while\s+.*:',            # while loops
        r'^\s*try\s*:',                # try blocks
        r'^\s*with\s+.*:',             # with statements
        r'print\s*\(',                 # print function calls
        r'\.append\s*\(',              # method calls
        r'\.join\s*\(',                # method calls
        r'len\s*\(',                   # built-in functions
    ]
    
    # 检查是否包含Python关键字
    keyword_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查关键字
        words = line.split()
        for word in words:
            clean_word = word.strip('():,[]{}')  
            if clean_word in python_keywords:
                keyword_count += 1
    
    # 检查是否匹配Python模式
    pattern_matches = 0
    for line in lines:
        for pattern in python_patterns:
            if re.search(pattern, line):
                pattern_matches += 1
                break
    
    # 检查Python特有的语法特征
    has_python_syntax = any([
        ':' in code and ('def ' in code or 'if ' in code or 'for ' in code or 'while ' in code),
        'import ' in code,
        'print(' in code,
        code.count('    ') >= 2,  # 有缩进
        '.py' in code.lower(),
    ])
    
    # 综合判断
    total_lines = len([line for line in lines if line.strip()])
    if total_lines == 0:
        return False
        
    # 如果有明显的Python模式匹配，认为是Python代码
    if pattern_matches > 0:
        return True
        
    # 如果有Python关键字且有Python语法特征，认为是Python代码
    if keyword_count > 0 and has_python_syntax:
        return True
        
    # 如果关键字密度足够高，认为是Python代码
    if keyword_count >= max(1, total_lines * 0.3):
        return True
        
    return False


def could_be_python_start(s: str) -> bool:
    """
    检查字符串是否可能是Python代码的开始
    
    Args:
        s: 要检查的字符串
        
    Returns:
        bool: 是否可能是Python代码的开始
    """
    s = s.strip()
    if not s:
        return False
    
    # Python代码的典型开始模式
    python_starts = [
        'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
        'try:', 'with ', 'async def', '@'
    ]
    
    return any(s.startswith(start) for start in python_starts)


def could_be_python_continuation(s: str) -> bool:
    """
    检查字符串是否可能是Python代码的继续
    
    Args:
        s: 要检查的字符串
        
    Returns:
        bool: 是否可能是Python代码的继续
    """
    s = s.strip()
    if not s:
        return False
    
    # Python代码继续的模式
    # 1. 缩进的代码
    if s.startswith('    ') or s.startswith('\t'):
        return True
    
    # 2. Python关键字
    python_keywords = [
        'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
        'try:', 'except:', 'finally:', 'with ', 'return ', 'yield ',
        'import ', 'from ', 'print(', 'pass', 'break', 'continue'
    ]
    
    if any(keyword in s for keyword in python_keywords):
        return True
    
    # 3. 包含Python特有的语法
    if any(pattern in s for pattern in ['(', ')', ':', '=', '+', '-']):
        # 但排除明显不是Python的字符串
        if not any(pattern in s for pattern in ['%ld', '%lu', '%d', '%s', 'ERR', 'OK:']):
            return True
    
    return False


def merge_consecutive_strings(strings: List[str]) -> List[str]:
    """
    智能合并连续的字符串，特别是Python代码片段
    
    Args:
        strings: 字符串列表
        
    Returns:
        List[str]: 合并后的字符串列表
    """
    if not strings:
        return strings
    
    merged = []
    i = 0
    
    while i < len(strings):
        current = strings[i]
        
        # 检查当前字符串是否可能是Python代码的开始
        if could_be_python_start(current):
            # 尝试合并后续可能的Python代码片段
            merged_python = current
            j = i + 1
            
            # 继续合并，直到遇到明显不是Python代码的字符串
            while j < len(strings):
                next_string = strings[j]
                
                # 如果下一个字符串看起来像Python代码的继续，就合并
                if could_be_python_continuation(next_string):
                    merged_python += next_string
                    j += 1
                else:
                    break
            
            merged.append(merged_python)
            i = j
        else:
            # 不是Python代码，单独保留
            merged.append(current)
            i += 1
    
    return merged


def filter_python_snippets(strings: List[str]) -> List[str]:
    """
    从字符串列表中过滤出Python代码片段
    
    Args:
        strings: 字符串列表
        
    Returns:
        List[str]: Python代码片段列表
    """
    python_snippets = []
    for string in strings:
        if is_python_code(string):
            python_snippets.append(string)
    return python_snippets


def extract_python_from_strings(raw_strings: List[str]) -> List[str]:
    """
    从原始字符串列表中提取Python代码片段的完整流程
    
    Args:
        raw_strings: 原始字符串列表
        
    Returns:
        List[str]: Python代码片段列表
    """
    # 先尝试合并所有连续的字符串
    merged_strings = merge_consecutive_strings(raw_strings)
    
    # 只返回Python代码片段
    python_snippets = filter_python_snippets(merged_strings)
    
    return python_snippets