#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Memory Implementation - A local-first knowledge graph builder

Learning Source: GitHub basicmachines-co/basic-memory repository
Date: Current date
Functionality:
- Implements a simple MCP server for LLM integration
- Manages local Markdown files as knowledge base
- Supports basic CRUD operations on memory notes
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
import uvicorn

class BasicMemory:
    """Core class for managing local knowledge base"""
    
    def __init__(self, base_dir: str = "~/basic-memory"):
        """Initialize with storage directory"""
        self.base_dir = Path(base_dir).expanduser()
        os.makedirs(self.base_dir, exist_ok=True)
        
    def create_note(self, topic: str, content: str) -> Dict:
        """Create a new markdown note"""
        filename = f"{topic.replace(' ', '_').lower()}.md"
        filepath = self.base_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# {topic}\n\n{content}")
            
        return {
            "status": "success",
            "path": str(filepath),
            "size": len(content)
        }
        
    def read_note(self, topic: str) -> Dict:
        """Read an existing note"""
        filename = f"{topic.replace(' ', '_').lower()}.md"
        filepath = self.base_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"No note found for {topic}")
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        return {
            "topic": topic,
            "content": content,
            "path": str(filepath)
        }
        
    def search_notes(self, query: str) -> Dict:
        """Simple content search across notes"""
        results = []
        
        for filepath in self.base_dir.glob("*.md"):
            with open(filepath, 'r') as f:
                content = f.read()
                if query.lower() in content.lower():
                    topic = filepath.stem.replace('_', ' ')
                    results.append({
                        "topic": topic,
                        "path": str(filepath)
                    })
                    
        return {"query": query, "results": results}

# Initialize FastAPI app and memory instance
app = FastAPI()
memory = BasicMemory()

@app.post("/mcp/basic-memory/create")
async def create_note_mcp(topic: str, content: str):
    """MCP endpoint for note creation"""
    try:
        return memory.create_note(topic, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mcp/basic-memory/read")
async def read_note_mcp(topic: str):
    """MCP endpoint for reading notes"""
    try:
        return memory.read_note(topic)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Note not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mcp/basic-memory/search")
async def search_notes_mcp(query: str):
    """MCP endpoint for searching notes"""
    try:
        return memory.search_notes(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def run_server(port: int = 8000):
    """Run the MCP server"""
    uvicorn.run(app, host="0.0.0.0", port=port)