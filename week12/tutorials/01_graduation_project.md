# 🎓 毕业项目指南 - 企业级AI Agent平台

> **目标**：综合运用12周所学，构建符合企业生产标准的AI Agent应用

---

## 🏆 项目选项

### 选项A：企业AI助手平台 (推荐)

**难度**：⭐⭐⭐⭐⭐ | **预计时间**：50小时

构建一个**生产级企业AI助手**，包含2025-2026年企业AI系统的核心要素：

| 企业级能力 | 技术实现 | 重要性 |
|-----------|---------|--------|
| **可观测性** | LangFuse + Prometheus + Grafana | 🔴 必需 |
| **Guardrails护栏** | NeMo Guardrails + 政策引擎 | 🔴 必需 |
| **多Agent编排** | LangGraph状态机 + CrewAI | 🔴 必需 |
| **人机协作** | 审批流程 + 升级机制 | 🟡 推荐 |
| **治理审计** | 决策日志 + 合规报告 | 🟡 推荐 |
| **生产部署** | K8s + HPA + 蓝绿部署 | 🟡 推荐 |

```
技术栈要求：
├── 后端：FastAPI + PostgreSQL + Redis
├── 向量库：Milvus/Qdrant
├── LLM：GPT-4o/DeepSeek/Claude
├── Agent框架：LangGraph + LangChain
├── 可观测性：LangFuse + OpenTelemetry
├── 护栏：NeMo Guardrails / Guardrails AI
└── 部署：Docker + Kubernetes
```

### 选项B：智能内容创作平台

**难度**：⭐⭐⭐⭐ | **预计时间**：35小时

### 选项C：个人AI工作台

**难度**：⭐⭐⭐ | **预计时间**：25小时

---

## 📊 企业级架构 (2025-2026标准)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     🏢 企业级AI Agent平台架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    📊 可观测性层 (Observability)                     │   │
│  │   LangFuse端到端追踪 + Prometheus指标 + Grafana仪表板 + 告警         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🛡️ Guardrails层 (Safety)                          │   │
│  │   输入验证 → 意图分类 → 越狱检测 → 输出审核 → PII脱敏               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🎭 多Agent编排层 (Orchestration)                   │   │
│  │                                                                      │   │
│  │   ┌───────────┐    ┌───────────┐    ┌───────────┐                   │   │
│  │   │ Supervisor│───▶│ Specialist│───▶│  Critic   │                   │   │
│  │   │   Agent   │    │   Agents  │    │   Agent   │                   │   │
│  │   │(协调者)   │    │(领域专家) │    │(质量审查) │                   │   │
│  │   └───────────┘    └───────────┘    └───────────┘                   │   │
│  │                                                                      │   │
│  │   LangGraph状态图 + 条件路由 + 检查点持久化                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    👤 人机协作层 (Human-in-the-Loop)                  │   │
│  │   置信度阈值 → 敏感操作审批 → 问题升级 → 回退策略                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    📈 治理与审计层 (Governance)                       │   │
│  │   决策日志 → 审计追踪 → 合规报告 → 成本核算 → RBAC权限              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │  
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    💾 存储层                                         │   │
│  │   PostgreSQL + Redis + Milvus/Qdrant + MinIO                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 项目评分标准 (企业级)

| 维度 | 权重 | 优秀标准 |
|------|------|---------| 
| **功能完整性** | 25% | 多Agent协作、RAG、护栏全部实现 |
| **可观测性** | 20% | 端到端追踪、指标监控、告警配置 |
| **安全护栏** | 15% | 输入/输出验证、越狱防护、PII脱敏 |
| **代码质量** | 15% | 类型完整、测试覆盖、文档清晰 |
| **系统设计** | 15% | 多Agent架构、状态管理、容错设计 |
| **用户体验** | 10% | 响应快、错误友好、人机协作流畅 |

---

## 🛠️ 项目开发流程 (敏捷迭代)

### Phase 1: 基础设施搭建 (Week 1)

```
□ 设置项目仓库和CI/CD
□ 配置可观测性基础设施 (LangFuse/Prometheus)
□ 设计多Agent系统状态图
□ 定义Guardrails规则
□ 搭建开发环境 (Docker Compose)
```

### Phase 2: 核心功能开发 (Week 2)

```
□ 实现Supervisor + Specialist Agent编排
□ 集成RAG检索服务
□ 实现Guardrails护栏层
□ 开发人机协作审批流程
□ 编写单元测试和集成测试
```

### Phase 3: 生产化与部署 (Week 3)

```
□ 完善Grafana监控仪表板
□ 配置K8s部署清单
□ 设置自动伸缩 (HPA)
□ 编写治理审计报告生成器
□ 准备演示视频和技术文档
```

---

## 📁 企业级项目结构

```
enterprise_ai_assistant/
├── README.md
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                 # FastAPI入口
│   │   ├── config.py               # 配置管理
│   │   │
│   │   ├── api/                    # API路由
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── agents.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/               # 核心服务
│   │   │   ├── llm.py              # LLM服务
│   │   │   ├── rag.py              # RAG服务
│   │   │   ├── orchestrator.py     # 🆕 多Agent编排
│   │   │   ├── guardrails.py       # 🆕 安全护栏
│   │   │   ├── observability.py    # 🆕 可观测性
│   │   │   ├── human_loop.py       # 🆕 人机协作
│   │   │   ├── governance.py       # 🆕 治理审计
│   │   │   └── memory.py           # 记忆服务
│   │   │
│   │   ├── agents/                 # 🆕 Agent定义
│   │   │   ├── supervisor.py       # 协调者Agent
│   │   │   ├── researcher.py       # 研究员Agent
│   │   │   ├── analyzer.py         # 分析师Agent
│   │   │   └── critic.py           # 审查员Agent
│   │   │
│   │   ├── workflows/              # 🆕 LangGraph工作流
│   │   │   ├── research_flow.py
│   │   │   └── analysis_flow.py
│   │   │
│   │   ├── guardrails/             # 🆕 护栏配置
│   │   │   ├── input_rails.yaml
│   │   │   ├── output_rails.yaml
│   │   │   └── policies.yaml
│   │   │
│   │   ├── models/                 # 数据模型
│   │   └── utils/                  # 工具函数
│   │
│   └── tests/
│
├── monitoring/                     # 🆕 监控配置
│   ├── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── alerts/
│
├── k8s/                            # 🆕 K8s部署
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── hpa.yaml
│   └── ingress.yaml
│
└── docs/
    ├── architecture.md
    ├── api.md
    ├── deployment.md
    └── governance.md
```

