# 📊 结构化输出详解

> **学习目标**：掌握如何让AI返回结构化的JSON数据，实现程序可读的输出

---

## 1. 为什么需要结构化输出？

### 传统对话的问题

```python
response = chat_completion("分析这段文本的情感：我今天很开心！")
# 输出: "这段文本表达了积极、正面的情感。作者使用了'很开心'这个词..."
```

**问题**：
- ❌ 输出是自然语言，程序难以解析
- ❌ 格式不固定，每次可能不同
- ❌ 无法直接用于后续处理

### 结构化输出的优势

```python
response = chat_completion_structured("分析这段文本的情感：我今天很开心！")
# 输出: {"sentiment": "positive", "score": 0.95, "keywords": ["开心"]}
```

**优势**：
- ✅ 固定格式，程序可直接解析
- ✅ 类型安全，便于验证
- ✅ 可用于API响应、数据存储

---

## 2. JSON Mode基础

### 2.1 启用JSON模式

```python
from config.deepseek_client import get_client
import json

client = get_client()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system", 
            "content": "你是一个数据分析助手。请以JSON格式返回分析结果。"
        },
        {
            "role": "user", 
            "content": "分析这段文本的情感：我今天很开心！"
        }
    ],
    response_format={"type": "json_object"}  # 启用JSON模式
)

# 解析JSON
result = json.loads(response.choices[0].message.content)
print(result)
```

**输出**：
```json
{
    "sentiment": "positive",
    "confidence": 0.95,
    "emotion": "happiness",
    "keywords": ["开心"]
}
```

---

### 2.2 指定JSON结构

在提示词中明确期望的格式：

```python
system_prompt = """你是一个情感分析助手。请分析用户输入的文本，并以以下JSON格式返回：
{
    "text": "原始文本",
    "sentiment": "positive" 或 "negative" 或 "neutral",
    "score": 0.0-1.0之间的数值,
    "emotions": ["情感列表"],
    "summary": "一句话总结"
}
"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "虽然今天下雨了，但我还是很高兴能见到老朋友。"}
    ],
    response_format={"type": "json_object"}
)

result = json.loads(response.choices[0].message.content)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

**输出**：
```json
{
  "text": "虽然今天下雨了，但我还是很高兴能见到老朋友。",
  "sentiment": "positive",
  "score": 0.85,
  "emotions": ["happiness", "nostalgia"],
  "summary": "尽管天气不好，但见到朋友让作者感到开心"
}
```

---

## 3. 结合Pydantic验证

### 3.1 定义数据模型

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class SentimentAnalysis(BaseModel):
    """情感分析结果模型"""
    text: str = Field(..., description="原始文本")
    sentiment: Literal["positive", "negative", "neutral"]
    score: float = Field(..., ge=0, le=1)
    emotions: List[str]
    summary: str

# 验证AI返回的数据
raw_response = {
    "text": "我今天很开心",
    "sentiment": "positive",
    "score": 0.95,
    "emotions": ["happiness"],
    "summary": "表达了积极情感"
}

# Pydantic自动验证
analysis = SentimentAnalysis(**raw_response)
print(analysis.sentiment)  # positive
```

---

### 3.2 完整工作流

```python
from config.deepseek_client import get_client
from pydantic import BaseModel, Field
from typing import List, Literal
import json

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    score: float = Field(..., ge=0, le=1)
    emotions: List[str]
    summary: str

def analyze_sentiment(text: str) -> SentimentAnalysis:
    """分析文本情感，返回结构化结果"""
    client = get_client()
    
    # 构建提示词（包含JSON Schema）
    system_prompt = f"""分析用户输入的文本情感。返回JSON格式：
{json.dumps(SentimentAnalysis.model_json_schema(), indent=2)}
"""
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0  # 确保一致性
    )
    
    # 解析并验证
    data = json.loads(response.choices[0].message.content)
    return SentimentAnalysis(**data)

# 使用
result = analyze_sentiment("今天加班到很晚，真的很累。")
print(f"情感: {result.sentiment}")
print(f"分数: {result.score}")
print(f"情绪: {result.emotions}")
```

