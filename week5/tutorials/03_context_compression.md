# 📦 上下文压缩技术

> **学习目标**：掌握上下文压缩技术，提升RAG效率和效果

---

## 1. 为什么需要上下文压缩？

### 问题1：检索结果太多

```
检索返回5个文档，每个1000字 → 5000字上下文
LLM上下文窗口有限 + 费用高
```

### 问题2：噪音太多

```
检索到的文档：
"FastAPI是一个现代Python框架。它由Sebastián Ramírez创建。
FastAPI支持异步。安装命令是pip install fastapi。
FastAPI的性能非常好，接近Go语言。"
                    ↑
用户问的是"FastAPI性能"，只有最后一句才是答案
```

### 解决方案：上下文压缩

**只保留与问题相关的内容！**

---

## 2. 压缩方法

### 2.1 LLM提取（最精准）

让LLM提取相关信息：

```python
from openai import OpenAI

def compress_with_llm(query: str, document: str, client: OpenAI) -> str:
    """使用LLM压缩文档"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user",
            "content": f"""从以下文档中提取与问题相关的信息。只输出相关内容，不要解释。
如果没有相关内容，输出"无相关内容"。

问题：{query}

文档：
{document}

相关内容："""
        }],
        temperature=0,
        max_tokens=500
    )
    return response.choices[0].message.content

# 使用
doc = """FastAPI是一个现代Python框架。它由Sebastián Ramírez创建。
FastAPI支持异步。安装命令是pip install fastapi。
FastAPI的性能非常好，接近Go语言，QPS可达10000+。"""

compressed = compress_with_llm("FastAPI性能如何?", doc, client)
print(compressed)
# 输出: FastAPI的性能非常好，接近Go语言，QPS可达10000+。
```

### 2.2 基于句子的提取

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def sentence_extraction(query: str, document: str, top_k: int = 3) -> str:
    """提取最相关的句子"""
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    
    # 分句
    sentences = [s.strip() for s in document.split('。') if s.strip()]
    
    # 编码
    query_emb = model.encode([query])
    sent_embs = model.encode(sentences)
    
    # 计算相似度
    similarities = np.dot(sent_embs, query_emb.T).flatten()
    
    # 获取Top-K句子
    top_indices = similarities.argsort()[-top_k:][::-1]
    top_sentences = [sentences[i] for i in sorted(top_indices)]
    
    return '。'.join(top_sentences) + '。'

# 使用
compressed = sentence_extraction("FastAPI性能", doc, top_k=2)
```

### 2.3 关键词过滤

```python
import jieba

def keyword_filter(query: str, document: str, threshold: float = 0.3) -> str:
    """保留包含查询关键词的句子"""
    query_words = set(jieba.cut(query))
    sentences = [s.strip() for s in document.split('。') if s.strip()]
    
    relevant = []
    for sent in sentences:
        sent_words = set(jieba.cut(sent))
        overlap = len(query_words & sent_words) / len(query_words)
        if overlap >= threshold:
            relevant.append(sent)
    
    return '。'.join(relevant) + '。' if relevant else document
```

---

## 3. 完整压缩器类

```python
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from enum import Enum

class CompressionMethod(Enum):
    LLM = "llm"
    SENTENCE = "sentence"
    KEYWORD = "keyword"

class ContextCompressor:
    def __init__(
        self, 
        method: CompressionMethod = CompressionMethod.SENTENCE,
        llm_client: OpenAI = None
    ):
        self.method = method
        self.llm_client = llm_client
        
        if method == CompressionMethod.SENTENCE:
            self.encoder = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    
    def compress(
        self, 
        query: str, 
        documents: list[str],
        max_length: int = 2000
    ) -> str:
        """压缩多个文档"""
        compressed_docs = []
        
        for doc in documents:
            if self.method == CompressionMethod.LLM:
                compressed = self._compress_llm(query, doc)
            elif self.method == CompressionMethod.SENTENCE:
                compressed = self._compress_sentence(query, doc)
            else:
                compressed = self._compress_keyword(query, doc)
            
            if compressed and compressed != "无相关内容":
                compressed_docs.append(compressed)
        
        # 合并并截断
        result = "\n\n".join(compressed_docs)
        if len(result) > max_length:
            result = result[:max_length] + "..."
        
        return result
    
    def _compress_llm(self, query: str, document: str) -> str:
        if not self.llm_client:
            raise ValueError("LLM压缩需要提供llm_client")
        
        response = self.llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": f"""提取与问题相关的信息：

