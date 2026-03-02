#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil核心功能实现脚本
学习来源: GitHub仓库 giampaolo/psutil (https://github.com/giampaolo/psutil)
创建日期: 2023年11月15日
功能描述: 实现系统进程和系统资源信息监控的核心功能，包括CPU、内存、磁盘、网络和进程信息查询
"""

import os
import time
import psutil  # 需要先安装: pip install psutil

def get_cpu_info():
    """获取CPU相关信息"""
    print("\n=== CPU信息 ===")
    # 获取CPU逻辑数量
    print(f"逻辑CPU数量: {psutil.cpu_count()}")
    # 获取CPU物理核心数
    print(f"物理核心数: {psutil.cpu_count(logical=False)}")
    # 获取CPU使用率(3秒内的平均使用率)
    print(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")
    # 获取每个CPU核心的使用率
    print(f"每个核心使用率: {psutil.cpu_percent(interval=1, percpu=True)}")

def get_memory_info():
    """获取内存相关信息"""
    print("\n=== 内存信息 ===")
    mem = psutil.virtual_memory()
    # 总内存(GB)
    print(f"总内存: {mem.total / (1024 ** 3):.2f} GB")
    # 可用内存(GB)
    print(f"可用内存: {mem.available / (1024 ** 3):.2f} GB")
    # 已用内存百分比
	print(f"内存使用率: {mem.percent}%")
    # 交换分区信息
    swap = psutil.swap_memory()
    print(f"交换分区使用率: {swap.percent}%")

def get_disk_info():
    """获取磁盘相关信息"""
    print("\n=== 磁盘信息 ===")
    # 获取磁盘分区信息
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"\n分区: {partition.device}")
        print(f"挂载点: {partition.mountpoint}")
        print(f"文件系统类型: {partition.fstype}")
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"总大小: {usage.total / (1024 ** 3):.2f} GB")
            print(f"使用率: {usage.percent}%")
        except PermissionError:
            print("权限不足，无法访问")

def get_network_info():
    """获取网络相关信息"""
    print("\n=== 网络信息 ===")
    # 获取网络IO计数
    net_io = psutil.net_io_counters()
    print(f"发送字节: {net_io.bytes_sent / (1024 ** 2):.2f} MB")
    print(f"接收字节: {net_io.bytes_recv / (1024 ** 2):.2f} MB")
    # 获取网络连接信息
    print("\n网络连接:")
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr and conn.raddr:
            print(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port} ({conn.status})")

def get_process_info():
    """获取进程相关信息"""
    print("\n=== 进程信息 ===")
    # 获取当前运行的所有进程ID
    pids = psutil.pids()
    print(f"总进程数: {len