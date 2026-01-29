# 🔗 使用LangChain构建混合检索

> **学习目标**：使用LangChain框架快速实现混合检索

---

## 1. LangChain简介

**LangChain**是构建LLM应用的流行框架，提供了丰富的检索组件。

---

## 2. 安装依赖

```bash
pip install langchain langchain-openai langchain-community chromadb rank-bm25
```

---

## 3. LangChain检索器

### 3.1 向量检索器

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# 创建embedding
embeddings = OpenAIEmbeddings(
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 创建文档
docs = [
    Document(page_content="FastAPI是高性能Python框架", metadata={"source": "web"}),
    Document(page_content="Django是全功能Web框架", metadata={"source": "web"}),
    Document(page_content="向量数据库存储embedding", metadata={"source": "db"}),
]

# 创建向量存储
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./langchain_db"
)

# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 检索
results = retriever.invoke("Python Web开发")
for doc in results:
    print(doc.page_content)
```

### 3.2 BM25检索器

```python
from langchain_community.retrievers import BM25Retriever

# 创建BM25检索器
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3

# 检索
results = bm25_retriever.invoke("Python框架")
for doc in results:
    print(doc.page_content)
```

---

## 4. 混合检索器

### 4.1 EnsembleRetriever

```python
from langchain.retrievers import EnsembleRetriever

# 创建向量检索器
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 创建BM25检索器
bm25_retriever = BM25Retriever.from_documents(docs, k=5)

# 创建混合检索器（RRF融合）
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]  # 语义:关键词 = 6:4
)

# 检索
results = ensemble_retriever.invoke("高性能API开发")
for doc in results:
    print(f"- {doc.page_content}")
```

### 4.2 自定义权重

```python
# 更侧重语义
semantic_heavy = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.8, 0.2]
)

# 更侧重关键词
keyword_heavy = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.3, 0.7]
)
```

---

## 5. 完整RAG with混合检索

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document

# 1. 准备文档
documents = [
    Document(page_content="FastAPI是一个现代、快速的Python Web框架，性能与Go和Node.js相当。"),
    Document(page_content="FastAPI使用Pydantic进行数据验证，自动生成OpenAPI文档。"),
    Document(page_content="Django是Python的全功能Web框架，适合大型项目。"),
    Document(page_content="Flask是轻量级Python微框架，灵活但功能较少。"),
    Document(page_content="向量数据库如ChromaDB用于存储和检索文本embedding。")
]

# 2. 创建检索器
embeddings = OpenAIEmbeddings(
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

vectorstore = Chroma.from_documents(documents, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

bm25_retriever = BM25Retriever.from_documents(documents, k=3)

# 混合检索器
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]
)

# 3. 创建LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 4. 创建Prompt
prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题：

上下文：
{context}

问题：{question}

请简洁准确地回答：
""")

# 5. 构建RAG Chain (LCEL语法)
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": hybrid_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. 使用
answer = rag_chain.invoke("FastAPI有什么特点？")
print(answer)
```

---

## 6. 多查询检索器

```python
from langchain.retrievers import MultiQueryRetriever

# 自动生成多个查询变体
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=hybrid_retriever,
    llm=llm
)

# 检索（会自动生成多个相关查询）
results = multi_query_retriever.invoke("Python Web框架对比")
```

---

## 7. 上下文压缩检索器

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# 创建压缩器
compressor = LLMChainExtractor.from_llm(llm)

# 创建压缩检索器
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=hybrid_retriever
)

# 检索（会自动提取相关内容）
results = compression_retriever.invoke("FastAPI性能如何？")
for doc in results:
    print(doc.page_content)
```

---

## 8. 完整示例：知识库问答

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class LangChainRAG:
    def __init__(self, docs_path: str = "./knowledge"):
        # 加载文档
        loader = DirectoryLoader(docs_path, glob="**/*.md", loader_cls=TextLoader)
        documents = loader.load()
        
        # 分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = splitter.split_documents(documents)
        
        # 创建检索器
        embeddings = OpenAIEmbeddings(
            openai_api_key="your-key",
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        vectorstore = Chroma.from_documents(splits, embeddings)
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        bm25_retriever = BM25Retriever.from_documents(splits, k=5)
        
        self.retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.6, 0.4]
        )
        
        # 创建LLM
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key="your-key",
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        # 创建对话记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 创建对话链
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            verbose=True
        )
    
    def chat(self, question: str) -> str:
        result = self.chain({"question": question})
        return result["answer"]

# 使用
rag = LangChainRAG("./knowledge")
print(rag.chat("FastAPI是什么？"))
print(rag.chat("它和Django有什么区别？"))  # 会记住上下文
```

---

## 📺 推荐B站视频

搜索：
- **"LangChain RAG 教程"**
- **"LangChain 混合检索"**
- **"LCEL 表达式语言"**

---

## 9. 继续学习

📌 **Week 5 学习顺序**：
1. ✅ 混合检索（原生或LangChain）
2. ➡️ 重排序模型详解
3. ➡️ 上下文压缩技术
4. ➡️ 高级RAG Pipeline

---

**LangChain让RAG开发更加简单！💪**
