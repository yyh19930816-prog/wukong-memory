# tailscale_healthcheck.py
# 学习来源：GitHub仓库 laitco/tailscale-healthcheck (https://github.com/laitco/tailscale-healthcheck)
# 创建日期：2023-10-15
# 功能描述：一个基于Flask的Tailscale设备健康检查工具，提供API端点检查设备在线状态和密钥状态

from flask import Flask, jsonify
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional

app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tailscale API基础配置
TAILSCALE_API_BASE = "https://api.tailscale.com/api/v2"
API_KEY = "your_tailscale_api_key"  # 替换为你的Tailscale API密钥
TAILNET = "your.tailnet"  # 替换为你的Tailnet名称

class TailscaleDevice:
    """表示Tailscale网络中的设备及其健康状态"""
    
    def __init__(self, device_data: Dict):
        """初始化设备数据"""
        self.id = device_data.get("id")
        self.hostname = device_data.get("hostname")
        self.online = device_data.get("online")
        self.key_expiry = datetime.fromisoformat(device_data.get("keyExpiry")) 
        self.client_version = device_data.get("clientVersion")
        
    @property
    def online_healthy(self) -> bool:
        """检查设备是否在线"""
        return self.online
    
    @property
    def key_healthy(self) -> bool:
        """检查设备密钥是否未过期"""
        return self.key_expiry > datetime.utcnow()
    
    @property
    def update_healthy(self) -> Optional[bool]:
        """检查设备是否需要更新（可选）"""
        if not self.client_version:
            return None
        # 这里可以添加版本检查逻辑
        return True

def get_tailscale_devices() -> List[TailscaleDevice]:
    """从Tailscale API获取所有设备信息"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"{TAILSCALE_API_BASE}/tailnet/{TAILNET}/devices"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        devices = [TailscaleDevice(d) for d in response.json().get("devices", [])]
        return devices
    except requests.exceptions.RequestException as e:
        logger.error(f"从Tailscale API获取设备失败: {e}")
        return []

@app.route('/health', methods=['GET'])
def health_overview():
    """返回所有设备的整体健康状态"""
    devices = get_tailscale_devices()
    if not devices:
        return jsonify({"error": "无法获取设备数据"}), 500
    
    # 计算全局健康状态
    global_healthy = all(d.online_healthy and d.key_healthy for d in devices)
    global_online_healthy = all(d.online_healthy for d in devices)
    global_key_healthy = all(d.key_healthy for d in devices)
    
    healthy_devices = [d.hostname for d in devices if d.online_healthy and d.key_healthy]
    unhealthy_devices = [d.hostname for d in devices if not (d.online_healthy and d.key_healthy)]
    
    return jsonify({
        "global_healthy": global_healthy,
        "global_online_healthy": global_online_healthy,
        "global_key_healthy": global_key_healthy,
        "healthy_devices": healthy_devices,
        "unhealthy_devices": unhealthy