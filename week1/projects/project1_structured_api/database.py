"""
项目1：图书管理API - 数据库模拟

使用内存字典模拟数据库操作
"""

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
        ),
        BookCreate(
            title="FastAPI入门与实战",
            author="张三",
            isbn="9787115500000",
            price=79.00,
            published_date=date(2024, 1, 1),
            description="FastAPI框架实战指南"
        )
    ]
    
    for book in sample_books:
        create_book(book)


# 初始化示例数据
init_sample_data()
