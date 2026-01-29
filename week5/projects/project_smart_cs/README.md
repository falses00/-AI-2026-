# 🚀 Week 5 项目：智能客服系统

> **项目目标**：构建一个企业级智能客服系统，整合高级RAG技术

---

## 🎯 项目要求

### 功能需求

1. **多源知识库**：支持FAQ、产品文档、政策文件
2. **混合检索**：语义+关键词双通道
3. **智能重排序**：使用Cross-Encoder精排
4. **对话记忆**：支持多轮对话
5. **答案评估**：置信度评估和不确定性提示

### 技术亮点

- 混合检索 + RRF融合
- 两阶段检索（粗排+精排）
- 上下文压缩节省Token
- 对话历史管理
- 答案置信度评估

---

## 📁 项目结构

```
project_smart_cs/
├── main.py                 # FastAPI入口
├── config.py               # 配置
├── engines/
│   ├── hybrid_retriever.py # 混合检索
│   ├── reranker.py         # 重排序
│   ├── compressor.py       # 上下文压缩
│   └── rag_engine.py       # RAG引擎
├── models/
│   └── schemas.py          # 数据模型
├── data/
│   ├── faq.json           # FAQ数据
│   └── docs/              # 产品文档
├── templates/
│   └── chat.html          # 聊天界面
└── requirements.txt
```

---

## 💻 核心代码

### config.py

```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    
    # 检索配置
    INITIAL_TOP_K: int = 20      # 粗排数量
    FINAL_TOP_K: int = 5         # 精排数量
    SEMANTIC_WEIGHT: float = 0.6 # 语义检索权重
    
    # 压缩配置
    MAX_CONTEXT_LENGTH: int = 2000
    
    # 置信度阈值
    CONFIDENCE_THRESHOLD: float = 0.7

settings = Settings()
```

### engines/hybrid_retriever.py

```python
import chromadb
from rank_bm25 import BM25Okapi
import jieba
from typing import List, Dict
from config import settings

class HybridRetriever:
    def __init__(self, collection_name: str = "knowledge"):
        # ChromaDB
        self.chroma = chromadb.PersistentClient(path="./chroma_cs")
        self.collection = self.chroma.get_or_create_collection(collection_name)
        
        # BM25
        self.documents = []
        self.doc_ids = []
        self.bm25 = None
        
        # 加载已有文档
        self._load_existing()
    
    def _load_existing(self):
        """加载已有文档到BM25"""
        if self.collection.count() > 0:
            results = self.collection.get()
            self.documents = results["documents"]
            self.doc_ids = results["ids"]
            tokenized = [list(jieba.cut(doc)) for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized)
    
    def add_documents(self, docs: List[str], metadatas: List[Dict] = None):
        """添加文档"""
        start_id = len(self.doc_ids)
        new_ids = [f"doc_{start_id + i}" for i in range(len(docs))]
        
        # ChromaDB
        self.collection.upsert(
            documents=docs,
            ids=new_ids,
            metadatas=metadatas
        )
        
        # 更新BM25
        self.documents.extend(docs)
        self.doc_ids.extend(new_ids)
        tokenized = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def search(self, query: str, top_k: int = 20) -> List[Dict]:
        """混合检索"""
        # 语义检索
        semantic = self._semantic_search(query, top_k)
        
        # 关键词检索
        keyword = self._keyword_search(query, top_k) if self.bm25 else []
        
        # RRF融合
        return self._rrf_fusion([semantic, keyword], top_k)
    
    def _semantic_search(self, query: str, top_k: int) -> List[tuple]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        return [
            (results["documents"][0][i], 1 - results["distances"][0][i])
            for i in range(len(results["ids"][0]))
        ]
    
    def _keyword_search(self, query: str, top_k: int) -> List[tuple]:
        tokens = list(jieba.cut(query))
        scores = self.bm25.get_scores(tokens)
        
        if scores.max() > 0:
            scores = scores / scores.max()
        
        indices = scores.argsort()[-top_k:][::-1]
        return [(self.documents[i], scores[i]) for i in indices]
    
    def _rrf_fusion(self, result_lists: List[List[tuple]], top_k: int, k: int = 60) -> List[Dict]:
        scores = {}
        docs_map = {}
        
        for results in result_lists:
            for rank, (doc, score) in enumerate(results):
                if doc not in scores:
                    scores[doc] = 0
                    docs_map[doc] = doc
                scores[doc] += 1 / (k + rank + 1)
        
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"content": doc, "score": score}
            for doc, score in sorted_docs[:top_k]
        ]
```

### engines/reranker.py

```python
from sentence_transformers import CrossEncoder
from typing import List, Dict

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """重排序文档"""
        if not documents:
            return []
        
        contents = [d["content"] for d in documents]
        pairs = [(query, c) for c in contents]
        
        scores = self.model.predict(pairs)
        
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
        
        documents.sort(key=lambda x: x["rerank_score"], reverse=True)
        return documents[:top_k]
```

### engines/compressor.py

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class ContextCompressor:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    
    def compress(self, query: str, documents: List[str], max_length: int = 2000) -> str:
        """压缩上下文"""
        # 收集所有句子
        all_sentences = []
        for doc in documents:
            sentences = [s.strip() for s in doc.replace('\n', '。').split('。') if s.strip()]
            all_sentences.extend(sentences)
        
        if not all_sentences:
            return ""
        
        # 计算相似度
        query_emb = self.model.encode([query])
        sent_embs = self.model.encode(all_sentences)
        
        similarities = np.dot(sent_embs, query_emb.T).flatten()
        
        # 选择top句子
        top_indices = similarities.argsort()[::-1]
        
        selected = []
        current_length = 0
        for i in top_indices:
            sent = all_sentences[i]
            if current_length + len(sent) > max_length:
                break
            selected.append((i, sent))
            current_length += len(sent)
        
        # 按原始顺序排列
        selected.sort(key=lambda x: x[0])
        
        return '。'.join([s for _, s in selected]) + '。'
