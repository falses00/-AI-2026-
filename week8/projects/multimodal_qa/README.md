# 🖼️ 图文问答系统项目

> **Week 8 综合实战项目** - 构建支持图片理解的智能问答系统

---

## 🎯 项目目标

构建一个能够理解图片内容并回答相关问题的AI问答系统，综合运用：
- GPT-4V/GPT-4o 多模态能力
- RAG检索增强
- FastAPI后端开发
- 流式响应

---

## 📊 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     图文问答系统架构                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      │
│  │   用户输入   │      │  图片+问题  │      │  纯文本问题 │       │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘      │
│         │                    │                    │              │
│         └────────────────────┴────────────────────┘              │
│                              │                                    │
│                              ▼                                    │
│                    ┌─────────────────┐                           │
│                    │   请求分析器     │                           │
│                    │ (判断是否含图)   │                           │
│                    └────────┬────────┘                           │
│                             │                                     │
│              ┌──────────────┴──────────────┐                     │
│              ▼                              ▼                     │
│    ┌─────────────────┐            ┌─────────────────┐            │
│    │   图片分析模块   │            │   文本RAG模块   │            │
│    │   (GPT-4V)      │            │   (ChromaDB)    │            │
│    └────────┬────────┘            └────────┬────────┘            │
│             │                              │                      │
│             └──────────────┬───────────────┘                     │
│                            ▼                                      │
│                  ┌─────────────────┐                             │
│                  │   综合生成模块   │                             │
│                  │   (GPT-4o)      │                             │
│                  └────────┬────────┘                             │
│                           │                                       │
│                           ▼                                       │
│                  ┌─────────────────┐                             │
│                  │   流式响应      │                              │
│                  └─────────────────┘                             │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
week8/projects/multimodal_qa/
├── README.md              # 本文件
├── requirements.txt       # 依赖
├── .env.example          # 环境变量模板
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI入口
│   ├── config.py         # 配置管理
│   ├── models.py         # Pydantic模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vision.py     # 图片分析服务
│   │   ├── rag.py        # 检索服务  
│   │   └── chat.py       # 对话服务
│   └── routers/
│       ├── __init__.py
│       └── qa.py         # QA路由
├── tests/
│   ├── test_vision.py
│   └── test_qa.py
└── docker-compose.yml
```

---

## 🔧 核心代码

### 1. 配置管理 (`app/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    MAX_IMAGE_SIZE_MB: int = 20
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. 图片分析服务 (`app/services/vision.py`)

```python
import base64
from openai import OpenAI
from ..config import settings

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

async def analyze_image(
    image_data: bytes,
    question: str,
    detail: str = "auto"
) -> str:
    """
    分析图片并回答问题
    
    Args:
        image_data: 图片二进制数据
        question: 用户问题
        detail: 图片分辨率 ("low", "high", "auto")
    
    Returns:
        AI对图片的分析结果
    """
    # Base64编码
    base64_image = base64.b64encode(image_data).decode("utf-8")
    
    # 检测图片类型
    if image_data[:8] == b'\x89PNG\r\n\x1a\n':
        media_type = "image/png"
    elif image_data[:2] == b'\xff\xd8':
        media_type = "image/jpeg"
    elif image_data[:4] == b'RIFF':
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"  # 默认
    
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"请仔细分析这张图片，然后回答以下问题：\n\n{question}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content


async def describe_image(image_data: bytes) -> str:
    """生成图片描述用于索引"""
    base64_image = base64.b64encode(image_data).decode("utf-8")
    
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请详细描述这张图片的内容，包括：主要物体、颜色、文字、布局等。用于建立图片索引。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"  # 描述用低分辨率即可
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

### 3. RAG服务 (`app/services/rag.py`)

```python
import chromadb
from openai import OpenAI
from ..config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
collection = chroma_client.get_or_create_collection("image_descriptions")

