# 📚 Week 4 项目：智能文档问答系统

> **项目目标**：构建一个完整的文档问答系统，支持上传文档、向量化存储和智能问答

---

## 🎯 项目要求

### 功能要求

1. **文档上传**：支持上传Markdown和TXT文件
2. **自动分块**：将长文档分割成合适大小的块
3. **向量存储**：使用ChromaDB存储文档向量
4. **智能问答**：基于文档内容回答问题
5. **来源追溯**：显示答案的来源文档

### 技术栈

- FastAPI（后端API）
- ChromaDB（向量存储）
- DeepSeek API（LLM + Embedding）
- 简单HTML前端

---

## 📁 项目结构

```
project_doc_qa/
├── main.py              # FastAPI应用入口
├── rag_engine.py        # RAG核心逻辑
├── document_loader.py   # 文档加载器
├── config.py            # 配置文件
├── templates/
│   └── index.html       # 前端页面
├── uploads/             # 上传文件目录
├── chroma_db/           # 向量数据库
└── requirements.txt     # 依赖
```

---

## 💻 代码实现

### config.py

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    CHROMA_PATH: str = "./chroma_db"
    UPLOAD_PATH: str = "./uploads"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

settings = Settings()
```

### document_loader.py

```python
import os
from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """将文本分块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def load_markdown(filepath: str) -> List[Dict]:
    """加载Markdown文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    chunks = chunk_text(content)
    
    return [
        {
            "content": chunk,
            "metadata": {
                "source": filename,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(chunks)
    ]

def load_text(filepath: str) -> List[Dict]:
    """加载TXT文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    chunks = chunk_text(content)
    
    return [
        {
            "content": chunk,
            "metadata": {
                "source": filename,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(chunks)
    ]

def load_document(filepath: str) -> List[Dict]:
    """根据文件类型加载文档"""
    if filepath.endswith('.md'):
        return load_markdown(filepath)
    elif filepath.endswith('.txt'):
        return load_text(filepath)
    else:
        raise ValueError(f"不支持的文件类型: {filepath}")
```

### rag_engine.py

```python
import chromadb
from openai import OpenAI
from typing import List, Dict, Optional
from config import settings

class RAGEngine:
    def __init__(self):
        # 初始化ChromaDB
        self.chroma = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.chroma.get_or_create_collection(
            name="documents",
            metadata={"description": "文档知识库"}
        )
        
        # 初始化LLM客户端
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
    
    def add_documents(self, documents: List[Dict]) -> int:
        """添加文档到向量库"""
        if not documents:
            return 0
        
        # 生成ID
        start_id = self.collection.count()
        ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        
        # 提取内容和元数据
        contents = [d["content"] for d in documents]
        metadatas = [d["metadata"] for d in documents]
        
        # 添加到ChromaDB
        self.collection.upsert(
            documents=contents,
            ids=ids,
            metadatas=metadatas
        )
        
        return len(documents)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return output
    
    def query(self, question: str) -> Dict:
        """RAG问答"""
        # 检索
        docs = self.search(question, top_k=settings.TOP_K)
        
        if not docs:
            return {
                "answer": "抱歉，知识库中没有相关信息。",
                "sources": []
            }
        
        # 构建上下文
        context = "\n\n---\n\n".join([d["content"] for d in docs])
        
        # 构建Prompt
        prompt = f"""基于以下文档内容回答问题：

{context}

问题：{question}

要求：
1. 只根据文档内容回答
2. 如果文档中没有答案，说明"文档中未提及"
3. 简洁准确地回答

答案："""
        
        # 调用LLM
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个文档问答助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # 提取来源
        sources = list(set([d["metadata"]["source"] for d in docs]))
        
        return {
            "answer": answer,
            "sources": sources,
            "context_count": len(docs)
        }
    
    def get_stats(self) -> Dict:
        """获取知识库统计"""
        return {
            "document_count": self.collection.count()
        }
    
    def clear(self):
        """清空知识库"""
        self.chroma.delete_collection("documents")
        self.collection = self.chroma.get_or_create_collection(name="documents")
```

### main.py

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import shutil

from config import settings
from rag_engine import RAGEngine
from document_loader import load_document

app = FastAPI(title="智能文档问答系统")

# 确保目录存在
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)

# 初始化RAG引擎
rag = RAGEngine()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    context_count: int

@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能文档问答系统</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            input, button, textarea { padding: 10px; margin: 5px; }
            button { background: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
            button:hover { background: #0056b3; }
            #answer { background: #f5f5f5; padding: 15px; margin-top: 10px; border-radius: 4px; }
            .sources { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>📚 智能文档问答系统</h1>
        
        <div class="section">
            <h2>1. 上传文档</h2>
            <input type="file" id="fileInput" accept=".md,.txt">
            <button onclick="uploadFile()">上传</button>
            <p id="uploadStatus"></p>
        </div>
        
        <div class="section">
            <h2>2. 提问</h2>
            <input type="text" id="question" placeholder="输入你的问题..." style="width: 70%">
            <button onclick="askQuestion()">提问</button>
            <div id="answer"></div>
        </div>
        
        <div class="section">
            <h2>3. 知识库状态</h2>
            <button onclick="getStats()">刷新统计</button>
            <button onclick="clearDB()" style="background: #dc3545;">清空知识库</button>
            <p id="stats"></p>
        </div>
        
        <script>
            async function uploadFile() {
                const file = document.getElementById('fileInput').files[0];
                if (!file) return alert('请选择文件');
                
                const formData = new FormData();
                formData.append('file', file);
                
                const res = await fetch('/upload', { method: 'POST', body: formData });
                const data = await res.json();
                document.getElementById('uploadStatus').textContent = 
                    `上传成功！添加了 ${data.chunks_added} 个文档块`;
            }
            
            async function askQuestion() {
                const question = document.getElementById('question').value;
                if (!question) return;
                
                document.getElementById('answer').innerHTML = '思考中...';
                
                const res = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question})
                });
                const data = await res.json();
                
                document.getElementById('answer').innerHTML = `
                    <p><strong>答案：</strong>${data.answer}</p>
                    <p class="sources">来源：${data.sources.join(', ')}</p>
                `;
            }
            
            async function getStats() {
                const res = await fetch('/stats');
                const data = await res.json();
                document.getElementById('stats').textContent = 
                    `知识库包含 ${data.document_count} 个文档块`;
            }
            
            async function clearDB() {
                if (!confirm('确定要清空知识库吗？')) return;
                await fetch('/clear', { method: 'POST' });
                getStats();
                alert('知识库已清空');
            }
            
            getStats();
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传并处理文档"""
    # 保存文件
    filepath = os.path.join(settings.UPLOAD_PATH, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # 加载并分块
    try:
        documents = load_document(filepath)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 添加到向量库
    count = rag.add_documents(documents)
    
    return {"filename": file.filename, "chunks_added": count}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """问答接口"""
    result = rag.query(request.question)
    return result

@app.get("/stats")
async def stats():
    """获取统计信息"""
    return rag.get_stats()

@app.post("/clear")
async def clear():
    """清空知识库"""
    rag.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### requirements.txt

```
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6
openai>=1.0.0
chromadb>=0.4.0
pydantic-settings>=2.0.0
```

---

## 🚀 运行项目

```bash
# 1. 进入项目目录
cd week4/projects/project_doc_qa

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export DEEPSEEK_API_KEY=your-api-key

# 4. 运行
python main.py
```

访问 http://localhost:8001 开始使用！

---

## ✅ 验收标准

- [ ] 能成功上传Markdown和TXT文件
- [ ] 文档被正确分块并存储
- [ ] 能基于文档内容准确回答问题
- [ ] 显示答案来源
- [ ] 知识库统计功能正常

---

## 🔥 进阶挑战

1. **添加PDF支持**：使用pypdf库
2. **添加流式输出**：使用SSE返回
3. **添加相似问题推荐**
4. **添加文档管理界面**
