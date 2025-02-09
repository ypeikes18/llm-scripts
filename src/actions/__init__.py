from typing import Dict, Any, Callable, Type
import importlib
import os
import pkgutil
from inspect import isclass

def load_tools() -> Dict[str, tuple[Dict[str, Any], Callable]]:
    """
    Dynamically load all tools from the tools directory.
    Returns a dictionary mapping tool names to their (config, function) pairs.
    """
    tools = {}
    
    # Get the directory of this file
    package_dir = os.path.dirname(__file__)
    
    # Iterate through all Python files in the tools directory
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name == "__init__":
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f"tools.{module_name}")
            
            # Look for a class that has tool_config and execute_function
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isclass(item) and 
                    hasattr(item, 'tool_config') and 
                    hasattr(item, 'execute_function')):
                    # Create an instance of the tool
                    tool_instance = item()
                    function_name = tool_instance.tool_config["function"]["name"]
                    tools[function_name] = (
                        tool_instance.tool_config,
                        tool_instance.execute_function
                    )
                    
        except Exception as e:
            print(f"Error loading tool {module_name}: {str(e)}")
            
    return tools 