import os
from dotenv import load_dotenv
import litellm

# 加载 .env 文件
load_dotenv()

# 自动丢弃不支持的参数（如某些模型不支持 temperature=0）
litellm.drop_params = True

# 默认模型
DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _setup_api_keys():
    """
    设置 API Keys，处理别名
    LiteLLM 需要特定的环境变量名称
    """
    # Claude: 支持 CLAUDE_API_KEY 作为 ANTHROPIC_API_KEY 的别名
    if not os.getenv("ANTHROPIC_API_KEY") and os.getenv("CLAUDE_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = os.getenv("CLAUDE_API_KEY")


# 初始化时设置 API Keys
_setup_api_keys()


class LLMClient:
    """
    统一的 LLM 客户端，使用 LiteLLM 实现
    
    支持的模型提供商：
    - Anthropic: claude-sonnet-4-20250514, claude-3-opus-20240229 等
    - OpenAI: gpt-4o, gpt-4-turbo, o1, o3 等
    - Google: gemini-pro, gemini-1.5-pro 等
    - 以及 LiteLLM 支持的其他 100+ 模型
    
    环境变量配置 (.env):
        ANTHROPIC_API_KEY=your_anthropic_key  # 或 CLAUDE_API_KEY
        OPENAI_API_KEY=your_openai_key
        GEMINI_API_KEY=your_gemini_key (可选)
    
    更多模型请参考: https://docs.litellm.ai/docs/providers
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._validate_api_key()
    
    def _validate_api_key(self):
        """验证模型对应的 API Key 是否存在"""
        model_lower = self.model.lower()
        
        if model_lower.startswith("claude"):
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError(
                    "Anthropic API Key not found. "
                    "Please set ANTHROPIC_API_KEY or CLAUDE_API_KEY in .env file."
                )
        elif model_lower.startswith(("gpt-", "o1", "o3", "o4", "chatgpt-")):
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError(
                    "OpenAI API Key not found. Please set OPENAI_API_KEY in .env file."
                )
        elif model_lower.startswith("gemini"):
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError(
                    "Gemini API Key not found. Please set GEMINI_API_KEY in .env file."
                )
    
    def generate(self, prompt: str, max_tokens: int = 8192, temperature: float = 0) -> str:
        """
        生成响应
        
        Args:
            prompt: 用户提示
            max_tokens: 最大生成 token 数
            temperature: 温度参数 (0-1)
        
        Returns:
            生成的文本响应
        """
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")
    
    def generate_with_system(self, system_prompt: str, user_prompt: str, 
                            max_tokens: int = 8192, temperature: float = 0) -> str:
        """
        带系统提示的生成
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            max_tokens: 最大生成 token 数
            temperature: 温度参数 (0-1)
        
        Returns:
            生成的文本响应
        """
        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")


def get_llm_client(model: str = None) -> LLMClient:
    """
    获取 LLM 客户端
    
    Args:
        model: 模型名称，如果为 None 则使用默认模型 (claude-sonnet-4-20250514)
    
    Returns:
        LLM 客户端实例
    
    支持的模型:
        Anthropic: claude-sonnet-4-20250514, claude-opus-4, claude-3-5-sonnet 等
        OpenAI: gpt-4o, gpt-4-turbo, o1, o3 等
        Google: gemini-pro, gemini-1.5-pro 等
        
        更多模型请参考: https://docs.litellm.ai/docs/providers
    """
    if model is None:
        model = DEFAULT_MODEL
    return LLMClient(model=model)
