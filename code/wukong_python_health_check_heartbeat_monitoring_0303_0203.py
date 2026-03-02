#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# tailscale_healthcheck.py
#
# 学习来源：https://github.com/laitco/tailscale-healthcheck
# 创建日期：2023-10-20
# 功能描述：一个简化版的Tailscale设备健康检查工具，提供基本的健康状态检测功能
#           检查设备的在线状态和密钥过期状态，并提供REST API端点

import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify

app = Flask(__name__)

class TailscaleHealthCheck:
    def __init__(self):
        # 初始化Tailscale API配置
        self.api_key = os.getenv('TAILSCALE_API_KEY')
        self.tailnet = os.getenv('TAILSCALE_TAILNET')
        self.api_base = 'https://api.tailscale.com/api/v2'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def fetch_devices(self):
        """从Tailscale API获取所有设备信息"""
        if not self.api_key or not self.tailnet:
            raise ValueError("缺少TAILSCALE_API_KEY或TAILSCALE_TAILNET环境变量")
            
        url = f"{self.api_base}/tailnet/{self.tailnet}/devices"
        response = requests.get(url, headers=self.headers)
        return response.json().get('devices', [])
        
    def check_device_health(self, device):
        """检查单个设备的健康状态"""
        now = datetime.utcnow()
        expiry_time = datetime.fromisoformat(device['expires'].replace('Z', ''))
        
        return {
            'id': device['id'],
            'name': device['name'],
            'online_healthy': device['online'],
            'key_healthy': now < expiry_time,
            'last_seen': device['lastSeen'],
            'expires': device['expires']
        }
        
    def get_health_status(self):
        """获取所有设备的健康状态"""
        devices = self.fetch_devices()
        status = {
            'devices': [],
            'global_healthy': True,
            'global_online_healthy': True,
            'global_key_healthy': True
        }
        
        for device in devices:
            device_status = self.check_device_health(device)
            status['devices'].append(device_status)
            
            # 更新全局状态
            if not device_status['online_healthy']:
                status['global_online_healthy'] = False
            if not device_status['key_healthy']:
                status['global_key_healthy'] = False
                
        # 整体健康状态 = 在线状态 AND 密钥状态
        status['global_healthy'] = status['global_online_healthy'] and status['global_key_healthy']
        return status

health_check = TailscaleHealthCheck()

@app.route('/health', methods=['GET'])
def get_all_health():
    """获取所有设备的健康状态"""
    return jsonify(health_check.get_health_status())

@app.route('/health/<device_id>', methods=['GET'])
def get_device_health(device_id):
    """获取指定设备的健康状态"""
    status = health_check.get_health_status()
    for device in status['devices']:
        if device['id'] == device_id:
            return jsonify(device)
    return jsonify({'error': 'Device not found'}), 404

@app.route('/health/healthy', methods=['GET'])
def get_healthy_devices():
    """获取所有健康的设备"""
    status = health_check.get_health_status()
    healthy_devices = [d for d in status