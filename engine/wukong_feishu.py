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
        "7. 老板要研究/分析/查资料某话题 → 调用 deep_research（自动联合Google+GitHub）\n"
        "8. 遇到技术问题，找现成工具/代码 → 调用 search_github\n"
        "9. 想了解某个开源项目 → 调用 read_github_repo\n\n"
        "【工具选择逻辑】\n"
        "search_web → 查一条具体信息\n"
        "deep_research → 研究话题/竞品分析/行业趋势（自动联合Google+GitHub）\n"
        "search_github → 找开源工具/代码/解决方案\n"
        "read_github_repo → 了解某个项目的用法\n\n"
        "10. 完成有价值的任务后 → 判断是否产生可复用套路，若有则调用 write_capability\n\n"
        "【能力进化规则 - 自动执行】\n"
        "完成任务后问自己：'这个套路下次还能用吗？'\n"
        "是 → 调用 write_capability 记录能力轮廓，默默进化，不需汇报\n\n"
        "【工具失败铁律】\n"
        "工具失败/搜不到 → 必须告诉老板'我搜不到'，禁止用训练知识悄悄补内容\n\n"
        "【回复格式铁律 - 违反即错误】\n"
        "绝对禁止：**粗体**、# 标题、## 标题、--- 分割线、`代码块`\n"
        "绝对禁止任何Markdown符号，只用纯文字\n"
        "必须：1. 2. 3. 数字列表 或 → 箭头，禁止开场白，口语化短句\n"
        "研究报告注明来源（'来自虎嗅2026-03-01'）\n\n"
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
    tool_results_log = []  # 记录已调用的工具，用于强制拦截检查
    for round_n in range(max_rounds):
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

            # 没有工具调用，检查是否需要强制调工具
            if finish_reason != "tool_calls" or not message.get("tool_calls"):
                reply = message.get("content", "处理完成")

                # 强制拦截：涉及查询/搜索类但没调工具
                m = user_msg.lower()
                needs_tool = None
                if any(x in user_msg for x in ["http://", "https://"]):
                    needs_tool = "open_url"
                elif any(k in reply_text for k in ["现在几点", "今天几号", "几点了", "现在时间", "当前时间"]):
                    needs_tool = "get_datetime"
                elif any(k in reply_text for k in ["帮我打开", "读取文件", "打开文件"]):
                    needs_tool = "read_file"
                elif any(k in reply_text for k in [
                    "帮我搜", "帮我查", "帮我找", "搜一下", "查一下",
                    "找一下", "搜索一下", "去搜", "上网查",
                    "最新新闻", "最新消息", "最新动态", "最新趋势",
                    "搜资料", "查资料", "找资料",
                ]):
                    needs_tool = "search_web"

                if needs_tool and not tool_results_log and TOOLS_ENABLED and round_n == 0:
                    msgs.append({
                        "role": "user",
                        "content": f"[系统强制] 必须先调用 {needs_tool} 获取真实数据再回答。立刻执行。"
                    })
                    continue  # 只拦截一次

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
                tool_results_log.append(fn_name)
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
