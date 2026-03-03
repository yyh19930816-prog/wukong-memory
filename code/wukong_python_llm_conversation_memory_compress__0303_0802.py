#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Memory Implementation - Local Knowledge Storage for LLMs
Based on GitHub repo: basicmachines-co/basic-memory
Created on: 2023-11-15
Description: Implements core functionality of Basic Memory - a local Markdown-based 
knowledge storage system that works with LLMs via Model Context Protocol (MCP).
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List
import re
from datetime import datetime

class BasicMemory:
    """Core implementation of Basic Memory local knowledge storage."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize Basic Memory with storage directory.
        
        Args:
            storage_dir: Path to store Markdown files (default: ~/basic-memory)
        """
        self.storage_dir = Path(storage_dir or os.path.expanduser("~/basic-memory"))
        self.storage_dir.mkdir(exist_ok=True)
    
    def create_note(self, title: str, content: str) -> str:
        """
        Create a new Markdown note file.
        
        Args:
            title: Note title/slug (will be sanitized)
            content: Markdown content of the note
            
        Returns:
            Path to the created note file
        """
        # Sanitize filename by removing special chars and spaces
        sanitized = re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-')[:50]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}-{sanitized}.md"
        filepath = self.storage_dir / filename
        
        # Write Markdown content with title as header
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{content}")
            
        return str(filepath)
    
    def search_notes(self, query: str) -> List[Dict]:
        """
        Search through all notes for matching content.
        
        Args:
            query: Search term(s) to look for
            
        Returns:
            List of matching notes with metadata
        """
        matches = []
        
        for filepath in self.storage_dir.glob("*.md"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        matches.append({
                            "path": str(filepath),
                            "content": content[:200] + "..."  # Return snippet
                        })
            except UnicodeDecodeError:
                continue
                
        return matches
    
    def get_note(self, path: str) -> Optional[str]:
        """
        Get the full content of a specific note.
        
        Args:
            path: Path to the note file
            
        Returns:
            Markdown content if exists, else None
        """
        path = Path(path)
        if path.exists() and path.suffix == '.md':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

if __name__ == "__main__":
    # Example usage
    mem = BasicMemory()
    
    # Create a sample note
    coffee_note = mem.create_note(
        "Coffee Brewing Methods",
        "Here are my favorite coffee brewing techniques:\n\n"
        "- Pour over (V60)\n"
        "- Aeropress\n"
        "- French press\n"
    )
    print(f"Created note at: {coffee_note}")
    
    # Search notes
    results = mem.search_notes("coffee")
    print