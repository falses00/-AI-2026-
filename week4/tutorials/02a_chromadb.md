# 📊 ChromaDB快速入门

> **学习目标**：掌握ChromaDB向量数据库的安装、配置和基本操作

---

## 1. ChromaDB简介

**ChromaDB**是一个开源的嵌入式向量数据库，专为AI应用设计：

- ✅ 安装简单：`pip install chromadb`
- ✅ 无需服务器：嵌入式运行
- ✅ 自动Embedding：内置embedding功能
- ✅ 支持持久化：数据可保存到磁盘

---

## 2. 安装与配置

### 2.1 安装

```bash
pip install chromadb
```

### 2.2 基础使用

```python
import chromadb

# 创建客户端（内存模式）
client = chromadb.Client()

# 创建或获取集合
collection = client.get_or_create_collection(name="my_documents")

print("ChromaDB初始化成功！")
```

### 2.3 持久化存储

```python
import chromadb

# 持久化客户端（数据保存到磁盘）
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="my_documents")
print(f"数据保存在: ./chroma_db")
```

---

## 3. 核心操作

### 3.1 添加文档

```python
# 创建集合
collection = client.get_or_create_collection(name="tech_docs")

# 添加文档（ChromaDB会自动生成embedding）
collection.add(
    documents=[
        "FastAPI是一个高性能的Python Web框架",
        "Django是一个全功能的Python Web框架",
        "Flask是一个轻量级的Python微框架",
        "NumPy是Python科学计算的核心库"
    ],
    ids=["doc1", "doc2", "doc3", "doc4"],
    metadatas=[
        {"category": "web", "year": 2018},
        {"category": "web", "year": 2005},
        {"category": "web", "year": 2010},
        {"category": "data", "year": 2006}
    ]
)

print(f"已添加 {collection.count()} 个文档")
```

### 3.2 查询文档

```python
# 语义查询
results = collection.query(
    query_texts=["高性能的API开发框架"],
    n_results=2
)

print("查询结果:")
for i, (doc, distance) in enumerate(zip(
    results["documents"][0], 
    results["distances"][0]
)):
    print(f"  {i+1}. {doc} (距离: {distance:.4f})")
```

输出：
```
查询结果:
  1. FastAPI是一个高性能的Python Web框架 (距离: 0.3421)
  2. Flask是一个轻量级的Python微框架 (距离: 0.5123)
```

### 3.3 带元数据过滤的查询

```python
# 只在web类别中搜索
results = collection.query(
    query_texts=["Python框架"],
    n_results=3,
    where={"category": "web"}  # 元数据过滤
)

# 组合条件
results = collection.query(
    query_texts=["Python框架"],
    n_results=3,
    where={
        "$and": [
            {"category": "web"},
            {"year": {"$gte": 2010}}  # 2010年及以后
        ]
    }
)
```

### 3.4 更新和删除

```python
# 更新文档（使用upsert）
collection.upsert(
    documents=["FastAPI是目前最快的Python Web框架之一"],
    ids=["doc1"],
    metadatas=[{"category": "web", "year": 2018, "updated": True}]
)

# 删除文档
collection.delete(ids=["doc4"])

# 按条件删除
collection.delete(where={"category": "data"})
```

### 3.5 获取所有文档

```python
# 获取所有文档
all_docs = collection.get()
print(f"文档数量: {len(all_docs['ids'])}")

# 获取特定文档
docs = collection.get(ids=["doc1", "doc2"])
```

---

## 4. 使用自定义Embedding

### 4.1 使用OpenAI Embedding

```python
import chromadb
from chromadb.utils import embedding_functions

# 创建OpenAI embedding函数
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-openai-api-key",
    model_name="text-embedding-3-small"
)

# 创建使用自定义embedding的集合
collection = client.get_or_create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

### 4.2 使用sentence-transformers

```python
# 使用sentence-transformers（本地模型）
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"  # 中文模型
)

collection = client.get_or_create_collection(
    name="local_docs",
    embedding_function=sentence_transformer_ef
)
```

---

## 5. 完整示例：知识库

```python
import chromadb
from chromadb.config import Settings

class KnowledgeBase:
    def __init__(self, persist_path: str = "./knowledge_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "个人知识库"}
        )
    
    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        """添加单个文档"""
        self.collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata] if metadata else None
        )
    
    def add_documents(self, docs: list[dict]):
        """批量添加文档"""
        self.collection.upsert(
            ids=[d["id"] for d in docs],
            documents=[d["content"] for d in docs],
            metadatas=[d.get("metadata") for d in docs]
        )
    
    def search(self, query: str, top_k: int = 5, filters: dict = None) -> list[dict]:
        """搜索文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"]
        )
        
        # 整理结果
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else None,
                "distance": results["distances"][0][i]
            })
        return output
    
    def delete(self, doc_id: str):
        """删除文档"""
        self.collection.delete(ids=[doc_id])
    
    def count(self) -> int:
        """文档数量"""
        return self.collection.count()

# 使用示例
kb = KnowledgeBase()

# 添加文档
kb.add_documents([
    {"id": "1", "content": "FastAPI是高性能Python框架", "metadata": {"type": "tech"}},
    {"id": "2", "content": "机器学习是人工智能的子领域", "metadata": {"type": "ai"}},
    {"id": "3", "content": "向量数据库用于存储embedding", "metadata": {"type": "db"}},
])

# 搜索
results = kb.search("Python Web开发", top_k=2)
for r in results:
    print(f"[{r['distance']:.4f}] {r['content']}")
```

---

## 6. 最佳实践

### 6.1 文档分块

```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """将长文本分块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # 重叠部分
    return chunks

# 添加长文档
long_doc = "这是一个很长的文档..." * 100
chunks = chunk_text(long_doc)
for i, chunk in enumerate(chunks):
    kb.add_document(
        doc_id=f"long_doc_chunk_{i}",
        content=chunk,
        metadata={"source": "long_doc", "chunk_index": i}
    )
```

### 6.2 距离阈值过滤

```python
def search_with_threshold(kb, query, threshold=0.5):
    """只返回相似度足够高的结果"""
    results = kb.search(query, top_k=10)
    return [r for r in results if r["distance"] < threshold]
```

---

## 📺 推荐B站视频

在B站搜索：
- **"ChromaDB 入门教程"**
- **"向量数据库 Python"**
- **"RAG ChromaDB 实战"**

---

## 7. 继续学习

📌 **Week 4 学习顺序**：
1. ✅ Embedding向量化入门
2. ✅ ChromaDB快速入门（本教程）
3. ➡️ 检索策略详解
4. ➡️ 构建简单RAG系统

---

**ChromaDB让向量存储变得简单！💪**
