#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil demo implementation
学习来源：https://github.com/giampaolo/psutil
日期：2023-11-21
功能描述：本脚本实现了psutil的核心功能，用于监控系统进程和系统利用率（CPU、内存、磁盘等）
"""

import psutil
import time
from datetime import datetime

def get_system_info():
    """获取并打印基本的系统信息"""
    print("\n=== 系统基本信息 ===")
    print(f"系统启动时间: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前用户: {psutil.users()[0].name}")
    print(f"CPU核心数: {psutil.cpu_count(logical=False)} (物理), {psutil.cpu_count()} (逻辑)")

def monitor_cpu(interval=1):
    """监控CPU使用情况"""
    print("\n=== CPU使用情况 ===")
    print(f"当前CPU使用率: {psutil.cpu_percent(interval=interval)}%")
    print(f"每个CPU核心使用率: {psutil.cpu_percent(interval=interval, percpu=True)}")

def monitor_memory():
    """监控内存使用情况"""
    print("\n=== 内存使用情况 ===")
    mem = psutil.virtual_memory()
    print(f"总内存: {mem.total/1024/1024:.2f} MB")
    print(f"可用内存: {mem.available/1024/1024:.2f} MB")
    print(f"使用比例: {mem.percent}%")

def monitor_disk():
    """监控磁盘使用情况"""
    print("\n=== 磁盘使用情况 ===")
    disk = psutil.disk_usage('/')
    print(f"总空间: {disk.total/1024/1024/1024:.2f} GB")
    print(f"可用空间: {disk.free/1024/1024/1024:.2f} GB")
    print(f"使用比例: {disk.percent}%")

def monitor_network():
    """监控网络IO"""
    print("\n=== 网络IO ===")
    net_io = psutil.net_io_counters()
    print(f"发送: {net_io.bytes_sent/1024/1024:.2f} MB")
    print(f"接收: {net_io.bytes_recv/1024/1024:.2f} MB")

def list_processes(top_n=5):
    """列出消耗资源最多的进程"""
    print("\n=== 消耗资源最多的进程 ===")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    
    # 按CPU排序
    print("\nTop CPU进程:")
    for proc in sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:top_n]:
        print(f"PID:{proc['pid']} {proc['name']}: CPU {proc['cpu_percent']}%")
    
    # 按内存排序
    print("\nTop 内存进程:")
    for proc in sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:top_n]:
        print(f"PID:{proc['pid']} {proc['name']}: 内存 {proc['memory_percent']}%")

def main():
    """主函数"""
    try:
        get_system_info()
        monitor_cpu()
        monitor_memory()
        monitor_disk()
        monitor_network()