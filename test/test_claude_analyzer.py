import sys
import os

# Add the llm directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'llm')))

from claude_analyzer import analyze_code_with_claude

def test_claude_analysis():
    """
    Tests the Claude code analysis functionality.
    """
    print("--- Starting Claude Analyzer Test ---")

    # A simple piece of code to be analyzed
    sample_code = """
    def add(a, b):
        return a + b

    def subtract(a, b):
        return a - b
    """

    print("\nAnalyzing the following code:\n")
    print(sample_code)

    # Call the analysis function
    analysis_result = analyze_code_with_claude(sample_code)

    print("\n--- Claude's Analysis Result ---")
    print(analysis_result)
    print("\n--- Test Finished ---")

if __name__ == "__main__":
    test_claude_analysis()