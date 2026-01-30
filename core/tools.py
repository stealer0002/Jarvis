"""
Tool definitions and registry for JARVIS
Each tool has a name, description, parameters, and handler function
"""

from typing import Callable, Any
from dataclasses import dataclass, field


@dataclass
class Tool:
    """Represents a tool that JARVIS can use."""
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]


class ToolRegistry:
    """Registry of all available tools for the agent."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., Any]
    ) -> None:
        """Register a new tool."""
        self._tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_ollama_format(self) -> list[dict]:
        """
        Convert all tools to Ollama's function calling format.
        
        Returns:
            List of tool definitions in Ollama format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self._tools.values()
        ]
    
    async def execute(self, name: str, arguments: dict) -> Any:
        """
        Execute a tool by name with given arguments.
        
        Args:
            name: Tool name
            arguments: Dict of arguments to pass
            
        Returns:
            Tool execution result
        """
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        
        try:
            # Handle both sync and async handlers
            result = tool.handler(**arguments)
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


# Global registry instance
registry = ToolRegistry()


def tool(name: str, description: str, parameters: dict):
    """
    Decorator to register a function as a tool.
    
    Usage:
        @tool("say_hello", "Says hello", {"type": "object", "properties": {...}})
        def say_hello(name: str):
            return f"Hello, {name}!"
    """
    def decorator(func: Callable):
        registry.register(name, description, parameters, func)
        return func
    return decorator
