# 💰 Token计算与成本优化

> **学习目标**：掌握Token计算方法，学会控制API成本，优化Prompt效率

---

## 1. 什么是Token？

### Token基础概念

**Token**是AI模型处理文本的最小单位，不等于字符或单词：

```
英文: "Hello world" → ["Hello", " world"] → 2 tokens
中文: "你好世界" → ["你好", "世界"] → 2 tokens (大约1字=1token)
代码: "def hello():" → ["def", " hello", "():", ...] → 多个tokens
```

### 为什么Token很重要？

1. **定价基础**：API按Token收费
2. **上下文限制**：每个模型有Token上限
3. **响应速度**：Token越多，处理越慢

---

## 2. 使用Tiktoken计算Token

### 2.1 安装

```bash
pip install tiktoken
```

### 2.2 基本用法

```python
import tiktoken

# 获取编码器（不同模型用不同编码）
enc = tiktoken.get_encoding("cl100k_base")  # GPT-4, GPT-3.5使用
# enc = tiktoken.encoding_for_model("gpt-4")  # 自动选择

# 编码
text = "Hello, 你好世界！"
tokens = enc.encode(text)
print(f"Token数量: {len(tokens)}")
print(f"Token列表: {tokens}")

# 解码
decoded = enc.decode(tokens)
print(f"解码结果: {decoded}")
```

### 2.3 计算消息Token

```python
def count_message_tokens(messages: list, model: str = "gpt-4") -> int:
    """计算消息列表的Token数量"""
    enc = tiktoken.encoding_for_model(model)
    
    # 每条消息的开销
    tokens_per_message = 4  # role + content开销
    
    total = 0
    for message in messages:
        total += tokens_per_message
        total += len(enc.encode(message.get("role", "")))
        total += len(enc.encode(message.get("content", "")))
    
    total += 2  # 对话结束标记
    return total

# 使用
messages = [
    {"role": "system", "content": "你是一个有帮助的助手。"},
    {"role": "user", "content": "什么是Python？"}
]

tokens = count_message_tokens(messages)
print(f"消息Token数: {tokens}")
```

---

## 3. 成本计算

### 3.1 各模型定价（2024年参考）

| 模型 | 输入 | 输出 | 上下文长度 |
|------|------|------|------------|
| DeepSeek-Chat | ¥1/百万Token | ¥2/百万Token | 64K |
| GPT-4o | $5/百万Token | $15/百万Token | 128K |
| GPT-4o-mini | $0.15/百万Token | $0.6/百万Token | 128K |
| GPT-3.5 | $0.5/百万Token | $1.5/百万Token | 16K |
| Claude-3.5-Sonnet | $3/百万Token | $15/百万Token | 200K |

### 3.2 成本估算函数

```python
def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "deepseek-chat"
) -> dict:
    """估算API调用成本"""
    
    # 定价表（每百万Token）
    pricing = {
        "deepseek-chat": {"input": 1.0, "output": 2.0, "currency": "CNY"},
        "gpt-4o": {"input": 5.0, "output": 15.0, "currency": "USD"},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6, "currency": "USD"},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5, "currency": "USD"},
    }
    
    if model not in pricing:
        return {"error": f"未知模型: {model}"}
    
    p = pricing[model]
    input_cost = (input_tokens / 1_000_000) * p["input"]
    output_cost = (output_tokens / 1_000_000) * p["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "currency": p["currency"]
    }

# 使用
cost = estimate_cost(1000, 500, "deepseek-chat")
print(f"总成本: {cost['total_cost']} {cost['currency']}")
```

### 3.3 日成本/月成本估算

```python
def estimate_monthly_cost(
    avg_input_tokens: int,
    avg_output_tokens: int,
    calls_per_day: int,
    model: str = "deepseek-chat"
) -> dict:
    """估算月度API成本"""
    
    single_call = estimate_cost(avg_input_tokens, avg_output_tokens, model)
    
    daily_cost = single_call["total_cost"] * calls_per_day
    monthly_cost = daily_cost * 30
    
    return {
        "single_call_cost": single_call["total_cost"],
        "daily_cost": round(daily_cost, 2),
        "monthly_cost": round(monthly_cost, 2),
        "currency": single_call["currency"]
    }

# 使用场景：客服机器人
# 平均每次对话：输入500Token，输出300Token
# 每天1000次对话
cost = estimate_monthly_cost(500, 300, 1000, "deepseek-chat")
print(f"月度成本: {cost['monthly_cost']} {cost['currency']}")
```

---

## 4. Prompt优化策略

### 4.1 精简System Prompt

