# 📈 治理与审计系统

> **学习目标**：掌握企业AI系统的治理框架，实现决策日志、合规审计和成本监控

---

## 1. 为什么需要治理？

企业级AI系统需要满足：
- ✅ **可解释性**：AI决策可被追溯和解释
- ✅ **合规性**：满足行业监管要求（GDPR、等保2.0等）
- ✅ **成本控制**：Token成本可见可控
- ✅ **问责性**：谁做了什么决策，什么时候，为什么

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI治理框架                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    决策层                                  │  │
│   │   Agent决策 → 决策日志 → 审计追踪 → 合规报告             │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    成本层                                  │  │
│   │   Token统计 → 成本核算 → 预算告警 → 成本优化建议         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    权限层                                  │  │
│   │   用户认证 → RBAC权限 → 操作授权 → 访问日志              │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 决策日志系统

### 2.1 日志数据模型

```python
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel
from uuid import UUID, uuid4


class DecisionType(str, Enum):
    """决策类型"""
    TOOL_CALL = "tool_call"           # 工具调用
    AGENT_ROUTING = "agent_routing"   # Agent路由
    LLM_RESPONSE = "llm_response"     # LLM回复
    HUMAN_APPROVAL = "human_approval" # 人工审批
    GUARDRAIL_BLOCK = "guardrail_block"  # 护栏拦截
    DATA_ACCESS = "data_access"       # 数据访问


class AuditLog(BaseModel):
    """审计日志模型"""
    id: UUID = uuid4()
    timestamp: datetime = datetime.utcnow()
    
    # 上下文
    conversation_id: str
    session_id: str
    user_id: Optional[str] = None
    
    # 决策信息
    decision_type: DecisionType
    agent_id: str
    action: str
    input_summary: str          # 输入摘要（脱敏后）
    output_summary: str         # 输出摘要（脱敏后）
    
    # 推理过程
    reasoning: str              # 决策理由
    confidence: float           # 置信度 0-1
    alternatives: list[str]     # 考虑过的其他选项
    
    # 结果
    success: bool
    error_message: Optional[str] = None
    
    # 资源消耗
    tokens_used: int = 0
    latency_ms: float = 0
    cost_usd: float = 0
    
    # 元数据
    metadata: dict = {}
```

