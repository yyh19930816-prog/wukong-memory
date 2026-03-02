# -*- coding: utf-8 -*-
import requests, sys, re
sys.stdout.reconfigure(encoding='utf-8')

print("=== 测试Bing连通性 ===")
try:
    r = requests.get(
        "https://www.bing.com/search",
        params={"q": "2026 AI trend", "cc": "CN"},
        timeout=12,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    )
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    titles = re.findall(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text[:8000], re.DOTALL)
    print(f"Titles found: {len(titles)}")
    for url, t in titles[:3]:
        clean_t = re.sub(r'<[^>]+>', '', t).strip()
        print(f"  - {clean_t[:60]}")
except Exception as e:
    print(f"Bing ERR: {e}")

print()
print("=== 测试DuckDuckGo HTML ===")
try:
    r2 = requests.get(
        "https://html.duckduckgo.com/html/",
        params={"q": "抖音涨粉技巧 2026"},
        timeout=12,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    )
    print(f"Status: {r2.status_code}, Length: {len(r2.text)}")
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', r2.text, re.DOTALL)
    titles2 = re.findall(r'class="result__a"[^>]*>(.*?)</a>', r2.text, re.DOTALL)
    clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()
    for t, s in list(zip(titles2, snippets))[:3]:
        print(f"  {clean(t)[:50]}: {clean(s)[:80]}")
except Exception as e:
    print(f"DDG ERR: {e}")

print()
print("=== 测试Baidu ===")
try:
    r3 = requests.get(
        "https://www.baidu.com/s",
        params={"wd": "抖音涨粉技巧 2026"},
        timeout=12,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
                 "Accept-Language": "zh-CN,zh;q=0.9"}
    )
    print(f"Status: {r3.status_code}, Length: {len(r3.text)}")
    # 百度摘要
    abs_list = re.findall(r'"c-abstract[^"]*"[^>]*>(.*?)</p>', r3.text, re.DOTALL)
    clean = lambda s: re.sub(r'<[^>]+>', '', s).strip()
    for a in abs_list[:3]:
        c = clean(a)
        if c:
            print(f"  {c[:100]}")
except Exception as e:
    print(f"Baidu ERR: {e}")
