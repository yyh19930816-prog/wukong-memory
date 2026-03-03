#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
psutil - 系统进程和系统利用率(CPU, 内存, 磁盘等)监控工具
学习来源: https://github.com/giampaolo/psutil
创建日期: 2023-10-25
功能描述: 实现系统进程查询和系统资源监控的基本功能
"""

import psutil
import time
from datetime import datetime

def get_system_info():
    """获取系统基本信息"""
    print("\n===== 系统基本信息 =====")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"系统启动时间: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"系统运行时间: {str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))}")

def get_cpu_info():
    """获取CPU使用情况"""
    print("\n===== CPU信息 =====")
    # 获取CPU逻辑数量
    print(f"CPU逻辑数量: {psutil.cpu_count()}")
    # 获取CPU物理核心数量
    print(f"CPU物理核心数量: {psutil.cpu_count(logical=False)}")
    # 获取CPU使用率(3秒间隔)
    print(f"CPU使用率: {psutil.cpu_percent(interval=3)}%")
    # 获取每个CPU的使用率
    print("每个CPU的使用率:")
    for i, percent in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
        print(f"  CPU {i}: {percent}%")

def get_memory_info():
    """获取内存使用情况"""
    print("\n===== 内存信息 =====")
    mem = psutil.virtual_memory()
    # 总内存 (GB)
    print(f"总内存: {mem.total / (1024 ** 3):.2f} GB")
    # 已使用内存 (GB)
    print(f"已使用内存: {mem.used / (1024 ** 3):.2f} GB")
    # 内存使用率
    print(f"内存使用率: {mem.percent}%")

def get_disk_info():
    """获取磁盘使用情况"""
    print("\n===== 磁盘信息 =====")
    # 获取磁盘分区信息
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"\n设备: {partition.device}")
        print(f"挂载点: {partition.mountpoint}")
        print(f"文件系统类型: {partition.fstype}")
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"总大小: {usage.total / (1024 ** 3):.2f} GB")
            print(f"已使用: {usage.used / (1024 ** 3):.2f} GB")
            print(f"使用率: {usage.percent}%")
        except PermissionError:
            print("权限不足，无法访问")

def get_process_info(limit=5):
    """获取进程信息"""
    print("\n===== 进程信息(按CPU使用率排序) =====")
    # 按CPU使用率排序进程
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append((proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # 排序并显示前limit个