# 🤖 构建简单RAG系统

> **学习目标**：整合Embedding、向量数据库和LLM，构建完整的RAG问答系统

---

## 1. RAG系统架构

```
用户问题
    │
    ▼
┌─────────────────┐
│  1. 问题向量化   │ ← Embedding API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 检索相关文档 │ ← 向量数据库
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 构建Prompt  │ ← 问题 + 检索文档
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. LLM生成回答 │ ← DeepSeek/GPT
└────────┬────────┘
         │
         ▼
      回答
```

---

## 2. 完整实现

### 2.1 安装依赖

```bash
pip install openai chromadb tiktoken
```

### 2.2 核心RAG类

```python
import chromadb
from openai import OpenAI
import os

class SimpleRAG:
    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_path: str = "./rag_db"
    ):
        # 初始化向量数据库
        self.chroma_client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )
        
        # 初始化LLM客户端
        self.llm_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        
        # RAG配置
        self.top_k = 5
        self.max_context_length = 3000
    
    def add_documents(self, documents: list[str], ids: list[str] = None):
        """添加文档到知识库"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.upsert(
            documents=documents,
            ids=ids
        )
        print(f"已添加 {len(documents)} 个文档，总数: {self.collection.count()}")
    
    def retrieve(self, query: str) -> list[str]:
        """检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=self.top_k,
            include=["documents", "distances"]
        )
        
        # 过滤低相似度结果
        docs = []
        for doc, dist in zip(results["documents"][0], results["distances"][0]):
            if dist < 1.0:  # 距离阈值
                docs.append(doc)
        
        return docs
    
    def _build_prompt(self, question: str, context_docs: list[str]) -> str:
        """构建RAG Prompt"""
        context = "\n\n---\n\n".join(context_docs)
        
        # 截断过长的上下文
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "..."
        
        prompt = f"""基于以下参考文档回答用户问题。

## 参考文档

{context}

## 用户问题

{question}

## 回答要求

1. 只根据参考文档中的信息回答
2. 如果文档中没有相关信息，请明确说明"根据现有资料无法回答"
3. 回答要简洁、准确、有条理
4. 如果可能，引用具体的文档内容

请回答："""
        
        return prompt
    
    def query(self, question: str) -> dict:
        """RAG问答"""
        # 1. 检索相关文档
        docs = self.retrieve(question)
        
        if not docs:
            return {
                "answer": "抱歉，我没有找到与您问题相关的信息。",
                "sources": [],
                "doc_count": 0
            }
        
        # 2. 构建Prompt
        prompt = self._build_prompt(question, docs)
        
        # 3. 调用LLM生成回答
        response = self.llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个知识库问答助手，根据提供的文档回答问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": docs,
            "doc_count": len(docs)
        }

# 使用示例
if __name__ == "__main__":
    rag = SimpleRAG()
    
    # 添加知识
    rag.add_documents([
        "FastAPI是一个现代、快速（高性能）的Web框架，用于构建API。它基于Python 3.7+的类型提示。",
        "FastAPI的性能与NodeJS和Go相当，是Python最快的框架之一。",
        "FastAPI自动生成交互式API文档（Swagger UI和ReDoc）。",
        "FastAPI使用Pydantic进行数据验证，使用Starlette作为Web部分。",
        "Django是一个高级Python Web框架，鼓励快速开发和简洁、务实的设计。"
    ])
    
    # 问答
    result = rag.query("FastAPI有什么特点？")
    print("回答:", result["answer"])
    print(f"参考了 {result['doc_count']} 个文档")
```

---

## 3. 添加流式输出

```python
def query_stream(self, question: str):
    """流式RAG问答"""
    docs = self.retrieve(question)
    
    if not docs:
        yield "抱歉，我没有找到与您问题相关的信息。"
        return
    
    prompt = self._build_prompt(question, docs)
    
    response = self.llm_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个知识库问答助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        stream=True  # 启用流式
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# 使用
for text in rag.query_stream("FastAPI是什么？"):
    print(text, end="", flush=True)
```

---

## 4. 添加FastAPI接口

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="RAG问答API")
rag = SimpleRAG()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    doc_count: int

class AddDocsRequest(BaseModel):
    documents: list[str]

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """问答接口"""
    result = rag.query(request.question)
    return result

@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """流式问答接口"""
    def generate():
        for text in rag.query_stream(request.question):
            yield f"data: {text}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/documents")
async def add_documents(request: AddDocsRequest):
    """添加文档"""
    rag.add_documents(request.documents)
    return {"status": "success", "count": len(request.documents)}

@app.get("/documents/count")
async def get_doc_count():
    """获取文档数量"""
    return {"count": rag.collection.count()}
```

---

## 5. 文档预处理

### 5.1 从文件加载

```python
def load_markdown(filepath: str) -> list[str]:
    """加载Markdown文件并分块"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按标题分块
    import re
    sections = re.split(r'\n##\s+', content)
    
    chunks = []
    for section in sections:
        if section.strip():
            # 进一步分割过长的section
            if len(section) > 1000:
                paragraphs = section.split('\n\n')
                for p in paragraphs:
                    if p.strip():
                        chunks.append(p.strip())
            else:
                chunks.append(section.strip())
    
    return chunks

# 使用
docs = load_markdown("./knowledge/fastapi_guide.md")
rag.add_documents(docs)
```

### 5.2 从目录加载

```python
import os

def load_directory(dirpath: str) -> list[str]:
    """加载目录下所有Markdown文件"""
    all_docs = []
    
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                docs = load_markdown(filepath)
                all_docs.extend(docs)
    
    return all_docs

# 使用
docs = load_directory("./knowledge")
rag.add_documents(docs)
```

---

## 6. 完整项目结构

```
simple_rag/
├── rag.py              # RAG核心类
├── api.py              # FastAPI接口
├── loader.py           # 文档加载器
├── config.py           # 配置
├── knowledge/          # 知识库文档
│   ├── fastapi.md
│   ├── python.md
│   └── ...
├── rag_db/             # 向量数据库
├── requirements.txt
└── README.md
```

---

## 📺 推荐B站视频

搜索：
- **"RAG 实战 教程"**
- **"LangChain RAG 入门"**
- **"知识库问答 Python"**

---

## 7. 继续学习

🎉 **恭喜完成Week 4！**

📌 **Week 4 学习顺序**：
1. ✅ Embedding向量化入门
2. ✅ ChromaDB或Milvus
3. ✅ 检索策略详解
4. ✅ 构建简单RAG系统（本教程）

继续前往 **Week 5** 学习RAG进阶技术！

---

**你已经构建了第一个RAG系统！💪**
