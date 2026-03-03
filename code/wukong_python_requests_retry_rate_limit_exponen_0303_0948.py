#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Requests HTTP Library Demo Script
来源：https://github.com/psf/requests
日期：2023-11-15
功能：演示requests库的核心功能，包括GET请求、POST请求、认证、会话保持等
"""

import requests
import json

def main():
    # 演示GET请求
    print("===== GET请求演示 =====")
    response = requests.get('https://httpbin.org/get')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {json.dumps(dict(response.headers), indent=4)}")
    print(f"响应内容: {response.text[:200]}...")  # 只打印前200个字符
    
    # 演示带参数的GET请求
    params = {'key1': 'value1', 'key2': 'value2'}
    response = requests.get('https://httpbin.org/get', params=params)
    print(f"\n带参数的URL: {response.url}")
    
    # 演示POST请求
    print("\n===== POST请求演示 =====")
    payload = {'username': 'test', 'password': '123456'}
    response = requests.post('https://httpbin.org/post', data=payload)
    print(f"POST响应: {response.json()['form']}")
    
    # 演示JSON POST请求
    headers = {'Content-Type': 'application/json'}
    json_payload = {'site': 'github', 'repo': 'requests'}
    response = requests.post('https://httpbin.org/post', json=json_payload, headers=headers)
    print(f"\nJSON POST响应: {response.json()['json']}")
    
    # 演示基本认证
    print("\n===== 认证演示 =====")
    response = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
    print(f"认证响应: {response.json()}")
    
    # 演示会话保持(cookies持续)
    print("\n===== 会话演示 =====")
    session = requests.Session()
    session.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    response = session.get('https://httpbin.org/cookies')
    print(f"会话Cookies: {response.json()['cookies']}")
    
    # 演示超时设置
    print("\n===== 超时演示 =====")
    try:
        response = requests.get('https://httpbin.org/delay/3', timeout=2)
    except requests.exceptions.Timeout:
        print("请求超时！")
    
    # 演示流式下载
    print("\n===== 流式下载演示 =====")
    response = requests.get('https://httpbin.org/stream/10', stream=True)
    print(f"流式响应状态码: {response.status_code}")
    
    # 演示自动解压缩
    print("\n===== 压缩处理演示 =====")
    response = requests.get('https://httpbin.org/gzip')
    print(f"自动解压缩后的内容: {response.json()['method']}")

if __name__ == '__main__':
    main()