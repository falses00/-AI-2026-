# 📊 结构化输出详解 (2026更新版)

> **学习目标**：掌握最新的结构化输出技术，让AI返回可靠的JSON数据

---

## 1. 为什么需要结构化输出？

### 传统对话的问题

```python
response = chat("分析这段文本的情感：我今天很开心！")
# 输出: "这段文本表达了积极、正面的情感。作者使用了'很开心'这个词..."
```

**问题**：
- ❌ 输出是自然语言，程序难以解析
- ❌ 格式不固定，每次可能不同
- ❌ 无法直接用于后续处理

### 结构化输出的优势

```python
response = chat_structured("分析这段文本的情感：我今天很开心！")
# 输出: {"sentiment": "positive", "score": 0.95, "keywords": ["开心"]}
```

**优势**：
- ✅ 固定格式，程序可直接解析
- ✅ 类型安全，便于验证
- ✅ 可用于API响应、数据存储

---

## 2. 三种结构化输出方式

### 方式对比

| 方式 | 可靠性 | 推荐度 | 适用场景 |
|------|--------|--------|----------|
| JSON Mode | 中 | ⭐⭐ | 简单场景 |
| JSON Schema (strict) | 高 | ⭐⭐⭐⭐⭐ | **推荐！生产环境** |
| Function Calling | 高 | ⭐⭐⭐⭐ | 工具调用场景 |

---

## 3. 🆕 JSON Schema (最新推荐方式)

> [!IMPORTANT]
> **2024年8月起，OpenAI/DeepSeek支持严格JSON Schema验证！**
> 使用 `strict: true` 确保100%遵循你定义的Schema。

### 3.1 基础示例

```python
from openai import OpenAI
import json

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com/v1"  # 或 OpenAI
)

response = client.chat.completions.create(
    model="deepseek-chat",  # 或 gpt-4o-2024-08-06
    messages=[
        {"role": "system", "content": "你是一个情感分析助手。"},
        {"role": "user", "content": "分析这段文本的情感：我今天很开心！"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "sentiment_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral"],
                        "description": "情感倾向"
                    },
                    "score": {
                        "type": "number",
                        "description": "置信度分数 0-1"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "关键情感词"
                    }
                },
                "required": ["sentiment", "score", "keywords"],
                "additionalProperties": False
            },
            "strict": True  # 🔒 严格模式：确保完全遵循Schema
        }
    }
)

result = json.loads(response.choices[0].message.content)
print(result)
# {"sentiment": "positive", "score": 0.95, "keywords": ["开心"]}
```

### 3.2 复杂嵌套结构

```python
# 定义嵌套的JSON Schema
complex_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "product_extraction",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {
                    "type": "object",
                    "properties": {
                        "original": {"type": "number"},
                        "current": {"type": "number"},
                        "currency": {"type": "string"}
                    },
                    "required": ["current", "currency"],
                    "additionalProperties": False
                },
                "specifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "string"}
                        },
                        "required": ["name", "value"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["name", "price", "specifications"],
            "additionalProperties": False
        },
        "strict": True
    }
}

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "从商品描述中提取结构化信息。"},
        {"role": "user", "content": """
        【限时特惠】Apple iPhone 15 Pro Max 256GB
        原价9999元，现价8999元
        - A17 Pro芯片
        - 钛金属边框
        """}
    ],
    response_format=complex_schema
)
```

---

## 4. 结合Pydantic自动生成Schema

### 4.1 从Pydantic模型生成JSON Schema

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class SentimentAnalysis(BaseModel):
    """情感分析结果"""
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="情感倾向"
    )
    score: float = Field(ge=0, le=1, description="置信度分数")
    keywords: List[str] = Field(description="关键情感词")
    summary: Optional[str] = Field(default=None, description="一句话总结")

# 自动生成JSON Schema
schema = SentimentAnalysis.model_json_schema()
print(json.dumps(schema, indent=2, ensure_ascii=False))
```

### 4.2 封装为可复用函数

```python
from pydantic import BaseModel
from typing import TypeVar, Type
import json

T = TypeVar('T', bound=BaseModel)

def structured_output(
    client,
    model: str,
    messages: list,
    response_model: Type[T],
    strict: bool = True
) -> T:
    """
    通用结构化输出函数
    
    Args:
        client: OpenAI客户端
        model: 模型名称
        messages: 对话消息
        response_model: Pydantic模型类
        strict: 是否启用严格模式
    
    Returns:
        解析后的Pydantic对象
    """
    # 获取Schema
    schema = response_model.model_json_schema()
    
    # 移除Pydantic特有字段，保留OpenAI兼容格式
    if "title" in schema:
        del schema["title"]
    if "$defs" in schema:
        # 展开引用（简化处理）
        pass
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__.lower(),
                "schema": schema,
                "strict": strict
            }
        }
    )
    
    data = json.loads(response.choices[0].message.content)
    return response_model(**data)

# 使用示例
result = structured_output(
    client=client,
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "分析用户输入的文本情感。"},
        {"role": "user", "content": "今天天气真好，心情愉快！"}
    ],
    response_model=SentimentAnalysis
)

print(f"情感: {result.sentiment}")
print(f"分数: {result.score}")
print(f"关键词: {result.keywords}")
```

---

## 5. JSON Mode (传统方式)

适用于简单场景或不支持JSON Schema的模型：

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system", 
            "content": """你是一个数据分析助手。
请以以下JSON格式返回：
{
    "sentiment": "positive/negative/neutral",
    "score": 0.0-1.0,
    "keywords": ["关键词列表"]
}"""
        },
        {"role": "user", "content": "分析：我今天很开心！"}
    ],
    response_format={"type": "json_object"}  # 传统JSON模式
)
```

> [!WARNING]
> JSON Mode只保证返回有效JSON，不保证遵循你定义的结构！
> **生产环境推荐使用JSON Schema + strict模式。**

---

## 6. 错误处理最佳实践

```python
import json
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def safe_structured_output(
    client, model: str, messages: list, response_model
):
    """带重试的结构化输出"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__.lower(),
                    "schema": response_model.model_json_schema(),
                    "strict": True
                }
            }
        )
        
        data = json.loads(response.choices[0].message.content)
        return response_model(**data)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        raise
    except ValidationError as e:
        print(f"❌ 数据验证失败: {e}")
        raise

# 使用
try:
    result = safe_structured_output(client, "deepseek-chat", messages, SentimentAnalysis)
except Exception as e:
    print(f"最终失败: {e}")
```

---

## 7. 实战练习

### 练习1：发票信息提取

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class InvoiceItem(BaseModel):
    """发票项目"""
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    """发票信息"""
    invoice_number: str
    date: str
    vendor: str
    buyer: str
    items: List[InvoiceItem]
    subtotal: float
    tax: float
    total: float

# TODO: 实现 extract_invoice(text: str) -> Invoice
# 使用上面的structured_output函数
```

---

## 8. 关键要点

> [!IMPORTANT]
> **2026最佳实践：**
> 
> 1. 🆕 **使用JSON Schema + strict模式** - 100%可靠的结构化输出
> 2. 📋 **Pydantic自动生成Schema** - 减少手写Schema的错误
> 3. 🔒 **additionalProperties: false** - 防止模型添加额外字段
> 4. 🔄 **带重试的错误处理** - 使用tenacity库
> 5. 📚 **明确的字段描述** - 帮助模型理解每个字段的含义

---

## 继续学习

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解（本教程）
3. ➡️ Response Format深度解析
4. ➡️ Function Calling详解

---

**结构化输出是AI应用的关键技术，让AI从"聊天"变成"做事"！💪**
