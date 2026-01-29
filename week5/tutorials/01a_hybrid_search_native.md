# 🔀 混合检索原理与实现

> **学习目标**：掌握语义检索与关键词检索的融合技术

---

## 1. 为什么需要混合检索？

### 语义检索的局限

```
查询: "BM25算法"
语义检索可能返回: "TF-IDF是一种文本权重算法"  ← 语义相近但不是BM25
```

### 关键词检索的局限

```
查询: "高性能API框架"
关键词检索返回: 必须包含这些词 ← 会遗漏"FastAPI是速度最快的Python Web框架"
```

### 混合检索 = 两者优势结合！

---

## 2. 混合检索架构

```
              查询
               │
       ┌───────┴───────┐
       ▼               ▼
  ┌─────────┐     ┌─────────┐
  │ 语义检索 │     │关键词检索│
  │ (Dense) │     │ (BM25)  │
  └────┬────┘     └────┬────┘
       │               │
       ▼               ▼
  ┌─────────┐     ┌─────────┐
  │ 结果列表1│     │ 结果列表2│
  └────┬────┘     └────┬────┘
       │               │
       └───────┬───────┘
               ▼
         ┌──────────┐
         │ 融合排序  │ ← RRF算法
         └────┬─────┘
              ▼
          最终结果
```

---

## 3. BM25关键词检索

### 3.1 安装

```bash
pip install rank-bm25
```

### 3.2 基础使用

```python
from rank_bm25 import BM25Okapi
import jieba  # 中文分词

class BM25Retriever:
    def __init__(self, documents: list[str]):
        self.documents = documents
        # 中文分词
        self.tokenized = [list(jieba.cut(doc)) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized)
    
    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """BM25搜索"""
        query_tokens = list(jieba.cut(query))
        scores = self.bm25.get_scores(query_tokens)
        
        # 获取Top-K
        top_indices = scores.argsort()[-top_k:][::-1]
        results = [(self.documents[i], scores[i]) for i in top_indices]
        return results

# 使用
docs = [
    "FastAPI是高性能Python Web框架",
    "BM25是经典的关键词检索算法",
    "向量数据库用于语义搜索"
]
bm25 = BM25Retriever(docs)
results = bm25.search("BM25算法")
for doc, score in results:
    print(f"{score:.4f}: {doc}")
```

---

## 4. 融合算法：RRF

### 4.1 RRF原理

**RRF (Reciprocal Rank Fusion)** 根据排名融合多个结果列表：

```
RRF_score = Σ 1 / (k + rank_i)
```

其中k通常取60。

### 4.2 实现

```python
def reciprocal_rank_fusion(
    result_lists: list[list[tuple[str, float]]], 
    k: int = 60
) -> list[tuple[str, float]]:
    """RRF融合多个结果列表"""
    scores = {}
    
    for results in result_lists:
        for rank, (doc, _) in enumerate(results):
            if doc not in scores:
                scores[doc] = 0
            scores[doc] += 1 / (k + rank + 1)
    
    # 按RRF分数排序
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results

# 使用
semantic_results = [("doc1", 0.9), ("doc2", 0.8), ("doc3", 0.7)]
keyword_results = [("doc2", 5.0), ("doc4", 4.0), ("doc1", 3.0)]

fused = reciprocal_rank_fusion([semantic_results, keyword_results])
print(fused)
# [('doc2', 0.033), ('doc1', 0.032), ('doc3', 0.016), ('doc4', 0.016)]
```

---

## 5. 完整混合检索类

