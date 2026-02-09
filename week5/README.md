# 📘 第5周：RAG系统进阶

> **学习目标**：掌握高级RAG技术，包括混合检索、重排序和上下文压缩

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 实现混合检索（语义+关键词）
- ✅ 使用重排序模型（Reranker）优化结果
- ✅ 掌握上下文压缩技术
- ✅ 处理长文档和多文档场景
- ✅ 构建企业级文档检索系统

---

## 📚 学习路径

### Day 1：混合检索

#### 📖 教程材料 - 双路线
**路线A：原生实现**
- [混合检索原理与实现](./tutorials/01a_hybrid_search_native.md) ✅

**路线B：LangChain实现**
- [使用LangChain构建混合检索](./tutorials/01b_hybrid_search_langchain.md) ✅

**核心概念**：
```
混合检索 = 语义检索 + 关键词检索

查询: "FastAPI依赖注入"
        │
   ┌────┴────┐
   ▼         ▼
语义检索   关键词检索(BM25)
   │         │
   └────┬────┘
        ▼
   融合排序(RRF)
        │
        ▼
   最终结果
```

#### 💻 原生实现示例
```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearch:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings
        
        # BM25索引
        tokenized = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def search(self, query: str, query_embedding: list, alpha: float = 0.5):
        # 语义检索得分
        semantic_scores = np.dot(self.embeddings, query_embedding)
        
        # BM25得分
        bm25_scores = self.bm25.get_scores(query.split())
        
        # 归一化并融合
        semantic_norm = (semantic_scores - semantic_scores.min()) / (semantic_scores.max() - semantic_scores.min())
        bm25_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min())
        
        # 加权融合
        final_scores = alpha * semantic_norm + (1 - alpha) * bm25_norm
        
        # 返回Top-K
        top_indices = np.argsort(final_scores)[-5:][::-1]
        return [(self.documents[i], final_scores[i]) for i in top_indices]
```

---

### Day 2：重排序（Reranking）

#### 📖 教程材料
- [重排序模型详解](./tutorials/02_reranking.md) ✅

**为什么需要重排序？**
- 初次检索（召回）追求高召回率
- 重排序追求高精确率
- 两阶段流程：召回 → 精排

#### 💻 使用BGE Reranker
```python
from FlagEmbedding import FlagReranker

# 加载重排序模型
reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True)

# 原始检索结果
query = "FastAPI如何处理请求？"
passages = [
    "FastAPI使用async/await处理异步请求",
    "Django是Python的Web框架",
    "FastAPI的请求处理基于Starlette"
]

# 重排序
pairs = [[query, p] for p in passages]
scores = reranker.compute_score(pairs)

# 按分数排序
ranked = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
for doc, score in ranked:
    print(f"{score:.4f}: {doc}")
```

**在线Reranker API**：
```python
# 使用Cohere Rerank API
import cohere

co = cohere.Client("your-api-key")
results = co.rerank(
    query="FastAPI请求处理",
    documents=passages,
    model="rerank-multilingual-v2.0"
)
```

---

### Day 3：上下文压缩

#### 📖 教程材料
- [上下文压缩技术](./tutorials/03_context_compression.md) ✅

**问题**：检索到的文档往往很长，包含很多无关内容

**解决**：上下文压缩 - 只保留与问题相关的部分

#### 💻 压缩实现
```python
async def compress_context(query: str, documents: list[str], client) -> str:
    """使用LLM压缩上下文"""
    prompt = f"""从以下文档中提取与问题相关的关键信息。只保留直接相关的内容。

问题：{query}

文档：
{chr(10).join(documents)}

请提取关键信息（不超过500字）："""
    
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    return response.choices[0].message.content

# 使用
compressed = await compress_context(
    "FastAPI路由定义",
    ["很长的文档1...", "很长的文档2..."],
    client
)
```

---

### Day 4：高级RAG架构

#### 📖 教程材料 - 双路线
**路线A：原生实现**
- [高级RAG Pipeline原生实现](./tutorials/04a_advanced_rag_native.md) ✅

**路线B：LangChain实现**
- [LangChain高级RAG](./tutorials/04b_advanced_rag_langchain.md) ✅

