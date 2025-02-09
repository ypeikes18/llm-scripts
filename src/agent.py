from typing import Any, TypeAlias
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
import os
from dotenv import load_dotenv
from src.actions.action import Action
from src.config.prompts import DEFAULT_SYSTEM_PROMPT
from src.actions.subtask_executor import SubtaskExecutor
from src.vector_store import VectorStore

load_dotenv()

Message: TypeAlias = dict[str, str]
ToolResult: TypeAlias = dict[str, Any]
AgentResponse: TypeAlias = dict[str, str | list[ToolResult] | int | None]
ToolCall: TypeAlias = Any

class Agent:
    def __init__(self, actions: list[Action]=[]) -> None:
        """Initialize the agent with tools."""
        self.client = OpenAI()
        self.action_map: dict[str, Action] = {action.name: action for action in actions}
        self.vector_store = VectorStore()
        self.add_context()

    def add_context(self):
        for action in self.action_map.values():
            action.add_context(self)
            
    def _execute_tool(self, 
                     tool_call: Any, 
                     depth: int = 0, 
                     max_depth: int = 5) -> Any:
        """
        Execute a tool with depth tracking.
        
        Args:
            tool_call: The tool call from OpenAI
            depth: Current recursion depth
            max_depth: Maximum allowed recursion depth
            
        Returns:
            Tool execution result
            
        Raises:
            KeyError: If tool not found
            Exception: If tool execution fails
        """
        try:
            tool = self.action_map[tool_call.function.name]
            return tool(tool_call.function.arguments, depth=depth, max_depth=max_depth)
        except Exception as e:
            return {"error": str(e)}
       
    def execute_task(self, 
             message: str, 
             system_prompt: str | None = None,
             temperature: float = 0.7,
             model: str = "o3-mini",
             max_depth: int = 5,
             current_depth: int = 0) -> AgentResponse:
        """
        Execute a message with the agent.
        
        Args:
            message: The user's message
            system_prompt: Optional system prompt to override default
            temperature: Temperature for response generation
            model: The model to use for chat completion
            max_depth: Maximum allowed tool recursion depth
            current_depth: Current recursion depth
            
        Returns:
            Dictionary containing response, tool calls, and depth info
        """
        if current_depth >= max_depth:
            return {
                "response": "Error: Maximum recursion depth exceeded",
                "tool_calls": None,
                "error": "max_depth_exceeded"
            }
            
        if system_prompt is None:
            system_prompt = DEFAULT_SYSTEM_PROMPT
            
        messages: list[Message] = [
            # {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # First call to get tool selection
        response: ChatCompletion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[tool.config for tool in self.action_map.values()],
            tool_choice="auto",
            # temperature=temperature
        )

        message_obj: ChatCompletionMessage = response.choices[0].message
        
        # Base caseIf no tool calls, return direct response
        if not hasattr(message_obj, 'tool_calls') or not message_obj.tool_calls:
            return {"response": message_obj.content, "tool_calls": None}
        tool_results: list[ToolResult] = self._handle_tool_calls(message_obj.tool_calls, current_depth, max_depth)
        # Get final response with tool results
        messages.extend([
            {"role": "assistant", "content": message_obj.content if message_obj.content else ""},
            # {"role": "function", "content": str(tool_results), "name": "function_results"}
        ])
        
        final_response: ChatCompletion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            # temperature=temperature
        )
        
        return {
            "response": final_response.choices[0].message.content,
            "tool_calls": tool_results,
            "depth": current_depth
        }
    
    def _handle_tool_calls(self, tool_calls: list[ToolCall], current_depth: int, max_depth: int) -> list[ToolResult]:
        tool_results: list[ToolResult] = []
        for tool_call in tool_calls:
            try:
                result = self._execute_tool(
                    tool_call, 
                    depth=current_depth,
                    max_depth=max_depth
                )
                tool_results.append({
                    "function": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                    "result": result
                })
            except Exception as e:
                tool_results.append({
                    "function": tool_call.function.name,
                    "error": str(e)
                })
