# 🔌 DeepSeek API 快速入门

> **学习目标**：掌握DeepSeek API的基本用法，包括环境配置、基本调用和参数控制

---

## 1. DeepSeek API简介

### 为什么选择DeepSeek？

DeepSeek是国产大模型的领军者，具有以下优势：

| 对比项 | DeepSeek | OpenAI GPT-4 |
|--------|----------|--------------|
| 中文能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 推理能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| API格式 | 兼容OpenAI | 原生 |
| 成本 | 低 (~1/10) | 高 |
| 访问限制 | 无 | 需科学上网 |

> [!TIP]
> DeepSeek API **完全兼容** OpenAI格式，只需更改 `base_url` 即可使用相同代码！

---

## 2. 环境配置

### 2.1 安装依赖

```bash
pip install openai python-dotenv
```

### 2.2 配置API密钥

创建 `.env` 文件（已为您创建）：

```env
DEEPSEEK_API_KEY=你的API密钥（从.env文件读取）
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

> [!CAUTION]
> **永远不要将API密钥提交到Git！** `.gitignore` 已配置忽略 `.env` 文件。

---

## 3. 基本调用

### 3.1 最简单的调用

```python
from openai import OpenAI

# 创建客户端（使用DeepSeek配置）
client = OpenAI(
    api_key="你的API密钥",  # 从.env文件获取，不要硬编码！
    base_url="https://api.deepseek.com"
)

# 发送请求
response = client.chat.completions.create(
    model="deepseek-chat",  # DeepSeek模型
    messages=[
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "你好！请介绍一下自己。"}
    ]
)

# 获取响应
print(response.choices[0].message.content)
```

**输出示例**：
```
你好！我是DeepSeek，一个AI助手，很高兴为你提供帮助！😊
```

---

### 3.2 使用项目配置（推荐）

我们已经为您创建了配置文件，只需简单导入：

```python
from config.deepseek_client import chat_completion

# 一行代码调用
response = chat_completion("请用Python写一个Hello World程序")
print(response)
```

---

## 4. 核心参数详解

### 4.1 模型选择

```python
# 通用对话模型
model="deepseek-chat"

# 推理增强模型（适合复杂推理任务）
model="deepseek-reasoner"
```

### 4.2 温度控制（Temperature）

控制输出的随机性：

```python
# 确定性输出（适合代码、事实）
temperature=0

# 平衡模式（推荐）
temperature=0.7

# 高创意输出（适合故事、创意）
temperature=1.5
```

**示例**：

```python
from config.deepseek_client import get_client

client = get_client()

# 温度=0：每次输出相同
response1 = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "1+1等于几？"}],
    temperature=0
)

# 温度=1.5：每次输出不同
response2 = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "写一个关于AI的短诗"}],
    temperature=1.5
)
```

### 4.3 最大Token数

```python
# 限制输出长度
max_tokens=500  # 约250-400个中文字
```

### 4.4 系统提示词（System Prompt）

定义AI的角色和行为：

```python
messages=[
    {"role": "system", "content": "你是一个专业的Python教师，用简洁易懂的语言解释技术概念。"},
    {"role": "user", "content": "什么是装饰器？"}
]
```

---

## 5. 多轮对话

AI可以记住上下文：

```python
from config.deepseek_client import get_client

client = get_client()

# 保存对话历史
messages = [
    {"role": "system", "content": "你是一个友好的聊天助手"}
]

def chat(user_message):
    # 添加用户消息
    messages.append({"role": "user", "content": user_message})
    
    # 调用API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    # 提取助手回复
    assistant_message = response.choices[0].message.content
    
    # 保存到历史
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

# 多轮对话示例
print(chat("我叫张三"))
# 输出: 你好张三！很高兴认识你。

print(chat("我叫什么名字？"))
# 输出: 你叫张三呀！
```

---

## 6. 实战练习

### 练习1：基础调用

编写代码，让AI用英文回答中文问题：

```python
# TODO: 完成以下代码
from config.deepseek_client import get_client

client = get_client()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        # TODO: 设置系统提示词，要求AI用英文回答
        # TODO: 用户问题："Python是什么？"
    ]
)

print(response.choices[0].message.content)
```

<details>
<summary>点击查看答案</summary>

```python
from config.deepseek_client import get_client

client = get_client()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Please answer all questions in English."},
        {"role": "user", "content": "Python是什么？"}
    ]
)

print(response.choices[0].message.content)
```

</details>

---

### 练习2：创建问答机器人

创建一个专业领域的问答机器人：

```python
# TODO: 创建一个"Python教师机器人"
# 要求:
# 1. 设置系统提示词定义角色
# 2. 支持多轮对话
# 3. 使用较低温度（0.3）确保回答准确

# 你的代码：
```

---

## 7. 关键要点

> [!IMPORTANT]
> **记住这些要点：**
> 
> 1. 🔑 **API密钥安全**：永远不要硬编码或提交密钥
> 2. 🌡️ **温度控制**：事实类用低温度，创意类用高温度
> 3. 💬 **多轮对话**：需要手动维护消息历史
> 4. 💰 **成本控制**：使用 `max_tokens` 限制输出

---

## 8. 下一步

掌握基础调用后，继续学习：

👉 [结构化输出详解](./02_structured_output.md)

---

**API调用是AI应用的核心技能，多练习！💪**
