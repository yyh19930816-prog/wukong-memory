#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions-OpenWrt Automation Script
Learn from: https://github.com/zszszszsz/.config
Date: 2023-11-20
Function: Automate OpenWrt build process using GitHub Actions API
"""
import os
import time
import requests
from typing import Optional

class OpenWrtBuilder:
    """
    A class to automate OpenWrt builds using GitHub Actions API.
    Implements core functionalities described in README.
    """
    
    def __init__(self, github_token: str, repo_name: str = "Actions-OpenWrt"):
        """
        Initialize with GitHub token and repository name.
        
        Args:
            github_token: Personal access token for GitHub API
            repo_name: Name of the target repository (default: Actions-OpenWrt)
        """
        self.token = github_token
        self.repo = repo_name
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def fork_repository(self) -> bool:
        """
        Fork the repository using GitHub API.
        
        Returns:
            bool: True if fork succeeded, False otherwise
        """
        url = f"{self.api_base}/repos/P3TERX/{self.repo}/forks"
        try:
            response = requests.post(url, headers=self.headers)
            return response.status_code == 202
        except Exception as e:
            print(f"Fork failed: {e}")
            return False
    
    def upload_config(self, config_file: str) -> bool:
        """
        Upload OpenWrt .config file to repository.
        
        Args:
            config_file: Path to local .config file
            
        Returns:
            bool: True if upload succeeded, False otherwise
        """
        if not os.path.exists(config_file):
            print("Config file not found")
            return False
            
        url = f"{self.api_base}/repos/{self.headers['Authorization'].split(' ')[2]}/{self.repo}/contents/.config"
        
        with open(config_file, 'r') as f:
            content = f.read()
            
        data = {
            "message": "Add OpenWrt config",
            "content": content.encode('ascii').hex()
        }
        
        try:
            response = requests.put(url, json=data, headers=self.headers)
            return response.status_code == 201
        except Exception as e:
            print(f"Upload failed: {e}")
            return False
    
    def trigger_build(self) -> Optional[str]:
        """
        Trigger GitHub Actions workflow run.
        
        Returns:
            str: Workflow run ID if successful, None otherwise
        """
        url = f"{self.api_base}/repos/{self.headers['Authorization'].split(' ')[2]}/{self.repo}/actions/workflows/build.yml/dispatches"
        data = {"ref": "master"}
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 204:
                # Small delay to get the run ID
                time.sleep(2)
                runs_url = f"{self.api_base}/repos/{self.headers['Authorization'].split(' ')[2]}/{self.repo}/actions/runs"
                runs_resp = requests.get(runs_url, headers=self.headers)
                return runs_resp.json()['workflow_runs'][0]['id']
            return None
        except Exception as e:
            print(f"Trigger failed: {e}")
            return None
    
    def check_build_status(self, run_id: str) -> str:
        """
        Check build status of a workflow