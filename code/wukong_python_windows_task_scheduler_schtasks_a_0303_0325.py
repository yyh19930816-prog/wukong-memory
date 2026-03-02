#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
topydo CLI implementation
学习来源: GitHub仓库 topydo/topydo (https://github.com/topydo/topydo)
日期: 2023-11-15
功能描述: 实现一个简化的todo.txt命令行管理工具，支持添加/完成/列出任务等核心功能
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict

DEFAULT_TODO_FILE = os.path.expanduser("~/todo.txt")

class TodoItem:
    """表示单个todo条目的类"""
    def __init__(self, text: str, priority: str = None, 
                 creation_date: str = None, completion_date: str = None,
                 projects: List[str] = None, contexts: List[str] = None,
                 tags: Dict[str, str] = None):
        self.text = text
        self.priority = priority
        self.creation_date = creation_date or datetime.now().strftime("%Y-%m-%d")
        self.completion_date = completion_date
        self.projects = projects or []
        self.contexts = contexts or []
        self.tags = tags or {}
        
    def __str__(self) -> str:
        """转换为todo.txt格式字符串"""
        parts = []
        if self.priority:
            parts.append(f"({self.priority})")
        if self.completion_date:
            parts.append(f"x {self.completion_date}")
        parts.append(self.creation_date)
        parts.append(self.text)
        
        # 添加项目和上下文
        for project in self.projects:
            parts.append(f"+{project}")
        for context in self.contexts:
            parts.append(f"@{context}")
            
        # 添加标签
        for key, value in self.tags.items():
            parts.append(f"{key}:{value}")
            
        return " ".join(parts)

class TodoList:
    """管理todo条目的集合"""
    def __init__(self, file_path: str = DEFAULT_TODO_FILE):
        self.file_path = file_path
        self.todos = self._load_todos()
        
    def _load_todos(self) -> List[TodoItem]:
        """从文件加载todo条目"""
        todos = []
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 简化的解析逻辑，实际更复杂
                        todos.append(TodoItem(text=line))
        return todos
        
    def save(self):
        """保存todo条目到文件"""
        with open(self.file_path, "w") as f:
            for todo in self.todos:
                f.write(str(todo) + "\n")
                
    def add(self, text: str):
        """添加新todo"""
        self.todos.append(TodoItem(text))
        self.save()
        
    def complete(self, index: int):
        """标记todo为完成状态"""
        if 0 <= index < len(self.todos):
            self.todos[index].completion_date = datetime.now().strftime("%Y-%m-%d")
            self.save()
            
    def list(self, show_completed: bool = False):
        """列出所有todo"""
        for i, todo in enumerate(self.todos):
            if not show_completed and todo.completion_date:
                continue
            prefix = "[x]" if todo.completion_date else f"[{i}]"
            print(f"{prefix} {todo}")

def main():
    """主命令行接口"""
    parser = argparse.ArgumentParser(description="A simple todo.txt CLI")
    subparsers = parser.add_subparsers(dest="command",