"""
OpenAI Function Calling Tools Implementation in Python
学习来源: https://github.com/JohannLai/openai-function-calling-tools
日期: 2023-11-15
功能描述: 实现OpenAI函数调用工具的Python版本，包括基础工具类和时间、计算器功能。
"""

import json
import time
import math
import openai
from typing import Dict, Any, Optional, List, Callable

class Tool:
    """基础工具类，所有具体工具都应继承此类"""
    
    def __init__(self, name: str, description: str):
        """
        初始化工具
        :param name: 工具名称
        :param description: 工具描述
        """
        self.name = name
        self.description = description
        
    def get_function_schema(self) -> Dict[str, Any]:
        """
        获取工具的OpenAI函数调用schema
        :return: 字典格式的函数schema
        """
        pass
        
    def execute(self, input_data: Any) -> Any:
        """
        执行工具的功能
        :param input_data: 工具需要的输入数据
        :return: 工具执行结果
        """
        pass

class Clock(Tool):
    """时钟工具，可以返回当前时间"""
    
    def __init__(self):
        super().__init__(
            name="clock",
            description="A clock that can tell you the current time."
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    def execute(self, input_data: Dict[str, Any]) -> str:
        return f"当前时间是: {time.strftime('%Y-%m-%d %H:%M:%S')}"

class Calculator(Tool):
    """简单计算器工具，用于基本数学运算"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="A simple calculator that can do basic arithmetic."
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如: 3.14*2"
                    }
                },
                "required": ["expression"]
            }
        }
    
    def execute(self, input_data: Dict[str, Any]) -> str:
        try:
            result = eval(input_data["expression"])
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"

class OpenAIFunctionCaller:
    """OpenAI函数调用管理类"""
    
    def __init__(self, api_key: str):
        """
        初始化OpenAI客户端
        :param api_key: OpenAI API密钥
        """
        openai.api_key = api_key
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool) -> None:
        """注册一个工具"""
        self.tools[tool.name] = tool
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """获取所有已注册工具的函数schema"""
        return [tool.get_function_schema() for tool in self.tools.values()]
    
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """执行函数调用"""
        if function_name not in self.tools:
            return f"未知工具: {function_name}"
        return