# -*- coding: utf-8 -*-
# Tailscale Healthcheck Implementation
# Learned from laitco/tailscale-healthcheck GitHub repository
# Date: 2023-11-15
# Description: Flask-based health check endpoints for Tailscale devices monitoring

from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import logging

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tailscale API configuration
TAILSCALE_API_URL = "https://api.tailscale.com/api/v2"
API_KEY = "your-tailscale-api-key"  # Replace with your actual API key

class TailscaleHealthCheck:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

    def get_devices(self):
        """Fetch all devices from Tailscale API"""
        try:
            response = requests.get(
                f"{TAILSCALE_API_URL}/tailnet/-/devices",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("devices", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch devices: {e}")
            return []

    def check_device_health(self, device):
        """Check individual device health status"""
        now = datetime.utcnow()
        key_expiry = datetime.fromisoformat(device["expires"].rstrip("Z"))
        
        health_status = {
            "id": device["id"],
            "name": device["name"],
            "online_healthy": device.get("online", False),
            "key_healthy": now < key_expiry,
            "update_healthy": True  # Simplified version - actual implementation would check updates
        }
        health_status["healthy"] = all([
            health_status["online_healthy"],
            health_status["key_healthy"],
            health_status["update_healthy"]
        ])
        return health_status

    def get_global_health(self, devices_status):
        """Calculate global health metrics"""
        if not devices_status:
            return {"global_healthy": False}
            
        return {
            "global_healthy": all(d["healthy"] for d in devices_status),
            "global_online_healthy": all(d["online_healthy"] for d in devices_status),
            "global_key_healthy": all(d["key_healthy"] for d in devices_status),
            "global_update_healthy": all(d["update_healthy"] for d in devices_status),
            "total_devices": len(devices_status),
            "healthy_devices": sum(1 for d in devices_status if d["healthy"])
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for checking health status of all devices"""
    checker = TailscaleHealthCheck()
    devices = checker.get_devices()
    devices_status = [checker.check_device_health(d) for d in devices]
    global_health = checker.get_global_health(devices_status)
    
    return jsonify({
        "status": "success",
        "data": {
            "devices": devices_status,
            "global": global_health
        }
    })

@app.route('/health/<identifier>', methods=['GET'])
def device_health_check(identifier):
    """Endpoint for checking health status of a specific device"""
    checker = TailscaleHealthCheck()
    devices = checker.get_devices()
    
    matched_device = next((d for d in devices if d["id"] == identifier or d["name"] == identifier), None)
    if not matched_device:
        return jsonify({"status": "