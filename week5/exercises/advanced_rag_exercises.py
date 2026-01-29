"""
Week 5 练习：高级RAG技术
=========================

完成以下练习来掌握高级RAG技术。
"""

import os
from typing import List, Dict
import numpy as np

# ============================================================
# 练习1: 混合检索
# ============================================================

"""
练习1.1: 实现BM25检索器

要求：
1. 使用rank_bm25库实现BM25Retriever类
2. 支持中文分词（使用jieba）
3. 实现search(query, top_k)方法

提示：安装 pip install rank-bm25 jieba
"""

def exercise_1_1():
    from rank_bm25 import BM25Okapi
    import jieba
    
    class BM25Retriever:
        def __init__(self, documents: list[str]):
            # TODO: 初始化BM25
            pass
        
        def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
            # TODO: 实现搜索
            pass
    
    # 测试
    docs = [
        "FastAPI是高性能Python框架",
        "BM25是经典的关键词检索算法",
        "Python可以用于机器学习",
    ]
    retriever = BM25Retriever(docs)
    results = retriever.search("Python框架", top_k=2)
    for doc, score in results:
        print(f"[{score:.2f}] {doc}")


"""
练习1.2: 实现RRF融合算法

要求：
1. 输入多个排序列表
2. 使用RRF公式计算融合分数
3. 返回统一排序的结果

公式：RRF_score = Σ 1/(k + rank_i)，k通常取60
"""

def exercise_1_2():
    def rrf_fusion(
        result_lists: list[list[tuple[str, float]]], 
        k: int = 60
    ) -> list[tuple[str, float]]:
        # TODO: 实现RRF融合
        pass
    
    # 测试
    semantic_results = [("doc1", 0.9), ("doc2", 0.8), ("doc3", 0.7)]
    keyword_results = [("doc2", 5.0), ("doc4", 4.0), ("doc1", 3.0)]
    
    fused = rrf_fusion([semantic_results, keyword_results])
    print("融合后结果:", fused)


"""
练习1.3: 构建完整的混合检索器

要求：
1. 整合语义检索（ChromaDB）和关键词检索（BM25）
2. 使用RRF或加权融合
3. 支持调节权重参数
"""

def exercise_1_3():
    # TODO: 实现完整的HybridRetriever类
    class HybridRetriever:
        def __init__(self, alpha: float = 0.5):
            # alpha: 语义检索权重
            pass
        
        def add_documents(self, documents: list[str]):
            pass
        
        def search(self, query: str, top_k: int = 5) -> list[dict]:
            pass


# ============================================================
# 练习2: 重排序
# ============================================================

"""
练习2.1: 使用Cross-Encoder重排序

要求：
1. 加载cross-encoder模型
2. 对检索结果进行重排序
3. 比较重排前后的顺序变化

提示：pip install sentence-transformers
"""

def exercise_2_1():
    from sentence_transformers import CrossEncoder
    
    # TODO: 加载模型并重排序
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    query = "FastAPI的性能如何？"
    documents = [
        "FastAPI安装很简单，pip install fastapi",
        "FastAPI性能非常好，可达到10000+ QPS",
        "Django是一个全功能框架",
    ]
    
    # TODO: 计算分数并排序


"""
练习2.2: 集成Reranker到RAG

要求：
1. 先用向量检索获取top 20
2. 再用Reranker重排序获取top 5
3. 比较检索质量
"""

def exercise_2_2():
    # TODO: 实现两阶段检索
    def retrieve_and_rerank(query: str, collection, reranker, 
                           initial_k: int = 20, final_k: int = 5):
        pass


# ============================================================
# 练习3: 上下文压缩
# ============================================================

"""
练习3.1: 实现句子级压缩

要求：
1. 将文档分割成句子
2. 计算每个句子与查询的相似度
3. 只保留最相关的N个句子

提示：使用sentence-transformers计算相似度
"""

