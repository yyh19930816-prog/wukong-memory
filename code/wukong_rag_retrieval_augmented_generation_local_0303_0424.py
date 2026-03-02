#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow API Client Implementation
学习来源: https://github.com/infiniflow/ragflow
日期: 2023-11-20
功能描述: 实现了RAGFlow REST API的基本交互功能，包括知识库管理、文档上传和向量搜索
"""

import requests
import json
from typing import Dict, List, Optional

class RAGFlowClient:
    """
    RAGFlow API客户端封装类
    
    提供对RAGFlow REST API的简单封装，支持:
    1. 知识库管理
    2. 文档上传和处理
    3. 向量搜索功能
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = None):
        """
        初始化客户端
        
        Args:
            base_url: RAGFlow服务基础URL (默认: http://localhost:8080)
            api_key: API密钥 (可选)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def create_knowledge_base(self, name: str, description: str = "") -> Dict:
        """
        创建新的知识库
        
        Args:
            name: 知识库名称
            description: 知识库描述 (可选)
            
        Returns:
            创建的知识库信息
        """
        url = f"{self.base_url}/api/v1/knowledge_bases"
        payload = {
            "name": name,
            "description": description
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def upload_document(self, kb_id: str, file_path: str) -> Dict:
        """
        上传文档到指定知识库
        
        Args:
            kb_id: 知识库ID
            file_path: 要上传的文件路径
            
        Returns:
            上传结果信息
        """
        url = f"{self.base_url}/api/v1/knowledge_bases/{kb_id}/documents"
        files = {'file': open(file_path, 'rb')}
        
        # 移除Content-Type头部，因为multipart/form-data需要自动生成boundary
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'content-type'}
        
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()

    def semantic_search(self, kb_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """
        在知识库中执行语义搜索
        
        Args:
            kb_id: 知识库ID
            query: 搜索查询文本
            top_k: 返回结果数量 (默认5)
            
        Returns:
            相关文档片段列表
        """
        url = f"{self.base_url}/api/v1/knowledge_bases/{kb_id}/search"
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get('results', [])

    def list_knowledge_bases(self) -> List[Dict]:
        """获取所有知识库列表"""
        url = f"{self.base_url}/api/v1/knowledge_bases"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()