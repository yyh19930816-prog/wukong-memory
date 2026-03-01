# -*- coding: utf-8 -*-
"""
悟空 EVOMAP 心跳保活程序
每15分钟发送心跳，保持悟空在EVOMAP网络在线
"""
import requests
import json
import time
import threading
from datetime import datetime

NODE_ID   = "node_wukong_001"
HUB_URL   = "https://evomap.ai"
INTERVAL  = 900   # 15分钟

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] EVOMAP {msg}")

def heartbeat():
    payload = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "heartbeat",
        "message_id": f"hb_{int(time.time())}",
        "sender_id": NODE_ID,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "status": "alive",
            "metrics": {
                "tasks_completed": 0,
                "uptime_seconds": int(time.time())
            }
        }
    }
    try:
        r = requests.post(f"{HUB_URL}/a2a/heartbeat",
                          json=payload, timeout=10)
        data = r.json()
        credits = data.get("payload", {}).get("credit_balance", "?")
        log(f"心跳成功 | 积分: {credits}")
        return True
    except Exception as e:
        log(f"心跳失败: {e}")
        return False

def run():
    log("悟空 EVOMAP 保活程序启动")
    log(f"节点: {NODE_ID} | 心跳间隔: {INTERVAL}秒")
    while True:
        heartbeat()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    run()
