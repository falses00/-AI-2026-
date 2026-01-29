# 🔗 使用LangChain构建Agent

> **学习目标**：使用LangChain框架快速构建Agent

---

## 1. LangChain Agent优势

- ✅ 内置多种Agent类型
- ✅ 丰富的工具集成
- ✅ 标准化接口
- ✅ 易于扩展

---

## 2. 安装依赖

```bash
pip install langchain langchain-openai langchain-community
```

---

## 3. 快速开始

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool

# 1. 创建LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 2. 定义工具
def search(query: str) -> str:
    """搜索信息"""
    return f"FastAPI是高性能Python框架"

def calculator(expression: str) -> str:
    """计算表达式"""
    return str(eval(expression))

tools = [
    Tool(name="search", func=search, description="搜索信息"),
    Tool(name="calculator", func=calculator, description="计算数学表达式"),
]

# 3. 获取ReAct Prompt
prompt = hub.pull("hwchase17/react")

# 4. 创建Agent
agent = create_react_agent(llm, tools, prompt)

# 5. 创建执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5
)

# 6. 运行
result = agent_executor.invoke({"input": "FastAPI是什么？"})
print(result["output"])
```

---

## 4. 使用@tool装饰器

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# 定义工具（使用装饰器）
@tool
def search(query: str) -> str:
    """搜索网络信息。参数query为搜索关键词。"""
    knowledge = {
        "fastapi": "FastAPI是现代Python Web框架，性能卓越",
        "python": "Python是流行的编程语言",
    }
    for key, value in knowledge.items():
        if key in query.lower():
            return value
    return "未找到相关信息"

@tool
def calculator(expression: str) -> str:
    """计算数学表达式。参数expression为数学表达式。"""
    try:
        return f"结果是: {eval(expression)}"
    except:
        return "计算错误"

@tool
def get_weather(city: str) -> str:
    """获取城市天气。参数city为城市名称。"""
    weather = {"北京": "晴 25°C", "上海": "多云 28°C"}
    return weather.get(city, "未知城市")

# 工具列表
tools = [search, calculator, get_weather]

# 创建LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

# 创建Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手。使用提供的工具来回答问题。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 创建Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行
result = agent_executor.invoke({"input": "北京天气怎么样？"})
print(result["output"])
```

---

## 5. 带记忆的Agent

```python
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 创建记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Prompt包含历史
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 创建Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

# 多轮对话
result1 = agent_executor.invoke({"input": "FastAPI是什么？"})
print(result1["output"])

result2 = agent_executor.invoke({"input": "它和Django相比如何？"})  # 会记住上文
print(result2["output"])
```

---

## 6. 结构化工具

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# 定义参数Schema
class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=5, description="最大结果数")

class CalculatorInput(BaseModel):
    expression: str = Field(description="数学表达式")

# 实现函数
def search_impl(query: str, max_results: int = 5) -> str:
    return f"搜索'{query}'，返回{max_results}个结果"

def calculator_impl(expression: str) -> str:
    return str(eval(expression))

# 创建结构化工具
search_tool = StructuredTool.from_function(
    func=search_impl,
    name="search",
    description="搜索信息",
    args_schema=SearchInput
)

calculator_tool = StructuredTool.from_function(
    func=calculator_impl,
    name="calculator",
    description="计算数学表达式",
    args_schema=CalculatorInput
)

tools = [search_tool, calculator_tool]
```

---

## 7. 自定义Agent类型

### 7.1 Plan-and-Execute Agent

```python
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner
)

# 创建规划器
planner = load_chat_planner(llm)

# 创建执行器
executor = load_agent_executor(llm, tools, verbose=True)

# 创建Plan-and-Execute Agent
plan_and_execute = PlanAndExecute(
    planner=planner,
    executor=executor,
    verbose=True
)

# 运行复杂任务
result = plan_and_execute.invoke({
    "input": "先搜索Python的信息，然后计算2024-1991的结果"
})
```

### 7.2 OpenAI Functions Agent

```python
from langchain.agents import create_openai_functions_agent

# 使用OpenAI Functions格式
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

---

## 8. 完整示例：研究助手

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import tool
import os

class ResearchAssistant:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # 保留最近5轮
        )
        
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
    
    def _create_tools(self):
        @tool
        def search_papers(topic: str) -> str:
            """搜索学术论文。topic为研究主题。"""
            # 模拟论文搜索
            papers = {
                "rag": "1. RAG: 检索增强生成 (2023)\n2. 高级RAG技术 (2024)",
                "agent": "1. ReAct框架 (2022)\n2. Multi-Agent系统 (2024)",
            }
            for key, value in papers.items():
                if key in topic.lower():
                    return value
            return "未找到相关论文"
        
        @tool
        def summarize(text: str) -> str:
            """总结文本内容。text为待总结文本。"""
            return f"总结：{text[:100]}..."
        
        @tool
        def save_note(content: str) -> str:
            """保存研究笔记。content为笔记内容。"""
            # 实际应保存到文件或数据库
            return f"已保存笔记：{content[:50]}..."
        
        return [search_papers, summarize, save_note]
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个研究助手，帮助用户进行学术研究。
你可以搜索论文、总结内容、保存笔记。
请一步步思考，合理使用工具完成任务。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10
        )
    
    def chat(self, message: str) -> str:
        result = self.agent_executor.invoke({"input": message})
        return result["output"]

# 使用
assistant = ResearchAssistant()
print(assistant.chat("帮我搜索关于RAG的最新论文"))
print(assistant.chat("总结一下刚才搜索到的内容"))
print(assistant.chat("保存一下这个总结"))
```

---

## 📺 推荐B站视频

搜索：
- **"LangChain Agent 教程"**
- **"LangChain 工具调用"**
- **"LCEL Agent 实战"**

---

## 9. 继续学习

📌 **Week 6 学习顺序**：
1. ✅ Agent基础概念
2. ✅ ReAct框架（原生或LangChain）
3. ➡️ 工具使用详解
4. ➡️ 多Agent系统

---

**LangChain让Agent开发更高效！💪**
