# 📋 Response Format 深度解析

> **学习目标**：掌握AI结构化输出的各种方式，深度集成Pydantic实现类型安全

---

## 1. 结构化输出的三种方式

### 方式对比

| 方式 | 适用场景 | 可靠性 | 复杂度 |
|------|----------|--------|--------|
| **Prompt约束** | 简单场景 | ⭐⭐ | 低 |
| **JSON Mode** | 需要JSON格式 | ⭐⭐⭐ | 中 |
| **Function Calling** | 需要调用函数 | ⭐⭐⭐⭐ | 高 |

---

## 2. Prompt约束（最简单）

直接在Prompt中要求输出格式：

```python
from config.deepseek_client import get_client
import json

client = get_client()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": """你是一个数据提取助手。
请从用户输入中提取信息，并以JSON格式返回：
{
    "name": "姓名",
    "age": 年龄数字,
    "email": "邮箱地址"
}
只返回JSON，不要其他内容。"""
        },
        {"role": "user", "content": "我是张三，今年25岁，邮箱是zhangsan@example.com"}
    ]
)

# 解析JSON（可能需要额外处理）
content = response.choices[0].message.content
# 去除可能的markdown标记
if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
        content = content[4:]

result = json.loads(content.strip())
print(result)
```

**问题**：AI可能返回额外文字或格式不规范

---

## 3. JSON Mode（推荐）

使用`response_format`参数强制JSON输出：

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": """提取用户信息，返回JSON格式：
{"name": "姓名", "age": 年龄, "email": "邮箱"}"""
        },
        {"role": "user", "content": "我是张三，25岁，zhangsan@example.com"}
    ],
    response_format={"type": "json_object"}  # 关键！
)

result = json.loads(response.choices[0].message.content)
print(result)  # 保证是有效JSON
```

**优势**：
- ✅ 保证返回有效JSON
- ✅ 不会有额外文字
- ✅ API层面的格式保证

---

## 4. 深度Pydantic集成

### 4.1 定义模型

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

class PersonInfo(BaseModel):
    """人员信息模型"""
    name: str = Field(..., description="姓名", min_length=1)
    age: int = Field(..., ge=0, le=150, description="年龄")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, description="电话号码")
    skills: List[str] = Field(default_factory=list, description="技能列表")
```

### 4.2 将模型转为JSON Schema

```python
import json

# 获取JSON Schema
schema = PersonInfo.model_json_schema()
print(json.dumps(schema, indent=2, ensure_ascii=False))
```

**输出**：
```json
{
  "title": "PersonInfo",
  "type": "object",
  "properties": {
    "name": {"type": "string", "minLength": 1, "description": "姓名"},
    "age": {"type": "integer", "minimum": 0, "maximum": 150, "description": "年龄"},
    "email": {"type": "string", "format": "email", "description": "邮箱地址"},
    "phone": {"type": "string", "description": "电话号码"},
    "skills": {"type": "array", "items": {"type": "string"}, "description": "技能列表"}
  },
  "required": ["name", "age", "email"]
}
```

### 4.3 完整工作流

```python
from config.deepseek_client import get_client
from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import Optional, List
import json

class PersonInfo(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=150)
    email: EmailStr
    phone: Optional[str] = None
    skills: List[str] = []

def extract_person_info(text: str) -> PersonInfo:
    """从文本中提取人员信息"""
    client = get_client()
    
    # 构建包含Schema的提示词
    schema = PersonInfo.model_json_schema()
    system_prompt = f"""从用户输入中提取人员信息。
返回JSON格式，必须符合以下Schema：
{json.dumps(schema, ensure_ascii=False, indent=2)}

只返回JSON对象，不要其他内容。"""
    
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
    return PersonInfo(**data)

# 使用
text = """
我叫李明，今年30岁，邮箱liming@tech.com，
电话13812345678，擅长Python和机器学习。
"""

try:
    person = extract_person_info(text)
    print(f"姓名: {person.name}")
    print(f"年龄: {person.age}")
    print(f"技能: {person.skills}")
except ValidationError as e:
    print(f"验证失败: {e}")
```

---

## 5. 错误处理最佳实践

### 5.1 解析失败处理

```python
import json
from pydantic import ValidationError

def safe_extract(text: str) -> Optional[PersonInfo]:
    """安全的信息提取"""
    try:
        # API调用
        response = client.chat.completions.create(...)
        content = response.choices[0].message.content
        
        # JSON解析
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始内容: {content}")
            return None
        
        # Pydantic验证
        try:
            return PersonInfo(**data)
        except ValidationError as e:
            print(f"数据验证失败: {e}")
            return None
            
    except Exception as e:
        print(f"API调用失败: {e}")
        return None
```

### 5.2 重试机制

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def extract_with_retry(text: str) -> PersonInfo:
    """带重试的信息提取"""
    return extract_person_info(text)

# 使用
try:
    result = extract_with_retry(text)
except Exception as e:
    print(f"重试3次后仍然失败: {e}")
```

---

## 6. 实战练习

### 练习：发票信息提取

```python
from pydantic import BaseModel, Field
from typing import List
from datetime import date

class InvoiceItem(BaseModel):
    """发票项目"""
    name: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    """发票模型"""
    invoice_no: str = Field(..., description="发票号码")
    date: str = Field(..., description="开票日期")
    seller: str = Field(..., description="销售方名称")
    buyer: str = Field(..., description="购买方名称")
    items: List[InvoiceItem]
    subtotal: float
    tax: float
    total: float

# TODO: 实现 extract_invoice 函数
def extract_invoice(invoice_text: str) -> Invoice:
    pass

# 测试文本
invoice_text = """
发票号码：No.2024010001
开票日期：2024年1月15日
销售方：ABC科技有限公司
购买方：XYZ集团

商品明细：
1. 笔记本电脑 x2 单价5000元 小计10000元
2. 显示器 x3 单价1500元 小计4500元

小计：14500元
税额：1885元
合计：16385元
"""
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | 结构化输出实战 | https://www.bilibili.com/video/BV1dZ421m7tB |
| DataWhale | JSON Mode详解 | https://www.bilibili.com/video/BV1Sp4y1s7Pt |

---

## 7. 继续学习

学完Response Format后，在左侧菜单选择下一个教程：

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解
3. ✅ Response Format深度解析（本教程）
4. ➡️ Function Calling详解
5. ➡️ Streaming流式响应
6. ➡️ Token计算与优化

---

**掌握Response Format，让AI输出可控可靠！💪**
