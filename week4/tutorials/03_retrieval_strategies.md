# 🎯 检索策略详解

> **学习目标**：掌握语义检索的核心策略和优化技巧

---

## 1. 检索的重要性

RAG系统的效果 = 检索质量 × 生成质量

**如果检索不到相关文档，LLM再强也无法生成正确答案！**

---

## 2. Top-K检索

### 2.1 基础Top-K

```python
def basic_topk_search(collection, query: str, k: int = 5):
    """基础Top-K检索"""
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results["documents"][0]

# 使用
docs = basic_topk_search(collection, "Python Web框架", k=3)
```

### 2.2 K值选择

| K值 | 优点 | 缺点 |
|-----|------|------|
| 小 (1-3) | 精确，省token | 可能遗漏 |
| 中 (5-10) | 平衡 | 适中 |
| 大 (15+) | 覆盖全 | 噪音多，费token |

**建议**：先检索较多(10-20)，再用重排序筛选。

---

## 3. 相似度阈值过滤

### 3.1 距离阈值

```python
def search_with_threshold(collection, query: str, threshold: float = 0.5):
    """带阈值的检索"""
    results = collection.query(
        query_texts=[query],
        n_results=20,  # 先取多一些
        include=["documents", "distances"]
    )
    
    # 过滤掉距离太大的（相似度太低）
    filtered = []
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        if dist < threshold:
            filtered.append({"doc": doc, "distance": dist})
    
    return filtered

# 余弦距离: 0=完全相同, 2=完全相反
# 建议阈值: 0.3-0.7
```

### 3.2 动态阈值

```python
def dynamic_threshold_search(collection, query: str, min_results: int = 3):
    """动态调整阈值确保有足够结果"""
    thresholds = [0.3, 0.5, 0.7, 1.0]
    
    for threshold in thresholds:
        results = search_with_threshold(collection, query, threshold)
        if len(results) >= min_results:
            return results
    
    return results  # 返回最后的结果
```

---

## 4. 元数据过滤

### 4.1 预过滤（推荐）

```python
def filtered_search(collection, query: str, filters: dict):
    """先过滤再搜索"""
    results = collection.query(
        query_texts=[query],
        n_results=10,
        where=filters  # 元数据过滤
    )
    return results

# 使用
results = filtered_search(
    collection,
    query="Python框架",
    filters={"category": "web", "year": {"$gte": 2020}}
)
```

### 4.2 复杂条件

```python
# AND条件
where={
    "$and": [
        {"category": "tech"},
        {"language": "python"}
    ]
}

# OR条件
where={
    "$or": [
        {"category": "web"},
        {"category": "api"}
    ]
}

# 范围条件
where={
    "year": {"$gte": 2020, "$lte": 2024}
}

# 包含条件
where={
    "tags": {"$in": ["fastapi", "flask", "django"]}
}
```

---

## 5. 查询扩展

### 5.1 同义词扩展

```python
def expand_query_synonyms(query: str, synonyms: dict) -> list[str]:
    """使用同义词扩展查询"""
    queries = [query]
    
    for word, syns in synonyms.items():
        if word in query:
            for syn in syns:
                queries.append(query.replace(word, syn))
    
    return queries

# 使用
synonyms = {
    "API": ["接口", "服务端点"],
    "框架": ["framework", "库"],
    "高性能": ["快速", "高效"]
}

queries = expand_query_synonyms("高性能API框架", synonyms)
# ["高性能API框架", "快速API框架", "高性能接口框架", ...]
```

### 5.2 LLM查询改写

```python
async def rewrite_query(client, query: str) -> list[str]:
    """使用LLM改写查询"""
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user",
            "content": f"""请将以下搜索查询改写成3个不同的表达方式，保持语义相同：

查询：{query}

请直接输出3个改写后的查询，每行一个："""
        }],
        temperature=0.7
    )
    
    rewrites = response.choices[0].message.content.strip().split("\n")
    return [query] + rewrites[:3]

# 使用
queries = await rewrite_query(client, "Python Web开发")
# ["Python Web开发", "使用Python进行网站开发", "Python后端开发框架", ...]
```

