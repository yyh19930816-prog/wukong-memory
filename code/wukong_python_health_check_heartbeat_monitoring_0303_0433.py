#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tailscale Healthcheck Monitor
-----------------------------
来源: laitco/tailscale-healthcheck GitHub仓库
日期: 2023-11-15
功能: 监控Tailscale网络设备状态的Flask应用，提供设备健康检查端点
"""

from flask import Flask, jsonify
import requests
import os
from typing import Dict, List, Optional

app = Flask(__name__)

# 从环境变量获取Tailscale API配置
TAILSCALE_API_KEY = os.getenv('TAILSCALE_API_KEY', '')
TAILSCALE_TAILNET = os.getenv('TAILSCALE_TAILNET', '')
TAILSCALE_API_URL = f'https://api.tailscale.com/api/v2/tailnet/{TAILSCALE_TAILNET}/devices'

def fetch_devices() -> Optional[List[Dict]]:
    """从Tailscale API获取设备列表"""
    headers = {'Authorization': f'Bearer {TAILSCALE_API_KEY}'}
    try:
        response = requests.get(TAILSCALE_API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get('devices', [])
    except requests.exceptions.RequestException:
        return None

def check_device_health(device: Dict) -> Dict:
    """检查单个设备健康状态"""
    return {
        'id': device.get('id'),
        'name': device.get('name'),
        'online': device.get('online'),  # 设备在线状态
        'key_expired': device.get('expires') <= 0,  # 密钥过期状态
        'client_version': device.get('clientVersion', 'unknown'),  # 客户端版本
        'update_available': device.get('updateAvailable', False)  # 更新可用状态
    }

@app.route('/health', methods=['GET'])
def health_overview():
    """获取所有设备健康状态概览"""
    devices = fetch_devices()
    if devices is None:
        return jsonify({'error': 'Failed to fetch devices from Tailscale API'}), 500

    health_data = {
        'devices': [],
        'global_status': {
            'total_devices': len(devices),
            'online_devices': sum(1 for d in devices if d.get('online')),
            'key_healthy_devices': sum(1 for d in devices if d.get('expires', 0) > 0)
        }
    }

    for device in devices:
        health_data['devices'].append(check_device_health(device))

    return jsonify(health_data)

@app.route('/health/<device_id>', methods=['GET'])
def device_health(device_id: str):
    """获取指定设备健康状态"""
    devices = fetch_devices()
    if devices is None:
        return jsonify({'error': 'Failed to fetch devices from Tailscale API'}), 500

    for device in devices:
        if device.get('id') == device_id:
            return jsonify(check_device_health(device))

    return jsonify({'error': 'Device not found'}), 404

@app.route('/health/healthy', methods=['GET'])
def healthy_devices():
    """获取所有健康设备列表"""
    devices = fetch_devices()
    if devices is None:
        return jsonify({'error': 'Failed to fetch devices from Tailscale API'}), 500

    healthy = [d.get('name') for d in devices 
               if d.get('online') and d.get('expires', 0) > 0]
    
    return jsonify({'healthy_devices': healthy})

@app.route('/health/unhealthy',methods=['GET'])
def unhealthy_dev