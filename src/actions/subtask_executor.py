from typing import Callable, Any
from dataclasses import dataclass, field
from src.actions.action import Action

@dataclass
class SubtaskExecutor(Action):
    name: str = "subtask_executor"
    execute_function: Callable[..., Any] = None
    is_self_referential: bool = True
    
    config: dict = field(default_factory=lambda: {
        "type": "function",
        "function": {
            "name": SubtaskExecutor.name,
            "description": "Execute a subtask with customizable parameters like system prompt and temperature",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to process"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Optional system prompt to override default",
                        "optional": True
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for response generation",
                        "default": 0.7
                    },
                    "model": {
                        "type": "string",
                        "description": "The model to use for chat completion",
                        "default": "gpt-4-1106-preview"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "The maximum depth of tool calls to make",
                        "default": 5 # TODO: make this enforceable
                    }
                },
                "required": ["message"]
            }
        }
    })

    def add_context(self, agent):
        self.execute_function = agent.execute_task

    def execute_function(self, task_id: str, parameters: dict) -> Any:
        """
        Execute the specified subtask with given parameters.
        This method should be implemented by specific subtask executors.
        """
        if self.execute_function is None:
            raise NotImplementedError("Execute function must be implemented by subtask executor")