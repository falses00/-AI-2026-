# 🖼️ CLIP图像Embedding与图文检索

> **学习目标**：掌握CLIP模型原理，实现图像向量化和图文跨模态检索

---

## 1. CLIP简介

CLIP（Contrastive Language-Image Pre-training）是OpenAI发布的多模态模型，能够将**图像和文本**映射到**同一向量空间**。

```
┌──────────────────────────────────────────────────────────────┐
│                       CLIP 架构                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   图像输入                          文本输入                   │
│      │                                │                       │
│      ▼                                ▼                       │
│  ┌─────────┐                    ┌─────────┐                  │
│  │ Vision  │                    │  Text   │                  │
│  │ Encoder │                    │ Encoder │                  │
│  │ (ViT)   │                    │(Transf) │                  │
│  └────┬────┘                    └────┬────┘                  │
│       │                              │                        │
│       ▼                              ▼                        │
│  [图像向量]  ←── 对比学习 ──→  [文本向量]                     │
│       │                              │                        │
│       └──────────┬──────────────────┘                        │
│                  ▼                                            │
│           统一向量空间                                         │
│    (图片和描述靠近，不相关的远离)                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### CLIP的应用场景

| 场景 | 描述 |
|-----|------|
| 图像分类 | 零样本分类，无需训练 |
| 图像检索 | 用文本搜索图片 |
| 图文匹配 | 判断图片和描述是否匹配 |
| 多模态RAG | 图文混合知识库 |

---

## 2. 环境配置

```bash
# 安装OpenAI CLIP
pip install git+https://github.com/openai/CLIP.git

# 或使用开源替代品
pip install open-clip-torch

# 安装图像处理库
pip install pillow
```

---

## 3. 基础使用

### 3.1 加载模型

```python
import torch
import clip
from PIL import Image

# 检查设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载CLIP模型
model, preprocess = clip.load("ViT-B/32", device=device)

print(f"模型加载完成，使用设备: {device}")
```

### 3.2 图像编码

```python
def encode_image(image_path: str) -> torch.Tensor:
    """将图像编码为向量"""
    image = Image.open(image_path)
    image_input = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        # 归一化
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    
    return image_features

# 示例
embedding = encode_image("example.jpg")
print(f"向量维度: {embedding.shape}")  # [1, 512]
```

### 3.3 文本编码

```python
def encode_text(texts: list[str]) -> torch.Tensor:
    """将文本编码为向量"""
    text_tokens = clip.tokenize(texts).to(device)
    
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    return text_features

# 示例
texts = ["一只猫", "一只狗", "一辆汽车"]
text_embeddings = encode_text(texts)
print(f"文本向量维度: {text_embeddings.shape}")  # [3, 512]
```

---

## 4. 零样本图像分类

```python
def zero_shot_classify(image_path: str, labels: list[str]) -> dict:
    """零样本分类"""
    # 编码图像
    image_features = encode_image(image_path)
    
    # 编码标签
    text_features = encode_text(labels)
    
    # 计算相似度
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    
    # 返回结果
    results = {}
    for i, label in enumerate(labels):
        results[label] = float(similarity[0][i])
    
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

# 使用示例
labels = ["猫", "狗", "鸟", "汽车", "飞机"]
results = zero_shot_classify("pet.jpg", labels)

for label, score in results.items():
    print(f"{label}: {score:.2%}")
```

---

## 5. 图像检索

### 5.1 构建图像索引

```python
import os
from typing import List, Tuple
import numpy as np

class ImageSearchEngine:
    """图像检索引擎"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.image_embeddings: List[np.ndarray] = []
        self.image_paths: List[str] = []
    
    def index_images(self, image_folder: str):
        """索引文件夹中的所有图片"""
        for filename in os.listdir(image_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                path = os.path.join(image_folder, filename)
                try:
                    embedding = self._encode_image(path)
                    self.image_embeddings.append(embedding)
                    self.image_paths.append(path)
                    print(f"已索引: {filename}")
                except Exception as e:
                    print(f"处理失败: {filename} - {e}")
        
        print(f"索引完成，共 {len(self.image_paths)} 张图片")
    
    def _encode_image(self, image_path: str) -> np.ndarray:
        """编码单张图片"""
        image = Image.open(image_path).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model.encode_image(image_input)
            features = features / features.norm(dim=-1, keepdim=True)
        
        return features.cpu().numpy()[0]
    
    def search_by_text(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """用文本搜索图片"""
        # 编码查询文本
        text_tokens = clip.tokenize([query]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        query_embedding = text_features.cpu().numpy()[0]
        
        # 计算相似度
        embeddings_matrix = np.array(self.image_embeddings)
        similarities = np.dot(embeddings_matrix, query_embedding)
        
        # 排序返回Top-K
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.image_paths[idx], float(similarities[idx])))
        
        return results
    
    def search_by_image(self, query_image_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """用图片搜索相似图片"""
        query_embedding = self._encode_image(query_image_path)
        
        embeddings_matrix = np.array(self.image_embeddings)
        similarities = np.dot(embeddings_matrix, query_embedding)
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.image_paths[idx], float(similarities[idx])))
        
        return results
```

### 5.2 使用示例

```python
# 创建检索引擎
engine = ImageSearchEngine()

# 索引图片
engine.index_images("./images")

# 文本搜索
results = engine.search_by_text("日落海边", top_k=5)
for path, score in results:
    print(f"{score:.4f}: {path}")

# 以图搜图
results = engine.search_by_image("query.jpg", top_k=5)
for path, score in results:
    print(f"{score:.4f}: {path}")
```

---

## 6. 与ChromaDB集成

```python
import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

# 使用ChromaDB的CLIP嵌入函数
embedding_function = OpenCLIPEmbeddingFunction()

# 创建ChromaDB客户端
client = chromadb.Client()

# 创建支持图像的集合
collection = client.create_collection(
    name="image_collection",
    embedding_function=embedding_function,
    data_loader=ImageLoader()  # 自定义图像加载器
)

# 添加图像
collection.add(
    ids=["img1", "img2"],
    images=["path/to/image1.jpg", "path/to/image2.jpg"],
    metadatas=[{"category": "cat"}, {"category": "dog"}]
)

# 用文本查询
results = collection.query(
    query_texts=["一只可爱的小猫"],
    n_results=5
)
```

---

## 7. 学习检查清单

- [ ] 理解CLIP的多模态对比学习原理
- [ ] 能够使用CLIP编码图像和文本
- [ ] 能够实现零样本图像分类
- [ ] 能够构建图文检索系统
- [ ] 能够将CLIP与向量数据库集成

---

## 继续学习

📌 **Week 8 学习顺序**：
1. ✅ Vision模型基础
2. ✅ CLIP图像Embedding（本教程）
3. □ 语音处理实战
4. □ 多模态RAG

---

**CLIP让你的系统能够理解图像和文本的语义关系！🖼️**
