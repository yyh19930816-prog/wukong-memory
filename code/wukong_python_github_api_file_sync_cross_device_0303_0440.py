#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions-OpenWrt Automation Tool
Learned from: https://github.com/zszszszsz/.config (P3TERX/Actions-OpenWrt)
Date: 2023-11-20
Description: Automates OpenWrt build process using GitHub Actions API
             - Creates config file
             - Triggers build workflow
             - Downloads artifacts
"""

import os
import sys
import json
import time
import requests
from getpass import getpass
from urllib.parse import urljoin

# GitHub API settings
GITHUB_API_URL = "https://api.github.com"
WORKFLOW_FILE = "build-openwrt.yml"
ARTIFACT_NAME = "openwrt_firmware"

def get_auth_token():
    """Get GitHub personal access token"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = getpass("Enter GitHub Personal Access Token: ")
    return token

def get_repo_info():
    """Get repository information from user"""
    print("Enter repository details (owner/repo):")
    owner = input("Owner/Organization: ").strip()
    repo = input("Repository name: ").strip()
    branch = input("Branch name (default: master): ").strip() or "master"
    return owner, repo, branch

def trigger_workflow(token, owner, repo, branch):
    """Trigger GitHub Actions workflow"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    
    payload = {
        "ref": branch,
        "inputs": {
            "build_config": "true"  # Triggers config generation
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Build workflow triggered successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error triggering workflow: {e}")
        return False

def check_workflow_status(token, owner, repo):
    """Check if workflow has completed"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/runs"
    
    print("Waiting for workflow completion...", end="")
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            runs = response.json()["workflow_runs"]
            
            if runs and runs[0]["status"] == "completed":
                print("\nWorkflow completed!")
                return runs[0]["conclusion"] == "success"
            
            time.sleep(30)
            print(".", end="", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"\nError checking workflow status: {e}")
            return False

def download_artifacts(token, owner, repo):
    """Download workflow artifacts"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    artifacts_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/artifacts"
    
    try:
        response = requests.get(artifacts_url, headers=headers)
        response.raise_for_status()
        artifacts = response.json()["artifacts"]
        
        for artifact in artifacts:
            if