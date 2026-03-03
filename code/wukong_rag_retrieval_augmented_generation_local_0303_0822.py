#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow API Client Implementation
Source: https://github.com/infiniflow/ragflow
Created: 2024-02-10
Description: A Python client for interacting with RAGFlow's API endpoints
to perform Retrieval-Augmented Generation tasks.
"""

import requests
from typing import Optional, Dict, Any
import json

class RAGFlowClient:
    """
    A client for interacting with the RAGFlow REST API.
    
    Attributes:
        base_url (str): The base URL of the RAGFlow API
        api_key (str): The API key for authentication
        timeout (int): Request timeout in seconds
    """
    
    def __init__(self, base_url: str = "https://demo.ragflow.io/api", 
                 api_key: Optional[str] = None, 
                 timeout: int = 30):
        """
        Initialize the RAGFlow client.
        
        Args:
            base_url: The base API URL (defaults to demo instance)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
    def _make_request(self, endpoint: str, method: str = 'GET', 
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Internal method to make HTTP requests to the API.
        
        Args:
            endpoint: API endpoint path (without base URL)
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            
        Returns:
            Dictionary containing the JSON response
            
        Raises:
            requests.exceptions.RequestException: If request fails
            ValueError: If response contains error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}") from e
            
    def query(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the RAGFlow knowledge base with a text prompt.
        
        Args:
            text: The input text/question to query
            top_k: Number of results to return (default: 3)
            
        Returns:
            Dictionary containing query results and generated answer
        """
        endpoint = "/v1/query"
        data = {
            "query": text,
            "top_k": top_k
        }
        return self._make_request(endpoint, method='POST', data=data)
        
    def upload_document(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a document to the RAGFlow knowledge base.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Dictionary containing upload status and document ID
        """
        endpoint = "/v1/documents"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('/')[-1], f)}
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    files=files,
                    headers={'Authorization': f'Bearer {self