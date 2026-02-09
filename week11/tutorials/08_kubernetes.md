# ☸️ Kubernetes生产部署

> **学习目标**：掌握AI应用的K8s生产部署，实现高可用、自动伸缩和蓝绿发布

---

## 1. 为什么用Kubernetes？

| 能力 | Docker Compose | Kubernetes |
|-----|---------------|------------|
| 高可用 | ❌ 单节点 | ✅ 多节点冗余 |
| 自动伸缩 | ❌ 手动 | ✅ HPA自动 |
| 滚动更新 | ⚠️ 基础 | ✅ 零停机 |
| 服务发现 | ⚠️ 基础 | ✅ 内置DNS |
| 密钥管理 | ❌ 环境变量 | ✅ Secrets |
| 资源限制 | ⚠️ 基础 | ✅ 精细控制 |

---

## 2. 项目结构

```
k8s/
├── namespace.yaml       # 命名空间
├── configmap.yaml       # 配置
├── secrets.yaml         # 密钥
├── deployment.yaml      # 部署配置
├── service.yaml         # 服务暴露
├── hpa.yaml             # 自动伸缩
├── ingress.yaml         # 入口路由
└── monitoring/
    ├── prometheus.yaml
    └── grafana.yaml
```

---

## 3. 核心配置文件

### 3.1 命名空间 (`namespace.yaml`)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-assistant
  labels:
    app: ai-assistant
    environment: production
```

### 3.2 配置管理 (`configmap.yaml`)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-assistant-config
  namespace: ai-assistant
data:
  # 应用配置
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://your-domain.com"
  
  # 模型配置
  DEFAULT_MODEL: "deepseek-chat"
  MAX_TOKENS: "4096"
  
  # RAG配置
  VECTOR_DB_HOST: "milvus-service"
  VECTOR_DB_PORT: "19530"
  CHUNK_SIZE: "512"
  
  # 可观测性
  LANGFUSE_HOST: "https://langfuse.your-domain.com"
  PROMETHEUS_ENABLED: "true"
```

### 3.3 密钥管理 (`secrets.yaml`)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-assistant-secrets
  namespace: ai-assistant
type: Opaque
stringData:
  # API密钥 (实际使用时应用base64编码)
  OPENAI_API_KEY: "sk-xxx"
  DEEPSEEK_API_KEY: "sk-xxx"
  
  # 数据库
  DATABASE_URL: "postgresql://user:pass@postgres-service:5432/aidb"
  REDIS_URL: "redis://redis-service:6379/0"
  
  # LangFuse
  LANGFUSE_PUBLIC_KEY: "pk-xxx"
  LANGFUSE_SECRET_KEY: "sk-xxx"
```

### 3.4 部署配置 (`deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
  namespace: ai-assistant
  labels:
    app: ai-assistant
spec:
  replicas: 3  # 生产环境建议3个副本
  selector:
    matchLabels:
      app: ai-assistant
  
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 滚动更新时最多多1个Pod
      maxUnavailable: 0  # 更新时不允许不可用
  
  template:
    metadata:
      labels:
        app: ai-assistant
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: api
        image: your-registry/ai-assistant:v1.0.0
        imagePullPolicy: Always
        
        ports:
        - containerPort: 8000
          name: http
        
        # 环境变量
        envFrom:
        - configMapRef:
            name: ai-assistant-config
        - secretRef:
            name: ai-assistant-secrets
        
        # 资源限制
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        
        # 健康检查
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 3
        
        # 启动检查（给AI模型加载时间）
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          failureThreshold: 30  # 最多等5分钟
      
      # 优雅终止
      terminationGracePeriodSeconds: 60
```

### 3.5 服务暴露 (`service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-assistant-service
  namespace: ai-assistant
spec:
  selector:
    app: ai-assistant
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

### 3.6 自动伸缩 (`hpa.yaml`)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-assistant-hpa
  namespace: ai-assistant
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-assistant
  
  minReplicas: 3
  maxReplicas: 10
  
  metrics:
  # CPU使用率
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  # 内存使用率
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  
  # 自定义指标：每秒请求数
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 缩容等待5分钟
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # 立即扩容
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### 3.7 入口路由 (`ingress.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-assistant-ingress
  namespace: ai-assistant
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: ai-assistant-tls
  
  rules:
  - host: api.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-assistant-service
            port:
              number: 80