```python
import chromadb
from rank_bm25 import BM25Okapi
import jieba
import numpy as np
from openai import OpenAI
import os

class HybridRetriever:
    def __init__(
        self, 
        collection_name: str = "hybrid_docs",
        alpha: float = 0.5  # 语义检索权重
    ):
        # ChromaDB for 语义检索
        self.chroma = chromadb.PersistentClient(path="./hybrid_db")
        self.collection = self.chroma.get_or_create_collection(name=collection_name)
        
        # BM25 for 关键词检索
        self.documents = []
        self.bm25 = None
        
        # 权重
        self.alpha = alpha
        
        # LLM客户端
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
    
    def add_documents(self, documents: list[str]):
        """添加文档"""
        ids = [f"doc_{len(self.documents) + i}" for i in range(len(documents))]
        
        # 添加到ChromaDB
        self.collection.upsert(
            documents=documents,
            ids=ids
        )
        
        # 更新BM25索引
        self.documents.extend(documents)
        tokenized = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
        
        print(f"已添加 {len(documents)} 个文档")
    
    def _semantic_search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        """语义检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        return list(zip(
            results["documents"][0],
            [1 - d for d in results["distances"][0]]  # 距离转相似度
        ))
    
    def _keyword_search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        """关键词检索"""
        if self.bm25 is None:
            return []
        
        query_tokens = list(jieba.cut(query))
        scores = self.bm25.get_scores(query_tokens)
        
        # 归一化
        if scores.max() > 0:
            scores = scores / scores.max()
        
        top_indices = scores.argsort()[-top_k:][::-1]
        return [(self.documents[i], scores[i]) for i in top_indices]
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """混合检索"""
        # 1. 分别检索
        semantic_results = self._semantic_search(query, top_k * 2)
        keyword_results = self._keyword_search(query, top_k * 2)
        
        # 2. 融合得分
        scores = {}
        
        for doc, score in semantic_results:
            scores[doc] = scores.get(doc, 0) + self.alpha * score
        
        for doc, score in keyword_results:
            scores[doc] = scores.get(doc, 0) + (1 - self.alpha) * score
        
        # 3. 排序返回
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"document": doc, "score": score}
            for doc, score in sorted_results[:top_k]
        ]
    
    def search_rrf(self, query: str, top_k: int = 5) -> list[dict]:
        """使用RRF融合的混合检索"""
        semantic_results = self._semantic_search(query, top_k * 2)
        keyword_results = self._keyword_search(query, top_k * 2)
        
        # RRF融合
        fused = reciprocal_rank_fusion([semantic_results, keyword_results])
        
        return [
            {"document": doc, "rrf_score": score}
            for doc, score in fused[:top_k]
        ]

# 使用示例
if __name__ == "__main__":
    retriever = HybridRetriever(alpha=0.6)  # 60%语义 + 40%关键词
    
    retriever.add_documents([
        "FastAPI是高性能Python Web框架，基于Starlette和Pydantic",
        "BM25是一种经典的关键词检索算法，广泛用于搜索引擎",
        "向量数据库如Milvus和ChromaDB用于存储和检索embedding",
        "RAG系统结合检索和生成，提供更准确的问答",
    ])
    
    results = retriever.search("BM25检索算法原理")
    for r in results:
        print(f"[{r['score']:.4f}] {r['document']}")
```

---

## 6. 调优参数

### α值选择

| α值 | 场景 |
|-----|------|
| 0.7-0.9 | 语义理解重要（问答、对话） |
| 0.5 | 平衡 |
| 0.3-0.5 | 精确匹配重要（代码搜索、专业术语） |

### 实验方法

```python
def evaluate_alpha(retriever, test_queries, ground_truth):
    """评估不同α值的效果"""
    results = {}
    
    for alpha in [0.3, 0.5, 0.7, 0.9]:
        retriever.alpha = alpha
        correct = 0
        
        for query, expected in zip(test_queries, ground_truth):
            result = retriever.search(query, top_k=1)
            if result and result[0]["document"] == expected:
                correct += 1
        
        results[alpha] = correct / len(test_queries)
    
    return results
```

---

## 📺 推荐B站视频

搜索：
- **"混合检索 RAG"**
- **"BM25 语义搜索 融合"**
- **"Hybrid Search 实战"**

---

## 7. 继续学习

📌 **Week 5 学习顺序**：
1. ✅ 混合检索原理与实现（本教程）
2. ➡️ 重排序模型详解
3. ➡️ 上下文压缩技术
4. ➡️ 高级RAG Pipeline

---

**混合检索 = 语义 + 关键词的完美结合！💪**
