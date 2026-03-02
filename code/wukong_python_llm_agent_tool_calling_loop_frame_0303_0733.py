#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio Python SDK Example Script
Learned from: GitHub ComposioHQ/composio (https://github.com/ComposioHQ/composio)
Date: 2023-11-15
Description: Demonstrates integration of Composio SDK with OpenAI Agents
             to fetch latest HackerNews post using composio_openai_agents.
"""

import asyncio
from agents import Agent, Runner
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
import json


async def get_latest_hackernews_post():
    """
    Example function demonstrating Composio SDK usage with OpenAI Agents.
    Creates an agent configured to fetch latest HackerNews post.
    
    Steps:
    1. Initialize Composio client with OpenAI provider
    2. Get HackerNews toolkit tools
    3. Create OpenAI agent with these tools
    4. Run agent query to get latest post
    
    Returns:
        dict: Parsed JSON response from the agent
    """
    # Initialize Composio client with OpenAI Agents Provider
    composio = Composio(provider=OpenAIAgentsProvider())

    # User identifier (can be any string)
    user_id = "user@example.com"

    # Get available tools from HACKERNEWS toolkit
    tools = composio.tools.get(user_id=user_id, toolkits=["HACKERNEWS"])

    # Create an agent instance configured with HackerNews tools
    agent = Agent(
        name="HackerNews Agent",
        instructions="You are an AI assistant specialized in fetching HackerNews data.",
        tools=tools,
    )

    # Run the agent with a query about the latest post
    runner = Runner(agent=agent)
    result = await runner.run("What is the latest HackerNews post about?")

    try:
        # Try to parse the result as JSON
        return json.loads(result.final_output)
    except json.JSONDecodeError:
        # If not JSON, return raw output
        return {"response": result.final_output}


if __name__ == "__main__":
    # Run the async function synchronously for demonstration
    response = asyncio.run(get_latest_hackernews_post())
    print("\nHackerNews API Response:")
    print(json.dumps(response, indent=2))