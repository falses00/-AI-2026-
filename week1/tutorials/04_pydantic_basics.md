# 📦 Pydantic数据验证

> **学习目标**：掌握Pydantic进行数据验证、序列化和类型安全编程

---

## 1. 为什么需要Pydantic？

### 传统数据验证的问题

在没有Pydantic之前，我们这样验证数据：

```python
def create_user(data: dict):
    """传统方式：手动验证每个字段"""
    
    # 检查必填字段
    if "username" not in data:
        raise ValueError("缺少username字段")
    if "email" not in data:
        raise ValueError("缺少email字段")
    
    # 检查类型
    if not isinstance(data["username"], str):
        raise TypeError("username必须是字符串")
    
    # 检查格式
    if "@" not in data["email"]:
        raise ValueError("email格式不正确")
    
    # 检查范围
    if "age" in data and data["age"] < 0:
        raise ValueError("age不能为负数")
    
    # ... 还有很多其他检查
    
    return data
```

**问题**：
- ❌ 代码冗长
- ❌ 容易出错
- ❌ 难以维护
- ❌ 没有类型提示

---

### Pydantic的解决方案

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    """用户模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(default=0, ge=0, le=150)
    is_active: bool = True

# 使用
try:
    user = User(
        username="alice",
        email="alice@example.com",
        age=25
    )
    print(user)
    print(user.model_dump())  # 转换为字典
except ValueError as e:
    print(f"验证错误: {e}")
```

**优势**：
- ✅ 代码简洁
- ✅ 自动验证
- ✅ 类型安全
- ✅ IDE支持

---

## 2. 基础用法

### 2.1 定义模型

```python
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    """产品模型"""
    name: str                    # 必填字段
    price: float                 # 必填字段
    description: Optional[str] = None  # 可选字段
    in_stock: bool = True        # 有默认值
    quantity: int = 0

# 创建实例
product = Product(
    name="iPhone 15",
    price=999.99
)

print(product.name)       # iPhone 15
print(product.price)      # 999.99
print(product.in_stock)   # True
```

---

### 2.2 数据验证

Pydantic会自动验证数据类型：

```python
from pydantic import BaseModel, ValidationError

class Book(BaseModel):
    title: str
    pages: int
    price: float

# ✅ 正确的数据
book1 = Book(title="Python入门", pages=300, price=59.9)

# ✅ 自动类型转换
book2 = Book(title="AI实战", pages="450", price="89.9")
print(book2.pages)  # 450 (int类型)

# ❌ 验证失败
try:
    book3 = Book(title="错误示例", pages="abc", price=29.9)
except ValidationError as e:
    print(e)
```

**输出**：
```
1 validation error for Book
pages
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='abc', input_type=str]
```

---

### 2.3 嵌套模型

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    """地址模型"""
    street: str
    city: str
    country: str = "中国"

class Company(BaseModel):
    """公司模型"""
    name: str
    address: Address                # 嵌套单个模型
    employees: List[str]            # 列表

# 创建实例
company = Company(
    name="科技公司",
    address={
        "street": "中关村大街1号",
        "city": "北京"
    },
    employees=["张三", "李四", "王五"]
)

print(company.address.city)  # 北京
print(company.employees[0])  # 张三
```

---

## 3. 高级验证

### 3.1 Field验证器

```python
from pydantic import BaseModel, Field

class Student(BaseModel):
    """学生模型"""
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=6, le=18, description="学生年龄必须在6-18岁")
    grade: float = Field(..., ge=0, le=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# ✅ 有效数据
student = Student(
    name="小明",
    age=12,
    grade=95.5,
    email="xiaoming@school.com"
)

# ❌ 无效数据
try:
    bad_student = Student(
        name="A",          # 太短
        age=20,            # 超过18岁
        grade=105,         # 超过100分
        email="invalid"    # 邮箱格式错误
    )
except ValueError as e:
    print(e)
```

**Field参数说明**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `min_length` | 最小长度 | `Field(min_length=3)` |
| `max_length` | 最大长度 | `Field(max_length=50)` |
| `ge` | 大于等于 (≥) | `Field(ge=0)` |
| `le` | 小于等于 (≤) | `Field(le=100)` |
| `gt` | 大于 (>) | `Field(gt=0)` |
| `lt` | 小于 (<) | `Field(lt=100)` |
| `pattern` | 正则表达式 | `Field(pattern=r'^\d+$')` |

---

### 3.2 自定义验证器

```python
from pydantic import BaseModel, field_validator

class UserAccount(BaseModel):
    """用户账号"""
    username: str
    password: str
    email: str
    
    @field_validator('username')
    @classmethod
    def username_must_be_lowercase(cls, v: str) -> str:
        """用户名必须小写"""
        if not v.islower():
            raise ValueError('用户名必须全部小写')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """密码强度检查"""
        if len(v) < 8:
            raise ValueError('密码至少8位')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        return v

# ✅ 有效账号
user = UserAccount(
    username="alice",
    password="Pass1234",
    email="alice@example.com"
)

# ❌ 无效账号
try:
    bad_user = UserAccount(
        username="Alice",      # 含大写字母
        password="weak",       # 密码过弱
        email="alice@example.com"
    )
except ValueError as e:
    print(e)
```

---

## 4. 数据序列化

### 4.1 转换为字典

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    content: str
    views: int = 0
    
article = Article(
    title="Pydantic教程",
    content="这是一篇教程"
)

# 转换为字典
print(article.model_dump())
# {'title': 'Pydantic教程', 'content': '这是一篇教程', 'views': 0}

# 转换为JSON字符串
print(article.model_dump_json())
# {"title":"Pydantic教程","content":"这是一篇教程","views":0}
```

---

### 4.2 从字典创建

```python
from pydantic import BaseModel

class Config(BaseModel):
    host: str
    port: int
    debug: bool

# 从字典创建
data = {
    "host": "localhost",
    "port": 8000,
    "debug": True
}

config = Config(**data)
print(config)
```

---

## 5. 实战示例：API请求验证

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True

# 模拟API处理
def create_user(request_data: dict):
    """创建用户"""
    # 验证输入
    try:
        user_input = CreateUserRequest(**request_data)
    except ValidationError as e:
        return {"error": str(e)}
    
    # 创建用户（模拟）
    user = UserResponse(
        id=1,
        username=user_input.username,
        email=user_input.email,
        full_name=user_input.full_name,
        created_at=datetime.now()
    )
    
    return user.model_dump()

# 测试
request = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123"
}

response = create_user(request)
print(response)
```

---

## 6. 实战练习

### 练习1：定义订单模型

创建一个电商订单模型：

```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    """订单项"""
    # TODO: 定义字段
    # - product_id: 产品ID (整数)
    # - product_name: 产品名称 (字符串)
    # - quantity: 数量 (整数, >=1)
    # - price: 单价 (浮点数, >0)
    pass

class Order(BaseModel):
    """订单"""
    # TODO: 定义字段
    # - order_id: 订单ID (字符串)
    # - customer_email: 客户邮箱 (EmailStr)
    # - items: 订单项列表 (List[OrderItem])
    # - total_amount: 总金额 (浮点数, >=0)
    # - created_at: 创建时间 (datetime)
    # - status: 状态 (字符串, 默认"pending")
    pass

# TODO: 创建测试数据并验证
```

<details>
<summary>点击查看答案</summary>

```python
from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int = Field(..., ge=1)
    price: float = Field(..., gt=0)

class Order(BaseModel):
    order_id: str
    customer_email: EmailStr
    items: List[OrderItem]
    total_amount: float = Field(..., ge=0)
    created_at: datetime
    status: str = "pending"

# 测试
order = Order(
    order_id="ORD-001",
    customer_email="customer@example.com",
    items=[
        OrderItem(product_id=1, product_name="手机", quantity=1, price=999.99),
        OrderItem(product_id=2, product_name="耳机", quantity=2, price=99.99)
    ],
    total_amount=1199.97,
    created_at=datetime.now()
)

print(order.model_dump_json(indent=2))
```
</details>

---

## 7. 关键要点总结

> [!IMPORTANT]
> **Pydantic核心优势：**
> 
> 1. 🎯 **自动验证**：声明式验证，无需手写if-else
> 2. 🔒 **类型安全**：完整的类型提示支持
> 3. 🔄 **数据转换**：自动类型转换（如"123" → 123）
> 4. 📦 **序列化**：轻松转换JSON/字典
> 5. 🐛 **友好错误**：清晰的验证错误信息

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 刘悦的技术博客 | Pydantic V2 完全指南 | https://www.bilibili.com/video/BV1xh411Z7nY |
| 黑马程序员 | Python类型注解与Pydantic | https://www.bilibili.com/video/BV1dv4y1F7jE |

---

## 8. 继续学习

学完Pydantic后，在左侧菜单选择下一个教程：

📌 **推荐学习顺序**：
1. ✅ 异步编程核心概念
2. ✅ Pydantic数据验证（本教程）
3. ➡️ FastAPI快速入门
4. ➡️ Docker基础入门

---

**Pydantic是FastAPI的核心依赖，掌握它至关重要！💪**

