# -*- coding: utf-8 -*-
"""
悟空飞书机器人服务端 v1.0
接收飞书消息 → 调用DeepSeek → 回复老板
"""
import json
import hashlib
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

# ── 配置 ─────────────────────────────────────────────────────────────────────
FEISHU_APP_ID        = "cli_a92effd632b85cd5"
FEISHU_APP_SECRET    = "agCdNI6zfbIjqMBAfF3cmeMzPkPhWFFq"
FEISHU_VERIFY_TOKEN  = ""   # 配置事件订阅后填入
FEISHU_ENCRYPT_KEY   = ""   # 可选，暂时留空

AI_API_KEY_PRIMARY   = "sk-lasvucwxlvjjxzmnyfdssmezwjwkycrotbnrtzhejfwfineo"
AI_API_KEY_BACKUP    = "sk-wngnqqegkuflnewxphmduagjskhesrafxxbhrwqpdahfyzaq"
AI_API_URL           = "https://api.siliconflow.cn/v1/chat/completions"
AI_MODEL             = "deepseek-ai/DeepSeek-V3"

MEMORY_FILE          = r"C:\Users\Administrator\.wukong\workspace\MEMORY.md"
HISTORY_FILE         = r"C:\Users\Administrator\.wukong\state\feishu_history.json"
PORT                 = 9919

os.makedirs(r"C:\Users\Administrator\.wukong\state", exist_ok=True)

# ── 全局变量 ──────────────────────────────────────────────────────────────────
_current_api_key = AI_API_KEY_PRIMARY
_processed_msg_ids = set()   # 防重复处理

# ── 飞书 Token ────────────────────────────────────────────────────────────────
_token_cache = {"token": "", "expire": 0}

def get_access_token():
    now = datetime.now().timestamp()
    if _token_cache["token"] and now < _token_cache["expire"] - 60:
        return _token_cache["token"]
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    )
    data = r.json()
    _token_cache["token"] = data.get("tenant_access_token", "")
    _token_cache["expire"] = now + data.get("expire", 7200)
    return _token_cache["token"]

# ── 发送飞书消息 ───────────────────────────────────────────────────────────────
def send_feishu_message(open_id, text):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    r = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        headers=headers,
        json=payload,
        timeout=10
    )
    return r.json()

# ── 对话历史 ──────────────────────────────────────────────────────────────────
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return []

def save_history(role, content):
    h = load_history()
    h.append({"role": role, "content": content})
    if len(h) > 40: h = h[-40:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

# ── 读取长期记忆 ──────────────────────────────────────────────────────────────
def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return f.read()[:2000]
    except: pass
    return ""

# ── 调用AI ────────────────────────────────────────────────────────────────────
def call_ai(user_msg):
    global _current_api_key
    memory = load_memory()

    sys_prompt = (
        "你是悟空，老板的私人AI生活秘书和数字分身。现在通过飞书和老板沟通。\n\n"
        "【铁律，必须遵守】\n"
        "1. 禁止输出 # ## 等井号标题，禁止 **粗体** 等Markdown符号，禁止 --- 分割线\n"
        "2. 禁止开场白，不说'好的！''当然！'，直接说结果\n"
        "3. 直接给最优方案，不列选项让老板选\n"
        "4. 口语化，短句，像真人发消息\n"
        "5. 需要分点用 1. 2. 3. 或 → 替代Markdown符号\n\n"
        f"【长期记忆】\n{memory}\n\n"
        "老板说'GO'就是立刻执行，说'没有'就是出问题了，说'好的'就是继续。"
    )

    msgs = [{"role": "system", "content": sys_prompt}]
    msgs.extend(load_history()[-10:])
    msgs.append({"role": "user", "content": user_msg})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_current_api_key}"
    }

    try:
        r = requests.post(
            AI_API_URL,
            headers=headers,
            json={"model": AI_MODEL, "messages": msgs, "stream": False},
            timeout=60
        )
        if r.status_code in (401, 403) and _current_api_key == AI_API_KEY_PRIMARY:
            print("主Key失效，切换备用Key")
            _current_api_key = AI_API_KEY_BACKUP
            headers["Authorization"] = f"Bearer {_current_api_key}"
            r = requests.post(AI_API_URL, headers=headers,
                              json={"model": AI_MODEL, "messages": msgs, "stream": False},
                              timeout=60)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            save_history("user", user_msg)
            save_history("assistant", reply)
            return reply
        else:
            return f"悟空暂时连不上，错误码 {r.status_code}，稍后再试"
    except Exception as e:
        return f"悟空出错了：{e}"

# ── 处理飞书事件 ──────────────────────────────────────────────────────────────
def handle_event(data):
    event_type = data.get("header", {}).get("event_type", "")

    if event_type == "im.message.receive_v1":
        event = data.get("event", {})
        msg = event.get("message", {})
        msg_id = msg.get("message_id", "")

        # 防重复
        if msg_id in _processed_msg_ids:
            return
        _processed_msg_ids.add(msg_id)
        if len(_processed_msg_ids) > 200:
            _processed_msg_ids.clear()

        # 只处理文本消息
        msg_type = msg.get("message_type", "")
        if msg_type != "text":
            return

        # 提取文字内容
        try:
            content = json.loads(msg.get("content", "{}"))
            text = content.get("text", "").strip()
        except:
            return

        if not text:
            return

        # 发送者
        sender = event.get("sender", {})
        open_id = sender.get("sender_id", {}).get("open_id", "")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到飞书消息: {text[:50]}")

        # 异步调用AI并回复
        def _reply():
            reply = call_ai(text)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 回复: {reply[:50]}")
            send_feishu_message(open_id, reply)

        threading.Thread(target=_reply, daemon=True).start()


# ── HTTP 服务器 ────────────────────────────────────────────────────────────────
class FeishuHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 关闭默认日志

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))

            # 飞书URL验证挑战
            if "challenge" in data:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"challenge": data["challenge"]}).encode())
                return

            # 正常事件
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"code":0}')

            # 异步处理
            threading.Thread(target=handle_event, args=(data,), daemon=True).start()

        except Exception as e:
            print(f"Handler错误: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("悟空飞书服务运行中".encode("utf-8"))


# ── 主入口 ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"悟空飞书服务启动，监听端口 {PORT}")
    print(f"本地地址: http://localhost:{PORT}")
    print("等待飞书消息...")
    server = HTTPServer(("0.0.0.0", PORT), FeishuHandler)
    server.serve_forever()
