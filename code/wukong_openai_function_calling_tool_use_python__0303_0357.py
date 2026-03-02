#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning from: JohannLai/openai-function-calling-tools (https://github.com/JohannLai/openai-function-calling-tools)
Date: April 2024
Description: Python implementation of OpenAI function calling tools including:
- Calculator: Basic arithmetic operations
- Clock: Get current time
- WebBrowser: Fetch webpage content
- FileReader: Read file content
"""

import json
import time
import datetime
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolResult:
    """Dataclass to standardize tool output"""
    success: bool
    result: Any
    error: Optional[str] = None

class Calculator:
    """Basic arithmetic calculator tool"""
    
    @staticmethod
    def execute(expression: str) -> ToolResult:
        """Evaluate math expression"""
        try:
            # Security note: eval is dangerous but we limit scope
            allowed_operators = {'+', '-', '*', '/', '(', ')', '.'}
            if not all(c.isdigit() or c.isspace() or c in allowed_operators 
                      for c in expression):
                raise ValueError("Invalid characters in expression")
                
            result = eval(expression.strip(), {'__builtins__': None}, {})
            return ToolResult(success=True, result=result)
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))

class Clock:
    """Clock tool to get current time"""
    
    @staticmethod
    def execute(timezone: str = "UTC") -> ToolResult:
        """Get current time"""
        try:
            # Simple timezone handling (would use pytz in production)
            if timezone.upper() != "UTC":
                raise ValueError("Only UTC timezone supported")
                
            current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            return ToolResult(success=True, result=f"Current time is {current_time}")
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))

class WebBrowser:
    """Simple web browser tool"""
    
    @staticmethod
    def execute(url: str) -> ToolResult:
        """Fetch webpage content"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return ToolResult(
                success=True,
                result={
                    'status_code': response.status_code,
                    'content': response.text[:500] + "..."  # Truncate long content
                }
            )
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))

class FileReader:
    """File system reader tool"""
    
    @staticmethod
    def execute(file_path: str) -> ToolResult:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return ToolResult(success=True, result=content)
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))

def run_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool by name with parameters"""
    tools = {
        'calculator': Calculator(),
        'clock': Clock(),
        'web_browser': WebBrowser(),
        'file_reader': FileReader(),
    }
    
    if tool_name not in tools:
        return {
            'success': False,
            'error': f"Tool {tool_name} not found"
        }
    
    tool = tools[tool_name]
    result = tool