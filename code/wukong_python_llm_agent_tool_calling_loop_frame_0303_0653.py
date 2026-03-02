#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio Python SDK 示例脚本
学习来源: https://github.com/ComposioHQ/composio
日期: 2024-03-20
功能: 
    - 演示如何使用Composio SDK连接HackerNews API
    - 创建并运行一个OpenAI代理，获取最新的HackerNews帖子
    - 展示基本错误处理和日志记录
"""

import asyncio
import logging
from agents import Agent, Runner
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def get_latest_hackernews_post():
    """
    获取最新的HackerNews帖子
    
    返回:
        dict: 包含最新HackerNews帖子信息的字典
        
    异常:
        Exception: 如果API调用失败会抛出异常
    """
    try:
        # 初始化Composio客户端并使用OpenAI代理提供者
        composio = Composio(provider=OpenAIAgentsProvider())
        logger.info("Composio客户端初始化成功")
        
        # 设置用户身份标识(虽然是示例但模拟真实场景)
        user_id = "demo_user@example.com"
        
        # 从HACKERNEWS工具包获取可用工具
        tools = composio.tools.get(user_id=user_id, toolkits=["HACKERNEWS"])
        logger.info(f"获取到{len(tools)}个HackerNews工具")
        
        # 创建代理实例
        agent = Agent(
            name="HackerNews Fetch Agent",
            instructions="""
            你是一个专业的HackerNews助手。
            你的任务是获取最新帖子的标题、URL和分数。
            确保返回清晰简明的信息。
            """,
            tools=tools,
        )
        logger.info("代理创建成功")
        
        # 运行代理查询最新帖子
        runner = Runner(agent=agent)
        result = await runner.run("获取最新的HackerNews帖子")
        logger.info("成功获取HackerNews数据")
        
        return result.finalOutput
    
    except Exception as e:
        logger.error(f"获取HackerNews数据失败: {str(e)}")
        raise

async def main():
    """主函数执行示例查询"""
    try:
        # 获取最新HackerNews帖子
        hn_post = await get_latest_hackernews_post()
        
        # 打印结果
        print("\n最新HackerNews帖子:")
        print(f"标题: {hn_post.get('title', '无标题')}")
        print(f"URL: {hn_post.get('url', '无URL')}")
        print(f"分数: {hn_post.get('score', '无分数')}")
        
    except Exception as e:
        print(f"执行过程中出错: {e}")

# 执行主函数
if __name__ == "__main__":
    asyncio.run(main())