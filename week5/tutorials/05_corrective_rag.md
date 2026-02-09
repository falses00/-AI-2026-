# 📘 Corrective RAG (CRAG) 与 Self-Reflective RAG

> **学习目标**：掌握自我修正的RAG技术，显著降低幻觉率，提升回答可靠性

---

## 🎯 为什么需要修正机制？

传统RAG的问题：
```
用户问题: "FastAPI 3.0有什么新特性？"
         │
         ▼
┌─────────────────────────────────────┐
│ 检索结果（可能不相关或过时）         │
│ - FastAPI 0.100 更新日志            │
│ - Flask vs FastAPI 对比             │  ← 检索质量差
│ - Python Web框架概述                │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ LLM生成（基于低质量上下文）          │
│ → 产生幻觉或错误信息                 │
└─────────────────────────────────────┘
```

**解决方案**：在生成前评估检索质量，必要时修正

---

## 📚 Corrective RAG (CRAG) 架构

### 核心流程

```
用户问题
    │
    ▼
┌─────────────────┐
│   初始检索       │
│  (Top-K文档)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│        📊 检索评估器 (Retrieval Evaluator)        │
│  对每个文档评分: Correct / Ambiguous / Incorrect   │
└────────┬─────────────────┬──────────┬─────────────┘
         │                 │          │
    [全部正确]         [部分正确]    [全部错误]
         │                 │          │
         ▼                 ▼          ▼
    ┌─────────┐      ┌──────────┐  ┌───────────┐
    │直接使用  │      │知识精炼   │  │ 网络搜索  │
    │检索结果  │      │+补充搜索  │  │ 补充知识  │
    └────┬────┘      └─────┬────┘  └─────┬─────┘
         │                 │            │
         └─────────────────┼────────────┘
                           ▼
                    ┌─────────────┐
                    │ 知识精炼器   │
                    │ (分解重组)   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  LLM生成    │
                    └─────────────┘
```

---

## 💻 CRAG 实现

### 1. 检索评估器

```python
from openai import OpenAI
from pydantic import BaseModel
from enum import Enum

class RelevanceScore(str, Enum):
    CORRECT = "correct"       # 文档与问题高度相关
    AMBIGUOUS = "ambiguous"   # 部分相关，需要补充
    INCORRECT = "incorrect"   # 完全不相关

class DocumentEvaluation(BaseModel):
    relevance: RelevanceScore
    confidence: float         # 0-1 置信度
    reason: str              # 判断理由

class RetrievalEvaluator:
    """检索质量评估器"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.evaluation_prompt = """你是一个专业的文档相关性评估专家。

请评估以下检索到的文档与用户问题的相关性。

用户问题: {query}

检索文档:
{document}

请判断文档相关性:
- correct: 文档直接回答了问题或包含关键信息
- ambiguous: 文档部分相关，但信息不完整
- incorrect: 文档与问题无关

返回JSON格式:
{{"relevance": "correct/ambiguous/incorrect", "confidence": 0.0-1.0, "reason": "判断理由"}}
"""
    
    async def evaluate(self, query: str, document: str) -> DocumentEvaluation:
        """评估单个文档的相关性"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.evaluation_prompt.format(
                    query=query,
                    document=document[:2000]  # 截断长文档
                )
            }],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return DocumentEvaluation(**result)
    
    async def evaluate_batch(
        self, 
        query: str, 
        documents: list[str]
    ) -> list[DocumentEvaluation]:
        """批量评估文档"""
        import asyncio
        tasks = [self.evaluate(query, doc) for doc in documents]
        return await asyncio.gather(*tasks)
```

### 2. 知识精炼器