问题：{query}
文档：{document}

相关内容（如果没有则输出"无相关内容"）："""
            }],
            temperature=0,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def _compress_sentence(self, query: str, document: str, top_k: int = 3) -> str:
        sentences = [s.strip() for s in document.replace('\n', '。').split('。') if s.strip()]
        
        if len(sentences) <= top_k:
            return document
        
        query_emb = self.encoder.encode([query])
        sent_embs = self.encoder.encode(sentences)
        
        similarities = np.dot(sent_embs, query_emb.T).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        top_sentences = [sentences[i] for i in sorted(top_indices)]
        
        return '。'.join(top_sentences) + '。'
    
    def _compress_keyword(self, query: str, document: str) -> str:
        import jieba
        query_words = set(jieba.cut(query))
        sentences = [s.strip() for s in document.split('。') if s.strip()]
        
        relevant = [s for s in sentences 
                   if any(w in s for w in query_words if len(w) > 1)]
        
        return '。'.join(relevant) + '。' if relevant else ""

# 使用
compressor = ContextCompressor(method=CompressionMethod.SENTENCE)
compressed = compressor.compress(
    query="FastAPI性能",
    documents=[doc1, doc2, doc3]
)
```

---

## 4. 集成到RAG

```python
import chromadb
from openai import OpenAI

class RAGWithCompression:
    def __init__(self):
        self.chroma = chromadb.PersistentClient(path="./compress_db")
        self.collection = self.chroma.get_or_create_collection("docs")
        self.llm = OpenAI(api_key="key", base_url="https://api.deepseek.com/v1")
        self.compressor = ContextCompressor(
            method=CompressionMethod.LLM,
            llm_client=self.llm
        )
    
    def add_documents(self, docs: list[str]):
        ids = [f"doc_{i}" for i in range(len(docs))]
        self.collection.upsert(documents=docs, ids=ids)
    
    def query(self, question: str) -> str:
        # 1. 检索
        results = self.collection.query(
            query_texts=[question],
            n_results=10
        )
        documents = results["documents"][0]
        
        # 2. 压缩
        compressed_context = self.compressor.compress(
            query=question,
            documents=documents,
            max_length=2000
        )
        
        # 3. 生成回答
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "根据提供的信息回答问题。"},
                {"role": "user", "content": f"信息：{compressed_context}\n\n问题：{question}"}
            ]
        )
        
        return response.choices[0].message.content

# 使用
rag = RAGWithCompression()
rag.add_documents([...])
answer = rag.query("FastAPI的主要优势是什么？")
```

---

## 5. LangChain上下文压缩

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI

# 创建LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 创建压缩器
compressor = LLMChainExtractor.from_llm(llm)

# 创建压缩检索器
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_retriever  # 你的基础检索器
)

# 使用
docs = compression_retriever.invoke("FastAPI性能")
for doc in docs:
    print(doc.page_content)  # 已压缩的内容
```

---

## 6. 压缩效果对比

| 方法 | 压缩率 | 精度 | 速度 | 成本 |
|------|--------|------|------|------|
| LLM | 高 | 最高 | 慢 | 高 |
| Sentence | 中 | 高 | 快 | 无 |
| Keyword | 低 | 中 | 最快 | 无 |

**建议**：
- 开发测试：Sentence
- 生产环境：LLM（精度要求高）或Sentence（成本敏感）

---

## 📺 推荐B站视频

搜索：
- **"RAG 上下文压缩"**
- **"LangChain Compression"**
- **"Context Window 优化"**

---

## 7. 继续学习

📌 **Week 5 学习顺序**：
1. ✅ 混合检索
2. ✅ 重排序模型
3. ✅ 上下文压缩技术（本教程）
4. ➡️ 高级RAG Pipeline

---

**压缩让RAG更高效！💪**
