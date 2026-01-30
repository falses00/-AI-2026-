r"""
图书管理系统 - 数据库层

使用SQLite数据库存储图书数据
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from models import BookCreate, BookUpdate

# 数据库文件路径（存储在data目录）
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "bookstore.db"


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 创建图书表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            published_date TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def create_book(book: BookCreate) -> dict:
    """创建图书"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO books (title, author, isbn, price, published_date, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        book.title,
        book.author,
        book.isbn,
        book.price,
        book.published_date.isoformat(),
        book.description,
        now,
        now
    ))
    
    book_id = cursor.lastrowid
    conn.commit()
    
    # 获取新创建的图书
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row)


def get_books(skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
    """获取图书列表（分页）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute("SELECT COUNT(*) FROM books")
    total = cursor.fetchone()[0]
    
    # 获取分页数据
    cursor.execute("""
        SELECT * FROM books
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, skip))
    
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return books, total


def get_book(book_id: int) -> Optional[dict]:
    """获取单本图书"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def update_book(book_id: int, book_update: BookUpdate) -> Optional[dict]:
    """更新图书"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查图书是否存在
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    # 构建更新语句
    update_fields = []
    values = []
    
    if book_update.title is not None:
        update_fields.append("title = ?")
        values.append(book_update.title)
    
    if book_update.author is not None:
        update_fields.append("author = ?")
        values.append(book_update.author)
    
    if book_update.isbn is not None:
        update_fields.append("isbn = ?")
        values.append(book_update.isbn)
    
    if book_update.price is not None:
        update_fields.append("price = ?")
        values.append(book_update.price)
    
    if book_update.published_date is not None:
        update_fields.append("published_date = ?")
        values.append(book_update.published_date.isoformat())
    
    if book_update.description is not None:
        update_fields.append("description = ?")
        values.append(book_update.description)
    
    # 更新时间
    update_fields.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    values.append(book_id)
    
    cursor.execute(f"""
        UPDATE books
        SET {", ".join(update_fields)}
        WHERE id = ?
    """, values)
    
    conn.commit()
    
    # 获取更新后的图书
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row)


def delete_book(book_id: int) -> bool:
    """删除图书"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


# 应用启动时初始化数据库
init_db()
