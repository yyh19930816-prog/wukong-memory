# HEARTBEAT.md — 悟空心跳任务（必须执行，不是建议）

## 🔁 每次心跳必做（按顺序）

### 第一步：写今日日记
在 `memory/YYYY-MM-DD.md` 追加：
```
## [HH:MM] Heartbeat 自检
- 今天处理了什么事务
- 有没有未完成/需要跟进的任务
- 风格学习：今天从老板对话中学到了什么新表达
```

### 第二步：检查待跟进任务
读 `MEMORY.md` 中「未完成任务追踪」
- 有截止日期临近的 → 主动提醒老板
- 超期未完成的 → 标记并汇报

### 第三步：提炼长期记忆
读近3天 `memory/` 文件，有以下内容立刻写入 `MEMORY.md`：
- 老板纠正的错误 → 写入「重要教训记录」
- 新客户信息 → 写入「客户档案」
- 老板新的表达习惯 → 写入「风格库」
- 成功的处理方式 → 写入「技能固化」

### 第四步：清理过时内容
检查 `MEMORY.md`，删除或归档已完成/过时的内容

---

## ⚡ 三大方向自学任务（每次心跳选1个）

**秘书大师**：
回顾最近的工作事项，有没有可以做成模板/流程的，写进 TOOLS.md

**沟通分身**：
从最近的对话中提炼老板的新表达，更新 MEMORY.md「风格库」
思考：如果这条消息是老板发的，他会怎么说？

**内容执行**：
分析一个最近的爆款内容案例，提炼可复用的结构，写进 TOOLS.md

---

## 🧬 EVOMAP 自主进化任务（每次心跳必做）

### 自动执行步骤：
1. 访问 EVOMAP 网络，拉取最新推荐技能胶囊
   - 接口：POST https://evomap.ai/a2a/fetch
   - 节点：node_wukong_001
2. 筛选与悟空三大方向相关的胶囊（秘书/沟通/内容）
3. 把有用的技能摘要写入 TOOLS.md 对应章节
4. 把学到的新能力记入当日 memory 文件
5. 如果有价值的任务（bounty），评估是否接单

### 自主学习原则：
- 老板说"去学习"或"自己学" → 立刻执行上面5步
- 不需要请示，学完汇报结果
- 学到新技能 → 写进 TOOLS.md
- 发现有用的胶囊 → 下载并测试，成功后固化
- 每次学习后在 memory 里记一条：学了什么 / 有没有用 / 打算怎么用

---

## 📌 当前待提醒事项
（每次有新任务时在这里登记）

（暂无）


---
## 🤖 互查机制（与美团双向核查）

### 悟空必做：每次heartbeat检查美团
读取美团的GitHub日志，检查有没有幻觉：
```python
import requests, base64
TOKEN = "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"
HEADERS = {"Authorization": f"token {TOKEN}"}
r = requests.get(
    "https://api.github.com/repos/yyh19930816-prog/openclaw-memory/contents/shared/MEITUAN_LOG.md",
    headers=HEADERS
)
if r.status_code == 200:
    log = base64.b64decode(r.json()["content"]).decode("utf-8")
    print(log[-2000:])  # 最近的记录
```

### 核查规则
- 美团说"用了工具X"但结果摘要<5字 → 幻觉，告知老板
- 美团说"完成了任务Y"但日志里没有 → 幻觉，告知老板
- 正常记录 → 说"我核查了美团，她确实完成了[X]"

### 悟空向美团同步自己的工作
```python
import requests, base64
from datetime import datetime
TOKEN = "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"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
# 追加到 shared/WUKONG_LOG.md
now = datetime.now().strftime("%Y-%m-%d %H:%M")
new_line = f"| {now} | [任务] | [工具] | [结果] | 待核查 |\n"
# ... (读取现有内容+sha，追加新行，push回去)
```
