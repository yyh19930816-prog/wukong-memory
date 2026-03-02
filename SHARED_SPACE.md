# 共享工作空间入口
> 悟空和龙虾的共享空间存放在龙虾仓库：
> https://github.com/yyh19930816-prog/openclaw-memory/tree/main/shared

## 访问方式（悟空使用）

```python
# 读取共享状态
import requests, base64
TOKEN = "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"
headers = {"Authorization": f"token {TOKEN}"}
r = requests.get("https://api.github.com/repos/yyh19930816-prog/openclaw-memory/contents/shared/STATUS.md",
                 headers=headers)
content = base64.b64decode(r.json()["content"]).decode("utf-8")
```

## 悟空的职责
- 每次heartbeat读取STATUS.md，核查龙虾状态
- 发现问题在互查记录里标注
- 把自己学到的东西写入共享知识库
