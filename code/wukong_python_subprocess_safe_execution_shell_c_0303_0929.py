#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sh 模块示例脚本

学习来源: GitHub仓库 amoffat/sh (https://github.com/amoffat/sh)
日期: 2023-11-15
功能描述:
- 演示sh模块核心功能：像调用函数一样执行系统命令
- 包含基本命令执行、参数传递、输出捕获等示例
- 错误处理演示
- 注意：此脚本只能在Unix-like系统运行(Linux/macOS/BSD等)
"""

import sys
import sh
from sh import git, ls, echo, whoami  # 导入常用命令作为可调用函数

def main():
    # 示例1: 基本命令执行 - 列出当前目录
    print("=== 示例1: 执行ls命令 ===")
    try:
        ls_result = ls("-l")  # 相当于在终端执行 'ls -l'
        print("当前目录内容:")
        print(ls_result)
    except sh.ErrorReturnCode as e:
        print(f"命令执行失败: {e}")

    # 示例2: 带参数的命令执行 - 获取git版本
    print("\n=== 示例2: 带参数执行 ===")
    try:
        git_version = git("--version")  # 相当于 'git --version'
        print(f"Git版本: {git_version.strip()}")
    except sh.CommandNotFound:
        print("错误: git未安装或不在PATH中")

    # 示例3: 获取命令输出 - 获取当前用户名
    print("\n=== 示例3: 获取命令输出 ===")
    try:
        username = whoami()  # 相当于 'whoami'
        print(f"当前用户: {username.strip()}")
    except Exception as e:
        print(f"获取用户名错误: {e}")

    # 示例4: 管道操作 - 组合命令
    print("\n=== 示例4: 管道操作 ===")
    try:
        # 相当于 'echo "hello world" | wc -w'
        word_count = echo("hello world") | sh.wc("-w")
        print(f"单词数: {word_count.strip()}")
    except Exception as e:
        print(f"管道操作失败: {e}")

    # 示例5: 带环境变量的命令
    print("\n=== 示例5: 带环境变量的命令 ===")
    try:
        # 设置环境变量后执行命令
        result = sh.env("PYTHONPATH=/usr/local/bin", "echo", "$PYTHONPATH")
        print(f"环境变量PYTHONPATH: {result}")
    except Exception as e:
        print(f"带环境变量的命令失败: {e}")

    # 示例6: 后台执行命令
    print("\n=== 示例6: 后台执行命令 ===")
    try:
        bg_process = sh.sleep("10", _bg=True)  # 后台执行sleep 10
        print(f"后台进程PID: {bg_process.pid}")
        print("主程序继续执行...")
        bg_process.wait()  # 等待后台进程完成
        print("后台进程已完成")
    except Exception as e:
        print(f"后台执行失败: {e}")

    # 示例7: 命令超时处理
    print("\n=== 示例7: 超时处理 ===")
    try:
        # 设置2秒超时
        result = sh.sleep("5", _timeout=2)
        print(result)
    except sh.TimeoutException:
        print("命令执行超时!")
    except Exception as e:
        print(f"命令执行出错: {e}