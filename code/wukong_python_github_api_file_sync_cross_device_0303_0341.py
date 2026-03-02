#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: openwrt_build_helper.py
Created from: Actions-OpenWrt repository (https://github.com/zszszszsz/.config)
Creation Date: 2023-04-01
Description: 
    A helper script to automate OpenWrt build process using GitHub Actions.
    Mimics core functionality described in README:
    - Configures OpenWrt build environment
    - Generates .config file
    - Triggers GitHub Actions build process
"""

import os
import subprocess
import shutil
import argparse
from datetime import datetime
import requests

def setup_build_environment():
    """Setup OpenWrt build environment by cloning Lean's OpenWrt repo."""
    print("Setting up build environment...")
    if not os.path.exists("lede"):
        subprocess.run(["git", "clone", "https://github.com/coolsnowwolf/lede.git"], check=True)
    os.chdir("lede")
    
    print("Updating feeds...")
    subprocess.run(["./scripts/feeds", "update", "-a"], check=True)
    subprocess.run(["./scripts/feeds", "install", "-a"], check=True)

def generate_config():
    """Generate OpenWrt .config file using menuconfig."""
    print("\nStarting menuconfig...")
    print("Please configure your build options. Save and exit when done.")
    subprocess.run(["make", "menuconfig"], check=True)
    
    # Copy generated config
    config_path = "../openwrt.config"
    shutil.copyfile(".config", config_path)
    print(f"\nConfiguration saved to: {config_path}")
    return config_path

def trigger_github_actions(repo, config_path, token=None):
    """Trigger GitHub Actions build by pushing config to repo."""
    print(f"\nPreparing to push config to {repo}")
    
    # Initialize temp git repo
    temp_dir = "openwrt_build_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Clone repo and add config
    subprocess.run(["git", "clone", f"https://github.com/{repo}.git", temp_dir], check=True)
    shutil.copy(config_path, os.path.join(temp_dir, ".config"))
    
    # Commit and push
    os.chdir(temp_dir)
    subprocess.run(["git", "add", ".config"], check=True)
    subprocess.run(["git", "commit", "-m", f"Build config {datetime.now().isoformat()}"], check=True)
    
    if token:
        auth_url = f"https://{token}@github.com/{repo}.git"
        subprocess.run(["git", "remote", "set-url", "origin", auth_url], check=True)
    
    subprocess.run(["git", "push"], check=True)
    print(f"\nBuild triggered on {repo}. Check GitHub Actions page.")

def main():
    parser = argparse.ArgumentParser(description="OpenWrt Build Automation Helper")
    parser.add_argument("-g", "--generate", action="store_true", help="Generate new .config file")
    parser.add_argument("-t", "--trigger", metavar="REPO", help="GitHub repo (user/repo) to trigger build")
    parser.add_argument("--token", help="GitHub token for private repos (optional)")
    args = parser.parse_args()
    
    try:
        if args.generate:
            setup_build_environment()
            config = generate_config()
            print("\nConfig generation complete.")
            
            if args.trigger:
                trigger_github_actions(args.trigger, config, args.token)
        
        elif args