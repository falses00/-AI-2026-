# 🤖 多Agent工作流项目

> **Week 11 综合实战项目** - 构建协作式多Agent系统

---

## 🎯 项目目标

构建一个多Agent协作系统，实现：
- 多个专业Agent协作完成复杂任务
- Supervisor模式的任务路由
- Agent间消息传递与状态共享
- 工具调用与结果整合

---

## 📊 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     多Agent工作流架构                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│                    ┌─────────────────┐                           │
│                    │   Supervisor    │                           │
│                    │   (任务调度器)   │                           │
│                    └────────┬────────┘                           │
│                             │                                     │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Researcher   │    │ Analyzer    │    │ Writer      │         │
│  │ (研究员)     │    │ (分析师)     │    │ (撰写者)    │         │
│  │              │    │              │    │              │         │
│  │ • 搜索资料   │    │ • 数据分析   │    │ • 生成报告   │         │
│  │ • 提取信息   │    │ • 洞察发现   │    │ • 格式优化   │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                             │                                     │
│                             ▼                                     │
│                    ┌─────────────────┐                           │
│                    │   共享状态       │                           │
│                    │   (State)       │                           │
│                    └─────────────────┘                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
week11/projects/multi_agent_workflow/
├── README.md              # 本文件
├── requirements.txt
├── config.yaml           # Agent配置
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI入口
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py       # Agent基类
│   │   ├── researcher.py # 研究员
│   │   ├── analyzer.py   # 分析师
│   │   ├── writer.py     # 撰写者
│   │   └── supervisor.py # 调度器
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py     # 搜索工具
│   │   ├── analyze.py    # 分析工具
│   │   └── format.py     # 格式工具
│   ├── state.py          # 状态管理
│   └── graph.py          # LangGraph工作流
└── tests/
    └── test_workflow.py
```

---

## 🔧 核心代码

### 1. 共享状态 (`app/state.py`)

```python
from typing import List, TypedDict, Annotated, Optional
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """多Agent共享状态"""
    # 消息历史
    messages: Annotated[list, add_messages]
    
    # 原始任务
    task: str
    
    # 研究结果
    research_data: Optional[List[dict]]
    
    # 分析结果
    analysis_results: Optional[dict]
    
    # 最终报告
    final_report: Optional[str]
    
    # 当前Agent
    current_agent: str
    
    # 下一步
    next_action: str
```

### 2. Agent基类 (`app/agents/base.py`)

```python
from abc import ABC, abstractmethod
from openai import OpenAI
from typing import List

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, description: str, tools: List = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.client = OpenAI()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    async def run(self, state: dict) -> dict:
        """执行Agent逻辑"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self._build_prompt(state)}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self._format_tools() if self.tools else None
        )
        
        return self._process_response(response, state)
    
    @abstractmethod
    def _build_prompt(self, state: dict) -> str:
        """构建提示词"""
        pass
    
    @abstractmethod
    def _process_response(self, response, state: dict) -> dict:
        """处理响应"""
        pass
    
    def _format_tools(self) -> List[dict]:
        """格式化工具为OpenAI格式"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools
        ]
```

### 3. 研究员Agent (`app/agents/researcher.py`)

```python
from .base import BaseAgent
from ..tools.search import web_search_tool

class ResearcherAgent(BaseAgent):
    """研究员Agent - 负责搜索和收集信息"""
    
    def __init__(self):
        super().__init__(
            name="Researcher",
            description="专业研究员，负责搜索和收集信息",
            tools=[web_search_tool]
        )
    
    def get_system_prompt(self) -> str:
        return """你是一个专业的研究员。你的职责是：
1. 根据任务需求搜索相关信息
2. 从多个来源收集数据
3. 提取关键事实和数据
4. 整理成结构化的研究结果

你可以使用搜索工具来获取信息。
请确保信息准确、来源可靠。"""
    
    def _build_prompt(self, state: dict) -> str:
        task = state.get("task", "")
        return f"""请针对以下任务进行研究：

任务: {task}

请使用搜索工具收集相关信息，然后整理成结构化的研究结果。
返回格式：
- 主题概述
- 关键发现（列表）
- 数据和事实
- 信息来源"""
    
    def _process_response(self, response, state: dict) -> dict:
        content = response.choices[0].message.content
        
        # 处理工具调用
        if response.choices[0].message.tool_calls:
            tool_results = self._execute_tools(response.choices[0].message.tool_calls)
            content = self._synthesize_results(tool_results)
        
        return {
            **state,
            "research_data": [{"content": content}],
            "current_agent": "Researcher",
            "next_action": "analyze"
        }
    
    def _execute_tools(self, tool_calls):
        """执行工具调用"""
        results = []
        for call in tool_calls:
            if call.function.name == "web_search":
                import json
                args = json.loads(call.function.arguments)
                result = web_search_tool.execute(args["query"])
                results.append(result)
        return results
    
    def _synthesize_results(self, results):
        """综合工具结果"""
        return "\n\n".join([str(r) for r in results])
