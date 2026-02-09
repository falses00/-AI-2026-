# 🤝 多Agent协作模式

> **学习目标**：掌握多Agent系统的协作模式与通信机制

---

## 🎯 为什么需要多Agent协作？

### 单Agent vs 多Agent

| 场景 | 单Agent | 多Agent |
|-----|---------|---------|
| 简单问答 | ✅ 足够 | 过度设计 |
| 代码生成+测试 | 职责混乱 | ✅ 分工明确 |
| 复杂项目管理 | 能力不足 | ✅ 协同工作 |
| 多步骤决策 | 容易出错 | ✅ 相互校验 |

---

## 📚 协作模式分类

```
┌─────────────────────────────────────────────────────────────────┐
│                    多Agent协作模式                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  模式1: 串行Pipeline                                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Agent A │─►│ Agent B │─►│ Agent C │─►│ 最终结果 │           │
│  │ (规划)  │  │ (执行)  │  │ (审核)  │  └─────────┘           │
│  └─────────┘  └─────────┘  └─────────┘                         │
│                                                                  │
│  模式2: 并行扇出                                                │
│               ┌─────────┐                                       │
│          ┌───►│ Agent A │───┐                                   │
│  ┌─────┐ │    └─────────┘   │    ┌─────────┐                   │
│  │任务 │─┼───►│ Agent B │───┼───►│ 聚合    │                   │
│  └─────┘ │    └─────────┘   │    └─────────┘                   │
│          └───►│ Agent C │───┘                                   │
│               └─────────┘                                       │
│                                                                  │
│  模式3: 层级委派                                                │
│          ┌─────────────────┐                                    │
│          │  Manager Agent  │                                    │
│          └────────┬────────┘                                    │
│       ┌───────────┼───────────┐                                 │
│       ▼           ▼           ▼                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                           │
│  │ Worker1 │ │ Worker2 │ │ Worker3 │                           │
│  └─────────┘ └─────────┘ └─────────┘                           │
│                                                                  │
│  模式4: 对话协商                                                │
│  ┌─────────┐     ┌─────────┐                                   │
│  │ Agent A │◄───►│ Agent B │  双向对话直到达成共识              │
│  └─────────┘     └─────────┘                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 串行Pipeline实现

```python
from dataclasses import dataclass
from typing import Any
from abc import ABC, abstractmethod

@dataclass
class TaskContext:
    """任务上下文"""
    original_task: str
    current_step: str
    previous_results: list[dict]
    metadata: dict = None

