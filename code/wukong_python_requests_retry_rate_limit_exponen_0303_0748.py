#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Requests HTTP 客户端示例
学习来源: https://github.com/psf/requests
创建日期: 2023-11-10
功能描述: 演示requests库的核心功能，包括GET/POST请求、认证处理、
          JSON数据交互、异常处理和会话保持等
"""

import requests
from requests.exceptions import RequestException

def main():
    """主函数，演示requests库的各种用法"""
    
    try:
        # 示例1: 基本GET请求
        print("--- 基本GET请求示例 ---")
        response = requests.get('https://httpbin.org/get')
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers['content-type']}")
        print(f"响应内容: {response.text[:200]}...")  # 截取前200个字符
        
        # 示例2: 带参数的GET请求
        print("\n--- 带参数的GET请求 ---")
        params = {'key1': 'value1', 'key2': 'value2'}
        response = requests.get('https://httpbin.org/get', params=params)
        print(f"请求URL: {response.url}")
        print(f"JSON响应: {response.json()}")
        
        # 示例3: 基本认证
        print("\n--- 基本认证示例 ---")
        response = requests.get(
            'https://httpbin.org/basic-auth/user/pass',
            auth=('user', 'pass')
        )
        print(f"认证状态: {response.json()['authenticated']}")
        
        # 示例4: POST请求发送JSON数据
        print("\n--- POST JSON数据 ---")
        data = {'name': 'John', 'age': 30}
        response = requests.post('https://httpbin.org/post', json=data)
        print(f"发送的数据: {response.json()['json']}")
        
        # 示例5: 使用会话保持(Session)
        print("\n--- 会话保持示例 ---")
        with requests.Session() as session:
            # 设置会话级参数
            session.headers.update({'x-test': 'true'})
            
            # 第一次请求会设置cookie
            response = session.get('https://httpbin.org/cookies/set/sessioncookie/12345')
            print(f"第一次请求Cookies: {response.json()['cookies']}")
            
            # 第二次请求会保持cookie
            response = session.get('https://httpbin.org/cookies')
            print(f"第二次请求Cookies: {response.json()['cookies']}")
            
        # 示例6: 处理超时
        print("\n--- 超时处理示例 ---")
        try:
            response = requests.get('https://httpbin.org/delay/3', timeout=1)
        except requests.exceptions.Timeout:
            print("请求超时！")
            
        # 示例7: 下载文件
        print("\n--- 文件下载示例 ---")
        response = requests.get('https://httpbin.org/image/png', stream=True)
        with open('image.png', 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print("图片下载完成，保存为image.png")
        
    except RequestException as e:
        print(f"请求发生错误: {str(e)}")

if __name__ == '__main__':
    main()