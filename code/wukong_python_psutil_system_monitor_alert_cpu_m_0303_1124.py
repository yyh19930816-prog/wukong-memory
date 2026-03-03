#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil 核心功能演示脚本
学习来源：giampaolo/psutil GitHub仓库 (https://github.com/giampaolo/psutil)
创建日期：2023-11-20
功能描述：展示psutil库的核心功能，包括CPU、内存、磁盘、网络、进程等系统信息监控
"""

import psutil
import time
from datetime import datetime

def get_cpu_info():
    """获取CPU相关信息"""
    print("\n===== CPU信息 =====")
    # CPU逻辑数量
    print(f"逻辑CPU数量: {psutil.cpu_count()}")
    # CPU物理核心
    print(f"物理核心数: {psutil.cpu_count(logical=False)}")
    # CPU使用率(每隔1秒采样1次，共采样3次)
    print("CPU使用率采样:")
    for i, percent in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
        print(f"  CPU {i}: {percent}%")
    # CPU频率
    cpufreq = psutil.cpu_freq()
    print(f"当前频率: {cpufreq.current:.2f}MHz (最大: {cpufreq.max:.2f}MHz)")

def get_memory_info():
    """获取内存相关信息"""
    print("\n===== 内存信息 =====")
    # 系统内存
    svmem = psutil.virtual_memory()
    print(f"总内存: {svmem.total / (1024**3):.2f} GB")
    print(f"可用内存: {svmem.available / (1024**3):.2f} GB")
    print(f"已使用内存: {svmem.used / (1024**3):.2f} GB ({svmem.percent}%)")
    # 交换内存
    swap = psutil.swap_memory()
    print(f"交换内存: 使用{swap.used / (1024**3):.2f}GB/{swap.total / (1024**3):.2f}GB ({swap.percent}%)")

def get_disk_info():
    """获取磁盘相关信息"""
    print("\n===== 磁盘信息 =====")
    # 磁盘分区
    print("磁盘分区:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"  设备: {partition.device}, 挂载点: {partition.mountpoint}, 文件系统: {partition.fstype}")
    # 磁盘使用情况
    disk_usage = psutil.disk_usage('/')
    print(f"根分区使用情况: {disk_usage.used / (1024**3):.2f}GB/{disk_usage.total / (1024**3):.2f}GB ({disk_usage.percent}%)")
    # 磁盘IO
    disk_io = psutil.disk_io_counters()
    print(f"磁盘IO: 读{disk_io.read_bytes / (1024**2):.2f}MB, 写{disk_io.write_bytes / (1024**2):.2f}MB")

def get_network_info():
    """获取网络相关信息"""
    print("\n===== 网络信息 =====")
    # 网络接口
    net_io = psutil.net_io_counters()
    print(f"发送: {net_io.bytes_sent / (1024**2):.2f}MB, 接收: {net_io.bytes_recv / (1024**2):.2f}MB")
    # 网络连接
    print("\n网络