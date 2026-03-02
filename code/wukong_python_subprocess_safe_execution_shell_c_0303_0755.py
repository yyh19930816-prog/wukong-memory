#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 学习来源：GitHub仓库 amoffat/sh (https://github.com/amoffat/sh)
# 创建日期：2023-11-20
# 功能描述：演示使用sh库调用系统命令的几种常见方式
# 该库可将系统命令作为Python函数调用，是subprocess的高级封装

import sh  # 必须安装: pip install sh

def demonstrate_basic_commands():
    """演示基本命令执行"""
    # 执行系统命令ls -l
    print("\n=== 执行ls -l命令 ===")
    print(sh.ls("-l"))  # 就像调用普通函数一样调用系统命令

    # 执行ifconfig(Unix)或ipconfig(Windows的替代方法)
    try:
        print("\n=== 执行ifconfig命令 ===")
        print(sh.ifconfig())
    except sh.CommandNotFound:
        print("ifconfig命令不存在, 尝试ip命令")
        print(sh.ip("addr"))


def demonstrate_command_piping():
    """演示命令管道操作"""
    print("\n=== 命令管道示例 ===")
    # 使用管道符|组合多个命令
    res = sh.ps("-aux") | sh.grep("python") | sh.wc("-l")
    print(f"当前运行的Python进程数量: {res}")


def demonstrate_command_with_options():
    """演示带选项的命令执行"""
    print("\n=== 带选项的命令执行 ===")
    # 通过函数参数传递命令选项
    print("\n执行du -h -d 1:")
    print(sh.du("-h", "-d", "1"))

    # 更简单的参数传递方式
    print("\n执行du -h -d 1(简化方式):")
    print(sh.du("-h -d 1", _iter=True))  # _iter=True逐行输出


def demonstrate_background_execution():
    """演示后台执行命令"""
    print("\n=== 后台执行命令 ===")
    # _bg=True让命令在后台执行
    p = sh.sleep(3, _bg=True)
    print("后台任务正在执行...")
    p.wait()  # 等待后台任务完成
    print("后台任务已完成")


def demonstrate_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理 ===")
    try:
        # 执行一个不存在的命令
        sh.nonexistent_command()
    except sh.CommandNotFound as e:
        print(f"命令未找到错误: {e}")

    try:
        # 执行返回非零状态码的命令
        sh.ls("/nonexistent_path")
    except sh.ErrorReturnCode as e:
        print(f"命令执行失败, 退出码: {e.exit_code}")
        print(f"完整输出:\n{e.stdout.decode()}")


if __name__ == "__main__":
    # 注意: 此脚本只能在Unix-like系统(Linux, macOS等)上运行
    print("sh库使用演示 - 可以像函数一样调用系统命令\n")
    
    demonstrate_basic_commands()
    demonstrate_command_piping()
    demonstrate_command_with_options()
    demonstrate_background_execution()
    demonstrate_error_handling()

    print("所有演示完成!")