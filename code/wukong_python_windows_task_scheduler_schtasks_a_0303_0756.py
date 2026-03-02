#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
topydo CLI implementation - basic todo.txt manager
学习来源: https://github.com/topydo/topydo
创建日期: 2023-11-15
功能描述: 实现todo.txt的基本CRUD操作，支持标签、优先级、依赖关系等核心功能
"""

import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict

TODO_FILE = os.path.expanduser('~/todo.txt')

class TodoItem:
    """表示单个待办事项的类"""
    def __init__(self, text, priority=None, creation_date=None, contexts=None, 
                 projects=None, tags=None, completed=False, completion_date=None):
        self.text = text
        self.priority = priority
        self.creation_date = creation_date or datetime.now().strftime('%Y-%m-%d')
        self.contexts = contexts or []
        self.projects = projects or []
        self.tags = tags or {}
        self.completed = completed
        self.completion_date = completion_date
        
    def __str__(self):
        """转换为todo.txt格式的字符串"""
        parts = []
        if self.completed:
            parts.append('x')
        if self.priority:
            parts.append(f'({self.priority})')
        parts.append(self.creation_date)
        if self.completion_date:
            parts.append(self.completion_date)
        parts.append(self.text)
        
        # 添加标签
        for tag, value in self.tags.items():
            parts.append(f'{tag}:{value}')
            
        return ' '.join(parts)

class TodoList:
    """管理待办事项列表的类"""
    def __init__(self):
        self.items = []
        self.load()
        
    def load(self):
        """从文件加载待办事项"""
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.parse_line(line)
                        
    def parse_line(self, line):
        """解析单行todo.txt格式"""
        parts = line.split()
        item = TodoItem('')
        
        # 处理完成状态
        if parts[0] == 'x':
            item.completed = True
            item.completion_date = parts[1]
            parts = parts[2:]
            
        # 处理优先级
        if parts and parts[0].startswith('(') and parts[0].endswith(')'):
            item.priority = parts[0][1:-1]
            parts = parts[1:]
            
        # 处理创建日期
        item.creation_date = parts[0]
        parts = parts[1:]
        
        # 处理剩余文本和标签
        text_parts = []
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                item.tags[key] = value
            else:
                text_parts.append(part)
                
        item.text = ' '.join(text_parts)
        self.items.append(item)
        
    def save(self):
        """保存待办事项到文件"""
        with open(TODO_FILE, 'w') as f:
            for item in self.items:
                f.write(str(item) + '\n')
                
    def add(self, text):
        """添加新待办事项"""
        item = TodoItem(text)
        self.items.append(item)
        self.save()
        
    def list(self, filter_completed=False):
        """列出待办事项"""
        for idx, item in enumerate(self.items):
            if not filter_completed or not item.completed:
                print(f"{idx + 1}. {item}")
                
    def