from dataclasses import dataclass, field
from src.actions.action import Action, JsonDict
from typing import Any, Literal

OperationType = Literal["add", "subtract", "multiply", "divide"]

@dataclass
class Calculator(Action):
    name: str = "calculator"
    config: JsonDict = field(default_factory=lambda: {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic mathematical operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The mathematical operation to perform"
                    },
                    "x": {
                        "type": "number",
                        "description": "First number"
                    },
                    "y": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "x", "y"]
            }
        }
    })

    def execute_function(self, operation: OperationType, x: float, y: float) -> float:
        """
        Perform basic mathematical operations.
        
        Args:
            operation: Type of operation to perform
            x: First number
            y: Second number
            
        Returns:
            Result of the operation
            
        Raises:
            ValueError: If operation is invalid or division by zero
        """
        match operation:
            case "add":
                return x + y
            case "subtract":
                return x - y
            case "multiply":
                return x * y
            case "divide":
                if y == 0:
                    raise ValueError("Cannot divide by zero")
                return x / y
            case _:
                raise ValueError(f"Unknown operation: {operation}") 