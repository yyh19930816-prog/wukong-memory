#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil 核心功能实现
从 giampaolo/psutil GitHub 仓库学习 (https://github.com/giampaolo/psutil)
实现日期: 2023-10-26
功能描述: 展示系统进程和系统资源使用情况的核心功能
"""

import psutil
import time
from datetime import datetime

def get_system_info():
    """
    获取基础系统信息
    
    返回格式化的系统信息字符串
    """
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    cpu_count = psutil.cpu_count(logical=False)  # 物理核心数
    cpu_count_logical = psutil.cpu_count(logical=True)  # 逻辑核心数
    
    info = f"""
=== 系统信息 ===
启动时间: {boot_time}
物理CPU核心数: {cpu_count}
逻辑CPU核心数: {cpu_count_logical}
系统平台: {psutil.os_info().pretty_name()}
    """
    return info.strip()

def get_cpu_usage():
    """
    获取CPU使用情况
    
    返回格式化的CPU使用率信息字符串
    """
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    avg_percent = sum(cpu_percent) / len(cpu_percent)
    
    info = f"""
=== CPU使用情况 ===
平均使用率: {avg_percent:.1f}%
各核心使用率:
"""
    for i, percent in enumerate(cpu_percent):
        info += f"  核心 {i}: {percent:.1f}%\n"
    
    return info.strip()

def get_memory_info():
    """
    获取内存使用情况
    
    返回格式化的内存信息字符串
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    info = f"""
=== 内存使用情况 ===
物理内存:
  总量: {mem.total / (1024**3):.2f} GB
  已使用: {mem.used / (1024**3):.2f} GB ({mem.percent}%)
  可用: {mem.available / (1024**3):.2f} GB
交换内存:
  总量: {swap.total / (1024**3):.2f} GB
  已使用: {swap.used / (1024**3):.2f} GB ({swap.percent}%)
"""
    return info.strip()

def get_processes(top_n=5):
    """
    获取占用资源最多的进程
    
    Args:
        top_n: 返回前N个进程
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except psutil.NoSuchProcess:
            pass
    
    # 按CPU使用率排序
    cpu_sorted = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:top_n]
    # 按内存使用率排序
    mem_sorted = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:top_n]
    
    cpu_info = "=== CPU占用最高的进程 ===\n"
    for i, p in enumerate(cpu_sorted, 1):
        cpu_info += f"{i}. PID: {p['pid']} {p['name']}: {p['cpu_percent']:.1f}%\n"
    
    mem_info = "\n=== 内存占用最高的进程 ===\n"
    for i, p in enumerate