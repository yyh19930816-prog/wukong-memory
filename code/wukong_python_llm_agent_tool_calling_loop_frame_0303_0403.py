#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Composio SDK Python Example

Learn from GitHub: ComposioHQ/composio
Date: 2023-11-15
Description: Demonstrates how to use Composio SDK with OpenAI Agents to fetch latest HackerNews post
"""

import asyncio
from agents import Agent, Runner
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider


async def main():
    """
    Main function to demonstrate Composio SDK usage:
    1. Initialize Composio client with OpenAI provider
    2. Fetch HACKERNEWS toolkit tools
    3. Create an agent with the tools
    4. Run the agent to get latest HackerNews post
    """
    try:
        # Initialize Composio client with OpenAI Agents Provider
        # Note: Replace "your-api-key" with actual API key if required
        composio = Composio(
            provider=OpenAIAgentsProvider(),
            # api_key="your-api-key"
        )

        # User identifier (can be any string identifying the user)
        user_id = "user@acme.org"

        # Get tools from HACKERNEWS toolkit
        print("Fetching HackerNews tools...")
        tools = await composio.tools.get(
            user_id=user_id,
            toolkits=["HACKERNEWS"]
        )

        # Create an agent with the tools
        print("Creating agent...")
        agent = Agent(
            name="HackerNews Assistant",
            instructions="""
                You are a helpful assistant specialized in fetching HackerNews information.
                When asked about HackerNews, use the provided tools to get accurate data.
            """,
            tools=tools,
        )

        # Run the agent with a query about latest HackerNews post
        print("Running agent query...")
        result = await Runner().run(
            agent=agent,
            task="What's the latest post on HackerNews?"
        )

        # Print the final output from agent execution
        print("\nAgent Result:")
        print(result.final_output)

    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())