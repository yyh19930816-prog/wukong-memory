#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RagaAI Catalyst Python Client Implementation
Source: https://github.com/raga-ai-hub/RagaAI-Catalyst
Date: August 2023
Description: Demonstrates core functionality of RagaAI Catalyst including project management,
dataset operations and basic configurations. Requires valid API credentials.
"""

import os
from ragaai_catalyst import RagaAICatalyst, Dataset

def main():
    # Initialize RagaAI Catalyst with your credentials (replace with actual values)
    # Recommended: Set these as environment variables in production
    catalyst = RagaAICatalyst(
        access_key=os.getenv("RAGA_ACCESS_KEY", "your_access_key"),
        secret_key=os.getenv("RAGA_SECRET_KEY", "your_secret_key"),
        base_url=os.getenv("RAGA_BASE_URL", "https://api.raga.ai")
    )

    # Project Management Examples
    try:
        # 1. Create a new project
        print("\n--- Project Management ---")
        new_project = catalyst.create_project(
            project_name="CustomerSupportBot",
            usecase="Chatbot"
        )
        print(f"Created project: {new_project}")

        # 2. List available use cases
        use_cases = catalyst.project_use_cases()
        print("\nAvailable use cases:")
        for case in use_cases:
            print(f"- {case}")

        # 3. List all projects
        projects = catalyst.list_projects()
        print("\nExisting projects:")
        for project in projects:
            print(f"- {project['name']} (ID: {project['id']})")

    except Exception as e:
        print(f"Project management error: {str(e)}")

    # Dataset Management Examples
    try:
        print("\n--- Dataset Management ---")
        # Initialize dataset manager for our project
        dataset = Dataset(project_name="CustomerSupportBot")

        # 1. List existing datasets
        datasets = dataset.list_datasets()
        print("Existing datasets:")
        for ds in datasets:
            print(f"- {ds['name']}")

        # Note: In a real scenario, you would provide actual CSV file path and schema mapping
        # Example dataset creation (commented out as it requires actual files):
        """
        dataset.create_from_csv(
            csv_path='customer_queries.csv',
            dataset_name='SupportQueries',
            schema_mapping={
                'question': 'user_input',
                'response': 'model_output',
                'rating': 'feedback_score'
            }
        )
        """
        print("\nNote: Uncomment dataset creation code with actual file paths")

    except Exception as e:
        print(f"Dataset management error: {str(e)}")

    print("\nDemo completed. See official docs for advanced features.")

if __name__ == "__main__":
    # Check for minimal configuration
    if os.getenv("RAGA_ACCESS_KEY") is None:
        print("Warning: Running with demo credentials. Set RAGA_ACCESS_KEY and RAGA_SECRET_KEY environment variables for production use.")
    main()