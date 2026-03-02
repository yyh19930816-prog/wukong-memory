# Composio Python SDK示例脚本
# 学习来源: ComposioHQ/composio GitHub仓库 (https://github.com/ComposioHQ/composio)
# 创建日期: 2023-12-15
# 功能描述: 演示如何使用Composio Python SDK与OpenAI Agents集成，访问HackerNews API获取数据

import asyncio
from agents import Agent, Runner
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider


async def hackernews_agent_example():
    """
    演示使用Composio SDK与HackerNews API交互的示例
    
    步骤:
    1. 初始化Composio客户端
    2. 获取HackerNews工具集
    3. 创建OpenAI Agent
    4. 运行Agent查询HackerNews最新帖子
    """
    try:
        # 1. 初始化Composio客户端，使用OpenAI Agents提供者
        print("初始化Composio客户端...")
        composio = Composio(
            provider=OpenAIAgentsProvider()
            # api_key="your-api-key",  # 如果需要认证可以取消注释
        )

        # 2. 获取HackerNews工具集
        print("获取HackerNews工具集...")
        user_id = "user@acme.org"
        tools = await composio.tools.get(
            user_id=user_id,
            toolkits=["HACKERNEWS"]  # 指定需要的工具包
        )

        # 3. 创建OpenAI Agent实例
        print("创建OpenAI Agent...")
        agent = Agent(
            name="HackerNews助手",
            instructions="你是一个帮助获取HackerNews信息的助手。",
            tools=tools,
        )

        # 4. 运行Agent查询HackerNews
        print("运行Agent查询HackerNews...")
        question = "获取HackerNews上最新热门帖子的标题和链接"
        print(f"查询问题: {question}")
        
        runner = Runner(agent)
        result = await runner.run(question)
        
        # 输出结果
        print("\n查询结果:")
        print(result.final_output)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    # 运行主异步函数
    asyncio.run(hackernews_agent_example())