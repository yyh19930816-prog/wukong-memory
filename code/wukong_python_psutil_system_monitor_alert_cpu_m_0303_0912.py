#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# psutil_example.py
# Based on giampaolo/psutil (https://github.com/giampaolo/psutil)
# Created: 2023-04-01
# 
# A demonstration of core psutil functionality showing how to retrieve:
# - System-wide CPU and memory usage
# - Process information (running processes, CPU/memory per process)
# - Disk and network statistics

import psutil
import time

def display_system_info():
    """Display system-wide CPU and memory usage information."""
    print("\n=== System Information ===")
    
    # CPU usage
    print(f"CPU Usage (%): {psutil.cpu_percent(interval=1)}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
    
    # Memory usage
    mem = psutil.virtual_memory()
    print(f"\nMemory:")
    print(f"  Total: {mem.total / (1024**3):.2f} GB")
    print(f"  Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
    print(f"  Available: {mem.available / (1024**3):.2f} GB")
    
    # Swap memory
    swap = psutil.swap_memory()
    print(f"\nSwap:")
    print(f"  Total: {swap.total / (1024**3):.2f} GB")
    print(f"  Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)")

def display_processes():
    """Display running processes information."""
    print("\n=== Running Processes ===")
    
    # Get all process IDs
    pids = psutil.pids()
    print(f"Total processes running: {len(pids)}\n")
    
    # Display top 5 CPU consuming processes
    print("Top 5 CPU consuming processes:")
    processes = []
    for pid in pids:
        try:
            p = psutil.Process(pid)
            processes.append((p.cpu_percent(interval=0.1), pid, p.name()))
        except psutil.NoSuchProcess:
            continue
    
    # Sort and display top processes
    for cpu_percent, pid, name in sorted(processes, reverse=True)[:5]:
        print(f"  PID:{pid} {name} - {cpu_percent:.1f}% CPU")

def display_disk_network():
    """Display disk and network statistics."""
    print("\n=== Disk & Network ===")
    
    # Disk partitions and usage
    print("\nDisk Partitions:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        print(f"  {partition.device} ({partition.fstype}):"
              f" Total:{usage.total / (1024**3):.1f}GB"
              f" Used:{usage.percent}%")
    
    # Network I/O
    print("\nNetwork Statistics:")
    net_io = psutil.net_io_counters()
    print(f"  Bytes Sent: {net_io.bytes_sent / (1024**2):.1f} MB")
    print(f"  Bytes Received: {net_io.bytes_recv / (1024**2):.1f} MB")

if __name__ == "__main__":
    print("psutil Demonstration Script")
    print("--------------------------")
    
    while True: