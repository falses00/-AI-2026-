r"""
项目1：图书管理API - 主应用

运行方式：
    cd i:\Study FastAPI\week1\projects\project1_structured_api
    python -m uvicorn main:app --reload

访问文档：
    http://localhost:8000/docs
    http://localhost:8000  (前端界面)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
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
* SQLite
* Python 3.12
    """,
    version="1.0.0",
    contact={
        "name": "AI工程师训练营",
        "email": "study@example.com"
    }
)


@app.get("/", response_class=HTMLResponse, tags=["前端"])
def read_root():
    """
    前端页面
    
    返回图书管理系统的前端界面
    """
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 图书管理系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .book-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .book-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .book-card p {
            margin: 5px 0;
            color: #666;
        }
        .book-card .price {
            color: #e74c3c;
            font-size: 1.3em;
            font-weight: bold;
            margin: 10px 0;
        }
        .book-card .actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        .btn-small {
            padding: 8px 15px;
            font-size: 14px;
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .status-message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 图书管理系统</h1>
            <p>FastAPI + SQLite 示例项目</p>
            <p><a href="/docs" style="color: white; text-decoration: none;">📖 查看API文档</a></p>
        </div>
        
        <div id="statusMessage" class="status-message"></div>
        
        <!-- 添加图书表单 -->
        <div class="card">
            <h2>➕ 添加新图书</h2>
            <form id="addBookForm">
                <div class="form-group">
                    <label>书名</label>
                    <input type="text" id="title" required>
                </div>
                <div class="form-group">
                    <label>作者</label>
                    <input type="text" id="author" required>
                </div>
                <div class="form-group">
                    <label>ISBN</label>
                    <input type="text" id="isbn" pattern="\\d{13}" required placeholder="13位数字">
                </div>
                <div class="form-group">
                    <label>价格（元）</label>
                    <input type="number" id="price" step="0.01" min="0" required>
                </div>
                <div class="form-group">
                    <label>出版日期</label>
                    <input type="date" id="published_date" required>
                </div>
                <div class="form-group">
                    <label>描述（可选）</label>
                    <textarea id="description" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">添加图书</button>
            </form>
        </div>
        
        <!-- 图书列表 -->
        <div class="card">
            <h2>📖 图书列表</h2>
            <div id="booksList" class="books-grid"></div>
            <div id="pagination" class="pagination"></div>
        </div>
    </div>
    
    <script>
        let currentPage = 1;
        const pageSize = 6;
        
        // 加载图书列表
        async function loadBooks(page = 1) {
            try {
                const response = await fetch(`/books/?page=${page}&page_size=${pageSize}`);
                const data = await response.json();
                
                const booksList = document.getElementById('booksList');
                booksList.innerHTML = '';
                
                if (data.books.length === 0) {
                    booksList.innerHTML = '<p style="text-align: center; color: #999;">暂无图书数据</p>';
                    return;
                }
                
                data.books.forEach(book => {
                    const bookCard = document.createElement('div');
                    bookCard.className = 'book-card';
                    bookCard.innerHTML = `
                        <h3>${book.title}</h3>
                        <p><strong>作者：</strong>${book.author}</p>
                        <p><strong>ISBN：</strong>${book.isbn}</p>
                        <p class="price">¥${book.price}</p>
                        <p><strong>出版日期：</strong>${book.published_date}</p>
                        ${book.description ? `<p>${book.description}</p>` : ''}
                        <div class="actions">
                            <button class="btn btn-small btn-danger" onclick="deleteBook(${book.id})">删除</button>
                        </div>
                    `;
                    booksList.appendChild(bookCard);
                });
                
                // 分页
                renderPagination(data.page, Math.ceil(data.total / pageSize));
            } catch (error) {
                showMessage('加载图书失败', 'error');
            }
        }
        
        // 渲染分页
        function renderPagination(currentPage, totalPages) {
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';
            
            if (totalPages <= 1) return;
            
            for (let i = 1; i <= totalPages; i++) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-small';
                btn.style.background = i === currentPage ? '#667eea' : '#e0e0e0';
                btn.style.color = i === currentPage ? 'white' : '#333';
                btn.textContent = i;
                btn.onclick = () => loadBooks(i);
                pagination.appendChild(btn);
            }
        }
        
        // 添加图书
        document.getElementById('addBookForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const bookData = {
                title: document.getElementById('title').value,
                author: document.getElementById('author').value,
                isbn: document.getElementById('isbn').value,
                price: parseFloat(document.getElementById('price').value),
                published_date: document.getElementById('published_date').value,
                description: document.getElementById('description').value || null
            };
            
            try {
                const response = await fetch('/books/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bookData)
                });
                
                if (response.ok) {
                    showMessage('图书添加成功！', 'success');
                    document.getElementById('addBookForm').reset();
                    loadBooks(1);
                } else {
                    const error = await response.json();
                    showMessage('添加失败：' + error.detail, 'error');
                }
            } catch (error) {
                showMessage('添加失败，请重试', 'error');
            }
        });
        
        // 删除图书
        async function deleteBook(id) {
            if (!confirm('确定要删除这本书吗？')) return;
            
            try {
                const response = await fetch(`/books/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    showMessage('删除成功！', 'success');
                    loadBooks(currentPage);
                } else {
                    showMessage('删除失败', 'error');
                }
            } catch (error) {
                showMessage('删除失败，请重试', 'error');
            }
        }
        
        // 显示消息
        function showMessage(message, type) {
            const msgDiv = document.getElementById('statusMessage');
            msgDiv.textContent = message;
            msgDiv.className = `status-message status-${type}`;
            msgDiv.style.display = 'block';
            setTimeout(() => {
                msgDiv.style.display = 'none';
            }, 3000);
        }
        
        // 页面加载时获取图书列表
        loadBooks(1);
    </script>
</body>
</html>
    """


@app.get("/api", response_model=MessageResponse, tags=["根路径"])
def api_root():
    """
    API根路径
    
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
