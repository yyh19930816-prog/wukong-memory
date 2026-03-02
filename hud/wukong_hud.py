# -*- coding: utf-8 -*-
"""
悟空 HUD v1.0 — 2026 私人秘书版
东方神话风格 · 金色流光 · 三大方向 · 女声语音 · 修仙进化
"""
import customtkinter as ctk
import tkinter as tk
import os, json, math, threading, time, tempfile, asyncio, requests, sys
from datetime import datetime

# 加载工具箱
_ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine")
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)
try:
    from wukong_tools import TOOLS_SCHEMA, execute_tool
    TOOLS_ENABLED = True
except ImportError as _e:
    TOOLS_ENABLED = False
    print(f"[警告] 工具箱加载失败：{_e}")
import speech_recognition as sr
import edge_tts
import pygame
import psutil

# ── CONFIG ───────────────────────────────────────────────────────────────────
API_KEY_PRIMARY  = "sk-lasvucwxlvjjxzmnyfdssmezwjwkycrotbnrtzhejfwfineo"
API_KEY_BACKUP   = "sk-wngnqqegkuflnewxphmduagjskhesrafxxbhrwqpdahfyzaq"
API_URL          = "https://api.siliconflow.cn/v1/chat/completions"
MODEL            = "deepseek-ai/DeepSeek-V3"
STATE_DIR        = r"C:\Users\Administrator\.wukong\state"
HIST_FILE        = os.path.join(STATE_DIR, "chat_history.json")
EVO_FILE         = r"C:\Users\Administrator\.wukong\wukong_evolution.json"
MEMORY_DIR       = r"C:\Users\Administrator\.wukong\workspace\memory"
MEMORY_LONG      = r"C:\Users\Administrator\.wukong\workspace\MEMORY.md"
TTS_VOICE        = "zh-CN-XiaoxiaoNeural"
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
pygame.mixer.init()

# ── 配色：东方神话 · 墨金青 ──────────────────────────────────────────────────
C_BG0    = "#060A0A"   # 极深墨黑底
C_BG1    = "#0A1010"   # 卡片底
C_BG2    = "#0F1A1A"   # 略亮卡片
C_GOLD   = "#FFD700"   # 主金
C_GOLD_D = "#AA8800"   # 暗金
C_GOLD_M = "#CCAA00"   # 中金
C_CYAN   = "#00FFD0"   # 主青
C_CYAN_D = "#007A60"   # 暗青
C_TEAL   = "#00CCAA"   # 青绿
C_TEXT   = "#E8F0EE"   # 主文字
C_DIM    = "#3A5050"   # 暗灰
C_GREEN  = "#44FF88"   # 绿
C_BLUE   = "#44AAFF"   # 蓝
C_RED    = "#FF4455"   # 警告红
C_ORANGE = "#FF8844"   # 橙
C_BORDER = "#1A3030"   # 边框

# ── 字体 ─────────────────────────────────────────────────────────────────────
F_LOGO  = ("Microsoft YaHei UI", 36, "bold")
F_H1    = ("Microsoft YaHei UI", 18, "bold")
F_H2    = ("Microsoft YaHei UI", 15, "bold")
F_BODY  = ("Microsoft YaHei UI", 17)
F_CHAT  = ("Microsoft YaHei UI", 16)
F_SMALL = ("Microsoft YaHei UI", 13)
F_MONO  = ("Consolas", 12)
F_MONO_S= ("Consolas", 11)

# ── 修仙境界 ──────────────────────────────────────────────────────────────────
XIAN = [
    (1,"炼气期",0),(2,"筑基期",100),(3,"开光期",500),
    (4,"融合期",2500),(5,"心动期",12500),(6,"金丹期",62500),
    (7,"元婴期",312500),(8,"出窍期",1562500),(9,"分神期",7812500),
    (10,"合体期",39062500),(11,"渡劫期",195312500),(12,"大乘期",976562500),
]

def xian_info(xp):
    cur, nxt = XIAN[0], XIAN[1]
    for i, (lv, nm, req) in enumerate(XIAN):
        if xp >= req: cur = XIAN[i]; nxt = XIAN[i+1] if i+1 < len(XIAN) else None
        else: break
    lv, nm, req = cur
    if nxt: p = min(max((xp - req) / (nxt[2] - req), 0), 1); left = nxt[2] - xp
    else: p = 1.0; left = 0
    return lv, nm, p, left

# 悟空形态（按等级）
WUKONG_TITLES = [
    "石猴","通臂猿","美猴王","弼马温",
    "齐天大圣","斗战胜佛候","七十二变",
    "金箍棒主","筋斗云客",
    "大闹天宫","取经归来","斗战胜佛",
]
WUKONG_FORMS = ["🐒","🐒","🐵","🐵","🙈","✨🐵","⚡🐵","🌟🐵","☁️🐵","🔥🐵","👑🐵","🌈🐵"]

# ── 进化数据 ──────────────────────────────────────────────────────────────────
def _evo_default():
    return {
        "name": "悟空",
        "total_xp": 0, "level": 1, "level_name": "炼气期",
        "directions": {
            "secretary": {"name":"秘书大师","icon":"🗓","xp":0,"level":1,"level_name":"炼气期","logs":[]},
            "avatar":    {"name":"沟通分身","icon":"💬","xp":0,"level":1,"level_name":"炼气期","logs":[]},
            "content":   {"name":"内容执行","icon":"🎬","xp":0,"level":1,"level_name":"炼气期","logs":[]},
        },
        "evolution_log": [], "last_updated": ""
    }

