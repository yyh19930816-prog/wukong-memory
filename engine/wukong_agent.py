# -*- coding: utf-8 -*-
"""
悟空自主Agent引擎 — wukong_agent.py
24小时自主学习与进化，老板有消息立刻切换优先执行。

核心逻辑：
  默认状态 → 自主学习循环（三方向轮流）
  老板消息 → 立刻打断，优先处理
  任务完成 → 自动回到学习状态
"""
import os, json, time, requests, threading, sys
from datetime import datetime, timedelta

# ── 加载工具箱 ────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
from wukong_tools import (
    execute_tool, TOOLS_SCHEMA,
    MEMORY_LONG, WORKSPACE_DIR,
    EVOMAP_NODE_ID, EVOMAP_URL
)

# ── 配置 ──────────────────────────────────────────────────────────────────────
API_KEY_PRIMARY  = "sk-lasvucwxlvjjxzmnyfdssmezwjwkycrotbnrtzhejfwfineo"
API_KEY_BACKUP   = "sk-wngnqqegkuflnewxphmduagjskhesrafxxbhrwqpdahfyzaq"
API_URL          = "https://api.siliconflow.cn/v1/chat/completions"
MODEL            = "deepseek-ai/DeepSeek-V3"
STATE_DIR        = r"C:\Users\Administrator\.wukong\state"
AGENT_LOG        = os.path.join(STATE_DIR, "agent_log.json")
AGENT_STATE_FILE = os.path.join(STATE_DIR, "agent_state.json")
FEISHU_HIST      = os.path.join(STATE_DIR, "feishu_history.json")
CHAT_HIST        = os.path.join(STATE_DIR, "chat_history.json")

os.makedirs(STATE_DIR, exist_ok=True)

# 自学循环间隔（秒）
LEARN_INTERVAL   = 900   # 15分钟自学一次
HEARTBEAT_INTERVAL = 900  # 15分钟心跳一次
CHECK_MSG_INTERVAL = 30   # 30秒检查一次新消息

# ── 全局状态 ──────────────────────────────────────────────────────────────────
_api_key = API_KEY_PRIMARY
_stop_event = threading.Event()
_learning_lock = threading.Lock()

# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    # 写日志文件
    try:
        logs = []
        if os.path.exists(AGENT_LOG):
            with open(AGENT_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append({"ts": ts, "level": level, "msg": msg})
        logs = logs[-500:]  # 只保留最近500条
        with open(AGENT_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except:
        pass


def load_memory(max_chars=2000):
    try:
        if os.path.exists(MEMORY_LONG):
            with open(MEMORY_LONG, "r", encoding="utf-8") as f:
                return f.read()[:max_chars]
    except:
        pass
    return ""


def load_recent_chat(n=20):
    """加载最近n条对话历史"""
    try:
        if os.path.exists(CHAT_HIST):
            with open(CHAT_HIST, "r", encoding="utf-8") as f:
                h = json.load(f)
            return h[-n:]
    except:
        pass
    return []


def save_agent_state(state: dict):
    try:
        with open(AGENT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except:
        pass


def load_agent_state() -> dict:
    try:
        if os.path.exists(AGENT_STATE_FILE):
            with open(AGENT_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {
        "last_learn": {"secretary": 0, "avatar": 0, "content": 0},
        "learn_count": {"secretary": 0, "avatar": 0, "content": 0},
        "total_learns": 0,
        "last_heartbeat": 0,
        "started_at": datetime.now().isoformat()
    }


def write_learn_result(direction: str, summary: str):
    """把自学结果写进当日记忆"""
    today = datetime.now().strftime("%Y-%m-%d")
    mem_dir = os.path.join(WORKSPACE_DIR, "memory")
    os.makedirs(mem_dir, exist_ok=True)
    mem_file = os.path.join(mem_dir, f"{today}.md")
    ts = datetime.now().strftime("%H:%M")
    dir_names = {"secretary": "秘书大师", "avatar": "沟通分身", "content": "内容执行"}
    entry = (
        f"\n## [{ts}] 自主学习记录 — {dir_names.get(direction, direction)}\n"
        f"{summary}\n"
    )
    try:
        with open(mem_file, "a", encoding="utf-8") as f:
            f.write(entry)
        log(f"学习记录已写入 {today}.md")
    except Exception as e:
        log(f"写学习记录失败: {e}", "WARN")


# ══════════════════════════════════════════════════════════════════════════════
# AI 调用（带 Function Calling）
# ══════════════════════════════════════════════════════════════════════════════

def call_ai(messages: list, task_desc: str = "") -> str:
    """调用AI，支持Function Calling，返回最终文本回复"""
    global _api_key

    memory = load_memory()
    sys_prompt = (
        "你是悟空，老板的私人AI秘书和数字分身。现在处于自主学习模式。\n"
        "你有真实工具可以调用，需要信息时先调工具，不要编造。\n\n"
        "【回复格式】不用井号标题，不用Markdown，口语化短句。\n"
        "【工具使用】需要数据时调工具，拿到真实结果再说。\n\n"
        f"【长期记忆】\n{memory}"
    )

    msgs = [{"role": "system", "content": sys_prompt}] + messages
    max_rounds = 5

    for _ in range(max_rounds):
        hdrs = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_api_key}"
        }
        req = {
            "model": MODEL,
            "messages": msgs,
            "stream": False,
            "tools": TOOLS_SCHEMA,
            "tool_choice": "auto"
        }
        try:
            r = requests.post(API_URL, headers=hdrs, json=req, timeout=90)
            if r.status_code in (401, 403) and _api_key == API_KEY_PRIMARY:
                log("主Key失效，切换备用Key", "WARN")
                _api_key = API_KEY_BACKUP
                hdrs["Authorization"] = f"Bearer {_api_key}"
                r = requests.post(API_URL, headers=hdrs, json=req, timeout=90)

            if r.status_code != 200:
                log(f"AI调用失败 HTTP {r.status_code}", "ERROR")
                return ""

            choice = r.json()["choices"][0]
            message = choice["message"]
            finish = choice.get("finish_reason", "stop")

            if finish != "tool_calls" or not message.get("tool_calls"):
                return message.get("content", "")

            # 执行工具
            msgs.append(message)
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"].get("arguments", "{}"))
                except:
                    fn_args = {}
                result = execute_tool(fn_name, fn_args)
                log(f"工具调用: {fn_name} → {result[:80]}")
                msgs.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": result
                })
        except Exception as e:
            log(f"AI调用异常: {e}", "ERROR")
            return ""

    return ""


# ══════════════════════════════════════════════════════════════════════════════
# 三大方向自学任务
# ══════════════════════════════════════════════════════════════════════════════

def learn_secretary():
    """秘书大师方向：整理记忆、优化工作流程、提炼老板偏好"""
    log("开始自学 → 秘书大师方向")

    recent = load_recent_chat(30)
    chat_summary = ""
    if recent:
        lines = []
        for m in recent[-10:]:
            role = "老板" if m.get("role") == "user" else "悟空"
            lines.append(f"{role}：{m.get('content','')[:80]}")
        chat_summary = "\n".join(lines)

    prompt = f"""你现在处于自主学习模式，方向：秘书大师。

任务：分析最近10条对话，自主完成以下工作：
1. 提炼老板的工作习惯和偏好（有什么新发现就写，没有就跳过）
2. 检查自己的回复质量（有没有废话、有没有格式问题）
3. 发现任何需要改进的地方，调用 write_memory 工具记录下来
4. 给自己打一个自评分（0-10分）并说明原因

最近对话记录：
{chat_summary if chat_summary else "（暂无对话记录）"}

直接开始工作，不需要解释你在做什么。完成后给我一个简短的学习总结。"""

    result = call_ai([{"role": "user", "content": prompt}], "秘书自学")
    if result:
        write_learn_result("secretary", result)
        log(f"秘书自学完成：{result[:100]}")
    return result


def learn_avatar():
    """沟通分身方向：分析老板说话风格，积累模仿素材"""
    log("开始自学 → 沟通分身方向")

    recent = load_recent_chat(50)
    user_msgs = [m["content"] for m in recent if m.get("role") == "user"]

    prompt = f"""你现在处于自主学习模式，方向：沟通分身。

任务：研究老板的说话风格，完成以下工作：
1. 分析老板的用词习惯（短句/长句？口语化程度？惯用词？）
2. 提炼3-5个老板的典型表达方式，写进记忆
3. 练习：用老板风格改写一句话（随便选一个你觉得有意思的场景）
4. 评估你模仿老板说话的准确度（0-10分）

老板说过的话（最近）：
{chr(10).join(f'- {m[:60]}' for m in user_msgs[-15:]) if user_msgs else '（暂无数据）'}

直接开始，完成后给简短总结。"""

    result = call_ai([{"role": "user", "content": prompt}], "分身自学")
    if result:
        write_learn_result("avatar", result)
        log(f"分身自学完成：{result[:100]}")
    return result


def learn_content():
    """内容执行方向：搜索行业资讯，练习文案改写"""
    log("开始自学 → 内容执行方向")

    prompt = """你现在处于自主学习模式，方向：内容执行。

任务：主动学习内容创作技能，完成以下工作：
1. 调用 search_web 搜索一个你认为老板可能关心的话题（自己选，比如AI行业动态、商业趋势等）
2. 把搜索结果改写成老板风格的简短文案（100字以内，口语化）
3. 思考：这个内容老板会不会感兴趣？为什么？
4. 把有价值的内容写进记忆

直接开始，先搜索，再改写，最后总结。"""

    result = call_ai([{"role": "user", "content": prompt}], "内容自学")
    if result:
        write_learn_result("content", result)
        log(f"内容自学完成：{result[:100]}")
    return result


