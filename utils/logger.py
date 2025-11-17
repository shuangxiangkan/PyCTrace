import sys

class Logger:
    def info(self, message: str):
        print(f"ℹ️  [INFO] {message}")
    
    def success(self, message: str):
        print(f"✅ [SUCCESS] {message}")
    
    def warning(self, message: str):
        print(f"⚠️  [WARNING] {message}")
    
    def error(self, message: str):
        print(f"❌ [ERROR] {message}", file=sys.stderr)


logger = Logger()