"""
项目1：图书管理API - 主应用

运行方式：
    cd i:\Study FastAPI\week1\projects\project1_structured_api
    D:\Anaconda\envs\pytorch_Gpu\python.exe -m uvicorn main:app --reload

访问文档：
    http://localhost:8000/docs
"""

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
    title="📚 图书管理API",
    description="""
一个简单的图书管理系统API，用于学习FastAPI和Pydantic。

## 功能介绍

* **创建图书** - 添加新书到系统
* **获取图书列表** - 分页查询所有图书
* **获取图书详情** - 根据ID查询单本图书
* **更新图书** - 修改图书信息
* **删除图书** - 从系统中移除图书

## 技术栈

* FastAPI
* Pydantic
* Python 3.12
    """,
    version="1.0.0",
    contact={
        "name": "AI工程师训练营",
        "email": "study@example.com"
    }
)


@app.get("/", response_model=MessageResponse, tags=["根路径"])
def root():
    """
    欢迎页面
    
    返回API欢迎信息
    """
    return {"message": "欢迎使用图书管理API！访问 /docs 查看交互式文档"}


@app.post("/books/", response_model=BookResponse, status_code=201, tags=["图书管理"])
def create_book(book: BookCreate):
    """
    创建新图书
    
    添加一本新书到系统中。
    
    - **title**: 书名（必填，1-200字符）
    - **author**: 作者（必填，1-100字符）
    - **isbn**: ISBN号（必填，13位数字）
    - **price**: 价格（必填，必须大于0）
    - **published_date**: 出版日期（必填，格式：YYYY-MM-DD）
    - **description**: 描述（可选，最多1000字符）
    """
    new_book = db.create_book(book)
    return BookResponse(**new_book)


@app.get("/books/", response_model=BookListResponse, tags=["图书管理"])
def get_books(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量，最多100")
):
    """
    获取图书列表（分页）
    
    返回图书列表，支持分页查询。
    
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


@app.get("/books/{book_id}", response_model=BookResponse, tags=["图书管理"])
def get_book(book_id: int):
    """
    获取单本图书详情
    
    根据图书ID获取详细信息。
    
    - **book_id**: 图书ID（路径参数）
    
    如果图书不存在，返回404错误。
    """
    book = db.get_book(book_id)
    if book is None:
        raise HTTPException(
            status_code=404, 
            detail=f"图书ID {book_id} 不存在"
        )
    return BookResponse(**book)


@app.put("/books/{book_id}", response_model=BookResponse, tags=["图书管理"])
def update_book(book_id: int, book_update: BookUpdate):
    """
    更新图书信息
    
    更新指定图书的信息，只需提供需要更新的字段。
    
    - **book_id**: 图书ID（路径参数）
    - 其他字段：要更新的字段（只需提供需要更新的字段）
    
    如果图书不存在，返回404错误。
    """
    updated_book = db.update_book(book_id, book_update)
    if updated_book is None:
        raise HTTPException(
            status_code=404, 
            detail=f"图书ID {book_id} 不存在"
        )
    return BookResponse(**updated_book)


@app.delete("/books/{book_id}", response_model=MessageResponse, tags=["图书管理"])
def delete_book(book_id: int):
    """
    删除图书
    
    从系统中删除指定的图书。
    
    - **book_id**: 图书ID（路径参数）
    
    如果图书不存在，返回404错误。
    """
    success = db.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"图书ID {book_id} 不存在"
        )
    return {"message": f"图书ID {book_id} 已成功删除"}


# 开发时直接运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
