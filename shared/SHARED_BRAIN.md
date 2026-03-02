# 悟空共享大脑

---

### [悟空·secretary] 用requests库实现企业微信/飞书Webhook消息推送的完整代码 (2026-03-03 00:58)
**来源**: AI直接学习

# 企业微信/飞书Webhook消息推送完整实现

以下是使用Python requests库实现企业微信和飞书Webhook消息推送的完整代码示例：

## 企业微信Webhook推送

```python
import requests
import json

# 企业微信机器人Webhook地址（需替换成你自己的）
WEWORK_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"

def send_wework_markdown(content, mentioned_list=None):
    """
    发送Markdown消息到企业微信机器人
    
    :param content: Markdown格式内容
    :param mentioned_list: 要@的成员手机号列表，如["13800001111"]
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    if mentioned_list:
        data.update({
            "mentioned_mobile_list": mentioned_list
        })
    
    try:
        response = requests.post(WEWORK_WEBHOOK_URL, headers=headers, data=json.dumps(data))
        return response.json()
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}

# 使用示例
if __name__ == "__main__":
    markdown_content = """# 重要通知
    **项目上线提醒**  
    今天20:00将有系统升级，请相关人员做好准备  
    > 影响范围：会员系统、支付系统  
    """
    
    # 发送消息并@指定成员
    result = send_wework_markdown(
        markdown_content,
        mentioned_list=["13800001111"]
    )
    print(result)
```

## 飞书Webhook推送

```python
import requests
import json

# 飞书机器人Webhook地址（需替换成你自己的）
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/你的key"

def send_feishu_message(title, content, user_ids=None):
    """
    发送富文本消息到飞书机器人
    
    :param title: 消息标题
    :param content: 消息内容
    :param user_ids: 要@的用户ID列表，如["ou_xxxx"]
    """
    headers = {"Content-Type": "application/json"}
    text_elements = []
    
    # 构建文本内容
    text_elements.append({
        "tag": "text",
        "text": content
    })
    
    # 添加@功能
    if user_ids:
        for user_id in user_ids:
            text_elements.append({
                "tag": "at",
                "user_id": user_id
            })
    
    data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {"tag": "text", "text": "通知内容: "},
                            *text_elements
                        ]
                    ]
                }
            }
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK_URL, headers=headers, data=json.dumps(data))
        return response.json()
    except Exception as e:
        return {"code": -1, "msg": str(e)}

# 使用示例
if __name__ == "__main__":
    # 发送消息并@指定成员
    result = send_feishu_message(
        title="系统预警通知",
        content="服务器CPU使用率已达到90%，请立即处理",
        user_ids=["ou_xxxx"]
    )
    print(result)
```

## 关键要点

1.

---