#### 架构图
```
            ┌─────────────────────────────────────────┐
            │           Advanced RAG Pipeline          │
            └─────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────────┐
            │         1. 查询理解与改写                │
            │   - 意图识别                            │
            │   - 查询扩展（Query Expansion）          │
            │   - 假设文档生成（HyDE）                 │
            └─────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────────┐
            │         2. 混合检索（Hybrid）            │
            │   - 语义检索（Dense）                   │
            │   - 关键词检索（Sparse/BM25）           │
            │   - 融合排序（RRF）                     │
            └─────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────────┐
            │         3. 重排序（Reranking）           │
            │   - Cross-Encoder重排                   │
            │   - 多样性过滤                          │
            └─────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────────┐
            │         4. 上下文处理                    │
            │   - 上下文压缩                          │
            │   - 上下文增强                          │
            └─────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────────┐
            │         5. 生成与后处理                  │
            │   - 引用标注                            │
            │   - 幻觉检测                            │
            └─────────────────────────────────────────┘
```

---

### Day 5-6：2025-2026最新RAG技术 【🆕 新增】

#### 📖 教程材料
- [Corrective RAG与Self-Reflective RAG](./tutorials/05_corrective_rag.md) ✅
- [GraphRAG - 知识图谱增强检索](./tutorials/06_graphrag.md) ✅
- [Agentic RAG - Agent驱动的智能检索](./tutorials/07_agentic_rag.md) ✅

**核心技术**：

| 技术 | 解决的问题 | 核心思想 |
|------|-----------|----------|
| CRAG | 检索质量不可靠 | 评估→修正→重试 |
| Self-RAG | 回答可能有幻觉 | 生成→反思→迭代 |
| GraphRAG | 多跳推理困难 | 知识图谱+向量检索 |
| Agentic RAG | 固定Pipeline不灵活 | Agent自主决策检索 |

#### 💻 Agentic RAG示例
```python
class AgenticRAGAgent:
    """Agent自主决定何时检索、检索什么"""
    
    async def query(self, question: str):
        # Agent思考：需要检索吗？检索哪个知识库？
        # Agent可能调用：vector_search, graph_query, web_search
        # Agent评估：结果够用吗？需要重试吗？
        # 最终给出高质量回答
        ...
```

> [!TIP]
> **Agentic RAG是进入Week6 Agent的重要铺垫！**
> 它引入了Agent的核心概念：工具调用、自主决策、思考-行动-观察循环。

---

### Day 7：实战项目

#### 🚀 项目：企业文档智能检索系统

**功能需求**：
- 📁 支持多种文档格式（PDF、Word、Markdown）
- 🔍 混合检索 + 重排序
- 💬 多轮对话支持
- 📊 检索质量评估
- 🔐 权限控制

**技术选型**：

| 组件 | 路线A（简单） | 路线B（生产级） |
|------|--------------|----------------|
| 向量库 | ChromaDB | Milvus |
| 框架 | 原生Python | LangChain |
| 重排序 | BGE Reranker | Cohere API |
| 部署 | Docker单机 | Kubernetes |

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | RAG进阶技术详解 | https://www.bilibili.com/video/BV1xK411o7aG |
| 跟李沐学AI | Reranker原理与实战 | https://www.bilibili.com/video/BV1om4y1A72P |
| DataWhale | LangChain RAG实战 | https://www.bilibili.com/video/BV1Sp4y1s7Pt |

---

## 📊 学习检查清单

### 混合检索
- [ ] 理解语义检索和关键词检索的区别
- [ ] 能够实现RRF融合算法
- [ ] 会调整混合检索权重

### 重排序
- [ ] 理解两阶段检索架构
- [ ] 会使用BGE Reranker
- [ ] 了解在线Reranker服务

### 上下文压缩
- [ ] 理解为什么需要压缩
- [ ] 能够实现LLM压缩方法
- [ ] 会控制上下文长度

### 高级RAG
- [ ] 理解完整的RAG Pipeline
- [ ] 会实现查询改写
- [ ] 能够进行RAG质量评估

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 6: 智能体入门](../week6/README.md)

> [!IMPORTANT]
> **Week5→Week6 过渡提示**
>
> 你在本周学到的 **Agentic RAG** 中的工具调用和自主决策机制，
> 正是Week6 Agent系统的核心能力！继续前进，探索更强大的智能体世界。

---

**高级RAG技术让检索更精准、回答更可靠！💪**
