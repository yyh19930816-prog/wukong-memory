#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topydo CLI Implementation
-------------------------
Learn from: https://github.com/topydo/topydo
Date: 2023-04-01
Main features:
- Basic todo.txt format operations (add/list/complete)
- Due date and priority support
- Simple dependency tracking
- Colorized output
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

class TodoItem:
    """Represents a single todo item with parsing and formatting"""
    
    def __init__(self, raw_text, todo_id=None):
        self.raw_text = raw_text.strip()
        self.id = todo_id
        self.priority = None
        self.completed = False
        self.due_date = None
        self.depends_on = []
        self._parse()
    
    def _parse(self):
        """Parse the raw todo.txt line into components"""
        if self.raw_text.startswith('x '):
            self.completed = True
        
        # Extract priority (e.g., (A))
        priority_match = re.search(r'\(([A-Z])\)', self.raw_text)
        if priority_match:
            self.priority = priority_match.group(1)
        
        # Extract due date (e.g., due:2023-04-30)
        due_match = re.search(r'due:(\d{4}-\d{2}-\d{2})', self.raw_text)
        if due_match:
            self.due_date = due_match.group(1)
        
        # Extract dependencies (e.g., dep:1,2)
        dep_match = re.search(r'dep:([0-9,]+)', self.raw_text)
        if dep_match:
            self.depends_on = dep_match.group(1).split(',')
    
    def __str__(self):
        """Format todo item back to string representation"""
        parts = []
        if self.completed:
            parts.append('x')
        if self.priority:
            parts.append(f'({self.priority})')
        parts.append(self.raw_text.replace('\n', ' ').strip())
        return ' '.join(parts)

class TodoList:
    """Main todo list manager with file operations"""
    
    def __init__(self, filename='todo.txt'):
        self.filename = Path.home() / filename
        self.items = []
        self._load()
    
    def _load(self):
        """Load todos from file"""
        if not self.filename.exists():
            return
        
        with open(self.filename, 'r') as f:
            for idx, line in enumerate(f, 1):
                if line.strip():
                    self.items.append(TodoItem(line, str(idx)))
    
    def _save(self):
        """Save todos to file"""
        with open(self.filename, 'w') as f:
            f.write('\n'.join(str(item) for item in self.items))
    
    def add(self, text):
        """Add new todo item"""
        new_item = TodoItem(text)
        self.items.append(new_item)
        self._save()
        print(f"Added: {new_item}")
    
    def list(self):
        """List all todos with color formatting"""
        for idx, item in enumerate(self.items, 1):
            status = '✓' if item.completed else ' '
            priority = f"[{item.priority}]" if item.priority else ' ' * 3
            due = f"due:{item.due_date}" if item.due_date else ''
            print(f"\033[1m{idx:3}\033[0m [{status}] {priority} {item.raw_text} {due}")
    
    def complete(self, todo_id):
        """