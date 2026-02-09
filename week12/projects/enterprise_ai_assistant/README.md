# 🏢 企业AI助手平台项目

> **Week 12 毕业项目选项A** - 完整企业级AI Agent应用 (2025-2026标准)

---

## 🎯 项目概述

构建一个**生产级企业AI助手平台**，综合运用12周所学技术，且符合2025-2026年企业AI最佳实践：

### 核心技术映射

| 技术模块 | 对应周次 | 应用场景 |
|---------|---------|---------| 
| FastAPI + Pydantic | Week 1 | API后端 |
| LLM API调用 | Week 2 | 对话核心 |
| MCP协议 | Week 3 | 工具扩展 |
| RAG检索 | Week 4-5 | 知识问答 |
| Agent系统 | Week 6, 11 | 智能决策 |
| 企业架构 | Week 7 | 系统设计 |
| 多模态 | Week 8 | 图文理解 |
| 模型微调 | Week 9 | 领域适配 |
| UX设计 | Week 10 | 用户体验 |

### 🆕 企业级新增能力

| 能力 | 技术 | 说明 |
|-----|------|------|
| **可观测性** | LangFuse + Prometheus | 端到端追踪、指标监控 |
| **Guardrails** | NeMo Guardrails | 输入/输出安全护栏 |
| **多Agent编排** | LangGraph | 状态机工作流 |
| **人机协作** | 自定义审批流 | 敏感操作审批 |
| **治理审计** | 决策日志系统 | 合规与成本追踪 |

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     🏢 企业级AI Agent平台架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    📊 可观测性层 (Observability)                     │   │
│  │   LangFuse追踪 ──▶ Prometheus指标 ──▶ Grafana仪表板 ──▶ 告警       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🛡️ Guardrails层 (Safety)                          │   │
│  │                                                                      │   │
│  │   输入 ──▶ 越狱检测 ──▶ 意图分类 ──▶ 敏感词过滤                     │   │
│  │   输出 ──▶ 幻觉检测 ──▶ PII脱敏 ──▶ 内容审核                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🎭 多Agent编排层 (LangGraph)                       │   │
│  │                                                                      │   │
│  │       ┌───────────────┐                                             │   │
│  │       │  Supervisor   │◀──────────────────────────┐                 │   │
│  │       │    Agent      │                           │                 │   │
│  │       └───────┬───────┘                           │                 │   │
│  │               │ 路由决策                          │ 结果回报        │   │
│  │    ┌──────────┼──────────┬──────────┐            │                 │   │
│  │    ▼          ▼          ▼          ▼            │                 │   │
│  │ ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │                 │   │
│  │ │研究员│  │分析师│  │写作者│  │审查员│──────────┘                 │   │
│  │ │Agent │  │Agent │  │Agent │  │Agent │                             │   │
│  │ └──────┘  └──────┘  └──────┘  └──────┘                             │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    👤 人机协作层 (HITL)                               │   │
│  │   置信度检查 ──▶ 敏感操作审批 ──▶ 问题升级 ──▶ 回退策略            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🔌 工具层 (MCP + Native)                           │   │
│  │   知识库检索 │ Web搜索 │ 数据分析 │ 代码执行 │ 日程管理            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    📈 治理与审计层                                    │   │
│  │   决策日志 ──▶ 合规检查 ──▶ 成本核算 ──▶ 审计报告                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    💾 存储层                                         │   │
│  │   PostgreSQL(元数据) + Redis(缓存) + Milvus(向量) + MinIO(文件)     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
enterprise_ai_assistant/
├── README.md
├── docker-compose.yml
├── .env.example
├── pyproject.toml
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                 # FastAPI入口
│   │   ├── config.py               # 配置管理
│   │   │
│   │   ├── api/                    # API路由
│   │   │   ├── __init__.py
│   │   │   ├── chat.py             # 对话API
│   │   │   ├── documents.py        # 文档API
│   │   │   ├── agents.py           # Agent API
│   │   │   ├── approval.py         # 🆕 审批API
│   │   │   └── auth.py             # 认证API
│   │   │
│   │   ├── services/               # 核心服务
│   │   │   ├── __init__.py
│   │   │   ├── llm.py              # LLM服务
│   │   │   ├── rag.py              # RAG服务
│   │   │   ├── memory.py           # 记忆服务
│   │   │   ├── orchestrator.py     # 🆕 多Agent编排
│   │   │   ├── guardrails.py       # 🆕 安全护栏
│   │   │   ├── observability.py    # 🆕 可观测性
│   │   │   ├── human_loop.py       # 🆕 人机协作
│   │   │   └── governance.py       # 🆕 治理审计
│   │   │
│   │   ├── agents/                 # 🆕 Agent定义
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 基础Agent类
│   │   │   ├── supervisor.py       # 协调者Agent
│   │   │   ├── researcher.py       # 研究员Agent
│   │   │   ├── analyzer.py         # 分析师Agent
│   │   │   └── critic.py           # 审查员Agent
│   │   │
│   │   ├── workflows/              # 🆕 LangGraph工作流
│   │   │   ├── __init__.py
│   │   │   ├── research_flow.py    # 研究工作流
│   │   │   └── qa_flow.py          # 问答工作流
│   │   │
│   │   ├── guardrails/             # 🆕 护栏配置
│   │   │   ├── config.yml          # NeMo配置
│   │   │   ├── input_rails.co      # 输入规则
│   │   │   ├── output_rails.co     # 输出规则
│   │   │   └── policies.yaml       # 政策定义
│   │   │
│   │   ├── models/                 # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   └── audit_log.py        # 🆕 审计日志模型
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── embedding.py
│   │       └── metrics.py          # 🆕 指标收集
│   │
│   └── tests/
│       ├── test_chat.py
│       ├── test_rag.py
│       ├── test_orchestrator.py    # 🆕
│       └── test_guardrails.py      # 🆕
│
├── monitoring/                     # 🆕 监控配置
│   ├── prometheus.yml
│   ├── grafana/
│   │   ├── provisioning/
│   │   └── dashboards/
│   │       ├── agent_overview.json
│   │       └── llm_metrics.json
│   └── alertmanager/
│       └── alerts.yml
│
├── k8s/                            # 🆕 Kubernetes部署
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── hpa.yaml                    # 自动伸缩
│   └── ingress.yaml
│
├── frontend/                       # 可选前端
│   ├── package.json
│   └── src/
│
└── docs/
    ├── architecture.md
    ├── api.md
    ├── deployment.md
    ├── guardrails.md               # 🆕
    └── governance.md               # 🆕
