# 🌐 多Agent系统

> **学习目标**：掌握多Agent协作的设计和实现

---

## 1. 为什么需要多Agent？

### 单Agent的局限

```
复杂任务: "分析市场数据，生成报告，并发送给团队"

单Agent: 需要同时精通数据分析、报告写作、邮件发送...
         → 提示词过长，容易出错
```

### 多Agent的优势

```
多Agent分工:
├── 数据分析Agent  → 专门分析数据
├── 报告生成Agent  → 专门写报告
└── 通知Agent      → 专门发邮件

每个Agent专注一件事，更准确！
```

---

## 2. 多Agent架构模式

### 2.1 顺序执行

```
Agent A → Agent B → Agent C
```

### 2.2 并行执行

```
       ┌→ Agent A ─┐
任务 ──┼→ Agent B ─┼→ 合并结果
       └→ Agent C ─┘
```

### 2.3 层级结构

```
        Manager Agent
       /      |      \
  Worker A  Worker B  Worker C
```

### 2.4 对话协作

```
Agent A ←→ Agent B ←→ Agent C
    (讨论直到达成共识)
```

---

## 3. 原生多Agent实现

```python
from openai import OpenAI
import os
from typing import Callable
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
    
    def chat(self, message: str) -> str:
        """与Agent对话"""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

# 专业Agent定义
class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="研究员",
            system_prompt="""你是一个研究员，专门负责收集和分析信息。
当收到任务时，你会：
1. 分析需要研究的内容
2. 提供详细的调研结果
3. 标注信息来源

只输出调研结果，不要多余的解释。"""
        )

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="撰稿人",
            system_prompt="""你是一个专业撰稿人，擅长将信息整理成文章。
当收到资料时，你会：
1. 提取关键信息
2. 组织成清晰的结构
3. 使用专业但易懂的语言

只输出文章内容，不要多余的解释。"""
        )

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="审核员",
            system_prompt="""你是一个审核员，负责审核文章质量。
你会检查：
1. 信息准确性
2. 结构完整性
3. 语言流畅度

输出审核意见和修改建议。如果通过，输出"通过"。"""
        )

class ManagerAgent(BaseAgent):
    """管理Agent，协调其他Agent"""
    
    def __init__(self):
        super().__init__(
            name="项目经理",
            system_prompt="""你是项目经理，负责协调团队完成任务。
分析任务后，决定需要哪些步骤和哪些角色参与。"""
        )
        
        self.team = {
            "researcher": ResearchAgent(),
            "writer": WriterAgent(),
            "reviewer": ReviewerAgent(),
        }
    
    def delegate(self, task: str) -> str:
        """分配并执行任务"""
        print(f"\n{'='*50}")
        print(f"[项目经理] 收到任务: {task}")
        print(f"{'='*50}")
        
        # Step 1: 研究
        print("\n[1/3] 研究员开始调研...")
        research_result = self.team["researcher"].chat(
            f"请为以下主题进行调研：\n{task}"
        )
        print(f"研究结果:\n{research_result[:200]}...")
        
        # Step 2: 撰写
        print("\n[2/3] 撰稿人开始写作...")
        article = self.team["writer"].chat(
            f"基于以下调研结果撰写文章：\n{research_result}"
        )
        print(f"文章:\n{article[:200]}...")
        
        # Step 3: 审核
        print("\n[3/3] 审核员开始审核...")
        review = self.team["reviewer"].chat(
            f"请审核以下文章：\n{article}"
        )
        print(f"审核结果:\n{review}")
        
        # 如果需要修改，让撰稿人修改
        if "通过" not in review:
            print("\n[额外步骤] 根据审核意见修改...")
            article = self.team["writer"].chat(
                f"原文：\n{article}\n\n审核意见：\n{review}\n\n请根据意见修改："
            )
        
        return article

# 使用
manager = ManagerAgent()
result = manager.delegate("写一篇关于FastAPI框架的介绍文章")
print(f"\n最终成果:\n{result}")
```

---

## 4. 对话式多Agent

```python
class DebateSystem:
    """辩论系统：多个Agent讨论问题"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        
        self.agents = {
            "支持方": "你是支持方，要为观点提供有力的论据支持。",
            "反对方": "你是反对方，要找出观点的问题和反例。",
            "主持人": "你是主持人，总结双方观点，得出结论。"
        }
    
    def _agent_speak(self, agent_name: str, context: str) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.agents[agent_name]},
                {"role": "user", "content": context}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def debate(self, topic: str, rounds: int = 2) -> str:
        """进行辩论"""
        print(f"\n辩题: {topic}\n")
        
        history = f"辩题: {topic}\n\n"
        
        for round_num in range(1, rounds + 1):
            print(f"--- 第{round_num}轮 ---")
            
            # 支持方发言
            support = self._agent_speak("支持方", history + "请发表你的观点：")
            print(f"\n[支持方]: {support}")
            history += f"支持方: {support}\n\n"
            
            # 反对方发言
            oppose = self._agent_speak("反对方", history + "请反驳对方观点：")
            print(f"\n[反对方]: {oppose}")
            history += f"反对方: {oppose}\n\n"
        
        # 主持人总结
        conclusion = self._agent_speak("主持人", history + "请总结双方观点，给出结论：")
        print(f"\n[主持人总结]: {conclusion}")
        
        return conclusion

# 使用
debate = DebateSystem()
result = debate.debate("AI会取代程序员吗？", rounds=2)
```