```python
class KnowledgeRefiner:
    """知识精炼器 - 提取文档中与问题相关的核心信息"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.refine_prompt = """你是一个专业的信息提取专家。

用户问题: {query}

文档内容:
{document}

请从文档中提取与问题直接相关的关键信息。
- 只保留回答问题所需的核心内容
- 去除无关信息和冗余内容
- 如果文档与问题无关，返回空字符串

提取的关键信息:"""

    async def refine(self, query: str, document: str) -> str:
        """精炼单个文档"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": self.refine_prompt.format(
                    query=query,
                    document=document
                )
            }],
            max_tokens=500,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    
    async def decompose_recompose(
        self, 
        query: str, 
        documents: list[str]
    ) -> str:
        """分解-重组算法：提取并整合所有相关信息"""
        import asyncio
        
        # 并行精炼所有文档
        refined_parts = await asyncio.gather(
            *[self.refine(query, doc) for doc in documents]
        )
        
        # 过滤空结果并组合
        valid_parts = [p for p in refined_parts if p.strip()]
        
        if not valid_parts:
            return ""
        
        return "\n\n---\n\n".join(valid_parts)
```

### 3. 完整CRAG Pipeline

```python
from typing import Optional
import httpx

class CorrectionAction(str, Enum):
    CORRECT = "use_retrieval"      # 直接使用检索结果
    AMBIGUOUS = "refine_and_search" # 精炼+补充搜索
    INCORRECT = "web_search"        # 网络搜索

class CRAGPipeline:
    """Corrective RAG 完整Pipeline"""
    
    def __init__(
        self, 
        client: OpenAI,
        vector_store,
        web_search_api_key: Optional[str] = None
    ):
        self.client = client
        self.vector_store = vector_store
        self.evaluator = RetrievalEvaluator(client)
        self.refiner = KnowledgeRefiner(client)
        self.web_search_key = web_search_api_key
    
    async def query(self, question: str) -> dict:
        """执行CRAG查询"""
        
        # Step 1: 初始检索
        retrieved_docs = self.vector_store.query(
            query_texts=[question],
            n_results=5
        )["documents"][0]
        
        # Step 2: 评估检索质量
        evaluations = await self.evaluator.evaluate_batch(
            question, retrieved_docs
        )
        
        # Step 3: 决定修正策略
        action = self._decide_action(evaluations)
        
        # Step 4: 根据策略处理
        if action == CorrectionAction.CORRECT:
            # 直接使用检索结果
            context = "\n\n".join(retrieved_docs)
            source = "retrieval"
            
        elif action == CorrectionAction.AMBIGUOUS:
            # 精炼现有文档 + 补充网络搜索
            refined = await self.refiner.decompose_recompose(
                question, retrieved_docs
            )
            web_results = await self._web_search(question) if self.web_search_key else ""
            context = f"{refined}\n\n[补充信息]\n{web_results}"
            source = "refined+web"
            
        else:  # INCORRECT
            # 完全依赖网络搜索
            context = await self._web_search(question) if self.web_search_key else ""
            source = "web_search"
        
        # Step 5: 生成回答
        answer = await self._generate_answer(question, context)
        
        return {
            "answer": answer,
            "action_taken": action.value,
            "source": source,
            "evaluations": [e.model_dump() for e in evaluations]
        }
    
    def _decide_action(
        self, 
        evaluations: list[DocumentEvaluation]
    ) -> CorrectionAction:
        """根据评估结果决定修正策略"""
        correct_count = sum(
            1 for e in evaluations 
            if e.relevance == RelevanceScore.CORRECT
        )
        incorrect_count = sum(
            1 for e in evaluations 
            if e.relevance == RelevanceScore.INCORRECT
        )
        
        total = len(evaluations)
        
        if correct_count >= total * 0.6:
            return CorrectionAction.CORRECT
        elif incorrect_count >= total * 0.8:
            return CorrectionAction.INCORRECT
        else:
            return CorrectionAction.AMBIGUOUS
    
    async def _web_search(self, query: str) -> str:
        """调用网络搜索API"""
        # 使用 Tavily/Serper/Bing 等搜索API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"query": query, "max_results": 3},
                headers={"Authorization": f"Bearer {self.web_search_key}"}
            )
            results = response.json().get("results", [])
            return "\n".join([r["content"] for r in results])
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """基于上下文生成回答"""
        if not context.strip():
            return "抱歉，我没有找到足够的信息来回答这个问题。"
        
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "基于提供的上下文回答问题。如果上下文不足，请说明。"
                },
                {
                    "role": "user",
                    "content": f"上下文:\n{context}\n\n问题: {question}"
                }
            ]
        )
        return response.choices[0].message.content
```

