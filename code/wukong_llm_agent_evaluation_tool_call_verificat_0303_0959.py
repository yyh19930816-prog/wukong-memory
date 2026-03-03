#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RagaAI Catalyst API Usage Example
Learning Source: https://github.com/raga-ai-hub/RagaAI-Catalyst
Created: 2023-11-15
Description: Demonstrates core functionalities of RagaAI Catalyst including project management,
             dataset operations, and basic evaluation setup.
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os
import pandas as pd
from io import StringIO

# Configuration - Replace with your actual credentials
CONFIG = {
    "access_key": os.getenv("RAGA_ACCESS_KEY", "your_access_key"),
    "secret_key": os.getenv("RAGA_SECRET_KEY", "your_secret_key"),
    "base_url": os.getenv("RAGA_BASE_URL", "https://api.raga.ai"),
    "project_name": "Demo-Chatbot-App",
    "usecase": "Chatbot"
}

def setup_catalyst():
    """Initialize RagaAI Catalyst client with authentication"""
    try:
        catalyst = RagaAICatalyst(
            access_key=CONFIG["access_key"],
            secret_key=CONFIG["secret_key"],
            base_url=CONFIG["base_url"]
        )
        print("Successfully connected to RagaAI Catalyst")
        return catalyst
    except Exception as e:
        print(f"Failed to initialize RagaAI Catalyst: {e}")
        return None

def manage_project(catalyst):
    """Demonstrate project management operations"""
    try:
        # Create new project
        project = catalyst.create_project(
            project_name=CONFIG["project_name"],
            usecase=CONFIG["usecase"]
        )
        print(f"Created project: {project}")

        # List all projects
        projects = catalyst.list_projects()
        print(f"\nAll Projects:\n{projects}")
        
        return True
    except Exception as e:
        print(f"Project operation failed: {e}")
        return False

def manage_datasets():
    """Show dataset management functionality"""
    try:
        dataset_manager = Dataset(project_name=CONFIG["project_name"])
        
        # Create sample CSV dataset
        csv_data = StringIO("""question,answer
What is Python?,A programming language
What is RagaAI Catalyst?,An LLM evaluation platform""")
        
        # Create dataset from CSV
        dataset_manager.create_from_csv(
            csv_path=csv_data,
            dataset_name="Sample-QA",
            schema_mapping={
                'question': 'user_query',
                'answer': 'model_response'
            }
        )
        print("Successfully created dataset from CSV")

        # List datasets
        datasets = dataset_manager.list_datasets()
        print(f"\nAvailable Datasets:\n{datasets}")
        
        return True
    except Exception as e:
       print(f"Dataset operation failed: {e}")
        return False

def main():
    """Main execution flow"""
    # Initialize client
    catalyst = setup_catalyst()
    if not catalyst:
        return

    # Project operations
    if not manage_project(catalyst):
        return

    # Dataset operations
    if not manage_datasets():
        return

    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()