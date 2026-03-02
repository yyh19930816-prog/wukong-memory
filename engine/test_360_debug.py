# -*- coding: utf-8 -*-
import requests, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"

# 先访问360首页建立session
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
s.get("https://www.so.com/", timeout=8)

r = s.get("https://www.so.com/s", params={"q": "2026抖音运营涨粉技巧"}, timeout=12)
text = r.text
print(f"360 Status: {r.status_code}, Length: {len(text)}")

with open("360_sample.html", "w", encoding="utf-8", errors="replace") as f:
    f.write(text[:80000])

clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()

# 试各种pattern
patterns = [
    (r'<h3[^>]*>(.*?)</h3>', "h3"),
    (r'class="[^"]*res-desc[^"]*"[^>]*>(.*?)</(?:p|div)', "res-desc"),
    (r'class="[^"]*result-item[^"]*".*?<h3[^>]*>(.*?)</h3>', "result-item h3"),
    (r'<div class="res-linkinfo[^"]*">(.*?)</div>', "res-linkinfo"),
    (r'"title":"([^"]+)"', "json title"),
    (r'"description":"([^"]+)"', "json desc"),
]
for pat, name in patterns:
    matches = re.findall(pat, text[:60000], re.DOTALL)
    cleaned = [clean(m)[:80] for m in matches if len(clean(m)) > 5][:4]
    if cleaned:
        print(f"[{name}] ({len(matches)}): {cleaned}")

# 找h3附近的段落
print("\n=== h3块内容 ===")
blocks = re.findall(r'(<li[^>]*>.*?</li>)', text[:60000], re.DOTALL)
for b in blocks[:5]:
    h3 = re.search(r'<h3[^>]*>(.*?)</h3>', b, re.DOTALL)
    p_tags = re.findall(r'<p[^>]*>(.*?)</p>', b, re.DOTALL)
    if h3:
        title = clean(h3.group(1))[:60]
        desc = " | ".join([clean(p)[:50] for p in p_tags if len(clean(p)) > 10])[:100]
        print(f"  T: {title}")
        if desc:
            print(f"  D: {desc}")
