# 📘 查询变换技术 - HyDE与Multi-Query

> **学习目标**：掌握查询变换技术，提升RAG检索效果

---

## 🎯 为什么需要查询变换？

### 用户查询的问题

```
用户查询: "FastAPI怎么限流"

问题:
1. 查询太简短，语义信息不足
2. 与文档表述不匹配（文档可能写"速率限制"、"Rate Limiting"）
3. 单一查询可能遗漏相关信息

解决方案: 查询变换
```

---

## 📚 三种主要查询变换技术

### 技术概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    查询变换技术                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Multi-Query（多查询扩展）                                     │
│     原始查询 → 生成多个相关查询 → 分别检索 → 合并结果             │
│                                                                  │
│  2. HyDE（假设文档嵌入）                                          │
│     原始查询 → 生成假设答案 → 用假设答案检索 → 找到真实文档       │
│                                                                  │
│  3. Step-Back Prompting（后退提示）                               │
│     原始查询 → 生成更抽象的问题 → 先回答抽象问题 → 再回答原问题   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Multi-Query 实现

### 原理

```
原始查询: "FastAPI怎么限流"
              │
              ▼
         LLM生成多个查询:
         ├── "FastAPI rate limiting 实现方法"
         ├── "FastAPI 请求频率限制中间件"
         ├── "FastAPI slowapi 使用教程"
         └── "如何防止FastAPI API被滥用"
              │
              ▼
       分别在向量库中检索
              │
              ▼
         合并去重结果
```

### 代码实现

```python
from openai import OpenAI
from typing import Optional

class MultiQueryRetriever:
    """多查询检索器"""
    
    def __init__(self, client: OpenAI, vector_store, num_queries: int = 4):
        self.client = client
        self.vector_store = vector_store
        self.num_queries = num_queries
        
        self.generation_prompt = """你是一个查询扩展专家。

用户的原始查询: {query}

请生成{num}个不同角度的相关查询，用于在知识库中搜索更全面的信息。
要求:
1. 每个查询应该从不同角度描述同一个问题
2. 使用不同的关键词和表述方式
3. 包含可能的同义词和相关术语

返回JSON格式:
{{"queries": ["查询1", "查询2", ...]}}
"""
    
    async def generate_queries(self, query: str) -> list[str]:
        """生成多个查询"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.generation_prompt.format(
                    query=query,
                    num=self.num_queries
                )
            }],
            response_format={"type": "json_object"},
            temperature=0.7  # 适度创造性
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return [query] + result.get("queries", [])  # 包含原始查询
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """执行多查询检索"""
        # 生成多个查询
        queries = await self.generate_queries(query)
        
        # 对每个查询进行检索
        all_results = {}
        
        for q in queries:
            results = self.vector_store.query(
                query_texts=[q],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 合并结果（使用文档ID去重）
            for i, doc_id in enumerate(results["ids"][0]):
                if doc_id not in all_results:
                    all_results[doc_id] = {
                        "id": doc_id,
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "min_distance": results["distances"][0][i],
                        "matched_queries": [q]
                    }
                else:
                    # 更新最小距离和匹配查询
                    all_results[doc_id]["min_distance"] = min(
                        all_results[doc_id]["min_distance"],
                        results["distances"][0][i]
                    )
                    all_results[doc_id]["matched_queries"].append(q)
        
        # 按匹配查询数量和距离排序
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: (-len(x["matched_queries"]), x["min_distance"])
        )
        
        return sorted_results[:top_k]


# 使用示例
async def demo_multi_query():
    client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="your-key")
    
    retriever = MultiQueryRetriever(client, vector_store)
    
    results = await retriever.retrieve("FastAPI怎么限流")
    
    print("生成的查询:")
    for r in results[:3]:
        print(f"  文档: {r['document'][:100]}...")
        print(f"  匹配查询数: {len(r['matched_queries'])}")
```

---

## 💻 HyDE 实现

### 原理

```
原始查询: "FastAPI怎么限流"
              │
              ▼
         LLM生成假设答案:
         "FastAPI可以使用slowapi库实现限流。首先pip install slowapi，
          然后创建Limiter实例..."
              │
              ▼
         用假设答案的Embedding检索
         (假设答案的语义更接近真实文档)
              │
              ▼
         返回真实文档
```

### 代码实现

