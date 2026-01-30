# 🐳 完整的 Docker + Nginx 部署方案

> **生产级部署：FastAPI + Nginx 反向代理**

---

## 📋 目录

- [Nginx 的作用](#nginx-的作用)
- [架构图](#架构图)
- [快速开始](#快速开始)
- [详细配置说明](#详细配置说明)
- [部署步骤](#部署步骤)
- [升级方案](#升级方案)
- [监控和日志](#监控和日志)

---

## 🌟 Nginx 的作用

### 为什么需要 Nginx？

在生产环境中，**不建议**直接暴露 FastAPI 应用，而是通过 Nginx 作为反向代理。

### Nginx 的核心功能

#### 1️⃣ **反向代理**
```
用户请求 → Nginx (80端口) → FastAPI (8000端口)
```

**好处**：
- ✅ 隐藏后端服务器细节
- ✅ 统一访问入口
- ✅ 方便切换后端服务

#### 2️⃣ **负载均衡**
```
           ┌→ FastAPI 实例1 (8001)
Nginx ─────┼→ FastAPI 实例2 (8002)
           └→ FastAPI 实例3 (8003)
```

**策略**：
- `round-robin`：轮询（默认）
- `least_conn`：最少连接
- `ip_hash`：IP 哈希

#### 3️⃣ **静态文件服务**
```
/static/  → Nginx 直接返回（快）
/api/     → 转发到 FastAPI（动态）
```

**性能提升**：
- 静态文件：Nginx 性能是 FastAPI 的 **10-100 倍**
- 减少 Python 进程负载

#### 4️⃣ **SSL/TLS 终止**
```
HTTPS (443) → Nginx (SSL处理) → HTTP (8000) FastAPI
```

**好处**：
- ✅ 统一管理证书
- ✅ FastAPI 无需处理 SSL
- ✅ 性能更好（Nginx 的 SSL 实现更优）

#### 5️⃣ **请求缓存**
```nginx
location /api/books/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;  # 缓存10分钟
}
```

#### 6️⃣ **限流和访问控制**
```nginx
# 限制每个IP每秒1个请求
limit_req_zone $binary_remote_addr zone=api:10m rate=1r/s;

location /api/ {
    limit_req zone=api burst=5;
}
```

#### 7️⃣ **压缩传输**
```nginx
gzip on;
gzip_types application/json;
```

**效果**：响应体积减少 **70-90%**

#### 8️⃣ **健康检查和故障转移**
```nginx
upstream backend {
    server api1:8000 max_fails=3 fail_timeout=30s;
    server api2:8000 backup;  # 备用服务器
}
```

---

## 🏛️ 架构图

### 完整架构

```
                    Internet
                       ↓
              ┌─────────────────┐
              │  Nginx (80/443) │
              │   反向代理       │
              └─────────────────┘
                       ↓
      ┌────────────────┼────────────────┐
      ↓                ↓                ↓
 ┌────────┐      ┌────────┐      ┌────────┐
 │API 容器1│      │API 容器2│      │API 容器3│
 │  :8000 │      │  :8000 │      │  :8000 │
 └────────┘      └────────┘      └────────┘
      ↓                ↓                ↓
 ┌──────────────────────────────────────┐
 │         SQLite / PostgreSQL          │
 │              数据库                  │
 └──────────────────────────────────────┘
```

### 请求流程

```
1. 用户访问 http://localhost
   ↓
2. Nginx 接收请求（80端口）
   ↓
3. Nginx 转发到 FastAPI（8000端口）
   ↓
4. FastAPI 处理业务逻辑
   ↓
5. FastAPI 返回响应给 Nginx
   ↓
6. Nginx 添加缓存/压缩
   ↓
7. Nginx 返回给用户
```

---

## 🚀 快速开始

### 前置要求

- ✅ Docker Desktop 已安装
- ✅ Docker Compose 可用

### 一键启动

```bash
# 进入项目目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 访问应用
# http://localhost  （通过 Nginx）
```

### 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

---

## 📁 项目结构

```
project1_structured_api/
├── main.py                      # FastAPI 应用
├── models.py                    # 数据模型
├── database.py                  # 数据库层
├── requirements.txt             # Python 依赖
├── Dockerfile                   # Docker 镜像
├── docker-compose.yml           # 开发环境配置
├── docker-compose.prod.yml      # 🆕 生产环境配置
├── nginx/                       # 🆕 Nginx 配置
│   ├── nginx.conf              # Nginx 主配置
│   ├── conf.d/
│   │   └── bookstore.conf      # 站点配置
│   └── logs/                    # 日志目录
├── data/                        # 数据库文件
│   └── bookstore.db
└── static/                      # 静态文件（可选）
```

---

## ⚙️ 详细配置说明

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  # FastAPI 应用
  api:
    build: .
    expose:
      - "8000"  # 只在内部网络暴露，不直接映射到宿主机
    networks:
      - app-network
  
  # Nginx 反向代理
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"  # 对外暴露 80 端口
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      api:
        condition: service_healthy
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

**关键点**：
- API 服务使用 `expose` 而非 `ports`（不直接暴露）
- Nginx 作为唯一对外入口
- 共享同一个网络 `app-network`

---

### nginx.conf（主配置）

```nginx
http {
    # Gzip 压缩
    gzip on;
    gzip_types application/json text/html;
    
    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

---

### bookstore.conf（站点配置）

```nginx
# 上游服务器
upstream bookstore_backend {
    least_conn;  # 最少连接负载均衡
    server api:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    # 代理所有请求到 FastAPI
    location / {
        proxy_pass http://bookstore_backend;
        
        # 重要：传递真实客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康检查
    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**关键配置**：

| 配置项 | 作用 |
|--------|------|
| `proxy_pass` | 将请求转发到后端 |
| `proxy_set_header Host` | 传递原始 Host 头 |
| `X-Real-IP` | 传递客户端真实 IP |
| `X-Forwarded-For` | 传递完整的代理链 |
| `X-Forwarded-Proto` | 传递协议（http/https） |

---

## 📝 部署步骤

### 步骤1：准备文件

确保以下文件存在：
```
✅ docker-compose.prod.yml
✅ nginx/nginx.conf
✅ nginx/conf.d/bookstore.conf
```

### 步骤2：创建必要的目录

```powershell
# 创建 Nginx 日志目录
mkdir nginx\logs

# 创建静态文件目录（可选）
mkdir static
```

### 步骤3：启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**参数说明**：
- `-f docker-compose.prod.yml`：指定配置文件
- `up`：启动服务
- `-d`：后台运行
- `--build`：重新构建镜像

### 步骤4：验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 输出示例：
# NAME              STATUS        PORTS
# bookstore-api     Up (healthy)  8000/tcp
# bookstore-nginx   Up (healthy)  0.0.0.0:80->80/tcp
```

### 步骤5：测试访问

```bash
# 方式1：浏览器访问
# http://localhost

# 方式2：命令行测试
curl http://localhost/api
# 输出：{"message": "API is running"}

# 方式3：查看 Nginx 健康检查
curl http://localhost/health
# 输出：healthy
```

### 步骤6：查看日志

```bash
# API 日志
docker-compose -f docker-compose.prod.yml logs api

# Nginx 日志
docker-compose -f docker-compose.prod.yml logs nginx

# 或直接查看文件
cat nginx/logs/access.log
cat nginx/logs/error.log
```

---

## 🔄 升级方案

### 方案1：添加多个 API 实例（负载均衡）

修改 `docker-compose.prod.yml`：

```yaml
services:
  api:
    deploy:
      replicas: 3  # 启动3个实例
```

修改 `nginx/conf.d/bookstore.conf`：

```nginx
upstream bookstore_backend {
    least_conn;
    server api:8000;
    # Docker Compose 会自动负载均衡到多个实例
}
```

启动：
```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

### 方案2：添加 PostgreSQL

在 `docker-compose.prod.yml` 中取消注释：

```yaml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: bookstore
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: bookstore

volumes:
  postgres-data:
```

更新 `main.py` 使用 PostgreSQL（需要安装 `sqlalchemy` 和 `psycopg2`）

---

### 方案3：添加 HTTPS 支持

1. 获取 SSL 证书（Let's Encrypt）
2. 修改 `bookstore.conf`：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 其他配置...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

3. 挂载证书：
```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro
```

---

## 📊 监控和日志

### 访问日志分析

```bash
# 查看访问日志
tail -f nginx/logs/access.log

# 统计请求次数
cat nginx/logs/access.log | wc -l

# 统计状态码
cat nginx/logs/access.log | grep "HTTP/1.1\" 200" | wc -l
```

### 性能监控

```bash
# 查看容器资源使用
docker stats bookstore-api bookstore-nginx

# 输出：
# CONTAINER       CPU %   MEM USAGE / LIMIT   NET I/O
# bookstore-api   0.5%    50MiB / 2GiB        1.2kB / 800B
# bookstore-nginx 0.1%    10MiB / 2GiB        800B / 1.2kB
```

### 健康检查

```bash
# 检查健康状态
docker inspect bookstore-api --format='{{.State.Health.Status}}'
# 输出：healthy

# 查看健康检查日志
docker inspect bookstore-api --format='{{json .State.Health}}' | jq
```

---

## 🔧 常见问题

### Q1: Nginx 无法访问 FastAPI

**错误**：`502 Bad Gateway`

**排查**：
```bash
# 检查 API 容器是否运行
docker ps | grep bookstore-api

# 检查网络连接
docker exec bookstore-nginx ping api

# 查看 Nginx 错误日志
cat nginx/logs/error.log
```

### Q2: 端口冲突

**错误**：`port is already allocated`

**解决**：
```bash
# 查找占用80端口的进程
netstat -ano | findstr :80

# 终止进程或使用其他端口
# 修改 docker-compose.prod.yml:
ports:
  - "8080:80"
```

### Q3: 日志文件权限问题

**解决**：
```bash
# 创建日志目录并设置权限
mkdir -p nginx/logs
chmod 777 nginx/logs
```

---

## 🎯 性能优化建议

### 1. Nginx缓存

```nginx
# 在 nginx.conf 中添加
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

# 在 location 中使用
location /api/books/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
}
```

### 2. 启用 HTTP/2

```nginx
listen 443 ssl http2;
```

### 3. 调整 Worker 数量

```dockerfile
# Dockerfile 中使用 Gunicorn
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

---

## 📈 对比总结

| 特性 | 无 Nginx | 有 Nginx |
|------|----------|----------|
| 性能 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 静态文件 | FastAPI处理 | Nginx处理（快10倍） |
| 负载均衡 | ❌ | ✅ |
| SSL | FastAPI处理 | Nginx处理（更优） |
| 限流 | 需自己实现 | ✅ Nginx内置 |
| 缓存 | 需自己实现 | ✅ Nginx内置 |
| 生产就绪 | ❌ | ✅ |

---

**🎉 恭喜！你已经掌握了完整的 Docker + Nginx 生产级部署方案！**
