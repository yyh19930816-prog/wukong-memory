# -*- coding: utf-8 -*-
"""
悟空搜索能力激活工具
运行此脚本可以测试Serper API Key是否有效，并自动写入配置
"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

TOOLS_FILE = os.path.join(os.path.dirname(__file__), "wukong_tools.py")

print("=" * 50)
print("悟空搜索能力激活")
print("=" * 50)
print()
print("步骤：")
print("1. 打开网址：https://serper.dev")
print("2. 点右上角 Sign Up，用Google账号或邮箱注册")
print("3. 注册后自动进入控制台，找到 API Key 复制")
print("   (免费2500次Google搜索，够用半年)")
print()

api_key = input("请粘贴你的 Serper API Key（直接Enter跳过）：").strip()

if not api_key:
    print("已跳过。你可以之后手动编辑 wukong_tools.py，把 SERPER_API_KEY = '' 改为你的Key。")
    sys.exit(0)

# 测试Key是否有效
print(f"\n正在测试 Key：{api_key[:8]}...{api_key[-4:]}")
try:
    import requests
    r = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": "抖音涨粉技巧 2026", "num": 3, "gl": "cn", "hl": "zh-cn"},
        timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        organic = data.get("organic", [])
        print(f"✓ API Key有效！搜索返回 {len(organic)} 条Google真实结果：")
        for i, item in enumerate(organic[:3], 1):
            print(f"  {i}. {item.get('title','')[:60]}")
        print()
        
        # 写入配置
        with open(TOOLS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = re.sub(
            r'SERPER_API_KEY\s*=\s*""',
            f'SERPER_API_KEY    = "{api_key}"',
            content
        )
        
        if new_content != content:
            with open(TOOLS_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✓ API Key 已自动写入 wukong_tools.py")
            print("✓ 悟空现在可以真实搜索Google了！")
            print("  重启 wukong_hud.py 生效")
        else:
            print("注意：自动写入失败，请手动把以下内容复制到 wukong_tools.py 第25行：")
            print(f'  SERPER_API_KEY = "{api_key}"')
    elif r.status_code == 401:
        print(f"✗ API Key无效（401），请确认复制正确")
    else:
        print(f"✗ 请求失败 HTTP {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"✗ 测试失败：{e}")
    print("  请检查网络连接")

print()
input("按Enter退出...")
