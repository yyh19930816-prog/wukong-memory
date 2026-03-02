#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions-OpenWrt Build Automation Script
Inspired by: https://github.com/zszszszsz/.config
Date: 2023-11-20
Description: Automates the OpenWrt build process with GitHub Actions API
Features:
- Interact with GitHub API to trigger builds
- Download built artifacts
- Basic error handling
"""

import os
import requests
import json
import time
from urllib.parse import urljoin

GITHUB_API_BASE = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "X-GitHub-Api-Version": "2022-11-28"
}

def trigger_workflow(repo_owner, repo_name, workflow_id="build.yml"):
    """Trigger GitHub Actions workflow for OpenWrt build"""
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
    
    payload = {
        "ref": "master",  # Default branch
        "inputs": {
            "config_source": "default"  # Can be modified per need
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Workflow triggered successfully for {repo_owner}/{repo_name}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error triggering workflow: {str(e)}")
        return False

def download_artifact(artifact_url, download_path="."):
    """Download built OpenWrt artifacts"""
    try:
        # First get the artifact download URL
        response = requests.get(artifact_url, headers=HEADERS)
        response.raise_for_status()
        download_url = response.json()["archive_download_url"]
        
        # Download the actual artifact zip file
        response = requests.get(download_url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        artifact_name = os.path.join(download_path, "openwrt_artifact.zip")
        with open(artifact_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Artifact downloaded to: {artifact_name}")
        return artifact_name
    except requests.exceptions.RequestException as e:
        print(f"Error downloading artifact: {str(e)}")
        return None

def check_build_status(repo_owner, repo_name):
    """Poll GitHub Actions to check build completion"""
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/actions/runs"
    
    print("Waiting for build to complete...", end="")
    for _ in range(30):  # Max 30 checks (30 minutes with sleep)
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            runs = response.json()["workflow_runs"]
            
            if runs and runs[0]["status"] == "completed":
                print("\nBuild completed!")
                return runs[0]["conclusion"], runs[0]["artifacts_url"]
            
            print(".", end="", flush=True)
            time.sleep(60)  # Check every minute
        except requests.exceptions.RequestException:
            print("Error checking build status")
            return None, None
    
    print("\nBuild timeout reached")
    return None, None

def main():
    """Main execution function"""
    repo_owner = input("