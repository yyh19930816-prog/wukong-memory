#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Learning Source: GitHub repository akj2018/Multi-AI-Agent-Systems-with-crewAI
Date: 2023-11-20
Description: Implementation of multi-AI agent system using crewAI framework.
             This script demonstrates how multiple specialized agents collaborate 
             to perform a research and writing task.
"""

from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process
import os

# Set your OpenAI API key (replace with your actual key)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def create_research_agent():
    """Create a research agent specialized in gathering information"""
    return Agent(
        role='Senior Research Analyst',
        goal='Conduct thorough research on given topics',
        backstory="""You're an expert researcher known for comprehensive analysis
                  and attention to detail.""",
        verbose=True,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.7)
    )

def create_writing_agent():
    """Create a writing agent specialized in content creation"""
    return Agent(
        role='Technical Writer',
        goal='Create well-written and structured content',
        backstory="""You're a professional writer specializing in transforming complex
                  information into clear, engaging content.""",
        verbose=True,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.7)
    )

def create_review_agent():
    """Create a review agent specialized in quality control"""
    return Agent(
        role='Quality Assurance Specialist',
        goal='Ensure accuracy and quality of final output',
        backstory="""You're a meticulous editor with expertise in fact-checking
                  and improving content quality.""",
        verbose=True,
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.7)
    )

def main():
    """Main workflow demonstrating multi-agent collaboration"""
    
    # Create agents with specialized roles
    researcher = create_research_agent()
    writer = create_writing_agent()
    reviewer = create_review_agent()
    
    # Define tasks with dependencies
    research_task = Task(
        description="""Research the latest advancements in AI agent technology
                    and multi-agent systems""",
        expected_output="Comprehensive research notes with key findings",
        agent=researcher
    )
    
    writing_task = Task(
        description="""Write a detailed report summarizing the research findings
                    in clear, professional language""",
        expected_output="Well-structured report (~1000 words) with references",
        agent=writer,
        context=[research_task]  # Depends on research_task completion
    )
    
    review_task = Task(
        description="""Review the report for accuracy, clarity, and coherence.
                    Suggest improvements.""",
        expected_output="Improved report with corrections and suggestions",
        agent=reviewer,
        context=[writing_task]  # Depends on writing_task completion
    )
    
    # Assemble crew and execute workflow
    crew = Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        verbose=2,
        process=Process.sequential  # Tasks execute in sequence
    )
    
    # Execute the workflow with research topic
    topic = "Multi-Agent AI Systems"
    print(f"\nStarting crewAI workflow for: {topic}")
    result = crew.kickoff(inputs={'topic': topic})
    
    # Print final result
    print("\n=== FINAL REPORT ===")
    print(result)

if __name__ == '__main__':
    main()