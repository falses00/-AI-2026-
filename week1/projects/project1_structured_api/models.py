"""
项目1：图书管理API - Pydantic模型定义

运行方式：
    uvicorn main:app --reload
"""

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
