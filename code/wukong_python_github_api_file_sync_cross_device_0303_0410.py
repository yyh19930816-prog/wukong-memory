#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions-OpenWrt Automation Script
学习来源: https://github.com/zszszszsz/.config
创建日期: 2023-04-01
功能描述: 自动化构建OpenWrt固件，模拟GitHub Actions的核心功能
         1. 克隆OpenWrt源码 2. 加载配置文件 3. 编译固件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

# 配置常量
OPENWRT_REPO = "https://github.com/coolsnowwolf/lede"
BUILD_DIR = Path("openwrt_build")
CONFIG_FILE = ".config"
LOG_FILE = "build.log"

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='OpenWrt自动化构建脚本')
    parser.add_argument('-c', '--config', help='指定.config配置文件路径', required=True)
    parser.add_argument('-o', '--output', help='输出目录', default='bin')
    return parser.parse_args()

def clone_repo():
    """克隆OpenWrt源码仓库"""
    print(f"正在克隆OpenWrt源码: {OPENWRT_REPO}")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    if subprocess.call(["git", "clone", "--depth=1", OPENWRT_REPO, BUILD_DIR]) != 0:
        print("错误: 克隆仓库失败")
        sys.exit(1)

def copy_config(config_path):
    """复制配置文件到构建目录"""
    target = BUILD_DIR / CONFIG_FILE
    print(f"正在复制配置文件到: {target}")
    try:
        shutil.copy(config_path, target)
    except IOError as e:
        print(f"错误: 复制配置文件失败 - {e}")
        sys.exit(1)

def prepare_build():
    """准备构建环境"""
    print("准备构建环境...")
    os.chdir(BUILD_DIR)
    
    # 更新feeds
    if subprocess.call("./scripts/feeds update -a", shell=True) != 0:
        print("错误: feeds更新失败")
        sys.exit(1)
        
    if subprocess.call("./scripts/feeds install -a", shell=True) != 0:
        print("错误: feeds安装失败")
        sys.exit(1)

def build_openwrt(output_dir):
    """编译OpenWrt固件"""
    print("开始编译OpenWrt...")
    # 使用多线程编译 (-j参数根据CPU核心数调整)
    cpu_count = os.cpu_count() or 2
    cmd = f"make -j{cpu_count} V=s"
    
    with open(LOG_FILE, 'w') as log:
        process = subprocess.Popen(
            cmd, shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                log.write(output)
                
        retcode = process.poll()
        if retcode != 0:
            print(f"错误: 编译失败，详情请查看{LOG_FILE}")
            sys.exit(retcode)

    # 复制输出文件
    print("编译完成，处理输出文件...")
    bin_dir = Path("bin/targets")
    if not bin_dir.exists():
        print("错误: 未找到编译输出目录")
        sys.exit(1)
        
    output_path = Path(output_dir)
    output_path.mkdir