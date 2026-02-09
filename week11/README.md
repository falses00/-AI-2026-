# 📘 第11周：高级Agent系统

> **学习目标**：掌握复杂Agent架构，构建生产级多Agent协作系统

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 设计复杂Agent架构
- ✅ 实现Agent记忆系统
- ✅ 构建多Agent协作流程
- ✅ 实现Agent监控与调试
- ✅ 部署生产级Agent系统
- ✅ 🆕 实现可观测性（LangFuse + Prometheus）
- ✅ 🆕 构建安全护栏（Guardrails）
- ✅ 🆕 设计人机协作流程（HITL）


---

## 📚 学习路径

### Day 1：Agent架构进阶

#### 📖 教程材料
- [高级Agent架构模式](./tutorials/01_advanced_architecture.md) 🔜

**核心架构**：

```
┌────────────────────────────────────────────────────────────────┐
│                    生产级Agent架构                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    协调层 (Orchestrator)                 │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │   │任务规划器│  │状态管理器│  │结果聚合器│            │   │
│  │   └──────────┘  └──────────┘  └──────────┘            │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         ▼                ▼                ▼                    │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│  │ 研究Agent │     │ 执行Agent │     │ 验证Agent │               │
│  │ (Research) │     │ (Execute) │     │ (Verify)  │               │
│  └─────┬────┘     └─────┬────┘     └─────┬────┘               │
│        │                │                │                      │
│        ▼                ▼                ▼                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      工具层 (Tools)                       │  │
│  │  [搜索] [代码执行] [文件操作] [API调用] [数据库] [...]   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      记忆层 (Memory)                      │  │
│  │  [短期记忆] [长期记忆] [情景记忆] [语义记忆]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### Day 2：Agent记忆系统

#### 📖 教程材料
- [Agent记忆系统设计](./tutorials/02_memory_system.md) 🔜

**记忆类型**：

| 类型 | 描述 | 实现方式 |
|------|------|---------|
| 短期记忆 | 当前对话上下文 | 消息列表 |
| 长期记忆 | 跨会话持久信息 | 向量数据库 |
| 情景记忆 | 具体事件记录 | 结构化存储 |
| 语义记忆 | 一般知识 | 知识图谱 |

#### 💻 记忆系统实现
```python
from typing import Optional
from datetime import datetime
import chromadb

