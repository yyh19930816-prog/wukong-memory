# -*- coding: utf-8 -*-
"""调试搜索页面，找对正则"""
import requests, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# 测试百度
r = requests.get(
    "https://www.baidu.com/s",
    params={"wd": "抖音涨粉技巧 2026"},
    timeout=12,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
)
text = r.text

# 保存一段HTML看看
with open("baidu_sample.html", "w", encoding="utf-8", errors="replace") as f:
    f.write(text[:30000])
print("百度HTML前30000字节已保存到 baidu_sample.html")

# 尝试不同的正则
patterns = [
    r'"content-right_8Zs40"[^>]*>(.*?)</div>',
    r'<div class="c-abstract[^"]*"[^>]*>(.*?)</div>',
    r'class="result[^"]*"[^>]*>.*?<h3[^>]*>(.*?)</h3>',
    r'<h3 class="[^"]*t[^"]*">(.*?)</h3>',
    r'data-title="([^"]+)"',
    r'"title":"([^"]+)"',
]

for p in patterns:
    matches = re.findall(p, text[:50000], re.DOTALL)
    clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()[:60]
    cleaned = [clean(m) for m in matches[:3] if clean(m)]
    print(f"Pattern: {p[:40]}... → {len(matches)} matches: {cleaned}")
