# 🚀 高级RAG Pipeline

> **学习目标**：整合所有技术，构建生产级RAG系统

---

## 1. 完整Pipeline架构

```
                    用户问题
                        │
                        ▼
               ┌────────────────┐
               │  查询理解/改写  │ ← LLM
               └───────┬────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌──────────────┐       ┌──────────────┐
    │  语义检索     │       │  关键词检索   │
    │  (Dense)     │       │  (BM25)      │
    └──────┬───────┘       └──────┬───────┘
           │                       │
           └───────────┬───────────┘
                       ▼
               ┌────────────────┐
               │  RRF融合排序   │
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │  重排序Rerank  │ ← Cross-Encoder
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │  上下文压缩    │ ← LLM/句子提取
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │  答案生成      │ ← LLM
               └───────┬────────┘
                       ▼
                    回答
```

---

## 2. 完整实现

```python
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer
from openai import OpenAI
import jieba
import numpy as np
from typing import Optional
import os

class AdvancedRAG:
    """生产级RAG系统"""
    
    def __init__(
        self,
        persist_path: str = "./advanced_rag_db",
        semantic_weight: float = 0.6,
        rerank_top_k: int = 20,
        final_top_k: int = 5
    ):
        # 向量数据库
        self.chroma = chromadb.PersistentClient(path=persist_path)
        self.collection = self.chroma.get_or_create_collection("knowledge")
        
        # BM25索引
        self.documents = []
        self.bm25 = None
        
        # 模型
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.sentence_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        
        # LLM
        self.llm = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        
        # 配置
        self.semantic_weight = semantic_weight
        self.rerank_top_k = rerank_top_k
        self.final_top_k = final_top_k
    
    # ============ 文档管理 ============
    
    def add_documents(self, documents: list[str], metadatas: list[dict] = None):
        """添加文档"""
        ids = [f"doc_{self.collection.count() + i}" for i in range(len(documents))]
        
        # ChromaDB
        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        # BM25
        self.documents.extend(documents)
        tokenized = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
        
        print(f"添加 {len(documents)} 个文档，总数: {self.collection.count()}")
    
    # ============ 查询改写 ============
    
    def _rewrite_query(self, query: str) -> list[str]:
        """LLM查询改写"""
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": f"""将以下查询改写成3个不同的表达方式，保持语义相同：

查询：{query}

直接输出3个改写，每行一个："""
            }],
            temperature=0.7,
            max_tokens=200
        )
        
        rewrites = response.choices[0].message.content.strip().split('\n')
        return [query] + [r.strip() for r in rewrites[:3] if r.strip()]
    
    # ============ 混合检索 ============
    
    def _semantic_search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        """语义检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        return list(zip(
            results["documents"][0],
            [1 - d for d in results["distances"][0]]  # 转相似度
        ))
    
    def _keyword_search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        """关键词检索"""
        if not self.bm25:
            return []
        
        tokens = list(jieba.cut(query))
        scores = self.bm25.get_scores(tokens)
        
        if scores.max() > 0:
            scores = scores / scores.max()
        
        indices = scores.argsort()[-top_k:][::-1]
        return [(self.documents[i], scores[i]) for i in indices]
    
    def _hybrid_search(self, queries: list[str], top_k: int) -> list[str]:
        """混合检索+RRF融合"""
        doc_scores = {}
        
        for query in queries:
            semantic = self._semantic_search(query, top_k)
            keyword = self._keyword_search(query, top_k)
            
            # 加权融合
            for doc, score in semantic:
                doc_scores[doc] = doc_scores.get(doc, 0) + self.semantic_weight * score
            
            for doc, score in keyword:
                doc_scores[doc] = doc_scores.get(doc, 0) + (1 - self.semantic_weight) * score
        
        # 排序
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in sorted_docs[:top_k]]
    
    # ============ 重排序 ============
    
    def _rerank(self, query: str, documents: list[str], top_k: int) -> list[str]:
        """交叉编码器重排序"""
        if not documents:
            return []
        
        pairs = [(query, doc) for doc in documents]
        scores = self.reranker.predict(pairs)
        
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]
    
    # ============ 上下文压缩 ============
    
    def _compress_context(self, query: str, documents: list[str]) -> str:
        """句子级压缩"""
        all_sentences = []
        for doc in documents:
            sentences = [s.strip() for s in doc.replace('\n', '。').split('。') if s.strip()]
            all_sentences.extend(sentences)
        
        if len(all_sentences) <= 5:
            return "\n\n".join(documents)
        
        # 按相似度选择句子
        query_emb = self.sentence_model.encode([query])
        sent_embs = self.sentence_model.encode(all_sentences)
        
        similarities = np.dot(sent_embs, query_emb.T).flatten()
        top_indices = similarities.argsort()[-10:][::-1]  # Top 10句子
        
        selected = [all_sentences[i] for i in sorted(top_indices)]
        return '。'.join(selected) + '。'
    
    # ============ 答案生成 ============
    
    def _generate_answer(self, query: str, context: str) -> str:
        """生成回答"""
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": """你是一个知识库问答助手。根据提供的上下文回答问题。
- 只根据上下文中的信息回答
- 如果上下文没有相关信息，明确说明
- 回答要简洁准确"""},
                {"role": "user", "content": f"上下文：\n{context}\n\n问题：{query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    
    # ============ 主查询方法 ============
    
    def query(
        self, 
        question: str,
        enable_rewrite: bool = True,
        enable_rerank: bool = True,
        enable_compress: bool = True
    ) -> dict:
        """完整RAG查询"""
        
        # 1. 查询改写
        if enable_rewrite:
            queries = self._rewrite_query(question)
        else:
            queries = [question]
        
        # 2. 混合检索
        candidates = self._hybrid_search(queries, self.rerank_top_k)
        
        if not candidates:
            return {
                "answer": "抱歉，没有找到相关信息。",
                "sources": [],
                "steps": {"rewrite": queries, "candidates": 0}
            }
        
        # 3. 重排序
        if enable_rerank:
            documents = self._rerank(question, candidates, self.final_top_k)
        else:
            documents = candidates[:self.final_top_k]
        
        # 4. 上下文压缩
        if enable_compress:
            context = self._compress_context(question, documents)
        else:
            context = "\n\n".join(documents)
        
        # 5. 生成回答
        answer = self._generate_answer(question, context)
        
        return {
            "answer": answer,
            "sources": documents,
            "context_length": len(context),
            "steps": {
                "rewrite_queries": queries,
                "candidates_count": len(candidates),
                "final_docs": len(documents)
            }
        }
    
    def query_stream(self, question: str):
        """流式查询"""
        queries = self._rewrite_query(question)
        candidates = self._hybrid_search(queries, self.rerank_top_k)
        documents = self._rerank(question, candidates, self.final_top_k)
        context = self._compress_context(question, documents)
        
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "根据上下文回答问题。"},
                {"role": "user", "content": f"上下文：\n{context}\n\n问题：{question}"}
            ],
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# ============ 使用示例 ============

if __name__ == "__main__":
    rag = AdvancedRAG()
    
    # 添加知识
    rag.add_documents([
        "FastAPI是一个现代、快速的Python Web框架。它基于Starlette和Pydantic。",
        "FastAPI的性能非常出色，benchmark测试显示其QPS可达到10000+，与Go和Node.js相当。",
        "FastAPI自动生成OpenAPI文档，支持Swagger UI和ReDoc。",
        "FastAPI使用Python类型提示进行数据验证，减少了大量样板代码。",
        "Django是一个全功能的Python Web框架，包含ORM、管理后台、认证系统等。",
        "Flask是一个轻量级的Python微框架，适合小型项目和API开发。"
    ])
    
    # 查询
    result = rag.query("FastAPI的性能怎么样？和其他框架相比如何？")
    
    print("回答:", result["answer"])
    print(f"\n使用了 {len(result['sources'])} 个文档")
    print(f"上下文长度: {result['context_length']} 字符")
    print(f"步骤: {result['steps']}")
```

