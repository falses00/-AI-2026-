# ⚠️ 错误处理与降级策略

> **学习目标**：构建稳健的AI系统，优雅处理各种异常情况

---

## 1. AI系统常见错误类型

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI系统错误分类                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐       ┌─────────────────────┐         │
│  │    API层错误         │       │    模型层错误        │         │
│  │ • 网络超时           │       │ • 幻觉/不准确        │         │
│  │ • Rate Limit        │       │ • 拒绝回答          │         │
│  │ • Token超限         │       │ • 格式错误          │         │
│  │ • 认证失败           │       │ • 安全违规          │         │
│  └─────────────────────┘       └─────────────────────┘         │
│                                                                  │
│  ┌─────────────────────┐       ┌─────────────────────┐         │
│  │    检索层错误        │       │    业务层错误        │         │
│  │ • 无相关结果         │       │ • 输入验证失败       │         │
│  │ • 向量库连接失败     │       │ • 权限不足          │         │
│  │ • 文档解析失败       │       │ • 资源不存在        │         │
│  └─────────────────────┘       └─────────────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 分层错误处理架构

### 2.1 自定义异常类

```python
from enum import Enum
from typing import Optional

class ErrorSeverity(Enum):
    """错误严重级别"""
    LOW = "low"           # 可忽略，不影响功能
    MEDIUM = "medium"     # 需要降级处理
    HIGH = "high"         # 功能不可用
    CRITICAL = "critical" # 系统级故障

class AIServiceError(Exception):
    """AI服务基础异常"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.severity = severity
        self.user_message = user_message or "服务暂时不可用，请稍后重试"
        self.retry_after = retry_after

class LLMError(AIServiceError):
    """LLM调用错误"""
    pass

class RateLimitError(LLMError):
    """速率限制错误"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="API rate limit exceeded",
            error_code="RATE_LIMIT",
            severity=ErrorSeverity.MEDIUM,
            user_message="请求过于频繁，请稍后重试",
            retry_after=retry_after
        )

class TokenLimitError(LLMError):
    """Token超限错误"""
    def __init__(self):
        super().__init__(
            message="Token limit exceeded",
            error_code="TOKEN_LIMIT",
            severity=ErrorSeverity.MEDIUM,
            user_message="输入内容过长，请精简后重试"
        )

class RetrievalError(AIServiceError):
    """检索错误"""
    pass

class NoResultsError(RetrievalError):
    """无检索结果"""
    def __init__(self):
        super().__init__(
            message="No relevant documents found",
            error_code="NO_RESULTS",
            severity=ErrorSeverity.LOW,
            user_message="没有找到相关信息，换个关键词试试？"
        )
```

### 2.2 错误处理中间件

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(AIServiceError)
async def ai_service_error_handler(request: Request, exc: AIServiceError):
    """处理AI服务错误"""
    # 记录日志
    logger.error(
        f"AI Service Error: {exc.error_code} - {exc}",
        extra={
            "error_code": exc.error_code,
            "severity": exc.severity.value,
            "path": request.url.path
        }
    )
    
    # 根据严重级别决定响应
    status_code = {
        ErrorSeverity.LOW: 200,      # 返回成功但带提示
        ErrorSeverity.MEDIUM: 503,   # 服务暂时不可用
        ErrorSeverity.HIGH: 500,     # 服务器错误
        ErrorSeverity.CRITICAL: 500
    }.get(exc.severity, 500)
    
    response = {
        "success": False,
        "error": {
            "code": exc.error_code,
            "message": exc.user_message
        }
    }
    
    if exc.retry_after:
        response["retry_after"] = exc.retry_after
    
    return JSONResponse(status_code=status_code, content=response)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.critical(
        f"Unhandled exception: {exc}",
        extra={"traceback": traceback.format_exc()}
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误，我们正在处理"
            }
        }
    )
```

---

## 3. 智能重试策略

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import httpx

class RetryConfig:
    """重试配置"""
    MAX_ATTEMPTS = 3
    MIN_WAIT = 1  # 秒
    MAX_WAIT = 60  # 秒
    MULTIPLIER = 2

def smart_retry(
    max_attempts: int = RetryConfig.MAX_ATTEMPTS,
    retryable_errors: tuple = (httpx.TimeoutException, RateLimitError)
):
    """智能重试装饰器"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=RetryConfig.MULTIPLIER,
            min=RetryConfig.MIN_WAIT,
            max=RetryConfig.MAX_WAIT
        ),
        retry=retry_if_exception_type(retryable_errors),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying in {retry_state.next_action.sleep} seconds..."
        )
    )

# 使用
@smart_retry()
async def call_llm_with_retry(prompt: str) -> str:
    """带重试的LLM调用"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after=retry_after)
        raise
```

