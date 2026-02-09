# 📘 第4周：RAG系统基础

> **学习目标**：掌握RAG（检索增强生成）核心技术，构建个人知识库问答系统

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解RAG系统的架构和原理
- ✅ 使用Embedding模型将文本向量化
- ✅ 掌握向量数据库的使用（ChromaDB / Milvus 双路线）
- ✅ 实现简单的语义检索
- ✅ 构建个人知识库问答系统

---

## 🤔 什么是RAG？

**RAG (Retrieval-Augmented Generation)** = 检索 + 生成

```
用户问题: "FastAPI如何实现依赖注入？"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  1. 检索（Retrieval）                                        │
│     将问题向量化 → 在知识库中搜索相关文档                      │
│     找到：fastapi_docs.md 中关于 Depends 的章节              │
├─────────────────────────────────────────────────────────────┤
│  2. 增强（Augmented）                                        │
│     将检索到的文档 + 用户问题组合成Prompt                     │
├─────────────────────────────────────────────────────────────┤
│  3. 生成（Generation）                                       │
│     LLM根据上下文生成准确的回答                              │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
回答: "FastAPI使用Depends实现依赖注入，例如..."
```

### RAG vs 直接问LLM

| 对比 | 直接问LLM | 使用RAG |
|------|-----------|---------|
| 知识更新 | 训练截止日期后的内容不知道 | 可以使用最新文档 |
| 私有数据 | 无法访问你的文档 | 可以检索私有知识库 |
| 准确性 | 可能产生幻觉 | 基于真实文档，更准确 |
| 可溯源 | 无法引用来源 | 可以标注信息来源 |

---

## 📚 学习路径

### Day 1：Embedding基础

#### 📖 教程材料
- [Embedding向量化入门](./tutorials/01_embedding_basics.md) ✅

**学习内容**：
- 什么是文本Embedding？
- OpenAI/DeepSeek Embedding API
- 本地Embedding模型（BGE、M3E）
- 向量相似度计算

#### 💻 快速示例
```python
from openai import OpenAI

client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="your-key")

# 获取文本的向量表示
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="FastAPI是一个现代Python Web框架"
)

embedding = response.data[0].embedding
print(f"向量维度: {len(embedding)}")  # 1536
```

---

### Day 2-3：向量数据库

#### 📖 教程材料 - 双路线选择

**路线A：ChromaDB（推荐入门）**
- [ChromaDB快速入门](./tutorials/02a_chromadb.md) ✅

```python
import chromadb

# 创建客户端
client = chromadb.Client()
collection = client.create_collection("my_docs")

# 添加文档
collection.add(
    documents=["FastAPI是高性能框架", "Pydantic用于数据验证"],
    ids=["doc1", "doc2"]
)

# 查询
results = collection.query(query_texts=["什么是FastAPI"], n_results=1)
print(results["documents"])
```

**路线B：Milvus（生产级）**
- [Milvus向量数据库](./tutorials/02b_milvus.md) ✅

```python
from pymilvus import connections, Collection

# 连接Milvus
connections.connect(host="localhost", port="19530")

# 创建集合并插入向量
# ...更复杂但更强大
```

#### 对比选择

| 特性 | ChromaDB | Milvus |
|------|----------|--------|
| 安装 | pip install | Docker部署 |
| 学习曲线 | 简单 | 中等 |
| 适用场景 | 原型/小规模 | 生产/大规模 |
| 性能 | 中等 | 高 |

---

### Day 4：检索策略

#### 📖 教程材料
- [检索策略详解](./tutorials/03_retrieval_strategies.md) ✅

**学习内容**：
- 语义检索 vs 关键词检索
- Top-K检索
- 相似度阈值设置
- 检索结果过滤

#### 💻 检索示例
```python
def semantic_search(query: str, collection, top_k: int = 5):
    """语义检索"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "distances", "metadatas"]
    )
    
    # 过滤相似度太低的结果
    filtered = []
    for doc, distance in zip(results["documents"][0], results["distances"][0]):
        if distance < 0.5:  # 距离阈值
            filtered.append(doc)
    
    return filtered
```

---

### Day 5：简单RAG实现

#### 📖 教程材料
- [构建简单RAG系统](./tutorials/04_simple_rag.md) ✅

**学习内容**：
- 文档加载与分块
- 向量化与存储
- 检索与生成整合
- 完整RAG Pipeline

#### 💻 RAG Pipeline
```python
class SimpleRAG:
    def __init__(self, collection, llm_client):
        self.collection = collection
        self.client = llm_client
    
    def query(self, question: str) -> str:
        # 1. 检索相关文档
        docs = self.collection.query(
            query_texts=[question],
            n_results=3
        )["documents"][0]
        
        # 2. 构建Prompt
        context = "\n".join(docs)
        prompt = f"""基于以下文档回答问题：

文档内容：
{context}

问题：{question}

请基于上述文档回答，如果文档中没有相关信息，请说明。"""
        
        # 3. 生成回答
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

# 使用
rag = SimpleRAG(collection, client)
answer = rag.query("FastAPI如何定义路由？")
print(answer)
```

---

### Day 6：检索增强技术 【🆕 新增】

#### 📖 教程材料
- [查询变换技术 - HyDE与Multi-Query](./tutorials/05_query_transformation.md) ✅
- [父文档检索器](./tutorials/06_parent_document_retriever.md) ✅

**学习内容**：
- Multi-Query：多查询扩展提高召回率
- HyDE：假设文档嵌入技术
- Step-Back Prompting：后退提示
- Parent Document Retriever：小块检索大块返回

#### 💻 Multi-Query示例
```python
class MultiQueryRetriever:
    """多查询检索器"""
    
    async def generate_queries(self, query: str) -> list[str]:
        """生成多个相关查询"""
        # "FastAPI怎么限流" -> [
        #     "FastAPI rate limiting 实现",
        #     "FastAPI 请求频率限制",
        #     "slowapi 使用教程"
        # ]
        ...
    
    async def retrieve(self, query: str) -> list[dict]:
        queries = await self.generate_queries(query)
        # 分别检索并合并去重
        ...
```

---

### Day 7：实战项目

#### 🚀 项目：个人知识库问答系统

**功能需求**：
- 📁 上传Markdown/PDF文档
- 🔍 自动分块和向量化
- 💬 自然语言问答
- 📊 显示引用来源

**项目结构**：
```
projects/knowledge_qa/
├── app.py           # FastAPI应用
├── rag.py           # RAG核心逻辑
├── vectorstore.py   # 向量数据库封装
├── document.py      # 文档处理
└── frontend/        # 简单Web界面
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | RAG从入门到精通 | https://www.bilibili.com/video/BV1xK411o7aG |
| 跟李沐学AI | 向量数据库原理 | https://www.bilibili.com/video/BV1om4y1A72P |
| DataWhale | ChromaDB实战教程 | https://www.bilibili.com/video/BV1Sp4y1s7Pt |

---

## 📊 学习检查清单

### Embedding
- [ ] 理解Embedding的概念和用途
- [ ] 会使用API获取文本向量
- [ ] 了解常用的Embedding模型

### 向量数据库
- [ ] 能够创建集合和插入数据
- [ ] 会执行相似度查询
- [ ] 理解距离度量（余弦相似度等）

### RAG系统
- [ ] 理解RAG的工作流程
- [ ] 能够实现简单的RAG Pipeline
- [ ] 会进行文档分块处理

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 5: RAG系统进阶](../week5/README.md)

---

**RAG让AI能够使用你的专属知识库！💪**