def exercise_3_1():
    from sentence_transformers import SentenceTransformer
    
    def compress_by_sentences(query: str, document: str, top_k: int = 3) -> str:
        # TODO: 实现句子级压缩
        pass
    
    # 测试
    doc = """FastAPI是一个现代Python框架。它由Sebastián Ramírez创建。
    FastAPI的性能非常好。它使用Pydantic进行数据验证。
    FastAPI自动生成API文档。安装方式是pip install fastapi。"""
    
    compressed = compress_by_sentences("FastAPI的性能", doc, top_k=2)
    print("压缩后:", compressed)


"""
练习3.2: 实现LLM压缩

要求：
1. 使用LLM提取与问题相关的内容
2. 比较与句子压缩的效果差异
3. 评估压缩率和信息保留度
"""

def exercise_3_2():
    from openai import OpenAI
    
    def compress_with_llm(query: str, document: str, client: OpenAI) -> str:
        # TODO: 使用LLM压缩
        pass


# ============================================================
# 练习4: 高级Pipeline
# ============================================================

"""
练习4.1: 实现查询改写

要求：
1. 使用LLM将用户查询改写成多个变体
2. 使用所有变体进行检索
3. 合并去重结果
"""

def exercise_4_1():
    def rewrite_query(query: str, client) -> list[str]:
        # TODO: 使用LLM改写查询
        pass
    
    def multi_query_search(query: str, collection, client) -> list[str]:
        # TODO: 使用多个查询变体检索
        pass


"""
练习4.2: 构建完整的高级RAG Pipeline

要求：
1. 整合所有技术：混合检索 + 重排序 + 压缩
2. 支持流式输出
3. 返回详细的执行信息
"""

def exercise_4_2():
    class AdvancedRAGPipeline:
        def __init__(self):
            # TODO: 初始化各组件
            pass
        
        def query(self, question: str) -> dict:
            """
            返回:
            {
                "answer": str,
                "sources": list,
                "steps": {
                    "rewrite": list[str],
                    "retrieved": int,
                    "reranked": int,
                    "compressed_length": int
                }
            }
            """
            pass


# ============================================================
# 参考答案
# ============================================================

def answer_1_1():
    """练习1.1参考答案"""
    from rank_bm25 import BM25Okapi
    import jieba
    
    class BM25Retriever:
        def __init__(self, documents: list[str]):
            self.documents = documents
            self.tokenized = [list(jieba.cut(doc)) for doc in documents]
            self.bm25 = BM25Okapi(self.tokenized)
        
        def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
            query_tokens = list(jieba.cut(query))
            scores = self.bm25.get_scores(query_tokens)
            
            # 获取top-k
            top_indices = scores.argsort()[-top_k:][::-1]
            return [(self.documents[i], scores[i]) for i in top_indices]
    
    # 测试
    docs = [
        "FastAPI是高性能Python框架",
        "BM25是经典的关键词检索算法",
        "Python可以用于机器学习",
    ]
    retriever = BM25Retriever(docs)
    results = retriever.search("Python框架", top_k=2)
    for doc, score in results:
        print(f"[{score:.2f}] {doc}")


def answer_1_2():
    """练习1.2参考答案"""
    def rrf_fusion(
        result_lists: list[list[tuple[str, float]]], 
        k: int = 60
    ) -> list[tuple[str, float]]:
        scores = {}
        
        for results in result_lists:
            for rank, (doc, _) in enumerate(results):
                if doc not in scores:
                    scores[doc] = 0
                scores[doc] += 1 / (k + rank + 1)
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    semantic_results = [("doc1", 0.9), ("doc2", 0.8), ("doc3", 0.7)]
    keyword_results = [("doc2", 5.0), ("doc4", 4.0), ("doc1", 3.0)]
    
    fused = rrf_fusion([semantic_results, keyword_results])
    print("融合后结果:", fused)


if __name__ == "__main__":
    print("Week 5 练习")
    print("=" * 50)
    print("请取消注释并运行各个练习函数")
    
    # exercise_1_1()
    # exercise_1_2()
    # exercise_2_1()
    # exercise_3_1()
    # exercise_4_2()
    
    # 参考答案
    # answer_1_1()
    # answer_1_2()
