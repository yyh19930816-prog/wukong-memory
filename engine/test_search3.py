# -*- coding: utf-8 -*-
"""测试各种搜索方式，找出哪个能返回真实结果"""
import requests, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
QUERY = "2026抖音运营涨粉技巧"

# === 方法1：Bing，保存HTML看结构 ===
print("=== Bing ===")
r = requests.get("https://www.bing.com/search", params={"q": QUERY, "setlang": "zh-Hans"}, timeout=12, headers={"User-Agent": UA})
print(f"Status: {r.status_code}")
# 保存并分析
with open("bing_sample.html", "w", encoding="utf-8", errors="replace") as f:
    f.write(r.text[:50000])

# 找所有<h2>标签
h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', r.text, re.DOTALL)
clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()
for h in h2s[:5]:
    c = clean(h)
    if c:
        print(f"  H2: {c[:80]}")

# 找<li class="b_algo">
b_algos = re.findall(r'<li class="b_algo">(.*?)</li>', r.text, re.DOTALL)
print(f"  b_algo items: {len(b_algos)}")
if b_algos:
    sample = clean(b_algos[0])[:200]
    print(f"  First: {sample}")

# 找<p>标签内容
ps = re.findall(r'<p[^>]*>(.*?)</p>', r.text, re.DOTALL)
cleaned_ps = [clean(p)[:100] for p in ps if len(clean(p)) > 30][:5]
for p in cleaned_ps:
    print(f"  P: {p}")

print()
# === 方法2：DuckDuckGo HTML（检查202) ===
print("=== DuckDuckGo ===")
r2 = requests.get(
    "https://html.duckduckgo.com/html/",
    params={"q": QUERY},
    timeout=12,
    headers={"User-Agent": UA, "Accept": "text/html"}
)
print(f"Status: {r2.status_code}, len={len(r2.text)}")
if r2.status_code == 200:
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:span|a|div)>', r2.text, re.DOTALL)
    for s in snippets[:3]:
        c = clean(s)
        if c:
            print(f"  {c[:100]}")

print()
# === 方法3：SogouWap ===
print("=== Sogou ===")
try:
    r3 = requests.get("https://www.sogou.com/web", params={"query": QUERY}, timeout=10,
                      headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
    print(f"Status: {r3.status_code}, len={len(r3.text)}")
    titles3 = re.findall(r'<h3[^>]*>(.*?)</h3>', r3.text, re.DOTALL)
    for t in titles3[:3]:
        c = clean(t)
        if c:
            print(f"  {c[:80]}")
except Exception as e:
    print(f"ERR: {e}")

print()
# === 方法4: 360搜索 ===
print("=== 360搜索 ===")
try:
    r4 = requests.get("https://www.so.com/s", params={"q": QUERY}, timeout=10,
                      headers={"User-Agent": UA, "Accept-Language": "zh-CN"})
    print(f"Status: {r4.status_code}, len={len(r4.text)}")
    titles4 = re.findall(r'<h3[^>]*>(.*?)</h3>', r4.text, re.DOTALL)
    for t in titles4[:3]:
        c = clean(t)
        if c:
            print(f"  {c[:80]}")
except Exception as e:
    print(f"ERR: {e}")
