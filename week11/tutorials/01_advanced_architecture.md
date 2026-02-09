# 📘 生产级Agent架构设计

> **学习目标**：掌握可扩展、可维护的Agent系统架构

---

## 🎯 本教程目标

完成本教程后，你将能够：

- ✅ 设计分层Agent架构
- ✅ 实现工具注册管理
- ✅ 构建Agent协调器
- ✅ 实现错误处理与重试

---

## 📚 架构设计

### 生产级Agent架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Agent System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Gateway Layer                            ││
│  │   [认证] [限流] [日志] [追踪] [监控]                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Orchestration Layer                        ││
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     ││
│  │   │ Task Router  │  │ State Manager│  │ Error Handler│     ││
│  │   └──────────────┘  └──────────────┘  └──────────────┘     ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐        │
│  │  Planner   │      │  Executor  │      │  Reviewer  │        │
│  │   Agent    │      │   Agent    │      │   Agent    │        │
│  └─────┬──────┘      └─────┬──────┘      └─────┬──────┘        │
│        │                   │                   │                │
│        └───────────────────┼───────────────────┘                │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Tool Layer                              ││
│  │   [搜索] [计算] [代码执行] [文件操作] [API调用] [数据库]      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Memory Layer                             ││
│  │   [短期记忆] [长期记忆] [向量存储] [会话缓存]                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 核心代码实现

### 1. 工具注册系统

```python
from typing import Callable, Any
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    SEARCH = "search"
    COMPUTE = "compute"
    FILE = "file"
    API = "api"
    DATABASE = "database"

@dataclass
class ToolDefinition:
    name: str
    description: str
    function: Callable
    category: ToolCategory
    parameters: dict
    required_permissions: list[str] = None

class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
    
    def register(self, tool: ToolDefinition):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"✅ 工具已注册: {tool.name}")
    
    def get(self, name: str) -> ToolDefinition:
        """获取工具"""
        if name not in self._tools:
            raise ValueError(f"工具不存在: {name}")
        return self._tools[name]
    
    def list_tools(self, category: ToolCategory = None) -> list[ToolDefinition]:
        """列出工具"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def to_openai_format(self) -> list[dict]:
        """转换为OpenAI tools格式"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self._tools.values()
        ]

# 使用装饰器注册工具
registry = ToolRegistry()

def tool(name: str, category: ToolCategory, description: str, parameters: dict):
    """工具注册装饰器"""
    def decorator(func: Callable):
        tool_def = ToolDefinition(
            name=name,
            description=description,
            function=func,
            category=category,
            parameters=parameters
        )
        registry.register(tool_def)
        return func
    return decorator

# 示例：注册搜索工具
@tool(
    name="web_search",
    category=ToolCategory.SEARCH,
    description="搜索互联网获取信息",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    }
)
async def web_search(query: str) -> str:
    # 实际搜索实现
    return f"搜索结果: {query}"
```

### 2. Agent基类

```python
from abc import ABC, abstractmethod
from typing import Optional
import asyncio

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        llm_client,
        tool_registry: ToolRegistry,
        max_iterations: int = 10
    ):
        self.name = name
        self.llm = llm_client
        self.tools = tool_registry
        self.max_iterations = max_iterations
        self.memory: list[dict] = []
    
    @abstractmethod
    async def plan(self, task: str, context: dict) -> list[dict]:
        """制定执行计划"""
        pass
    
    @abstractmethod
    async def execute(self, plan: list[dict]) -> dict:
        """执行计划"""
        pass
    
    async def run(self, task: str, context: dict = None) -> dict:
        """运行Agent完整流程"""
        context = context or {}
        
        for i in range(self.max_iterations):
            try:
                # 1. 规划
                plan = await self.plan(task, context)
                
                # 2. 执行
                result = await self.execute(plan)
                
                # 3. 检查是否完成
                if result.get("status") == "completed":
                    return result
                
                # 4. 更新上下文
                context.update(result.get("context_updates", {}))
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "iteration": i
                }
        
        return {"status": "max_iterations_reached"}
```

### 3. 协调器实现

```python
class AgentOrchestrator:
    """Agent协调器"""
    
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self.task_queue = asyncio.Queue()
        self.results: dict[str, dict] = {}
    
    def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.name] = agent
    
    async def dispatch(self, task: dict) -> dict:
        """分发任务"""
        agent_name = task.get("agent")
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent不存在: {agent_name}")
        
        agent = self.agents[agent_name]
        result = await agent.run(
            task=task["description"],
            context=task.get("context", {})
        )
        
        return result
    
    async def run_workflow(self, workflow: list[dict]) -> dict:
        """执行工作流"""
        context = {}
        results = []
        
        for step in workflow:
            step["context"] = context
            result = await self.dispatch(step)
            results.append(result)
            
            # 传递上下文到下一步
            if result.get("status") == "completed":
                context.update(result.get("output", {}))
            else:
                # 失败时中止
                return {
                    "status": "workflow_failed",
                    "failed_step": step,
                    "results": results
                }
        
        return {
            "status": "workflow_completed",
            "results": results
        }
```

---

## 📊 学习检查清单

- [ ] 理解分层架构设计
- [ ] 会实现工具注册系统
- [ ] 能够设计Agent基类
- [ ] 理解协调器模式

---

## 🎯 下一步

继续学习：[Agent记忆系统](./02_memory_system.md)
