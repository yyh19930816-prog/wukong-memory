#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: OpenWrt Builder Helper
Description: Python implementation of core functions from Actions-OpenWrt repo
Features:
  - Generate OpenWrt .config file
  - Trigger GitHub Actions workflow
  - Download built artifacts
Learning Source: GitHub zszszszsz/.config README
Date: 2023-11-20
"""

import os
import sys
import shutil
import subprocess
import requests
from pathlib import Path

# Configuration
GH_USERNAME = "your_github_username"
GH_TOKEN = "your_github_token"
LEDE_REPO = "https://github.com/coolsnowwolf/lede.git"
WORKFLOW_FILE = ".github/workflows/build-openwrt.yml"
CONFIG_TEMPLATE = """
CONFIG_TARGET_x86=y
CONFIG_TARGET_x86_64=y
"""

def clone_lede_repo():
    """Clone Lean's OpenWrt source code repository"""
    print("Cloning LEDE repository...")
    try:
        subprocess.run(["git", "clone", "--depth=1", LEDE_REPO, "lede"], check=True)
        os.chdir("lede")
        print("LEDE repository cloned successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        sys.exit(1)

def generate_config():
    """Generate OpenWrt .config file"""
    print("Generating .config file...")
    try:
        # Run initial setup commands
        subprocess.run(["./scripts/feeds", "update", "-a"], check=True)
        subprocess.run(["./scripts/feeds", "install", "-a"], check=True)
        
        # Create minimal config
        with open(".config", "w") as f:
            f.write(CONFIG_TEMPLATE)
        
        print(".config file generated")
    except Exception as e:
        print(f"Error generating config: {e}")
        sys.exit(1)

def upload_to_github(repo_name):
    """Push config to GitHub repository"""
    print(f"Uploading to GitHub repository {repo_name}...")
    try:
        # Initialize new git repo
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", ".config"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial OpenWrt config"], check=True)
        
        # Create remote repo via GitHub API
        headers = {
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {"name": repo_name, "auto_init": False}
        r = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=data
        )
        r.raise_for_status()
        
        # Push to GitHub
        remote_url = f"https://{GH_TOKEN}@github.com/{GH_USERNAME}/{repo_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        subprocess.run(["git", "push", "-u", "origin", "master"], check=True)
        
        print("Config pushed to GitHub successfully")
    except Exception as e:
        print(f"Error uploading to GitHub: {e}")
        sys.exit(1)

def main():
    if not GH_TOKEN or not GH_USERNAME:
        print("Please set GH_TOKEN and GH_USERNAME variables")
        sys.exit(1)
    
    repo_name = input("Enter name for new GitHub repository: ")
    
    # Prepare clean workspace
    if os.path.exists("lede