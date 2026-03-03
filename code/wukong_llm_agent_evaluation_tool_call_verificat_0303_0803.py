#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RagaAI Catalyst Client Implementation
Learned from: https://github.com/raga-ai-hub/RagaAI-Catalyst
Date: 2023-11-20
Description: Demonstrates core functionalities of RagaAI Catalyst including:
    - Project management (creation, listing)
    - Dataset operations (listing, creation from CSV)
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os

# Configuration - Replace with your actual credentials
CONFIG = {
    "access_key": os.getenv("RAGA_ACCESS_KEY", "your_access_key"),
    "secret_key": os.getenv("RAGA_SECRET_KEY", "your_secret_key"),
    "base_url": os.getenv("RAGA_BASE_URL", "https://api.raga.ai"),
    "project_name": "Demo-RAG-App",
    "usecase": "Information Retrieval",
    "test_csv_path": "sample_data.csv"  # Path to your test CSV file
}

def initialize_client():
    """Initialize RagaAI Catalyst client with authentication"""
    try:
        catalyst = RagaAICatalyst(
            access_key=CONFIG["access_key"],
            secret_key=CONFIG["secret_key"],
            base_url=CONFIG["base_url"]
        )
        print("Successfully initialized RagaAI Catalyst client")
        return catalyst
    except Exception as e:
        print(f"Failed to initialize client: {str(e)}")
        return None

def demo_project_management(catalyst):
    """Demonstrate project management operations"""
    if not catalyst:
        return
        
    try:
        # Create new project
        print("\nCreating project...")
        project = catalyst.create_project(
            project_name=CONFIG["project_name"],
            usecase=CONFIG["usecase"]
        )
        print(f"Created project: {project}")
        
        # List available project use cases
        print("\nAvailable use cases:")
        use_cases = catalyst.project_use_cases()
        print(use_cases)
        
        # List all projects
        print("\nListing all projects:")
        projects = catalyst.list_projects()
        for p in projects:
            print(f"- {p['name']} ({p['usecase']})")
            
    except Exception as e:
        print(f"Project management error: {str(e)}")

def demo_dataset_management(catalyst):
    """Demonstrate dataset management operations"""
    if not catalyst:
        return
        
    try:
        # Initialize dataset manager
        dataset_manager = Dataset(project_name=CONFIG["project_name"])
        
        # List existing datasets
        print("\nListing datasets:")
        datasets = dataset_manager.list_datasets()
        print(datasets)
        
        # Create dataset from CSV (if sample file exists)
        if os.path.exists(CONFIG["test_csv_path"]):
            print("\nCreating dataset from CSV...")
            result = dataset_manager.create_from_csv(
                csv_path=CONFIG["test_csv_path"],
                dataset_name="demo_dataset",
                schema_mapping={  # Example mapping - adjust based on your CSV
                    "question": "query",
                    "answer": "response"
                }
            )
            print("Dataset creation result:", result)
        else:
            print(f"\nCSV file not found: {CONFIG['test_csv_path']}")
            
    except Exception as e:
        print(f"Dataset management error: {str(e)}")

def main():
    """Main execution function"""
    print("RagaAI Catalyst Demo")
    
    # Initialize client
    catalyst = initialize_client()
    
    # Demonstrate features
    demo_project_management(catalyst)
    demo_dataset_management(catalyst)

if __name__ == "__main__":