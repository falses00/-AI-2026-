# 📘 GraphRAG - 知识图谱增强检索

> **学习目标**：掌握GraphRAG技术，构建支持多跳推理的知识图谱RAG系统

---

## 🎯 为什么需要GraphRAG？

### 传统RAG的局限

```
问题: "A公司CEO的妻子在哪家公司工作？"

传统RAG检索:
- 文档1: "张三是A公司的CEO"
- 文档2: "李四在B公司担任产品经理"
- 文档3: "张三的妻子是李四"

问题: 三个文档分散，向量相似度无法建立"张三-妻子-李四-B公司"的关联
结果: 回答失败或产生幻觉
```

### GraphRAG的优势

```
知识图谱:
    ┌─────────┐    CEO    ┌─────────┐
    │  张三   │──────────→│  A公司  │
    └────┬────┘           └─────────┘
         │
    spouse (妻子)
         │
         ▼
    ┌─────────┐   works_at  ┌─────────┐
    │  李四   │────────────→│  B公司  │
    └─────────┘             └─────────┘

查询: 从"A公司CEO" → 张三 → 妻子 → 李四 → B公司
答案: "李四在B公司工作"
```

---

## 📚 GraphRAG 架构

### 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      GraphRAG Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐    ┌────────────────┐    ┌──────────────┐  │
│  │  文档/数据源    │ →  │  实体关系抽取   │ →  │  知识图谱    │  │
│  └────────────────┘    └────────────────┘    │  (Neo4j)     │  │
│                                              └───────┬──────┘  │
│                                                      │         │
│  ┌────────────────┐    ┌────────────────┐           │         │
│  │  用户问题       │ →  │  问题理解      │           │         │
│  └────────────────┘    │  + 实体识别    │           │         │
│                        └───────┬────────┘           │         │
│                                │                     │         │
│                                ▼                     ▼         │
│                        ┌────────────────────────────────┐     │
│                        │      图查询 + 向量检索          │     │
│                        │  (Cypher Query + Embedding)    │     │
│                        └─────────────┬──────────────────┘     │
│                                      │                         │
│                                      ▼                         │
│                        ┌────────────────────────────────┐     │
│                        │        上下文构建               │     │
│                        │  (实体+关系+相关文档)           │     │
│                        └─────────────┬──────────────────┘     │
│                                      │                         │
│                                      ▼                         │
│                        ┌────────────────────────────────┐     │
│                        │        LLM 生成回答            │     │
│                        └────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 实现GraphRAG

### 1. 环境准备

```bash
# 安装依赖
pip install neo4j langchain-community openai

# 启动Neo4j（Docker）
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

### 2. 实体关系抽取

```python
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

class Entity(BaseModel):
    name: str
    type: str  # Person, Organization, Location, Product, etc.
    description: Optional[str] = None

class Relationship(BaseModel):
    source: str      # 源实体名
    target: str      # 目标实体名
    relation: str    # 关系类型
    description: Optional[str] = None

class ExtractionResult(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]

class EntityRelationExtractor:
    """实体关系抽取器"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.extraction_prompt = """你是一个专业的知识图谱构建专家。

请从以下文本中抽取实体和关系：

文本:
{text}

要求:
1. 识别所有重要实体（人物、组织、地点、产品、概念等）
2. 识别实体之间的关系
3. 关系应该是动词或动词短语

返回JSON格式:
{{
    "entities": [
        {{"name": "实体名", "type": "类型", "description": "描述"}}
    ],
    "relationships": [
        {{"source": "源实体", "target": "目标实体", "relation": "关系", "description": "描述"}}
    ]
}}
"""
    
    async def extract(self, text: str) -> ExtractionResult:
        """从文本抽取实体和关系"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.extraction_prompt.format(text=text)
            }],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return ExtractionResult(**result)
```

### 3. Neo4j 图数据库操作

```python
from neo4j import GraphDatabase

