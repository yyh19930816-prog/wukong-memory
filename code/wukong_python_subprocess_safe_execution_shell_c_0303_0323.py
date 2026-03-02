#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script Name: sh_example.py
Created By: You
Creation Date: 2023-10-25
Description: Demonstrates core functionality of 'sh' Python module - executing shell commands as Python functions
Source: Learned from amoffat/sh GitHub repository (https://github.com/amoffat/sh)
Required Packages: sh (install via 'pip install sh')
"""

from sh import (
    ls,      # Unix ls command
    git,     # Git version control
    python3, # Python interpreter
    echo,    # Display text
    whoami,  # Show current user
    uname,   # Print system information
    df,      # Disk space usage
    ErrorReturnCode  # Exception for non-zero exit codes
)

def demonstrate_sh_basics():
    """Show basic usage of sh module"""
    try:
        # Running simple commands - each command is callable like a function
        print("\n=== Running Basic Commands ===")
        print("Current directory contents:")
        print(ls("-l"))  # Equivalent to 'ls -l' in terminal
        
        print("\nSystem information:")
        print(uname("-a"))  # Print all system info
        
        print("\nCurrent user:")
        print(whoami())
        
    except ErrorReturnCode as e:
        print(f"Command failed: {e}")

def demonstrate_piping():
    """Show command chaining/piping"""
    print("\n=== Command Chaining/Piping ===")
    # Chain commands together with pipe operator |
    print("Disk usage for root filesystem:")
    print(df("-h") | grep("/dev/root"))

def demonstrate_git_integration():
    """Demonstrate using git through sh"""
    print("\n=== Git Integration ===")
    try:
        # Git commands work the same way
        print("Git version:")
        print(git("--version"))
        
        # Commands with dashes become underscores
        print("\nGit config --list:")
        print(git.config("--list"))
        
    except ErrorReturnCode as e:
        print(f"Git command failed: {e}")

def demonstrate_python_interaction():
    """Show interacting with Python process"""
    print("\n=== Python Interaction ===")
    # Run Python code through sh's python command
    print("Python version:")
    print(python3("--version"))
    
    # Pass Python code via -c flag
    print("\nSimple math calculation:")
    print(python3("-c", "print(42 * 42)"))

def demonstrate_background_processes():
    """Show running commands in background"""
    print("\n=== Background Processes ===")
    # Start echo command in background (doesn't block)
    bg_process = echo("This will print", _bg=True)
    print("Command started in background...")
    
    # Wait for process to complete
    bg_process.wait()
    print("Background process finished")

if __name__ == "__main__":
    # Execute demonstration functions
    demonstrate_sh_basics()
    demonstrate_piping()
    demonstrate_git_integration()
    demonstrate_python_interaction()
    demonstrate_background_processes()
    
    print("\nAll demonstrations complete!")