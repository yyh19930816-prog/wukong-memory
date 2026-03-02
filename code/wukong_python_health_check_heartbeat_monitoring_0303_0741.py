#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tailscale Healthcheck Monitor 
Based on laitco/tailscale-healthcheck repository
Created: 2023-11-20
Function: Monitors health status of Tailscale network devices
"""
import requests
from flask import Flask, jsonify
from typing import Dict, List, Optional

app = Flask(__name__)

# Tailscale API endpoint configurations
TAILSCALE_API_URL = "https://api.tailscale.com/api/v2"
HEADERS = {
    "Content-Type": "application/json",
    # Add your Tailscale API key here
    "Authorization": "Bearer YOUR_TAILSCALE_API_KEY"
}

class TailscaleHealthMonitor:
    """Core class for monitoring Tailscale device health"""
    
    def __init__(self):
        self.device_cache = []
        self.last_update = None
    
    def fetch_devices(self) -> List[Dict]:
        """Fetch all devices from Tailscale API"""
        try:
            response = requests.get(
                f"{TAILSCALE_API_URL}/tailnet/devices",
                headers=HEADERS,
                timeout=10
            )
            response.raise_for_status()
            self.device_cache = response.json().get("devices", [])
            self.last_update = response.headers.get("Date")
            return self.device_cache
        except requests.exceptions.RequestException as e:
            print(f"Error fetching devices: {e}")
            return []

    def check_device_health(self) -> Dict:
        """
        Check health status of all devices
        Returns dict with overall health metrics
        """
        devices = self.fetch_devices()
        if not devices:
            return {"error": "Could not fetch devices"}
            
        # Initialize health counters
        stats = {
            "total": len(devices),
            "online_healthy": 0,
            "key_healthy": 0,
            "update_healthy": 0,
            "devices": []
        }
        
        for device in devices:
            # Check online status (last seen within 5 minutes)
            online = device.get("online", False)
            stats["online_healthy"] += int(online)
            
            # Check if keys are expired
            expires = device.get("expires", {}).get("seconds", 0)
            key_ok = expires > 0  # Simplified check
            stats["key_healthy"] += int(key_ok)
            
            # Add simplified update check (would need proper version comparison)
            update_ok = True  # Placeholder
            stats["update_healthy"] += int(update_ok)
            
            # Append individual device status
            stats["devices"].append({
                "name": device.get("name"),
                "id": device.get("id"),
                "online": online,
                "key_healthy": key_ok,
                "update_healthy": update_ok
            })
        
        # Calculate global health percentages
        stats["global_healthy"] = all([
            stats["online_healthy"] == stats["total"],
            stats["key_healthy"] == stats["total"]
        ])
        stats["global_online_healthy"] = stats["online_healthy"] / stats["total"]
        stats["global_key_healthy"] = stats["key_healthy"] / stats["total"]
        stats["global_update_healthy"] = stats["update_healthy"] / stats["total"]
        
        return stats

# Flask API endpoints
@app.route("/health", methods=["GET"])
def health_overview():
    """Endpoint for overall health status"""
    monitor = TailscaleHealthMonitor()
    return jsonify(monitor.check_device_health())

@app.route("/health/<identifier>", methods=["GET"])
def device_health(identifier: str):