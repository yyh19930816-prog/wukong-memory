#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ragflow-cli.py - A minimal RAGFlow client implementation

Created based on infiniflow/ragflow README content
Date: [Current Date]

Core Features:
- Interact with RAGFlow API endpoints
- Supports document upload and query operations
- Lightweight implementation mimicking official RAGFlow demo functionality

Note: This is a simplified demonstration using mock endpoints.
In production, use the official Docker container or API endpoints.
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

class RAGFlowClient:
    """A minimal client for interacting with RAGFlow services."""
    
    def __init__(self, base_url: str = "https://demo.ragflow.io/api/v1"):
        """
        Initialize RAGFlow client.
        
        Args:
            base_url: Base API URL (defaults to demo instance)
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def upload_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a document to RAGFlow for processing.
        
        Args:
            file_path: Path to document file
            metadata: Optional document metadata
            
        Returns:
            Dictionary containing upload response
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        url = f"{self.base_url}/documents"
        files = {'file': open(file_path, 'rb')}
        data = {'metadata': json.dumps(metadata or {})}
        
        try:
            resp = self.session.post(url, files=files, data=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
            
    def query_knowledge(self, question: str, docs_limit: int = 5) -> Dict[str, Any]:
        """
        Query RAGFlow knowledge base.
        
        Args:
            question: Natural language question
            docs_limit: Maximum documents to return
            
        Returns:
            Dictionary containing query results
        """
        url = f"{self.base_url}/query"
        data = {
            'question': question,
            'limit': docs_limit
        }
        
        try:
            resp = self.session.post(url, json=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            resp = self.session.get(f"{self.base_url}/status")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise Exception(f"Status check failed: {str(e)}")

def main():
    """Demonstrate RAGFlow client functionality."""
    print("RAGFlow Mini Client\n-------------------")
    
    # Initialize client (using demo endpoint)
    client = RAGFlowClient()
    
    # Check service status
    status = client.get_status()
    print(f"\nService Status: {status.get('status', 'unknown')}")
    
    # Simple query demonstration
    question = "What is RAGFlow?"
    print(f"\nQuerying: '{question}'")
    
    try:
        results = client.query_knowledge(question)
        print("\nQuery Results:")
        if 'answers' in results:
            for i, answer in enumerate(results['answers'], 1):
                print(f"{i}. {answer.get('text', 'No text')}")
                print(f"   Source: {answer.get('source',