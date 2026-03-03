#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
脚本名称: openwrt_build_helper.py
学习来源: https://github.com/zszszszsz/.config
创建日期: 2023-12-27
功能描述: GitHub Actions自动构建OpenWrt固件的简化版本
           1. 下载Lean's OpenWrt源码
           2. 处理自定义.config配置文件
           3. 自动化构建流程
'''

import os
import sys
import subprocess
import argparse
from typing import Optional

class OpenWRTBuilder:
    def __init__(self, config_path: str, output_dir: str = "bin"):
        """
        初始化构建器
        :param config_path: .config文件路径
        :param output_dir: 输出目录
        """
        self.config_path = config_path
        self.output_dir = output_dir
        self.repo_url = "https://github.com/coolsnowwolf/lede.git"
        self.repo_dir = "lede"

    def clone_source(self) -> bool:
        """克隆Lean's OpenWrt源码仓库"""
        print(f"正在克隆源码仓库: {self.repo_url}")
        try:
            subprocess.run(["git", "clone", self.repo_url], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"克隆失败: {e}")
            return False

    def update_feeds(self) -> bool:
        """更新feeds包"""
        print("正在更新feeds...")
        try:
            subprocess.run(["./scripts/feeds", "update", "-a"], 
                         cwd=self.repo_dir, check=True)
            subprocess.run(["./scripts/feeds", "install", "-a"], 
                         cwd=self.repo_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"更新feeds失败: {e}")
            return False

    def apply_config(self) -> bool:
        """应用自定义配置文件"""
        if not os.path.exists(self.config_path):
            print(f"错误: 配置文件不存在 {self.config_path}")
            return False
            
        print(f"应用配置文件: {self.config_path}")
        try:
            destination = os.path.join(self.repo_dir, ".config")
            os.replace(self.config_path, destination)
            return True
        except OSError as e:
            print(f"应用配置失败: {e}")
            return False

    def make_defconfig(self) -> bool:
        """生成默认配置"""
        print("生成默认配置...")
        try:
            subprocess.run(["make", "defconfig"], 
                         cwd=self.repo_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"生成配置失败: {e}")
            return False

    def build_firmware(self, threads: int = 4) -> bool:
        """
        构建固件
        :param threads: 编译线程数
        """
        print(f"开始构建固件 (使用 {threads} 线程)...")
        try:
            env = os.environ.copy()
            env["JOBS"] = str(threads)
            subprocess.run(["make", "-j", str(threads)], 
                         cwd=self.repo_dir, env=env, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"构建失败: {e}")
            return False

    def run(self):
        """执行完整构建流程"""
        steps = [
            self.clone_source,
            self.update_feeds,
            self.apply_config,
            self.make_defconfig,
            self.build_firmware
        ]