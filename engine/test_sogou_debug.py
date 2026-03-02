# -*- coding: utf-8 -*-
import requests, re, sys
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"
r = requests.get("https://www.sogou.com/web", params={"query": "抖音涨粉技巧 2026"},
                 timeout=12, headers={"User-Agent": UA, "Accept-Language": "zh-CN"})

text = r.text
# 保存样本
with open("sogou_sample.html", "w", encoding="utf-8", errors="replace") as f:
    f.write(text[:80000])
print(f"搜狗HTML长度: {len(text)}, 保存了前80000字节")

clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()

# 尝试各种摘要pattern
patterns = [
    (r'<p class="str-[^"]*"[^>]*>(.*?)</p>', "str-class p"),
    (r'<div class="str-[^"]*"[^>]*>(.*?)</div>', "str-class div"),
    (r'class="[^"]*abstract[^"]*"[^>]*>(.*?)</(?:p|div|span)>', "abstract"),
    (r'class="[^"]*txt[^"]*"[^>]*>(.*?)</(?:p|div|span)>', "txt"),
    (r'class="[^"]*desc[^"]*"[^>]*>(.*?)</(?:p|div|span)>', "desc"),
    (r'class="[^"]*content[^"]*"[^>]*>(.*?)</(?:p|div|span)>', "content"),
    (r'<p class="">(.*?)</p>', "empty class p"),
    (r'class="[^"]*result[^"]*".*?<p[^>]*>(.*?)</p>', "result > p"),
]

for pat, name in patterns:
    matches = re.findall(pat, text[:40000], re.DOTALL)
    cleaned = [clean(m)[:80] for m in matches if len(clean(m)) > 10][:3]
    if cleaned:
        print(f"[{name}]: {cleaned}")

# 查找h3附近内容
print("\n=== h3附近内容 ===")
blocks = re.findall(r'<h3[^>]*>.*?</h3>(.*?)(?=<h3|</div>)', text[:50000], re.DOTALL)
for b in blocks[:3]:
    c = clean(b)[:150]
    if c:
        print(f"  {c}")
