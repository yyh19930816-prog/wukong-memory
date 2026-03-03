#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Actions-OpenWrt 自动化构建脚本
学习来源: GitHub 仓库 zszszszsz/.config (https://github.com/zszszszsz/.config)
创建日期: 2023-04-01
功能描述: 模拟 GitHub Actions 自动化构建 OpenWrt 固件流程
         包含配置生成、自动构建和固件下载功能
"""

import os
import sys
import subprocess
import shutil
import time
import requests
from typing import Optional, List

class OpenWrtBuilder:
    def __init__(self, config_file: str = ".config"):
        """
        初始化构建器
        :param config_file: OpenWrt 配置文件路径
        """
        self.config_file = config_file
        self.work_dir = os.path.join(os.getcwd(), "openwrt_build")
        self.lede_dir = os.path.join(self.work_dir, "lede")
        self.build_log = os.path.join(self.work_dir, "build.log")
        
    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> bool:
        """
        执行 shell 命令
        :param command: 命令列表
        :param cwd: 工作目录
        :return: 是否成功
        """
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd or self.work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            with open(self.build_log, "a") as log_file:
                for line in process.stdout:
                    log_file.write(line)
                    print(line, end="")
            return process.wait() == 0
        except Exception as e:
            print(f"执行命令失败: {e}")
            return False

    def _clone_repo(self, repo_url: str) -> bool:
        """
        克隆 OpenWrt 源码仓库
        :param repo_url: 仓库地址
        :return: 是否成功
        """
        if os.path.exists(self.lede_dir):
            print("检测到已存在的源码目录，跳过克隆...")
            return True
            
        print(f"正在克隆源码仓库: {repo_url}")
        return self._run_command(["git", "clone", "--depth=1", repo_url, self.lede_dir])

    def _generate_config(self) -> bool:
        """
        生成 OpenWrt 配置文件
        :return: 是否成功
        """
        print(f"使用配置文件: {self.config_file}")
        
        if not os.path.exists(self.config_file):
            print("找不到配置文件，使用默认配置...")
            return self._run_command(["make", "defconfig"], self.lede_dir)
            
        print("应用自定义配置...")
        shutil.copy(self.config_file, os.path.join(self.lede_dir, ".config"))
        return self._run_command(["make", "defconfig"], self.lede_dir)

    def _build_firmware(self) -> bool:
        """
        编译 OpenWrt 固件
        :return: 是否成功
        """
        print("开始编译固件...")
        # 多线程编译 (建议根据系统CPU核心数调整)
        thread_num = os.cpu_count() or 2
        return self._run_command(["make", f"-j{thread_num}", "download", "world"], self.lede_dir)

    def _package_firmware(self) -> bool:
        """
        打包编译好的固件
        :return: 是否成功
        """
        print("打包固件...")
        firmware_dir = os.path.join