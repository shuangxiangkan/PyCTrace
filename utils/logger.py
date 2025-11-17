import sys

class Logger:
    def info(self, message: str):
        print(f"ℹ️  {message}")
    
    def success(self, message: str):
        print(f"✅ {message}")
    
    def warning(self, message: str):
        print(f"⚠️  {message}")
    
    def error(self, message: str):
        print(f"❌ {message}", file=sys.stderr)


logger = Logger()