```

### engines/rag_engine.py

```python
from openai import OpenAI
from typing import Dict, List, Optional
from config import settings
from engines.hybrid_retriever import HybridRetriever
from engines.reranker import Reranker
from engines.compressor import ContextCompressor

class SmartCSEngine:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker = Reranker()
        self.compressor = ContextCompressor()
        
        self.llm = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        self.conversation_history = {}
    
    def add_knowledge(self, documents: List[str], category: str = "general"):
        """添加知识"""
        metadatas = [{"category": category} for _ in documents]
        self.retriever.add_documents(documents, metadatas)
    
    def chat(self, session_id: str, question: str) -> Dict:
        """对话问答"""
        # 获取对话历史
        history = self.conversation_history.get(session_id, [])
        
        # 1. 检索（粗排）
        retrieved = self.retriever.search(question, top_k=settings.INITIAL_TOP_K)
        
        # 2. 重排序（精排）
        reranked = self.reranker.rerank(question, retrieved, top_k=settings.FINAL_TOP_K)
        
        # 3. 压缩上下文
        contents = [d["content"] for d in reranked]
        compressed = self.compressor.compress(
            question, contents, 
            max_length=settings.MAX_CONTEXT_LENGTH
        )
        
        # 4. 计算置信度
        confidence = self._calculate_confidence(reranked)
        
        # 5. 构建Prompt
        history_text = self._format_history(history[-3:])  # 最近3轮
        
        prompt = f"""你是一个智能客服助手。

## 对话历史
{history_text}

## 参考资料
{compressed}

## 用户问题
{question}

## 回答要求
1. 只根据参考资料回答
2. 如果资料不足，诚实说明
3. 语气友好专业
4. 简洁明了

回答："""
        
        # 6. 生成回答
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的客服助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # 添加不确定性提示
        if confidence < settings.CONFIDENCE_THRESHOLD:
            answer += "\n\n⚠️ 温馨提示：以上信息仅供参考，如需进一步帮助，请联系人工客服。"
        
        # 7. 更新历史
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        self.conversation_history[session_id] = history
        
        return {
            "answer": answer,
            "confidence": confidence,
            "sources_count": len(reranked),
            "context_length": len(compressed)
        }
    
    def _calculate_confidence(self, reranked: List[Dict]) -> float:
        """计算置信度"""
        if not reranked:
            return 0.0
        
        scores = [d.get("rerank_score", 0) for d in reranked]
        return min(1.0, max(0.0, sum(scores) / len(scores) + 0.3))
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化历史"""
        if not history:
            return "无"
        
        lines = []
        for h in history:
            role = "用户" if h["role"] == "user" else "客服"
            lines.append(f"{role}: {h['content'][:100]}")
        
        return "\n".join(lines)
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
```

### main.py

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid

from engines.rag_engine import SmartCSEngine

app = FastAPI(title="智能客服系统")
engine = SmartCSEngine()

# 初始化一些FAQ
engine.add_knowledge([
    "Q: 如何退款？A: 登录账户，进入订单页面，点击退款按钮即可申请退款。",
    "Q: 配送需要多久？A: 普通配送3-5天，加急配送1-2天。",
    "Q: 如何修改订单？A: 订单发货前可在订单详情页修改，发货后请联系客服。",
    "Q: 会员有什么优惠？A: 会员享受95折优惠，积分翻倍，专属客服等权益。",
    "Q: 如何联系客服？A: 可拨打400-xxx-xxxx或在线留言。",
], category="faq")

class ChatRequest(BaseModel):
    session_id: str = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence: float
    sources_count: int

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能客服</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            .chat-box { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; border-radius: 8px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user { background: #007bff; color: white; text-align: right; }
            .assistant { background: #f1f1f1; }
            .input-area { display: flex; margin-top: 15px; }
            .input-area input { flex: 1; padding: 10px; }
            .input-area button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .confidence { font-size: 0.8em; color: #666; }
        </style>
    </head>
    <body>
        <h1>🤖 智能客服</h1>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="请输入您的问题..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">发送</button>
        </div>
        
        <script>
            let sessionId = null;
            
            function addMessage(content, isUser, confidence = null) {
                const box = document.getElementById('chatBox');
                let html = `<div class="message ${isUser ? 'user' : 'assistant'}">${content}`;
                if (confidence !== null) {
                    html += `<div class="confidence">置信度: ${(confidence * 100).toFixed(0)}%</div>`;
                }
                html += '</div>';
                box.innerHTML += html;
                box.scrollTop = box.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                input.value = '';
                
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message})
                });
                
                const data = await res.json();
                sessionId = data.session_id;
                addMessage(data.answer, false, data.confidence);
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    result = engine.chat(session_id, request.message)
    
    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        confidence=result["confidence"],
        sources_count=result["sources_count"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

## 🚀 运行项目

```bash
cd week5/projects/project_smart_cs
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8002

---

## ✅ 验收标准

- [ ] 混合检索正常工作
- [ ] 重排序提升结果质量
- [ ] 多轮对话记忆上下文
- [ ] 置信度评估合理
- [ ] 低置信度时有提示

---

## 🔥 进阶挑战

1. 添加意图识别
2. 支持工单创建
3. 集成知识图谱
4. 添加管理后台
