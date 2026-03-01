# -*- coding: utf-8 -*-
"""
悟空工具箱 — wukong_tools.py
给悟空配备真实可执行的工具，每个工具都返回真实结果。
用于 Function Calling，悟空自主决定用哪个工具。
"""
import os, json, time, requests
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────────────────────────────
FEISHU_APP_ID     = "cli_a92effd632b85cd5"
FEISHU_APP_SECRET = "agCdNI6zfbIjqMBAfF3cmeMzPkPhWFFq"
EVOMAP_URL        = "https://evomap.ai"
EVOMAP_NODE_ID    = "node_wukong_001"
MEMORY_LONG       = r"C:\Users\Administrator\.wukong\workspace\MEMORY.md"
TOOLS_MD          = r"C:\Users\Administrator\.wukong\workspace\TOOLS.md"
WORKSPACE_DIR     = r"C:\Users\Administrator\.wukong\workspace"

# ── 飞书 token 缓存 ────────────────────────────────────────────────────────────
_feishu_token = None
_feishu_token_expire = 0

def _get_feishu_token():
    global _feishu_token, _feishu_token_expire
    if _feishu_token and time.time() < _feishu_token_expire - 60:
        return _feishu_token
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    )
    d = r.json()
    if d.get("code") == 0:
        _feishu_token = d["tenant_access_token"]
        _feishu_token_expire = time.time() + d.get("expire", 7200)
        return _feishu_token
    return None

# ══════════════════════════════════════════════════════════════════════════════
# 工具实现（每个函数返回字符串结果，悟空读取后用中文回答老板）
# ══════════════════════════════════════════════════════════════════════════════

def tool_get_datetime() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    wd = weekdays[now.weekday()]
    return f"{now.strftime('%Y年%m月%d日')} {wd} {now.strftime('%H:%M:%S')}"


def tool_read_memory(filename: str = "MEMORY.md") -> str:
    """
    读取记忆文件内容
    filename: 文件名，如 MEMORY.md / TOOLS.md / SOUL.md / AGENTS.md / HEARTBEAT.md
              或日期如 2026-03-01（读当日对话记录）
    """
    safe_names = {
        "MEMORY.md": MEMORY_LONG,
        "TOOLS.md": TOOLS_MD,
        "SOUL.md": os.path.join(WORKSPACE_DIR, "SOUL.md"),
        "AGENTS.md": os.path.join(WORKSPACE_DIR, "AGENTS.md"),
        "HEARTBEAT.md": os.path.join(WORKSPACE_DIR, "HEARTBEAT.md"),
    }
    # 日期格式，读当日 memory
    if len(filename) == 10 and filename[4] == '-':
        path = os.path.join(WORKSPACE_DIR, "memory", f"{filename}.md")
    else:
        path = safe_names.get(filename, "")

    if not path or not os.path.exists(path):
        return f"文件不存在：{filename}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:3000] if len(content) > 3000 else content
    except Exception as e:
        return f"读取失败：{e}"