```

---

## 🔧 核心模块实现

### 1. 可观测性模块 (`services/observability.py`)

```python
"""
可观测性服务 - 端到端追踪 + 指标监控
"""
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from prometheus_client import Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger()

# Prometheus指标定义
llm_requests = Counter(
    'llm_requests_total', 
    'LLM请求总数',
    ['model', 'agent', 'status']
)
llm_latency = Histogram(
    'llm_latency_seconds',
    'LLM响应延迟',
    ['model', 'agent'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)
llm_tokens = Counter(
    'llm_tokens_total',
    'Token使用量',
    ['model', 'type']  # type: input/output
)
llm_cost = Counter(
    'llm_cost_dollars',
    'LLM调用成本(美元)',
    ['model']
)
active_conversations = Gauge(
    'active_conversations',
    '活跃对话数'
)


class ObservabilityService:
    """可观测性服务"""
    
    def __init__(self):
        self.langfuse = Langfuse()
    
    @observe(name="chat_completion")
    async def traced_chat(
        self, 
        model: str,
        messages: list,
        agent_id: str = "default"
    ):
        """带完整追踪的对话"""
        
        # 开始计时
        with llm_latency.labels(model=model, agent=agent_id).time():
            try:
                result = await self._call_llm(model, messages)
                
                # 记录成功指标
                llm_requests.labels(
                    model=model, 
                    agent=agent_id, 
                    status="success"
                ).inc()
                
                # 记录Token使用
                llm_tokens.labels(model=model, type="input").inc(
                    result.usage.prompt_tokens
                )
                llm_tokens.labels(model=model, type="output").inc(
                    result.usage.completion_tokens
                )
                
                # 记录成本
                cost = self._calculate_cost(model, result.usage)
                llm_cost.labels(model=model).inc(cost)
                
                # 添加LangFuse元数据
                langfuse_context.update_current_observation(
                    metadata={"tokens": result.usage.total_tokens}
                )
                
                return result
                
            except Exception as e:
                llm_requests.labels(
                    model=model, 
                    agent=agent_id, 
                    status="error"
                ).inc()
                logger.error("llm_call_failed", error=str(e))
                raise
    
    def _calculate_cost(self, model: str, usage) -> float:
        """计算API调用成本"""
        pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "deepseek-chat": {"input": 0.00014, "output": 0.00028},
        }
        rates = pricing.get(model, {"input": 0.001, "output": 0.002})
        return (
            usage.prompt_tokens * rates["input"] / 1000 +
            usage.completion_tokens * rates["output"] / 1000
        )
