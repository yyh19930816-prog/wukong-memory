"""
OpenAI Function Calling Tools - Python Implementation
Based on https://github.com/JohannLai/openai-function-calling-tools
Created: 2023-11-15
Implements core tools functionality including Calculator, Clock, and basic file operations.
"""

import json
import datetime
import math
import subprocess
from typing import Dict, Any, Optional
import openai

class Tool:
    """Base class for all tools"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parameters = {}

    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        raise NotImplementedError("Tool.execute must be implemented")

class Calculator(Tool):
    """Calculator tool that evaluates math expressions"""
    def __init__(self):
        super().__init__(
            name="Calculator",
            description="A simple calculator that can do basic arithmetic."
        )
        self.parameters = {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate"
            }
        }

    def execute(self, expression: str) -> float:
        try:
            # Safely evaluate math expressions
            allowed_names = {
                k: v for k, v in math.__dict__.items() 
                if not k.startswith("_")
            }
            return eval(expression, {"__builtins__": None}, allowed_names)
        except Exception as e:
            return f"Error: {str(e)}"

class Clock(Tool):
    """Clock tool that returns current time"""
    def __init__(self):
        super().__init__(
            name="Clock",
            description="A clock that can tell you the current time and date."
        )
        self.parameters = {}

    def execute(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class FileTool(Tool):
    """Base class for file operations"""
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.parameters = {
            "file_path": {
                "type": "string",
                "description": "Path to the file"
            }
        }

class ReadFileTool(FileTool):
    """Tool to read file contents"""
    def __init__(self):
        super().__init__(
            name="ReadFile",
            description="Reads contents from a file"
        )

    def execute(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileTool(FileTool):
    """Tool to write to file"""
    def __init__(self):
        super().__init__(
            name="WriteFile",
            description="Writes text to a file"
        )
        self.parameters["content"] = {
            "type": "string",
            "description": "Content to write to file"
        }

    def execute(self, file_path: str, content: str) -> str:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class OpenAIFunctionCaller:
    """Handles OpenAI function calling with registered tools"""
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """