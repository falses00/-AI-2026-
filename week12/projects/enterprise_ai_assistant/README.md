# 🏢 企业AI助手平台项目

> **Week 12 毕业项目选项A** - 完整企业级AI应用

---

## 🎯 项目概述

构建一个生产级企业AI助手平台，综合运用12周所学技术：

| 技术模块 | 对应周次 | 应用场景 |
|---------|---------|---------|
| FastAPI + Pydantic | Week 1 | API后端 |
| LLM API调用 | Week 2 | 对话核心 |
| MCP协议 | Week 3 | 工具扩展 |
| RAG检索 | Week 4-5 | 知识问答 |
| Agent系统 | Week 6, 11 | 智能决策 |
| 企业架构 | Week 7 | 系统设计 |
| 多模态 | Week 8 | 图文理解 |
| 模型微调 | Week 9 | 领域适配 |
| UX设计 | Week 10 | 用户体验 |

---

## 📊 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                    企业AI助手平台架构                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌───────────────────────────────────────────────────────────┐  │
│   │                      前端层                                │  │
│   │   React/Vue + WebSocket + 文件上传 + 语音输入             │  │
│   └───────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              ▼                                    │
│   ┌───────────────────────────────────────────────────────────┐  │
│   │                      API网关层                             │  │
│   │   FastAPI + JWT认证 + 限流 + 日志                         │  │
│   └───────────────────────────────────────────────────────────┘  │
│                              │                                    │
│         ┌────────────────────┼────────────────────┐              │
│         ▼                    ▼                    ▼              │
│   ┌───────────┐       ┌───────────┐       ┌───────────┐         │
│   │  对话服务  │       │  RAG服务  │       │ Agent服务 │         │
│   │           │       │           │       │           │         │
│   │ • 多轮对话│       │ • 文档检索│       │ • 任务执行│         │
│   │ • 记忆管理│       │ • 知识图谱│       │ • 工具调用│         │
│   │ • 流式输出│       │ • 重排序  │       │ • 结果整合│         │
│   └───────────┘       └───────────┘       └───────────┘         │
│         │                    │                    │              │
│         └────────────────────┴────────────────────┘              │
│                              │                                    │
│                              ▼                                    │
│   ┌───────────────────────────────────────────────────────────┐  │
│   │                      存储层                                │  │
│   │   PostgreSQL + Redis + Milvus/ChromaDB + MinIO           │  │
│   └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
enterprise_ai_assistant/
├── README.md
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置管理
│   │   │
│   │   ├── api/                 # API路由
│   │   │   ├── chat.py          # 对话API
│   │   │   ├── documents.py     # 文档API
│   │   │   ├── agents.py        # Agent API
│   │   │   └── auth.py          # 认证API
│   │   │
│   │   ├── services/            # 业务服务
│   │   │   ├── llm.py           # LLM服务
│   │   │   ├── rag.py           # RAG服务
│   │   │   ├── agent.py         # Agent服务
│   │   │   └── memory.py        # 记忆服务
│   │   │
│   │   ├── models/              # 数据模型
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   └── document.py
│   │   │
│   │   └── utils/               # 工具函数
│   │       ├── auth.py
│   │       └── embedding.py
│   │
│   └── tests/
│
├── frontend/                     # 前端（可选）
│   ├── package.json
│   └── src/
│
└── docs/
    ├── api.md
    ├── deployment.md
    └── architecture.md
```

---

## 🔧 核心功能模块

### 1. 多轮对话 + 记忆

```python
class ConversationService:
    """对话服务"""
    
    async def chat(
        self,
        user_id: str,
        message: str,
        conversation_id: str = None
    ) -> AsyncGenerator[str, None]:
        # 1. 获取对话历史
        history = await self.memory.get_history(conversation_id)
        
        # 2. 检索相关知识
        context = await self.rag.search(message)
        
        # 3. 构建提示词
        messages = self._build_messages(history, context, message)
        
        # 4. 流式生成
        async for chunk in self.llm.stream(messages):
            yield chunk
        
        # 5. 保存到记忆
        await self.memory.save(conversation_id, message, full_response)
```

### 2. 文档知识库

```python
class KnowledgeBaseService:
    """知识库服务"""
    
    async def ingest_document(self, file: UploadFile, user_id: str):
        # 1. 解析文档
        content = await self.parser.parse(file)
        
        # 2. 分块
        chunks = self.splitter.split(content)
        
        # 3. 向量化
        embeddings = await self.embedder.embed_batch(chunks)
        
        # 4. 存储
        await self.vector_store.add(chunks, embeddings, metadata)
        
        return {"status": "indexed", "chunks": len(chunks)}
    
    async def search(self, query: str, top_k: int = 5):
        # 1. 语义检索
        results = await self.vector_store.search(query, top_k)
        
        # 2. 重排序
        reranked = await self.reranker.rerank(query, results)
        
        return reranked
```

### 3. Agent工具调用

```python
TOOLS = [
    {
        "name": "search_knowledge",
        "description": "搜索内部知识库",
        "parameters": {...}
    },
    {
        "name": "web_search", 
        "description": "搜索互联网",
        "parameters": {...}
    },
    {
        "name": "analyze_data",
        "description": "分析数据并生成图表",
        "parameters": {...}
    }
]

class AgentService:
    async def execute(self, task: str) -> str:
        # ReAct循环
        while not done:
            thought = await self.think(task, history)
            action = await self.decide_action(thought)
            result = await self.execute_tool(action)
            history.append((action, result))
        
        return self.synthesize(history)
```

---

## 📋 评分标准

| 维度 | 分值 | 要求 |
|------|------|------|
| 功能完整性 | 30分 | 基础对话、RAG、Agent全部实现 |
| 代码质量 | 25分 | 类型完整、测试覆盖、文档清晰 |
| 系统设计 | 20分 | 架构合理、可扩展、容错处理 |
| 用户体验 | 15分 | 响应快、错误友好、流式输出 |
| 创新特性 | 10分 | 有独特功能或优化 |

---

## 🚀 开发建议

> [!TIP]
> **迭代开发**：先实现最小可用版本（MVP），再逐步添加功能

> [!IMPORTANT]  
> **优先级排序**：
> 1. 基础对话 → 2. RAG检索 → 3. Agent工具 → 4. 用户认证 → 5. 前端界面

---

**完成这个项目，你就是一名合格的AI工程师！🎓**
