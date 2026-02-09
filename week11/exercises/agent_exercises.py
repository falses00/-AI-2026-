# 💻 Agent开发练习

"""
Week 9-11 Agent开发练习
涵盖：微调数据准备、Agent记忆、多Agent协作
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import json


# ============================================
# 练习1：微调数据构建
# ============================================

class ConversationSample(BaseModel):
    """对话样本"""
    messages: List[Dict[str, str]]
    quality_score: Optional[float] = None


def exercise_1_build_finetune_data(
    raw_conversations: List[dict]
) -> List[dict]:
    """
    练习1：构建微调数据集
    
    要求：
    1. 过滤掉低质量对话（少于2轮、空消息等）
    2. 转换为OpenAI微调格式
    3. 添加system message
    4. 输出JSONL格式数据
    
    输入格式：
    [
        {"user": "你好", "assistant": "你好！有什么可以帮助你的？"},
        ...
    ]
    
    输出格式（OpenAI格式）：
    {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
    """
    # TODO: 实现你的代码
    formatted_data = []
    
    for conv in raw_conversations:
        # 质量过滤
        if not conv.get("user") or not conv.get("assistant"):
            continue
        if len(conv.get("user", "")) < 2:
            continue
            
        # 转换格式
        sample = {
            "messages": [
                {"role": "system", "content": "你是一个专业的AI助手，回答准确、简洁、友好。"},
                {"role": "user", "content": conv["user"]},
                {"role": "assistant", "content": conv["assistant"]}
            ]
        }
        formatted_data.append(sample)
    
    return formatted_data


# ============================================
# 练习2：短期记忆实现
# ============================================

class ShortTermMemory:
    """
    练习2：实现短期记忆管理
    
    要求：
    1. 支持添加消息
    2. 支持按token限制获取上下文
    3. 支持清空记忆
    4. 支持摘要压缩（bonus）
    """
    
    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []
    
    def add(self, role: str, content: str):
        """添加消息"""
        # TODO: 实现添加逻辑，注意不要超过max_messages
        pass
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取上下文（不超过max_tokens）"""
        # TODO: 实现获取逻辑
        pass
    
    def clear(self):
        """清空记忆"""
        # TODO: 实现清空逻辑
        pass
    
    def summarize(self) -> str:
        """摘要压缩（bonus）"""
        # TODO: 使用LLM压缩历史对话
        pass


# ============================================
# 练习3：工具注册与调用
# ============================================

class ToolRegistry:
    """
    练习3：实现工具注册中心
    
    要求：
    1. 支持注册工具（带描述和参数定义）
    2. 支持列出所有工具
    3. 支持根据名称调用工具
    4. 支持生成OpenAI tools格式
    """
    
    def __init__(self):
        self.tools: Dict[str, dict] = {}
    
    def register(self, name: str, description: str, parameters: dict, func):
        """
        注册工具
        
        Args:
            name: 工具名称
            description: 工具描述
            parameters: 参数定义（JSON Schema格式）
            func: 实际执行的函数
        """
        # TODO: 实现注册逻辑
        pass
    
    def list_tools(self) -> List[dict]:
        """列出所有工具"""
        # TODO: 实现列出逻辑
        pass
    
    def call(self, name: str, arguments: dict) -> Any:
        """调用工具"""
        # TODO: 实现调用逻辑
        pass
    
    def to_openai_format(self) -> List[dict]:
        """转换为OpenAI tools格式"""
        # TODO: 实现格式转换
        pass


# ============================================
# 练习4：Agent执行循环
# ============================================

async def exercise_4_agent_loop(
    user_query: str,
    tools: ToolRegistry,
    max_iterations: int = 5
) -> str:
    """
    练习4：实现Agent执行循环
    
    要求：
    1. 调用LLM决定是否使用工具
    2. 如果需要工具，执行工具并获取结果
    3. 将工具结果反馈给LLM
    4. 循环直到LLM给出最终答案或达到最大迭代次数
    
    提示：
    - 使用OpenAI的function calling
    - 注意处理工具调用失败的情况
    """
    # TODO: 实现你的代码
    pass


# ============================================
# 练习5：多Agent编排
# ============================================

class AgentMessage(BaseModel):
    """Agent间消息"""
    from_agent: str
    to_agent: str
    content: str
    timestamp: datetime = datetime.now()


class MultiAgentOrchestrator:
    """
    练习5：实现多Agent编排器
    
    要求：
    1. 支持注册多个Agent
    2. 支持Agent间消息传递
    3. 实现简单的任务分发逻辑
    4. 收集并汇总各Agent结果
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.message_queue: List[AgentMessage] = []
    
    def register_agent(self, name: str, agent):
        """注册Agent"""
        # TODO: 实现注册逻辑
        pass
    
    def send_message(self, from_agent: str, to_agent: str, content: str):
        """发送消息"""
        # TODO: 实现消息发送
        pass
    
    async def run_task(self, task: str) -> str:
        """运行任务"""
        # TODO: 实现任务编排
        # 1. 分析任务，决定调用哪些Agent
        # 2. 按顺序或并行调用Agent
        # 3. 汇总结果
        pass


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    print("Week 9-11 Agent开发练习")
    print("=" * 50)
    
    # 测试练习1
    print("\n练习1：微调数据构建")
    raw_data = [
        {"user": "你好", "assistant": "你好！有什么可以帮助你的？"},
        {"user": "今天天气怎么样", "assistant": "抱歉，我没有实时天气信息。"},
        {"user": "", "assistant": "test"},  # 应该被过滤
    ]
    formatted = exercise_1_build_finetune_data(raw_data)
    print(f"格式化后: {len(formatted)} 条数据")
    
    # 测试练习2
    print("\n练习2：短期记忆")
    # memory = ShortTermMemory(max_messages=10)
    # memory.add("user", "你好")
    # memory.add("assistant", "你好！")
    # print(f"上下文: {memory.get_context()}")
    
    # 测试练习3
    print("\n练习3：工具注册")
    # registry = ToolRegistry()
    # registry.register("calculator", "计算器", {...}, lambda x: eval(x))
    # print(registry.to_openai_format())
    
    # 测试练习4
    print("\n练习4：Agent执行循环")
    # import asyncio
    # result = asyncio.run(exercise_4_agent_loop("计算1+1", registry))
    
    # 测试练习5
    print("\n练习5：多Agent编排")
    # orchestrator = MultiAgentOrchestrator()
    
    print("\n请完成上述练习，运行测试验证你的实现！")