def tool_write_memory(content: str, section: str = "新增记录") -> str:
    """
    追加内容到 MEMORY.md（老板的偏好/教训/重要信息）
    content: 要写入的内容
    section: 段落标题
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## [{ts}] {section}\n{content}\n"
    try:
        os.makedirs(os.path.dirname(MEMORY_LONG), exist_ok=True)
        with open(MEMORY_LONG, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"已写入 MEMORY.md — 段落：{section}，时间：{ts}"
    except Exception as e:
        return f"写入失败：{e}"


def tool_query_evomap(action: str = "heartbeat") -> str:
    """
    查询或更新 EVOMAP.AI 网络
    action:
      - heartbeat: 发送心跳，返回当前状态和积分
      - fetch_skills: 拉取推荐技能列表
    """
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    mid = f"wk_{int(time.time())}"

    if action == "heartbeat":
        payload = {
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": "heartbeat",
            "message_id": mid,
            "sender_id": EVOMAP_NODE_ID,
            "timestamp": ts,
            "payload": {
                "status": "alive",
                "metrics": {"tasks_completed": 0, "uptime_seconds": int(time.time())}
            }
        }
        try:
            r = requests.post(f"{EVOMAP_URL}/a2a/heartbeat", json=payload, timeout=15)
            data = r.json()
            code = data.get("code", data.get("status", "unknown"))
            credit = data.get("credit_balance", data.get("payload", {}).get("credit_balance", "未知"))
            if r.status_code == 200:
                return f"EVOMAP心跳成功 | HTTP {r.status_code} | code:{code} | 积分:{credit} | 时间:{ts}"
            else:
                return f"EVOMAP心跳返回异常 | HTTP {r.status_code} | 原始响应:{r.text[:300]}"
        except requests.exceptions.ConnectionError:
            return "EVOMAP连接失败：服务器无法访问（ConnectionError）"
        except requests.exceptions.Timeout:
            return "EVOMAP连接超时：15秒无响应"
        except Exception as e:
            return f"EVOMAP请求异常：{e}"

    elif action == "fetch_skills":
        payload = {
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": "fetch",
            "message_id": mid,
            "sender_id": EVOMAP_NODE_ID,
            "timestamp": ts,
            "payload": {"filter": {"tags": ["secretary", "assistant", "communication", "content"]}}
        }
        try:
            r = requests.post(f"{EVOMAP_URL}/a2a/fetch", json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                assets = data.get("payload", {}).get("assets", [])
                if not assets:
                    return f"EVOMAP返回空技能列表 | HTTP 200 | 原始:{r.text[:200]}"
                lines = [f"EVOMAP技能列表（共{len(assets)}个）："]
                for a in assets[:8]:
                    lines.append(f"- {a.get('name','未命名')} | {a.get('description','')[:60]}")
                return "\n".join(lines)
            else:
                return f"EVOMAP拉取技能失败 | HTTP {r.status_code} | {r.text[:300]}"
        except requests.exceptions.ConnectionError:
            return "EVOMAP连接失败：服务器无法访问（ConnectionError）"
        except requests.exceptions.Timeout:
            return "EVOMAP连接超时"
        except Exception as e:
            return f"EVOMAP请求异常：{e}"

    return f"未知action：{action}，支持的action：heartbeat / fetch_skills"


def tool_send_feishu(message: str, chat_id: str = "") -> str:
    """
    通过飞书机器人发送消息
    message: 消息内容
    chat_id: 群或用户的chat_id（空则发到默认群）
    """
    token = _get_feishu_token()
    if not token:
        return "飞书token获取失败，请检查App ID和Secret"

    # 读取保存的默认chat_id
    default_chat_file = os.path.join(WORKSPACE_DIR, ".feishu_default_chat")
    if not chat_id and os.path.exists(default_chat_file):
        try:
            with open(default_chat_file, "r") as f:
                chat_id = f.read().strip()
        except:
            pass

    if not chat_id:
        return "没有指定飞书chat_id，也没有默认群。请先告诉我发给谁。"

    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            params={"receive_id_type": "chat_id"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": message})
            },
            timeout=15
        )
        d = r.json()
        if d.get("code") == 0:
            msg_id = d.get("data", {}).get("message_id", "")
            return f"飞书消息发送成功 | code:0 | message_id:{msg_id}"
        else:
            return f"飞书发送失败 | code:{d.get('code')} | msg:{d.get('msg')} | 原始:{r.text[:200]}"
    except Exception as e:
        return f"飞书发送异常：{e}"


def tool_search_web(query: str) -> str:
    """
    搜索网络，获取真实信息
    query: 搜索关键词
    """
    try:
        # 使用 DuckDuckGo 即时搜索 API（无需key）
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 WukongBot/1.0"}
        )
        data = r.json()
        abstract = data.get("AbstractText", "")
        abstract_url = data.get("AbstractURL", "")
        related = data.get("RelatedTopics", [])[:3]

        lines = [f"搜索：{query}"]
        if abstract:
            lines.append(f"摘要：{abstract[:300]}")
            if abstract_url:
                lines.append(f"来源：{abstract_url}")
        if related:
            lines.append("相关：")
            for t in related:
                if isinstance(t, dict) and t.get("Text"):
                    lines.append(f"- {t['Text'][:100]}")
        if len(lines) == 1:
            lines.append("没有找到直接摘要，可能需要更具体的关键词")
        return "\n".join(lines)
    except Exception as e:
        return f"搜索失败：{e}"


def tool_list_files(directory: str = "workspace") -> str:
    """
    列出目录下的文件
    directory: workspace / memory / engine / hud
    """
    base = r"C:\Users\Administrator\.wukong"
    dir_map = {
        "workspace": os.path.join(base, "workspace"),
        "memory": os.path.join(base, "workspace", "memory"),
        "engine": r"E:\CURSOR\wukong-memory\engine",
        "hud": r"E:\CURSOR\wukong-memory\hud",
    }
    path = dir_map.get(directory, os.path.join(base, directory))
    if not os.path.exists(path):
        return f"目录不存在：{directory}"
    try:
        files = os.listdir(path)
        if not files:
            return f"{directory}/ 目录为空"
        return f"{directory}/ 目录文件列表：\n" + "\n".join(f"- {f}" for f in sorted(files))
    except Exception as e:
        return f"列目录失败：{e}"


# ══════════════════════════════════════════════════════════════════════════════
# Function Calling 工具定义（OpenAI格式，DeepSeek-V3支持）
# ══════════════════════════════════════════════════════════════════════════════
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "获取当前日期和时间",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_memory",
            "description": "读取悟空的记忆文件，包括老板偏好、历史对话、技能手册等",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名：MEMORY.md / TOOLS.md / SOUL.md / AGENTS.md / HEARTBEAT.md，或日期如2026-03-01"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_memory",
            "description": "把重要信息/教训/老板偏好写入长期记忆（MEMORY.md）",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "要写入的内容"},
                    "section": {"type": "string", "description": "段落标题，如：老板偏好 / 教训 / 客户信息"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_evomap",
            "description": "查询或更新EVOMAP.AI进化网络，发送心跳或拉取技能",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["heartbeat", "fetch_skills"],
                        "description": "heartbeat=发心跳检查状态和积分，fetch_skills=拉取推荐技能列表"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_feishu",
            "description": "通过飞书机器人发送消息给老板或群",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "消息内容"},
                    "chat_id": {"type": "string", "description": "飞书chat_id，不知道就留空"}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索网络获取实时信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录下的文件，了解当前有哪些记忆/工具文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "enum": ["workspace", "memory", "engine", "hud"],
                        "description": "要查看的目录"
                    }
                },
                "required": []
            }
        }
    }
]

# ══════════════════════════════════════════════════════════════════════════════
# 工具调度器（根据函数名调用对应工具，返回结果字符串）
# ══════════════════════════════════════════════════════════════════════════════
TOOL_DISPATCH = {
    "get_datetime":  lambda args: tool_get_datetime(),
    "read_memory":   lambda args: tool_read_memory(args.get("filename", "MEMORY.md")),
    "write_memory":  lambda args: tool_write_memory(args.get("content", ""), args.get("section", "新增记录")),
    "query_evomap":  lambda args: tool_query_evomap(args.get("action", "heartbeat")),
    "send_feishu":   lambda args: tool_send_feishu(args.get("message", ""), args.get("chat_id", "")),
    "search_web":    lambda args: tool_search_web(args.get("query", "")),
    "list_files":    lambda args: tool_list_files(args.get("directory", "workspace")),
}

def execute_tool(name: str, arguments: dict) -> str:
    """调度并执行工具，返回结果字符串"""
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return f"未知工具：{name}"
    try:
        return fn(arguments)
    except Exception as e:
        return f"工具执行出错 [{name}]：{e}"
