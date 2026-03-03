#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: crewai_agent_demo.py
Description: Multi-AI Agent System Demo using crewAI framework
Features: Creates team of specialized AI agents to perform complex tasks (research + writing)
Requirements: crewai>=0.28.8, langchain-community, python-dotenv
Author: inspired by akj2018/Multi-AI-Agent-Systems-with-crewAI (GitHub)
Date: 2024-02-15
"""

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables (API keys)
load_dotenv()

def setup_research_agent():
    """Create a research-focused AI agent"""
    return Agent(
        role='Senior Research Analyst',
        goal='Find and analyze the latest trends in AI',
        backstory="""An expert analyst with 10+ years experience in technology market research.
        Skilled at finding reliable sources and extracting key insights.""",
        verbose=True,
        allow_delegation=False,
        llm=OpenAI(temperature=0.3)  # Lower temp for factual accuracy
    )

def setup_writer_agent():
    """Create a content writing AI agent"""
    return Agent(
        role='Technical Content Writer',
        goal='Write engaging technical content',
        backstory="""Former tech journalist turned content specialist.
        Excels at explaining complex topics in simple terms.""",
        verbose=True,
        allow_delegation=True,
        llm=OpenAI(temperature=0.7)  # Higher temp for creativity
    )

def create_research_task(agent):
    """Task for researching AI trends"""
    return Task(
        description="""Research the latest trends in AI for 2024.
        Focus on major breakthroughs, popular frameworks, and real-world applications.
        Gather data from reliable sources.""",
        agent=agent,
        expected_output="""A comprehensive report with:
        1. Key AI trends for 2024
        2. Emerging technologies
        3. Practical applications
        4. Sources/References""",
    )

def create_writing_task(agent, context):
    """Task for creating content based on research"""
    return Task(
        description="""Write an engaging blog post about AI trends for 2024.
        Use the research data to create insightful content for tech professionals.
        Include examples and practical applications.""",
        agent=agent,
        context=context,
        expected_output="""A well-written blog post (800-1000 words) with:
        1. Introduction to AI trends
        2. Breakdown of key technologies
        3. Practical use cases
        4. Future outlook""",
    )

def main():
    # Set up the AI team
    researcher = setup_research_agent()
    writer = setup_writer_agent()

    # Define tasks with dependencies
    research_task = create_research_task(researcher)
    writing_task = create_writing_task(writer, [research_task])

    # Assemble the crew
    ai_crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,  # Tasks run in order
        verbose=2  # Show detailed execution logs
    )

    print("🚀 Starting AI Crew Execution...")
    result = ai_crew.kickoff()
    
    print("\n📝 Final Output:\n")
    print(result)

if __name__ == "__main__":
    main()