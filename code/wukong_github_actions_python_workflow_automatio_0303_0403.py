#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup-python 功能模拟实现
学习来源: GitHub actions/setup-python@v6
日期: 2023-10-20
功能描述: 模拟实现 GitHub Actions setup-python 的核心功能，包括:
- Python/PyPy/GraalPy 版本安装
- 添加到系统PATH
- 依赖缓存功能模拟
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional

class PythonInstaller:
    """模拟 setup-python 的核心功能类"""
    
    def __init__(self):
        self.python_versions_dir = os.path.expanduser("~/.python/versions")
        self.cache_dir = os.path.expanduser("~/.cache/pip")
        self.original_path = os.environ.get("PATH", "")
        
    def install_python(self, version: str) -> bool:
        """
        模拟安装指定版本的Python
        Args:
            version: Python版本号 (如 '3.13', 'pypy3.10')
        Returns:
            bool: 是否安装成功
        """
        # 创建模拟的版本目录
        version_dir = os.path.join(self.python_versions_dir, version)
        os.makedirs(version_dir, exist_ok=True)
        
        # 创建模拟的python可执行文件
        bin_dir = os.path.join(version_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        python_exec = "pypy3" if "pypy" in version else "python3"
        
        with open(os.path.join(bin_dir, python_exec), "w") as f:
            f.write("#!/bin/sh\necho 'Python simulator running!'\n")
        os.chmod(os.path.join(bin_dir, python_exec), 0o755)
        
        # 添加到PATH
        os.environ["PATH"] = f"{bin_dir}:{self.original_path}"
        print(f"🔧 Installed Python {version} and added to PATH")
        return True
    
    def setup_cache(self) -> None:
        """模拟依赖缓存设置"""
        os.makedirs(self.cache_dir, exist_ok=True)
        print(f"🔧 Cache directory ready at {self.cache_dir}")
        
    def verify_installation(self, version: str) -> bool:
        """
        验证Python安装
        Args:
            version: 要验证的版本号
        Returns:
            bool: 是否验证成功
        """
        python_exec = "pypy3" if "pypy" in version else "python3"
        return shutil.which(python_exec) is not None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Python setup simulator")
    parser.add_argument(
        "--python-version", 
        type=str,
        help="Python version to install (e.g. '3.13', 'pypy3.10')"
    )
    parser.add_argument(
        "--cache-dependencies",
        action="store_true",
        help="Enable dependency caching"
    )
    
    args = parser.parse_args()
    installer = PythonInstaller()
    
    if not args.python_version:
        print("⚠️  No python-version specified, using system Python")
        sys.exit(0)
        
    if installer.install_python(args.python_version):
        if args.cache_dependencies:
            installer.setup_cache()
        
        if installer.verify_installation(args.python_version):
            print("✅ Setup completed successfully")
        else:
            print("❌ Failed to verify Python installation")
            sys.exit(1)