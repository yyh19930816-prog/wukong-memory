#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-AI Agent System using crewAI
学习来源: https://github.com/akj2018/Multi-AI-Agent-Systems-with-crewAI
创建日期: 2024-02-20
功能描述: 实现一个多AI代理系统，包含研究员和写手两个角色，协作完成技术文章写作任务
"""

from crewai import Agent, Task, Crew
from langchain.llms import Ollama  # Requires ollama server running locally

# 1. 设置AI模型 - 可以使用不同的模型给不同代理
# 需要先运行 ollama pull llama2 下载模型
llm = Ollama(model="llama2")

# 2. 创建AI代理 - 每个代理有特定角色和目标
researcher = Agent(
    role="技术研究员",
    goal="为技术主题进行深入调研，收集准确的技术信息",
    backstory="一个擅长从技术文档和白皮书中提取关键信息的AI研究员",
    verbose=True,  # 显示详细思考过程
    allow_delegation=False,
    llm=llm  # 可以每个代理使用不同的LLM
)

writer = Agent(
    role="技术写手",
    goal="根据研究内容编写专业的技术文章",
    backstory="一位能将复杂技术概念转化为清晰易懂文字的技术作家",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 3. 定义任务 - 明确每个代理的具体任务
research_task = Task(
    description=(
        "调研关于大语言模型(LLM)在自动化业务流程中的最新应用。"
        "重点关注multi-agent系统和crewAI框架。"
        "提供详细的技术细节和使用案例。"
    ),
    expected_output="一份包含3-5个关键点的详细技术研究报告",
    agent=researcher
)

write_task = Task(
    description=(
        "根据研究结果撰写一篇1000字左右的技术博客文章。"
        "文章需要专业但易懂，包含引言、正文和结论。"
        "重点关注multi-agent系统相比单一LLM的优势。"
    ),
    expected_output="一篇格式完整、内容专业的技术博客文章",
    agent=writer
)

# 4. 创建代理团队 - 配置代理的工作流
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=2  # 控制日志详细程度
)

# 5. 启动任务执行
if __name__ == "__main__":
    print("## 开始执行多代理任务 ##")
    result = crew.kickoff()
    
    print("\n\n## 最终输出结果 ##")
    print(result)