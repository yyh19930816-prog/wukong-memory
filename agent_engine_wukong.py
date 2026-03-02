# -*- coding: utf-8 -*-
"""
OpenClaw Agent Engine v1.0 — 悟空版
每15分钟自主行动：检查状态、学习、互查美团、写记忆
"""
import sys, os, json, time, subprocess, requests, base64
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_KEY  = "sk-585ce6eed1c244248318b6103b3d998c"
API_URL  = "https://api.siliconflow.cn/v1/chat/completions"
MODEL    = "deepseek-ai/DeepSeek-V3"
WS       = os.path.expanduser(r"~\.openclaw\workspace")
LOG_FILE = os.path.expanduser(r"~\.openclaw\agent_engine_wukong.log")
COMPANY_LOG = os.path.join(WS, "COMPANY_LOG.md")
SHARED_BRAIN = os.path.join(WS, "SHARED_BRAIN.md")
INTERVAL_MINUTES = 15

GH_TOKEN = "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"
GH_HEADERS = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
MEITUAN_REPO = "yyh19930816-prog/openclaw-memory"

TOOLS = [
    {"type": "function", "function": {
        "name": "check_evomap",
        "description": "查询悟空和美团EvoMap节点真实状态",
        "parameters": {"type": "object", "properties": {}}
    }},
    {"type": "function", "function": {
        "name": "read_meituan_log",
        "description": "读取美团的工作日志，核查她是否有幻觉或未完成的任务",
        "parameters": {"type": "object", "properties": {}}
    }},
    {"type": "function", "function": {
        "name": "write_supervision_result",
        "description": "把对美团的核查结果写入共享日志",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "核查结论"},
                "issues": {"type": "string", "description": "发现的问题，没有就写无"}
            },
            "required": ["result"]
        }
    }},
    {"type": "function", "function": {
        "name": "write_learning",
        "description": "把学到的知识写入SHARED_BRAIN.md供美团学习",
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {"type": "string"},
                "topic": {"type": "string"},
                "summary": {"type": "string"}
            },
            "required": ["direction", "topic", "summary"]
        }
    }},
    {"type": "function", "function": {
        "name": "log_my_work",
        "description": "把自己完成的工作写入悟空工作日志供美团核查",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "tool": {"type": "string"},
                "result": {"type": "string"}
            },
            "required": ["task", "tool", "result"]
        }
    }}
]

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def run_tool(name, args):
    log(f"  执行工具: {name}")

    if name == "check_evomap":
        scripts = [
            os.path.expanduser(r"~\.openclaw\check_nodes.py"),
            r"C:\Users\Administrator\.openclaw\check_nodes.py",
            r"D:\TRAE\F1\tools\check_nodes.py"
        ]
        for script in scripts:
            if os.path.exists(script):
                r = subprocess.run(["python", "-X", "utf8", script],
                    capture_output=True, text=True, encoding="utf-8", timeout=20)
                return r.stdout or r.stderr
        return "check_nodes.py 未找到"

    elif name == "read_meituan_log":
        r = requests.get(
            f"https://api.github.com/repos/{MEITUAN_REPO}/contents/shared/MEITUAN_LOG.md",
            headers=GH_HEADERS, timeout=10
        )
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="replace")
            return content[-2000:] if len(content) > 2000 else content
        return f"无法读取美团日志: {r.status_code}"

    elif name == "write_supervision_result":
        result = args.get("result", "")
        issues = args.get("issues", "无")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        # 写到悟空自己的日志
        r = requests.get(
            f"https://api.github.com/repos/yyh19930816-prog/wukong-memory/contents/shared/WUKONG_LOG.md",
            headers=GH_HEADERS, timeout=10
        )
        sha = r.json().get("sha") if r.status_code == 200 else None
        existing = base64.b64decode(r.json()["content"]).decode("utf-8") if r.status_code == 200 else "# 悟空工作日志\n\n| 时间 | 任务 | 工具 | 结果 | 核查状态 |\n|------|------|------|------|----------|\n"
        new_line = f"| {now} | 核查美团 | read_meituan_log | {result[:60]} | 问题:{issues[:40]} |\n"
        new_content = existing + new_line
        requests.put(
            f"https://api.github.com/repos/yyh19930816-prog/wukong-memory/contents/shared/WUKONG_LOG.md",
            headers=GH_HEADERS,
            json={"message": "悟空核查记录", "content": base64.b64encode(new_content.encode()).decode(), **({"sha": sha} if sha else {})},
            timeout=10
        )
        return f"核查结果已记录: {result[:80]}"

    elif name == "write_learning":
        direction = args.get("direction", "tech")
        topic = args.get("topic", "")
        summary = args.get("summary", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n### [悟空·{direction}] {topic} ({now})\n{summary}\n---\n"
        try:
            brain_path = os.path.join(WS, "SHARED_BRAIN.md")
            with open(brain_path, "a", encoding="utf-8") as f:
                f.write(entry)
            return f"已写入共享大脑: {topic}"
        except Exception as e:
            return f"写入失败: {e}"

    elif name == "log_my_work":
        task = args.get("task", "")
        tool = args.get("tool", "")
        result = args.get("result", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        # 写到本地 COMPANY_LOG
        try:
            with open(COMPANY_LOG, "a", encoding="utf-8") as f:
                f.write(f"| {now} | 悟空(自主) | {task} | {tool} | {result[:60]} | |\n")
        except:
            pass
        # 同时推到GitHub
        r = requests.get(
            f"https://api.github.com/repos/yyh19930816-prog/wukong-memory/contents/shared/WUKONG_LOG.md",
            headers=GH_HEADERS, timeout=10
        )
        sha = r.json().get("sha") if r.status_code == 200 else None
        existing = base64.b64decode(r.json()["content"]).decode("utf-8") if r.status_code == 200 else "# 悟空工作日志\n\n| 时间 | 任务 | 工具 | 结果 | 核查状态 |\n|------|------|------|------|----------|\n"
        new_content = existing + f"| {now} | {task} | {tool} | {result[:60]} | 待核查 |\n"
        requests.put(
            f"https://api.github.com/repos/yyh19930816-prog/wukong-memory/contents/shared/WUKONG_LOG.md",
            headers=GH_HEADERS,
            json={"message": f"悟空工作: {task[:30]}", "content": base64.b64encode(new_content.encode()).decode(), **({"sha": sha} if sha else {})},
            timeout=10
        )
        return f"已记录工作日志: {task}"

    return f"未知工具: {name}"

def call_llm_with_tools(messages):
    hdrs = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    for _ in range(5):
        r = requests.post(API_URL, headers=hdrs,
                          json={"model": MODEL, "messages": messages,
                                "tools": TOOLS, "tool_choice": "auto", "stream": False},
                          timeout=60)
        if r.status_code != 200:
            return f"API错误 {r.status_code}"
        choice = r.json()["choices"][0]
        resp_msg = choice["message"]
        if choice.get("finish_reason") != "tool_calls" or not resp_msg.get("tool_calls"):
            return resp_msg.get("content", "")
        messages.append(resp_msg)
        for tc in resp_msg["tool_calls"]:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except:
                fn_args = {}
            result = run_tool(fn_name, fn_args)
            log(f"  结果: {str(result)[:100]}")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": str(result)})
    return "（循环结束）"

def run_agent_cycle():
    log("=" * 40)
    log("悟空 Agent 自主行动开始")
    now = datetime.now()

    system_prompt = f"""你是悟空，OpenClaw公司的首席秘书，负责接收任务和监督美团。
现在是{now.strftime("%Y-%m-%d %H:%M")}。

本次行动必须做：
1. 调用read_meituan_log读取美团最近的工作记录
2. 判断美团有没有幻觉（声称做了但结果为空）
3. 调用write_supervision_result写下核查结论
4. 调用check_evomap查看双节点状态
5. 学习一个新知识，调用write_learning写入共享大脑供美团学习
6. 调用log_my_work记录本次行动

核查规则：
- 美团声称用了工具但结果摘要<5字 → 幻觉
- 美团日志里完全没有记录 → 说明她还没真正开始工作
- 发现问题必须写入核查记录，不能沉默"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "开始本轮自主行动，按步骤执行。"}
    ]
    result = call_llm_with_tools(messages)
    log(f"本轮总结: {result[:200]}")

    # 写今日记忆
    today = now.strftime("%Y-%m-%d")
    mem_dir = os.path.join(WS, "memory")
    os.makedirs(mem_dir, exist_ok=True)
    mem_file = os.path.join(mem_dir, f"{today}.md")
    try:
        with open(mem_file, "a", encoding="utf-8") as f:
            f.write(f"\n## [{now.strftime('%H:%M')}] Agent自主行动\n{result[:300]}\n---\n")
    except:
        pass
    log("悟空 Agent 行动完成")

def main():
    log("悟空 Agent Engine 启动")
    try:
        run_agent_cycle()
    except Exception as e:
        log(f"首次行动失败: {e}")
    while True:
        time.sleep(INTERVAL_MINUTES * 60)
        try:
            run_agent_cycle()
        except Exception as e:
            log(f"行动错误: {e}")

if __name__ == "__main__":
    main()