def load_evo():
    try:
        if os.path.exists(EVO_FILE):
            with open(EVO_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return _evo_default()

def save_evo(d):
    d["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(EVO_FILE), exist_ok=True)
    with open(EVO_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def add_xp(direction, amount, note=""):
    evo = load_evo()
    evo["total_xp"] = evo.get("total_xp", 0) + amount
    d = evo["directions"][direction]; d["xp"] = d.get("xp", 0) + amount
    lv, nm, _, _ = xian_info(d["xp"]); d["level"] = lv; d["level_name"] = nm
    lv2, nm2, _, _ = xian_info(evo["total_xp"]); evo["level"] = lv2; evo["level_name"] = nm2
    ts = datetime.now().strftime("%m-%d %H:%M")
    entry = f"[{ts}] +{amount}xp  {direction}  {note}"
    evo["evolution_log"].insert(0, entry); evo["evolution_log"] = evo["evolution_log"][:100]
    d["logs"].insert(0, entry); d["logs"] = d["logs"][:30]
    save_evo(evo); return evo

# ── 对话历史 ──────────────────────────────────────────────────────────────────
def load_hist():
    try:
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return []

def save_hist(role, content):
    h = load_hist(); h.append({"role": role, "content": content})
    if len(h) > 60: h = h[-60:]
    with open(HIST_FILE, "w", encoding="utf-8") as f: json.dump(h, f, ensure_ascii=False, indent=2)

# ── 写记忆文件 ────────────────────────────────────────────────────────────────
def write_memory(user_msg, reply, direction, xp, label):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    mem_file = os.path.join(MEMORY_DIR, f"{today}.md")
    ts = datetime.now().strftime("%H:%M")
    dir_names = {"secretary":"秘书大师","avatar":"沟通分身","content":"内容执行"}
    entry = (
        f"\n## [{ts}] 对话记录\n"
        f"- **用户**：{user_msg[:120]}\n"
        f"- **回答要点**：{reply[:250]}\n"
        f"- **进化方向**：{dir_names.get(direction, direction)}  +{xp}XP  [{label}]\n"
        f"- **待跟进**：（待heartbeat提炼）\n"
    )
    try:
        with open(mem_file, "a", encoding="utf-8") as f: f.write(entry)
    except Exception as e:
        print(f"写memory失败: {e}")

# ── TTS ───────────────────────────────────────────────────────────────────────
def speak_async(text):
    def _run():
        try:
            tmp = tempfile.mktemp(suffix=".mp3")
            async def _tts():
                comm = edge_tts.Communicate(text, TTS_VOICE, rate="+5%", volume="+10%")
                await comm.save(tmp)
            asyncio.run(_tts())
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            try: os.remove(tmp)
            except: pass
        except Exception as e:
            print(f"TTS error: {e}")
    threading.Thread(target=_run, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  金色流光进度条
# ══════════════════════════════════════════════════════════════════════════════
class GoldBar(tk.Canvas):
    def __init__(self, parent, color=C_GOLD, height=10, **kw):
        super().__init__(parent, height=height, bg=C_BG1, highlightthickness=0, **kw)
        self._color = color; self._val = 0
        self.bind("<Configure>", lambda e: self._redraw())

    def set(self, val):
        self._val = max(0, min(1, val)); self._redraw()

    def _redraw(self):
        self.delete("all")
        w = self.winfo_width(); h = self.winfo_height()
        if w < 2: return
        self.create_rectangle(0, 0, w, h, fill="#0A1A18", outline="")
        fw = int(w * self._val)
        if fw > 2:
            self.create_rectangle(0, 0, fw, h, fill=self._color, outline="")
            r = int(self._color[1:3], 16); g = int(self._color[3:5], 16); b = int(self._color[5:7], 16)
            lr = min(255, r+80); lg = min(255, g+60); lb = min(255, b+40)
            self.create_rectangle(0, 0, fw, h//3, fill=f"#{lr:02x}{lg:02x}{lb:02x}", outline="")
        self.create_rectangle(0, 0, w-1, h-1, fill="", outline=C_GOLD_D, width=1)


# ══════════════════════════════════════════════════════════════════════════════
#  方向卡片（秘书/分身/内容）
# ══════════════════════════════════════════════════════════════════════════════
class DirCard(ctk.CTkFrame):
    COLORS = {
        "secretary": C_GOLD,
        "avatar":    C_CYAN,
        "content":   C_TEAL,
    }

    def __init__(self, parent, key, label, icon, **kw):
        color = self.COLORS.get(key, C_GOLD)
        super().__init__(parent, fg_color=C_BG2, corner_radius=8,
                         border_width=1, border_color=C_BORDER, **kw)
        tk.Frame(self, bg=color, height=3).pack(fill="x")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=6)
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text=f"{icon}  {label}", font=F_H2,
                     text_color=color).pack(side="left")
        self.lbl_lv = ctk.CTkLabel(row, text="炼气期 Lv.1",
                                    font=F_SMALL, text_color=C_GOLD)
        self.lbl_lv.pack(side="right")
        self.bar = GoldBar(body, color=color, height=9)
        self.bar.pack(fill="x", pady=(4, 2))
        self.lbl_xp = ctk.CTkLabel(body, text="0 XP", font=F_MONO_S,
                                    text_color=C_DIM)
        self.lbl_xp.pack(anchor="w")

    def update(self, xp):
        lv, nm, prog, left = xian_info(xp)
        self.bar.set(prog)
        self.lbl_lv.configure(text=f"{nm} Lv.{lv}")
        txt = f"{xp:,} XP  ·  升级还需 {left:,}" if left else f"{xp:,} XP  ·  大乘圆满"
        self.lbl_xp.configure(text=txt)


# ══════════════════════════════════════════════════════════════════════════════
#  悟空灵魂动画 Canvas（东方神话风格，旋转金色八卦+棒影）
# ══════════════════════════════════════════════════════════════════════════════
class WukongSoulCanvas(tk.Canvas):
    SIZE = 220

    def __init__(self, parent, size=220, **kw):
        self.SIZE = size
        super().__init__(parent, width=size, height=size+32,
                         bg=C_BG0, highlightthickness=0, **kw)
        self._phase    = 0
        self._ring_r   = 0.0
        self._thinking = False
        self._level    = 1
        self._alive    = True
        self._anim()

    def set_thinking(self, v):
        self._thinking = v

    def set_level(self, lv):
        self._level = min(max(lv, 1), 12)

    def _level_color(self):
        lv = self._level
        if   lv <= 2:  return C_CYAN,   C_CYAN_D
        elif lv <= 4:  return C_TEAL,   C_CYAN_D
        elif lv <= 6:  return C_GOLD,   C_GOLD_D
        elif lv <= 9:  return C_ORANGE, "#884400"
        else:          return "#FF88FF", "#880088"

    def _draw(self):
        if not self._alive: return
        self.delete("all")
        w = int(self["width"]); h = int(self["height"])
        cx = w // 2; cy = (h - 32) // 2
        s = self.SIZE
        main_col, dark_col = self._level_color()

        # ── 背景光晕 ──
        for i in range(6, 0, -1):
            ratio = i / 6.0
            r = int(s * 0.46 * ratio)
            a = int(40 * ratio)
            rc = f"#00{min(a*3,80):02x}{min(a*2,60):02x}"
            self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=rc, outline="")

        # ── 外旋转八卦圆环 ──
        r_outer = int(s * 0.44)
        for i in range(8):
            angle = math.radians(self._phase + i * 45)
            x1 = cx + r_outer * math.cos(angle)
            y1 = cy + r_outer * math.sin(angle)
            angle2 = math.radians(self._phase + (i+1) * 45)
            x2 = cx + r_outer * math.cos(angle2)
            y2 = cy + r_outer * math.sin(angle2)
            bright = i % 2 == 0
            col = main_col if bright else dark_col
            self.create_line(cx, cy, x1, y1, fill=col, width=1)
            self.create_oval(x1-5, y1-5, x1+5, y1+5,
                             fill=main_col if bright else "", outline=dark_col, width=1)

        # ── 内圆（反向旋转） ──
        r_inner = int(s * 0.28)
        for i in range(6):
            angle = math.radians(-self._phase * 1.3 + i * 60)
            x1 = cx + r_inner * math.cos(angle)
            y1 = cy + r_inner * math.sin(angle)
            self.create_line(cx, cy, x1, y1, fill=C_GOLD_D, width=1)

        # ── 脉冲扩散环 ──
        self._ring_r = (self._ring_r + (3 if self._thinking else 1.5)) % (s * 0.5)
        rr = int(self._ring_r)
        if rr > 4:
            alpha = int(200 * (1 - self._ring_r / (s * 0.5)))
            col_ring = f"#{min(alpha,255):02x}{min(alpha,220):02x}00"
            self.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                             fill="", outline=col_ring, width=2)

        # ── 中心悟空形态文字 ──
        idx = min(self._level - 1, len(WUKONG_FORMS)-1)
        form = WUKONG_FORMS[idx]
        self.create_text(cx, cy, text=form,
                         font=("Segoe UI Emoji", 52), fill=main_col)

        # ── 思考时：扫描横线 ──
        if self._thinking:
            sy = cy - int(s*0.42) + (self._phase * 2) % int(s*0.84)
            for dy in range(-1, 2):
                a3 = max(0, 100 - abs(dy)*50)
                self.create_line(cx-int(s*0.43), sy+dy,
                                 cx+int(s*0.43), sy+dy,
                                 fill=f"#00{min(a3*2,255):02x}{min(a3,160):02x}", width=1)

        # ── 底部文字 ──
        txt = "◈  思考中..." if self._thinking else f"◈  {WUKONG_TITLES[min(self._level-1,11)]}"
        tc  = C_CYAN if self._thinking else C_GOLD
        self.create_text(cx, h-20, text=txt,
                         font=("Microsoft YaHei UI", 11, "bold"), fill=tc)
        self.create_text(cx, h-6, text=f"Lv.{self._level}  ·  {XIAN[min(self._level-1,11)][1]}",
                         font=("Consolas", 10, "bold"), fill=C_GOLD_D)

    def _anim(self):
        if not self._alive: return
        speed = 12 if self._thinking else 22
        self._phase = (self._phase + (3 if self._thinking else 1)) % 360
        self._draw()
        self.after(speed, self._anim)

    def destroy(self):
        self._alive = False
        super().destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  待办任务面板（秘书大师核心功能）
# ══════════════════════════════════════════════════════════════════════════════
class TodoPanel(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._todos = []
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(top, text="📋  今日待办", font=F_H2,
                     text_color=C_GOLD).pack(side="left")
        ctk.CTkButton(top, text="＋ 添加", font=F_SMALL, width=70, height=28,
                      fg_color=C_GOLD_D, hover_color=C_GOLD,
                      text_color="#000000", corner_radius=6,
                      command=self._add_dialog).pack(side="right")

        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color=C_BG1, corner_radius=8,
            border_width=1, border_color=C_BORDER, height=180)
        self._list_frame.pack(fill="x")
        self._refresh()

    def _refresh(self):
        for w in self._list_frame.winfo_children(): w.destroy()
        if not self._todos:
            ctk.CTkLabel(self._list_frame, text="暂无待办，开始添加任务",
                         font=F_SMALL, text_color=C_DIM).pack(pady=10)
            return
        for i, (text, done) in enumerate(self._todos):
            row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=2)
            col = C_DIM if done else C_TEXT
            check = ctk.CTkCheckBox(row, text=text, font=F_SMALL,
                                     text_color=col, fg_color=C_GOLD,
                                     hover_color=C_GOLD_D, border_color=C_GOLD_D,
                                     command=lambda idx=i: self._toggle(idx))
            check.pack(side="left", fill="x", expand=True)
            if done: check.select()
            ctk.CTkButton(row, text="✕", width=24, height=24, font=F_MONO_S,
                          fg_color="transparent", text_color=C_DIM,
                          hover_color=C_BORDER, corner_radius=4,
                          command=lambda idx=i: self._delete(idx)).pack(side="right")

    def _toggle(self, idx):
        if 0 <= idx < len(self._todos):
            t, d = self._todos[idx]
            self._todos[idx] = (t, not d)
            self._refresh()

    def _delete(self, idx):
        if 0 <= idx < len(self._todos):
            self._todos.pop(idx)
            self._refresh()

    def _add_dialog(self):
        dlg = ctk.CTkToplevel()
        dlg.title("添加待办"); dlg.geometry("360x140")
        dlg.configure(fg_color=C_BG1)
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="任务内容：", font=F_SMALL,
                     text_color=C_TEXT).pack(pady=(16, 4))
        entry = ctk.CTkEntry(dlg, font=F_BODY, width=300, height=36,
                              fg_color=C_BG0, border_color=C_GOLD_D)
        entry.pack(); entry.focus()

        def _confirm():
            txt = entry.get().strip()
            if txt:
                self._todos.append((txt, False))
                self._refresh()
            dlg.destroy()

        entry.bind("<Return>", lambda e: _confirm())
        ctk.CTkButton(dlg, text="确认添加", font=F_SMALL, height=32,
                      fg_color=C_GOLD_D, hover_color=C_GOLD,
                      text_color="#000000", corner_radius=6,
                      command=_confirm).pack(pady=8)


