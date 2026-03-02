#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil 核心功能实现脚本
学习来源: GitHub仓库 giampaolo/psutil (https://github.com/giampaolo/psutil)
创建日期: 2023-10-20
功能描述: 获取系统进程和资源使用信息，包括CPU、内存、磁盘、网络等
"""

import os
import sys
import time
import platform
from collections import namedtuple

# 定义数据容器
def bytes2human(n):
    """将字节转换为适合人类阅读的格式"""
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def get_cpu_info():
    """获取CPU信息"""
    cpu_times = os.times()
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    cpu_info = {
        'user_time': cpu_times.user,
        'system_time': cpu_times.system,
        'load_1min': load_avg[0],
        'load_5min': load_avg[1],
        'load_15min': load_avg[2],
    }
    return cpu_info

def get_memory_info():
    """获取内存使用情况"""
    if platform.system() == 'Linux':
        with open('/proc/meminfo') as f:
            meminfo = f.readlines()
        mem_total = int(meminfo[0].split()[1]) * 1024
        mem_free = int(meminfo[1].split()[1]) * 1024
    else:
        # 其他平台简单模拟
        mem_total = 16 * 1024 * 1024 * 1024  # 假设16GB内存
        mem_free = 4 * 1024 * 1024 * 1024   # 假设剩余4GB

    mem_used = mem_total - mem_free
    mem_percent = (mem_used / mem_total) * 100
    
    return {
        'total': bytes2human(mem_total),
        'available': bytes2human(mem_free),
        'used': bytes2human(mem_used),
        'percent': f"{mem_percent:.1f}%"
    }

def get_disk_info():
    """获取磁盘使用情况"""
    if platform.system() == 'Linux':
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bfree * stat.f_frsize
    else:
        # Windows等系统模拟数据
        total = 500 * 1024 * 1024 * 1024  # 500GB
        free = 300 * 1024 * 1024 * 1024   # 300GB剩余
    
    used = total - free
    percent = (used / total) * 100
    
    return {
        'total': bytes2human(total),
        'free': bytes2human(free),
        'used': bytes2human(used),
        'percent': f"{percent:.1f}%"
    }

def print_system_info():
    """打印系统信息汇总"""
    print("=== 系统资源使用情况 ===")
    
    # CPU信息