---

## 4. 降级策略实现

### 4.1 多模型降级

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    priority: int
    max_tokens: int
    cost_per_1k: float

class ModelFallbackChain:
    """模型降级链"""
    
    def __init__(self):
        self.models = [
            ModelConfig("gpt-4o", 1, 128000, 0.015),
            ModelConfig("gpt-4o-mini", 2, 128000, 0.003),
            ModelConfig("gpt-3.5-turbo", 3, 16385, 0.001),
        ]
    
    async def call_with_fallback(self, messages: list) -> str:
        """按优先级尝试调用模型"""
        last_error = None
        
        for model in sorted(self.models, key=lambda m: m.priority):
            try:
                response = await client.chat.completions.create(
                    model=model.name,
                    messages=messages
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Model {model.name} failed: {e}")
                last_error = e
                continue
        
        raise LLMError(
            message=f"All models failed: {last_error}",
            error_code="ALL_MODELS_FAILED",
            severity=ErrorSeverity.HIGH
        )

# 使用
fallback_chain = ModelFallbackChain()
result = await fallback_chain.call_with_fallback(messages)
```

### 4.2 功能降级

```python
class FeatureDegradation:
    """功能降级管理"""
    
    def __init__(self):
        self.degraded_features = set()
    
    def mark_degraded(self, feature: str):
        """标记功能为降级状态"""
        self.degraded_features.add(feature)
        logger.warning(f"Feature {feature} is now degraded")
    
    def is_degraded(self, feature: str) -> bool:
        """检查功能是否降级"""
        return feature in self.degraded_features
    
    def recover(self, feature: str):
        """恢复功能"""
        self.degraded_features.discard(feature)
        logger.info(f"Feature {feature} recovered")

degradation_manager = FeatureDegradation()

async def smart_search(query: str) -> dict:
    """智能搜索（带降级）"""
    # 尝试语义搜索
    if not degradation_manager.is_degraded("semantic_search"):
        try:
            results = await semantic_search(query)
            return {"type": "semantic", "results": results}
        except Exception as e:
            degradation_manager.mark_degraded("semantic_search")
    
    # 降级到关键词搜索
    if not degradation_manager.is_degraded("keyword_search"):
        try:
            results = await keyword_search(query)
            return {"type": "keyword", "results": results, "degraded": True}
        except Exception:
            degradation_manager.mark_degraded("keyword_search")
    
    # 最终降级：返回预设回复
    return {
        "type": "fallback",
        "results": [],
        "message": "搜索服务暂时不可用",
        "degraded": True
    }
```

---

## 5. 用户友好的错误提示

```python
ERROR_MESSAGES = {
    "RATE_LIMIT": {
        "title": "请求过于频繁",
        "description": "您的请求速度太快了，请稍等片刻再试。",
        "suggestion": "建议等待 {retry_after} 秒后重试",
        "icon": "⏳"
    },
    "TOKEN_LIMIT": {
        "title": "输入内容过长",
        "description": "您的问题或文档太长了，超出了处理能力。",
        "suggestion": "请尝试精简输入内容，或分段提问",
        "icon": "📝"
    },
    "NO_RESULTS": {
        "title": "没有找到相关信息",
        "description": "在知识库中没有找到与您问题相关的内容。",
        "suggestion": "请尝试换一种问法，或使用更具体的关键词",
        "icon": "🔍"
    },
    "MODEL_UNAVAILABLE": {
        "title": "AI服务暂时不可用",
        "description": "我们的AI助手正在休息，请稍后再试。",
        "suggestion": "通常几分钟后就会恢复",
        "icon": "🤖"
    }
}

def format_user_error(error_code: str, **kwargs) -> dict:
    """格式化用户友好的错误信息"""
    template = ERROR_MESSAGES.get(error_code, {
        "title": "出现了一些问题",
        "description": "服务暂时遇到问题，请稍后重试。",
        "suggestion": "如果问题持续，请联系客服",
        "icon": "⚠️"
    })
    
    return {
        "title": template["title"],
        "description": template["description"].format(**kwargs),
        "suggestion": template["suggestion"].format(**kwargs),
        "icon": template["icon"]
    }
```

---

## 6. 学习检查清单

- [ ] 理解AI系统常见错误类型
- [ ] 能够实现分层错误处理
- [ ] 会配置智能重试策略
- [ ] 能够实现多模型降级

---

## 继续学习

📌 **Week 10 学习顺序**：
1. ✅ AI产品设计原则
2. ✅ 对话交互设计
3. ✅ 错误处理策略（本教程）