class PipelineAgent(ABC):
    """Pipeline Agent基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def process(self, context: TaskContext) -> dict:
        pass

class PlannerAgent(PipelineAgent):
    """规划Agent"""
    
    @property
    def name(self) -> str:
        return "planner"
    
    async def process(self, context: TaskContext) -> dict:
        # 使用LLM生成计划
        plan = await self._generate_plan(context.original_task)
        return {
            "agent": self.name,
            "output": plan,
            "steps": plan.get("steps", [])
        }
    
    async def _generate_plan(self, task: str) -> dict:
        # 实际实现调用LLM
        return {
            "goal": task,
            "steps": [
                {"id": 1, "action": "research", "description": "调研需求"},
                {"id": 2, "action": "implement", "description": "实现代码"},
                {"id": 3, "action": "test", "description": "测试验证"}
            ]
        }

class ExecutorAgent(PipelineAgent):
    """执行Agent"""
    
    @property
    def name(self) -> str:
        return "executor"
    
    async def process(self, context: TaskContext) -> dict:
        # 获取上一步的计划
        planner_result = context.previous_results[-1]
        steps = planner_result.get("steps", [])
        
        results = []
        for step in steps:
            result = await self._execute_step(step)
            results.append(result)
        
        return {
            "agent": self.name,
            "output": results,
            "success": all(r.get("success") for r in results)
        }
    
    async def _execute_step(self, step: dict) -> dict:
        # 实际执行步骤
        return {"step_id": step["id"], "success": True, "output": f"完成: {step['description']}"}

class ReviewerAgent(PipelineAgent):
    """审核Agent"""
    
    @property
    def name(self) -> str:
        return "reviewer"
    
    async def process(self, context: TaskContext) -> dict:
        # 审核执行结果
        executor_result = context.previous_results[-1]
        
        issues = await self._review_results(executor_result)
        
        return {
            "agent": self.name,
            "approved": len(issues) == 0,
            "issues": issues,
            "feedback": "审核通过" if len(issues) == 0 else f"发现{len(issues)}个问题"
        }
    
    async def _review_results(self, results: dict) -> list:
        # 实际审核逻辑
        return []

class AgentPipeline:
    """Agent Pipeline"""
    
    def __init__(self):
        self.agents: list[PipelineAgent] = []
    
    def add_agent(self, agent: PipelineAgent):
        self.agents.append(agent)
        return self
    
    async def run(self, task: str) -> dict:
        context = TaskContext(
            original_task=task,
            current_step="",
            previous_results=[]
        )
        
        for agent in self.agents:
            context.current_step = agent.name
            
            print(f"🔄 Running {agent.name}...")
            result = await agent.process(context)
            context.previous_results.append(result)
            
            print(f"✅ {agent.name} completed")
        
        return {
            "task": task,
            "results": context.previous_results,
            "final_output": context.previous_results[-1]
        }

# 使用
async def main():
    pipeline = AgentPipeline()
    pipeline.add_agent(PlannerAgent())
    pipeline.add_agent(ExecutorAgent())
    pipeline.add_agent(ReviewerAgent())
    
    result = await pipeline.run("开发一个用户登录功能")
    print(result)
```

---

## 💻 并行扇出实现

```python
import asyncio
from typing import Callable

class ParallelFanOut:
    """并行扇出协调器"""
    
    def __init__(self):
        self.agents: list[PipelineAgent] = []
    
    def add_agent(self, agent: PipelineAgent):
        self.agents.append(agent)
        return self
    
    async def run(
        self,
        task: str,
        aggregator: Callable[[list[dict]], dict] = None
    ) -> dict:
        """并行执行所有Agent并聚合结果"""
        context = TaskContext(
            original_task=task,
            current_step="parallel",
            previous_results=[]
        )
        
        # 并行执行
        tasks = [agent.process(context) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        cleaned_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                cleaned_results.append({
                    "agent": self.agents[i].name,
                    "error": str(result)
                })
            else:
                cleaned_results.append(result)
        
        # 聚合
        if aggregator:
            final = aggregator(cleaned_results)
        else:
            final = self._default_aggregator(cleaned_results)
        
        return {
            "task": task,
            "individual_results": cleaned_results,
            "aggregated": final
        }
    
    def _default_aggregator(self, results: list[dict]) -> dict:
        """默认聚合：投票机制"""
        # 简单合并所有输出
        return {
            "combined_outputs": [r.get("output") for r in results],
            "success_count": sum(1 for r in results if r.get("success", True))
        }

# 实战例子: 多视角分析
class OptimistAgent(PipelineAgent):
    @property
    def name(self): return "optimist"
    
    async def process(self, context: TaskContext) -> dict:
        return {
            "agent": self.name,
            "perspective": "positive",
            "output": f"积极分析: {context.original_task}的优势和机会..."
        }

class PessimistAgent(PipelineAgent):
    @property
    def name(self): return "pessimist"
    
    async def process(self, context: TaskContext) -> dict:
        return {
            "agent": self.name,
            "perspective": "negative",
            "output": f"风险分析: {context.original_task}的挑战和风险..."
        }

class RealistAgent(PipelineAgent):
    @property
    def name(self): return "realist"
    
    async def process(self, context: TaskContext) -> dict:
        return {
            "agent": self.name,
            "perspective": "balanced",
            "output": f"客观分析: {context.original_task}的现实评估..."
        }

# 使用
async def analyze_with_multiple_perspectives(task: str):
    fanout = ParallelFanOut()
    fanout.add_agent(OptimistAgent())
    fanout.add_agent(PessimistAgent())
    fanout.add_agent(RealistAgent())
    
    result = await fanout.run(task)
    return result
```

---

## 💻 层级委派实现

```python
class ManagerAgent:
    """管理者Agent - 分配任务给Worker"""
    
    def __init__(self, workers: list[PipelineAgent]):
        self.workers = {w.name: w for w in workers}
    
    async def delegate(self, task: str) -> dict:
        """分析任务并委派给合适的Worker"""
        
        # 1. 分解任务
        subtasks = await self._decompose_task(task)
        
        # 2. 分配任务
        assignments = await self._assign_tasks(subtasks)
        
        # 3. 执行并收集结果
        results = []
        for assignment in assignments:
            worker = self.workers.get(assignment["worker"])
            if worker:
                context = TaskContext(
                    original_task=assignment["subtask"],
                    current_step="execution",
                    previous_results=[]
                )
                result = await worker.process(context)
                results.append({
                    "subtask": assignment["subtask"],
                    "worker": assignment["worker"],
                    "result": result
                })
        
        # 4. 汇总结果
        summary = await self._summarize_results(task, results)
        
        return {
            "task": task,
            "subtask_results": results,
            "summary": summary
        }
    
    async def _decompose_task(self, task: str) -> list[dict]:
        """分解任务"""
        # 实际使用LLM分解
        return [
            {"id": 1, "description": f"{task} - 子任务1"},
            {"id": 2, "description": f"{task} - 子任务2"}
        ]
    
    async def _assign_tasks(self, subtasks: list[dict]) -> list[dict]:
        """分配任务给Workers"""
        worker_names = list(self.workers.keys())
        return [
            {"subtask": st["description"], "worker": worker_names[i % len(worker_names)]}
            for i, st in enumerate(subtasks)
        ]
    
    async def _summarize_results(self, task: str, results: list[dict]) -> str:
        """汇总结果"""
        return f"任务'{task}'已完成，共{len(results)}个子任务"
```

---

## 💻 对话协商实现

```python
class NegotiatingAgent:
    """协商Agent - 通过对话达成共识"""
    
    def __init__(self, name: str, position: str):
        self.name = name
        self.position = position  # 初始立场
        self.conversation_history = []
    
    async def respond(self, message: str) -> dict:
        """响应对方消息"""
        self.conversation_history.append({
            "from": "other",
            "content": message
        })
        
        # 生成响应（实际使用LLM）
        response = await self._generate_response(message)
        
        self.conversation_history.append({
            "from": "self",
            "content": response["message"]
        })
        
        return response
    
    async def _generate_response(self, message: str) -> dict:
        """生成响应"""
        # 实际调用LLM生成
        return {
            "message": f"[{self.name}] 关于你说的'{message[:30]}...'，我的看法是...",
            "agreement_level": 0.7,  # 0-1之间
            "proposal": None
        }

class NegotiationOrchestrator:
    """协商协调器"""
    
    def __init__(self, agent_a: NegotiatingAgent, agent_b: NegotiatingAgent):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.max_rounds = 10
        self.consensus_threshold = 0.85
    
    async def negotiate(self, topic: str) -> dict:
        """进行协商"""
        conversation = []
        
        # Agent A先发言
        current_message = f"讨论议题: {topic}"
        current_agent = self.agent_a
        other_agent = self.agent_b
        
        for round_num in range(self.max_rounds):
            response = await current_agent.respond(current_message)
            conversation.append({
                "round": round_num,
                "speaker": current_agent.name,
                "message": response["message"],
                "agreement": response["agreement_level"]
            })
            
            # 检查是否达成共识
            if response["agreement_level"] >= self.consensus_threshold:
                return {
                    "status": "consensus_reached",
                    "rounds": round_num + 1,
                    "conversation": conversation,
                    "final_agreement": response
                }
            
            # 交换角色
            current_message = response["message"]
            current_agent, other_agent = other_agent, current_agent
        
        return {
            "status": "max_rounds_reached",
            "rounds": self.max_rounds,
            "conversation": conversation
        }

# 使用
async def resolve_conflict():
    agent_a = NegotiatingAgent("架构师", "使用微服务架构")
    agent_b = NegotiatingAgent("开发者", "使用单体架构")
    
    orchestrator = NegotiationOrchestrator(agent_a, agent_b)
    result = await orchestrator.negotiate("选择系统架构方案")
    
    return result
```

---

## 📊 模式选择指南

| 模式 | 适用场景 | 优点 | 缺点 |
|-----|---------|------|------|
| 串行Pipeline | 有明确阶段的任务 | 简单清晰 | 串行瓶颈 |
| 并行扇出 | 可并行的独立子任务 | 高效并发 | 需要聚合逻辑 |
| 层级委派 | 复杂项目管理 | 可扩展 | 管理开销 |
| 对话协商 | 需要达成共识 | 结果优化 | 时间成本高 |

---

## 📊 学习检查清单

- [ ] 理解四种协作模式的区别
- [ ] 能够实现串行Pipeline
- [ ] 能够实现并行扇出
- [ ] 理解层级委派的设计思想
- [ ] 了解对话协商机制

---

## 🎯 Week 11完成！

恭喜完成高级Agent系统全部内容！

继续前往：
👉 [Week 12: 毕业项目](../week12/README.md)