```

### 4. Supervisor调度器 (`app/agents/supervisor.py`)

```python
from typing import Literal

class SupervisorAgent:
    """Supervisor - 负责任务路由和决策"""
    
    def __init__(self, agents: list):
        self.agents = {a.name: a for a in agents}
        self.agent_names = list(self.agents.keys())
        self.client = OpenAI()
    
    async def route(self, state: dict) -> str:
        """决定下一个执行的Agent"""
        prompt = f"""你是一个任务调度器。根据当前状态，决定下一步应该由哪个Agent执行。

当前任务: {state.get('task')}
已完成的Agent: {state.get('current_agent', '无')}
研究数据: {'有' if state.get('research_data') else '无'}
分析结果: {'有' if state.get('analysis_results') else '无'}
最终报告: {'有' if state.get('final_report') else '无'}

可选Agent: {', '.join(self.agent_names)}

返回下一个应该执行的Agent名称，或返回"FINISH"如果任务已完成。
只返回Agent名称或FINISH，不要其他内容。"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        
        decision = response.choices[0].message.content.strip()
        
        if decision in self.agent_names:
            return decision
        elif "FINISH" in decision.upper():
            return "FINISH"
        else:
            # 默认逻辑
            if not state.get('research_data'):
                return "Researcher"
            elif not state.get('analysis_results'):
                return "Analyzer"
            elif not state.get('final_report'):
                return "Writer"
            else:
                return "FINISH"
```

### 5. LangGraph工作流 (`app/graph.py`)

```python
from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents.researcher import ResearcherAgent
from .agents.analyzer import AnalyzerAgent
from .agents.writer import WriterAgent
from .agents.supervisor import SupervisorAgent

def create_workflow():
    """创建多Agent工作流"""
    
    # 初始化Agent
    researcher = ResearcherAgent()
    analyzer = AnalyzerAgent()
    writer = WriterAgent()
    supervisor = SupervisorAgent([researcher, analyzer, writer])
    
    # 创建图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("Researcher", researcher.run)
    workflow.add_node("Analyzer", analyzer.run)
    workflow.add_node("Writer", writer.run)
    workflow.add_node("Supervisor", supervisor.route)
    
    # 添加边
    workflow.set_entry_point("Supervisor")
    
    # 条件路由
    def route_next(state):
        next_agent = state.get("next_action")
        if next_agent == "FINISH":
            return END
        return next_agent
    
    workflow.add_conditional_edges(
        "Supervisor",
        route_next,
        {
            "Researcher": "Researcher",
            "Analyzer": "Analyzer",
            "Writer": "Writer",
            END: END
        }
    )
    
    # 所有Agent完成后回到Supervisor
    for agent in ["Researcher", "Analyzer", "Writer"]:
        workflow.add_edge(agent, "Supervisor")
    
    return workflow.compile()

# 运行工作流
async def run_multi_agent_task(task: str) -> dict:
    """执行多Agent任务"""
    workflow = create_workflow()
    
    initial_state = {
        "messages": [],
        "task": task,
        "research_data": None,
        "analysis_results": None,
        "final_report": None,
        "current_agent": None,
        "next_action": None
    }
    
    result = await workflow.ainvoke(initial_state)
    
    return {
        "task": task,
        "report": result.get("final_report"),
        "agents_used": ["Researcher", "Analyzer", "Writer"]
    }
```

---

## 📦 依赖 (`requirements.txt`)

```
fastapi>=0.109.0
uvicorn>=0.27.0
openai>=1.12.0
langgraph>=0.0.40
langchain>=0.1.0
pydantic>=2.5.0
httpx>=0.26.0
```

---

## 🚀 使用方式

```bash
# 运行服务
uvicorn app.main:app --reload --port 8000

# 调用API
curl -X POST "http://localhost:8000/workflow/run" \
  -H "Content-Type: application/json" \
  -d '{"task": "分析2024年AI行业趋势并生成报告"}'
```

---

## 📊 学习收获

- [x] 多Agent系统设计
- [x] LangGraph工作流编排
- [x] Agent间状态共享
- [x] Supervisor路由模式
