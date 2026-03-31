import ast
import re
import subprocess
import json
import openai

# Set up OpenAI API key
openai.api_key = 'your_openai_api_key'

# Function to parse code and generate AST
def parse_code(code):
    try:
        tree = ast.parse(code)
        return tree
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return None

# Function to detect common bugs using AST
def detect_bugs(tree):
    bugs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            if not any(isinstance(handler, ast.ExceptHandler) for handler in node.handlers):
                bugs.append("Missing except block in try-except")
        if isinstance(node, ast.If):
            if not node.orelse and not node.body:
                bugs.append("If statement without else block")
    return bugs

# Function to refactor inefficient functions using GPT-4
def refactor_code(code):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Refactor the following Python code for efficiency:\n\n{code}\n\nRefactored code:",
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to suggest improvements using GPT-4
def suggest_improvements(code):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Suggest improvements for the following Python code:\n\n{code}\n\nImprovements:",
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to process a repository
def process_repository(repo_path):
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                    tree = parse_code(code)
                    if tree:
                        bugs = detect_bugs(tree)
                        if bugs:
                            print(f"Bugs detected in {file_path}:")
                            for bug in bugs:
                                print(f" - {bug}")
                        
                        refactored_code = refactor_code(code)
                        print(f"Refactored code for {file_path}:\n{refactored_code}\n")
                        
                        improvements = suggest_improvements(code)
                        print(f"Suggested improvements for {file_path}:\n{improvements}\n")

# Example usage
repo_path = "path_to_your_repository"
process_repository(repo_path)