#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: psutil_demo.py
Description: Demo script showing psutil core functionality - system process monitoring
Based on: giampaolo/psutil GitHub repository (https://github.com/giampaolo/psutil)
Date: 2023-11-20
Features:
  - Get system process information
  - Monitor CPU, memory, disk, network usage
  - List running processes
"""

import psutil
import time

def get_system_info():
    """Show basic system information using psutil"""
    print("\n===== System Information =====")
    
    # CPU Info
    print(f"CPU Cores (Physical): {psutil.cpu_count(logical=False)}")
    print(f"CPU Cores (Logical): {psutil.cpu_count(logical=True)}")
    print(f"CPU Usage (%): {psutil.cpu_percent(interval=1)}")
    
    # Memory Info
    mem = psutil.virtual_memory()
    print(f"\nTotal Memory: {mem.total / (1024**3):.2f} GB")
    print(f"Available Memory: {mem.available / (1024**3):.2f} GB")
    print(f"Memory Used (%): {mem.percent}")
    
    # Disk Info
    disk = psutil.disk_usage('/')
    print(f"\nTotal Disk Space: {disk.total / (1024**3):.2f} GB")
    print(f"Free Disk Space: {disk.free / (1024**3):.2f} GB")
    print(f"Disk Used (%): {disk.percent}")
    
    # Network Info
    net_io = psutil.net_io_counters()
    print(f"\nBytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB")
    print(f"Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB")

def list_processes(limit=5):
    """List top running processes sorted by CPU usage"""
    print("\n===== Running Processes (Top by CPU) =====")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    
    # Sort by CPU usage descending
    processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:limit]
    
    print(f"{'PID':<8}{'Name':<25}{'CPU %':<8}{'RAM %':<8}")
    for p in processes:
        print(f"{p['pid']:<8}{p['name']:<25}{p['cpu_percent']:<8.1f}{p['memory_percent']:<8.1f}")

def monitor_system(duration=5):
    """Monitor system resources for given duration"""
    print(f"\n===== Monitoring System Resources for {duration} seconds =====")
    print(f"{'Time':<8}{'CPU %':<8}{'Memory %':<10}{'Disk %':<8}{'Network (MB/s)'}")
    
    prev_net = psutil.net_io_counters()
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # CPU
        cpu = psutil.cpu_percent(interval=1)
        
        # Memory
        mem = psutil.virtual_memory().percent
        
        # Disk
        disk = psutil.disk_usage('/').percent
        
        # Network
        curr_net = psutil.net_io_count