#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python HTTP Requests 示例程序
学习来源: https://github.com/psf/requests
创建日期: 2023-11-15
功能描述: 演示requests库的核心功能，包括GET/POST请求、认证、JSON处理、Headers操作等
"""

import requests
from pprint import pprint

def main():
    # 示例1: 基本GET请求
    print("="*40)
    print("示例1: 基本GET请求")
    print("="*40)
    try:
        # 发送GET请求到测试API
        response = requests.get('https://httpbin.org/get')
        
        # 打印响应状态码
        print(f"状态码: {response.status_code}")
        
        # 打印响应头部
        print("\n响应头部:")
        pprint(dict(response.headers))
        
        # 以JSON格式解析响应内容
        print("\n响应内容:")
        pprint(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # 示例2: 带参数的GET请求
    print("\n" + "="*40)
    print("示例2: 带参数的GET请求")
    print("="*40)
    try:
        # 构造查询参数
        params = {'key1': 'value1', 'key2': 'value2'}
        
        # 发送GET请求并附加查询参数
        response = requests.get('https://httpbin.org/get', params=params)
        
        # 显示最终的URL(包含查询参数)
        print(f"请求URL: {response.url}")
        
        # 显示解析后的参数
        print("\n返回的参数:")
        pprint(response.json()['args'])
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # 示例3: 基本认证
    print("\n" + "="*40)
    print("示例3: 基本认证")
    print("="*40)
    try:
        # 使用基本认证发送请求
        response = requests.get(
            'https://httpbin.org/basic-auth/user/pass',
            auth=('user', 'pass')  # 认证凭据
        )
        
        print(f"状态码: {response.status_code}")
        print("认证结果:")
        pprint(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # 示例4: POST请求发送JSON数据
    print("\n" + "="*40)
    print("示例4: POST请求发送JSON数据")
    print("="*40)
    try:
        # 构造JSON数据
        data = {'name': 'John', 'age': 30, 'city': 'New York'}
        
        # 发送POST请求并附加JSON数据
        response = requests.post(
            'https://httpbin.org/post',
            json=data  # 自动序列化为JSON并设置Content-Type
        )
        
        print(f"状态码: {response.status_code}")
        print("\n返回的JSON数据:")
        pprint(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # 示例5: 处理响应内容
    print("\n" + "="*40)
    print("示例5: 处理响应内容")
    print("="*40)
    try:
        # 发送GET请求
        response = requests.get('https://httpbin.org/encoding/utf8')
        
        # 获取响应内容的不同表示形式
        print(f"Encoding: