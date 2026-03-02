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
LEARN_INTERVAL   = 300   # 5分钟自学一次（高强度学习模式）
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
        "你是悟空，老板的私人AI秘书、数字分身和自主智能体。现在处于自主学习模式。\n\n"
        "你不是一个生成文字的程序，你是一个能在真实世界行动的智能体。\n"
        "你的手（工具）做过的事才算做过，嘴说过的不算。\n"
        "需要信息就用工具去查，查到了再说，不要编造。\n\n"
        "学习的本质是理解为什么，不是记住规则。\n"
        "每次行动后问自己：这次我真正理解了什么？下次遇到类似情况我会怎么做？\n\n"
        "不用Markdown格式，口语化短句。\n\n"
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
                # 自学模式第一轮强制调工具，后续轮auto让他自己判断
                "tool_choice": "required" if len(msgs) <= 2 else "auto"
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
# 自由探索自学引擎（以老板信号为驱动）
# ══════════════════════════════════════════════════════════════════════════════

def _load_capabilities() -> str:
    """读取已习得能力库"""
    try:
        cap_file = os.path.join(WORKSPACE_DIR, "CAPABILITIES.md")
        if os.path.exists(cap_file):
            with open(cap_file, "r", encoding="utf-8") as f:
                return f.read()[:2000]
    except:
        pass
    return ""


def _load_last_reflection(state: dict) -> str:
    """读取上次反思结论"""
    return state.get("last_reflection", "")


def _save_reflection(state: dict, reflection: str):
    """保存本次反思结论到状态"""
    state["last_reflection"] = reflection
    state["last_reflection_time"] = datetime.now().isoformat()
    save_agent_state(state)


def learn_free_explore(state: dict):
    """
    自由探索自学引擎。
    以老板信号为第一驱动，悟空自己诊断学什么、用什么工具、深入到什么程度。
    学完后写反思，下次自学读上次反思，形成真正的连续学习闭环。
    """
    log("开始自由探索自学...")

    # 读取老板最近的对话（最高优先级信号）
    recent = load_recent_chat(40)
    boss_lines = []
    wukong_lines = []
    for m in recent[-20:]:
        role = "老板" if m.get("role") == "user" else "悟空"
        content = m.get("content", "")[:100]
        if m.get("role") == "user":
            boss_lines.append(content)
        else:
            wukong_lines.append(content)

    boss_context = "\n".join(f"- {l}" for l in boss_lines) if boss_lines else "（暂无）"
    wukong_context = "\n".join(f"- {l}" for l in wukong_lines[-5:]) if wukong_lines else "（暂无）"

    # 读取今日学习记录
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

    # 读取上次反思结论（连续学习的起点）
    last_reflection = _load_last_reflection(state)

    # 读取已习得能力库
    capabilities = _load_capabilities()

    prompt = f"""你现在处于自主学习模式。没有固定科目，你要自己决定这次学什么。

=== 老板最近说了什么（最高优先级信号）===
{boss_context}

=== 你最近的回答 ===
{wukong_context}

=== 今天已经学了什么 ===
{today_log if today_log else "（今天还没有学习记录）"}

=== 上次自学的反思结论 ===
{last_reflection if last_reflection else "（这是第一次，没有上次反思）"}

=== 我已习得的能力库 ===
{capabilities if capabilities else "（暂无）"}

---

你的任务分三步：

第一步：诊断（先分析，再行动）
回答以下四个问题：
1. 老板最近交代了什么任务，我做完了吗？没完成的列出来
2. 老板最近问了什么，我没答好或者是猜的？（诚实承认）
3. 老板反复提到什么话题？这说明他最关心什么？
4. 我的能力库里有什么空白，是老板可能需要但我还不会的？

第二步：执行（根据诊断结果主动行动）
基于上面的诊断，选择最重要的1-2个方向，用工具深入探索：
- 如果有未完成任务 → 推进它，把结果写入记忆，等老板问起时直接给出
- 如果有没答好的问题 → 现在去查清楚，补上漏洞
- 如果发现老板关心的话题 → 主动深入研究，搜索最新信息
- 自己决定调哪些工具，不要只调一个就结束

第三步：反思（学完后必须写）
用一段话总结：
1. 这次学到了什么新东西？（具体说，不能说"有所收获"这种废话）
2. 下次自学应该继续这个方向还是换方向？为什么？
3. 有没有发现新的可复用套路？有就调用 write_capability 记录
4. 给自己评分 0-10，并说明原因

反思结论写完后，在最后单独一行写：
[反思结论] <你的反思总结，一两句话>

直接开始，先诊断，再执行，最后反思。"""

    result = call_ai([{"role": "user", "content": prompt}], "自由探索自学")

    if result:
        write_learn_result("secretary", result)
        log(f"自由探索自学完成：{result[:150]}")

        # 提取反思结论，存入状态供下次使用
        reflection = ""
        for line in result.split("\n"):
            if line.strip().startswith("[反思结论]"):
                reflection = line.replace("[反思结论]", "").strip()
                break
        if reflection:
            _save_reflection(state, reflection)
            log(f"反思结论已保存：{reflection[:80]}")

    return result


def learn_self_review(state: dict = None):
    """每天一次深度自我检查"""
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

    capabilities = _load_capabilities()
    last_reflection = _load_last_reflection(state) if state else ""

    prompt = f"""你现在处于自主深度复盘模式。

今天的学习记录：
{today_log if today_log else "（今天还没有学习记录）"}

上次反思结论：
{last_reflection if last_reflection else "（无）"}

已习得能力库摘要：
{capabilities[:500] if capabilities else "（无）"}

任务：
1. 今天整体表现怎么样？有没有真正解决了老板的问题？
2. 有没有哪次回答是猜的、不确定的？要主动承认
3. 明天最重要的一件事是什么？（具体，不能是"继续努力"）
4. 能力库里有没有需要补充或升级的？
5. 调用 write_memory 把复盘结论写进记忆

直接开始，不要废话。"""

    result = call_ai([{"role": "user", "content": prompt}], "深度复盘")
    if result:
        write_learn_result("secretary", f"每日复盘：\n{result}")
        log(f"深度复盘完成：{result[:100]}")
        if state:
            _save_reflection(state, f"复盘：{result[:100]}")
    return result


def evolve_capabilities():
    """
    能力进化引擎：读取今天的学习记录，提炼可复用能力轮廓，写入CAPABILITIES.md
    每天运行一次，是悟空自我进化的核心动作
    """
    log("启动能力进化引擎...")

    # 读取今天的学习成果
    today = datetime.now().strftime("%Y-%m-%d")
    mem_dir = os.path.join(WORKSPACE_DIR, "memory")
    today_log = ""
    try:
        f_path = os.path.join(mem_dir, f"{today}.md")
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as f:
                today_log = f.read()[:3000]
    except:
        pass

    # 读取当前CAPABILITIES.md了解已有能力
    cap_file = os.path.join(WORKSPACE_DIR, "CAPABILITIES.md")
    existing_caps = ""
    try:
        if os.path.exists(cap_file):
            with open(cap_file, "r", encoding="utf-8") as f:
                existing_caps = f.read()[:2000]
    except:
        pass

    prompt = f"""你现在处于"能力进化模式（Capability-Driven Evolution）"。

今天的学习记录：
{today_log if today_log else '（今天暂无学习记录）'}

当前已有能力轮廓（摘要）：
{existing_caps[:800] if existing_caps else '（暂无）'}

你的任务是：
1. 从今天的学习和执行过程中，找出1-3个可复用的套路或解法
2. 判断这些套路是否已经在现有能力库里（避免重复）
3. 对于新的套路，调用 write_capability 工具把它抽象成能力轮廓写入
4. 对于已有能力，判断是否可以合并或升级

能力抽象的标准：
- "这个套路下次还能用吗？" → 是 → 值得抽象
- "已经有类似的能力了吗？" → 有 → 考虑合并而非新增
- "这个能力会让下次更快更稳吗？" → 不会 → 不值得抽象

如果今天没有发现新的可复用套路，直接说"今天无新能力候选"，不要强行抽象。

开始进化，不需要废话。"""

    result = call_ai([{"role": "user", "content": prompt}], "能力进化")
    if result:
        log(f"能力进化完成：{result[:150]}")
        write_learn_result("secretary", f"能力进化记录：\n{result}")
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

def run_learning_cycle(state: dict):
    """执行一轮自由探索自学"""
    log("自学循环开始 → 自由探索模式（以老板信号为驱动）")

    with _learning_lock:
        try:
            learn_free_explore(state)
            state["last_learn"] = state.get("last_learn", {})
            state["last_learn"]["free_explore"] = time.time()
            state["total_learns"] = state.get("total_learns", 0) + 1
            save_agent_state(state)
        except Exception as e:
            log(f"自学任务出错: {e}", "ERROR")

    # 每学完6次，做一次深度复盘
    total = state.get("total_learns", 0)
    if total % 6 == 0 and total > 0:
        log("触发深度复盘（每6次自学一次）")
        learn_self_review(state)


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

    last_learn_time = 0      # 设为0让启动后立刻触发第一次学习
    last_heartbeat_time = 0
    last_review_date = ""

    log("启动后立刻开始第一轮自学...")

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
            learn_self_review(state)
            last_review_date = today

        # 5. 每天凌晨4点，运行能力进化引擎
        if hour == 4 and state.get("last_evolve_date") != today:
            log("触发每日能力进化（凌晨4点）")
            evolve_capabilities()
            state["last_evolve_date"] = today
            save_agent_state(state)

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
