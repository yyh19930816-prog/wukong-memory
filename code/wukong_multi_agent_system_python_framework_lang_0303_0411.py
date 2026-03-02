"""
基于GitHub仓库 akj2018/Multi-AI-Agent-Systems-with-crewAI 实现的多AI代理系统
日期: 2023-11-20
功能: 实现一个简历优化多代理系统，包含研究员和写作专家两个角色
"""

from crewai import Agent, Task, Crew
from langchain_community.llms import OpenAI
import os

# 设置OpenAI API密钥
os.environ["OPENAI_API_KEY"] = "your-api-key"

def setup_resume_agents():
    """
    设置简历优化代理团队
    Returns:
        crewAI Crew对象: 包含配置好的代理和任务
    """
    
    # 创建LLM实例 - 可以根据不同任务使用不同的模型
    llm = OpenAI(temperature=0.7, model_name="gpt-4")
    
    # 创建研究员代理 - 专门负责简历调研
    researcher = Agent(
        role='资深职业顾问',
        goal='深入研究职位描述并识别关键技能要求',
        backstory='你是一位拥有10年人力资源经验的职业顾问，擅长分析职位要求并匹配候选人技能',
        verbose=True,
        llm=llm,
        memory=True  # 启用记忆功能让代理可以记住上下文
    )
    
    # 创建写作专家代理 - 专门负责简历改写
    writer = Agent(
        role='专业简历写手', 
        goal='根据研究报告优化简历内容，使其更符合职位要求',
        backstory='你是一位专业的简历优化专家，拥有为500强高管改写简历的经验',
        verbose=True,
        llm=llm
    )
    
    # 创建研究员任务
    research_task = Task(
        description="""
        分析以下职位描述：
        '{job_description}'
        
        并识别出关键的技能要求和行业术语，为简历优化提供方向。
        """,
        agent=researcher,
        expected_output='一份详细的分析报告，列出职位要求的关键技能和行业术语'
    )
    
    # 创建写作任务
    write_task = Task(
        description="""
        根据研究结果优化以下简历：
        '{resume_content}'
        
        使其更符合职位要求，突出相关技能和经验。
        保持专业格式，使用行业适当术语。
        """,
        agent=writer,
        expected_output='优化后的专业简历文档，格式整洁，内容针对职位定制'
    )
    
    # 创建多代理团队
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=2  # 显示详细执行信息
    )
    
    return crew

def optimize_resume(job_description, resume_content):
    """
    执行简历优化流程
    Args:
        job_description (str): 职位描述文本
        resume_content (str): 原始简历内容
    
    Returns:
        dict: 包含研究结果和优化后的简历
    """
    # 设置代理团队
    crew = setup_resume_agents()
    
    # 执行任务流
    inputs = {
        'job_description': job_description,
        'resume_content': resume_content
    }
    result = crew.kickoff(inputs=inputs)
    
    return {
        'research_report': result[0],  # 第一个任务的输出(研究结果)
        'optimized_resume': result[1]  # 第二个任务的输出(优化简历)
    }

if __name__ == '__main__':
    # 示例用法
    job_desc = "寻找Python开发工程师，需要5年以上经验，熟悉Django/Flask框架，有AWS部署经验"
    resume = """
    张三
    工作经验:
    - Python开发4年
    - 使用Flask构建Web应用
    - 基础的云服务知识