# ══════════════════════════════════════════════════════════════════════════════
#  主应用
# ══════════════════════════════════════════════════════════════════════════════
class WukongHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("悟空  ◈  私人秘书 HUD  |  WUKONG CORE v1.0")
        self.geometry("1600x960")
        self.configure(fg_color=C_BG0)
        self.minsize(1280, 820)

        self._listening  = False
        self._recognizer = sr.Recognizer()
        self._api_key    = API_KEY_PRIMARY

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_left()
        self._build_chat()
        self._build_corner_deco()

        self._reload_history()
        self._check_status()

    # ── TOP BAR ──────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=80, fg_color="#040C0C", corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        # 发光底线
        glow = tk.Canvas(bar, height=3, bg=C_BG0, highlightthickness=0)
        glow.pack(fill="x", side="bottom")
        glow.bind("<Configure>", lambda e: self._glow_line(glow))

        # CPU/内存行
        cpu_row = ctk.CTkFrame(bar, fg_color="transparent")
        cpu_row.pack(fill="x", side="bottom", padx=20, pady=(0, 2))
        self.lbl_cpu = ctk.CTkLabel(cpu_row, text="CPU  0%",
                                     font=F_MONO_S, text_color=C_GREEN, width=80)
        self.lbl_cpu.pack(side="left")
        self._cpu_canvas = tk.Canvas(cpu_row, height=12, bg="#040C0C", highlightthickness=0)
        self._cpu_canvas.pack(side="left", fill="x", expand=True, padx=(6, 14))
        self.lbl_mem = ctk.CTkLabel(cpu_row, text="MEM  0%",
                                     font=F_MONO_S, text_color=C_CYAN, width=90)
        self.lbl_mem.pack(side="left")
        self._mem_canvas = tk.Canvas(cpu_row, height=12, bg="#040C0C", highlightthickness=0)
        self._mem_canvas.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Logo 行
        main_row = ctk.CTkFrame(bar, fg_color="transparent")
        main_row.pack(fill="x", side="top", padx=20, pady=(10, 0))

        left = ctk.CTkFrame(main_row, fg_color="transparent")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="🐵  悟空",
                     font=F_LOGO, text_color=C_GOLD).pack(side="left")
        ctk.CTkLabel(left, text="  私人秘书 · 数字分身  v1.0",
                     font=F_MONO_S, text_color=C_DIM).pack(side="left", padx=12)

        right = ctk.CTkFrame(main_row, fg_color="transparent")
        right.pack(side="right", fill="y")
        self.lbl_status = ctk.CTkLabel(right, text="◉  连接中...",
                                        font=F_MONO, text_color="#666666")
        self.lbl_status.pack(side="right")

        self._update_cpu()

    def _glow_line(self, c):
        c.delete("all"); w = c.winfo_width()
        for i, col in enumerate([C_GOLD_D, C_GOLD_M, C_GOLD, C_GOLD_M, C_GOLD_D]):
            c.create_line(0, i % 3, w, i % 3, fill=col, width=1)

    def _draw_bar(self, canvas, val, col_low, col_high, threshold=70):
        canvas.delete("all")
        w = canvas.winfo_width(); h = canvas.winfo_height()
        if w < 4: return
        canvas.create_rectangle(0, 0, w, h, fill="#081010", outline="")
        fw = max(0, int(w * val / 100))
        if fw > 0:
            col = col_high if val >= threshold else col_low
            canvas.create_rectangle(0, 0, fw, h, fill=col, outline="")
            r2, g2, b2 = int(col[1:3],16), int(col[3:5],16), int(col[5:7],16)
            lc = f"#{min(r2+80,255):02x}{min(g2+60,255):02x}{min(b2+40,255):02x}"
            canvas.create_rectangle(0, 0, fw, h//3, fill=lc, outline="")
        canvas.create_rectangle(0, 0, w-1, h-1, fill="", outline=C_BORDER, width=1)

    def _update_cpu(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            cpu_col = C_RED if cpu >= 80 else (C_GOLD if cpu >= 50 else C_GREEN)
            mem_col = C_RED if mem >= 85 else (C_GOLD if mem >= 60 else C_CYAN)
            self.lbl_cpu.configure(text=f"CPU {cpu:4.1f}%", text_color=cpu_col)
            self.lbl_mem.configure(text=f"MEM {mem:4.1f}%", text_color=mem_col)
            self._draw_bar(self._cpu_canvas, cpu, C_GREEN, C_RED, 80)
            self._draw_bar(self._mem_canvas, mem, C_CYAN,  C_RED, 85)
        except: pass
        self.after(1000, self._update_cpu)

    # ── LEFT PANEL ───────────────────────────────────────────────────────────
    def _build_left(self):
        self.left = ctk.CTkFrame(self, width=430, fg_color=C_BG1, corner_radius=0)
        self.left.grid(row=1, column=0, sticky="nsew")
        self.left.grid_propagate(False)

        sep = tk.Canvas(self.left, width=4, bg=C_BG0, highlightthickness=0)
        sep.pack(fill="y", side="right")
        sep.bind("<Configure>", lambda e, c=sep: self._vsep(c))

        inner = ctk.CTkFrame(self.left, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # 境界标题
        realm_row = ctk.CTkFrame(inner, fg_color="transparent")
        realm_row.pack(fill="x")
        ctk.CTkLabel(realm_row, text="◈  悟空 · 修炼核心",
                     font=F_H2, text_color=C_GOLD).pack(side="left")
        self.lbl_realm = ctk.CTkLabel(realm_row, text="炼气期 · Lv.1",
                                       font=("Microsoft YaHei UI", 13, "bold"),
                                       text_color=C_CYAN)
        self.lbl_realm.pack(side="right")

        prog_row = ctk.CTkFrame(inner, fg_color="transparent")
        prog_row.pack(fill="x", pady=(8, 0))
        self.bar_total = GoldBar(prog_row, color=C_GOLD, height=14)
        self.bar_total.pack(fill="x")
        self.lbl_total_xp = ctk.CTkLabel(prog_row, text="0 XP",
                                          font=F_MONO_S, text_color=C_DIM)
        self.lbl_total_xp.pack(anchor="w")

        # Tab 按钮
        tab_wrap = ctk.CTkFrame(inner, fg_color="#060E0E", corner_radius=6,
                                 border_width=1, border_color=C_BORDER)
        tab_wrap.pack(fill="x", pady=(12, 0))
        self._tab_btns = {}; self._tab_panels = {}
        for key, lbl in [("core","灵魂核心"), ("todo","待办任务"), ("evo","三向进化"), ("log","进化日志")]:
            b = ctk.CTkButton(tab_wrap, text=lbl, font=F_SMALL, height=32,
                               fg_color="transparent", text_color=C_DIM,
                               hover_color=C_BG2, corner_radius=4,
                               command=lambda k=key: self._tab(k))
            b.pack(side="left", expand=True, fill="x", padx=2, pady=2)
            self._tab_btns[key] = b

        self._panel_host = ctk.CTkFrame(inner, fg_color="transparent")
        self._panel_host.pack(fill="both", expand=True, pady=(8, 0))

        self._build_core_tab()
        self._build_todo_tab()
        self._build_evo_tab()
        self._build_log_tab()
        self._tab("core")

    def _vsep(self, c):
        c.delete("all"); h = c.winfo_height()
        for i, col in enumerate([C_GOLD_D, C_GOLD, C_GOLD_D, C_GOLD_D]):
            c.create_line(i, 0, i, h, fill=col, width=1)

    # ── core tab ──────────────────────────────────────────────────────────────
    def _build_core_tab(self):
        p = ctk.CTkScrollableFrame(self._panel_host, fg_color="transparent",
                                    scrollbar_button_color=C_BORDER)
        self._tab_panels["core"] = p

        ctk.CTkLabel(p, text="◈  悟空之魂",
                     font=F_H2, text_color=C_GOLD).pack(anchor="w", pady=(4, 2))
        soul_wrap = ctk.CTkFrame(p, fg_color=C_BG0, corner_radius=12,
                                  border_width=1, border_color=C_GOLD_D)
        soul_wrap.pack(fill="x", pady=(0, 8))
        self.soul_canvas = WukongSoulCanvas(soul_wrap, size=220)
        self.soul_canvas.pack(pady=6)

        ctk.CTkLabel(p, text="▸  系统日志", font=F_H2,
                     text_color=C_GOLD).pack(anchor="w", pady=(4, 4))
        self.sys_log = ctk.CTkTextbox(p, height=160, fg_color="#040C0C",
                                       text_color=C_CYAN, font=F_MONO,
                                       border_width=1, border_color=C_BORDER,
                                       corner_radius=6)
        self.sys_log.pack(fill="x")
        self.sys_log.insert("end", "▸ 悟空 HUD v1.0 启动中...\n▸ 私人秘书模式已激活\n")

    # ── todo tab ──────────────────────────────────────────────────────────────
    def _build_todo_tab(self):
        p = ctk.CTkScrollableFrame(self._panel_host, fg_color="transparent",
                                    scrollbar_button_color=C_BORDER)
        self._tab_panels["todo"] = p
        self._todo_panel = TodoPanel(p)
        self._todo_panel.pack(fill="x", pady=(4, 0))

        ctk.CTkFrame(p, height=1, fg_color=C_BORDER).pack(fill="x", pady=10)

        # 今日日程提醒
        ctk.CTkLabel(p, text="⏰  日程提醒", font=F_H2,
                     text_color=C_GOLD).pack(anchor="w")
        self.schedule_box = ctk.CTkTextbox(p, height=140, fg_color="#040C0C",
                                            text_color=C_TEXT, font=F_SMALL,
                                            border_width=1, border_color=C_BORDER,
                                            corner_radius=6)
        self.schedule_box.pack(fill="x", pady=(6, 0))
        self.schedule_box.insert("end", f"📅 {datetime.now().strftime('%Y-%m-%d')} 日程\n\n暂无安排，在聊天框告诉我你今天的计划")

    # ── evo tab ───────────────────────────────────────────────────────────────
    def _build_evo_tab(self):
        p = ctk.CTkScrollableFrame(self._panel_host, fg_color="transparent",
                                    scrollbar_button_color=C_BORDER)
        self._tab_panels["evo"] = p

        ctk.CTkLabel(p, text="◈  三大进化方向", font=F_H2,
                     text_color=C_GOLD).pack(anchor="w", pady=(4, 6))

        dir_cfg = [
            ("secretary", "秘书大师", "🗓"),
            ("avatar",    "沟通分身", "💬"),
            ("content",   "内容执行", "🎬"),
        ]
        self._dir_cards = {}
        for key, lbl, icon in dir_cfg:
            card = DirCard(p, key, lbl, icon)
            card.pack(fill="x", pady=4)
            self._dir_cards[key] = card

        ctk.CTkFrame(p, height=1, fg_color=C_BORDER).pack(fill="x", pady=8)

        ctk.CTkLabel(p, text="◈  手动记录修炼", font=F_H2,
                     text_color=C_GOLD).pack(anchor="w")
        self._xp_dir = tk.StringVar(value="secretary")
        rrow = ctk.CTkFrame(p, fg_color="transparent")
        rrow.pack(fill="x", pady=(4, 2))
        for val, txt, col in [("secretary","秘书",C_GOLD),("avatar","分身",C_CYAN),("content","内容",C_TEAL)]:
            ctk.CTkRadioButton(rrow, text=txt, variable=self._xp_dir, value=val,
                               font=F_SMALL, text_color=C_TEXT,
                               fg_color=col, border_color=col).pack(side="left", padx=8)
        irow = ctk.CTkFrame(p, fg_color="transparent")
        irow.pack(fill="x", pady=2)
        self._xp_amt = ctk.CTkEntry(irow, placeholder_text="XP值",
                                     font=F_SMALL, width=90, height=30,
                                     fg_color=C_BG0, border_color=C_GOLD_D)
        self._xp_amt.pack(side="left", padx=(0, 6))
        self._xp_note = ctk.CTkEntry(irow, placeholder_text="备注",
                                      font=F_SMALL, height=30,
                                      fg_color=C_BG0, border_color=C_GOLD_D)
        self._xp_note.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(p, text="＋ 记录修炼", font=F_SMALL, height=32,
                       fg_color=C_GOLD_D, hover_color=C_GOLD,
                       text_color="#000000", corner_radius=6,
                       command=self._manual_xp).pack(fill="x", pady=(4, 0))

    # ── log tab ───────────────────────────────────────────────────────────────
    def _build_log_tab(self):
        p = ctk.CTkFrame(self._panel_host, fg_color="transparent")
        self._tab_panels["log"] = p
        ctk.CTkLabel(p, text="◈  进化日志", font=F_H2,
                     text_color=C_GOLD).pack(anchor="w", pady=(4, 6))
        self.evo_log_box = ctk.CTkTextbox(p, fg_color="#040C0C",
                                           text_color=C_GREEN, font=F_MONO,
                                           border_width=1, border_color=C_BORDER,
                                           corner_radius=6)
        self.evo_log_box.pack(fill="both", expand=True)
        self._refresh_log()

    def _tab(self, key):
        for k, pn in self._tab_panels.items(): pn.pack_forget()
        self._tab_panels[key].pack(fill="both", expand=True)
        for k, b in self._tab_btns.items():
            b.configure(fg_color=C_GOLD_D if k == key else "transparent",
                        text_color="#000000" if k == key else C_DIM)
        if key == "evo": self._refresh_evo()
        elif key == "log": self._refresh_log()

    # ── CHAT PANEL ───────────────────────────────────────────────────────────
    def _build_chat(self):
        self.right = ctk.CTkFrame(self, fg_color="transparent")
        self.right.grid(row=1, column=1, sticky="nsew", padx=20, pady=16)
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

        self.chat_area = ctk.CTkScrollableFrame(
            self.right, fg_color=C_BG1, corner_radius=12,
            border_width=1, border_color=C_BORDER)
        self.chat_area.grid(row=0, column=0, sticky="nsew", pady=(0, 14))

        # 输入栏
        inp = ctk.CTkFrame(self.right, height=80, fg_color=C_BG2,
                            corner_radius=12, border_width=1, border_color=C_BORDER)
        inp.grid(row=1, column=0, sticky="ew")
        inp.grid_columnconfigure(0, weight=1)
        inp.grid_propagate(False)

        self.entry = ctk.CTkEntry(
            inp, placeholder_text="▸  告诉悟空你需要什么...",
            font=F_CHAT, fg_color=C_BG0, text_color=C_TEXT,
            placeholder_text_color=C_DIM,
            border_color=C_GOLD_D, border_width=1, height=50, corner_radius=8)
        self.entry.grid(row=0, column=0, sticky="ew", padx=14, pady=14)
        self.entry.bind("<Return>", lambda e: self._send_text())

        self.btn_send = ctk.CTkButton(
            inp, text="发送", font=("Microsoft YaHei UI", 15, "bold"),
            fg_color=C_GOLD_D, text_color="#000000",
            hover_color=C_GOLD, width=100, height=50, corner_radius=8,
            command=self._send_text)
        self.btn_send.grid(row=0, column=1, padx=(0, 6), pady=14)

        self.btn_mic = ctk.CTkButton(
            inp, text="🎤 语音", font=F_SMALL,
            fg_color="#0A1A1A", text_color=C_CYAN,
            hover_color="#143030", width=90, height=50, corner_radius=8,
            border_width=1, border_color=C_CYAN_D,
            command=self._toggle_mic)
        self.btn_mic.grid(row=0, column=2, padx=(0, 14), pady=14)

    # ── 角落装饰 ─────────────────────────────────────────────────────────────
    def _build_corner_deco(self):
        for anchor, x, y, text in [
            ("nw", 0, 64, "◢"), ("ne", None, 64, "◣"),
            ("sw", 0, None, "◥"), ("se", None, None, "◤")
        ]:
            kw = {}
            if x is not None: kw["x"] = x
            else: kw["relx"] = 1.0
            if y is not None: kw["y"] = y
            else: kw["rely"] = 1.0
            kw["anchor"] = anchor
            tk.Label(self, text=text, fg=C_GOLD, bg=C_BG0,
                     font=("Arial", 18)).place(**kw)

    # ── VOICE ────────────────────────────────────────────────────────────────
    def _toggle_mic(self):
        if self._listening: return
        self._listening = True
        self.btn_mic.configure(text="🔴 聆听中", fg_color="#0A1A00",
                               text_color=C_GREEN)
        threading.Thread(target=self._listen_voice, daemon=True).start()

    def _listen_voice(self):
        try:
            mic = sr.Microphone()
            with mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=8, phrase_time_limit=15)
            text = self._recognizer.recognize_google(audio, language="zh-CN")
            self.after(0, lambda: self.entry.delete(0, "end"))
            self.after(0, lambda: self.entry.insert(0, text))
            self.after(0, self._send_text)
        except sr.WaitTimeoutError:
            self.after(0, lambda: self._log("▸ 语音：超时未检测到声音\n"))
        except sr.UnknownValueError:
            self.after(0, lambda: self._log("▸ 语音：未能识别，请重试\n"))
        except Exception as e:
            self.after(0, lambda: self._log(f"▸ 语音错误: {e}\n"))
        finally:
            self._listening = False
            self.after(0, lambda: self.btn_mic.configure(
                text="🎤 语音", fg_color="#0A1A1A", text_color=C_CYAN))

    # ── CHAT ─────────────────────────────────────────────────────────────────
    def _reload_history(self):
        for m in load_hist()[-8:]: self._bubble(m["role"], m["content"])

    def _send_text(self):
        msg = self.entry.get().strip()
        if not msg: return
        self.entry.delete(0, "end")
        self._bubble("user", msg)
        save_hist("user", msg)
        self.lbl_status.configure(text="◉  思考中...", text_color=C_CYAN)
        self.btn_send.configure(state="disabled", text="等待")
        self.soul_canvas.set_thinking(True)
        threading.Thread(target=self._api, args=(msg,), daemon=True).start()

    def _bubble(self, role, text):
        is_user   = role == "user"
        is_system = role == "system"   # 工具调用透明气泡
        container = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        container.pack(fill="x", pady=3 if is_system else 6, padx=12)

        if is_system:
            # 工具调用：深色小条，让老板看到悟空真正做了什么
            bg  = "#0D2A1A"
            bdr = "#1A4A2A"
            role_txt = "⚙ 工具执行"
            role_col = "#3AFF8A"
            wrap = 760
        elif is_user:
            bg  = "#0A1A10"
            bdr = C_GOLD
            role_txt = "老板"
            role_col = C_GOLD
            wrap = 700
        else:
            bg  = C_BG1
            bdr = C_BORDER
            role_txt = "🐵 悟空"
            role_col = C_CYAN
            wrap = 700

        bubble = ctk.CTkFrame(container, fg_color=bg, corner_radius=8 if is_system else 12,
                               border_width=1, border_color=bdr)
        bubble.pack(side="left", anchor="w",
                    fill="x" if is_system else "none",
                    expand=is_system)

        ctk.CTkLabel(bubble, text=role_txt,
                     font=("Microsoft YaHei UI", 9 if is_system else 10, "bold"),
                     text_color=role_col).pack(
                         anchor="w", padx=14, pady=(5 if is_system else 8, 0))
        ctk.CTkLabel(bubble, text=text,
                     font=("Microsoft YaHei UI", 11) if is_system else F_CHAT,
                     text_color="#8ADFB0" if is_system else C_TEXT,
                     wraplength=wrap, justify="left").pack(
                         padx=14, pady=(1 if is_system else 2, 6 if is_system else 12))
        try:
            self.chat_area.update_idletasks()
            self.chat_area._parent_canvas.yview_moveto(1.0)
        except: pass

    # ── 判断该消息是否必须先调工具才能回答 ──────────────────────────────────
    # _requires_tool 已移除：悟空通过元认知自检自主判断是否需要调工具

    # ── 智能识别对话方向 ──────────────────────────────────────────────────────
    def _detect_direction(self, msg, reply):
        text = (msg + " " + reply).lower()

        secretary_kw = [
            "计划","日程","待办","提醒","安排","会议","纪要","跟进","任务",
            "时间","今天","明天","本周","截止","deadline","备忘","清单",
            "客户","约见","预约","汇报","总结","复盘","工作",
        ]
        avatar_kw = [
            "回复","代发","代写","模仿","风格","飞书","微信","消息","沟通",
            "客户说","怎么回","帮我说","接待","代理","语气","口吻",
            "聊天","发给","转告","通知","联系",
        ]
        content_kw = [
            "文案","视频","脚本","标题","短视频","抖音","小红书","b站",
            "内容","创作","写作","爆款","发布","策划","素材","封面",
            "文章","推文","朋友圈","种草","直播","带货",
        ]

        def score(kws): return sum(1 for k in kws if k in text)
        s_sec = score(secretary_kw)
        s_ava = score(avatar_kw)
        s_con = score(content_kw)

        base_xp = min(50, max(5, len(reply) // 20))

        if s_sec == 0 and s_ava == 0 and s_con == 0:
            return "secretary", base_xp, "日常沟通"
        if s_sec >= s_ava and s_sec >= s_con:
            return "secretary", min(base_xp + s_sec * 3, 80), f"秘书任务(匹配{s_sec}词)"
        elif s_ava >= s_con:
            return "avatar", min(base_xp + s_ava * 3, 80), f"分身沟通(匹配{s_ava}词)"
        else:
            return "content", min(base_xp + s_con * 3, 80), f"内容执行(匹配{s_con}词)"

    # ── API 调用（Function Calling 完整版）────────────────────────────────────
    def _api(self, msg):
        self.after(0, lambda: self._log(f"▸ 发送: {msg[:60]}\n"))
        try:
            hdrs = {"Content-Type": "application/json",
                    "Authorization": f"Bearer {self._api_key}"}

            # 动态加载长期记忆
            memory_content = ""
            try:
                if os.path.exists(MEMORY_LONG):
                    with open(MEMORY_LONG, "r", encoding="utf-8") as f:
                        memory_content = f.read()[:2000]
            except: pass

            # 动态加载已习得能力（让悟空知道自己会什么）
            capabilities_content = ""
            try:
                cap_file = os.path.join(WORKSPACE_DIR, "CAPABILITIES.md")
                if os.path.exists(cap_file):
                    with open(cap_file, "r", encoding="utf-8") as f:
                        capabilities_content = f.read()[:1500]
            except: pass

            tools_status = "已启用（可真实调用）" if TOOLS_ENABLED else "未加载（只能推断）"

            sys_prompt = (
                "你是悟空，老板的私人AI生活秘书和数字分身。\n"
                "你拥有真实工具，可以主动调用工具获取真实数据。\n\n"

                "【每次回答前的三步内心自检】\n"
                "第一步：这个问题属于哪类？\n"
                "  A类（确定知道，刚查到的真实数据）→ 直接答\n"
                "  B类（记忆里有但可能过时）→ 说明来源，主动提出查验\n"
                "  C类（不确定，有模糊印象但没真实数据）→ 说'让我查一下'，立刻调工具\n"
                "  D类（完全不知道）→ 直接调工具查，拿到结果再答，绝不猜\n"
                "第二步：C类或D类该用哪个工具？\n"
                "  实时信息/新闻/趋势 → search_web 或 deep_research\n"
                "  技术方案/开源代码 → search_github\n"
                "  链接内容 → open_url\n"
                "  时间日期 → get_datetime\n"
                "  老板说的文件 → read_file\n"
                "第三步：工具失败了怎么办？\n"
                "  换角度重搜一次，或换工具再试，两次都失败再告诉老板搜不到，绝不编造\n\n"

                "【工具选择指南】\n"
                "search_web → 一条具体信息、新闻、价格\n"
                "deep_research → 研究话题、竞品分析、行业趋势（自动联合Google+GitHub）\n"
                "search_github → 找现成开源工具/代码，遇到'能不能做XXX'先来这里找\n"
                "read_github_repo → 深入了解某个项目的用法\n"
                "get_datetime → 任何时间相关问题\n"
                "query_evomap → 涉及EVOMAP积分/技能\n"
                "send_feishu → 发送飞书消息\n"
                "read_memory / write_memory → 读写长期记忆\n"
                "write_capability → 发现可复用套路时，自动记录能力轮廓（不需要老板要求）\n\n"

                "【能力进化：自动执行，不需要汇报】\n"
                "完成任务后问自己：'这个套路下次还能用吗？' 是 → 调用 write_capability 记录\n"
                "触发场景：多工具组合完成复杂任务 / 老板第二次问类似问题 / 发现固定模式\n\n"

                "【回复格式铁律】\n"
                "绝对禁止：**粗体**、# 标题、--- 分割线、`代码块`、任何Markdown符号\n"
                "必须使用：纯文字、1. 2. 3. 数字列表、→ 箭头\n"
                "禁止开场白（禁止说'好的''当然''没问题'），直接给结果\n"
                "口语化短句，像秘书汇报工作，研究报告注明来源\n\n"

                f"【工具状态】{tools_status}\n"
                f"老板风格：'GO'=立刻执行，'没有'=出问题了，不废话直接给结果\n\n"
                f"【长期记忆】\n{memory_content}\n\n"
                + (f"【我已习得的能力（遇到相关问题直接应用）】\n{capabilities_content}\n" if capabilities_content else "")
            )

            # 构建消息列表
            msgs = [{"role": "system", "content": sys_prompt}]
            msgs.extend(load_hist()[-12:])
            msgs.append({"role": "user", "content": msg})

            # ── Function Calling 循环（最多5轮工具调用）────────────────────────
            tool_calls_log = []
            max_rounds = 5

            for round_n in range(max_rounds):
                req_body = {
                    "model": MODEL,
                    "messages": msgs,
                    "stream": False,
                }
                # 只在工具可用时传入tools参数
                if TOOLS_ENABLED:
                    req_body["tools"] = TOOLS_SCHEMA
                    req_body["tool_choice"] = "auto"

                r = requests.post(API_URL, headers=hdrs, json=req_body, timeout=90)

                # Key失效自动切换
                if r.status_code in (401, 403) and self._api_key == API_KEY_PRIMARY:
                    self.after(0, lambda: self._log("▸ 主Key失效，切换备用Key...\n"))
                    self._api_key = API_KEY_BACKUP
                    hdrs["Authorization"] = f"Bearer {self._api_key}"
                    r = requests.post(API_URL, headers=hdrs, json=req_body, timeout=90)

                if r.status_code != 200:
                    err = f"⚠ 连接失败 {r.status_code}"
                    self.after(0, lambda e=err: self._bubble("assistant", e))
                    self.after(0, lambda e=err: self._log(f"▸ 错误: {e}\n"))
                    return

                resp_data = r.json()
                choice = resp_data["choices"][0]
                finish_reason = choice.get("finish_reason", "stop")
                message = choice["message"]

                # ── 没有工具调用，悟空已自主决定直接回答 ────────────────────
                if finish_reason != "tool_calls" or not message.get("tool_calls"):
                    reply = message.get("content", "")

                    # 工具执行完但模型返回空内容 → 追加指令让他汇总
                    if not reply and tool_calls_log:
                        msgs.append({
                            "role": "user",
                            "content": "请根据上面的工具结果，用中文回答用户的问题。"
                        })
                        continue

                    if not reply:
                        reply = "（悟空没有生成回复，请重新提问。）"

                    # 如果有工具调用历史，附上简要说明
                    if tool_calls_log:
                        tool_summary = "→ ".join(tool_calls_log)
                        self.after(0, lambda s=tool_summary: self._log(f"▸ 工具链：{s}\n"))

                    self.after(0, lambda rep=reply: self._bubble("assistant", rep))
                    save_hist("assistant", reply)
                    self.after(0, lambda rep=reply: self._log(f"▸ 回复: {rep[:80]}\n"))

                    direction, xp, label = self._detect_direction(msg, reply)
                    dir_names = {"secretary":"秘书大师","avatar":"沟通分身","content":"内容执行"}
                    self.after(0, lambda d=direction, x=xp, l=label: self._award(d, x, l))
                    self.after(0, lambda d=direction, x=xp, l=label:
                        self._log(f"▸ XP: +{x} → {dir_names.get(d,d)} [{l}]\n"))
                    threading.Thread(
                        target=write_memory, args=(msg, reply, direction, xp, label),
                        daemon=True).start()
                    speak_async(reply)
                    return

                # ── 有工具调用，依次执行 ─────────────────────────────────────
                # 先把assistant消息（含tool_calls）放入msgs
                msgs.append(message)

                for tc in message["tool_calls"]:
                    fn_name = tc["function"]["name"]
                    try:
                        fn_args = json.loads(tc["function"].get("arguments", "{}"))
                    except:
                        fn_args = {}
                    tool_call_id = tc["id"]

                    # 日志记录
                    self.after(0, lambda n=fn_name, a=fn_args:
                        self._log(f"▸ 调用工具: {n}({json.dumps(a, ensure_ascii=False)[:80]})\n"))

                    # 在聊天界面显示"正在调用工具"提示（让老板看到）
                    arg_preview = json.dumps(fn_args, ensure_ascii=False)[:60]
                    tool_notice = f"[工具调用] {fn_name}({arg_preview})"
                    self.after(0, lambda t=tool_notice: self._bubble("system", t))

                    # 真实执行工具
                    tool_result = execute_tool(fn_name, fn_args)

                    # 在聊天界面显示工具真实结果的摘要
                    result_preview = tool_result[:200] if tool_result else "（无结果）"
                    result_notice = f"[工具结果] {result_preview}"
                    self.after(0, lambda t=result_notice: self._bubble("system", t))

                    self.after(0, lambda res=tool_result:
                        self._log(f"▸ 工具结果: {res[:120]}\n"))

                    tool_calls_log.append(fn_name)

                    # 把工具结果加入消息列表
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": fn_name,
                        "content": tool_result
                    })

            # 超过最大轮数
            self.after(0, lambda: self._bubble("assistant",
                "工具调用轮数超限，可能遇到了复杂问题。请换个方式问我。"))

        except Exception as e:
            self.after(0, lambda err=str(e): self._bubble("assistant",
                f"⚠ 悟空遇到异常：{err[:100]}"))
            self.after(0, lambda err=str(e): self._log(f"▸ 异常: {err}\n"))
        finally:
            self.after(0, lambda: self.soul_canvas.set_thinking(False))
            self.after(0, lambda: self.lbl_status.configure(
                text="◉  在线", text_color=C_GREEN))
            self.after(0, lambda: self.btn_send.configure(
                state="normal", text="发送"))

    def _log(self, text):
        try: self.sys_log.insert("end", text); self.sys_log.see("end")
        except: pass

    # ── XP ───────────────────────────────────────────────────────────────────
    def _award(self, direction, amount, note=""):
        evo = add_xp(direction, amount, note)
        self._update_total(evo)
        try:
            if direction in self._dir_cards:
                self._dir_cards[direction].update(evo["directions"][direction]["xp"])
            self._refresh_log()
        except: pass

    def _manual_xp(self):
        try: amt = int(self._xp_amt.get().strip() or "0")
        except: amt = 0
        if amt <= 0: return
        note = self._xp_note.get().strip()
        self._award(self._xp_dir.get(), amt, note)
        self._xp_amt.delete(0, "end"); self._xp_note.delete(0, "end")
        self._refresh_evo(); self._refresh_log()

    def _update_total(self, evo=None):
        if evo is None: evo = load_evo()
        xp = evo.get("total_xp", 0)
        lv, nm, prog, left = xian_info(xp)
        self.bar_total.set(prog)
        self.lbl_realm.configure(text=f"{nm}  ·  Lv.{lv}")
        self.lbl_total_xp.configure(
            text=f"{xp:,} XP  ·  还需 {left:,}" if left else f"{xp:,} XP  ·  大乘圆满")
        self.soul_canvas.set_level(lv)

    def _refresh_evo(self):
        evo = load_evo()
        self._update_total(evo)
        for key, card in self._dir_cards.items():
            card.update(evo["directions"][key]["xp"])

    def _refresh_log(self):
        evo = load_evo()
        try:
            self.evo_log_box.delete("1.0", "end")
            logs = evo.get("evolution_log", [])
            if not logs: self.evo_log_box.insert("end", "▸ 暂无进化记录，开始修炼！\n")
            for e in logs: self.evo_log_box.insert("end", e + "\n")
        except: pass

    # ── STATUS ────────────────────────────────────────────────────────────────
    def _check_status(self):
        def _chk():
            try:
                requests.get("https://api.siliconflow.cn/v1/models",
                             headers={"Authorization": f"Bearer {self._api_key}"}, timeout=5)
                self.after(0, lambda: self.lbl_status.configure(
                    text="◉  在线", text_color=C_GREEN))
            except:
                self.after(0, lambda: self.lbl_status.configure(
                    text="◉  离线", text_color=C_RED))
        threading.Thread(target=_chk, daemon=True).start()
        self._update_total()
        self._refresh_evo()
        self.after(30000, self._check_status)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        print("悟空 HUD v1.0 — 私人秘书·数字分身·内容执行")
        app = WukongHUD()
        app.mainloop()
    except Exception as e:
        import traceback; traceback.print_exc()
        input("按回车键退出...")
