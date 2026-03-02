#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tailscale Healthcheck Monitor
学习来源: laitco/tailscale-healthcheck (https://github.com/laitco/tailscale-healthcheck)
创建日期: 2023-11-16
功能描述: 监控Tailscale网络设备状态的Flask应用，提供健康检查端点
"""

from flask import Flask, jsonify, request
import requests
from typing import Dict, List, Optional

app = Flask(__name__)

# 配置项 - 替换成你自己的Tailscale配置
TAILSCALE_API_KEY = "your-api-key-here"
TAILSCALE_TAILNET = "your.tailnet"  # 如: example.com
API_BASE_URL = "https://api.tailscale.com"

def fetch_tailscale_devices() -> List[Dict]:
    """从Tailscale API获取所有设备信息"""
    headers = {
        "Authorization": f"Bearer {TAILSCALE_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE_URL}/api/v2/tailnet/{TAILSCALE_TAILNET}/devices"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("devices", [])

def check_device_health(device: Dict) -> Dict:
    """检查单个设备健康状态"""
    return {
        "id": device.get("id"),
        "name": device.get("name"),
        "online_healthy": device.get("online", False),  # 设备是否在线
        "key_healthy": not device.get("expired", True),  # 密钥是否过期
        # update_healthy可以在实际使用中添加更新状态检查
        "update_healthy": True  # 假设为True，实际应根据更新状态检查
    }

@app.route('/health', methods=['GET'])
def health_overview():
    """获取所有设备的健康状态概览"""
    try:
        devices = fetch_tailscale_devices()
        device_health = [check_device_health(d) for d in devices]
        
        # 计算全局健康状态
        global_online = all(d['online_healthy'] for d in device_health)
        global_key = all(d['key_healthy'] for d in device_health)
        global_update = all(d['update_healthy'] for d in device_health)
        
        return jsonify({
            "devices": device_health,
            "global_healthy": global_online and global_key and global_update,
            "global_online_healthy": global_online,
            "global_key_healthy": global_key,
            "global_update_healthy": global_update,
            "total_devices": len(devices),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health/<device_id>', methods=['GET'])
def device_health(device_id: str):
    """获取特定设备的健康状态"""
    try:
        devices = fetch_tailscale_devices()
        device = next((d for d in devices if d.get("id") == device_id), None)
        
        if not device:
            return jsonify({"error": "Device not found"}), 404
            
        return jsonify(check_device_health(device))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health/healthy', methods=['GET'])
def healthy_devices():
    """获取所有健康设备列表"""
    return filter_devices_by_health(True)

@app.route('/health/unhealthy', methods=['GET'])
def unhealthy_devices():
    """获取所有不健康设备列表"""
    return