---

## 4. 实战示例：信息提取

### 从名片文本提取信息

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
import json

class ContactInfo(BaseModel):
    """名片信息模型"""
    name: str
    company: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

def extract_contact(text: str) -> ContactInfo:
    """从文本中提取联系人信息"""
    from config.deepseek_client import get_client
    client = get_client()
    
    system_prompt = f"""从用户提供的名片或联系信息文本中提取结构化数据。
返回JSON格式，字段说明：
- name: 姓名（必填）
- company: 公司名称
- title: 职位
- phone: 电话号码
- email: 电子邮箱
- address: 地址

如果某个字段无法提取，设为null。
"""
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    data = json.loads(response.choices[0].message.content)
    return ContactInfo(**data)

# 测试
card_text = """
张三
高级软件工程师
ABC科技有限公司
电话：13812345678
邮箱：zhangsan@abc.com
地址：北京市海淀区中关村大街1号
"""

contact = extract_contact(card_text)
print(f"姓名: {contact.name}")
print(f"公司: {contact.company}")
print(f"电话: {contact.phone}")
```

---

## 5. 错误处理

### 5.1 JSON解析失败

```python
import json
from pydantic import ValidationError

def safe_parse_response(raw_content: str, model_class):
    """安全解析AI响应"""
    try:
        # 尝试解析JSON
        data = json.loads(raw_content)
        # 验证数据结构
        return model_class(**data)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except ValidationError as e:
        print(f"数据验证错误: {e}")
        return None

# 使用
result = safe_parse_response(response_content, SentimentAnalysis)
if result:
    print("解析成功")
else:
    print("解析失败，需要重试")
```

### 5.2 重试机制

```python
import time

def extract_with_retry(text: str, max_retries: int = 3) -> ContactInfo:
    """带重试的信息提取"""
    for attempt in range(max_retries):
        try:
            return extract_contact(text)
        except Exception as e:
            print(f"尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待1秒后重试
    
    raise Exception("达到最大重试次数")
```

---

## 6. 实战练习

### 练习1：商品信息提取

创建一个函数，从商品描述中提取结构化信息：

```python
from pydantic import BaseModel
from typing import List, Optional

class ProductInfo(BaseModel):
    """商品信息模型"""
    name: str
    price: float
    category: str
    features: List[str]
    brand: Optional[str] = None

# TODO: 实现extract_product函数
def extract_product(description: str) -> ProductInfo:
    pass

# 测试文本
text = """
【限时特惠】Apple iPhone 15 Pro Max 256GB 原色钛金属
原价9999元，现价8999元
- A17 Pro芯片
- 钛金属边框
- 4800万像素主摄
- USB-C充电
"""

# product = extract_product(text)
# print(product.model_dump_json(indent=2))
```

---

## 7. 关键要点

> [!IMPORTANT]
> **结构化输出要点：**
> 
> 1. 📋 **明确格式**：在提示词中清楚定义期望的JSON结构
> 2. ✅ **启用JSON模式**：使用 `response_format={"type": "json_object"}`
> 3. 🔒 **Pydantic验证**：用模型类验证数据完整性
> 4. 🔄 **错误处理**：实现重试和降级机制
> 5. 🌡️ **低温度**：使用 `temperature=0` 确保输出一致

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | 大模型结构化输出实战 | https://www.bilibili.com/video/BV1dZ421m7tB |
| DataWhale | JSON Mode与结构化输出 | https://www.bilibili.com/video/BV1Sp4y1s7Pt |

---

## 8. 继续学习

学完结构化输出后，在左侧菜单选择下一个教程：

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解（本教程）
3. ➡️ Function Calling详解

---

**结构化输出是AI应用的关键技术，让AI从"聊天"变成"做事"！💪**

