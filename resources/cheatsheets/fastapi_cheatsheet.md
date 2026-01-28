# FastAPI 速查表

## 基础应用

### 创建应用
```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0")
```

### 启动应用
```bash
uvicorn main:app --reload
```

---

## 路由定义

### GET请求
```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

### POST请求
```python
@app.post("/items/")
def create_item(item: Item):
    return item
```

### PUT/DELETE
```python
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": "删除成功"}
```

---

## 参数类型

### 路径参数
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

### 查询参数
```python
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### 请求体
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item):
    return item
```

---

## Pydantic模型

### 基础模型
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: str
    age: int = Field(..., ge=0, le=150)
```

### 嵌套模型
```python
class Address(BaseModel):
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address
```

### 响应模型
```python
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    return created_user
```

---

## 验证与错误

### Query参数验证
```python
from fastapi import Query

@app.get("/items/")
def read_items(
    q: str = Query(None, min_length=3, max_length=50)
):
    return {"q": q}
```

### 抛出HTTP错误
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not found:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    return item
```

---

## 依赖注入

### 简单依赖
```python
from fastapi import Depends

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def read_users(db = Depends(get_db)):
    return db.get_users()
```

---

## 异步路由

### async/await
```python
@app.get("/async-data/")
async def get_async_data():
    data = await fetch_data_async()
    return data
```

---

## 文档

### 访问文档
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 添加描述
```python
@app.get("/items/", summary="获取商品列表")
def read_items():
    """
    获取所有商品：
    - **skip**: 跳过数量
    - **limit**: 限制数量
    """
    return items
```

---

## 状态码

```python
from fastapi import status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item
```

常用状态码：
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 中间件

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

**访问完整文档：https://fastapi.tiangolo.com/**
