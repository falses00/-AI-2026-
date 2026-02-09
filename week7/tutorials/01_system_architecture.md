# 📘 企业级系统架构设计

> **学习目标**：掌握企业级RAG应用的系统架构设计

---

## 🎯 本教程目标

完成本教程后，你将能够：

- ✅ 设计可扩展的系统架构
- ✅ 选择合适的技术栈组合
- ✅ 实现模块化的代码结构
- ✅ 处理高并发场景

---

## 📚 核心概念

### 1. 架构设计原则

```
┌─────────────────────────────────────────────────────────────────┐
│                    企业级系统架构层次                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  表现层 (Presentation Layer)                                     │
│  ├── Web UI / Mobile App / API                                  │
│  └── 负责用户交互和数据展示                                       │
│                                                                  │
│  应用层 (Application Layer)                                      │
│  ├── FastAPI 路由和控制器                                        │
│  ├── 业务逻辑编排                                                │
│  └── 认证授权中间件                                              │
│                                                                  │
│  领域层 (Domain Layer)                                           │
│  ├── RAG Pipeline                                                │
│  ├── Agent 系统                                                  │
│  └── 核心业务逻辑                                                │
│                                                                  │
│  基础设施层 (Infrastructure Layer)                               │
│  ├── 数据库 (PostgreSQL/SQLite)                                 │
│  ├── 向量库 (ChromaDB/Milvus)                                   │
│  ├── 缓存 (Redis)                                               │
│  └── 消息队列 (RabbitMQ/Celery)                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 技术栈选型

| 组件 | 开发环境 | 生产环境 |
|------|---------|---------|
| Web框架 | FastAPI | FastAPI + Gunicorn |
| 数据库 | SQLite | PostgreSQL |
| 向量库 | ChromaDB | Milvus / Qdrant |
| 缓存 | 内存字典 | Redis |
| 任务队列 | 同步执行 | Celery + Redis |

---

## 💻 项目结构设计

```
enterprise_rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── api/                  # API路由
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证接口
│   │   ├── documents.py     # 文档管理
│   │   ├── chat.py          # 对话接口
│   │   └── admin.py         # 管理接口
│   ├── core/                 # 核心业务
│   │   ├── __init__.py
│   │   ├── rag.py           # RAG引擎
│   │   ├── embeddings.py    # Embedding服务
│   │   └── llm.py           # LLM客户端
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── document.py
│   ├── services/             # 业务服务
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── document_service.py
│   └── utils/                # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                    # 测试
├── migrations/               # 数据库迁移
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🔧 核心代码示例

### 1. 应用配置

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    # 应用设置
    app_name: str = "Enterprise RAG"
    debug: bool = False
    
    # 数据库
    database_url: str = "sqlite:///./app.db"
    
    # 向量库
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # LLM
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2. 依赖注入

```python
# app/dependencies.py
from functools import lru_cache
from app.core.rag import RAGEngine
from app.core.llm import LLMClient

@lru_cache()
def get_llm_client():
    settings = get_settings()
    return LLMClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url
    )

@lru_cache()
def get_rag_engine():
    llm = get_llm_client()
    return RAGEngine(llm_client=llm)
```

### 3. RAG引擎封装

```python
# app/core/rag.py
from typing import Optional
import chromadb

class RAGEngine:
    """企业级RAG引擎"""
    
    def __init__(self, llm_client, collection_name: str = "documents"):
        self.llm = llm_client
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
    
    async def add_documents(self, documents: list[str], metadatas: list[dict]):
        """添加文档到知识库"""
        ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return len(documents)
    
    async def query(self, question: str, top_k: int = 5) -> str:
        """RAG问答"""
        # 1. 检索
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k
        )
        
        # 2. 构建上下文
        context = "\n\n".join(results["documents"][0])
        
        # 3. 生成回答
        prompt = f"""基于以下文档回答问题：

{context}

问题：{question}

请基于文档内容回答，如果文档中没有相关信息，请说明。"""
        
        response = await self.llm.chat(prompt)
        return response
```

---

## 📊 学习检查清单

- [ ] 理解分层架构设计
- [ ] 会使用依赖注入
- [ ] 能够设计模块化代码结构
- [ ] 理解配置管理最佳实践

---

## 🎯 下一步

继续学习：[文档处理Pipeline](./02_document_processing.md)
