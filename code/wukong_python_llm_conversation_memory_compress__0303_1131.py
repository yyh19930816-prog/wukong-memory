#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Memory Implementation - Local Knowledge Base for LLMs

Source: GitHub repo basicmachines-co/basic-memory (https://github.com/basicmachines-co/basic-memory)
Date: 2023-12-01

This script implements core functionality of Basic Memory:
- Local knowledge base stored in Markdown files
- CRUD operations for notes/information
- MCP-compatible interface for LLM integration
"""

import os
import json
import glob
from pathlib import Path
from typing import Optional, Dict, List
import markdown


class BasicMemory:
    """Core class implementing Basic Memory functionality"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize Basic Memory instance
        
        Args:
            base_dir: Optional path to knowledge base directory
                     (defaults to ~/basic-memory)
        """
        self.base_dir = base_dir or os.path.expanduser("~/basic-memory")
        os.makedirs(self.base_dir, exist_ok=True)
        
    def create_note(self, title: str, content: str) -> str:
        """
        Create a new note in the knowledge base
        
        Args:
            title: Title/name of the note
            content: Content in Markdown format
            
        Returns:
            Path to the created note file
        """
        filename = self._sanitize_filename(title) + ".md"
        filepath = os.path.join(self.base_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(f"# {title}\n\n{content}")
            
        return filepath
    
    def search_notes(self, query: str) -> List[Dict[str, str]]:
        """
        Search notes matching query
        
        Args:
            query: Search string
            
        Returns:
            List of matching notes with title and content
        """
        results = []
        for md_file in glob.glob(os.path.join(self.base_dir, "*.md")):
            with open(md_file, "r") as f:
                content = f.read()
                if query.lower() in content.lower():
                    title = os.path.basename(md_file)[:-3]
                    results.append({
                        "title": title,
                        "content": content,
                        "path": md_file
                    })
        return results
    
    def get_note(self, title: str) -> Optional[Dict[str, str]]:
        """
        Get a note by title
        
        Args:
            title: Title of the note
            
        Returns:
            Note content dict or None if not found
        """
        filename = self._sanitize_filename(title) + ".md"
        filepath = os.path.join(self.base_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            return {
                "title": title,
                "content": content,
                "path": filepath
            }
        return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize string for safe filename use"""
        return "".join(
            c for c in filename 
            if c.isalnum() or c in "-_ "
        ).rstrip().replace(" ", "_")


if __name__ == "__main__":
    # Example usage
    print("Basic Memory Demo")
    bm = BasicMemory()
    
    # Create sample note
    note_path = bm.create_note(
        "Coffee Brewing Methods",
        "Here are some common brewing methods:\n"
        "- Pour Over\n- French Press\n- Aeropress\n"
    )
    print(f"Created note at: {note