---

## 3. FastAPI接口

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Advanced RAG API")
rag = AdvancedRAG()

class QueryRequest(BaseModel):
    question: str
    enable_rewrite: bool = True
    enable_rerank: bool = True
    enable_compress: bool = True

@app.post("/query")
async def query(request: QueryRequest):
    result = rag.query(
        request.question,
        enable_rewrite=request.enable_rewrite,
        enable_rerank=request.enable_rerank,
        enable_compress=request.enable_compress
    )
    return result

@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    def generate():
        for text in rag.query_stream(request.question):
            yield f"data: {text}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 4. 性能优化

### 4.1 批量Embedding

```python
# 批量处理而非逐个
embeddings = model.encode(texts, batch_size=32)
```

### 4.2 模型缓存

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_reranker():
    return CrossEncoder('...')
```

### 4.3 异步处理

```python
import asyncio

async def async_query(rag, questions):
    tasks = [asyncio.to_thread(rag.query, q) for q in questions]
    return await asyncio.gather(*tasks)
```

---

## 📺 推荐B站视频

搜索：
- **"RAG 生产级 架构"**
- **"高级RAG Pipeline"**
- **"RAG 性能优化"**

---

## 5. 继续学习

🎉 **恭喜完成Week 5！**

📌 **Week 5 学习顺序**：
1. ✅ 混合检索
2. ✅ 重排序模型
3. ✅ 上下文压缩
4. ✅ 高级RAG Pipeline（本教程）

继续前往 **Week 6** 学习AI Agent！

---

**你已掌握生产级RAG技术！💪**
