#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: sh_demo.py
Author: Wukong
Date: 2024-01-28
Description: 
学习自 GitHub 仓库 amoffat/sh (https://github.com/amoffat/sh) 
展示如何使用 sh 库作为子进程替换方案来调用系统命令，
示例包括基本的命令调用、参数传递和输出处理。
"""

import sh
from sh import git, ls, echo, whoami

def demo_basic_commands():
    """演示基本的 sh 命令调用"""
    print("=== 基本命令调用示例 ===")
    
    # 调用 ls 命令并打印输出
    print("\n1. 当前目录内容:")
    print(ls())
    
    # 调用 ls 命令带 -l 参数
    print("\n2. 带参数的长列表格式:")
    print(ls("-l"))
    
    # 调用 whoami 显示当前用户
    print("\n3. 当前登录用户:")
    print(whoami())

def demo_piping():
    """演示命令管道操作"""
    print("\n=== 命令管道示例 ===")
    
    # 使用 echo 和 grep 管道查找包含'Python'的行
    print("\n1. 管道 grep 过滤:")
    cmd = echo("Python\nJava\nGo\nPython\nC++") | grep("Python")
    print(cmd)

def demo_git_commands():
    """演示 git 命令调用"""
    print("\n=== Git 命令示例 ===")
    
    try:
        # 获取 git 状态
        print("\n1. Git 仓库状态:")
        print(git.status())
        
        # 获取 git 日志 (带限制参数)
        print("\n2. 最近3条Git日志:")
        print(git.log("-n", "3", "--oneline"))
    except sh.ErrorReturnCode as e:
        print(f"Git命令出错: {e}")

def demo_background_process():
    """演示后台进程调用"""
    print("\n=== 后台进程示例 ===")
    
    print("\n1. 启动后台进程:")
    bg_process = echo("后台输出", _bg=True)
    print("后台进程已启动...等待2秒")
    
    import time
    time.sleep(2)
    print(f"\n后台进程结果: {bg_process.wait()}")

if __name__ == "__main__":
    # 演示各种 sh 功能
    demo_basic_commands()
    demo_piping()
    demo_git_commands()
    demo_background_process()
    
    print("\n所有演示完成!")