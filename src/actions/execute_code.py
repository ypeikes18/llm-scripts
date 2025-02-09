from dataclasses import dataclass, field
from typing import Any, Dict
import ast
from src.actions.action import Action, JsonDict

@dataclass
class CodeExecutor(Action):
    name: str = "code_executor"
    config: JsonDict = field(default_factory=lambda: {
        "type": "function",
        "function": {
            "name": "code_executor",
            "description": "Execute Python code that must be wrapped in a main() function",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_code": {
                        "type": "string",
                        "description": """The Python code to execute. Requirements:
                        1. ALL code must be wrapped inside a main() function with no arguments - even imports
                        2. No code should exist outside the main() function
                        3. You can define other functions inside main()
                        4. main() must return the final result
                        5. Do not call main() - the executor will do that
                        
                        Example:
                        def main():
                            # Define helper functions here if needed
                            def helper():
                                return "helper result"
                                
                            # Your main logic here
                            result = helper()
                            return result  # main must return something
                        """
                    }
                },
                "required": ["function_code"]
            }
        }
    })

    def _validate_main_function(self, code: str) -> bool:
        """
        Validate that the code follows the main() function requirements.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if code structure is valid, False otherwise
        """
        try:
            tree = ast.parse(code)
            
            # Check if there's exactly one top-level function definition
            top_level_nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            if len(top_level_nodes) != 1:
                return False
                
            # Check if the function is named 'main'
            main_func = top_level_nodes[0]
            if main_func.name != 'main':
                return False
                
            # Check if main() has no arguments
            if main_func.args.args or main_func.args.vararg or main_func.args.kwarg:
                return False
                
            # Check that there are no other top-level nodes except the main function
            if len(tree.body) != 1:
                return False
                
            return True
            
        except SyntaxError:
            return False

    def _is_safe_code(self, code: str) -> bool:
        """
        Check if the code is safe to execute by analyzing the AST.
        
        Args:
            code: Python code to analyze
            
        Returns:
            True if code is safe, False otherwise
        """
        try:
            tree = ast.parse(code)
            
            # List of allowed node types
            allowed_nodes = {
                ast.FunctionDef, ast.Return, ast.Expr, ast.Call,
                ast.Name, ast.Load, ast.Store, ast.Num, ast.Str,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.BinOp,
                ast.List, ast.Dict, ast.Tuple, ast.Set,
                ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
                ast.Gt, ast.GtE, ast.If, ast.For, ast.While,
                ast.Break, ast.Continue, ast.Pass, ast.Assign,
                ast.AugAssign, ast.ListComp, ast.DictComp, ast.SetComp,
                ast.Constant  # For Python 3.8+ compatibility
            }
            
            # Check each node in the AST
            for node in ast.walk(tree):
                if type(node) not in allowed_nodes:
                    return False
                    
                # Check for potentially dangerous function calls
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                        
                    dangerous_functions = {
                        'eval', 'exec', 'compile', 'open', 'file',
                        'delete', 'remove', 'system', 'os', 'subprocess',
                        '__import__', 'globals', 'locals', 'vars'
                    }
                    
                    if func_name.lower() in dangerous_functions:
                        return False
            
            return True
            
        except SyntaxError:
            return False

    def execute_function(self, function_code: str) -> Any:
        """
        Execute Python code wrapped in a main() function.
        
        Args:
            function_code: The Python code to execute (must be wrapped in main())
            
        Returns:
            Result of the main() function execution
            
        Raises:
            ValueError: If code is unsafe, invalid structure, or execution fails
        """
        if not self._validate_main_function(function_code):
            raise ValueError(
                "Invalid code structure. Code must be wrapped in a main() function "
                "with no arguments and no code outside of it."
            )
            
        print(function_code, "\n", "---")
        try:
            # Create a scope with access to globals
            local_scope: dict[str, Any] = {}
            global_scope = globals()
            
            # Execute the function definition
            exec(function_code, global_scope, local_scope)
            
            # Execute main() function
            result = local_scope['main']()
            return result
            
        except Exception as e:
            raise ValueError(f"Error executing function: {str(e)}")
