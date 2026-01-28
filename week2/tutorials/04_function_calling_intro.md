# 🔧 Function Calling 详解

> **学习目标**：掌握AI调用外部函数的能力，让AI从"聊天"变成"做事"

---

## 1. 什么是Function Calling？

让AI能够**调用你定义的函数**，获取实时数据或执行操作。

**示例**：
- 用户："今天北京天气怎么样？"
- AI：（调用`get_weather("北京")`函数）
- AI："北京今天晴天，25°C"

---

## 2. 工作流程

```
用户提问 → AI判断需要调用函数 → 返回函数调用请求 
    → 你执行函数 → 将结果返回给AI → AI生成最终回答
```

---

## 3. 实战代码

```python
from config.deepseek_client import get_client
import json

client = get_client()

# 定义可用的工具（函数）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 模拟天气函数
def get_weather(city: str) -> str:
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，22°C",
        "广州": "小雨，28°C"
    }
    return weather_data.get(city, "未知城市")

# 调用API
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools,
    tool_choice="auto"
)

# 检查是否需要调用函数
message = response.choices[0].message
if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    # 执行函数
    result = get_weather(arguments["city"])
    
    # 将结果返回给AI
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "北京今天天气怎么样？"},
            message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            }
        ]
    )
    print(final_response.choices[0].message.content)
```

**输出**：`北京今天是晴天，气温25°C，适合外出活动！`

---

## 4. 多函数示例

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索网页",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送邮件",
            "parameters": {...}
        }
    }
]
```

AI会根据用户问题**自动选择**合适的函数！

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 吴恩达AI | Function Calling详解 | https://www.bilibili.com/video/BV1es4y1G7Dy |
| DataWhale | 大模型工具调用原理 | https://www.bilibili.com/video/BV1Yc41197Xz |

---

## 6. 继续学习

🎉 **恭喜！你已完成Week 2基础课程！**

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解
3. ✅ Function Calling详解（本教程）

在左侧菜单选择 **Week 3** 的教程继续学习MCP协议！

---

**Function Calling让AI拥有"手脚"，能够与真实世界交互！💪**

