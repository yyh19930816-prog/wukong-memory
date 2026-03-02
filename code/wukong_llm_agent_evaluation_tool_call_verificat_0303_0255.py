#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RagaAI Catalyst API Client Implementation
Based on GitHub repository: raga-ai-hub/RagaAI-Catalyst
Date: 2023-11-20
Description: A Python client for RagaAI Catalyst platform with core functionalities including:
- Project Management
- Dataset Management
- Evaluation Management
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os
from typing import Dict, List, Optional

class RagaAICatalystClient:
    """
    Client for interacting with RagaAI Catalyst platform.
    Handles authentication and provides core functionality.
    """
    
    def __init__(self, access_key: str, secret_key: str, base_url: str):
        """
        Initialize RagaAI Catalyst client with authentication credentials.
        
        Args:
            access_key: API access key
            secret_key: API secret key
            base_url: Base URL for API endpoints
        """
        self.client = RagaAICatalyst(
            access_key=access_key,
            secret_key=secret_key,
            base_url=base_url
        )
        
    def create_project(self, project_name: str, usecase: str) -> Dict:
        """
        Create a new project in RagaAI Catalyst.
        
        Args:
            project_name: Name of the project
            usecase: Use case category (e.g., "Chatbot")
            
        Returns:
            Created project details
        """
        return self.client.create_project(
            project_name=project_name,
            usecase=usecase
        )
    
    def list_projects(self) -> List[Dict]:
        """List all available projects."""
        return self.client.list_projects()
    
    def manage_dataset(self, project_name: str) -> 'DatasetManager':
        """
        Initialize dataset management for a specific project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            DatasetManager instance
        """
        return DatasetManager(self.client, project_name)

class DatasetManager:
    """
    Handles dataset operations for a specific project.
    """
    
    def __init__(self, client: RagaAICatalyst, project_name: str):
        """
        Initialize dataset manager.
        
        Args:
            client: Authenticated RagaAICatalyst instance
            project_name: Name of the project
        """
        self.dataset = Dataset(project_name=project_name)
        self.client = client
        
    def create_from_csv(self, csv_path: str, dataset_name: str, 
                       schema_mapping: Dict[str, str]) -> Dict:
        """
        Create dataset from CSV file with schema mapping.
        
        Args:
            csv_path: Path to CSV file
            dataset_name: Name for new dataset
            schema_mapping: Column to schema element mapping
            
        Returns:
            Created dataset details
        """
        return self.dataset.create_from_csv(
            csv_path=csv_path,
            dataset_name=dataset_name,
            schema_mapping=schema_mapping
        )
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets in the project."""
        return self.dataset.list_datasets()

if __name__ == "__main__":
    # Example usage
    try:
        # Initialize client with environment variables
        client = RagaAICatalystClient(
            access_key=os.getenv('RAGAAI_ACCESS_KEY'),
            secret_key=os.getenv('RAGAAI_SECRET_KEY'),
            base_url=os.getenv('RAGAAI_BASE_URL')
        )
        
        # Project management example
        print("Creating project...")
        project = client.create_project(
            project_name="Demo-RAG-App",
            usecase="Chatbot"
        )
        print(f"Created