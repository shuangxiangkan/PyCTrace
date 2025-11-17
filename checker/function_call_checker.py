#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from pylint.lint import Run

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import logger


@dataclass
class CallIssue:
    file: str
    line: int
    column: int
    severity: str
    code: str
    message: str
    symbol: str


class PylintCallChecker:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.issues: List[CallIssue] = []
        self.raw_output: str = ""
        
    def check_calls(self) -> List[CallIssue]:
        logger.info("使用 pylint 进行函数调用检查...")
        try:
            py_files = [str(f) for f in self.target_dir.rglob('*.py')]
            if not py_files:
                logger.warning("未找到 Python 文件")
                return []
            
            import sys
            import io
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            captured_output = io.StringIO()
            sys.stdout = captured_output
            sys.stderr = captured_output
            
            pylint_args = [
                '--disable=all',
                '--enable=E0602,E1101,E0611,E1121,E1120,E1123,E1125',
                '--output-format=text',
                '--reports=no',
                '--score=no',
            ] + py_files
            
            try:
                Run(pylint_args, exit=False)
            except SystemExit:
                pass
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            output = captured_output.getvalue()
            self.raw_output = output
            
            issues = []
            for line in output.strip().split('\n'):
                if not line or line.startswith('*'):
                    continue
                
                if ':' in line and not line.startswith(' '):
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        try:
                            file_path = parts[0].strip()
                            line_num = int(parts[1].strip())
                            col_str = parts[2].strip()
                            col_num = int(col_str) if col_str.isdigit() else 0
                            
                            message_part = parts[3].strip()
                            
                            severity = 'error'
                            code = 'pylint'
                            symbol = ''
                            message = message_part
                            
                            if ':' in message_part:
                                code_msg_parts = message_part.split(':', 1)
                                if len(code_msg_parts) == 2:
                                    code = code_msg_parts[0].strip()
                                    message = code_msg_parts[1].strip()
                            
                            if '(' in message and message.endswith(')'):
                                paren_start = message.rfind('(')
                                symbol = message[paren_start+1:-1]
                                message = message[:paren_start].strip()
                            
                            issues.append(CallIssue(
                                file=file_path,
                                line=line_num,
                                column=col_num,
                                severity=severity,
                                code=code,
                                message=message,
                                symbol=symbol
                            ))
                        except (ValueError, IndexError) as e:
                            continue
            
            logger.success(f"pylint 检测到 {len(issues)} 个函数调用问题")
            self.issues = issues
            return issues
            
        except ImportError:
            logger.warning("pylint 未安装")
            logger.info("  安装命令: pip install pylint")
            return []
        except Exception as e:
            logger.error(f"pylint 检查失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_report(self, output_file: Optional[str] = None):
        logger.info("=" * 80)
        logger.info(f"pylint 检测到 {len(self.issues)} 个函数调用问题")
        logger.info("=" * 80)
        
        for issue in self.issues:
            symbol_info = f" ({issue.symbol})" if issue.symbol else ""
            logger.info(f"{issue.file}:{issue.line}:{issue.column}: {issue.message}{symbol_info}  [{issue.code}]")
            logger.info("=" * 80)
        
        if output_file:
            output_path = Path(output_file)
            
            report_data = {
                "raw_output": self.raw_output,
                "parsed_issues": [asdict(issue) for issue in self.issues],
                "summary": {
                    "total_issues": len(self.issues),
                    "files_with_issues": len(set(issue.file for issue in self.issues))
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            logger.success(f"完整报告已保存到: {output_path}")
            
            raw_txt_path = output_path.with_suffix('.txt')
            with open(raw_txt_path, 'w', encoding='utf-8') as f:
                f.write(self.raw_output)
            logger.success(f"原始输出已保存到: {raw_txt_path}")


def main():
    if len(sys.argv) < 2:
        logger.info("用法: python function_call_checker.py <目标目录> [输出JSON文件]")
        logger.info("\n示例:")
        logger.info("  python function_call_checker.py /path/to/python/code")
        logger.info("  python function_call_checker.py /path/to/python/code report.json")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    checker = PylintCallChecker(target_dir)
    checker.check_calls()
    checker.generate_report(output_file)


if __name__ == '__main__':
    main()