---

## 5. 使用LangGraph构建多Agent

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
import operator

# 定义状态
class AgentState(TypedDict):
    task: str
    research: str
    draft: str
    review: str
    final: str
    messages: Annotated[list, operator.add]

# 创建LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 定义节点函数
def researcher(state: AgentState) -> AgentState:
    """研究节点"""
    response = llm.invoke([
        {"role": "system", "content": "你是研究员，提供调研结果。"},
        {"role": "user", "content": f"调研主题：{state['task']}"}
    ])
    return {"research": response.content}

def writer(state: AgentState) -> AgentState:
    """撰写节点"""
    response = llm.invoke([
        {"role": "system", "content": "你是撰稿人，将资料整理成文章。"},
        {"role": "user", "content": f"资料：{state['research']}\n请撰写文章："}
    ])
    return {"draft": response.content}

def reviewer(state: AgentState) -> AgentState:
    """审核节点"""
    response = llm.invoke([
        {"role": "system", "content": "你是审核员，审核文章质量。"},
        {"role": "user", "content": f"文章：{state['draft']}\n请审核："}
    ])
    return {"review": response.content}

def should_revise(state: AgentState) -> str:
    """决定是否需要修改"""
    if "通过" in state["review"]:
        return "end"
    return "revise"

def revise(state: AgentState) -> AgentState:
    """修改节点"""
    response = llm.invoke([
        {"role": "system", "content": "你是撰稿人，根据意见修改文章。"},
        {"role": "user", "content": f"原文：{state['draft']}\n意见：{state['review']}\n请修改："}
    ])
    return {"draft": response.content, "final": response.content}

# 构建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("researcher", researcher)
workflow.add_node("writer", writer)
workflow.add_node("reviewer", reviewer)
workflow.add_node("revise", revise)

# 添加边
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    should_revise,
    {"end": END, "revise": "revise"}
)
workflow.add_edge("revise", END)

# 编译
app = workflow.compile()

# 运行
result = app.invoke({"task": "写一篇FastAPI入门教程"})
print(result["final"])
```

---

## 6. 使用AutoGen

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# 配置LLM
llm_config = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_key": "your-key",
        "base_url": "https://api.deepseek.com/v1"
    }]
}

# 创建Agent
researcher = AssistantAgent(
    name="Researcher",
    system_message="你是研究员，负责收集信息。",
    llm_config=llm_config
)

writer = AssistantAgent(
    name="Writer", 
    system_message="你是撰稿人，负责撰写内容。",
    llm_config=llm_config
)

reviewer = AssistantAgent(
    name="Reviewer",
    system_message="你是审核员，负责审核质量。",
    llm_config=llm_config
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False
)

# 创建群聊
groupchat = GroupChat(
    agents=[user_proxy, researcher, writer, reviewer],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 启动对话
user_proxy.initiate_chat(
    manager,
    message="请帮我写一篇关于FastAPI的介绍文章"
)
```

---

## 7. 最佳实践

### 7.1 Agent数量
- 3-5个Agent最佳
- 太多会增加协调成本

### 7.2 职责划分
- 每个Agent有明确的专长
- 避免职责重叠

### 7.3 通信协议
- 定义清晰的输入输出格式
- 使用结构化数据传递

### 7.4 错误处理
- 设置最大轮次
- 有超时机制
- 可以回退到单Agent

---

## 📺 推荐B站视频

搜索：
- **"多Agent系统 教程"**
- **"LangGraph 多Agent"**
- **"AutoGen Multi-Agent"**

---

## 8. 继续学习

🎉 **恭喜完成Week 6！**

📌 **Week 6 学习顺序**：
1. ✅ Agent基础概念
2. ✅ ReAct框架
3. ✅ 工具使用详解
4. ✅ 多Agent系统（本教程）

**你已掌握AI Agent开发的核心技能！💪**

---

## 完成整个课程！🎊

恭喜你完成了6周的AI工程师学习之旅：
- Week 1-3: Python/FastAPI/MCP基础
- Week 4: RAG系统入门
- Week 5: RAG进阶技术
- Week 6: AI Agent开发
