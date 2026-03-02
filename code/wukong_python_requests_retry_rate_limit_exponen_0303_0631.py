#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
requests库使用示例脚本
学习来源: https://github.com/psf/requests
创建日期: 2023-12-01
功能描述: 演示requests库的核心功能，包括GET/POST请求、认证、Session、超时设置等最佳实践
"""

import requests
from requests.auth import HTTPBasicAuth

def main():
    """
    主函数，展示requests库的核心功能
    """
    
    # 1. 基本GET请求
    print("\n1. 基本GET请求示例:")
    resp = requests.get('https://httpbin.org/get')
    print(f"状态码: {resp.status_code}")
    print(f"响应头: {resp.headers['content-type']}")
    print(f"响应内容: {resp.json()}")  # 自动解析JSON响应
    
    # 2. 带参数的GET请求
    print("\n2. 带参数的GET请求示例:")
    params = {'key1': 'value1', 'key2': 'value2'}
    resp = requests.get('https://httpbin.org/get', params=params)
    print(f"请求URL: {resp.url}")
    print(f"参数返回: {resp.json()['args']}")
    
    # 3. 基本认证
    print("\n3. 基本认证示例:")
    auth = HTTPBasicAuth('user', 'pass')
    resp = requests.get('https://httpbin.org/basic-auth/user/pass', auth=auth)
    print(f"认证状态: {resp.json()['authenticated']}")
    
    # 4. POST请求(表单数据和JSON数据)
    print("\n4. POST请求示例:")
    # 表单数据POST
    form_data = {'key': 'value'}
    resp = requests.post('https://httpbin.org/post', data=form_data)
    print(f"表单数据返回: {resp.json()['form']}")
    
    # JSON数据POST
    json_data = {'key': 'value'}
    resp = requests.post('https://httpbin.org/post', json=json_data)
    print(f"JSON数据返回: {resp.json()['json']}")
    
    # 5. 使用Session保持会话
    print("\n5. Session会话保持示例:")
    session = requests.Session()
    session.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    resp = session.get('https://httpbin.org/cookies')
    print(f"会话Cookies: {resp.json()['cookies']}")
    
    # 6. 超时设置
    print("\n6. 超时设置示例:")
    try:
        # 连接超时3秒，读取超时7秒
        resp = requests.get('https://httpbin.org/delay/5', timeout=(3, 7))
        print("请求成功!")
    except requests.exceptions.Timeout:
        print("请求超时!")
    
    # 7. 流式下载大文件
    print("\n7. 流式下载示例:")
    resp = requests.get('https://httpbin.org/stream/5', stream=True)
    for line in resp.iter_lines():
        if line:
            print(f"接收到流数据: {line}")
    
    # 8. 异常处理
    print("\n8. 异常处理示例:")
    try:
        resp = requests.get('https://httpbin.org/status/404')
        resp.raise_for_status()  # 如果状态码不是200，抛出HTTPError异常
    except requests.exceptions.HTTPError as err:
        print(f"HTTP错误: {err}")

if __name__ == '__main__':
    main()