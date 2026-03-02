#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tailscale Healthcheck Monitor

Based on laitco/tailscale-healthcheck repository
Created: 2024-02-20
Core functionality: Monitors health status of Tailscale network devices
Provides endpoints for checking device health states

Features:
- Checks device online status, key expiry and update status
- Returns global health metrics
"""

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration defaults
TAILSCALE_API_BASE = "https://api.tailscale.com/api/v2"
HEALTH_STATUSES = {
    'online_healthy': bool,
    'key_healthy': bool,
    'update_healthy': bool
}

class TailscaleHealthCheck:
    def __init__(self, api_key):
        """Initialize with Tailscale API key"""
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _get_devices(self):
        """Fetch all devices from Tailscale API"""
        try:
            response = requests.get(
                f"{TAILSCALE_API_BASE}/tailnet/devices",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('devices', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching devices: {e}")
            return []

    def check_device_health(self, device):
        """Check health status for a single device"""
        health = {
            'online_healthy': device.get('online', False),
            'key_healthy': not device.get('keyExpired', True),
            'update_healthy': True  # Placeholder for update check
        }
        device_id = device.get('id', 'unknown')
        return {device_id: health}

    def get_all_device_health(self):
        """Get health status for all devices"""
        devices = self._get_devices()
        return {dev['id']: self.check_device_health(dev) for dev in devices}

    def get_global_metrics(self):
        """Calculate global health metrics"""
        devices = self._get_devices()
        if not devices:
            return {}
            
        total = len(devices)
        online = sum(1 for d in devices if d.get('online', False))
        keys_ok = sum(1 for d in devices if not d.get('keyExpired', True))
        
        return {
            'global_healthy': (online == total and keys_ok == total),
            'global_online_healthy': online == total,
            'global_key_healthy': keys_ok == total,
            'device_count': total
        }

# Flask endpoints
@app.route('/health', methods=['GET'])
def health_overview():
    """Return health status for all devices"""
    checker = TailscaleHealthCheck(api_key="your_api_key_here")
    return jsonify(checker.get_all_device_health())

@app.route('/health/<device_id>', methods=['GET'])
def health_single(device_id):
    """Return health status for specific device"""
    checker = TailscaleHealthCheck(api_key="your_api_key_here")
    devices = checker._get_devices()
    device = next((d for d in devices if d['id'] == device_id), None)
    if device:
        return jsonify(checker.check_device_health(device))
    return jsonify({"error": "Device not found"}), 404

@app.route('/health/global', methods=['GET'])
def global_health():
    """Return global health metrics"""
    checker = TailscaleHealthCheck(api_key="your_api_key_here")
    return json