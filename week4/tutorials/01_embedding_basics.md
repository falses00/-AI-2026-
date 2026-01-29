# 🧮 Embedding向量化入门

> **学习目标**：理解文本向量化原理，掌握Embedding API的使用

---

## 1. 什么是Embedding？

**Embedding**（嵌入/向量化）是将文本转换为数值向量的过程：

```
"FastAPI是高性能框架" → [0.023, -0.009, 0.015, ..., 0.042]
                              ↑
                        1536维浮点数向量
```

### 为什么需要Embedding？

计算机不理解文字，但能处理数字：
- ❌ 无法直接比较 "狗" 和 "猫" 的相似度
- ✅ 可以计算 `[0.8, 0.2]` 和 `[0.7, 0.3]` 的余弦相似度

### Embedding的神奇之处

语义相近的文本，向量也相近：
```
"狗" → [0.8, 0.2, 0.1]
"猫" → [0.7, 0.3, 0.1]  ← 距离很近
"汽车" → [0.1, 0.1, 0.9]  ← 距离很远
```

---

## 2. 使用DeepSeek/OpenAI Embedding API

### 2.1 安装依赖

```bash
pip install openai numpy
```

### 2.2 基础使用

```python
from openai import OpenAI
import os

# 使用DeepSeek API（兼容OpenAI格式）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# 获取文本的向量表示
response = client.embeddings.create(
    model="text-embedding-3-small",  # 或使用DeepSeek的embedding模型
    input="FastAPI是一个现代Python Web框架"
)

embedding = response.data[0].embedding
print(f"向量维度: {len(embedding)}")  # 1536
print(f"前5个值: {embedding[:5]}")
```

### 2.3 批量获取Embedding

```python
def get_embeddings(texts: list[str]) -> list[list[float]]:
    """批量获取文本向量"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

# 使用
texts = [
    "FastAPI是高性能框架",
    "Django是全功能框架",
    "今天天气很好"
]
embeddings = get_embeddings(texts)

for text, emb in zip(texts, embeddings):
    print(f"{text[:20]}... → 维度: {len(emb)}")
```

---

## 3. 向量相似度计算

### 3.1 余弦相似度

```python
import numpy as np

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """计算两个向量的余弦相似度"""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 测试
texts = ["狗是忠诚的宠物", "猫是可爱的动物", "汽车需要加油"]
embeddings = get_embeddings(texts)

print("相似度矩阵:")
for i, t1 in enumerate(texts):
    for j, t2 in enumerate(texts):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"  {t1[:8]} vs {t2[:8]}: {sim:.4f}")
```

输出：
```
相似度矩阵:
  狗是忠诚的宠 vs 狗是忠诚的宠: 1.0000
  狗是忠诚的宠 vs 猫是可爱的动: 0.8234  ← 语义相近
  狗是忠诚的宠 vs 汽车需要加油: 0.3421  ← 语义较远
```

### 3.2 欧氏距离

```python
def euclidean_distance(vec1: list[float], vec2: list[float]) -> float:
    """计算欧氏距离（越小越相似）"""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.linalg.norm(a - b)
```

---

## 4. 本地Embedding模型

### 4.1 使用sentence-transformers

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

# 加载模型（首次会下载）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')  # 中文模型

# 获取embedding
texts = ["FastAPI是高性能框架", "Django是全功能框架"]
embeddings = model.encode(texts)

print(f"维度: {embeddings.shape}")  # (2, 512)
```

### 4.2 常用中文Embedding模型

| 模型 | 维度 | 特点 |
|------|------|------|
| BAAI/bge-small-zh-v1.5 | 512 | 小巧快速 |
| BAAI/bge-base-zh-v1.5 | 768 | 平衡效果 |
| BAAI/bge-large-zh-v1.5 | 1024 | 效果最好 |
| moka-ai/m3e-base | 768 | 多语言 |

### 4.3 API vs 本地模型对比

| 特性 | API调用 | 本地模型 |
|------|---------|----------|
| 速度 | 网络延迟 | 快（GPU加速） |
| 成本 | 按token付费 | 免费 |
| 隐私 | 数据发送到云 | 数据留在本地 |
| 维护 | 无需维护 | 需要GPU资源 |

---

## 5. 实战：简单语义搜索

```python
from openai import OpenAI
import numpy as np

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.deepseek.com/v1"
)

class SimpleSemanticSearch:
    def __init__(self):
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, docs: list[str]):
        """添加文档"""
        self.documents.extend(docs)
        
        # 获取embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=docs
        )
        new_embeddings = [item.embedding for item in response.data]
        self.embeddings.extend(new_embeddings)
    
    def search(self, query: str, top_k: int = 3) -> list[tuple[str, float]]:
        """搜索最相似的文档"""
        # 获取query的embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_emb = response.data[0].embedding
        
        # 计算相似度
        similarities = []
        for doc, emb in zip(self.documents, self.embeddings):
            sim = self._cosine_similarity(query_emb, emb)
            similarities.append((doc, sim))
        
        # 排序返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 使用
search = SimpleSemanticSearch()
search.add_documents([
    "FastAPI是一个现代、快速的Python Web框架",
    "Django是一个全功能的Python Web框架",
    "Flask是一个轻量级的Python Web框架",
    "NumPy是Python科学计算的基础库",
    "Pandas用于数据分析和处理"
])

results = search.search("高性能的API框架")
for doc, score in results:
    print(f"{score:.4f}: {doc}")
```

---

## 📺 推荐B站视频

在B站搜索以下关键词：
- **"Embedding 向量化 教程"** - 了解原理
- **"sentence-transformers 中文"** - 本地模型使用
- **"OpenAI Embedding API"** - API调用方法

---

## 6. 继续学习

📌 **Week 4 学习顺序**：
1. ✅ Embedding向量化入门（本教程）
2. ➡️ ChromaDB快速入门 或 Milvus向量数据库
3. ➡️ 检索策略详解
4. ➡️ 构建简单RAG系统

---

**Embedding是RAG系统的基石！💪**
