"""
Calculator tool
Allows the agent to perform mathematical calculations accurately.
"""

from core.tools import tool

@tool(
    name="calculate",
    description="Realiza cálculos matemáticos precisos. Use para somas, subtrações, multiplicações, divisões, raízes, potências, etc.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expressão matemática a calcular (ex: '2 + 2', 'sqrt(144)', '3.14 * 2**2')"
            }
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression safely."""
    import math
    
    # Safe dictionary of allowed functions
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pi': math.pi,
        'e': math.e,
        'log': math.log,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor
    }
    
    try:
        # Clean expression
        expr = expression.replace('^', '**')
        
        # Evaluate
        result = eval(expr, {"__builtins__": None}, safe_dict)
        
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "message": f"O resultado de {expression} é {result}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao calcular '{expression}': {str(e)}"
        }
