#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习来源：https://github.com/topydo/topydo
创建日期：2023-05-01
功能描述：一个简易的todo.txt命令行管理工具，实现核心的添加、完成、列表功能
"""

import argparse
from datetime import datetime
import os
import re

class TodoList:
    def __init__(self, todo_file='todo.txt'):
        self.todo_file = todo_file
        # 如果todo.txt不存在则创建
        if not os.path.exists(todo_file):
            open(todo_file, 'w').close()

    def add_task(self, task_text, priority=None):
        """添加新任务到todo.txt"""
        with open(self.todo_file, 'a') as f:
            # 如果有优先级则添加到任务前面
            if priority:
                task_text = f"({priority.upper()}) " + task_text
            # 添加创建日期
            task_text += f" c:{datetime.now().strftime('%Y-%m-%d')}"
            f.write(task_text + '\n')
        return True

    def complete_task(self, task_id):
        """标记任务为已完成"""
        with open(self.todo_file, 'r') as f:
            tasks = f.readlines()
        
        if 0 < task_id <= len(tasks):
            # 添加完成日期和x标记
            completed_task = tasks[task_id-1].rstrip() + f" d:{datetime.now().strftime('%Y-%m-%d')}\n"
            # 在行首添加x标记
            completed_task = 'x ' + completed_task.lstrip()
            tasks[task_id-1] = completed_task
            
            with open(self.todo_file, 'w') as f:
                f.writelines(tasks)
            return True
        return False

    def list_tasks(self, show_ids=False, filter_active=False):
        """列出所有任务或只列出未完成任务"""
        with open(self.todo_file, 'r') as f:
            tasks = f.readlines()
        
        for idx, task in enumerate(tasks, 1):
            task = task.strip()
            # 如果只显示活跃任务且任务已完成则跳过
            if filter_active and (task.startswith('x ') or ' d:' in task.lower()):
                continue
            # 如果有显示ID的需求则打印ID
            if show_ids:
                print(f"{idx}. {task}")
            else:
                print(task)
        return True

    def get_task_count(self):
        """获取任务总数"""
        with open(self.todo_file, 'r') as f:
            return len(f.readlines())

def main():
    parser = argparse.ArgumentParser(description='A simple todo.txt manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # 添加任务命令
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('task', help='Task description')
    add_parser.add_argument('-p', '--priority', help='Task priority (A-Z)')

    # 完成任务命令
    done_parser = subparsers.add_parser('done', help='Mark task as done')
    done_parser.add_argument('task_id', type=int, help='Task ID to mark as done')

    # 列出任务命令
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-i', '--ids', action='store_true', help='Show task IDs')
    list_parser.add_argument('-a', '--active', action='store_true',