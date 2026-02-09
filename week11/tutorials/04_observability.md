# 📊 可观测性实战：LangFuse + Prometheus

> **学习目标**：掌握企业级AI系统的可观测性实现

---

## 1. 为什么需要可观测性？

在生产环境中运行AI系统，你需要回答：

- ❓ 这次请求为什么响应这么慢？
- ❓ 模型返回的质量如何？
- ❓ 每月花了多少API费用？
- ❓ 哪些请求导致了错误？

**可观测性 = 追踪 + 指标 + 日志**

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI系统可观测性架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐    │
│   │   追踪         │   │   指标         │   │   日志         │    │
│   │   (Traces)     │   │   (Metrics)   │   │   (Logs)       │    │
│   ├───────────────┤   ├───────────────┤   ├───────────────┤    │
│   │ • LangFuse    │   │ • Prometheus  │   │ • structlog   │    │
│   │ • LangSmith   │   │ • Grafana     │   │ • ELK Stack   │    │
│   │ • Arize       │   │               │   │               │    │
│   └───────────────┘   └───────────────┘   └───────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. LangFuse：LLM全链路追踪

### 2.1 安装和配置

```bash
pip install langfuse openai
```

```python
# 环境变量配置
# LANGFUSE_PUBLIC_KEY=pk-lf-xxx
# LANGFUSE_SECRET_KEY=sk-lf-xxx
# LANGFUSE_HOST=https://cloud.langfuse.com (或自托管地址)
```

### 2.2 基础使用：装饰器追踪

```python
from langfuse.decorators import observe, langfuse_context
from openai import OpenAI

client = OpenAI()

@observe()
def chat(user_message: str) -> str:
    """带追踪的对话函数"""
    
    # 添加自定义元数据
    langfuse_context.update_current_trace(
        user_id="user_123",
        session_id="session_456",
        tags=["production", "chat"]
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

# 使用
result = chat("什么是RAG？")
```

### 2.3 多步骤追踪：Agent工作流

```python
from langfuse.decorators import observe
from langfuse import Langfuse

langfuse = Langfuse()

@observe(name="multi_step_agent")
async def agent_workflow(task: str):
    """多步骤Agent工作流追踪"""
    
    # Step 1: 规划
    with langfuse_context.observe_as("planning") as span:
        plan = await plan_task(task)
        span.update(output=plan)
    
    # Step 2: 执行
    with langfuse_context.observe_as("execution") as span:
        result = await execute_plan(plan)
        span.update(
            output=result,
            metadata={"steps": len(plan)}
        )
    
    # Step 3: 验证
    with langfuse_context.observe_as("verification") as span:
        verified = await verify_result(result)
        span.update(
            output=verified,
            level="WARNING" if not verified["passed"] else "INFO"
        )
    
    # 记录评分
    langfuse_context.score_current_trace(
        name="quality",
        value=verified["score"],
        comment="自动质量评分"
    )
    
    return verified

async def plan_task(task: str) -> list:
    """规划任务"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"分解任务: {task}"}]
    )
    return parse_plan(response.choices[0].message.content)

async def execute_plan(plan: list) -> dict:
    """执行计划"""
    results = []
    for step in plan:
        result = await execute_step(step)
        results.append(result)
    return {"steps": results}

async def verify_result(result: dict) -> dict:
    """验证结果"""
    return {"passed": True, "score": 0.9}
```

### 2.4 RAG追踪

```python
@observe()
async def rag_query(question: str) -> str:
    """RAG查询追踪"""
    
    # 追踪检索步骤
    with langfuse_context.observe_as("retrieval", type="retriever") as span:
        docs = await vector_store.similarity_search(question, k=5)
        span.update(
            input=question,
            output=[doc.page_content[:100] for doc in docs],
            metadata={"num_docs": len(docs)}
        )
    
    # 追踪生成步骤
    with langfuse_context.observe_as("generation", type="llm") as span:
        context = "\n".join([doc.page_content for doc in docs])
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"根据以下内容回答:\n{context}"},
                {"role": "user", "content": question}
            ]
        )
        
        answer = response.choices[0].message.content
        span.update(
            input={"question": question, "context_length": len(context)},
            output=answer,
            usage={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens
            }
        )
    
    return answer
```

