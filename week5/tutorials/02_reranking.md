# 🏆 重排序模型详解

> **学习目标**：掌握Reranker重排序模型，优化检索结果质量

---

## 1. 为什么需要重排序？

### 问题：检索≠最佳排序

```
查询: "FastAPI性能对比"

初步检索结果（Top-5）:
1. "FastAPI框架介绍"          ← 相关但不是对比
2. "Python Web框架对比"        ← 相关
3. "FastAPI vs Django性能测试" ← 最相关！为什么排第3？
4. "FastAPI安装教程"          ← 不太相关
5. "Web API设计原则"          ← 不相关
```

### 解决方案：两阶段检索

```
Stage 1: 粗排（Embedding检索）
    ↓ 检索100个候选
Stage 2: 精排（Reranker重排序）
    ↓ 重新排序，返回Top-5
```

---

## 2. Reranker原理

### 2.1 Bi-Encoder vs Cross-Encoder

| 类型 | 原理 | 速度 | 精度 |
|------|------|------|------|
| Bi-Encoder | 分别编码query和doc | 快 | 中 |
| Cross-Encoder | 同时编码query+doc | 慢 | 高 |

**Reranker使用Cross-Encoder**：将query和doc拼接后一起编码，能捕获更细粒度的交互。

### 2.2 工作流程

```python
# Bi-Encoder (Stage 1)
query_emb = encode(query)      # [0.1, 0.2, ...]
doc_emb = encode(doc)          # [0.3, 0.4, ...]
score = cosine_sim(query_emb, doc_emb)  # 0.85

# Cross-Encoder (Stage 2)
score = encode_pair(query, doc)  # 直接输出相关性分数 0.92
```

---

## 3. 使用sentence-transformers重排序

### 3.1 安装

```bash
pip install sentence-transformers
```

### 3.2 基础使用

```python
from sentence_transformers import CrossEncoder

# 加载模型
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 计算相关性分数
pairs = [
    ("FastAPI性能对比", "FastAPI vs Django性能测试：FastAPI更快"),
    ("FastAPI性能对比", "FastAPI安装教程"),
    ("FastAPI性能对比", "Python Web框架介绍"),
]

scores = model.predict(pairs)
for pair, score in zip(pairs, scores):
    print(f"{score:.4f}: {pair[1][:30]}")
```

输出：
```
0.9234: FastAPI vs Django性能测试：FastAPI更快
0.1245: FastAPI安装教程
0.4532: Python Web框架介绍
```

---

## 4. 使用BGE Reranker（中文推荐）

### 4.1 安装

```bash
pip install FlagEmbedding
```

### 4.2 使用

```python
from FlagEmbedding import FlagReranker

# 加载模型（首次会下载）
reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True)

# 重排序
query = "FastAPI有什么优势？"
documents = [
    "FastAPI是基于Starlette的现代Python Web框架",
    "FastAPI性能卓越，是Python最快的Web框架之一",
    "Django是一个全功能的Python Web框架",
    "Flask是轻量级Python微框架",
]

# 计算分数
pairs = [[query, doc] for doc in documents]
scores = reranker.compute_score(pairs)

# 排序
ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
for doc, score in ranked:
    print(f"[{score:.4f}] {doc}")
```

---

## 5. 完整Reranker类

```python
from sentence_transformers import CrossEncoder
from typing import Optional

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self, 
        query: str, 
        documents: list[str], 
        top_k: Optional[int] = None
    ) -> list[dict]:
        """重排序文档"""
        if not documents:
            return []
        
        # 创建query-doc对
        pairs = [(query, doc) for doc in documents]
        
        # 计算分数
        scores = self.model.predict(pairs)
        
        # 排序
        results = [
            {"document": doc, "score": float(score)}
            for doc, score in zip(documents, scores)
        ]
        results.sort(key=lambda x: x["score"], reverse=True)
        
        if top_k:
            results = results[:top_k]
        
        return results

# 使用
reranker = Reranker()
results = reranker.rerank(
    query="Python Web框架性能",
    documents=["FastAPI很快", "Django功能全", "Flask很轻量"],
    top_k=2
)
```

---

## 6. 集成到RAG系统

```python
import chromadb
from openai import OpenAI
from sentence_transformers import CrossEncoder

class RAGWithReranker:
    def __init__(self):
        # 向量数据库
        self.chroma = chromadb.PersistentClient(path="./rerank_db")
        self.collection = self.chroma.get_or_create_collection("docs")
        
        # Reranker
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # LLM
        self.llm = OpenAI(
            api_key="your-key",
            base_url="https://api.deepseek.com/v1"
        )
    
    def add_documents(self, docs: list[str]):
        ids = [f"doc_{i}" for i in range(len(docs))]
        self.collection.upsert(documents=docs, ids=ids)
    
    def retrieve_and_rerank(
        self, 
        query: str, 
        initial_k: int = 20,
        final_k: int = 5
    ) -> list[str]:
        """两阶段检索"""
        # Stage 1: 粗排
        results = self.collection.query(
            query_texts=[query],
            n_results=initial_k
        )
        candidates = results["documents"][0]
        
        # Stage 2: 精排
        pairs = [(query, doc) for doc in candidates]
        scores = self.reranker.predict(pairs)
        
        # 排序取Top-K
        ranked = sorted(
            zip(candidates, scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [doc for doc, _ in ranked[:final_k]]
    
    def query(self, question: str) -> str:
        # 检索+重排序
        docs = self.retrieve_and_rerank(question)
        
        if not docs:
            return "未找到相关信息"
        
        # 构建Prompt
        context = "\n\n".join(docs)
        prompt = f"""基于以下文档回答问题：

文档：
{context}

问题：{question}

回答："""
        
        # 调用LLM
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# 使用
rag = RAGWithReranker()
rag.add_documents([
    "FastAPI性能测试显示其QPS可达到10000+，比Django快3倍",
    "FastAPI是基于Python的现代Web框架",
    "Django是全功能框架，适合大型项目",
    "Flask适合小型项目和微服务",
])

answer = rag.query("FastAPI的性能怎么样？")
print(answer)
```

---

## 7. 使用Cohere Rerank API

### 7.1 安装

```bash
pip install cohere
```

### 7.2 使用

```python
import cohere

co = cohere.Client("your-cohere-api-key")

# 重排序
results = co.rerank(
    model="rerank-multilingual-v3.0",
    query="FastAPI性能",
    documents=["FastAPI很快", "Django功能全", "Flask轻量"],
    top_n=3
)

for item in results.results:
    print(f"[{item.relevance_score:.4f}] {item.document.text}")
```

---

## 8. 常用Reranker模型

| 模型 | 语言 | 大小 | 推荐场景 |
|------|------|------|---------|
| ms-marco-MiniLM-L-6-v2 | 英文 | 小 | 开发测试 |
| bge-reranker-base | 中英 | 中 | 中文生产 |
| bge-reranker-large | 中英 | 大 | 高精度 |
| Cohere rerank-v3 | 多语言 | API | 商业项目 |

---

## 📺 推荐B站视频

搜索：
- **"Reranker 重排序 教程"**
- **"RAG 两阶段检索"**
- **"BGE Reranker 使用"**

---

## 9. 继续学习

📌 **Week 5 学习顺序**：
1. ✅ 混合检索
2. ✅ 重排序模型详解（本教程）
3. ➡️ 上下文压缩技术
4. ➡️ 高级RAG Pipeline

---

**重排序让检索结果更精准！💪**
