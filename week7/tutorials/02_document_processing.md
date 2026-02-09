# 📄 多格式文档处理Pipeline

> **学习目标**：构建支持PDF、Word、网页的统一文档处理系统

---

## 1. 文档处理架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    文档处理Pipeline架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  PDF    │  │  Word   │  │  HTML   │  │  TXT    │            │
│  │ 文档    │  │ 文档    │  │ 网页    │  │ 文本    │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
│       │            │            │            │                  │
│       └────────────┴────────────┴────────────┘                  │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                            │
│              │   DocumentLoader     │                            │
│              │   (统一加载接口)      │                            │
│              └──────────┬───────────┘                            │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                            │
│              │   TextSplitter       │                            │
│              │   (智能分块)          │                            │
│              └──────────┬───────────┘                            │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                            │
│              │   Embedder           │                            │
│              │   (向量化)            │                            │
│              └──────────┬───────────┘                            │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                            │
│              │   VectorStore        │                            │
│              │   (ChromaDB/Milvus)  │                            │
│              └──────────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PDF文档处理

### 2.1 安装依赖

```bash
pip install pdfplumber pymupdf pypdf2
```

### 2.2 PDF解析器

```python
import pdfplumber
from dataclasses import dataclass
from typing import Optional

@dataclass
class PDFPage:
    """PDF页面数据"""
    page_num: int
    text: str
    tables: list[list[list[str]]]
    images: list[bytes]

@dataclass 
class PDFDocument:
    """PDF文档数据"""
    filename: str
    pages: list[PDFPage]
    metadata: dict

class PDFParser:
    """PDF解析器"""
    
    def parse(self, file_path: str) -> PDFDocument:
        """解析PDF文件"""
        pages = []
        
        with pdfplumber.open(file_path) as pdf:
            metadata = pdf.metadata or {}
            
            for i, page in enumerate(pdf.pages):
                # 提取文本
                text = page.extract_text() or ""
                
                # 提取表格
                tables = page.extract_tables() or []
                
                # 提取图片（简化处理）
                images = []
                
                pages.append(PDFPage(
                    page_num=i + 1,
                    text=text,
                    tables=tables,
                    images=images
                ))
        
        return PDFDocument(
            filename=file_path,
            pages=pages,
            metadata=metadata
        )
    
    def extract_text(self, file_path: str) -> str:
        """只提取文本"""
        doc = self.parse(file_path)
        return "\n\n".join(page.text for page in doc.pages)

# 使用
parser = PDFParser()
doc = parser.parse("example.pdf")
print(f"共 {len(doc.pages)} 页")
print(f"第1页文本: {doc.pages[0].text[:200]}...")
```

---

## 3. Word文档处理

### 3.1 安装依赖

```bash
pip install python-docx
```

### 3.2 Word解析器

```python
from docx import Document
from docx.table import Table
from dataclasses import dataclass

@dataclass
class WordDocument:
    """Word文档数据"""
    filename: str
    paragraphs: list[str]
    tables: list[list[list[str]]]
    metadata: dict

class WordParser:
    """Word解析器"""
    
    def parse(self, file_path: str) -> WordDocument:
        """解析Word文件"""
        doc = Document(file_path)
        
        # 提取段落
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # 提取表格
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        
        # 提取元数据
        metadata = {
            "author": doc.core_properties.author,
            "title": doc.core_properties.title,
            "created": str(doc.core_properties.created),
        }
        
        return WordDocument(
            filename=file_path,
            paragraphs=paragraphs,
            tables=tables,
            metadata=metadata
        )
    
    def extract_text(self, file_path: str) -> str:
        """只提取文本"""
        doc = self.parse(file_path)
        return "\n\n".join(doc.paragraphs)

# 使用
parser = WordParser()
doc = parser.parse("example.docx")
print(f"共 {len(doc.paragraphs)} 个段落")
```

---

## 4. 网页内容处理

### 4.1 安装依赖

```bash
pip install beautifulsoup4 httpx trafilatura
```

### 4.2 网页解析器

