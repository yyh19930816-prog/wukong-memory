#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习来源: akj2018/Multi-AI-Agent-Systems-with-crewAI
日期: 2023-11-15
功能描述: 使用crewAI框架实现多AI代理系统，包含研究代理和写作代理协作完成任务
"""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os

# 设置OpenAI API密钥
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def setup_research_agent():
    """设置研究代理"""
    return Agent(
        role='资深研究员',
        goal='进行深入的行业和市场研究',
        backstory="""你是一位经验丰富的研究员，擅长收集和分析复杂数据，
                     并能从多个角度看待问题。""",
        verbose=True,
        llm=ChatOpenAI(temperature=0.7, model="gpt-4"),
        allow_delegation=False
    )

def setup_writer_agent():
    """设置写作代理"""
    return Agent(
        role='专业科技作家',
        goal='基于研究材料撰写清晰、准确的技术文档',
        backstory="""你是一位获奖科技作家，擅长将复杂的技术信息转化为
                     易于理解的叙述性内容。""",
        verbose=True,
        llm=ChatOpenAI(temperature=0.7, model="gpt-4"),
        allow_delegation=True
    )

def create_research_task(agent):
    """创建研究任务"""
    return Task(
        description="""调查2023年人工智能在医疗保健领域的最新趋势和应用。
                       重点关注诊断、患者护理和药物发现方面的创新。""",
        agent=agent,
        expected_output="包含关键发现、统计数据和具体用例的详细研究报告。"
    )

def create_writing_task(agent, research_task):
    """创建写作任务"""
    return Task(
        description="""使用研究团队的发现撰写一篇8段的博客文章，
                       主题是AI如何改变医疗保健行业。""",
        agent=agent,
        expected_output="一篇结构合理、引人入胜的8段博客文章，附带3个关键要点。",
        context=[research_task]
    )

def main():
    """主函数：设置代理、任务并运行工作流"""
    # 初始化代理
    researcher = setup_research_agent()
    writer = setup_writer_agent()

    # 创建任务
    research_task = create_research_task(researcher)
    writing_task = create_writing_task(writer, research_task)

    # 组建团队并定义流程
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=2,
        process=Process.sequential  # 顺序执行任务
    )

    # 执行工作流
    result = crew.kickoff()

    # 输出结果
    print("\n\n########################")
    print("## 最终内容输出 ##")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    main()