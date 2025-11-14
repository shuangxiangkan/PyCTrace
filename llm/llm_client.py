import os
import anthropic
from dotenv import load_dotenv


class ClaudeClient:
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API Key not found. Please set ANTHROPIC_API_KEY or CLAUDE_API_KEY "
                "in .env file or environment variables."
            )
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, max_tokens: int = 8192, temperature: float = 0) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            return response_text
            
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")
    
    def generate_with_system(self, system_prompt: str, user_prompt: str, 
                            max_tokens: int = 8192, temperature: float = 0) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            return response_text
            
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")