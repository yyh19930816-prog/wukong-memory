#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习来源: basicmachines-co/basic-memory GitHub仓库
日期: 2024-03-20
功能描述: 实现一个本地知识管理系统，允许LLMs通过Markdown文件持久化对话知识
特征:
1. 创建/读取/搜索Markdown格式的笔记
2. 默认笔记存储在~/basic-memory目录
3. 提供简单的REST API接口供LLM调用
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT_MEMORY_DIR = os.path.expanduser("~/basic-memory")


class BasicMemory:
    def __init__(self, memory_dir: str = DEFAULT_MEMORY_DIR):
        """初始化Basic Memory，设置笔记存储目录"""
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

    def create_note(self, title: str, content: str) -> str:
        """创建新笔记，返回文件路径"""
        filename = self._sanitize_filename(title)
        filepath = self.memory_dir / f"{filename}.md"
        
        with open(filepath, "w") as f:
            f.write(f"# {title}\n\n{content}")
            
        return str(filepath)

    def search_notes(self, query: str) -> Dict[str, str]:
        """搜索笔记内容，返回匹配的笔记标题和内容"""
        results = {}
        pattern = re.compile(query, re.IGNORECASE)
        
        for file in self.memory_dir.glob("*.md"):
            with open(file, "r") as f:
                content = f.read()
                if pattern.search(content):
                    title = self._extract_title(content)
                    results[title] = content
        
        return results

    def get_note(self, title: str) -> Optional[str]:
        """获取指定标题的笔记内容"""
        filename = self._sanitize_filename(title)
        filepath = self.memory_dir / f"{filename}.md"
        
        if filepath.exists():
            with open(filepath, "r") as f:
                return f.read()
        return None

    def _sanitize_filename(self, text: str) -> str:
        """清理字符串作为有效文件名"""
        return re.sub(r'[^\w\-_]', '_', text.strip().lower())

    def _extract_title(self, content: str) -> str:
        """从Markdown内容提取标题"""
        return content.split("\n")[0].lstrip("#").strip()


class MCPRequestHandler(BaseHTTPRequestHandler):
    """MCP协议HTTP请求处理器"""

    def do_POST(self):
        """处理LLM的POST请求"""
        content_length = int(self.headers["Content-Length"])
        post_data = json.loads(self.rfile.read(content_length))
        
        memory = BasicMemory()
        response = {"status": "success"}
        
        if post_data.get("action") == "create_note":
            path = memory.create_note(post_data["title"], post_data["content"])
            response["filepath"] = path
        elif post_data.get("action") == "search_notes":
            response["results"] = memory.search_notes(post_data["query"])
        elif post_data.get("action") == "get_note":
            content = memory.get_note(post_data["title"])
            response["content"] = content if content else "Note not found"
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps