#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from mypy import api


@dataclass
class TypeIssue:
    file: str
    line: int
    column: int
    severity: str
    code: str
    message: str


class MypyTypeChecker:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.issues: List[TypeIssue] = []
        self.raw_output: str = ""
        self.raw_stderr: str = ""
        
    def check_types(self) -> List[TypeIssue]:
        print("使用 mypy API 进行类型检查...")
        try:
            py_files = [str(f) for f in self.target_dir.rglob('*.py')]
            if not py_files:
                print("  ⚠ 未找到 Python 文件")
                return []
            
            args = [
                '--show-column-numbers',
                '--show-error-codes',
            ] + py_files
            
            result = api.run(args)
            stdout, stderr, exit_status = result
            
            self.raw_output = stdout
            self.raw_stderr = stderr
            
            issues = []
            for line in stdout.strip().split('\n'):
                if not line or line.startswith('Found') or line.startswith('Success'):
                    continue
                
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    try:
                        file_path = parts[0]
                        line_num = int(parts[1])
                        col_num = int(parts[2]) if parts[2].isdigit() else 0
                        
                        full_message = parts[3].strip()
                        
                        error_code = 'mypy'
                        message = full_message
                        
                        if '[' in full_message and ']' in full_message:
                            code_start = full_message.rfind('[')
                            code_end = full_message.rfind(']')
                            if code_start > 0 and code_end > code_start:
                                error_code = full_message[code_start+1:code_end]
                                message = full_message[:code_start].strip()
                        
                        issues.append(TypeIssue(
                            file=file_path,
                            line=line_num,
                            column=col_num,
                            severity='error',
                            code=error_code,
                            message=message
                        ))
                    except (ValueError, IndexError) as e:
                        continue
            
            print(f"  ✓ mypy 检测到 {len(issues)} 个问题")
            self.issues = issues
            return issues
            
        except ImportError:
            print("  ⚠ mypy 未安装")
            print("    安装命令: pip install mypy")
            return []
        except Exception as e:
            print(f"  ✗ mypy 检查失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_report(self, output_file: Optional[str] = None):
        print("=" * 80)
        print(f"mypy 检测到 {len(self.issues)} 个问题")
        print("=" * 80)
        
        for issue in self.issues:
            print(f"{issue.file}:{issue.line}:{issue.column}: {issue.message}  [{issue.code}]")
            print("=" * 80)
        
        if output_file:
            output_path = Path(output_file)
            
            report_data = {
                "raw_output": self.raw_output,
                "raw_stderr": self.raw_stderr,
                "parsed_issues": [asdict(issue) for issue in self.issues],
                "summary": {
                    "total_issues": len(self.issues),
                    "files_with_issues": len(set(issue.file for issue in self.issues))
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 完整报告已保存到: {output_path}")
            
            raw_txt_path = output_path.with_suffix('.txt')
            with open(raw_txt_path, 'w', encoding='utf-8') as f:
                f.write(self.raw_output)
                if self.raw_stderr:
                    f.write("\n\n=== stderr ===\n")
                    f.write(self.raw_stderr)
            print(f"💾 原始输出已保存到: {raw_txt_path}")


def main():
    if len(sys.argv) < 2:
        print("用法: python type_checker.py <目标目录> [输出JSON文件]")
        print("\n示例:")
        print("  python type_checker.py /path/to/python/code")
        print("  python type_checker.py /path/to/python/code report.json")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    checker = MypyTypeChecker(target_dir)
    checker.check_types()
    checker.generate_report(output_file)


if __name__ == '__main__':
    main()