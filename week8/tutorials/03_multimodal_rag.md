# 🖼️ 多模态RAG系统

> **学习目标**：构建支持图文混合的智能问答系统

---

## 1. 多模态RAG架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    多模态RAG架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │  用户查询   │ "这张图片里的产品是什么？"                       │
│  │ (文本+图片) │                                                │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              多模态嵌入层 (Multimodal Embedding)             │ │
│  │  ┌────────────┐              ┌────────────┐                 │ │
│  │  │ 文本Embed  │              │ 图像Embed  │                 │ │
│  │  │ (text-3)   │              │ (CLIP)     │                 │ │
│  │  └──────┬─────┘              └──────┬─────┘                 │ │
│  │         │                          │                        │ │
│  │         └────────────┬─────────────┘                        │ │
│  │                      ▼                                       │ │
│  │              ┌──────────────┐                                │ │
│  │              │  统一向量    │                                │ │
│  │              └──────────────┘                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              向量检索层 (Vector Search)                      │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │ │
│  │  │  文档块    │  │  图片描述  │  │  表格数据  │             │ │
│  │  └────────────┘  └────────────┘  └────────────┘             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              多模态生成层 (GPT-4V / Gemini)                  │ │
│  │  结合检索到的文本、图片、表格，生成综合回答                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 图像嵌入与检索

### 2.1 使用CLIP模型

```bash
pip install transformers torch pillow
```

```python
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

class ImageEmbedder:
    """图像嵌入器"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
    
    def embed_image(self, image_path: str) -> np.ndarray:
        """生成图像嵌入向量"""
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
        
        # 归一化
        features = features / features.norm(dim=-1, keepdim=True)
        return features.numpy()[0]
    
    def embed_text(self, text: str) -> np.ndarray:
        """生成文本嵌入向量（用于图文匹配）"""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
        
        features = features / features.norm(dim=-1, keepdim=True)
        return features.numpy()[0]
    
    def similarity(self, image_path: str, text: str) -> float:
        """计算图文相似度"""
        img_embed = self.embed_image(image_path)
        text_embed = self.embed_text(text)
        return float(np.dot(img_embed, text_embed))

# 使用
embedder = ImageEmbedder()
similarity = embedder.similarity("product.jpg", "红色运动鞋")
print(f"相似度: {similarity:.4f}")
```

---

## 3. 多模态文档索引

### 3.1 文档结构

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"

@dataclass
class MultimodalChunk:
    """多模态内容块"""
    id: str
    content_type: ContentType
    text_content: Optional[str] = None
    image_path: Optional[str] = None
    image_description: Optional[str] = None
    table_data: Optional[list] = None
    embedding: Optional[list] = None
    metadata: dict = None
```

### 3.2 多模态索引器

```python
from openai import OpenAI
import chromadb
import uuid

class MultimodalIndexer:
    """多模态索引器"""
    
    def __init__(self, collection_name: str = "multimodal_docs"):
        self.client = OpenAI()
        self.image_embedder = ImageEmbedder()
        
        # ChromaDB
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def describe_image(self, image_path: str) -> str:
        """使用GPT-4V生成图像描述"""
        import base64
        
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "详细描述这张图片的内容，包括所有可见的文字、物体、颜色和布局。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def index_text(self, text: str, metadata: dict = None) -> str:
        """索引文本"""
        chunk_id = str(uuid.uuid4())
        
        # 生成文本嵌入
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        
        self.collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"type": "text", **(metadata or {})}]
        )
        
        return chunk_id
    
    def index_image(self, image_path: str, metadata: dict = None) -> str:
        """索引图像"""
        chunk_id = str(uuid.uuid4())
        
        # 生成图像描述
        description = self.describe_image(image_path)
        
        # 使用描述生成文本嵌入
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=description
        )
        embedding = response.data[0].embedding
        
        self.collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[description],
            metadatas=[{
                "type": "image",
                "image_path": image_path,
                **(metadata or {})
            }]
        )
        
        return chunk_id
    
    def search(self, query: str, n_results: int = 5) -> list:
        """搜索相关内容"""
        # 生成查询嵌入
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return [
            {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]

# 使用
indexer = MultimodalIndexer()

# 索引文本
indexer.index_text("iPhone 15 Pro采用钛金属边框，搭载A17 Pro芯片")

# 索引图像
indexer.index_image("iphone15_pro.jpg", {"product": "iPhone 15 Pro"})

# 搜索
results = indexer.search("苹果最新手机是什么配置？")
```

---

## 4. 多模态问答

```python
import base64
from typing import List

class MultimodalQA:
    """多模态问答系统"""
    
    def __init__(self):
        self.client = OpenAI()
        self.indexer = MultimodalIndexer()
    
    def answer(
        self,
        question: str,
        image_path: str = None,
        n_context: int = 5
    ) -> str:
        """回答问题"""
        # 1. 检索相关内容
        context_results = self.indexer.search(question, n_results=n_context)
        
        # 2. 构建上下文
        context_parts = []
        image_contents = []
        
        for result in context_results:
            if result["metadata"]["type"] == "text":
                context_parts.append(f"文档片段: {result['document']}")
            elif result["metadata"]["type"] == "image":
                context_parts.append(f"图片描述: {result['document']}")
                # 获取图片用于GPT-4V
                img_path = result["metadata"].get("image_path")
                if img_path:
                    with open(img_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                        image_contents.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                        })
        
        context = "\n\n".join(context_parts)
        
        # 3. 构建消息
        messages = [
            {"role": "system", "content": f"""你是一个多模态问答助手。

参考以下检索到的内容回答问题：

{context}

如果提供了图片，请结合图片内容回答。"""},
        ]
        
        # 用户消息
        user_content = [{"type": "text", "text": question}]
        
        # 添加用户提供的图片
        if image_path:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                })
        
        # 添加检索到的图片
        user_content.extend(image_contents[:3])  # 最多3张
        
        messages.append({"role": "user", "content": user_content})
        
        # 4. 生成回答
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

# 使用
qa = MultimodalQA()
answer = qa.answer(
    "这款手机的主要特点是什么？",
    image_path="phone_photo.jpg"
)
print(answer)
```

---

## 5. 学习检查清单

- [ ] 理解多模态嵌入原理
- [ ] 能够使用CLIP进行图文匹配
- [ ] 会构建多模态索引系统
- [ ] 能够实现图文混合问答

---

## 继续学习

📌 **Week 8 学习顺序**：
1. ✅ Vision模型使用
2. ✅ 语音处理与Whisper
3. ✅ 多模态RAG系统（本教程）
