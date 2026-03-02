#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
requests库示例脚本
学习来源: GitHub仓库 psf/requests (https://github.com/psf/requests)
创建日期: 2023-11-20
功能描述: 演示requests库的核心功能，包括GET/POST请求、认证、JSON处理、错误处理等
"""

import requests
from pprint import pprint  # 用于美化输出

def main():
    # 示例1: 基本GET请求
    print("\n=== 示例1: 基本GET请求 ===")
    try:
        response = requests.get("https://httpbin.org/get")
        print(f"状态码: {response.status_code}")
        print("响应头:")
        pprint(dict(response.headers), indent=4)
        print("响应内容:")
        pprint(response.json(), indent=4)
    except requests.RequestException as e:
        print(f"请求错误: {e}")

    # 示例2: 带参数的GET请求
    print("\n=== 示例2: 带参数的GET请求 ===")
    params = {"key1": "value1", "key2": "value2"}
    response = requests.get("https://httpbin.org/get", params=params)
    print(f"实际请求URL: {response.url}")
    print("URL参数:")
    pprint(response.json()["args"], indent=4)

    # 示例3: POST请求发送表单数据
    print("\n=== 示例3: POST表单数据 ===")
    data = {"username": "demo", "password": "secret"}
    response = requests.post("https://httpbin.org/post", data=data)
    print(f"状态码: {response.status_code}")
    print("表单数据:")
    pprint(response.json()["form"], indent=4)

    # 示例4: POST请求发送JSON数据
    print("\n=== 示例4: POST JSON数据 ===")
    json_data = {"name": "Alice", "age": 25, "city": "New York"}
    response = requests.post("https://httpbin.org/post", json=json_data)
    print("发送的JSON数据:")
    pprint(response.json()["json"], indent=4)

    # 示例5: 基本认证
    print("\n=== 示例5: 基本认证 ===")
    auth = ("user", "pass")
    response = requests.get("https://httpbin.org/basic-auth/user/pass", auth=auth)
    print(f"认证状态: {response.status_code == 200}")
    if response.status_code == 200:
        print("认证响应:")
        pprint(response.json(), indent=4)

    # 示例6: 会话保持(cookie持久化)
    print("\n=== 示例6: 会话保持 ===")
    with requests.Session() as session:
        # 第一次请求设置cookie
        session.get("https://httpbin.org/cookies/set/sessioncookie/123456789")
        # 第二次请求会携带cookie
        response = session.get("https://httpbin.org/cookies")
        print("当前会话cookie:")
        pprint(response.json(), indent=4)

    # 示例7: 错误处理
    print("\n=== 示例7: 错误处理 ===")
    try:
        response = requests.get("https://httpbin.org/status/404")
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError
    except requests.HTTPError as e:
        print(f"HTTP错误: {e}")
    except requests.RequestException as e:
        print(f"请求错误: {e}")

    # 示例8: 下载文件