#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sh模块演示脚本
学习来源: GitHub仓库 amoffat/sh (https://github.com/amoffat/sh)
创建日期: <当前日期>
功能描述: 演示sh模块的核心功能 - 将系统命令作为Python函数调用
"""

import sh
from sh import git, ls, ifconfig  # 导入特定命令作为函数
import sys

def demonstrate_basic_commands():
    """演示基本命令调用"""
    try:
        # 1. ls命令 - 列出当前目录
        print("\n=== ls命令演示 ===")
        print("当前目录内容:")
        print(ls("-l"))  # 等同于运行 'ls -l'
        
        # 2. git命令 - 显示版本
        print("\n=== git命令演示 ===")
        print("Git版本:")
        print(git("--version"))
        
    except sh.ErrorReturnCode as e:
        print(f"命令执行失败: {e}", file=sys.stderr)

def demonstrate_command_piping():
    """演示命令管道"""
    try:
        print("\n=== 命令管道演示 ===")
        # 使用管道将find命令输出传递给wc命令
        file_count = sh.wc(sh.find(".", "-name", "*.py"), "-l")
        print(f"当前目录下Python文件数量: {file_count.strip()}")
        
    except sh.ErrorReturnCode as e:
        print(f"管道命令执行失败: {e}", file=sys.stderr)

def demonstrate_background_process():
    """演示后台进程"""
    try:
        print("\n=== 后台进程演示 ===")
        # 启动长时间运行的进程在后台
        sleep_process = sh.sleep(3, _bg=True)
        print("启动了一个3秒的后台sleep进程，主程序继续执行...")
        
        # 检查进程是否完成
        print("检查sleep进程是否完成...")
        print(f"完成状态: {'是' if sleep_process.done else '否'}")
        sleep_process.wait()  # 等待进程完成
        print("sleep进程现在已完成")
        
    except sh.ErrorReturnCode as e:
        print(f"后台进程错误: {e}", file=sys.stderr)

def demonstrate_network_info():
    """演示网络信息获取"""
    try:
        print("\n=== 网络信息演示 ===")
        # 获取网络接口信息
        if "eth0" in sh.ifconfig():
            print("eth0接口信息:")
            print(ifconfig("eth0"))
        else:
            print("找不到eth0接口，改用lo:")
            print(ifconfig("lo"))
            
    except sh.ErrorReturnCode as e:
        print(f"网络命令错误: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("=== sh模块功能演示 ===")
    
    # 检查操作系统是否为Unix-like
    if not hasattr(sh, "_is_unix"):
        print("错误: sh只能在Unix-like系统上运行", file=sys.stderr)
        sys.exit(1)
    
    demonstrate_basic_commands()
    demonstrate_command_piping()
    demonstrate_background_process()
    demonstrate_network_info()
    
    print("\n演示完成!")