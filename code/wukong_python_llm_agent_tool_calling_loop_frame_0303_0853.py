#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio SDK Python Demo Script
学习来源: GitHub ComposioHQ/composio (https://github.com/ComposioHQ/composio)
日期: 2023-11-15
功能: 演示如何使用Composio Python SDK集成HACKERNEWS工具包创建AI助手
      查询HackerNews最新帖子信息
"""

import asyncio
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
from agents import Agent, Runner

async def main():
    """
    主函数，演示Composio SDK与OpenAI Agents的集成用法
    """
    try:
        # 初始化Composio客户端，使用OpenAI Agents提供者
        # 注意: 实际使用时需要设置api_key参数
        composio = Composio(provider=OpenAIAgentsProvider())
        
        # 设置用户ID(可以是任意标识符)
        user_id = "demo_user@example.com"
        
        print("[INFO] 从Composio获取HACKERNEWS工具集...")
        # 获取HACKERNEWS工具集的函数调用工具
        tools = composio.tools.get(user_id=user_id, toolkits=["HACKERNEWS"])
        
        print("[INFO] 创建AI助手代理...")
        # 创建代理实例
        agent = Agent(
            name="HackerNews查询助手",
            instructions="""
            你是一个专业的HackerNews助手，能够获取最新的HackerNews帖子信息。
            当用户询问最新或热门的HN帖子时，你需要使用提供的工具查询数据。
            """,
            tools=tools,
        )
        
        print("[INFO] 执行查询任务...")
        # 创建运行器并执行查询任务
        runner = Runner(agent=agent)
        task = "获取HackerNews上最新的帖子标题和链接"
        result = await runner.run(task)
        
        # 打印最终结果
        print("\n[RESULT] 查询结果:")
        print(result.finalOutput)
        
    except Exception as e:
        print(f"[ERROR] 执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    # 运行主异步函数
    asyncio.run(main())