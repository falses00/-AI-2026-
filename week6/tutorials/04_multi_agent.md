# 🤖 多Agent系统开发指南 (LangGraph版)

> **学习目标**：使用LangGraph构建可靠的多Agent协作系统

---

## 1. 为什么需要多Agent系统？

单个Agent的局限：
- ❌ 复杂任务难以独立完成
- ❌ 缺乏专业领域知识分工
- ❌ 错误难以检测和纠正

多Agent系统的优势：
- ✅ 专业分工，各司其职
- ✅ 互相审核，减少错误
- ✅ 并行处理，提高效率

---

## 2. LangGraph多Agent架构

### 2.1 核心概念

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph 多Agent架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        ┌───────────┐                             │
│                        │   User    │                             │
│                        └─────┬─────┘                             │
│                              │                                   │
│                              ▼                                   │
│                     ┌────────────────┐                           │
│                     │   Supervisor   │ ← 决定下一个执行的Agent    │
│                     │    (Router)    │                           │
│                     └───────┬────────┘                           │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│   ┌───────────┐      ┌───────────┐      ┌───────────┐          │
│   │ Researcher│      │  Coder    │      │ Reviewer  │          │
│   │   Agent   │      │  Agent    │      │  Agent    │          │
│   └─────┬─────┘      └─────┬─────┘      └─────┬─────┘          │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│                     ┌──────────────┐                            │
│                     │ Shared State │ ← 共享状态和消息            │
│                     │  (Messages)  │                            │
│                     └──────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 状态定义

```python
from typing import Annotated, TypedDict, Literal
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """多Agent共享状态"""
    messages: Annotated[list, add_messages]  # 消息历史
    next: str                                 # 下一个执行的Agent
    task: str                                 # 当前任务
    research_data: dict                       # 研究数据
    code_output: str                          # 代码输出
    review_result: dict                       # 审核结果
```

---

## 3. 实现Agent节点

### 3.1 研究员Agent

```python
from langchain.chat_models import init_chat_model
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """搜索互联网获取信息"""
    # 实际应用中接入搜索API
    return f"搜索结果: {query} 的相关信息..."

researcher_tools = [web_search]

def researcher_node(state: AgentState) -> AgentState:
    """研究员Agent：负责信息收集"""
    model = init_chat_model("deepseek-chat")
    model_with_tools = model.bind_tools(researcher_tools)
    
    messages = [
        {"role": "system", "content": """你是一名研究员，负责：
1. 搜索和收集相关信息
2. 整理研究发现
3. 为其他Agent提供背景资料

使用web_search工具进行搜索。"""},
        *state["messages"]
    ]
    
    response = model_with_tools.invoke(messages)
    
    # 处理工具调用
    if response.tool_calls:
        # 执行工具并获取结果...
        pass
    
    return {
        "messages": [response],
        "research_data": {"findings": response.content}
    }
```

### 3.2 编码员Agent

```python
def coder_node(state: AgentState) -> AgentState:
    """编码员Agent：负责代码生成"""
    model = init_chat_model("deepseek-chat")
    
    research_context = state.get("research_data", {})
    
    messages = [
        {"role": "system", "content": f"""你是一名Python开发工程师。

参考研究资料：
{research_context}

根据任务要求编写高质量代码：
- 使用类型提示
- 添加详细注释
- 处理异常情况"""},
        *state["messages"]
    ]
    
    response = model.invoke(messages)
    
    return {
        "messages": [response],
        "code_output": response.content
    }
```

### 3.3 审核员Agent

```python
def reviewer_node(state: AgentState) -> AgentState:
    """审核员Agent：负责质量检查"""
    model = init_chat_model("deepseek-chat")
    
    code = state.get("code_output", "")
    
    messages = [
        {"role": "system", "content": """你是一名代码审核专家。

审核标准：
1. 代码正确性
2. 安全性检查
3. 性能考虑
4. 可读性

返回JSON格式的审核结果：
{
    "approved": true/false,
    "score": 1-10,
    "issues": ["问题列表"],
    "suggestions": ["改进建议"]
}"""},
        {"role": "user", "content": f"请审核以下代码：\n\n{code}"}
    ]
    
    response = model.invoke(messages)
    
    return {
        "messages": [response],
        "review_result": {"content": response.content}
    }
```

---

## 4. 构建多Agent图

### 4.1 Supervisor路由

```python
from langgraph.graph import StateGraph, END, START

def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor：决定下一个执行的Agent"""
    model = init_chat_model("deepseek-chat")
    
    messages = [
        {"role": "system", "content": """你是一个任务协调者。

根据当前状态决定下一步：
- "researcher": 需要收集更多信息
- "coder": 需要编写代码
- "reviewer": 需要审核代码
- "FINISH": 任务已完成

返回JSON: {"next": "agent_name"}"""},
        *state["messages"]
    ]
    
    response = model.invoke(messages)
    
    # 解析下一个Agent
    import json
    try:
        result = json.loads(response.content)
        next_agent = result.get("next", "FINISH")
    except:
        next_agent = "FINISH"
    
    return {"next": next_agent}

def route_next(state: AgentState) -> Literal["researcher", "coder", "reviewer", "FINISH"]:
    """路由函数"""
    return state.get("next", "FINISH")
```

### 4.2 组装Graph

```python
from langgraph.graph import StateGraph, END, START

# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("coder", coder_node)
workflow.add_node("reviewer", reviewer_node)

# 添加边
workflow.add_edge(START, "supervisor")

# 条件路由
workflow.add_conditional_edges(
    "supervisor",
    route_next,
    {
        "researcher": "researcher",
        "coder": "coder",
        "reviewer": "reviewer",
        "FINISH": END
    }
)

# 所有Agent执行完后回到Supervisor
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("coder", "supervisor")
workflow.add_edge("reviewer", "supervisor")

# 编译
app = workflow.compile()
```

### 4.3 运行

```python
async def run_multi_agent(task: str):
    """运行多Agent系统"""
    initial_state = {
        "messages": [{"role": "user", "content": task}],
        "task": task,
        "next": "",
        "research_data": {},
        "code_output": "",
        "review_result": {}
    }
    
    async for event in app.astream(initial_state):
        print(f"Event: {event}")
    
    return event

# 使用
result = await run_multi_agent("创建一个FastAPI用户认证系统")
```

---

## 5. Agent间Handoff模式

### 5.1 定义Handoff工具

```python
from langchain.tools import tool

def create_handoff_tool(target_agent: str):
    """创建切换到目标Agent的工具"""
    @tool
    def handoff():
        f"""将任务移交给 {target_agent}"""
        return f"Handoff to {target_agent}"
    return handoff

# 为每个Agent创建handoff工具
handoff_to_coder = create_handoff_tool("coder")
handoff_to_reviewer = create_handoff_tool("reviewer")
```

---

## 6. 学习检查清单

- [ ] 理解多Agent协作的优势
- [ ] 掌握LangGraph状态管理
- [ ] 会实现Supervisor路由模式
- [ ] 了解Agent间Handoff机制

---

## 继续学习

📌 **Week 6 学习顺序**：
1. ✅ AI Agent基础概念
2. ✅ ReAct原生实现
3. ✅ LangChain Agent
4. ✅ 工具开发详解
5. ✅ 多Agent系统（本教程）

---

**多Agent系统是复杂AI应用的核心架构！🤖🤖🤖**