---

## 🔧 核心模块实现指南

### 1. 可观测性模块

```python
# services/observability.py
from langfuse import Langfuse
from langfuse.decorators import observe
from prometheus_client import Counter, Histogram, Gauge

# Prometheus指标
llm_requests = Counter('llm_requests_total', 'LLM请求总数', ['model', 'status'])
llm_latency = Histogram('llm_latency_seconds', 'LLM响应延迟', ['model'])
llm_tokens = Counter('llm_tokens_total', 'Token使用量', ['model', 'type'])
active_agents = Gauge('active_agents', '活跃Agent数量')

class ObservabilityService:
    def __init__(self):
        self.langfuse = Langfuse()
    
    @observe(name="agent_execution")
    async def trace_agent(self, agent_id: str, task: str):
        """追踪Agent执行全过程"""
        with llm_latency.labels(model="gpt-4").time():
            result = await self.execute_with_trace(task)
        llm_requests.labels(model="gpt-4", status="success").inc()
        return result
```

### 2. Guardrails护栏模块

```python
# services/guardrails.py
from nemoguardrails import RailsConfig, LLMRails

class GuardrailsService:
    def __init__(self):
        config = RailsConfig.from_path("./guardrails")
        self.rails = LLMRails(config)
    
    async def validate_input(self, text: str) -> tuple[bool, str]:
        """
        输入护栏检查:
        - 越狱攻击检测
        - 敏感词过滤
        - 意图分类验证
        """
        result = await self.rails.generate(
            messages=[{"role": "user", "content": text}]
        )
        return result.get("blocked", False), result.get("reason", "")
    
    async def validate_output(self, text: str) -> tuple[bool, str]:
        """
        输出护栏检查:
        - 幻觉检测
        - PII脱敏
        - 内容安全审核
        """
        pass
```

### 3. 多Agent编排模块

```python
# services/orchestrator.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    task: str
    messages: list
    next_agent: str
    final_answer: str

class MultiAgentOrchestrator:
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("researcher", self.research_node)
        workflow.add_node("analyzer", self.analyze_node)
        workflow.add_node("critic", self.critique_node)
        
        # 条件边
        workflow.add_conditional_edges(
            "supervisor",
            self.route_decision,
            {
                "research": "researcher",
                "analyze": "analyzer",
                "critique": "critic",
                "end": END
            }
        )
        
        workflow.set_entry_point("supervisor")
        return workflow.compile()
    
    async def run(self, task: str) -> str:
        result = await self.graph.ainvoke({"task": task, "messages": []})
        return result["final_answer"]
```

### 4. 人机协作模块

```python
# services/human_loop.py
import asyncio
from enum import Enum

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

class HumanInTheLoop:
    def __init__(self, notification_service):
        self.notifications = notification_service
        self.pending_approvals = {}
    
    async def request_approval(
        self,
        action: str,
        context: dict,
        timeout_seconds: int = 300
    ) -> ApprovalStatus:
        """请求人工审批敏感操作"""
        approval_id = self._create_approval(action, context)
        
        # 发送通知
        await self.notifications.send(
            type="approval_request",
            data={"id": approval_id, "action": action}
        )
        
        # 等待审批结果
        try:
            result = await asyncio.wait_for(
                self._wait_for_approval(approval_id),
                timeout=timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            return ApprovalStatus.TIMEOUT
    
    async def fallback(self, context: dict) -> str:
        """Agent无法处理时的回退策略"""
        return "抱歉，我需要人工协助处理此请求。已将问题升级给相关人员。"
```

---

## ✅ 提交要求

### 必须提交：
1. **源代码** - GitHub仓库链接
2. **README.md** - 包含架构图和安装说明
3. **演示视频** - 5-8分钟功能演示
4. **技术文档** - 架构设计 + API文档

### 企业级加分项：
- ✅ LangFuse追踪截图/仪表板
- ✅ Grafana监控仪表板
- ✅ K8s部署成功截图
- ✅ Guardrails测试用例
- ✅ 多Agent协作流程图

---

## 💡 行业最佳实践参考

> [!TIP]
> **2025-2026企业AI趋势**
> - AI从"项目"变成"基础设施"，需要SLA和持续监控
> - 多Agent系统成为标准，Supervisor+Specialist架构
> - 治理和护栏是生产部署的必要条件

> [!IMPORTANT]
> **安全第一**
> - 所有Agent操作都应经过Guardrails验证
> - 敏感操作必须有人工审批机制
> - 完整的审计日志用于合规

> [!WARNING]
> **避免常见陷阱**
> - 不要直接将Agent连接到生产数据库
> - 始终设置Token限制和成本预算
> - 为所有外部API调用添加超时和重试

---

**完成这个企业级项目，你将具备真正的AI工程师能力！🎓🚀**