```python
# ❌ 冗余的Prompt（约100 tokens）
system_bad = """
你是一个非常有帮助的AI助手。你需要尽可能地帮助用户解决他们的问题。
在回答问题时，请确保你的回答是准确的、有用的、并且友好的。
如果你不确定答案，请诚实地告诉用户你不确定。
请用简洁明了的语言回答问题。
"""

# ✅ 精简的Prompt（约20 tokens）
system_good = """
你是AI助手。简洁准确地回答问题。不确定时说明。
"""
```

### 4.2 使用Few-shot代替长描述

```python
# ❌ 用文字描述格式要求
system_bad = """
请分析用户输入的文本情感。返回JSON格式，包含以下字段：
- sentiment: 情感类型，可以是positive、negative或neutral
- score: 情感分数，0到1之间的小数
- keywords: 关键词列表
"""

# ✅ 用示例展示
system_good = """
分析情感，返回JSON：
输入：今天天气真好
输出：{"sentiment":"positive","score":0.9,"keywords":["天气好"]}
"""
```

### 4.3 限制输出长度

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    max_tokens=100,  # 限制输出Token
)
```

### 4.4 使用更高效的模型

```python
# 简单任务用便宜模型
simple_response = client.chat.completions.create(
    model="deepseek-chat",  # 便宜
    messages=[{"role": "user", "content": "1+1等于多少？"}]
)

# 复杂任务用强模型
complex_response = client.chat.completions.create(
    model="deepseek-reasoner",  # 更强但更贵
    messages=[{"role": "user", "content": "解释量子纠缠原理"}]
)
```

---

## 5. 上下文窗口管理

### 5.1 问题：对话过长

```python
# 对话历史越来越长，Token越来越多
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "问题1"},
    {"role": "assistant", "content": "回答1..."},
    {"role": "user", "content": "问题2"},
    {"role": "assistant", "content": "回答2..."},
    # ... 可能有几十轮对话
]
```

### 5.2 解决方案：滑动窗口

```python
def manage_context(
    messages: list,
    max_tokens: int = 4000,
    model: str = "gpt-4"
) -> list:
    """管理上下文长度"""
    enc = tiktoken.encoding_for_model(model)
    
    # 保留system message
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    history = messages[1:] if system_msg else messages
    
    # 计算system token
    system_tokens = len(enc.encode(system_msg["content"])) if system_msg else 0
    available_tokens = max_tokens - system_tokens - 100  # 预留buffer
    
    # 从最新消息开始保留
    kept_messages = []
    current_tokens = 0
    
    for msg in reversed(history):
        msg_tokens = len(enc.encode(msg["content"]))
        if current_tokens + msg_tokens <= available_tokens:
            kept_messages.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break
    
    # 组合结果
    result = [system_msg] if system_msg else []
    result.extend(kept_messages)
    
    return result
```

### 5.3 解决方案：摘要压缩

```python
async def compress_history(messages: list) -> str:
    """将历史对话压缩成摘要"""
    history_text = "\n".join([
        f"{m['role']}: {m['content']}" 
        for m in messages
    ])
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "请用3句话总结以下对话的关键信息："},
            {"role": "user", "content": history_text}
        ],
        max_tokens=200
    )
    
    return response.choices[0].message.content
```

---

## 6. 实战练习

### 练习：Token监控仪表板

```python
# TODO: 实现一个Token使用监控类

class TokenMonitor:
    def __init__(self, daily_budget: float, model: str = "deepseek-chat"):
        self.daily_budget = daily_budget
        self.model = model
        self.today_usage = {"input": 0, "output": 0, "cost": 0}
    
    def record_usage(self, input_tokens: int, output_tokens: int):
        """记录一次API调用"""
        # TODO: 更新使用量和成本
        pass
    
    def get_remaining_budget(self) -> float:
        """获取剩余预算"""
        # TODO: 计算剩余预算
        pass
    
    def should_warn(self) -> bool:
        """是否需要发出警告（超过80%预算）"""
        # TODO: 判断是否需要警告
        pass

# 使用示例
monitor = TokenMonitor(daily_budget=10.0)  # 每天10元预算
monitor.record_usage(1000, 500)
print(f"剩余预算: {monitor.get_remaining_budget()}")
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | 大模型成本优化技巧 | https://www.bilibili.com/video/BV1hZ421m7tB |
| 跟李沐学AI | Tiktoken使用教程 | https://www.bilibili.com/video/BV1om4y1A72P |

---

## 7. 继续学习

🎉 **恭喜！你已完成Week 2所有教程！**

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解
3. ✅ Response Format深度解析
4. ✅ Function Calling详解
5. ✅ Streaming流式响应
6. ✅ Token计算与优化（本教程）

在左侧菜单选择 **Week 3** 继续学习MCP协议！

---

**控制成本是工程师的必备技能！💪**
