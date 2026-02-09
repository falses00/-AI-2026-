# 📘 父文档检索器 - Parent Document Retriever

> **学习目标**：掌握父文档检索策略，解决"小块检索、大块返回"的问题

---

## 🎯 为什么需要父文档检索？

### 传统分块的困境

```
原始文档（完整上下文）:
┌─────────────────────────────────────────────────────────────────┐
│ FastAPI依赖注入系统                                              │
│                                                                  │
│ FastAPI的依赖注入（Dependency Injection）是其核心功能之一。      │
│ 它使用Python的类型提示和Depends函数来声明依赖。                  │
│                                                                  │
│ 基本用法：                                                       │
│ ```python                                                        │
│ from fastapi import Depends                                      │
│                                                                  │
│ def get_db():                                                    │
│     db = SessionLocal()                                          │
│     try:                                                         │
│         yield db                                                 │
│     finally:                                                     │
│         db.close()                                               │
│                                                                  │
│ @app.get("/users")                                               │
│ def read_users(db: Session = Depends(get_db)):                   │
│     return db.query(User).all()                                  │
│ ```                                                              │
│                                                                  │
│ 这个模式的好处是...                                              │
└─────────────────────────────────────────────────────────────────┘

传统分块后（丢失上下文）:
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ Chunk 1:          │ │ Chunk 2:          │ │ Chunk 3:          │
│ FastAPI依赖注入... │ │ def get_db():     │ │ @app.get(...)     │
│ 是核心功能...     │ │     db = ...      │ │     return ...    │
└───────────────────┘ └───────────────────┘ └───────────────────┘
      ↑ 检索到这个块，但缺少代码示例
```

### 父文档检索的解决方案

```
存储策略:
                    ┌─────────────────────────────────────────┐
                    │        父文档 (Parent Document)          │
                    │        完整的FastAPI依赖注入章节         │
                    └───────────────────┬─────────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
    │ 子块1 (Embedding) │    │ 子块2 (Embedding) │    │ 子块3 (Embedding) │
    │ 概念介绍部分      │    │ 代码示例部分      │    │ 好处说明部分      │
    └──────────────────┘    └──────────────────┘    └──────────────────┘

检索流程:
查询 "FastAPI Depends用法" 
    → 匹配到子块2（代码示例）
    → 返回父文档（完整章节，包含概念+代码+说明）
```

---

## 📚 架构设计

### 核心思想

| 存储 | 检索 | 返回 |
|-----|------|------|
| 小块（精确匹配） | 小块（高相似度） | 父文档（完整上下文） |

### 数据结构

```python
# 父文档
ParentDocument:
    id: str
    content: str          # 完整内容
    metadata: dict        # 元数据（来源、章节等）

# 子块
ChildChunk:
    id: str
    content: str          # 小块内容
    parent_id: str        # 关联的父文档ID
    embedding: list[float]
```

---

## 💻 实现父文档检索器

### 1. 文档分块器

```python
from typing import Optional
import uuid
import re

class HierarchicalChunker:
    """层级分块器 - 生成父文档和子块"""
    
    def __init__(
        self,
        parent_chunk_size: int = 2000,   # 父文档大小
        child_chunk_size: int = 400,      # 子块大小
        child_overlap: int = 50           # 子块重叠
    ):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
    
    def split_document(self, document: str, metadata: dict = None) -> dict:
        """将文档分割为父文档和子块"""
        
        # 首先按段落/章节分割成父文档
        parent_docs = self._split_into_parents(document)
        
        result = {
            "parents": [],
            "children": []
        }
        
        for parent_content in parent_docs:
            parent_id = str(uuid.uuid4())
            
            # 存储父文档
            result["parents"].append({
                "id": parent_id,
                "content": parent_content,
                "metadata": metadata or {}
            })
            
            # 将父文档分割成子块
            children = self._split_into_children(parent_content, parent_id)
            result["children"].extend(children)
        
        return result
    
    def _split_into_parents(self, document: str) -> list[str]:
        """按自然边界分割成父文档"""
        # 尝试按Markdown标题分割
        sections = re.split(r'\n(?=#{1,3}\s)', document)
        
        parents = []
        current = ""
        
        for section in sections:
            if len(current) + len(section) <= self.parent_chunk_size:
                current += section + "\n"
            else:
                if current:
                    parents.append(current.strip())
                current = section + "\n"
        
        if current:
            parents.append(current.strip())
        
        return parents
    
    def _split_into_children(self, parent: str, parent_id: str) -> list[dict]:
        """将父文档分割成子块"""
        children = []
        
        # 简单的滑动窗口分块
        start = 0
        chunk_index = 0
        
        while start < len(parent):
            end = start + self.child_chunk_size
            chunk_content = parent[start:end]
            
            children.append({
                "id": f"{parent_id}_child_{chunk_index}",
                "content": chunk_content,
                "parent_id": parent_id,
                "chunk_index": chunk_index
            })
            
            start = end - self.child_overlap
            chunk_index += 1
        
        return children
```

### 2. 父文档存储

