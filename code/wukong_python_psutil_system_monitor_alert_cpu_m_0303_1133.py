#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
psutil功能示例脚本
学习来源: giampaolo/psutil GitHub仓库
日期: 2023-11-15
功能描述: 演示psutil库的核心功能，包括获取系统信息、进程管理等
"""

import psutil
import time

def get_system_info():
    """获取并打印系统基本信息"""
    # CPU信息
    print(f"CPU核心数: {psutil.cpu_count(logical=False)}物理/{psutil.cpu_count()}逻辑")
    print(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")

    # 内存信息
    mem = psutil.virtual_memory()
    print(f"内存总量: {mem.total / (1024**3):.2f}GB")
    print(f"内存使用率: {mem.percent}%")

    # 磁盘信息
    disk = psutil.disk_usage('/')
    print(f"磁盘总量: {disk.total / (1024**3):.2f}GB")
    print(f"磁盘使用率: {disk.percent}%")

def monitor_processes():
    """监控并显示进程信息"""
    print("\n当前运行中的进程:")
    
    # 获取所有进程信息
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.as_dict()
            if info['cpu_percent'] > 0 or info['memory_percent'] > 1:
                print(f"PID: {info['pid']:<6} Name: {info['name']:<15} "
                      f"CPU: {info['cpu_percent']:.1f}% "
                      f"MEM: {info['memory_percent']:.1f}%")
        except psutil.NoSuchProcess:
            pass

def network_info():
    """获取网络连接信息"""
    print("\n网络连接信息:")
    conns = psutil.net_connections(kind='inet')
    for conn in conns[:5]:  # 显示前5个连接
        print(f"类型: {conn.type} 本地: {conn.laddr} 远程: {conn.raddr} "
              f"状态: {conn.status}")

def battery_info():
    """获取电池信息(如果可用)"""
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            print(f"\n电池电量: {battery.percent}%")
            print(f"电源状态: {'插电' if battery.power_plugged else '电池供电'}")

def main():
    """主函数"""
    print("------ PSUTIL 系统监控演示 ------\n")
    
    # 演示各个功能
    get_system_info()
    monitor_processes()
    network_info()
    battery_info()
    
    print("\n------ 监控结束 ------\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断操作")