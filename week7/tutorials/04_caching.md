# 🚀 缓存策略与性能优化

> **学习目标**：掌握企业级RAG系统的缓存设计和性能优化技术

---

## 🎯 为什么需要缓存？

### RAG系统的性能瓶颈

```
用户查询
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline 耗时分析                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Embedding计算      ████████████  ~100-300ms                    │
│  向量检索           ████████      ~50-200ms                      │
│  重排序             ██████████████████  ~200-500ms              │
│  LLM生成            ████████████████████████████  ~500-3000ms   │
│                                                                  │
│  总计               ~1-4秒/请求                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

问题：相同问题重复计算，浪费资源
解决：多层缓存策略
```

---

## 📚 多层缓存架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    多层缓存架构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  用户请求                                                        │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────┐                                           │
│  │   L1: 结果缓存    │ ← 命中率最高，直接返回答案                │
│  │   (Redis)        │   TTL: 1小时                               │
│  └────────┬─────────┘                                           │
│           │ miss                                                 │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │   L2: 检索缓存    │ ← 缓存检索结果，跳过向量搜索              │
│  │   (Redis)        │   TTL: 6小时                               │
│  └────────┬─────────┘                                           │
│           │ miss                                                 │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │   L3: Embedding  │ ← 缓存向量，跳过Embedding计算              │
│  │   (Redis/本地)   │   TTL: 24小时                              │
│  └────────┬─────────┘                                           │
│           │ miss                                                 │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │   完整RAG流程    │ ← 无缓存，执行完整流程                     │
│  └──────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 实现多层缓存

### 1. 缓存管理器

```python
import redis
import json
import hashlib
from typing import Optional, Any
from dataclasses import dataclass
import pickle

@dataclass
class CacheConfig:
    """缓存配置"""
    result_ttl: int = 3600      # 结果缓存 1小时
    retrieval_ttl: int = 21600  # 检索缓存 6小时
    embedding_ttl: int = 86400  # Embedding缓存 24小时

class CacheManager:
    """多层缓存管理器"""
    
    def __init__(self, redis_url: str, config: CacheConfig = None):
        self.redis = redis.from_url(redis_url)
        self.config = config or CacheConfig()
    
    def _hash_key(self, *args) -> str:
        """生成缓存键"""
        content = json.dumps(args, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    # ========== L1: 结果缓存 ==========
    async def get_result(self, query: str, tenant_id: str) -> Optional[dict]:
        """获取缓存的结果"""
        key = f"result:{tenant_id}:{self._hash_key(query)}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_result(self, query: str, tenant_id: str, result: dict):
        """缓存结果"""
        key = f"result:{tenant_id}:{self._hash_key(query)}"
        self.redis.setex(key, self.config.result_ttl, json.dumps(result))
    
    # ========== L2: 检索缓存 ==========
    async def get_retrieval(self, query: str, tenant_id: str) -> Optional[list]:
        """获取缓存的检索结果"""
        key = f"retrieval:{tenant_id}:{self._hash_key(query)}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_retrieval(self, query: str, tenant_id: str, docs: list):
        """缓存检索结果"""
        key = f"retrieval:{tenant_id}:{self._hash_key(query)}"
        self.redis.setex(key, self.config.retrieval_ttl, json.dumps(docs))
    
    # ========== L3: Embedding缓存 ==========
    async def get_embedding(self, text: str) -> Optional[list]:
        """获取缓存的Embedding"""
        key = f"embedding:{self._hash_key(text)}"
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    async def set_embedding(self, text: str, embedding: list):
        """缓存Embedding"""
        key = f"embedding:{self._hash_key(text)}"
        self.redis.setex(key, self.config.embedding_ttl, pickle.dumps(embedding))
    
    # ========== 缓存失效 ==========
    async def invalidate_tenant(self, tenant_id: str):
        """失效租户所有缓存"""
        pattern = f"*:{tenant_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    async def invalidate_by_pattern(self, pattern: str):
        """按模式失效缓存"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### 2. 带缓存的RAG引擎

```python
class CachedRAGEngine:
    """带缓存的RAG引擎"""
    
    def __init__(
        self,
        rag_engine,
        cache_manager: CacheManager,
        enable_cache: bool = True
    ):
        self.engine = rag_engine
        self.cache = cache_manager
        self.enable_cache = enable_cache
        self.stats = {"hits": 0, "misses": 0}
    
    async def query(
        self,
        question: str,
        tenant_id: str,
        skip_cache: bool = False
    ) -> dict:
        """带缓存的查询"""
        
        if not self.enable_cache or skip_cache:
            return await self.engine.query(question, tenant_id)
        
        # L1: 检查结果缓存
        cached_result = await self.cache.get_result(question, tenant_id)
        if cached_result:
            self.stats["hits"] += 1
            cached_result["from_cache"] = True
            return cached_result
        
        self.stats["misses"] += 1
        
        # L2: 检查检索缓存
        cached_docs = await self.cache.get_retrieval(question, tenant_id)
        
        if cached_docs:
            # 使用缓存的检索结果，只调用LLM
            result = await self.engine.generate_with_docs(
                question, cached_docs
            )
        else:
            # 执行完整RAG流程
            result = await self.engine.query(question, tenant_id)
            
            # 缓存检索结果
            await self.cache.set_retrieval(
                question, tenant_id, result.get("sources", [])
            )
        
        # 缓存最终结果
        await self.cache.set_result(question, tenant_id, result)
        result["from_cache"] = False
        
        return result
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        return {
            **self.stats,
            "hit_rate": f"{hit_rate:.2%}"
        }
