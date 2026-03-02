# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'.')
sys.stdout.reconfigure(encoding='utf-8')
from wukong_tools import tool_search_web, tool_deep_research

print("=== 测试 search_web ===")
result = tool_search_web("2026年抖音运营技巧")
print(result[:800])

print()
print("=== 测试 deep_research ===")
result2 = tool_deep_research("抖音博主涨粉策略", "涨粉方法,内容选题,发布时间")
print(result2[:1200])
