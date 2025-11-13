import os
import anthropic
from dotenv import load_dotenv

def analyze_code_with_claude(code_to_analyze: str):
    """
    Analyzes the given code using the Claude API.

    Args:
        code_to_analyze: The code string to be analyzed.

    Returns:
        The analysis result from Claude.
    """
    load_dotenv()
    api_key = os.getenv("CLAUDE_API_KEY")

    if not api_key:
        raise ValueError("CLAUDE_API_KEY not found in .env file or environment variables.")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"Please analyze the following code and provide a summary of its functionality, potential bugs, and suggestions for improvement.\n\nCode:\n```python\n{code_to_analyze}\n```"
                }
            ]
        )
        return message.content
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example usage:
    # You can replace this with code to read a file from command line arguments
    sample_code = """
def hello_world():
    print("Hello, world!")
    """

    analysis_result = analyze_code_with_claude(sample_code)
    print(analysis_result)