```python
class HyDERetriever:
    """HyDE (Hypothetical Document Embeddings) 检索器"""
    
    def __init__(self, client: OpenAI, vector_store, embedding_model=None):
        self.client = client
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        
        self.hyde_prompt = """你是一个技术文档专家。

用户问题: {query}

请写一段技术文档内容，直接回答这个问题。
要求:
1. 写法要像真正的技术文档/教程
2. 包含具体的技术细节和代码示例
3. 不要以问答形式，而是以教程/文档形式

文档内容:"""
    
    async def generate_hypothetical_document(self, query: str) -> str:
        """生成假设文档"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.hyde_prompt.format(query=query)
            }],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def get_embedding(self, text: str) -> list[float]:
        """获取文本向量"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",  # 或其他embedding模型
            input=text
        )
        return response.data[0].embedding
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """使用HyDE进行检索"""
        # Step 1: 生成假设文档
        hypothetical_doc = await self.generate_hypothetical_document(query)
        
        # Step 2: 用假设文档进行检索
        # ChromaDB会自动计算embedding
        results = self.vector_store.query(
            query_texts=[hypothetical_doc],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        return {
            "hypothetical_document": hypothetical_doc,
            "retrieved_documents": [
                {
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i]
                }
                for i in range(len(results["documents"][0]))
            ]
        }


# 使用示例
async def demo_hyde():
    client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="your-key")
    
    retriever = HyDERetriever(client, vector_store)
    
    result = await retriever.retrieve("FastAPI怎么限流")
    
    print("假设文档:")
    print(result["hypothetical_document"][:300])
    print("\n检索到的真实文档:")
    for doc in result["retrieved_documents"][:2]:
        print(f"  - {doc['document'][:100]}...")
```

---

## 💻 Step-Back Prompting 实现

### 原理

```
原始查询: "FastAPI 0.100.0版本的路由装饰器有什么变化"
              │
              ▼
         生成抽象问题:
         "FastAPI路由系统的设计和演进"
              │
              ▼
         先检索抽象问题相关文档
         获得背景知识
              │
              ▼
         结合背景知识回答原始具体问题
```

### 代码实现

```python
class StepBackRetriever:
    """Step-Back Prompting 检索器"""
    
    def __init__(self, client: OpenAI, vector_store):
        self.client = client
        self.vector_store = vector_store
        
        self.stepback_prompt = """你是一个问题抽象专家。

原始问题: {query}

请将这个具体问题抽象为一个更一般性的问题。
这个抽象问题应该能帮助理解原始问题所需的背景知识。

例如:
- "Python 3.11的match语句性能如何" → "Python模式匹配的设计和实现原理"
- "React 18的useTransition怎么用" → "React并发渲染的概念和机制"

返回JSON格式:
{{"abstract_question": "抽象后的问题"}}
"""
    
    async def generate_stepback_question(self, query: str) -> str:
        """生成抽象问题"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.stepback_prompt.format(query=query)
            }],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("abstract_question", query)
    
    async def retrieve(self, query: str, top_k: int = 5) -> dict:
        """执行Step-Back检索"""
        # 生成抽象问题
        abstract_query = await self.generate_stepback_question(query)
        
        # 检索抽象问题的相关文档（背景知识）
        background_results = self.vector_store.query(
            query_texts=[abstract_query],
            n_results=top_k // 2
        )
        
        # 检索原始问题的相关文档（具体信息）
        specific_results = self.vector_store.query(
            query_texts=[query],
            n_results=top_k // 2
        )
        
        return {
            "original_query": query,
            "stepback_query": abstract_query,
            "background_docs": background_results["documents"][0],
            "specific_docs": specific_results["documents"][0]
        }
```

---

## 🎯 技术选择指南

| 场景 | 推荐技术 | 原因 |
|-----|---------|------|
| 用户表述多样 | Multi-Query | 覆盖不同表述方式 |
| 查询与文档表述差异大 | HyDE | 假设答案更接近文档 |
| 需要背景知识 | Step-Back | 先理解概念再回答 |
| 综合使用 | 组合方案 | 取长补短 |

---

## 💻 组合使用示例

```python
class AdvancedRetriever:
    """高级检索器 - 组合多种查询变换技术"""
    
    def __init__(self, client: OpenAI, vector_store):
        self.multi_query = MultiQueryRetriever(client, vector_store)
        self.hyde = HyDERetriever(client, vector_store)
        self.stepback = StepBackRetriever(client, vector_store)
    
    async def retrieve(
        self, 
        query: str, 
        strategy: str = "auto",
        top_k: int = 5
    ) -> list[str]:
        """智能选择检索策略"""
        
        if strategy == "auto":
            # 根据查询特点自动选择
            if len(query) < 10:
                strategy = "multi_query"  # 短查询用多查询扩展
            elif "版本" in query or "变化" in query:
                strategy = "stepback"     # 版本相关用Step-Back
            else:
                strategy = "hyde"          # 默认用HyDE
        
        if strategy == "multi_query":
            results = await self.multi_query.retrieve(query, top_k)
            return [r["document"] for r in results]
        
        elif strategy == "hyde":
            results = await self.hyde.retrieve(query, top_k)
            return [r["document"] for r in results["retrieved_documents"]]
        
        elif strategy == "stepback":
            results = await self.stepback.retrieve(query, top_k)
            return results["background_docs"] + results["specific_docs"]
        
        else:
            raise ValueError(f"未知策略: {strategy}")
```

---

## 📊 学习检查清单

- [ ] 理解用户查询与文档不匹配的问题
- [ ] 掌握Multi-Query的原理和实现
- [ ] 掌握HyDE（假设文档嵌入）的原理和实现
- [ ] 了解Step-Back Prompting的使用场景
- [ ] 能够根据场景选择合适的查询变换技术

---

## 🎯 下一步

继续学习：
👉 [父文档检索器](./06_parent_document_retriever.md)
