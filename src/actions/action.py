from typing import Any, TypeVar, Self
from typing_extensions import TypeAlias
import json
from abc import ABC, abstractmethod

JsonDict: TypeAlias = dict[str, Any]

class Action:
    """Base class for all tools."""
    
    name: str  # Tool name
    config: JsonDict  # Tool configuration
    
    def __call__(self, args_str: str | JsonDict, depth: int = 0, max_depth: int = 5) -> Any:
        """
        Call the tool with string arguments.
        
        Args:
            args_str: JSON string or dict of arguments
            depth: Current recursion depth
            max_depth: Maximum allowed recursion depth
            
        Returns:
            Tool execution result
            
        Raises:
            RecursionError: If max depth is exceeded
            ValueError: If arguments are invalid
            RuntimeError: If tool execution fails
        """
        if depth >= max_depth:
            raise RecursionError(f"Maximum tool recursion depth ({max_depth}) exceeded")
            
        try:
            # Safely parse JSON arguments
            if isinstance(args_str, str):
                args = json.loads(args_str)
            else:
                args = args_str
                
            # Validate required parameters
            required_params = self.config["function"]["parameters"].get("required", [])
            for param in required_params:
                if param not in args:
                    raise ValueError(f"Missing required parameter: {param}")
            
            # Execute the tool with parsed arguments
            return self.execute_function(**args)
            
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON arguments: {args_str}")
        except Exception as e:
            raise RuntimeError(f"Tool execution failed: {str(e)}") from e
    
    def execute_function(self, **kwargs) -> Any:
        """Execute the tool's main functionality."""
        pass

    def add_context(self, agent):
        pass