# 🚀 云平台部署指南

> **学习目标**：掌握企业级RAG系统的容器化和云平台部署

---

## 🎯 部署架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    生产环境部署架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  用户请求                                                        │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   云服务商负载均衡 (ALB/CLB/SLB)                          │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Kubernetes Cluster                             │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │   Ingress Controller (Nginx/Traefik)                │ │   │
│  │  └──────────────────────┬──────────────────────────────┘ │   │
│  │                         │                                 │   │
│  │    ┌────────────────────┼────────────────────┐           │   │
│  │    ▼                    ▼                    ▼           │   │
│  │  ┌────────┐         ┌────────┐         ┌────────┐       │   │
│  │  │ API    │         │ API    │         │ API    │       │   │
│  │  │ Pod 1  │         │ Pod 2  │         │ Pod 3  │       │   │
│  │  └───┬────┘         └───┬────┘         └───┬────┘       │   │
│  │      │                  │                  │             │   │
│  │      └──────────────────┼──────────────────┘             │   │
│  │                         │                                 │   │
│  │    ┌────────────────────┼────────────────────┐           │   │
│  │    ▼                    ▼                    ▼           │   │
│  │  ┌────────┐         ┌────────┐         ┌────────┐       │   │
│  │  │ Redis  │         │ Milvus │         │ PG DB  │       │   │
│  │  └────────┘         └────────┘         └────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Docker容器化

### 1. 应用Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 2. Docker Compose（开发环境）

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ragdb
      - REDIS_URL=redis://redis:6379
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on:
      - postgres
      - redis
      - milvus
    volumes:
      - ./app:/app/app
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ragdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  milvus:
    image: milvusdb/milvus:v2.3.0
    ports:
      - "19530:19530"
      - "9091:9091"
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
    depends_on:
      - etcd
      - minio

  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    command: etcd --listen-client-urls=http://0.0.0.0:2379 --advertise-client-urls=http://etcd:2379

  minio:
    image: minio/minio
    environment:
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    command: minio server /data
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## 📦 Kubernetes部署

### 1. 应用Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
  labels:
    app: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: api
        image: your-registry/rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: redis-url
        - name: LLM_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: llm-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 2. Service和Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: rag-api
spec:
  selector:
    app: rag-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rag-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.yourcompany.com
    secretName: rag-api-tls
  rules:
  - host: api.yourcompany.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rag-api
            port:
              number: 80
```

### 3. HPA自动扩缩

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🔧 CI/CD流水线

### GitHub Actions示例

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and Push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/rag-api:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
        images: |
          ${{ secrets.REGISTRY_URL }}/rag-api:${{ github.sha }}
```

---

## 📊 监控与日志

### 1. 健康检查端点

```python
# app/api/health.py
from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter(tags=["健康检查"])

@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/ready")
async def readiness_check(
    db = Depends(get_db),
    redis = Depends(get_redis),
    vector_store = Depends(get_vector_store)
):
    """就绪检查 - 检查所有依赖"""
    checks = {}
    
    # 数据库检查
    try:
        db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    # Redis检查
    try:
        redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
    
    # 向量库检查
    try:
        vector_store.heartbeat()
        checks["vector_store"] = "ok"
    except Exception as e:
        checks["vector_store"] = f"error: {str(e)}"
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks
    }
```

### 2. Prometheus指标

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# 定义指标
REQUEST_COUNT = Counter(
    'rag_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'rag_request_latency_seconds',
    'Request latency',
    ['method', 'endpoint']
)

RAG_QUERY_LATENCY = Histogram(
    'rag_query_latency_seconds',
    'RAG query latency',
    ['stage']  # retrieve, rerank, generate
)

async def metrics_middleware(request: Request, call_next):
    """指标中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    latency = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(latency)
    
    return response

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## 🔐 生产环境安全

### 环境变量管理

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用
    app_name: str = "Enterprise RAG"
    debug: bool = False
    environment: str = "production"
    
    # 安全
    secret_key: str
    allowed_origins: list[str] = ["https://yourapp.com"]
    
    # 数据库
    database_url: str
    
    # Redis
    redis_url: str
    
    # 向量库
    milvus_host: str = "milvus"
    milvus_port: int = 19530
    
    # LLM
    llm_api_key: str
    llm_base_url: str = "https://api.deepseek.com/v1"
    
    # 限流
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 📊 学习检查清单

- [ ] 能够编写生产级Dockerfile
- [ ] 理解Docker Compose多服务编排
- [ ] 掌握Kubernetes基本部署
- [ ] 了解CI/CD流水线设计
- [ ] 知道如何添加健康检查和监控

---

## 🎯 Week 7完成！

恭喜完成Week 7企业级RAG项目全部内容！

继续前往：
👉 [Week 8: 多模态AI](../week8/README.md)
