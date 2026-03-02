#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Actions OpenWrt Builder Automation Script

Description:
This script automates the process of building OpenWrt firmware using GitHub Actions,
mimicking the functionality described in P3TERX/Actions-OpenWrt repository.

Features:
- Creates GitHub repository from template
- Handles .config file generation/upload
- Triggers build workflow
- Monitors build progress

Learning Source:
https://github.com/zszszszsz/.config/blob/master/README.md

Created: 2023-11-08
"""

import os
import sys
import time
import json
import requests
from github import Github  # PyGithub library

# Configuration - fill these with your details
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # GitHub personal access token
TEMPLATE_REPO = "P3TERX/Actions-OpenWrt"  # Template repository
USERNAME = "your_github_username"  # Your GitHub username
CONFIG_FILE = "openwrt.config"  # Path to your OpenWrt config file


def create_repository_from_template():
    """
    Create a new repository from the Actions-OpenWrt template
    Returns the new repository object
    """
    try:
        gh = Github(GITHUB_TOKEN)
        user = gh.get_user(USERNAME)
        template_repo = gh.get_repo(TEMPLATE_REPO)
        
        # Create new repo from template
        repo_name = f"openwrt-build-{int(time.time())}"
        new_repo = user.create_repo_from_template(
            repo_name,
            template_repo,
            description="Automated OpenWrt build repository"
        )
        print(f"Created new repository: {new_repo.full_name}")
        return new_repo
    except Exception as e:
        print(f"Error creating repository: {str(e)}")
        sys.exit(1)


def upload_config_file(repo, config_path):
    """
    Upload OpenWrt .config file to the repository
    """
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        repo.create_file(
            path=".config",
            message="Add OpenWrt configuration",
            content=str(config_content),
            branch="master"
        )
        print("Successfully uploaded .config file")
    except Exception as e:
        print(f"Error uploading config file: {str(e)}")
        sys.exit(1)


def monitor_build_progress(repo):
    """
    Monitor the GitHub Actions workflow progress
    """
    print("Monitoring build progress...")
    while True:
        workflows = repo.get_workflow_runs()
        latest_run = workflows[0]
        
        if latest_run.status == 'completed':
            if latest_run.conclusion == 'success':
                print("Build completed successfully!")
                artifacts = latest_run.get_artifacts()
                if artifacts:
                    print(f"Artifacts available: {artifacts[0].archive_download_url}")
                else:
                    print("No artifacts found")
            else:
                print(f"Build failed: {latest_run.conclusion}")
            break
        
        print(f"Current status: {latest_run.status}...")
        time.sleep(60)  # Check every minute


def main():
    # Verify config file exists
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Config file {CONFIG_FILE} not found")
        sys.exit(1)
    
    # Create new repository from template
    new_repo = create_repository_from_template()
    
    # Upload config file to trigger build
    upload_config_file(new_repo, CONFIG_FILE)
    
    # Monitor build progress