```

---

## 4. 蓝绿部署

### 4.1 蓝绿切换脚本

```bash
#!/bin/bash
# blue-green-deploy.sh

NEW_VERSION=$1
CURRENT_COLOR=$(kubectl get service ai-assistant-service -n ai-assistant -o jsonpath='{.spec.selector.color}')

if [ "$CURRENT_COLOR" = "blue" ]; then
    NEW_COLOR="green"
else
    NEW_COLOR="blue"
fi

echo "当前: $CURRENT_COLOR -> 新版本: $NEW_COLOR"

# 1. 部署新版本到新颜色
kubectl apply -f deployment-$NEW_COLOR.yaml

# 2. 等待新版本就绪
kubectl rollout status deployment/ai-assistant-$NEW_COLOR -n ai-assistant

# 3. 运行健康检查
./health-check.sh $NEW_COLOR
if [ $? -ne 0 ]; then
    echo "健康检查失败，中止部署"
    exit 1
fi

# 4. 切换流量
kubectl patch service ai-assistant-service -n ai-assistant \
    -p "{\"spec\":{\"selector\":{\"color\":\"$NEW_COLOR\"}}}"

echo "流量已切换到 $NEW_COLOR"

# 5. 保留旧版本一段时间（用于回滚）
echo "旧版本保留10分钟后删除..."
sleep 600
kubectl delete deployment ai-assistant-$CURRENT_COLOR -n ai-assistant
```

---

## 5. 健康检查端点

```python
# app/api/health.py
from fastapi import APIRouter, Response
from datetime import datetime

router = APIRouter()

startup_time = datetime.now()
is_ready = False


@router.get("/health")
async def health_check():
    """存活检查 - 进程是否运行"""
    return {
        "status": "healthy",
        "uptime_seconds": (datetime.now() - startup_time).total_seconds()
    }


@router.get("/ready")
async def readiness_check(response: Response):
    """就绪检查 - 是否可以接收流量"""
    global is_ready
    
    if not is_ready:
        # 检查依赖服务
        checks = {
            "database": await check_database(),
            "redis": await check_redis(),
            "vector_db": await check_vector_db(),
            "llm_api": await check_llm_api()
        }
        
        all_ready = all(checks.values())
        
        if not all_ready:
            response.status_code = 503
            return {"status": "not_ready", "checks": checks}
        
        is_ready = True
    
    return {"status": "ready"}


async def check_database() -> bool:
    try:
        # 执行简单查询
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_llm_api() -> bool:
    try:
        # 发送简单请求验证API密钥
        response = await llm_client.models.list()
        return True
    except Exception:
        return False
```

---

## 6. 部署流程

```bash
# 1. 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 2. 配置密钥（生产环境使用Vault或SOPS）
kubectl apply -f k8s/secrets.yaml

# 3. 配置ConfigMap
kubectl apply -f k8s/configmap.yaml

# 4. 部署应用
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 5. 配置自动伸缩
kubectl apply -f k8s/hpa.yaml

# 6. 配置入口
kubectl apply -f k8s/ingress.yaml

# 7. 验证部署
kubectl get pods -n ai-assistant
kubectl get svc -n ai-assistant
kubectl get ingress -n ai-assistant

# 8. 查看日志
kubectl logs -f deployment/ai-assistant -n ai-assistant
```

---

## 7. 监控集成

```yaml
# monitoring/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-assistant
  namespace: ai-assistant
spec:
  selector:
    matchLabels:
      app: ai-assistant
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
```

---

## 8. 学习检查清单

- [ ] 理解K8s核心概念（Pod、Deployment、Service）
- [ ] 能够编写Deployment配置
- [ ] 会配置HPA自动伸缩
- [ ] 理解蓝绿部署流程
- [ ] 能够配置健康检查和就绪检查

---

## 继续学习

📌 **相关教程**：
- [可观测性实战](./04_observability.md) - Prometheus集成
- [治理审计](./07_governance.md) - 成本和合规

---

**K8s让你的AI应用真正达到生产级标准！☸️**
