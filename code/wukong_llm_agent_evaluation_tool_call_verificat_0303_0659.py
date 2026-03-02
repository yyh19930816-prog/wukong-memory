#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RagaAI Catalyst Python SDK Demo Script
Source: raga-ai-hub/RagaAI-Catalyst GitHub repository (https://github.com/raga-ai-hub/RagaAI-Catalyst)
Date: [Current Date]
Description: Demonstrates core features of RagaAI Catalyst including project management,
             dataset handling, and synthetic data generation with proper authentication.
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os

def main():
    # Configuration - Replace with your actual credentials
    config = {
        "access_key": os.getenv("RAGA_ACCESS_KEY", "your_access_key"),
        "secret_key": os.getenv("RAGA_SECRET_KEY", "your_secret_key"),
        "base_url": os.getenv("RAGA_BASE_URL", "https://api.raga.ai"),
        "project_name": "Demo-RAG-App",
        "usecase": "Question Answering"
    }

    try:
        # Initialize RagaAI Catalyst client
        print("Initializing RagaAI Catalyst client...")
        catalyst = RagaAICatalyst(
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            base_url=config["base_url"]
        )

        # Project Management Demo
        print("\n--- Project Management ---")
        # Create new project
        project = catalyst.create_project(
            project_name=config["project_name"],
            usecase=config["usecase"]
        )
        print(f"Created project: {project}")

        # List all projects
        projects = catalyst.list_projects()
        print("\nAvailable Projects:")
        for idx, proj in enumerate(projects, 1):
            print(f"{idx}. {proj['name']} ({proj['usecase']})")

        # Dataset Management Demo
        print("\n--- Dataset Management ---")
        dataset_manager = Dataset(project_name=config["project_name"])

        # List datasets (likely empty initially)
        datasets = dataset_manager.list_datasets()
        print("\nExisting Datasets:")
        print(datasets if datasets else "No datasets found")

        # Example: How to create dataset from CSV (commented out as it requires actual file)
        """
        dataset_manager.create_from_csv(
            csv_path='sample_data.csv',
            dataset_name='DemoDataset',
            schema_mapping={'question': 'input', 'answer': 'output'}
        )
        print("Dataset created from CSV")
        """

        # Synthetic Data Generation Demo
        print("\n--- Synthetic Data Generation ---")
        # Example prompt template for synthetic data
        synthetic_config = {
            "prompt_template": "Generate a question about {topic}",
            "parameters": {"topic": "machine learning"},
            "num_samples": 3
        }
        print(f"Would generate synthetic data with config: {synthetic_config}")
        # Actual generation would use:
        # synthetic_data = catalyst.generate_synthetic_data(**synthetic_config)

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Please check your credentials and network connection")

if __name__ == "__main__":
    main()