def learn_self_review():
    """每天一次深度自我检查：我哪里还不够好？"""
    log("开始自主深度复盘")

    today = datetime.now().strftime("%Y-%m-%d")
    mem_dir = os.path.join(WORKSPACE_DIR, "memory")
    today_log = ""
    try:
        f_path = os.path.join(mem_dir, f"{today}.md")
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as f:
                today_log = f.read()[:2000]
    except:
        pass

    prompt = f"""你现在处于自主深度复盘模式。

今天的学习记录：
{today_log if today_log else '（今天还没有学习记录）'}

任务：
1. 今天学了什么？真的学到东西了吗？
2. 我在哪个方向最弱？为什么？
3. 明天重点练什么？（具体一点，不能说"继续努力"这种废话）
4. 有没有发现自己之前说错了或者做错了的地方？主动写出来
5. 调用 write_memory 把复盘结论写进记忆，标题用"每日复盘"

直接开始复盘，不要废话。"""

    result = call_ai([{"role": "user", "content": prompt}], "深度复盘")
    if result:
        write_learn_result("secretary", f"每日复盘：\n{result}")
        log(f"深度复盘完成：{result[:100]}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 老板消息检测
# ══════════════════════════════════════════════════════════════════════════════

_last_msg_count = 0

def check_new_boss_message() -> bool:
    """检查是否有新消息（HUD对话或飞书）"""
    global _last_msg_count
    try:
        if os.path.exists(CHAT_HIST):
            with open(CHAT_HIST, "r", encoding="utf-8") as f:
                hist = json.load(f)
            current_count = len([m for m in hist if m.get("role") == "user"])
            if current_count > _last_msg_count:
                _last_msg_count = current_count
                return True
            _last_msg_count = current_count
    except:
        pass
    return False


# ══════════════════════════════════════════════════════════════════════════════
# EVOMAP 心跳
# ══════════════════════════════════════════════════════════════════════════════

def do_heartbeat():
    try:
        import time as _time
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        r = requests.post(f"{EVOMAP_URL}/a2a/heartbeat", json={
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": "heartbeat",
            "message_id": f"hb_{int(_time.time())}",
            "sender_id": EVOMAP_NODE_ID,
            "timestamp": ts,
            "payload": {"status": "alive", "metrics": {"tasks_completed": 0, "uptime_seconds": int(_time.time())}}
        }, timeout=15)
        data = r.json()
        credit = data.get("credit_balance", "?")
        log(f"EVOMAP心跳 | HTTP {r.status_code} | 积分: {credit}")
    except Exception as e:
        log(f"EVOMAP心跳失败: {e}", "WARN")


# ══════════════════════════════════════════════════════════════════════════════
# 自主循环主引擎
# ══════════════════════════════════════════════════════════════════════════════

LEARN_TASKS = [
    ("secretary", learn_secretary),
    ("avatar",    learn_avatar),
    ("content",   learn_content),
]


def pick_next_direction(state: dict) -> tuple:
    """根据上次学习时间，选最久没练的方向"""
    now = time.time()
    last = state.get("last_learn", {})
    # 找最久没学的方向
    oldest_dir = min(LEARN_TASKS, key=lambda x: last.get(x[0], 0))
    return oldest_dir


def run_learning_cycle(state: dict):
    """执行一轮自学"""
    direction, task_fn = pick_next_direction(state)
    dir_names = {"secretary": "秘书大师", "avatar": "沟通分身", "content": "内容执行"}
    log(f"自学循环开始 → {dir_names[direction]}")

    with _learning_lock:
        try:
            task_fn()
            state["last_learn"][direction] = time.time()
            state["learn_count"][direction] = state["learn_count"].get(direction, 0) + 1
            state["total_learns"] = state.get("total_learns", 0) + 1
            save_agent_state(state)
        except Exception as e:
            log(f"自学任务出错: {e}", "ERROR")

    # 每学完5次，做一次深度复盘
    if state.get("total_learns", 0) % 5 == 0 and state.get("total_learns", 0) > 0:
        log("触发深度复盘（每5次自学一次）")
        learn_self_review()


def main_loop():
    """主循环：消息检测 + 自学 + 心跳，24小时不停"""
    log("=" * 50)
    log("悟空自主Agent引擎启动")
    log("模式：24小时自主学习 + 随时响应老板")
    log("=" * 50)

    state = load_agent_state()
    state["started_at"] = datetime.now().isoformat()
    save_agent_state(state)

    # 初始化消息计数
    global _last_msg_count
    try:
        if os.path.exists(CHAT_HIST):
            with open(CHAT_HIST, "r", encoding="utf-8") as f:
                hist = json.load(f)
            _last_msg_count = len([m for m in hist if m.get("role") == "user"])
    except:
        pass

    last_learn_time = 0
    last_heartbeat_time = 0
    last_review_date = ""

    while not _stop_event.is_set():
        now = time.time()
        today = datetime.now().strftime("%Y-%m-%d")

        # 1. 检查老板新消息（优先级最高）
        if check_new_boss_message():
            log("检测到老板新消息，学习暂停，等待HUD处理")
            # HUD会处理消息，这里只是记录一下
            time.sleep(CHECK_MSG_INTERVAL)
            continue

        # 2. EVOMAP心跳
        if now - last_heartbeat_time >= HEARTBEAT_INTERVAL:
            do_heartbeat()
            last_heartbeat_time = now

        # 3. 自学循环
        if now - last_learn_time >= LEARN_INTERVAL:
            run_learning_cycle(state)
            last_learn_time = now

        # 4. 每天一次深度复盘（凌晨3点）
        hour = datetime.now().hour
        if hour == 3 and last_review_date != today:
            log("触发每日深度复盘（凌晨3点）")
            learn_self_review()
            last_review_date = today

        # 每30秒检查一次消息
        time.sleep(CHECK_MSG_INTERVAL)

    log("悟空自主Agent引擎已停止")


# ══════════════════════════════════════════════════════════════════════════════
# 状态查询接口（供HUD调用）
# ══════════════════════════════════════════════════════════════════════════════

def get_status() -> dict:
    """返回当前Agent状态"""
    state = load_agent_state()
    dir_names = {"secretary": "秘书大师", "avatar": "沟通分身", "content": "内容执行"}
    last = state.get("last_learn", {})
    result = {
        "running": not _stop_event.is_set(),
        "total_learns": state.get("total_learns", 0),
        "started_at": state.get("started_at", ""),
        "directions": {}
    }
    for d, name in dir_names.items():
        t = last.get(d, 0)
        if t:
            mins = int((time.time() - t) / 60)
            last_str = f"{mins}分钟前"
        else:
            last_str = "从未"
        result["directions"][d] = {
            "name": name,
            "count": state.get("learn_count", {}).get(d, 0),
            "last": last_str
        }
    return result


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log("收到停止信号，Agent关闭")
        _stop_event.set()