class AgentMemory:
    """Agent记忆系统"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.short_term: list[dict] = []  # 短期记忆
        self.client = chromadb.Client()
        self.long_term = self.client.get_or_create_collection(
            name=f"agent_{agent_id}_memory"
        )
    
    def add_to_short_term(self, message: dict):
        """添加到短期记忆"""
        self.short_term.append({
            **message,
            "timestamp": datetime.now().isoformat()
        })
        # 保持最近20条
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def consolidate_to_long_term(self, summary: str, metadata: dict):
        """将重要信息固化到长期记忆"""
        self.long_term.add(
            documents=[summary],
            metadatas=[{**metadata, "timestamp": datetime.now().isoformat()}],
            ids=[f"memory_{datetime.now().timestamp()}"]
        )
    
    def recall(self, query: str, n_results: int = 5) -> list[str]:
        """从长期记忆中检索相关信息"""
        results = self.long_term.query(query_texts=[query], n_results=n_results)
        return results["documents"][0] if results["documents"] else []
    
    def get_context(self) -> str:
        """获取当前上下文"""
        return "\n".join([
            f"{m['role']}: {m['content']}" 
            for m in self.short_term[-10:]
        ])
```

---

### Day 3：多Agent协作模式

#### 📖 教程材料
- [多Agent协作设计](./tutorials/03_multi_agent.md) 🔜

**协作模式**：

```
模式1: 顺序执行 (Sequential)
┌────────┐    ┌────────┐    ┌────────┐
│Agent A │ → │Agent B │ → │Agent C │
└────────┘    └────────┘    └────────┘

模式2: 并行执行 (Parallel)
         ┌────────┐
         │Agent A │
┌────────┤        ├────────┐
│        └────────┘        │
│        ┌────────┐        ▼
│        │Agent B │    ┌────────┐
│        │        │ → │ 聚合器  │
│        └────────┘    └────────┘
│        ┌────────┐        ▲
│        │Agent C │        │
└────────┤        ├────────┘
         └────────┘

模式3: 层级委托 (Hierarchical)
         ┌────────────┐
         │ 主管Agent   │
         └─────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│工人A   │ │工人B   │ │工人C   │
└────────┘ └────────┘ └────────┘
```

#### 💻 多Agent协作框架
```python
from abc import ABC, abstractmethod
from enum import Enum
import asyncio

class AgentRole(Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, role: AgentRole, llm_client):
        self.name = name
        self.role = role
        self.client = llm_client
    
    @abstractmethod
    async def execute(self, task: dict, context: dict) -> dict:
        """执行任务"""
        pass

class Orchestrator:
    """多Agent协调器"""
    
    def __init__(self):
        self.agents: dict[AgentRole, BaseAgent] = {}
        self.task_queue = asyncio.Queue()
    
    def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.role] = agent
    
    async def execute_workflow(self, workflow: list[dict]) -> dict:
        """执行工作流"""
        context = {}
        
        for step in workflow:
            role = step["role"]
            task = step["task"]
            
            if role not in self.agents:
                raise ValueError(f"未找到角色: {role}")
            
            agent = self.agents[role]
            result = await agent.execute(task, context)
            
            # 更新上下文
            context[f"{role.value}_result"] = result
        
        return context
```

---

### Day 4：Agent监控与调试

#### 📖 教程材料
- [可观测性实战：LangFuse + Prometheus](./tutorials/04_observability.md) ✅

**监控维度**：

| 维度 | 指标 | 工具 |
|------|------|------|
| 性能 | 响应时间、吞吐量 | Prometheus |
| 质量 | 成功率、准确率 | 自定义指标 |
| 成本 | Token消耗、API调用 | 计费系统 |
| 安全 | 异常行为、敏感操作 | 日志审计 |

---

### Day 5：安全护栏与人机协作

#### 📖 教程材料
- [Guardrails：AI安全护栏](./tutorials/05_guardrails.md) ✅
- [Human-in-the-Loop：人机协作模式](./tutorials/06_human_in_the_loop.md) ✅

**安全护栏清单**：
- [ ] 输入护栏（越狱检测、敏感词过滤）
- [ ] 输出护栏（PII脱敏、幻觉检测）
- [ ] 操作护栏（敏感操作审批）
- [ ] 政策引擎配置

---

### Day 6-7：实战项目

#### 🚀 项目：自动化内容工作流

**项目目标**：
构建一个多Agent协作的内容生产系统

**Agent角色**：
- 📋 **规划Agent**：分解任务、制定计划
- 🔍 **研究Agent**：搜索资料、收集信息
- ✍️ **写作Agent**：撰写内容
- 🔎 **审核Agent**：检查质量、提供反馈
- 🎨 **优化Agent**：优化表达、润色文章

**工作流**：
```
用户需求 → 规划 → 研究 → 写作 → 审核 → 优化 → 最终输出
                           ↑           │
                           └───反馈────┘
```

---

## 📊 学习检查清单

### 架构设计
- [ ] 理解生产级Agent架构
- [ ] 会设计工具层
- [ ] 能够实现协调器

### 记忆系统
- [ ] 理解不同记忆类型
- [ ] 会实现长期记忆
- [ ] 能够实现记忆检索

### 多Agent协作
- [ ] 知道常见协作模式
- [ ] 会实现工作流
- [ ] 能够处理Agent间通信

### 生产化
- [ ] 会实现监控系统
- [ ] 能够进行调试
- [ ] 理解生产化要求

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 12: 毕业项目](../week12/README.md)

---

**复杂任务需要Agent团队协作完成！💪**
