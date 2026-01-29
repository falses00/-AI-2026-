# 🗄️ Milvus向量数据库

> **学习目标**：掌握生产级向量数据库Milvus的使用

---

## 1. Milvus简介

**Milvus**是一个开源的分布式向量数据库，适合生产环境：

| 特性 | ChromaDB | Milvus |
|------|----------|--------|
| 部署 | 嵌入式/简单 | Docker/K8s |
| 规模 | 小规模 | 亿级向量 |
| 性能 | 中等 | 高性能 |
| 功能 | 基础 | 丰富 |

---

## 2. 安装与启动

### 2.1 使用Docker启动

```bash
# 下载docker-compose文件
wget https://github.com/milvus-io/milvus/releases/download/v2.3.0/milvus-standalone-docker-compose.yml -O docker-compose.yml

# 启动Milvus
docker-compose up -d

# 检查状态
docker-compose ps
```

### 2.2 安装Python SDK

```bash
pip install pymilvus
```

### 2.3 连接测试

```python
from pymilvus import connections, utility

# 连接到Milvus
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

# 检查连接
print(f"连接成功: {utility.get_server_version()}")
```

---

## 3. 核心概念

```
Milvus层级结构:

Database (数据库)
    └── Collection (集合，类似表)
            ├── Schema (模式定义)
            │     ├── Field: id (主键)
            │     ├── Field: embedding (向量)
            │     └── Field: metadata (标量)
            └── Index (索引)
```

---

## 4. 基础操作

### 4.1 创建Collection

```python
from pymilvus import (
    connections, Collection, FieldSchema, 
    CollectionSchema, DataType, utility
)

# 连接
connections.connect(host="localhost", port="19530")

# 定义字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
]

# 创建schema
schema = CollectionSchema(fields=fields, description="文档集合")

# 创建collection
collection = Collection(name="documents", schema=schema)
print(f"Collection创建成功: {collection.name}")
```

### 4.2 创建索引

```python
# 创建向量索引（必须在搜索前创建）
index_params = {
    "metric_type": "COSINE",  # 余弦相似度
    "index_type": "IVF_FLAT",  # 索引类型
    "params": {"nlist": 128}   # 聚类数
}

collection.create_index(
    field_name="embedding",
    index_params=index_params
)

# 加载到内存
collection.load()
print("索引创建并加载成功")
```

### 4.3 插入数据

```python
from openai import OpenAI

client = OpenAI(api_key="your-key", base_url="https://api.deepseek.com/v1")

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 准备数据
texts = [
    "FastAPI是高性能Python框架",
    "Django是全功能Web框架",
    "机器学习用于数据预测"
]
categories = ["web", "web", "ai"]
embeddings = [get_embedding(t) for t in texts]

# 插入数据
data = [texts, embeddings, categories]
collection.insert(data)
collection.flush()  # 确保数据持久化

print(f"插入完成，总数: {collection.num_entities}")
```

### 4.4 搜索

```python
# 搜索向量
query = "Python Web开发框架"
query_embedding = get_embedding(query)

results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param={"metric_type": "COSINE", "params": {"nprobe": 10}},
    limit=3,
    output_fields=["text", "category"]
)

print("搜索结果:")
for hits in results:
    for hit in hits:
        print(f"  ID: {hit.id}")
        print(f"  距离: {hit.distance:.4f}")
        print(f"  文本: {hit.entity.get('text')}")
        print(f"  类别: {hit.entity.get('category')}")
        print()
```

### 4.5 带过滤的搜索

```python
# 只搜索web类别
results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param={"metric_type": "COSINE", "params": {"nprobe": 10}},
    limit=3,
    expr='category == "web"',  # 过滤条件
    output_fields=["text", "category"]
)
```

### 4.6 删除数据

```python
# 按ID删除
collection.delete(expr="id in [1, 2, 3]")

# 按条件删除
collection.delete(expr='category == "ai"')
```

---

## 5. 完整示例：文档库

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from openai import OpenAI
from typing import Optional

class MilvusDocStore:
    def __init__(self, collection_name: str = "documents", dim: int = 1536):
        # 连接Milvus
        connections.connect(host="localhost", port="19530")
        
        # OpenAI客户端
        self.client = OpenAI(
            api_key="your-key",
            base_url="https://api.deepseek.com/v1"
        )
        
        # 创建或获取collection
        if utility.has_collection(collection_name):
            self.collection = Collection(name=collection_name)
        else:
            self.collection = self._create_collection(collection_name, dim)
        
        self.collection.load()
    
    def _create_collection(self, name: str, dim: int) -> Collection:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
        ]
        schema = CollectionSchema(fields=fields)
        collection = Collection(name=name, schema=schema)
        
        # 创建索引
        collection.create_index(
            field_name="embedding",
            index_params={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        )
        return collection
    
    def _get_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def add(self, text: str, source: str = ""):
        embedding = self._get_embedding(text)
        self.collection.insert([[text], [embedding], [source]])
        self.collection.flush()
    
    def add_batch(self, texts: list[str], sources: list[str] = None):
        if sources is None:
            sources = [""] * len(texts)
        embeddings = [self._get_embedding(t) for t in texts]
        self.collection.insert([texts, embeddings, sources])
        self.collection.flush()
    
    def search(self, query: str, top_k: int = 5, source_filter: Optional[str] = None):
        query_emb = self._get_embedding(query)
        
        expr = f'source == "{source_filter}"' if source_filter else None
        
        results = self.collection.search(
            data=[query_emb],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            expr=expr,
            output_fields=["text", "source"]
        )
        
        output = []
        for hits in results:
            for hit in hits:
                output.append({
                    "id": hit.id,
                    "text": hit.entity.get("text"),
                    "source": hit.entity.get("source"),
                    "score": 1 - hit.distance  # 转换为相似度
                })
        return output
    
    def count(self) -> int:
        return self.collection.num_entities

# 使用
store = MilvusDocStore()
store.add_batch(
    texts=["FastAPI入门指南", "Django REST框架", "Flask微服务"],
    sources=["docs", "docs", "docs"]
)

results = store.search("高性能API框架")
for r in results:
    print(f"[{r['score']:.4f}] {r['text']}")
```

---

## 6. 索引类型选择

| 索引类型 | 特点 | 适用场景 |
|---------|------|---------|
| FLAT | 精确搜索，无压缩 | 小数据集 |
| IVF_FLAT | 聚类索引，较快 | 中等规模 |
| IVF_SQ8 | 量化压缩，省内存 | 大规模 |
| HNSW | 图索引，最快 | 追求速度 |

---

## 📺 推荐B站视频

搜索：
- **"Milvus 向量数据库 教程"**
- **"Milvus Docker 部署"**
- **"RAG Milvus 实战"**

---

## 7. 继续学习

📌 **Week 4 学习顺序**：
1. ✅ Embedding向量化入门
2. ✅ ChromaDB或Milvus（本教程）
3. ➡️ 检索策略详解
4. ➡️ 构建简单RAG系统

---

**Milvus是生产级RAG的首选！💪**
