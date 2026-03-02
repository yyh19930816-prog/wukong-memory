#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习来源: akj2018/Multi-AI-Agent-Systems-with-crewAI GitHub仓库
日期: 2023-11-15
功能描述: 使用crewAI框架构建多AI代理系统，演示如何创建具有不同角色的AI代理团队协作完成任务
         示例实现了一个市场研究报告生成系统，包含研究员、写作专家和分析师三个角色
"""

from crewai import Agent, Task, Crew
from langchain.llms import Ollama  # 可以使用其他LLM后端，如OpenAI

# 1. 定义AI代理及其角色
def create_agents():
    """创建具有不同专业角色的AI代理"""
    
    # 研究员代理 - 负责数据收集和市场分析
    researcher = Agent(
        role='资深市场研究员',
        goal='收集和分析最新的市场趋势和数据',
        backstory="""你是一位经验丰富的市场研究专家，擅长通过多种渠道获取准确的市场数据，
        并能识别关键的市场趋势和机遇。""",
        verbose=True,
        llm=Ollama(model="llama2")  # 使用本地LLM模型
    )
    
    # 写作专家代理 - 负责报告撰写
    writer = Agent(
        role='技术写作专家',
        goal='根据研究数据撰写专业、易懂的市场报告',
        backstory="""你是一位技术写作专家，擅长将复杂的数据和分析结果转化为清晰、
        专业的商业报告。""",
        verbose=True,
        llm=Ollama(model="llama2")
    )
    
    # 分析师代理 - 负责提炼关键见解
    analyst = Agent(
        role='市场分析师',
        goal='从数据中提炼有价值的商业见解',
        backstory="""你是市场分析专家，擅长从各种数据中发现有价值的商业见解
        并给出可操作的建议。""",
        verbose=True,
        llm=Ollama(model="llama2")
    )
    
    return researcher, writer, analyst

# 2. 定义任务及工作流程
def create_tasks(researcher, writer, analyst):
    """为每个代理创建具体任务并定义工作流程"""
    
    # 研究员任务 - 收集市场数据
    research_task = Task(
        description="""收集2023年AI代理技术市场的最新数据，包括市场规模、增长趋势、
        主要参与者和技术趋势。""",
        agent=researcher,
        expected_output="一份包含关键数据和趋势的详细研究报告"
    )
    
    # 分析任务 - 提炼关键见解
    analysis_task = Task(
        description="""分析研究数据，识别3-5个最重要的市场机会
        和潜在风险，并提供数据支持。""",
        agent=analyst,
        expected_output="清晰的商业机会列表，每个机会都有数据支持",
        context=[research_task]  # 依赖研究任务的结果
    )
    
    # 写作任务 - 生成最终报告
    write_task = Task(
        description="""根据研究和分析结果，撰写一份专业的市场研究报告。
        报告应包括执行摘要、市场概况、机会分析和建议部分。""",
        agent=writer,
        expected_output="一份15-20页的专业市场研究报告（MD格式）",
        context=[research_task, analysis_task]  # 依赖前两个任务的结果
    )
    
    return research_task, analysis_task, write_task

def main():
    """执行多代理协作流程"""
    
    # 创建代理团队
    researcher, writer, analyst = create_agents()
    
    # 定义任务链
    research_task, analysis_task, write_task = create_tasks(researcher, writer, analyst)
    
    # 组建团队并执行任务
    market_research_crew = Crew(
        agents=[res