class KnowledgeGraph:
    """知识图谱管理器"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def add_entity(self, entity: Entity):
        """添加实体节点"""
        query = """
        MERGE (e:{type} {{name: $name}})
        SET e.description = $description
        RETURN e
        """.format(type=entity.type.replace(" ", "_"))
        
        with self.driver.session() as session:
            session.run(query, 
                name=entity.name, 
                description=entity.description
            )
    
    def add_relationship(self, rel: Relationship):
        """添加关系边"""
        query = """
        MATCH (a), (b)
        WHERE a.name = $source AND b.name = $target
        MERGE (a)-[r:`{relation}`]->(b)
        SET r.description = $description
        RETURN r
        """.format(relation=rel.relation.replace(" ", "_").upper())
        
        with self.driver.session() as session:
            session.run(query,
                source=rel.source,
                target=rel.target,
                description=rel.description
            )
    
    def query_path(self, start_entity: str, end_entity: str, max_hops: int = 3) -> list:
        """查询两个实体间的路径（多跳推理）"""
        query = f"""
        MATCH path = shortestPath(
            (a {{name: $start}})-[*1..{max_hops}]-(b {{name: $end}})
        )
        RETURN path
        """
        
        with self.driver.session() as session:
            result = session.run(query, start=start_entity, end=end_entity)
            paths = []
            for record in result:
                path = record["path"]
                nodes = [node["name"] for node in path.nodes]
                rels = [rel.type for rel in path.relationships]
                paths.append({"nodes": nodes, "relationships": rels})
            return paths
    
    def query_neighbors(self, entity: str, depth: int = 2) -> dict:
        """查询实体的邻居节点"""
        query = f"""
        MATCH (e {{name: $name}})-[r*1..{depth}]-(neighbor)
        RETURN DISTINCT neighbor.name as name, 
               labels(neighbor)[0] as type,
               neighbor.description as description
        LIMIT 20
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=entity)
            return [dict(record) for record in result]
    
    def find_entities_by_query(self, query: str) -> list:
        """基于查询找到相关实体"""
        # 简单的模糊匹配，生产环境建议使用全文索引
        cypher = """
        MATCH (e)
        WHERE e.name CONTAINS $query OR e.description CONTAINS $query
        RETURN e.name as name, labels(e)[0] as type
        LIMIT 10
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, query=query)
            return [dict(record) for record in result]
```

### 4. 完整GraphRAG Pipeline

```python
class GraphRAGPipeline:
    """GraphRAG 完整Pipeline"""
    
    def __init__(
        self, 
        client: OpenAI,
        kg: KnowledgeGraph,
        vector_store=None  # 可选的向量存储
    ):
        self.client = client
        self.kg = kg
        self.vector_store = vector_store
        self.extractor = EntityRelationExtractor(client)
    
    async def index_document(self, text: str, doc_id: str):
        """索引文档到知识图谱"""
        # 抽取实体和关系
        extraction = await self.extractor.extract(text)
        
        # 添加到图数据库
        for entity in extraction.entities:
            self.kg.add_entity(entity)
        
        for rel in extraction.relationships:
            self.kg.add_relationship(rel)
        
        # 可选：同时加入向量存储
        if self.vector_store:
            self.vector_store.add(
                documents=[text],
                ids=[doc_id]
            )
        
        return extraction
    
    async def query(self, question: str) -> dict:
        """执行GraphRAG查询"""
        
        # Step 1: 从问题中识别实体
        entities_in_question = await self._extract_question_entities(question)
        
        # Step 2: 图查询 - 获取相关子图
        subgraph_context = []
        visited_entities = set()
        
        for entity in entities_in_question:
            if entity in visited_entities:
                continue
            
            # 获取邻居信息
            neighbors = self.kg.query_neighbors(entity, depth=2)
            subgraph_context.append({
                "entity": entity,
                "neighbors": neighbors
            })
            visited_entities.add(entity)
        
        # Step 3: 检查是否需要多跳推理
        if len(entities_in_question) >= 2:
            for i, e1 in enumerate(entities_in_question):
                for e2 in entities_in_question[i+1:]:
                    paths = self.kg.query_path(e1, e2)
                    if paths:
                        subgraph_context.append({
                            "path_query": f"{e1} -> {e2}",
                            "paths": paths
                        })
        
        # Step 4: 可选 - 结合向量检索
        vector_context = ""
        if self.vector_store:
            results = self.vector_store.query(
                query_texts=[question],
                n_results=3
            )
            vector_context = "\n".join(results["documents"][0])
        
        # Step 5: 构建上下文并生成回答
        context = self._build_context(subgraph_context, vector_context)
        answer = await self._generate_answer(question, context)
        
        return {
            "answer": answer,
            "entities_found": entities_in_question,
            "subgraph": subgraph_context
        }
    
    async def _extract_question_entities(self, question: str) -> list[str]:
        """从问题中抽取实体"""
        prompt = f"""从以下问题中识别关键实体名称（人名、公司名、地名等）：