### 2.2 审计日志服务

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class AuditLogService:
    """审计日志服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_decision(
        self,
        decision_type: DecisionType,
        agent_id: str,
        action: str,
        input_data: Any,
        output_data: Any,
        reasoning: str,
        confidence: float,
        context: dict,
        **kwargs
    ) -> AuditLog:
        """记录决策"""
        
        log = AuditLog(
            decision_type=decision_type,
            agent_id=agent_id,
            action=action,
            input_summary=self._summarize(input_data),
            output_summary=self._summarize(output_data),
            reasoning=reasoning,
            confidence=confidence,
            conversation_id=context.get("conversation_id", ""),
            session_id=context.get("session_id", ""),
            user_id=context.get("user_id"),
            **kwargs
        )
        
        self.db.add(log)
        await self.db.commit()
        
        return log
    
    def _summarize(self, data: Any, max_length: int = 500) -> str:
        """生成脱敏摘要"""
        text = str(data)
        # PII脱敏
        text = self._mask_pii(text)
        # 截断
        if len(text) > max_length:
            text = text[:max_length] + "..."
        return text
    
    def _mask_pii(self, text: str) -> str:
        """PII脱敏"""
        import re
        # 手机号
        text = re.sub(r'1[3-9]\d{9}', '[PHONE]', text)
        # 身份证
        text = re.sub(r'\d{17}[\dXx]', '[ID_CARD]', text)
        # 邮箱
        text = re.sub(r'[\w.-]+@[\w.-]+\.\w+', '[EMAIL]', text)
        return text
    
    async def get_decision_chain(
        self, 
        conversation_id: str
    ) -> list[AuditLog]:
        """获取完整决策链"""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.conversation_id == conversation_id)
            .order_by(AuditLog.timestamp)
        )
        return result.scalars().all()
    
    async def get_agent_statistics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """获取Agent统计"""
        result = await self.db.execute(
            select(
                AuditLog.agent_id,
                func.count(AuditLog.id).label("total_decisions"),
                func.avg(AuditLog.confidence).label("avg_confidence"),
                func.sum(AuditLog.tokens_used).label("total_tokens"),
                func.sum(AuditLog.cost_usd).label("total_cost")
            )
            .where(AuditLog.timestamp.between(start_date, end_date))
            .group_by(AuditLog.agent_id)
        )
        return [dict(row) for row in result]
```

---

## 3. 成本监控与预算

### 3.1 成本追踪器

```python
from dataclasses import dataclass
from prometheus_client import Counter, Gauge


# Prometheus指标
token_usage = Counter(
    'ai_tokens_total',
    'Total tokens used',
    ['model', 'user_id', 'agent_id']
)
cost_total = Counter(
    'ai_cost_dollars',
    'Total cost in USD',
    ['model', 'user_id']
)
budget_remaining = Gauge(
    'ai_budget_remaining',
    'Remaining budget in USD',
    ['user_id']
)


@dataclass
class CostConfig:
    """成本配置"""
    # 每1K Token价格 (USD)
    PRICING = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "deepseek-chat": {"input": 0.00014, "output": 0.00028},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    }


class CostTracker:
    """成本追踪器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = CostConfig()
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """计算单次调用成本"""
        pricing = self.config.PRICING.get(
            model, 
            {"input": 0.001, "output": 0.002}
        )
        return (
            input_tokens * pricing["input"] / 1000 +
            output_tokens * pricing["output"] / 1000
        )
    
    async def record_usage(
        self,
        user_id: str,
        model: str,
        agent_id: str,
        input_tokens: int,
        output_tokens: int
    ):
        """记录使用量"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        # 更新Prometheus指标
        token_usage.labels(
            model=model, 
            user_id=user_id,
            agent_id=agent_id
        ).inc(input_tokens + output_tokens)
        
        cost_total.labels(model=model, user_id=user_id).inc(cost)
        
        # 持久化到数据库
        await self._save_usage_record(
            user_id, model, agent_id,
            input_tokens, output_tokens, cost
        )
        
        # 检查预算
        await self._check_budget(user_id)
    
    async def get_usage_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """生成使用报告"""
        # 查询数据库...
        return {
            "total_tokens": 150000,
            "total_cost": 2.35,
            "by_model": {
                "gpt-4o": {"tokens": 50000, "cost": 1.5},
                "deepseek-chat": {"tokens": 100000, "cost": 0.85}
            },
            "by_agent": {
                "researcher": {"tokens": 80000, "cost": 1.2},
                "analyzer": {"tokens": 70000, "cost": 1.15}
            },
            "daily_trend": [...]
        }
    
    async def _check_budget(self, user_id: str):
        """检查预算并告警"""
        from app.services.notification import send_alert
        
        usage = await self.get_monthly_usage(user_id)
        budget = await self.get_user_budget(user_id)
        
        remaining = budget - usage["total_cost"]
        budget_remaining.labels(user_id=user_id).set(remaining)
        
        if remaining < budget * 0.2:  # 剩余不足20%
            await send_alert(
                user_id=user_id,
                type="budget_warning",
                message=f"本月AI预算剩余 ${remaining:.2f}，请注意控制使用"
            )
```

---

## 4. 合规报告生成

### 4.1 报告生成器

```python
from jinja2 import Template
from datetime import datetime, timedelta


class ComplianceReportGenerator:
    """合规报告生成器"""
    
    REPORT_TEMPLATE = """
# AI系统合规审计报告

**报告期间**: {{ start_date }} - {{ end_date }}
**生成时间**: {{ generated_at }}
**系统版本**: {{ system_version }}

---

## 1. 执行摘要

| 指标 | 数值 |
|-----|------|
| 总对话数 | {{ stats.total_conversations }} |
| 总决策数 | {{ stats.total_decisions }} |
| 护栏拦截次数 | {{ stats.guardrail_blocks }} |
| 人工审批次数 | {{ stats.human_approvals }} |
| 平均置信度 | {{ "%.2f"|format(stats.avg_confidence) }} |

---

## 2. 决策类型分布

{% for dt in decision_types %}
- **{{ dt.type }}**: {{ dt.count }} 次 ({{ "%.1f"|format(dt.percentage) }}%)
{% endfor %}

---

## 3. 护栏拦截详情

| 拦截原因 | 次数 | 占比 |
|---------|------|------|
{% for block in guardrail_blocks %}
| {{ block.reason }} | {{ block.count }} | {{ "%.1f"|format(block.percentage) }}% |
{% endfor %}

---

## 4. 高风险决策

以下决策的置信度低于0.7或被标记为需关注：

{% for decision in high_risk_decisions %}
### {{ decision.id }}

- **时间**: {{ decision.timestamp }}
- **Agent**: {{ decision.agent_id }}
- **操作**: {{ decision.action }}
- **置信度**: {{ "%.2f"|format(decision.confidence) }}
- **原因**: {{ decision.reasoning }}

