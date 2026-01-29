"""
Week 4 练习：RAG系统基础
=========================

完成以下练习来巩固RAG基础知识。
每个练习都有提示和参考答案。
"""

import os
from typing import Optional

# ============================================================
# 练习1: Embedding基础
# ============================================================

"""
练习1.1: 使用OpenAI API获取文本的embedding向量

要求：
1. 创建一个函数 get_embedding(text: str) -> list[float]
2. 使用DeepSeek API（兼容OpenAI格式）
3. 返回文本的向量表示

提示：使用 client.embeddings.create()
"""

def exercise_1_1():
    # TODO: 实现get_embedding函数
    def get_embedding(text: str) -> list[float]:
        # 你的代码
        pass
    
    # 测试
    text = "FastAPI是一个高性能Python框架"
    embedding = get_embedding(text)
    print(f"向量维度: {len(embedding)}")


"""
练习1.2: 计算两个文本的余弦相似度

要求：
1. 创建函数 cosine_similarity(vec1, vec2) -> float
2. 比较3个文本对的相似度
3. 解释结果

提示：使用numpy的dot和norm
"""

def exercise_1_2():
    import numpy as np
    
    # TODO: 实现余弦相似度函数
    def cosine_similarity(vec1, vec2) -> float:
        # 你的代码
        pass
    
    # 测试文本
    texts = [
        "Python是一种编程语言",
        "Python用于机器学习和数据分析",
        "今天天气很好"
    ]
    
    # TODO: 获取embeddings并计算相似度
    # 预期：前两个文本相似度高，第三个与前两个相似度低


# ============================================================
# 练习2: ChromaDB操作
# ============================================================

"""
练习2.1: 创建ChromaDB知识库

要求：
1. 创建一个持久化的ChromaDB客户端
2. 创建名为"tech_knowledge"的collection
3. 添加5个技术相关的文档
4. 为每个文档添加metadata（category, year）

提示：使用 chromadb.PersistentClient
"""

def exercise_2_1():
    import chromadb
    
    # TODO: 创建客户端和collection
    
    # TODO: 添加文档
    documents = [
        "FastAPI是2018年发布的Python Web框架",
        "Django是2005年发布的全功能框架",
        "React是Facebook开发的前端框架",
        "Vue.js是渐进式JavaScript框架",
        "TensorFlow是Google的机器学习框架"
    ]
    
    # TODO: 添加文档，包含category和year元数据


"""
练习2.2: 实现带过滤的查询

要求：
1. 查询"Python框架"相关内容
2. 过滤只返回category为"backend"的结果
3. 返回top 3结果

提示：使用collection.query()的where参数
"""

def exercise_2_2():
    # TODO: 实现带过滤的查询
    pass


# ============================================================
# 练习3: 检索策略
# ============================================================

"""
练习3.1: 实现动态阈值检索

要求：
1. 创建函数 dynamic_search(query, min_results=3)
2. 从阈值0.3开始，逐步放宽到0.5, 0.7, 1.0
3. 确保返回至少min_results个结果

提示：循环尝试不同阈值
"""

def exercise_3_1():
    # TODO: 实现动态阈值检索
    def dynamic_search(collection, query: str, min_results: int = 3):
        thresholds = [0.3, 0.5, 0.7, 1.0]
        # 你的代码
        pass


"""
练习3.2: 实现查询扩展

要求：
1. 创建同义词字典
2. 对查询进行同义词扩展
3. 使用多个查询进行检索并合并结果

提示：使用字符串replace进行扩展
"""

def exercise_3_2():
    synonyms = {
        "API": ["接口", "服务"],
        "框架": ["framework", "库"],
        "高性能": ["快速", "高效"]
    }
    
    def expand_query(query: str) -> list[str]:
        # TODO: 实现查询扩展
        pass
    
    # 测试
    queries = expand_query("高性能API框架")
    print(f"扩展后的查询: {queries}")


# ============================================================
# 练习4: 简单RAG系统
# ============================================================

"""
练习4.1: 构建完整的RAG问答函数

要求：
1. 整合embedding、检索、生成
2. 输入：问题字符串
3. 输出：包含answer和sources的字典

提示：参考04_simple_rag.md的SimpleRAG类
"""

def exercise_4_1():
    # TODO: 实现完整的RAG问答函数
    def rag_query(question: str, collection, llm_client) -> dict:
        # 1. 检索相关文档
        # 2. 构建prompt
        # 3. 调用LLM生成答案
        # 4. 返回结果
        pass


"""
练习4.2: 添加流式输出支持

要求：
1. 修改rag_query函数支持流式输出
2. 使用yield逐字返回
3. 创建FastAPI端点测试

提示：使用stream=True参数
"""

def exercise_4_2():
    # TODO: 实现流式RAG
    def rag_query_stream(question: str, collection, llm_client):
        # 你的代码（使用yield）
        pass


# ============================================================
# 参考答案
# ============================================================

def answer_1_1():
    """练习1.1参考答案"""
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    
    def get_embedding(text: str) -> list[float]:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    text = "FastAPI是一个高性能Python框架"
    embedding = get_embedding(text)
    print(f"向量维度: {len(embedding)}")
    return embedding


def answer_1_2():
    """练习1.2参考答案"""
    import numpy as np
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    
    def get_embedding(text: str) -> list[float]:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def cosine_similarity(vec1, vec2) -> float:
        a, b = np.array(vec1), np.array(vec2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    texts = [
        "Python是一种编程语言",
        "Python用于机器学习和数据分析",
        "今天天气很好"
    ]
    
    embeddings = [get_embedding(t) for t in texts]
    
    print("相似度矩阵:")
    for i in range(len(texts)):
        for j in range(len(texts)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            print(f"  {texts[i][:10]} vs {texts[j][:10]}: {sim:.4f}")


if __name__ == "__main__":
    print("Week 4 练习")
    print("=" * 50)
    print("请取消注释并运行各个练习函数")
    print("完成后对照参考答案检查")
    
    # 运行练习
    # exercise_1_1()
    # exercise_1_2()
    # exercise_2_1()
    # exercise_2_2()
    # exercise_3_1()
    # exercise_3_2()
    # exercise_4_1()
    # exercise_4_2()
    
    # 查看参考答案
    # answer_1_1()
    # answer_1_2()