问题: {question}

只返回实体名称列表，JSON格式:
{{"entities": ["实体1", "实体2"]}}
"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        # 验证实体是否在图中存在
        verified = []
        for entity in result.get("entities", []):
            found = self.kg.find_entities_by_query(entity)
            if found:
                verified.append(found[0]["name"])
        
        return verified
    
    def _build_context(self, subgraph: list, vector_text: str) -> str:
        """构建上下文"""
        parts = ["[知识图谱信息]"]
        
        for item in subgraph:
            if "entity" in item:
                parts.append(f"\n实体: {item['entity']}")
                if item["neighbors"]:
                    for n in item["neighbors"][:5]:
                        parts.append(f"  - 相关: {n['name']} ({n['type']})")
            
            if "paths" in item:
                parts.append(f"\n关系路径 ({item['path_query']}):")
                for path in item["paths"][:3]:
                    path_str = " -> ".join([
                        f"{path['nodes'][i]}--[{path['relationships'][i] if i < len(path['relationships']) else ''}]-->"
                        for i in range(len(path['nodes']))
                    ])
                    parts.append(f"  {path_str}")
        
        if vector_text:
            parts.append(f"\n[相关文档]\n{vector_text}")
        
        return "\n".join(parts)
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """生成回答"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个基于知识图谱的问答助手。
请根据提供的知识图谱信息和相关文档回答问题。
如果需要多跳推理，请明确说明推理过程。"""
                },
                {
                    "role": "user",
                    "content": f"知识库信息:\n{context}\n\n问题: {question}"
                }
            ]
        )
        return response.choices[0].message.content
```

---

## 🚀 使用示例

```python
import asyncio

async def main():
    # 初始化
    client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="your-key")
    kg = KnowledgeGraph("bolt://localhost:7687", "neo4j", "password123")
    pipeline = GraphRAGPipeline(client, kg)
    
    # 索引文档
    documents = [
        "张三是A科技公司的CEO，他于2020年创立了这家公司。",
        "李四是张三的妻子，她在B咨询公司担任高级顾问。",
        "A科技公司开发了智能助手产品SmartBot，获得了多项专利。",
        "B咨询公司是A科技公司的战略合作伙伴。"
    ]
    
    for i, doc in enumerate(documents):
        await pipeline.index_document(doc, f"doc_{i}")
        print(f"已索引文档 {i+1}")
    
    # 多跳推理查询
    result = await pipeline.query("A科技公司CEO的妻子在哪工作？")
    print(f"\n问题: A科技公司CEO的妻子在哪工作？")
    print(f"回答: {result['answer']}")
    print(f"推理路径: {result['subgraph']}")
    
    kg.close()

asyncio.run(main())
```

---

## 📊 GraphRAG vs 传统RAG

| 特性 | 传统RAG | GraphRAG |
|-----|--------|----------|
| 多跳推理 | ❌ 困难 | ✅ 原生支持 |
| 实体关系 | ❌ 隐式 | ✅ 显式建模 |
| 跨文档关联 | ⚠️ 依赖Embedding | ✅ 图连接 |
| 结构化查询 | ❌ 不支持 | ✅ Cypher |
| 索引成本 | 低 | 高（需抽取） |
| 适用场景 | 通用问答 | 复杂推理 |

---

## 🔗 与Week6 Agent的关系

> [!TIP]
> GraphRAG为Agent提供了强大的**知识推理**能力。
> 
> 在Week6学习Agent时，你将了解如何将GraphRAG作为Agent的工具，
> 让Agent自主决定何时需要进行图查询来完成复杂推理任务。

---

## 📊 学习检查清单

- [ ] 理解GraphRAG解决的核心问题（多跳推理）
- [ ] 能够实现实体关系抽取
- [ ] 掌握Neo4j基本操作（Cypher查询）
- [ ] 理解图查询与向量检索的结合
- [ ] 知道GraphRAG的适用场景

---

## 🎯 下一步

继续学习：
👉 [Agentic RAG - Agent驱动的智能检索](./07_agentic_rag.md)
