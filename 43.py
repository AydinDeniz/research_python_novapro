import sympy as sp
import re

def evaluate_expression(expression, variables=None):
    if variables is None:
        variables = {}
    
    # Define allowed symbols
    allowed_symbols = set(dir(sp)) | set(dir(sp.functions)) | set(dir(sp.abc))
    
    # Extract symbols from the expression
    symbols_in_expression = set(re.findall(r'\b\w+\b', expression))
    
    # Check for disallowed symbols
    if not symbols_in_expression.issubset(allowed_symbols):
        raise ValueError("Expression contains disallowed symbols")
    
    # Create SymPy expression
    expr = sp.sympify(expression)
    
    # Substitute variables
    for var, value in variables.items():
        expr = expr.subs(var, value)
    
    return expr.evalf()

def define_function(func_name, expression):
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', func_name):
        raise ValueError("Invalid function name")
    
    globals()[func_name] = lambda x: evaluate_expression(expression, {'x': x})

def main():
    while True:
        user_input = input("Enter expression or 'define' to define a function (or 'quit' to exit): ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower().startswith('define'):
            parts = user_input.split(maxsplit=2)
            if len(parts) != 3:
                print("Invalid define syntax. Use 'define <func_name> <expression>'")
                continue
            func_name, expression = parts[1], parts[2]
            try:
                define_function(func_name, expression)
                print(f"Function {func_name} defined successfully")
            except ValueError as e:
                print(f"Error defining function: {e}")
        else:
            try:
                result = evaluate_expression(user_input)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error evaluating expression: {e}")

if __name__ == "__main__":
    main()