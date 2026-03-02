# -*- coding: utf-8 -*-
"""
悟空飞书机器人服务端 v2.0 — Function Calling 版
接收飞书消息 → 悟空自主调工具 → 拿到真实结果 → 回复老板
"""
import json
import hashlib
import requests
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

# 加载工具箱
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)
try:
    from wukong_tools import TOOLS_SCHEMA, execute_tool
    TOOLS_ENABLED = True
    print("[悟空工具箱] 加载成功")
except ImportError as _e:
    TOOLS_ENABLED = False
    print(f"[悟空工具箱] 加载失败: {_e}")

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

# ── 调用AI（Function Calling 版）────────────────────────────────────────────
def call_ai(user_msg):
    global _current_api_key
    memory = load_memory()

    sys_prompt = (
        "你是悟空，老板的私人AI生活秘书和数字分身。现在通过飞书和老板沟通。\n"
        "你有真实工具，需要数据时先调工具，绝对不能编造结果。\n\n"
        "【工具使用规则 - 不可违反】\n"
        "1. 需要时间日期 → 调用 get_datetime，禁止从上下文推断时间\n"
        "2. 涉及EVOMAP → 调用 query_evomap，不要自己编\n"
        "3. 老板发来链接 → 调用 open_url 打开，不要猜内容\n"
        "4. 老板让记住某事 → 调用 write_memory 实际写入\n"
        "5. 需要发消息给别人 → 调用 send_feishu\n"
        "6. 不知道的问题 → 调用 search_web\n"
        "7. 老板要研究/分析/查资料某话题 → 调用 deep_research（比search_web全面10倍）\n\n"
        "【deep_research 使用时机】\n"
        "'帮我研究XXX' / '分析一下XXX' / '查查XXX行业' / '这个博主/品牌怎么样'\n"
        "→ 必须用 deep_research，它会自动搜多个角度给出完整报告\n\n"
        "【工具失败铁律】\n"
        "工具失败/搜不到 → 必须告诉老板'我搜不到'，禁止用训练知识悄悄补内容\n\n"
        "【回复格式】\n"
        "1. 禁止 # ## 井号标题，禁止 **粗体** Markdown，禁止 --- 分割线\n"
        "2. 禁止开场白，直接说结果\n"
        "3. 口语化短句，分点用 1. 2. 3. 或 →\n"
        "4. 工具有结果就说结果+证据，失败就说失败+原因\n"
        "5. 研究报告要注明来源\n\n"
        f"【长期记忆】\n{memory}\n\n"
        "老板说'GO'=立刻执行，'没有'=出问题了，'好的'=继续。"
    )

    msgs = [{"role": "system", "content": sys_prompt}]
    msgs.extend(load_history()[-10:])
    msgs.append({"role": "user", "content": user_msg})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_current_api_key}"
    }

    # Function Calling 循环（最多5轮）
    max_rounds = 5
    for _ in range(max_rounds):
        req_body = {"model": AI_MODEL, "messages": msgs, "stream": False}
        if TOOLS_ENABLED:
            req_body["tools"] = TOOLS_SCHEMA
            req_body["tool_choice"] = "auto"

        try:
            r = requests.post(AI_API_URL, headers=headers, json=req_body, timeout=90)
            if r.status_code in (401, 403) and _current_api_key == AI_API_KEY_PRIMARY:
                print("主Key失效，切换备用Key")
                _current_api_key = AI_API_KEY_BACKUP
                headers["Authorization"] = f"Bearer {_current_api_key}"
                r = requests.post(AI_API_URL, headers=headers, json=req_body, timeout=90)

            if r.status_code != 200:
                return f"悟空暂时连不上，错误码 {r.status_code}，稍后再试"

            resp = r.json()
            choice = resp["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")

            # 没有工具调用，返回最终答案
            if finish_reason != "tool_calls" or not message.get("tool_calls"):
                reply = message.get("content", "处理完成")
                save_history("user", user_msg)
                save_history("assistant", reply)
                return reply

            # 有工具调用，执行工具
            msgs.append(message)
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"].get("arguments", "{}"))
                except:
                    fn_args = {}
                tool_result = execute_tool(fn_name, fn_args)
                print(f"[工具] {fn_name} → {tool_result[:80]}")
                msgs.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": tool_result
                })

        except Exception as e:
            return f"悟空出错了：{e}"

    return "工具调用轮数超限，请换个方式问我。"

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