---

## 📚 Self-Reflective RAG

Self-Reflective RAG 在CRAG基础上增加了**迭代反思**能力。

### 核心特点

```
┌─────────────────────────────────────────────────────┐
│              Self-Reflective RAG                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. 检索 → 2. 评估 → 3. 生成 → 4. 反思              │
│                ↑                    │               │
│                └────────────────────┘               │
│                    (不满意则重新检索)                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 实现

```python
class SelfReflectiveRAG:
    """自反思RAG - 迭代优化回答质量"""
    
    def __init__(self, client: OpenAI, vector_store, max_iterations: int = 3):
        self.client = client
        self.vector_store = vector_store
        self.max_iterations = max_iterations
    
    async def query(self, question: str) -> dict:
        """带反思的RAG查询"""
        
        current_query = question
        iteration = 0
        history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # 检索
            docs = self.vector_store.query(
                query_texts=[current_query],
                n_results=5
            )["documents"][0]
            
            # 生成回答
            answer = await self._generate(question, docs)
            
            # 反思：评估回答质量
            reflection = await self._reflect(question, answer, docs)
            
            history.append({
                "iteration": iteration,
                "query": current_query,
                "answer": answer,
                "reflection": reflection
            })
            
            if reflection["is_satisfactory"]:
                # 回答满意，结束迭代
                break
            
            if reflection["needs_new_query"]:
                # 生成新的查询继续检索
                current_query = reflection["suggested_query"]
        
        return {
            "final_answer": history[-1]["answer"],
            "iterations": iteration,
            "history": history
        }
    
    async def _reflect(
        self, 
        original_question: str, 
        answer: str, 
        docs: list[str]
    ) -> dict:
        """反思回答质量"""
        
        prompt = f"""评估以下回答的质量：

原始问题: {original_question}

检索文档摘要: {docs[0][:500] if docs else '无'}

生成的回答: {answer}

请评估:
1. 回答是否完整回答了问题？
2. 回答是否有事实错误？
3. 是否需要更多信息？

返回JSON:
{{
    "is_satisfactory": true/false,
    "needs_new_query": true/false,
    "suggested_query": "如果需要，建议的新查询",
    "reason": "评估理由"
}}
"""
        
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    async def _generate(self, question: str, docs: list[str]) -> str:
        """生成回答"""
        context = "\n\n".join(docs)
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "基于文档回答问题。"},
                {"role": "user", "content": f"文档:\n{context}\n\n问题: {question}"}
            ]
        )
        return response.choices[0].message.content
```

---

## 🔗 与Week6 Agent的关系

> [!TIP]
> CRAG和Self-Reflective RAG的**自我评估和修正**机制，正是Agent的核心能力之一。
> 
> 在Week6中，你将学习如何将这种"思考-行动-观察"的循环扩展为完整的ReAct Agent。

---

## 📊 学习检查清单

- [ ] 理解CRAG的三种修正策略（Correct/Ambiguous/Incorrect）
- [ ] 能够实现检索评估器
- [ ] 掌握知识精炼（分解-重组）技术
- [ ] 理解Self-Reflective RAG的迭代机制
- [ ] 知道何时需要引入网络搜索补充

---

## 🎯 下一步

继续学习：
👉 [GraphRAG - 知识图谱增强检索](./06_graphrag.md)