### 5.3 多查询融合

```python
def multi_query_search(collection, queries: list[str], top_k: int = 5):
    """多查询搜索并融合结果"""
    all_results = {}
    
    for query in queries:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        for doc, dist in zip(results["documents"][0], results["distances"][0]):
            if doc not in all_results:
                all_results[doc] = []
            all_results[doc].append(dist)
    
    # 计算平均距离
    ranked = []
    for doc, distances in all_results.items():
        avg_dist = sum(distances) / len(distances)
        ranked.append({"doc": doc, "avg_distance": avg_dist, "count": len(distances)})
    
    # 按平均距离排序
    ranked.sort(key=lambda x: x["avg_distance"])
    return ranked[:top_k]
```

---

## 6. 分块检索策略

### 6.1 固定大小分块

```python
def chunk_fixed(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """固定大小分块"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

### 6.2 语义分块（按段落/章节）

```python
def chunk_by_paragraph(text: str) -> list[str]:
    """按段落分块"""
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]

def chunk_by_heading(text: str) -> list[str]:
    """按标题分块（Markdown）"""
    import re
    sections = re.split(r'\n#{1,3}\s+', text)
    return [s.strip() for s in sections if s.strip()]
```

### 6.3 检索时的上下文扩展

```python
def search_with_context(collection, query: str, context_size: int = 1):
    """检索并返回相邻chunks"""
    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=["documents", "metadatas"]
    )
    
    expanded = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunk_idx = meta.get("chunk_index", 0)
        source = meta.get("source", "")
        
        # 获取相邻chunks
        neighbors = collection.get(
            where={
                "$and": [
                    {"source": source},
                    {"chunk_index": {"$gte": chunk_idx - context_size}},
                    {"chunk_index": {"$lte": chunk_idx + context_size}}
                ]
            }
        )
        
        # 合并文本
        combined = " ".join(neighbors["documents"])
        expanded.append(combined)
    
    return expanded
```

---

## 7. 完整检索Pipeline

```python
class SmartRetriever:
    def __init__(self, collection, client):
        self.collection = collection
        self.client = client
    
    async def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: dict = None,
        expand_query: bool = True,
        threshold: float = 0.7
    ) -> list[dict]:
        """智能检索Pipeline"""
        
        # 1. 查询扩展
        if expand_query:
            queries = await self._expand_query(query)
        else:
            queries = [query]
        
        # 2. 多查询检索
        all_results = []
        for q in queries:
            results = self.collection.query(
                query_texts=[q],
                n_results=top_k * 2,
                where=filters,
                include=["documents", "distances", "metadatas"]
            )
            all_results.append(results)
        
        # 3. 融合去重
        merged = self._merge_results(all_results)
        
        # 4. 阈值过滤
        filtered = [r for r in merged if r["distance"] < threshold]
        
        # 5. 返回Top-K
        return filtered[:top_k]
    
    async def _expand_query(self, query: str) -> list[str]:
        # 实现查询扩展...
        return [query]
    
    def _merge_results(self, results_list) -> list[dict]:
        # 实现结果融合...
        merged = {}
        for results in results_list:
            for doc, dist, meta in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0]
            ):
                if doc not in merged or dist < merged[doc]["distance"]:
                    merged[doc] = {"doc": doc, "distance": dist, "metadata": meta}
        
        return sorted(merged.values(), key=lambda x: x["distance"])
```

---

## 📺 推荐B站视频

搜索：
- **"RAG 检索优化"**
- **"向量检索 策略"**
- **"语义搜索 实战"**

---

## 8. 继续学习

📌 **Week 4 学习顺序**：
1. ✅ Embedding向量化入门
2. ✅ ChromaDB或Milvus
3. ✅ 检索策略详解（本教程）
4. ➡️ 构建简单RAG系统

---

**好的检索策略是RAG成功的一半！💪**
