#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions-OpenWrt Automation Script
Learn from: https://github.com/zszszszsz/.config
Created: 2023-11-20
Function: Automate OpenWrt build process using GitHub Actions API
Features:
1. Detect existing config file in repo
2. Trigger GitHub Actions workflow
3. Monitor build progress
4. Download artifacts when complete
"""

import os
import time
import requests
from github import Github  # PyGithub library

class OpenWrtBuilder:
    def __init__(self, token, repo_name):
        """
        Initialize OpenWrt builder with GitHub token and repo name
        :param token: GitHub personal access token
        :param repo_name: format "username/repo"
        """
        self.token = token
        self.repo_name = repo_name
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_name)
        
    def check_config(self):
        """Check if .config file exists in repo root"""
        try:
            contents = self.repo.get_contents(".config")
            print("Found existing .config file")
            return True
        except:
            print("No .config file found in repository")
            return False
    
    def trigger_build(self):
        """Dispatch workflow to trigger GitHub Actions build"""
        # The workflow file should be named 'build-openwrt.yml'
        workflow = self.repo.get_workflow("build-openwrt.yml")
        
        print("Triggering OpenWrt build workflow...")
        workflow.create_dispatch("main")  # Trigger on main branch
        
    def monitor_build(self, timeout=3600):
        """
        Monitor build progress with timeout
        :param timeout: max wait time in seconds (default 1 hour)
        """
        start_time = time.time()
        print("Monitoring build progress...")
        
        while time.time() - start_time < timeout:
            runs = self.repo.get_workflow_runs().get_page(0)
            if not runs:
                print("No workflow runs found")
                return False
                
            latest_run = runs[0]
            status = latest_run.status
            conclusion = latest_run.conclusion
            
            if status == "completed":
                if conclusion == "success":
                    print("Build completed successfully!")
                    return True
                else:
                    print(f"Build failed with status: {conclusion}")
                    return False
                    
            print(f"Current status: {status} (elapsed: {int(time.time()-start_time)}s)")
            time.sleep(30)  # Check every 30 seconds
            
        print("Build monitoring timeout reached")
        return False
    
    def download_artifacts(self, output_dir="artifacts"):
        """
        Download build artifacts from latest successful run
        :param output_dir: local directory to save artifacts
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the latest successful workflow run
        runs = self.repo.get_workflow_runs(status="success").get_page(0)
        if not runs:
            print("No successful workflow runs found")
            return
            
        latest_run = runs[0]
        artifacts = latest_run.get_artifacts()
        
        if artifacts.totalCount == 0:
            print("No artifacts found for this run")
            return
            
        print(f"Downloading {artifacts.totalCount} artifact(s)...")
        for artifact in artifacts:
            download_url = artifact.archive_download_url
            # GitHub API requires auth header
            headers = {"Authorization": f"token {self.token}"}
            response = requests.get(download_url, headers=headers, stream=True)
            
            if response.status_code == 200: