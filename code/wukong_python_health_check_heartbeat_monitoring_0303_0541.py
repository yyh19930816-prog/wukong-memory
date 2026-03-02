#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tailscale Healthcheck Monitor - Lightweight Implementation
Learn from: https://github.com/laitco/tailscale-healthcheck
Created: 2023-11-15
Description: A simplified version of tailscale-healthcheck that monitors device
             status in a Tailscale network via its API.
"""

import os
import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Tailscale API configuration
TAILSCALE_API_KEY = os.getenv('TAILSCALE_API_KEY', 'your-api-key')
TAILSCALE_API_URL = "https://api.tailscale.com/api/v2/tailnet/{}/devices"
TAILSCALE_TAILNET = os.getenv('TAILSCALE_TAILNET', 'your-tailnet.example.com')

def fetch_devices():
    """Fetch device list from Tailscale API."""
    headers = {
        'Authorization': f'Bearer {TAILSCALE_API_KEY}',
        'Content-Type': 'application/json'
    }
    url = TAILSCALE_API_URL.format(TAILSCALE_TAILNET)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('devices', [])
    except requests.RequestException as e:
        return {'error': str(e)}

def check_device_health(device):
    """Check health status of a single device."""
    return {
        'id': device.get('id'),
        'name': device.get('name'),
        'online': device.get('online'),
        'last_seen': device.get('lastSeen'),
        'expires': device.get('expires'),
        'key_expired': False if device.get('keyExpiryDisabled') else device.get('expires')
    }

@app.route('/health', methods=['GET'])
def health_overview():
    """Get health status overview for all devices."""
    devices = fetch_devices()
    if isinstance(devices, dict) and 'error' in devices:
        return jsonify({'error': devices['error']}), 500
        
    results = []
    healthy_count = unhealthy_count = 0
    
    for device in devices:
        status = check_device_health(device)
        is_healthy = status['online'] and not status['key_expired']
        status['healthy'] = is_healthy
        results.append(status)
        
        if is_healthy:
            healthy_count += 1
        else:
            unhealthy_count += 1
    
    return jsonify({
        'devices': results,
        'stats': {
            'total': len(results),
            'healthy': healthy_count,
            'unhealthy': unhealthy_count,
            'global_healthy': unhealthy_count == 0
        }
    })

@app.route('/health/<device_id>', methods=['GET'])
def device_health(device_id):
    """Get health status for specific device."""
    devices = fetch_devices()
    if isinstance(devices, dict) and 'error' in devices:
        return jsonify({'error': devices['error']}), 500
        
    for device in devices:
        if device.get('id') == device_id:
            status = check_device_health(device)
            status['healthy'] = status['online'] and not status['key_expired']
            return jsonify(status)
    
    return jsonify({'error': 'Device not found'}), 404

@app.route('/health/healthy', methods=['GET'])
def list_healthy_devices():
    """List all healthy devices."""
    return filter_devices_by_health(True)

@app.route('/health/unhealthy', methods=['GET'])
def list_unhealthy_devices():
    """List all unhealthy devices