---

## 3. Prometheus：指标监控

### 3.1 定义指标

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 计数器：累积值
llm_requests_total = Counter(
    'llm_requests_total',
    'LLM请求总数',
    ['model', 'endpoint', 'status']
)

# 直方图：分布（如延迟）
llm_latency_seconds = Histogram(
    'llm_latency_seconds',
    'LLM响应延迟（秒）',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# 计数器：Token用量
llm_tokens_total = Counter(
    'llm_tokens_total',
    'Token使用量',
    ['model', 'type']  # type: input/output
)

# 仪表：当前值
active_sessions = Gauge(
    'active_sessions',
    '当前活跃会话数'
)
```

### 3.2 在代码中记录指标

```python
import time

async def tracked_chat(message: str, model: str = "gpt-4o-mini"):
    """带指标追踪的对话"""
    
    start_time = time.time()
    active_sessions.inc()
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}]
        )
        
        # 记录成功
        llm_requests_total.labels(
            model=model,
            endpoint="chat",
            status="success"
        ).inc()
        
        # 记录Token
        llm_tokens_total.labels(model=model, type="input").inc(
            response.usage.prompt_tokens
        )
        llm_tokens_total.labels(model=model, type="output").inc(
            response.usage.completion_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        llm_requests_total.labels(
            model=model,
            endpoint="chat",
            status="error"
        ).inc()
        raise
        
    finally:
        # 记录延迟
        duration = time.time() - start_time
        llm_latency_seconds.labels(model=model).observe(duration)
        active_sessions.dec()
```

### 3.3 FastAPI集成

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()

# 挂载Prometheus指标端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/chat")
async def chat_endpoint(message: str):
    result = await tracked_chat(message)
    return {"response": result}
```

### 3.4 Prometheus配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-assistant'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

---

## 4. Grafana仪表板

### 4.1 核心面板

**请求速率**：
```promql
rate(llm_requests_total[5m])
```

**平均延迟**：
```promql
histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m]))
```

**Token使用**：
```promql
sum(rate(llm_tokens_total[1h])) by (model, type)
```

**错误率**：
```promql
rate(llm_requests_total{status="error"}[5m]) / rate(llm_requests_total[5m]) * 100
```

### 4.2 告警规则

```yaml
# alerts.yml
groups:
  - name: ai-alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM响应延迟过高"
          
      - alert: HighErrorRate
        expr: rate(llm_requests_total{status="error"}[5m]) / rate(llm_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "LLM错误率超过5%"
```

---

## 5. 成本追踪

```python
# 各模型定价 (美元/1K tokens)
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},
}

llm_cost_dollars = Counter(
    'llm_cost_dollars',
    'LLM调用成本（美元）',
    ['model']
)

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """计算API调用成本"""
    pricing = MODEL_PRICING.get(model, {"input": 0.001, "output": 0.002})
    cost = (
        input_tokens * pricing["input"] / 1000 +
        output_tokens * pricing["output"] / 1000
    )
    llm_cost_dollars.labels(model=model).inc(cost)
    return cost
```

---

## 6. 学习检查清单

- [ ] 能够配置LangFuse追踪
- [ ] 会使用装饰器追踪Agent工作流
- [ ] 理解Prometheus指标类型（Counter/Histogram/Gauge）
- [ ] 能够创建Grafana仪表板
- [ ] 会设置告警规则
- [ ] 能够追踪Token成本

---

## 继续学习

📌 **推荐顺序**：
1. ✅ 可观测性实战（本教程）
2. 🔜 [Guardrails安全护栏](./05_guardrails.md)

---

**没有可观测性的AI系统是飞行盲区！👁️**