```

### 3. 语义缓存（高级）

```python
import numpy as np

class SemanticCache:
    """语义缓存 - 相似问题复用答案"""
    
    def __init__(
        self,
        embedding_client,
        cache_manager: CacheManager,
        similarity_threshold: float = 0.95
    ):
        self.embedder = embedding_client
        self.cache = cache_manager
        self.threshold = similarity_threshold
        
        # 内存索引（生产环境应使用持久化存储）
        self.query_embeddings: dict[str, list] = {}
        self.query_results: dict[str, dict] = {}
    
    async def get_similar(
        self,
        query: str,
        tenant_id: str
    ) -> Optional[dict]:
        """查找语义相似的缓存结果"""
        
        # 获取查询embedding
        query_embedding = await self._get_embedding(query)
        
        # 遍历缓存查找相似项
        best_match = None
        best_score = self.threshold
        
        for cached_query, cached_embedding in self.query_embeddings.items():
            if not cached_query.startswith(f"{tenant_id}:"):
                continue
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, cached_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_match = cached_query
        
        if best_match:
            result = self.query_results.get(best_match)
            if result:
                result["semantic_match"] = True
                result["similarity_score"] = best_score
                return result
        
        return None
    
    async def set(self, query: str, tenant_id: str, result: dict):
        """缓存查询结果"""
        query_key = f"{tenant_id}:{query}"
        embedding = await self._get_embedding(query)
        
        self.query_embeddings[query_key] = embedding
        self.query_results[query_key] = result
    
    async def _get_embedding(self, text: str) -> list:
        """获取文本embedding（带缓存）"""
        cached = await self.cache.get_embedding(text)
        if cached:
            return cached
        
        embedding = await self.embedder.embed(text)
        await self.cache.set_embedding(text, embedding)
        return embedding
    
    def _cosine_similarity(self, a: list, b: list) -> float:
        """计算余弦相似度"""
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## 📊 性能优化技巧

### 1. 批量处理

```python
class BatchProcessor:
    """批量处理器 - 减少API调用"""
    
    def __init__(self, embedding_client, batch_size: int = 32):
        self.client = embedding_client
        self.batch_size = batch_size
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成Embedding"""
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self.client.embed_many(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
```

### 2. 异步并发

```python
import asyncio

class ParallelRAG:
    """并行RAG - 并发执行多个检索"""
    
    async def query_with_parallel_retrieval(
        self,
        question: str,
        collections: list[str]
    ) -> dict:
        """并行检索多个集合"""
        
        # 并行检索
        tasks = [
            self._retrieve_from_collection(question, collection)
            for collection in collections
        ]
        results = await asyncio.gather(*tasks)
        
        # 合并结果
        all_docs = []
        for docs in results:
            all_docs.extend(docs)
        
        # 去重和排序
        unique_docs = self._deduplicate(all_docs)
        
        return {"documents": unique_docs}
```

### 3. 流式响应

```python
from fastapi.responses import StreamingResponse

async def stream_rag_response(question: str, rag_engine):
    """流式RAG响应"""
    
    # 先检索
    docs = await rag_engine.retrieve(question)
    context = "\n".join(docs)
    
    # 流式生成
    async for chunk in rag_engine.llm.stream_chat(question, context):
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    yield "data: [DONE]\n\n"

@app.get("/api/chat/stream")
async def chat_stream(question: str):
    return StreamingResponse(
        stream_rag_response(question, rag_engine),
        media_type="text/event-stream"
    )
```

---

## 📊 学习检查清单

- [ ] 理解多层缓存架构
- [ ] 能够实现结果缓存和检索缓存
- [ ] 了解语义缓存的原理
- [ ] 掌握批量处理和并发优化

---

## 🎯 下一步

继续学习：
👉 [云平台部署](./05_deployment.md)
