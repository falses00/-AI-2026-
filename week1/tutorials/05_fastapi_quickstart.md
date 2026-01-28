# ⚡ FastAPI 快速入门

> **学习目标**：10分钟搭建第一个FastAPI应用，理解核心概念

---

## 1. 什么是FastAPI？

FastAPI是一个**现代、高性能**的Python Web框架，特点：

| 特性 | 说明 |
|------|------|
| 🚀 **高性能** | 与NodeJS、Go相当 |
| 📝 **自动文档** | 内置Swagger UI |
| ✅ **类型安全** | 基于Python类型注解 |
| 🔧 **易于使用** | 极简语法 |

---

## 2. 第一个API

### 2.1 最简示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}
```

### 2.2 运行

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000 → `{"message": "Hello, World!"}`

访问 http://localhost:8000/docs → 自动生成的API文档！

---

## 3. 核心概念

### 3.1 路由装饰器

```python
@app.get("/users")      # GET请求
@app.post("/users")     # POST请求
@app.put("/users/{id}") # PUT请求
@app.delete("/users/{id}") # DELETE请求
```

### 3.2 路径参数

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

访问 `/users/123` → `{"user_id": 123}`

### 3.3 查询参数

```python
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

访问 `/items?skip=5&limit=20` → `{"skip": 5, "limit": 20}`

### 3.4 请求体（Pydantic）

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: User):
    return {"name": user.name, "age": user.age}
```

---

## 4. 实战练习

创建一个计算器API：

```python
from fastapi import FastAPI

app = FastAPI(title="计算器API")

# TODO: 实现以下端点
# GET /add?a=1&b=2 → {"result": 3}
# GET /subtract?a=5&b=3 → {"result": 2}
# GET /multiply?a=4&b=5 → {"result": 20}
```

<details>
<summary>查看答案</summary>

```python
@app.get("/add")
def add(a: float, b: float):
    return {"result": a + b}

@app.get("/subtract")
def subtract(a: float, b: float):
    return {"result": a - b}

@app.get("/multiply")
def multiply(a: float, b: float):
    return {"result": a * b}
```

</details>

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 李辉Python | FastAPI从入门到精通 | https://www.bilibili.com/video/BV1R14y1Y7G8 |
| 编程浪子 | FastAPI零基础教程 | https://www.bilibili.com/video/BV1Zu4y1f72U |

---

## 5. 继续学习

学完FastAPI后，在左侧菜单选择下一个教程：

📌 **推荐学习顺序**：
1. ✅ 异步编程核心概念
2. ✅ Pydantic数据验证
3. ✅ FastAPI快速入门（本教程）
4. ➡️ Docker基础入门

---

**FastAPI = Python + 类型注解 + 自动文档，就是这么简单！💪**

