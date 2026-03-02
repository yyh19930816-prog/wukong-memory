"""
Multi-AI Agent System with crewAI
Source: GitHub repo akj2018/Multi-AI-Agent-Systems-with-crewAI
Date: 2023-11-20
Description: Demonstrates a multi-agent system where agents collaborate to research,
analyze and summarize company information autonomously.
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

# Set OpenAI API key (replace with your actual key)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def setup_crew_agents():
    """
    Creates and configures AI agents with specialized roles
    Returns configured Crew instance ready to run tasks
    """
    # Initialize language model (using OpenAI GPT-4)
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # Create Research Agent specialized in gathering company information
    researcher = Agent(
        role="Company Research Analyst",
        goal="Conduct thorough research on target companies",
        backstory="An expert analyst who scours multiple sources for detailed company information",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Create Analysis Agent specialized in comparing and scoring companies
    analyst = Agent(
        role="Business Intelligence Analyst",
        goal="Analyze and score companies based on research data",
        backstory="A data-driven analyst with expertise in business metrics and scoring models",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Create Reporter Agent specialized in summarizing findings
    reporter = Agent(
        role="Business Reporter",
        goal="Compile research findings into clear, executive summaries",
        backstory="A concise communicator who transforms complex data into actionable insights",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Define tasks for each agent
    research_task = Task(
        description="Research latest information about company XYZ including financials, competitors and market position",
        agent=researcher,
        expected_output="Detailed report with key facts about the company"
    )

    analysis_task = Task(
        description="Analyze company XYZ against industry benchmarks and score its performance",
        agent=analyst,
        expected_output="Scoring report showing company strengths/weaknesses vs competitors",
        context=[research_task]
    )

    summary_task = Task(
        description="Prepare an executive summary highlighting key insights about company XYZ",
        agent=reporter,
        expected_output="Concise 1-page summary suitable for executive review",
        context=[analysis_task]
    )

    # Form the crew with all agents
    crew = Crew(
        agents=[researcher, analyst, reporter],
        tasks=[research_task, analysis_task, summary_task],
        verbose=2  # Show detailed execution logs
    )

    return crew

def run_multi_agent_system():
    """
    Executes the multi-agent workflow:
    1. Research -> 2. Analyze -> 3. Summarize
    Prints final summary output
    """
    print("Setting up AI agent crew...")
    crew = setup_crew_agents()
    
    print("Executing multi-agent workflow...")
    result = crew.kickoff()
    
    print("\nFinal Executive Summary:")
    print(result)

if __name__ == "__main__":
    run_multi_agent_system()