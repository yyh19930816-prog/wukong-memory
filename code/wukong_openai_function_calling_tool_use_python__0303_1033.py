#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习来源: JohannLai/openai-function-calling-tools GitHub仓库
日期: 2023-11-20
功能描述: OpenAI函数调用工具集的Python实现，包含计算器、时钟等基本工具
"""

import math
from datetime import datetime
from typing import Any, Dict, Optional

class OpenAITools:
    """OpenAI函数调用工具集的核心类"""
    
    def __init__(self):
        """初始化各类工具"""
        self.tools = {
            "calculator": self.calculator,
            "clock": self.clock,
            "reverse_geocode": self.reverse_geocode,
        }
        
    def run_tool(self, tool_name: str, input_data: Any) -> Optional[Dict[str, Any]]:
        """
        运行指定的工具
        
        Args:
            tool_name: 工具名称
            input_data: 工具的输入数据
            
        Returns:
            字典形式的工具返回结果，包含工具名称和执行结果
        """
        if tool_name not in self.tools:
            return None
            
        try:
            result = self.tools[tool_name](input_data)
            return {
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "error": str(e)
            }
    
    def calculator(self, expression: str) -> float:
        """
        计算器工具，执行数学表达式计算
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果
            
        Examples:
            >>> calculator("3 + 4 * 2")
            11.0
        """
        # 安全计算，避免执行任意代码
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters")
            
        # 使用eval计算表达式，已做初步安全过滤
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return float(result)
    
    def clock(self, _: Any = None) -> str:
        """
        时钟工具，返回当前时间
        
        Args:
            _: 忽略的参数
            
        Returns:
            格式化的当前时间字符串
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def reverse_geocode(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """
        反向地理编码工具（模拟实现）
        
        Args:
            coordinates: 包含纬度和经度的字典
            
        Returns:
            模拟的地理编码信息
        """
        # 在实际应用中应该调用真实的地理编码API
        lat = coordinates.get("latitude", 0)
        lng = coordinates.get("longitude", 0)
        
        return {
            "address": f"模拟地址 {lat:.4f}, {lng:.4f}",
            "city": "模拟城市",
            "country": "模拟国家"
        }


if __name__ == "__main__":
    # 示例用法
    tools = OpenAITools()
    
    # 使用计算器
    calc_result = tools.run_tool("calculator", "3 + 4 * 2")
    print(f"计算器结果: {calc_result}")
    
    # 使用时钟
    time_result = tools.run_tool("clock", None)
    print(f"当前时间: {time_result}")
    
    # 使用反向地理编码（模拟）
    geo_result = tools.run_tool("reverse_geocode", {"latitude": 40.7128, "longitude": -74.0060})
    print(f"地理位置: