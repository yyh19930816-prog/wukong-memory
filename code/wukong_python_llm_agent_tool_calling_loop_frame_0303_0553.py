#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
COMPOSIO SDK DEMO SCRIPT
学习来源: GitHub ComposioHQ/composio README
日期: 2023-11-28
功能: 演示如何使用Composio Python SDK与OpenAI Agents集成，获取HackerNews最新帖子信息
"""

import asyncio
from agents import Agent, Runner
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider


async def get_latest_hackernews_post():
    """
    使用Composio SDK和OpenAI Agents获取HackerNews最新帖子
    """
    try:
        # 1. 初始化Composio客户端并与OpenAI Agents集成
        composio = Composio(
            provider=OpenAIAgentsProvider(),
            # api_key="your-api-key-here"  # 如需认证可取消注释
        )
        print("✅ Composio client initialized successfully")

        # 2. 配置用户ID和所需的工具包(HACKERNEWS)
        user_id = "demo_user@example.com"
        print(f"🔧 Fetching tools for user: {user_id}")
        
        # 3. 获取HACKERNEWS工具集
        tools = composio.tools.get(
            user_id=user_id,
            toolkits=["HACKERNEWS"]
        )
        print(f"🛠️ Acquired {len(tools)} tools from HACKERNEWS toolkit")

        # 4. 创建OpenAI Agent实例
        agent = Agent(
            name="HN Assistant",
            instructions="You are a helpful assistant specialized in fetching "
                        "information from HackerNews.",
            tools=tools,
        )
        print(f"🤖 Created agent: {agent.name}")

        # 5. 运行Agent查询最新帖子
        print("🚀 Querying latest HackerNews post...")
        runner = Runner(agent)
        result = await runner.run("What is the latest hackernews post about?")
        
        # 6. 输出结果
        print("\n📢 Latest HackerNews Post:")
        print(result.finalOutput or "No result found")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(get_latest_hackernews_post())