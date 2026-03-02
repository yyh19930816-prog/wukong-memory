#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topydo CLI 简化实现
学习来源: https://github.com/topydo/topydo
创建日期: 2023-11-28
功能描述: 实现todo.txt的基本CRUD操作，支持优先级、标签、项目、上下文等特性
"""

import argparse
from datetime import datetime
import os
import re

class TodoItem:
    """表示单个待办事项的类"""
    
    def __init__(self, text, priority=None, projects=None, contexts=None, 
                 created=None, completed=False, completed_date=None):
        self.text = text
        self.priority = priority
        self.projects = projects or []
        self.contexts = contexts or []
        self.created = created or datetime.now()
        self.completed = completed
        self.completed_date = completed_date
        
    def __str__(self):
        """转换为todo.txt格式字符串"""
        parts = []
        if self.completed:
            parts.append("x")
            if self.completed_date:
                parts.append(self.completed_date.strftime("%Y-%m-%d"))
        
        if self.priority:
            parts.append(f"({self.priority.upper()})")
            
        parts.append(self.text)
        
        for project in self.projects:
            if not re.search(rf"\B\+{project}\b", self.text):
                parts.append(f"+{project}")
                
        for context in self.contexts:
            if not re.search(rf"\B@{context}\b", self.text):
                parts.append(f"@{context}")
                
        if not any(tag.startswith("due:") for tag in self.text.split()):
            pass  # 可以添加due日期处理
            
        return " ".join(parts)
            
class TodoList:
    """管理待办事项列表的类"""
    
    def __init__(self, filepath="todo.txt"):
        self.filepath = filepath
        self.todos = []
        self.load()
        
    def load(self):
        """从文件加载待办事项"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.parse_todo(line)
                        
    def parse_todo(self, line):
        """解析单行todo.txt"""
        completed = False
        priority = None
        projects = []
        contexts = []
        
        parts = line.split()
        
        if parts[0] == "x":
            completed = True
            parts = parts[1:]
            
        if parts and parts[0].startswith("(") and parts[0].endswith(")"):
            priority = parts[0][1:-1]
            parts = parts[1:]
            
        text = " ".join(parts)
        
        # 提取项目和上下文
        for part in parts:
            if part.startswith("+"):
                projects.append(part[1:])
            elif part.startswith("@"):
                contexts.append(part[1:])
                
        todo = TodoItem(text, priority, projects, contexts, completed=completed)
        self.todos.append(todo)
        
    def save(self):
        """保存到文件"""
        with open(self.filepath, 'w') as f:
            for todo in self.todos:
                f.write(str(todo) + "\n")
                
    def add(self, text):
        """添加新的待办事项"""
        todo = TodoItem(text)
        self.todos.append(todo)
        self.save()
        
    def list(self, filter=None):
        """列出待办事项"""
        for i, todo in enumerate(self.todos, 1):
            if not todo.completed or filter !=