#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RagaAI Catalyst Integration Script
Learn Source: GitHub raga-ai-hub/RagaAI-Catalyst (https://github.com/raga-ai-hub/ragaai-catalyst)
Date: 2023-11-15
Description: Demonstrates core functionalities of RagaAI Catalyst including project management,
dataset operations, and basic setup. Requires valid authentication keys.
"""

import os
from ragaai_catalyst import RagaAICatalyst, Dataset

def main():
    # Configuration (Replace with your actual credentials)
    config = {
        "access_key": os.getenv("RAGAAI_ACCESS_KEY", "your_access_key"),
        "secret_key": os.getenv("RAGAAI_SECRET_KEY", "your_secret_key"),
        "base_url": os.getenv("RAGAAI_BASE_URL", "https://api.ragaai-catalyst.com"),
        "project_name": "Demo-RAG-App",
        "usecase": "Question Answering"
    }

    try:
        # Initialize Catalyst client
        print("Initializing RagaAI Catalyst client...")
        catalyst = RagaAICatalyst(
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            base_url=config["base_url"]
        )

        # Project Management Demo
        print("\n=== Project Management ===")
        
        # Create new project
        print(f"Creating project: {config['project_name']}")
        project = catalyst.create_project(
            project_name=config["project_name"],
            usecase=config["usecase"]
        )
        print(f"Project created: {project}")

        # List all available use cases
        print("\nAvailable use cases:")
        use_cases = catalyst.project_use_cases()
        print(use_cases)

        # Dataset Management Demo
        print("\n=== Dataset Management ===")
        dataset_manager = Dataset(project_name=config["project_name"])

        # List datasets (empty initially)
        print("\nListing datasets:")
        datasets = dataset_manager.list_datasets()
        print(datasets)

        print("\nDemo completed successfully!")
    
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Please verify your credentials and network connection.")

if __name__ == "__main__":
    main()