#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Requests HTTP 客户端示例
来源: GitHub仓库 psf/requests (https://github.com/psf/requests)
日期: 2023-11-15
功能: 演示requests库的核心功能，包括各种HTTP请求方法、认证、headers处理、JSON处理等
"""

import requests
from requests.auth import HTTPBasicAuth

def main():
    # 1. 基本的GET请求
    print("1. 基本GET请求示例:")
    response = requests.get("https://httpbin.org/get")
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers['content-type']}")
    print(f"响应内容: {response.text[:200]}...")  # 截取前200字符防止输出过长
    print("-" * 50)

    # 2. 带参数的GET请求 (参数会自动编码)
    print("2. 带参数的GET请求示例:")
    params = {"key1": "value1", "key2": "value2"}
    response = requests.get("https://httpbin.org/get", params=params)
    print(f"请求URL: {response.url}")
    print(f"JSON响应: {response.json()}")
    print("-" * 50)

    # 3. 基本认证请求
    print("3. 基本认证示例:")
    auth = HTTPBasicAuth("user", "pass")
    response = requests.get("https://httpbin.org/basic-auth/user/pass", auth=auth)
    print(f"认证状态: {response.json()}")
    print("-" * 50)

    # 4. POST请求 (表单数据和JSON数据)
    print("4. POST请求示例:")
    
    # 4.1 表单POST
    form_data = {"key": "value"}
    response = requests.post("https://httpbin.org/post", data=form_data)
    print("表单POST响应:")
    print(response.json()["form"])
    
    # 4.2 JSON POST (推荐方式)
    json_data = {"name": "Alice", "age": 25}
    response = requests.post("https://httpbin.org/post", json=json_data)
    print("\nJSON POST响应:")
    print(response.json()["json"])
    print("-" * 50)

    # 5. 处理响应内容(文本、二进制、JSON)
    print("5. 响应内容处理示例:")
    response = requests.get("https://httpbin.org/image/png")
    print(f"二进制响应长度: {len(response.content)} bytes")
    
    response = requests.get("https://httpbin.org/json")
    print(f"直接解析JSON: {response.json()}")
    print("-" * 50)

    # 6. 超时和错误处理
    print("6. 超时和错误处理示例:")
    try:
        response = requests.get("https://httpbin.org/delay/3", timeout=1)
    except requests.Timeout:
        print("请求超时!")
    
    try:
        response = requests.get("https://httpbin.org/status/404")
        response.raise_for_status()  # 对4XX/5XX状态码抛出异常
    except requests.HTTPError as e:
        print(f"HTTP错误: {e}")
    print("-" * 50)

    # 7. 持久会话(保持cookies和headers)
    print("7. 会话示例:")
    with requests.Session() as session:
        session.headers.update({"x-test": "true"})
        
        # 第一次请求设置cookie
        response = session.get("https://httpbin.org/cookies/set/sessioncookie