```python
import httpx
from bs4 import BeautifulSoup
import trafilatura
from dataclasses import dataclass

@dataclass
class WebPage:
    """网页数据"""
    url: str
    title: str
    text: str
    links: list[str]
    metadata: dict

class WebParser:
    """网页解析器"""
    
    async def fetch(self, url: str) -> str:
        """获取网页内容"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
    
    def parse(self, html: str, url: str) -> WebPage:
        """解析HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.title.string if soup.title else ""
        
        # 使用trafilatura提取正文（过滤广告、导航等）
        text = trafilatura.extract(html) or ""
        
        # 提取链接
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http'):
                links.append(href)
        
        return WebPage(
            url=url,
            title=title,
            text=text,
            links=links[:20],  # 只保留前20个链接
            metadata={"source": "web"}
        )
    
    async def parse_url(self, url: str) -> WebPage:
        """从URL解析网页"""
        html = await self.fetch(url)
        return self.parse(html, url)

# 使用
import asyncio

async def main():
    parser = WebParser()
    page = await parser.parse_url("https://example.com")
    print(f"标题: {page.title}")
    print(f"正文: {page.text[:500]}...")

asyncio.run(main())
```

---

## 5. 统一文档加载器

```python
from pathlib import Path
from typing import Union
from enum import Enum

class DocumentType(Enum):
    PDF = "pdf"
    WORD = "docx"
    TEXT = "txt"
    HTML = "html"
    WEB = "web"

@dataclass
class Document:
    """统一文档格式"""
    source: str
    doc_type: DocumentType
    content: str
    metadata: dict
    chunks: list[str] = None

class UnifiedDocumentLoader:
    """统一文档加载器"""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.word_parser = WordParser()
        self.web_parser = WebParser()
    
    def load(self, source: str) -> Document:
        """加载文档"""
        # 判断类型
        if source.startswith("http"):
            return self._load_web(source)
        
        path = Path(source)
        suffix = path.suffix.lower()
        
        if suffix == ".pdf":
            return self._load_pdf(source)
        elif suffix in [".docx", ".doc"]:
            return self._load_word(source)
        elif suffix == ".txt":
            return self._load_text(source)
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
    
    def _load_pdf(self, path: str) -> Document:
        text = self.pdf_parser.extract_text(path)
        return Document(
            source=path,
            doc_type=DocumentType.PDF,
            content=text,
            metadata={"type": "pdf"}
        )
    
    def _load_word(self, path: str) -> Document:
        text = self.word_parser.extract_text(path)
        return Document(
            source=path,
            doc_type=DocumentType.WORD,
            content=text,
            metadata={"type": "word"}
        )
    
    def _load_text(self, path: str) -> Document:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        return Document(
            source=path,
            doc_type=DocumentType.TEXT,
            content=text,
            metadata={"type": "text"}
        )
    
    async def _load_web(self, url: str) -> Document:
        page = await self.web_parser.parse_url(url)
        return Document(
            source=url,
            doc_type=DocumentType.WEB,
            content=page.text,
            metadata={"type": "web", "title": page.title}
        )

# 使用
loader = UnifiedDocumentLoader()
doc = loader.load("report.pdf")
print(f"内容长度: {len(doc.content)} 字符")
```

---

## 6. 智能文本分块

```python
from typing import List

class SmartTextSplitter:
    """智能文本分块器"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", ".", " "]
    
    def split(self, text: str) -> list[str]:
        """分割文本"""
        chunks = []
        current_chunk = ""
        
        # 按段落分割
        paragraphs = text.split("\n\n")
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 处理重叠
        if self.chunk_overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # 添加前一个chunk的末尾作为上下文
                    prev_tail = chunks[i-1][-self.chunk_overlap:]
                    chunk = prev_tail + "\n...\n" + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks
        
        return chunks

# 使用
splitter = SmartTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split(long_text)
print(f"分成 {len(chunks)} 个块")
```

---

## 7. 学习检查清单

- [ ] 能够解析PDF文档并提取表格
- [ ] 能够解析Word文档
- [ ] 能够爬取网页并提取正文
- [ ] 理解文本分块策略

---

## 继续学习

📌 **Week 7 学习顺序**：
1. ✅ 企业级系统架构
2. ✅ 多格式文档处理（本教程）
3. ➡️ 用户认证与权限
4. ➡️ 云平台部署
