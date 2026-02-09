# 👤 Human-in-the-Loop：人机协作模式

> **学习目标**：实现AI系统中的人工审批和干预机制

---

## 1. 什么是Human-in-the-Loop (HITL)?

HITL是在AI决策过程中引入人工审核的机制，用于：

- 🎯 **高风险决策**：涉及资金、合同等敏感操作
- 🎯 **低置信度**：模型不确定时请求人工确认
- 🎯 **合规要求**：法规要求人工审批的场景
- 🎯 **质量保障**：重要输出需要人工验证

```
┌─────────────────────────────────────────────────────────────────┐
│                    Human-in-the-Loop 工作流                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   用户请求 ──▶ Agent处理 ──▶ 风险评估 ──┬──▶ 自动执行           │
│                                         │                        │
│                                         └──▶ [需要审批]          │
│                                              │                   │
│                                              ▼                   │
│                                         人工审批队列              │
│                                              │                   │
│                                    ┌─────────┴─────────┐        │
│                                    ▼                   ▼        │
│                                  批准              拒绝          │
│                                    │                   │        │
│                                    ▼                   ▼        │
│                                 执行操作           通知用户      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 何时需要人工介入

### 2.1 触发条件

| 类型 | 条件 | 示例 |
|------|------|------|
| **敏感操作** | 预定义的高风险操作 | 发送邮件、付款、删除数据 |
| **低置信度** | 模型置信度 < 阈值 | 意图分类不确定 |
| **金额阈值** | 涉及金额 > 限额 | 订单金额 > 1000元 |
| **用户偏好** | 用户要求确认 | "发送前让我确认" |
| **异常检测** | 请求模式异常 | 短时间大量请求 |

### 2.2 置信度评估

```python
from pydantic import BaseModel
from typing import Optional

class ConfidenceEvaluation(BaseModel):
    """置信度评估结果"""
    score: float           # 0-1
    reason: str
    needs_human: bool
    
