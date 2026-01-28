# 项目1：FastAPI结构化输出服务

> **项目目标**：构建一个完整的FastAPI服务，实现数据验证、结构化输出和自动文档生成

---

## 📋 项目概述

你将构建一个**图书管理API**，支持：
- ✅ 添加图书
- ✅ 查询图书列表
- ✅ 获取单本图书详情
- ✅ 更新图书信息
- ✅ 删除图书

**技术要点**：
- Pydantic模型定义
- FastAPI路由设计
- 数据验证
- 错误处理
- 自动文档

**预计时间**：4-6小时

---

## 🎯 项目要求

### 功能要求

1. **添加图书（POST /books/）**
   - 输入：书名、作者、ISBN、价格、出版日期
   - 验证：所有字段必填，价格>0，ISBN格式正确
   - 输出：创建的图书信息（包含自动生成的ID）

2. **获取图书列表（GET /books/）**
   - 支持分页（page、page_size参数）
   - 返回图书列表和总数

3. **获取图书详情（GET /books/{book_id}）**
   - 输入：图书ID
   - 输出：图书完整信息
   - 错误处理：图书不存在返回404

4. **更新图书（PUT /books/{book_id}）**
   - 输入：图书ID + 更新字段
   - 输出：更新后的图书信息

5. **删除图书（DELETE /books/{book_id}）**
   - 输入：图书ID
   - 输出：删除成功消息

---

## 📁 项目结构

```
project1_structured_api/
├── main.py              # 主应用文件
├── models.py            # Pydantic模型
├── database.py          # 模拟数据库
├── requirements.txt     # 依赖列表
└── README.md           # 项目说明
```

---

## 💻 实现步骤

### Step 1: 创建项目目录

```bash
cd i:\Study FastAPI\week1\projects
mkdir project1_structured_api
cd project1_structured_api
```

---

### Step 2: 定义Pydantic模型（models.py）

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class BookBase(BaseModel):
    """图书基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="书名")
    author: str = Field(..., min_length=1, max_length=100, description="作者")
    isbn: str = Field(..., pattern=r'^\d{13}$', description="ISBN（13位数字）")
    price: float = Field(..., gt=0, description="价格（必须大于0）")
    published_date: date = Field(..., description="出版日期")
    description: Optional[str] = Field(None, max_length=1000, description="图书描述")

class BookCreate(BookBase):
    """创建图书请求模型"""
    pass

class BookUpdate(BaseModel):
    """更新图书请求模型（所有字段可选）"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, pattern=r'^\d{13}$')
    price: Optional[float] = Field(None, gt=0)
    published_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)

class BookResponse(BookBase):
    """图书响应模型"""
    id: int = Field(..., description="图书ID")
    
    class Config:
        from_attributes = True

