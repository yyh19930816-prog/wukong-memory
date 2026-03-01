# -*- coding: utf-8 -*-
"""
悟空 EVOMAP 新节点注册脚本
当 hello 接口恢复后运行这个脚本，注册属于你的节点并获取激活码
"""
import requests, json, time, secrets, os
from datetime import datetime

EVOMAP_URL = "https://evomap.ai"

def register():
    new_node_id = "node_wk_" + secrets.token_hex(6)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"正在注册新节点: {new_node_id}")
    print(f"时间: {ts}")
    print()

    try:
        r = requests.post(f"{EVOMAP_URL}/a2a/hello", json={
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": "hello",
            "message_id": f"hello_{int(time.time())}_{secrets.token_hex(4)}",
            "sender_id": new_node_id,
            "timestamp": ts,
            "payload": {
                "capabilities": {
                    "secretary": True,
                    "communication": True,
                    "content": True,
                    "languages": ["zh", "en"]
                },
                "gene_count": 0,
                "capsule_count": 0,
                "env_fingerprint": {
                    "platform": "win32",
                    "arch": "x64",
                    "agent": "wukong-secretary-v2"
                }
            }
        }, timeout=30)

        print(f"HTTP 状态码: {r.status_code}")
        data = r.json()
        payload = data.get("payload", {})

        if r.status_code == 200 and payload.get("status") != "rejected":
            claim_code = payload.get("claim_code", "")
            claim_url = payload.get("claim_url", "")
            credit = payload.get("credit_balance", 0)

            print("=" * 50)
            print("注册成功！")
            print(f"节点ID:   {new_node_id}")
            print(f"激活码:   {claim_code}")
            print(f"激活链接: {claim_url}")
            print(f"初始积分: {credit}")
            print("=" * 50)
            print()
            print("下一步：")
            print("1. 打开激活链接，把节点绑定到你的 EVOMAP 账户")
            print("2. 绑定后悟空节点就拥有你账户的积分了")

            # 保存节点信息
            save_path = os.path.join(os.path.dirname(__file__), "wukong_node_new.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f"node_id={new_node_id}\n")
                f.write(f"claim_code={claim_code}\n")
                f.write(f"claim_url={claim_url}\n")
                f.write(f"registered_at={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"\n信息已保存到: {save_path}")

            # 更新工具箱里的节点ID
            tools_path = os.path.join(os.path.dirname(__file__), "wukong_tools.py")
            with open(tools_path, "r", encoding="utf-8") as f:
                content = f.read()
            old_node = 'EVOMAP_NODE_ID    = "node_wukong_001"'
            new_node = f'EVOMAP_NODE_ID    = "{new_node_id}"'
            if old_node in content:
                content = content.replace(old_node, new_node)
                with open(tools_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"工具箱节点ID已更新为: {new_node_id}")
            else:
                print(f"请手动把 wukong_tools.py 里的 EVOMAP_NODE_ID 改为: {new_node_id}")

            return True

        elif payload.get("status") == "rejected":
            reason = payload.get("reason", "未知原因")
            print(f"注册被拒绝: {reason}")
            return False
        else:
            print("未知响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return False

    except requests.exceptions.Timeout:
        print("连接超时 - EVOMAP hello 接口暂时不可用")
        print("请稍后重新运行此脚本")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("悟空 EVOMAP 节点注册工具")
    print("=" * 50)
    print()

    # 先检查服务器是否可用
    try:
        r = requests.get(f"{EVOMAP_URL}/a2a/stats", timeout=10)
        stats = r.json()
        print(f"EVOMAP 服务器状态: 正常")
        print(f"平台节点总数: {stats.get('total_nodes', '未知')}")
        print(f"平台资产总数: {stats.get('total_assets', '未知')}")
        print()
    except:
        print("EVOMAP 服务器当前不可达，请检查网络后重试")
        exit(1)

    register()
    input("\n按回车键退出...")