class ConfidenceChecker:
    """置信度检查器"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
    
    def evaluate(self, response: dict) -> ConfidenceEvaluation:
        """评估响应置信度"""
        
        # 方法1：基于模型的logprobs
        if "logprobs" in response:
            score = self._calculate_from_logprobs(response["logprobs"])
        
        # 方法2：基于关键词
        elif "content" in response:
            score = self._calculate_from_content(response["content"])
        
        else:
            score = 0.5
        
        return ConfidenceEvaluation(
            score=score,
            reason=self._get_reason(score),
            needs_human=score < self.threshold
        )
    
    def _calculate_from_content(self, content: str) -> float:
        """从内容推断置信度"""
        uncertainty_markers = [
            "可能", "也许", "不确定", "我认为", "大概",
            "似乎", "好像", "应该是"
        ]
        
        marker_count = sum(1 for m in uncertainty_markers if m in content)
        
        if marker_count >= 3:
            return 0.3
        elif marker_count >= 2:
            return 0.5
        elif marker_count >= 1:
            return 0.7
        return 0.9
    
    def _get_reason(self, score: float) -> str:
        if score < 0.5:
            return "模型表达高度不确定"
        elif score < 0.7:
            return "存在不确定性标记"
        return "置信度正常"
```

---

## 3. 审批流程实现

### 3.1 审批请求模型

```python
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel
import uuid

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ApprovalRequest(BaseModel):
    """审批请求"""
    id: str
    created_at: datetime
    expires_at: datetime
    
    action_type: str          # 操作类型
    action_params: dict       # 操作参数
    
    context: dict             # 上下文信息
    risk_level: str           # low, medium, high
    reason: str               # 需要审批的原因
    
    user_id: str              # 触发用户
    assignee: Optional[str]   # 审批人
    
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_at: Optional[datetime] = None
    decision_by: Optional[str] = None
    decision_comment: Optional[str] = None

class ApprovalResponse(BaseModel):
    """审批响应"""
    approved: bool
    comment: Optional[str] = None
    modified_params: Optional[dict] = None  # 审批人可修改参数
```

### 3.2 审批队列服务

```python
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta

class ApprovalQueue:
    """审批队列服务"""
    
    def __init__(self, default_timeout: int = 3600):
        self.pending: Dict[str, ApprovalRequest] = {}
        self.default_timeout = default_timeout
        self.waiting_tasks: Dict[str, asyncio.Event] = {}
    
    async def submit(
        self,
        action_type: str,
        action_params: dict,
        context: dict,
        risk_level: str,
        reason: str,
        user_id: str,
        timeout: Optional[int] = None
    ) -> ApprovalRequest:
        """提交审批请求"""
        
        timeout = timeout or self.default_timeout
        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=timeout),
            action_type=action_type,
            action_params=action_params,
            context=context,
            risk_level=risk_level,
            reason=reason,
            user_id=user_id
        )
        
        self.pending[request.id] = request
        self.waiting_tasks[request.id] = asyncio.Event()
        
        # 发送通知给审批人
        await self._notify_approvers(request)
        
        return request
    
    async def wait_for_decision(
        self,
        request_id: str,
        timeout: Optional[int] = None
    ) -> ApprovalRequest:
        """等待审批决定"""
        
        if request_id not in self.pending:
            raise ValueError(f"审批请求不存在: {request_id}")
        
        event = self.waiting_tasks[request_id]
        timeout = timeout or self.default_timeout
        
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            # 超时自动过期
            self.pending[request_id].status = ApprovalStatus.EXPIRED
        
        return self.pending[request_id]
    
    async def approve(
        self,
        request_id: str,
        approver_id: str,
        comment: Optional[str] = None,
        modified_params: Optional[dict] = None
    ):
        """批准请求"""
        
        if request_id not in self.pending:
            raise ValueError(f"审批请求不存在: {request_id}")
        
        request = self.pending[request_id]
        request.status = ApprovalStatus.APPROVED
        request.decision_at = datetime.now()
        request.decision_by = approver_id
        request.decision_comment = comment
        
        if modified_params:
            request.action_params.update(modified_params)
        
        # 唤醒等待任务
        if request_id in self.waiting_tasks:
            self.waiting_tasks[request_id].set()
    
    async def reject(
        self,
        request_id: str,
        approver_id: str,
        comment: str
    ):
        """拒绝请求"""
        
        request = self.pending[request_id]
        request.status = ApprovalStatus.REJECTED
        request.decision_at = datetime.now()
        request.decision_by = approver_id
        request.decision_comment = comment
        
        if request_id in self.waiting_tasks:
            self.waiting_tasks[request_id].set()
    
    async def _notify_approvers(self, request: ApprovalRequest):
        """通知审批人"""
        # 实现通知逻辑：邮件、Slack、微信等
        print(f"[通知] 新审批请求: {request.id} - {request.action_type}")
```

### 3.3 FastAPI审批API

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List

app = FastAPI()
approval_queue = ApprovalQueue()

@app.get("/approvals/pending")
async def list_pending_approvals() -> List[ApprovalRequest]:
    """获取待审批列表"""
    return [r for r in approval_queue.pending.values() 
            if r.status == ApprovalStatus.PENDING]

@app.post("/approvals/{request_id}/approve")
async def approve_request(
    request_id: str,
    response: ApprovalResponse,
    approver_id: str = "admin"  # 实际应从JWT获取
):
    """批准请求"""
    try:
        await approval_queue.approve(
            request_id=request_id,
            approver_id=approver_id,
            comment=response.comment,
            modified_params=response.modified_params
        )
        return {"status": "approved"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/approvals/{request_id}/reject")
async def reject_request(
    request_id: str,
    comment: str,
    approver_id: str = "admin"
):
    """拒绝请求"""
    try:
        await approval_queue.reject(
            request_id=request_id,
            approver_id=approver_id,
            comment=comment
        )
        return {"status": "rejected"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 4. 在Agent中集成HITL

### 4.1 带审批的Agent执行器

```python
class HumanInTheLoopAgent:
    """支持人机协作的Agent"""
    
    # 需要审批的操作
    APPROVAL_REQUIRED_ACTIONS = {
        "send_email": "medium",
        "create_order": "medium",
        "modify_user_data": "high",
        "execute_payment": "high",
        "delete_record": "high",
    }
    
    def __init__(self, approval_queue: ApprovalQueue):
        self.approval_queue = approval_queue
        self.confidence_checker = ConfidenceChecker()
    
    async def execute_action(
        self,
        action: str,
        params: dict,
        context: dict,
        user_id: str
    ) -> dict:
        """执行操作（可能需要人工审批）"""
        
        needs_approval = False
        risk_level = "low"
        reason = ""
        
        # 1. 检查是否在需审批列表中
        if action in self.APPROVAL_REQUIRED_ACTIONS:
            needs_approval = True
            risk_level = self.APPROVAL_REQUIRED_ACTIONS[action]
            reason = f"操作 '{action}' 需要人工确认"
        
        # 2. 检查金额阈值
        if "amount" in params and params["amount"] > 1000:
            needs_approval = True
            risk_level = "high"
            reason = f"涉及金额 {params['amount']} 超过阈值"
        
        # 3. 如果需要审批
        if needs_approval:
            request = await self.approval_queue.submit(
                action_type=action,
                action_params=params,
                context=context,
                risk_level=risk_level,
                reason=reason,
                user_id=user_id
            )
            
            # 等待审批结果
            result = await self.approval_queue.wait_for_decision(
                request.id,
                timeout=3600
            )
            
            if result.status == ApprovalStatus.APPROVED:
                # 使用可能被审批人修改的参数
                return await self._perform_action(action, result.action_params)
            elif result.status == ApprovalStatus.REJECTED:
                return {
                    "success": False,
                    "error": f"审批被拒绝: {result.decision_comment}"
                }
            else:
                return {
                    "success": False,
                    "error": "审批超时"
                }
        
        # 4. 无需审批，直接执行
        return await self._perform_action(action, params)
    
    async def _perform_action(self, action: str, params: dict) -> dict:
        """实际执行操作"""
        # 实现具体操作逻辑
        return {"success": True, "result": f"执行 {action} 完成"}
```

### 4.2 在LangGraph中集成

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class AgentState(TypedDict):
    messages: list
    pending_action: Optional[dict]
    approval_status: Optional[str]
    final_result: Optional[str]

def build_hitl_workflow():
    """构建带人机协作的工作流"""
    
    workflow = StateGraph(AgentState)
    
    # 节点
    workflow.add_node("agent", agent_node)
    workflow.add_node("check_approval", check_approval_node)
    workflow.add_node("wait_human", wait_human_node)
    workflow.add_node("execute", execute_node)
    
    # 入口
    workflow.set_entry_point("agent")
    
    # 边
    workflow.add_edge("agent", "check_approval")
    
    workflow.add_conditional_edges(
        "check_approval",
        lambda s: "wait" if s["pending_action"] else "execute",
        {"wait": "wait_human", "execute": "execute"}
    )
    
    workflow.add_conditional_edges(
        "wait_human",
        lambda s: "execute" if s["approval_status"] == "approved" else "end",
        {"execute": "execute", "end": END}
    )
    
    workflow.add_edge("execute", END)
    
    # 使用checkpoint支持中断和恢复
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["wait_human"])

async def wait_human_node(state: AgentState):
    """人工等待节点 - 工作流在此中断"""
    # LangGraph会在这里暂停，等待人工输入
    return state
```

---

## 5. 回退策略

```python
class FallbackStrategy:
    """回退策略"""
    
    async def handle_rejection(
        self,
        action: str,
        rejection_reason: str,
        context: dict
    ) -> dict:
        """处理审批拒绝"""
        
        # 1. 记录日志
        await self._log_rejection(action, rejection_reason, context)
        
        # 2. 生成友好的用户消息
        user_message = self._generate_user_message(rejection_reason)
        
        # 3. 建议替代方案
        alternatives = await self._suggest_alternatives(action, context)
        
        return {
            "message": user_message,
            "alternatives": alternatives
        }
    
    async def handle_timeout(
        self,
        action: str,
        context: dict
    ) -> dict:
        """处理审批超时"""
        
        # 选项1：自动取消
        # 选项2：使用默认安全操作
        # 选项3：升级到更高级别审批人
        
        return {
            "message": "审批超时，操作已取消",
            "action": "cancelled"
        }
    
    async def _suggest_alternatives(self, action: str, context: dict) -> list:
        """建议替代方案"""
        alternatives = {
            "send_email": ["保存草稿", "发送到自己邮箱预览"],
            "execute_payment": ["拆分为小额支付", "申请更高额度"],
        }
        return alternatives.get(action, [])
```

---

## 6. 学习检查清单

- [ ] 理解HITL的应用场景
- [ ] 能够实现置信度评估
- [ ] 会设计审批工作流
- [ ] 能够实现审批队列
- [ ] 了解LangGraph中断/恢复机制
- [ ] 能够实现回退策略

---

## 继续学习

📌 **Week 11 学习顺序**：
1. ✅ 高级Agent架构
2. ✅ Agent记忆系统
3. ✅ 多Agent协作
4. ✅ 可观测性实战
5. ✅ Guardrails安全护栏
6. ✅ Human-in-the-Loop（本教程）

---

**关键决策需要人类参与！🤝**
