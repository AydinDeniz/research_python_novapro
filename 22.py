import astroid
from pylint.lint import Run as pylint_run
from pylint.reporters.text import TextReporter
import io

# Function to run pylint and capture output
def run_pylint(code):
    reporter = TextReporter(io.StringIO())
    pylint_run(["--rcfile=pylintrc"], reporter=reporter, exit=False)
    output = reporter._output.getvalue()
    return output

# Function to analyze code for best practices, efficiency, and security vulnerabilities
def analyze_code(code):
    pylint_output = run_pylint(code)
    suggestions = []
    
    # Parse pylint output for suggestions
    lines = pylint_output.split("\n")
    for line in lines:
        if "C:" in line:  # Convention
            suggestions.append(line)
        elif "R:" in line:  # Refactor
            suggestions.append(line)
        elif "W:" in line:  # Warning
            suggestions.append(line)
        elif "E:" in line:  # Error
            suggestions.append(line)
        elif "F:" in line:  # Fatal
            suggestions.append(line)
    
    return suggestions

# Example usage
code = """
def example_function():
    a = 1
    b = 2
    c = a + b
    return c
"""

suggestions = analyze_code(code)
for suggestion in suggestions:
    print(suggestion)