async def add_image_to_index(image_id: str, description: str, metadata: dict = None):
    """将图片描述添加到索引"""
    # 生成嵌入
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=description
    )
    embedding = response.data[0].embedding
    
    collection.add(
        ids=[image_id],
        embeddings=[embedding],
        documents=[description],
        metadatas=[metadata or {}]
    )

async def search_similar_images(query: str, n_results: int = 5) -> list:
    """搜索相关图片"""
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=query
    )
    query_embedding = response.data[0].embedding
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas"]
    )
    
    return [
        {
            "id": results["ids"][0][i],
            "description": results["documents"][0][i],
            "metadata": results["metadatas"][0][i]
        }
        for i in range(len(results["ids"][0]))
    ]
```

### 4. API路由 (`app/routers/qa.py`)

```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from ..services import vision, rag, chat
from ..models import QARequest, QAResponse

router = APIRouter(prefix="/api/qa", tags=["图文问答"])

@router.post("/ask")
async def ask_with_image(
    question: str = Form(...),
    image: UploadFile = File(None)
):
    """
    图文问答接口
    
    - question: 用户问题
    - image: 可选的图片文件
    """
    try:
        if image:
            # 验证图片大小
            content = await image.read()
            if len(content) > 20 * 1024 * 1024:  # 20MB
                raise HTTPException(400, "图片过大，最大支持20MB")
            
            # 分析图片
            answer = await vision.analyze_image(content, question)
            
            return {
                "answer": answer,
                "has_image": True,
                "image_filename": image.filename
            }
        else:
            # 纯文本问答 - 使用RAG
            context = await rag.search_similar_images(question, n_results=3)
            answer = await chat.generate_answer(question, context)
            
            return {
                "answer": answer,
                "has_image": False,
                "context_used": len(context) > 0
            }
            
    except Exception as e:
        raise HTTPException(500, f"处理失败: {str(e)}")

@router.post("/ask/stream")
async def ask_with_image_stream(
    question: str = Form(...),
    image: UploadFile = File(None)
):
    """流式图文问答"""
    async def generate():
        if image:
            content = await image.read()
            async for chunk in vision.analyze_image_stream(content, question):
                yield f"data: {chunk}\n\n"
        else:
            context = await rag.search_similar_images(question)
            async for chunk in chat.generate_answer_stream(question, context):
                yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/index-image")
async def index_image(
    image: UploadFile = File(...),
    image_id: str = Form(...)
):
    """将图片添加到索引"""
    content = await image.read()
    
    # 生成描述
    description = await vision.describe_image(content)
    
    # 添加到索引
    await rag.add_image_to_index(
        image_id=image_id,
        description=description,
        metadata={"filename": image.filename}
    )
    
    return {"status": "indexed", "description": description}
```

### 5. 主入口 (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import qa

app = FastAPI(
    title="图文问答系统",
    description="支持图片理解的智能问答API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(qa.router)

@app.get("/")
async def root():
    return {"message": "图文问答系统 API v1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## 📦 依赖 (`requirements.txt`)

```
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6
openai>=1.12.0
chromadb>=0.4.22
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
```

---

## 🚀 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑.env，填入API Key

# 3. 运行服务
uvicorn app.main:app --reload --port 8000

# 4. 访问文档
# http://localhost:8000/docs
```

---

## 📋 API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/qa/ask` | 图文问答（支持上传图片） |
| POST | `/api/qa/ask/stream` | 流式图文问答 |
| POST | `/api/qa/index-image` | 将图片添加到索引 |

---

## 💡 扩展建议

1. **多图片支持** - 上传多张图片进行对比分析
2. **OCR增强** - 对图片中的文字进行专门处理
3. **历史记录** - 保存问答历史，支持上下文对话
4. **图片库管理** - 构建图片知识库，支持按标签检索

---

## 📊 学习收获

完成此项目后，你将掌握：
- [x] GPT-4V多模态API的使用
- [x] Base64图片编码与格式处理
- [x] 多模态RAG系统设计
- [x] FastAPI文件上传处理
- [x] 流式响应实现