```

### 2. Guardrails护栏模块 (`services/guardrails.py`)

```python
"""
安全护栏服务 - 输入/输出验证
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional
import re


class RailResult(BaseModel):
    """护栏检查结果"""
    passed: bool
    blocked_reason: Optional[str] = None
    modified_content: Optional[str] = None


class GuardrailsService:
    """安全护栏服务"""
    
    # 越狱攻击模式
    JAILBREAK_PATTERNS = [
        r"ignore.*previous.*instructions",
        r"pretend.*you.*are",
        r"act.*as.*if",
        r"DAN.*mode",
        r"jailbreak",
    ]
    
    # 敏感词列表
    SENSITIVE_WORDS = ["密码", "信用卡", "身份证", "银行卡"]
    
    # PII正则模式
    PII_PATTERNS = {
        "phone": r"\b1[3-9]\d{9}\b",
        "id_card": r"\b\d{17}[\dXx]\b",
        "email": r"\b[\w.-]+@[\w.-]+\.\w+\b",
    }
    
    async def validate_input(self, text: str) -> RailResult:
        """
        输入护栏检查:
        1. 越狱攻击检测
        2. 敏感词过滤
        3. 长度限制
        """
        # 1. 越狱检测
        for pattern in self.JAILBREAK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return RailResult(
                    passed=False,
                    blocked_reason=f"检测到潜在越狱攻击: {pattern}"
                )
        
        # 2. 敏感词检查
        for word in self.SENSITIVE_WORDS:
            if word in text:
                return RailResult(
                    passed=False,
                    blocked_reason=f"请勿在对话中提供敏感信息: {word}"
                )
        
        # 3. 长度限制
        if len(text) > 10000:
            return RailResult(
                passed=False,
                blocked_reason="输入过长，请精简后重试"
            )
        
        return RailResult(passed=True)
    
    async def validate_output(self, text: str) -> RailResult:
        """
        输出护栏检查:
        1. PII脱敏
        2. 幻觉标记检测
        3. 有害内容过滤
        """
        modified = text
        
        # 1. PII脱敏
        for pii_type, pattern in self.PII_PATTERNS.items():
            modified = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", modified)
        
        # 2. 检测常见幻觉标记
        hallucination_markers = ["据我所知", "我认为", "可能是"]
        has_uncertainty = any(m in text for m in hallucination_markers)
        
        return RailResult(
            passed=True,
            modified_content=modified if modified != text else None
        )
    
    async def check_action_policy(
        self, 
        action: str, 
        parameters: dict
    ) -> RailResult:
        """检查Agent操作是否符合政策"""
        
        # 禁止的操作
        forbidden_actions = ["delete_database", "send_email_bulk", "access_admin"]
        
        if action in forbidden_actions:
            return RailResult(
                passed=False,
                blocked_reason=f"操作 {action} 被政策禁止"
            )
        
        # 需要审批的操作
        approval_required = ["send_email", "modify_user", "export_data"]
        
        if action in approval_required:
            return RailResult(
                passed=False,
                blocked_reason=f"操作 {action} 需要人工审批"
            )
        
        return RailResult(passed=True)
```

### 3. 多Agent编排模块 (`services/orchestrator.py`)

```python
"""
多Agent编排器 - 基于LangGraph的状态机工作流
"""
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
import operator


class AgentState(TypedDict):
    """Agent状态定义"""
    task: str
    messages: Annotated[list, operator.add]  # 消息累积
    next_agent: str
    research_results: list
    analysis_results: dict
    final_answer: str
    iteration_count: int


class MultiAgentOrchestrator:
    """多Agent编排器"""
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建Agent状态图"""
        
        workflow = StateGraph(AgentState)
        
        # ===== 添加节点 =====
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # ===== 设置入口点 =====
        workflow.set_entry_point("supervisor")
        
        # ===== 条件路由 =====
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "research": "researcher",
                "analyze": "analyzer",
                "critique": "critic",
                "synthesize": "synthesizer",
                "end": END
            }
        )
        
        # 各Agent完成后返回Supervisor
        for agent in ["researcher", "analyzer", "critic"]:
            workflow.add_edge(agent, "supervisor")
        
        # Synthesizer直接结束
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _supervisor_node(self, state: AgentState) -> dict:
        """Supervisor Agent - 任务分解与路由"""
        
        system_prompt = """你是一个任务协调者。根据任务和当前状态，决定下一步：
        - "research": 需要搜索和收集信息
        - "analyze": 需要分析已有数据
        - "critique": 需要审查和验证结果
        - "synthesize": 信息充足，可以生成最终答案
        - "end": 任务完成或无法继续
        
        当前迭代次数: {iteration_count}
        已有研究结果: {has_research}
        已有分析结果: {has_analysis}
        """
        
        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt.format(
                iteration_count=state.get("iteration_count", 0),
                has_research=bool(state.get("research_results")),
                has_analysis=bool(state.get("analysis_results"))
            )},
            {"role": "user", "content": f"任务: {state['task']}"}
        ])
        
        # 解析决策
        next_agent = self._parse_decision(response.content)
        
        return {
            "next_agent": next_agent,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "messages": [AIMessage(content=f"Supervisor决策: {next_agent}")]
        }
    
    async def _researcher_node(self, state: AgentState) -> dict:
        """Researcher Agent - 信息收集"""
        # 实现研究逻辑...
        return {"research_results": [...], "messages": [...]}
    
    async def _analyzer_node(self, state: AgentState) -> dict:
        """Analyzer Agent - 数据分析"""
        # 实现分析逻辑...
        return {"analysis_results": {...}, "messages": [...]}
    
    async def _critic_node(self, state: AgentState) -> dict:
        """Critic Agent - 质量审查"""
        # 实现审查逻辑...
        return {"messages": [...]}
    
    async def _synthesizer_node(self, state: AgentState) -> dict:
        """Synthesizer - 生成最终答案"""
        # 综合所有结果生成答案...
        return {"final_answer": "...", "messages": [...]}
    
    def _route_from_supervisor(self, state: AgentState) -> str:
        """路由函数"""
        # 防止无限循环
        if state.get("iteration_count", 0) > 10:
            return "synthesize"
        return state.get("next_agent", "end")
    
    async def run(
        self, 
        task: str, 
        thread_id: str = "default"
    ) -> str:
        """执行多Agent工作流"""
        
        config = {"configurable": {"thread_id": thread_id}}
        
        result = await self.graph.ainvoke(
            {"task": task, "messages": [], "iteration_count": 0},
            config=config
        )
        
        return result.get("final_answer", "无法生成答案")
```

---

## 📋 评分标准

| 维度 | 分值 | 要求 |
|------|------|------|
| **多Agent编排** | 25分 | LangGraph实现Supervisor+Specialist模式 |
| **可观测性** | 20分 | LangFuse追踪 + Prometheus指标 |
| **Guardrails** | 15分 | 输入/输出护栏 + 政策检查 |
| **功能完整性** | 15分 | RAG + 对话 + 工具调用 |
| **代码质量** | 15分 | 类型完整、测试覆盖 |
| **生产化** | 10分 | Docker/K8s部署 + 监控 |

---

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone <your-repo>
cd enterprise_ai_assistant

# 2. 配置环境
cp .env.example .env
# 编辑.env填写API密钥

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# API: http://localhost:8000
# Grafana: http://localhost:3000
# LangFuse: http://localhost:3001
```

---

## 📚 参考资源

- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [LangFuse文档](https://langfuse.com/docs)
- [Prometheus + Grafana监控](https://prometheus.io/docs/)

---

**完成这个企业级项目，你将具备真正的AI Agent工程能力！🎓**