```python
import chromadb

class ParentDocumentStore:
    """父文档存储 - 分离存储父文档和子块"""
    
    def __init__(self, persist_directory: str = None):
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        
        # 子块集合 - 用于向量检索
        self.children_collection = self.client.get_or_create_collection(
            name="children",
            metadata={"hnsw:space": "cosine"}
        )
        
        # 父文档存储 - 使用字典（或数据库）
        self.parent_store: dict[str, dict] = {}
    
    def add_document(self, document: str, metadata: dict = None):
        """添加文档"""
        chunker = HierarchicalChunker()
        result = chunker.split_document(document, metadata)
        
        # 存储父文档
        for parent in result["parents"]:
            self.parent_store[parent["id"]] = parent
        
        # 存储子块到向量数据库
        if result["children"]:
            self.children_collection.add(
                ids=[c["id"] for c in result["children"]],
                documents=[c["content"] for c in result["children"]],
                metadatas=[{
                    "parent_id": c["parent_id"],
                    "chunk_index": c["chunk_index"]
                } for c in result["children"]]
            )
        
        return {
            "parents_added": len(result["parents"]),
            "children_added": len(result["children"])
        }
    
    def get_parent(self, parent_id: str) -> Optional[dict]:
        """获取父文档"""
        return self.parent_store.get(parent_id)
```

### 3. 父文档检索器

```python
class ParentDocumentRetriever:
    """父文档检索器 - 小块检索，大块返回"""
    
    def __init__(self, store: ParentDocumentStore):
        self.store = store
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        return_children: bool = False
    ) -> list[dict]:
        """检索相关父文档"""
        
        # Step 1: 在子块中检索
        child_results = self.store.children_collection.query(
            query_texts=[query],
            n_results=top_k * 2,  # 多检索一些，因为可能有重复父文档
            include=["documents", "metadatas", "distances"]
        )
        
        # Step 2: 去重并获取父文档
        seen_parents = set()
        results = []
        
        for i in range(len(child_results["ids"][0])):
            parent_id = child_results["metadatas"][0][i]["parent_id"]
            
            if parent_id in seen_parents:
                continue
            seen_parents.add(parent_id)
            
            # 获取父文档
            parent = self.store.get_parent(parent_id)
            if parent:
                result = {
                    "parent_id": parent_id,
                    "parent_content": parent["content"],
                    "parent_metadata": parent["metadata"],
                    "matched_child": child_results["documents"][0][i],
                    "distance": child_results["distances"][0][i]
                }
                
                if return_children:
                    result["matched_child_content"] = child_results["documents"][0][i]
                
                results.append(result)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def retrieve_with_context(
        self, 
        query: str, 
        top_k: int = 3
    ) -> str:
        """检索并格式化为上下文"""
        results = self.retrieve(query, top_k)
        
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(f"[文档 {i}]\n{r['parent_content']}")
        
        return "\n\n---\n\n".join(context_parts)
```

---

## 🚀 完整使用示例

```python
# 初始化
store = ParentDocumentStore()
retriever = ParentDocumentRetriever(store)

# 添加文档
document = """
# FastAPI依赖注入

FastAPI的依赖注入系统非常强大，让你可以轻松地：
- 共享数据库连接
- 实现认证和授权
- 复用通用逻辑

## 基本用法

使用 `Depends` 函数声明依赖：

```python
from fastapi import Depends, FastAPI

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

## 依赖的依赖

依赖可以有自己的依赖，形成依赖链：

```python
def get_current_user(db: Session = Depends(get_db)):
    # 从数据库获取用户
    ...

def get_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Not admin")
    return user
```
"""

# 添加文档
result = store.add_document(document, {"source": "fastapi_tutorial.md"})
print(f"添加了 {result['parents_added']} 个父文档和 {result['children_added']} 个子块")

# 检索
query = "FastAPI Depends 用法示例"
results = retriever.retrieve(query, top_k=2)

for r in results:
    print(f"匹配的子块: {r['matched_child'][:100]}...")
    print(f"返回的父文档: {r['parent_content'][:200]}...")
    print(f"距离: {r['distance']}")
    print("---")

# 获取格式化上下文（用于RAG）
context = retriever.retrieve_with_context(query)
print("RAG上下文:")
print(context)
```

---

## 📊 参数调优建议

| 参数 | 建议值 | 说明 |
|-----|-------|------|
| parent_chunk_size | 1500-3000 | 父文档大小，确保包含完整上下文 |
| child_chunk_size | 300-500 | 子块大小，越小匹配越精确 |
| child_overlap | 50-100 | 重叠区域，避免信息丢失 |

### 场景适配

| 场景 | 父文档大小 | 子块大小 |
|-----|-----------|---------|
| 技术文档 | 2000-3000 | 400-500 |
| FAQ问答 | 500-1000 | 200-300 |
| 长篇文章 | 3000-5000 | 500-800 |

---

## 🔗 与其他技术的结合

### 父文档检索 + Multi-Query

```python
async def enhanced_retrieve(query: str, store: ParentDocumentStore):
    """结合Multi-Query和父文档检索"""
    
    # 1. 生成多个查询
    multi_query = MultiQueryRetriever(client, store.children_collection)
    queries = await multi_query.generate_queries(query)
    
    # 2. 对每个查询进行子块检索
    all_parent_ids = set()
    for q in queries:
        results = store.children_collection.query(query_texts=[q], n_results=3)
        for meta in results["metadatas"][0]:
            all_parent_ids.add(meta["parent_id"])
    
    # 3. 返回所有匹配的父文档
    parents = [store.get_parent(pid) for pid in all_parent_ids]
    return [p for p in parents if p]
```

---

## 📊 学习检查清单

- [ ] 理解传统分块丢失上下文的问题
- [ ] 掌握父文档检索的核心思想（小块检索，大块返回）
- [ ] 能够实现层级分块器
- [ ] 能够实现父文档存储和检索器
- [ ] 知道如何调优分块参数

---

## 🎯 下一步

完成Week4 RAG基础全部内容！

继续前往：
👉 [Week5: RAG系统进阶](../week5/README.md)