{% endfor %}

---

## 5. 成本分析

**总成本**: ${{ "%.2f"|format(cost.total) }}

### 按模型分布
{% for model in cost.by_model %}
- {{ model.name }}: ${{ "%.2f"|format(model.cost) }} ({{ model.tokens }} tokens)
{% endfor %}

---

## 6. 建议

{% for rec in recommendations %}
- {{ rec }}
{% endfor %}

---

*本报告自动生成，如有疑问请联系AI治理团队*
"""
    
    def __init__(self, audit_service: AuditLogService, cost_tracker: CostTracker):
        self.audit = audit_service
        self.cost = cost_tracker
    
    async def generate_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """生成合规报告"""
        
        # 收集数据
        stats = await self._get_statistics(start_date, end_date)
        decision_types = await self._get_decision_distribution(start_date, end_date)
        guardrail_blocks = await self._get_guardrail_blocks(start_date, end_date)
        high_risk = await self._get_high_risk_decisions(start_date, end_date)
        cost_report = await self.cost.get_usage_report("*", start_date, end_date)
        
        # 生成建议
        recommendations = self._generate_recommendations(stats, guardrail_blocks)
        
        # 渲染报告
        template = Template(self.REPORT_TEMPLATE)
        return template.render(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            system_version="1.0.0",
            stats=stats,
            decision_types=decision_types,
            guardrail_blocks=guardrail_blocks,
            high_risk_decisions=high_risk,
            cost=cost_report,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, stats: dict, blocks: list) -> list[str]:
        """根据数据生成建议"""
        recommendations = []
        
        if stats.get("avg_confidence", 1) < 0.7:
            recommendations.append(
                "平均置信度较低，建议检查Prompt质量或增加训练数据"
            )
        
        if stats.get("guardrail_blocks", 0) > 100:
            recommendations.append(
                "护栏拦截次数较多，建议分析拦截原因并优化用户引导"
            )
        
        return recommendations
```

---

## 5. RBAC权限控制

```python
from enum import Enum
from functools import wraps
from fastapi import HTTPException, Depends


class Permission(str, Enum):
    """权限枚举"""
    CHAT = "chat"                      # 基础对话
    RAG_QUERY = "rag:query"            # RAG查询
    RAG_UPLOAD = "rag:upload"          # 上传文档
    AGENT_EXECUTE = "agent:execute"    # 执行Agent
    AGENT_ADMIN = "agent:admin"        # Agent管理
    AUDIT_VIEW = "audit:view"          # 查看审计
    AUDIT_EXPORT = "audit:export"      # 导出审计
    BUDGET_VIEW = "budget:view"        # 查看预算
    BUDGET_MANAGE = "budget:manage"    # 管理预算


class Role(str, Enum):
    """角色枚举"""
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"
    AUDITOR = "auditor"


# 角色权限映射
ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.CHAT,
        Permission.RAG_QUERY
    ],
    Role.POWER_USER: [
        Permission.CHAT,
        Permission.RAG_QUERY,
        Permission.RAG_UPLOAD,
        Permission.AGENT_EXECUTE
    ],
    Role.ADMIN: [
        Permission.CHAT,
        Permission.RAG_QUERY,
        Permission.RAG_UPLOAD,
        Permission.AGENT_EXECUTE,
        Permission.AGENT_ADMIN,
        Permission.BUDGET_VIEW,
        Permission.BUDGET_MANAGE
    ],
    Role.AUDITOR: [
        Permission.AUDIT_VIEW,
        Permission.AUDIT_EXPORT,
        Permission.BUDGET_VIEW
    ]
}


def require_permission(permission: Permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"需要权限: {permission.value}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# 使用示例
@router.get("/audit/logs")
@require_permission(Permission.AUDIT_VIEW)
async def get_audit_logs(current_user: User = Depends(get_current_user)):
    """获取审计日志（需要审计查看权限）"""
    ...
```

---

## 6. 学习检查清单

- [ ] 理解AI治理的重要性和核心组件
- [ ] 能够设计和实现决策日志系统
- [ ] 能够实现成本追踪和预算告警
- [ ] 能够生成合规审计报告
- [ ] 理解RBAC权限控制模型

---

## 继续学习

📌 **相关教程**：
- [可观测性实战](./04_observability.md) - 监控与追踪
- [Guardrails护栏](./05_guardrails.md) - 安全验证
- [人机协作](./06_human_in_the_loop.md) - 审批流程

---

**完善的治理体系是企业AI系统合规运营的基础！📈**
