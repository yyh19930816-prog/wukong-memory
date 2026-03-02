#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Learning Source: GitHub repository amoffat/sh (https://github.com/amoffat/sh)
Date: [Current Date]
Description: Demonstrate core functionality of sh module - a Python subprocess
             replacement that allows calling shell commands as if they were functions.
             This script shows basic usage, error handling, command piping and streaming.
"""

import sh
from sh import (  # Import specific commands directly
    ls,          # List directory contents
    grep,        # Search text
    whoami,      # Show current user
    ping,        # Network diagnostic tool
    echo,        # Print text
)


def main():
    """Showcase the main features of the sh module."""
    # Basic command execution
    print("\n=== Basic Command Execution ===")
    print("Current user:", whoami().strip())  # strip() removes trailing newline

    # Listing files in current directory
    print("\nFiles in current directory:")
    print(ls("-l"))  # Pass arguments directly like in shell

    # Error handling demonstration
    try:
        # This will fail intentionally (directory doesn't exist)
        ls("/nonexistent/directory")
    except sh.ErrorReturnCode as e:
        print(f"\nCommand failed with exit code {e.exit_code}")
        print("Error output:", e.stderr.decode().strip())

    # Command piping (ls | grep .py)
    print("\nPython files in directory:")
    print(grep(ls("-1"), ".py"))

    # Streaming output example (ping Google)
    print("\nStreaming ping output (press Ctrl+C to stop):")
    try:
        # Use _out=_print to stream output line by line
        for line in ping("google.com", "-c", 5, _iter=True):
            print(line.strip())
    except KeyboardInterrupt:
        print("\nPing stopped by user")

    # Getting command output properties
    print("\n=== Command Output Properties ===")
    cmd = echo("Hello World!")
    print("Command exit code:", cmd.exit_code)
    print("Command stdout:", cmd.stdout.decode().strip())

    # Background processes
    print("\nStarting background process (sleep 3)...")
    bg_process = sh.sleep("3", _bg=True)
    print(f"Process PID: {bg_process.pid}")
    bg_process.wait()
    print("Background process finished")


if __name__ == "__main__":
    # Check if running on Unix-like OS (sh doesn't work on Windows)
    import sys
    import os

    if os.name != "posix":
        print("Error: sh module only works on Unix-like systems")
        sys.exit(1)

    try:
        import sh
    except ImportError:
        print("Error: sh module not installed. Install with: pip install sh")
        sys.exit(1)

    main()