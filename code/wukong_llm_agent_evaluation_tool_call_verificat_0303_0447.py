#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RagaAI Catalyst Python Client Implementation
Source: raga-ai-hub/RagaAI-Catalyst (GitHub)
Date: 2023-11-20 (assumed)

This script demonstrates core functionality of RagaAI Catalyst:
- Project management (create/list projects)
- Dataset management (list/create datasets from CSV)
- Initialize with API credentials from environment variables
"""

import os
from ragaai_catalyst import RagaAICatalyst, Dataset

def main():
    # Initialize RagaAI Catalyst client
    # Recommended to set credentials via environment variables
    catalyst = RagaAICatalyst(
        access_key=os.getenv('RAGAAI_ACCESS_KEY', 'your_access_key'),
        secret_key=os.getenv('RAGAAI_SECRET_KEY', 'your_secret_key'),
        base_url=os.getenv('RAGAAI_BASE_URL', 'https://api.raga.ai')
    )

    # 1. Project Management Demo
    print("\n=== Project Management ===")
    
    # Create a sample project
    try:
        project = catalyst.create_project(
            project_name="Demo-RAG-App",
            usecase="Q&A System"
        )
        print(f"Created project: {project['name']}")
    except Exception as e:
        print(f"Project creation failed: {str(e)}")

    # List all projects
    try:
        projects = catalyst.list_projects()
        print("\nAvailable Projects:")
        for p in projects:
            print(f"- {p['name']} ({p['usecase']})")
    except Exception as e:
        print(f"Failed to list projects: {str(e)}")

    # 2. Dataset Management Demo
    print("\n=== Dataset Management ===")
    
    # Initialize dataset manager - replace with actual project name
    dataset_manager = Dataset(project_name="Demo-RAG-App")

    # List existing datasets
    try:
        datasets = dataset_manager.list_datasets()
        print("\nExisting Datasets:")
        for ds in datasets:
            print(f"- {ds['name']}")
    except Exception as e:
        print(f"Failed to list datasets: {str(e)}")

    # Example dataset creation (commented out as it needs actual CSV)
    # try:
    #     result = dataset_manager.create_from_csv(
    #         csv_path='data/sample.csv',
    #         dataset_name='SampleQuestions',
    #         schema_mapping={
    #             'question': 'text',
    #             'answer': 'text',
    #             'category': 'label'
    #         }
    #     )
    #     print(f"\nDataset created: {result}")
    # except Exception as e:
    #     print(f"Dataset creation failed: {str(e)}")

if __name__ == "__main__":
    # Before running: Set environment variables RAGAAI_ACCESS_KEY and RAGAAI_SECRET_KEY
    main()