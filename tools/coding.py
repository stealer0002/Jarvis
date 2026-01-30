"""
Coding tools - Python REPL and code execution
WARNING: This executes arbitrary code. Use with caution.
"""

import sys
import io
from core.tools import tool


@tool(
    name="python_repl",
    description="Executa código Python e retorna o resultado. Útil para cálculos complexos, manipulação de dados, ou scripts rápidos. ATENÇÃO: Use com responsabilidade.",
    parameters={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Código Python a ser executado"
            }
        },
        "required": ["code"]
    }
)
def python_repl(code: str) -> dict:
    """Execute Python code and return the result."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_buffer = io.StringIO()
    sys.stderr = stderr_buffer = io.StringIO()
    
    result = None
    error = None
    
    try:
        # Create a safe globals dict with common modules
        safe_globals = {
            '__builtins__': __builtins__,
            'math': __import__('math'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            're': __import__('re'),
            'os': __import__('os'),
            'random': __import__('random'),
        }
        
        # Try to evaluate as expression first (for simple calculations)
        try:
            result = eval(code, safe_globals)
        except SyntaxError:
            # If not an expression, execute as statements
            exec(code, safe_globals)
            result = None
        
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()
        
        return {
            "success": True,
            "result": str(result) if result is not None else None,
            "stdout": stdout_output if stdout_output else None,
            "stderr": stderr_output if stderr_output else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "stdout": stdout_buffer.getvalue() if stdout_buffer.getvalue() else None
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@tool(
    name="evaluate_expression",
    description="Avalia uma expressão matemática ou lógica simples. Mais seguro que python_repl para cálculos.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expressão a avaliar (ex: '2 + 2', 'math.sqrt(16)', '10 * 5 / 2')"
            }
        },
        "required": ["expression"]
    }
)
def evaluate_expression(expression: str) -> dict:
    """Safely evaluate a mathematical expression."""
    try:
        import math
        
        # Allowed names for safe evaluation
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'len': len, 'pow': pow, 'int': int, 'float': float,
            'math': math, 'pi': math.pi, 'e': math.e,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10, 'exp': math.exp,
            'ceil': math.ceil, 'floor': math.floor,
            'True': True, 'False': False, 'None': None,
        }
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return {
            "success": True,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
