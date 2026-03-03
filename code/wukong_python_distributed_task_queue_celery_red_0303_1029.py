#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery任务队列基础示例
学习来源: https://github.com/celery/celery
创建日期: 2023-11-20
功能描述: 
    基于Celery实现异步任务队列的完整示例
    包含任务定义、worker启动、任务调度和结果获取
    使用Redis作为消息代理和结果后端
"""

from celery import Celery
import time

# 初始化Celery应用，设置Redis作为消息代理和结果后端
# broker参数指定消息代理URL，backend参数指定结果存储URL
app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 简单配置Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True)
def long_running_task(self, x, y):
    """模拟长时间运行的任务，带进度更新
    
    Args:
        x: 第一个数字
        y: 第二个数字
        self: Celery任务绑定，用于更新状态
        
    Returns:
        x和y的处理结果
    """
    total_steps = 100
    result = 0
    
    # 模拟长时间处理过程
    for i in range(total_steps):
        time.sleep(0.1)  # 模拟耗时操作
        result = x * y + i  # 简单的计算
        
        # 更新任务状态，包括进度百分比
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_steps,
                'percent': (i + 1) / total_steps * 100,
                'result': result
            }
        )
    
    return {'final_result': result}

@app.task
def add(x, y):
    """简单的加法任务
    
    Args:
        x: 第一个数字
        y: 第二个数字
        
    Returns:
        两数之和
    """
    return x + y

if __name__ == '__main__':
    # 演示如何调用任务
    # 1. 启动worker命令: celery -A tasks worker --loglevel=info
    # 2. 然后在另一个终端运行此脚本
    
    # 调用异步加法任务
    async_result = add.delay(4, 6)
    print(f"异步任务已提交，任务ID: {async_result.id}")
    
    # 检查任务是否完成
    if async_result.ready():
        print(f"任务结果: {async_result.get()}")  # 获取结果
    else:
        print("任务仍在处理中...")
    
    # 调用长时间运行的任务
    long_task = long_running_task.delay(3, 4)
    print(f"长时间任务已提交，任务ID: {long_task.id}")
    
    # 轮询获取长时间任务进度
    while not long_task.ready():
        print(f"当前进度: {long_task.info.get('percent', 0):.1f}%")
        time.sleep(1)
    
    print(f"最终结果: {long_task.get()['final_result']}")