#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
topydo-core.py - Minimal implementation of topydo core functionality

Based on https://github.com/topydo/topydo README
Created: 2023-04-20
Functionality:
- Todo.txt format parser/writer
- Basic CRUD operations for todo items
- Due date and priority support
- Simple CLI interface

Note: This is a simplified implementation demonstrating core concepts.
"""

import sys
import re
from datetime import datetime
from collections import defaultdict

class TodoItem:
    """Represents a single todo item with todo.txt attributes"""
    
    def __init__(self, raw_text=''):
        """Initialize todo item from raw text line"""
        self.raw_text = raw_text.strip()
        self.completed = False
        self.priority = None
        self.description = ''
        self.contexts = []
        self.projects = []
        self.tags = {}
        self.created_date = None
        self.due_date = None
        
        self._parse()
    
    def _parse(self):
        """Parse raw text into todo item components"""
        parts = self.raw_text.split()
        
        # Check completed status
        if parts and parts[0] == 'x':
            self.completed = True
            parts = parts[1:]
        
        # Parse priority (A-Z in parentheses)
        if parts and re.match(r'^\([A-Z]\)$', parts[0]):
            self.priority = parts[0][1:-1]
            parts = parts[1:]
        
        # Parse dates (created date may appear here)
        if len(parts) >= 2 and re.match(r'^\d{4}-\d{2}-\d{2}$', parts[0]):
            self.created_date = parts[0]
            parts = parts[1:]
        
        # Remaining parts make up description + tags/projects/contexts
        self.description_parts = []
        
        for part in parts:
            # Projects start with +
            if part.startswith('+'):
                self.projects.append(part[1:])
            # Contexts start with @
            elif part.startswith('@'):
                self.contexts.append(part[1:])
            # Tags are key:value pairs
            elif ':' in part:
                key, value = part.split(':', 1)
                self.tags[key] = value
                # Special handling for due date
                if key == 'due':
                    self.due_date = value
            else:
                self.description_parts.append(part)
        
        self.description = ' '.join(self.description_parts)
    
    def __str__(self):
        """Convert todo item back to todo.txt format"""
        parts = []
        
        if self.completed:
            parts.append('x')
        
        if self.priority:
            parts.append(f'({self.priority})')
        
        if self.created_date:
            parts.append(self.created_date)
        
        parts.append(self.description)
        
        for project in self.projects:
            parts.append(f'+{project}')
        
        for context in self.contexts:
            parts.append(f'@{context}')
        
        for key, value in self.tags.items():
            parts.append(f'{key}:{value}')
        
        return ' '.join(parts)

class TodoList:
    """Manages a collection of todo items"""
    
    def __init__(self, filename='todo.txt'):
        self.filename = filename
        self.items = []
        self.load()
    
    def load(self):
        """Load todo items from file"""
        try:
            with open(self.filename, 'r') as f:
                self.items = [TodoItem(line) for line in f.readlines() if line.strip()]
        except