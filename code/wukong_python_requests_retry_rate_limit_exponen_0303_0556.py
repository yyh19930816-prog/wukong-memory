#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Requests HTTP库示例脚本
学习来源: https://github.com/psf/requests
日期: 2023-11-20
功能: 演示requests库的核心功能，包括GET/POST请求、认证、JSON处理、异常处理等
"""

import requests
from requests.exceptions import RequestException

def main():
    # 示例1: 基本GET请求
    print("=== 示例1: 基本GET请求 ===")
    try:
        response = requests.get('https://httpbin.org/get')
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers['content-type']}")
        print(f"响应内容(前100字符): {response.text[:100]}...")
    except RequestException as e:
        print(f"请求失败: {e}")

    # 示例2: 带参数的GET请求
    print("\n=== 示例2: 带参数的GET请求 ===")
    params = {'key1': 'value1', 'key2': 'value2'}
    response = requests.get('https://httpbin.org/get', params=params)
    print(f"请求URL: {response.url}")
    print(f"响应JSON: {response.json()}")

    # 示例3: POST请求发送JSON数据
    print("\n=== 示例3: POST请求发送JSON数据 ===")
    data = {'username': 'test', 'password': 'secret'}
    response = requests.post('https://httpbin.org/post', json=data)
    print(f"状态码: {response.status_code}")
    print("响应JSON:")
    print(response.json())

    # 示例4: 基本认证
    print("\n=== 示例4: 基本认证 ===")
    response = requests.get(
        'https://httpbin.org/basic-auth/user/pass',
        auth=('user', 'pass')
    )
    print(f"认证状态: {response.json()['authenticated']}")

    # 示例5: 处理异常和超时
    print("\n=== 示例5: 处理异常和超时 ===")
    try:
        response = requests.get('https://httpbin.org/delay/5', timeout=3)
    except requests.Timeout:
        print("请求超时!")
    except RequestException as e:
        print(f"其他请求错误: {e}")

    # 示例6: 使用会话保持(Session)保持cookies
    print("\n=== 示例6: 会话保持 ===")
    session = requests.Session()
    session.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    response = session.get('https://httpbin.org/cookies')
    print(f"会话Cookies: {response.json()['cookies']}")

    # 示例7: 流式下载大文件(这里只展示模式)
    print("\n=== 示例7: 流式下载 ===")
    response = requests.get('https://httpbin.org/stream/1', stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:  # 过滤掉保持活动新行
                print(f"收到流数据: {line.decode('utf-8')}")

if __name__ == '__main__':
    main()