class BookListResponse(BaseModel):
    """图书列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    books: list[BookResponse] = Field(..., description="图书列表")

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
```

---

### Step 3: 模拟数据库（database.py）

```python
from typing import Dict, Optional
from models import BookCreate, BookUpdate
from datetime import date

# 模拟数据库（使用内存字典）
books_db: Dict[int, dict] = {}
next_id = 1

def create_book(book: BookCreate) -> dict:
    """创建图书"""
    global next_id
    book_dict = book.model_dump()
    book_dict["id"] = next_id
    books_db[next_id] = book_dict
    next_id += 1
    return book_dict

def get_book(book_id: int) -> Optional[dict]:
    """获取图书"""
    return books_db.get(book_id)

def get_books(skip: int = 0, limit: int = 10) -> tuple[list[dict], int]:
    """获取图书列表"""
    all_books = list(books_db.values())
    total = len(all_books)
    books = all_books[skip:skip + limit]
    return books, total

def update_book(book_id: int, book_update: BookUpdate) -> Optional[dict]:
    """更新图书"""
    if book_id not in books_db:
        return None
    
    # 只更新提供的字段
    update_data = book_update.model_dump(exclude_unset=True)
    books_db[book_id].update(update_data)
    return books_db[book_id]

def delete_book(book_id: int) -> bool:
    """删除图书"""
    if book_id in books_db:
        del books_db[book_id]
        return True
    return False

# 初始化一些测试数据
def init_sample_data():
    """初始化示例数据"""
    sample_books = [
        BookCreate(
            title="Python编程：从入门到实践",
            author="埃里克·马瑟斯",
            isbn="9787115428028",
            price=89.00,
            published_date=date(2016, 7, 1),
            description="一本针对初学者的Python编程书"
        ),
        BookCreate(
            title="深度学习",
            author="伊恩·古德费洛",
            isbn="9787115461476",
            price=168.00,
            published_date=date(2017, 8, 1),
            description="深度学习领域的经典教材"
        )
    ]
    
    for book in sample_books:
        create_book(book)

init_sample_data()
```

---

### Step 4: 创建FastAPI应用（main.py）

```python
from fastapi import FastAPI, HTTPException, Query
from models import (
    BookCreate, 
    BookUpdate, 
    BookResponse, 
    BookListResponse,
    MessageResponse
)
import database as db

# 创建FastAPI应用
app = FastAPI(
    title="图书管理API",
    description="一个简单的图书管理系统API",
    version="1.0.0"
)

@app.get("/", response_model=MessageResponse)
def root():
    """根路径"""
    return {"message": "欢迎使用图书管理API！访问 /docs 查看文档"}

@app.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    """
    创建新图书
    
    - **title**: 书名（必填，1-200字符）
    - **author**: 作者（必填，1-100字符）
    - **isbn**: ISBN号（必填，13位数字）
    - **price**: 价格（必填，必须大于0）
    - **published_date**: 出版日期（必填）
    - **description**: 描述（可选，最多1000字符）
    """
    new_book = db.create_book(book)
    return BookResponse(**new_book)

@app.get("/books/", response_model=BookListResponse)
def get_books(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """
    获取图书列表（分页）
    
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10，最大100）
    """
    skip = (page - 1) * page_size
    books, total = db.get_books(skip=skip, limit=page_size)
    
    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        books=[BookResponse(**book) for book in books]
    )

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """
    获取单本图书详情
    
    - **book_id**: 图书ID
    """
    book = db.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"图书ID {book_id} 不存在")
    return BookResponse(**book)

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate):
    """
    更新图书信息
    
    - **book_id**: 图书ID
    - 其他字段：要更新的字段（只需提供需要更新的字段）
    """
    updated_book = db.update_book(book_id, book_update)
    if updated_book is None:
        raise HTTPException(status_code=404, detail=f"图书ID {book_id} 不存在")
    return BookResponse(**updated_book)

@app.delete("/books/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int):
    """
    删除图书
    
    - **book_id**: 图书ID
    """
    success = db.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"图书ID {book_id} 不存在")
    return {"message": f"图书ID {book_id} 已成功删除"}

# 运行方式：uvicorn main:app --reload
```

---

### Step 5: 创建依赖文件（requirements.txt）

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
```

---

## 🚀 运行项目

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn main:app --reload
```

### 3. 测试API

打开浏览器访问：
- **交互式文档**：http://localhost:8000/docs
- **ReDoc文档**：http://localhost:8000/redoc

---

## ✅ 测试清单

使用Swagger UI测试以下场景：

### 1. 创建图书
- [ ] 提交所有必填字段 → 成功（201）
- [ ] 缺少必填字段 → 失败（422）
- [ ] ISBN格式错误 → 失败（422）
- [ ] 价格为负数 → 失败（422）

### 2. 获取图书列表
- [ ] 默认参数 → 返回第1页
- [ ] 指定page=2 → 返回第2页
- [ ] page_size=5 → 每页5条

### 3. 获取图书详情
- [ ] 存在的ID → 返回详情
- [ ] 不存在的ID → 404错误

### 4. 更新图书
- [ ] 更新单个字段 → 成功
- [ ] 更新多个字段 → 成功
- [ ] 不存在的ID → 404错误

### 5. 删除图书
- [ ] 删除存在的图书 → 成功
- [ ] 删除不存在的图书 → 404错误

---

## 🎓 学习总结

完成本项目后，你应该掌握：

- ✅ 使用Pydantic定义数据模型
- ✅ FastAPI路由装饰器（@app.get、@app.post等）
- ✅ 路径参数和查询参数
- ✅ 请求体验证
- ✅ 响应模型和状态码
- ✅ 错误处理（HTTPException）
- ✅ 自动文档生成

---

## 🎯 挑战任务（可选）

想要更进一步？尝试：

1. **搜索功能**：添加按书名或作者搜索的API
2. **排序功能**：支持按价格、出版日期排序
3. **批量删除**：支持一次删除多本图书
4. **统计接口**：返回图书总数、平均价格等

---

## 📝 提交清单

项目完成后，确保：

- [ ] 所有API都能正常工作
- [ ] Swagger文档清晰完整
- [ ] 代码有适当注释
- [ ] 错误处理完善
- [ ] 完成所有测试场景

---

**恭喜完成项目1！继续下一个项目：Docker部署实战 🎉**
