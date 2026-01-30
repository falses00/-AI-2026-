# 🐳 图书管理系统 - Docker部署指南

> **完整的前后端一体化项目，支持Docker容器化部署**

---

## 📁 项目结构

```
project1_structured_api/
├── main.py              # FastAPI应用（包含前端）
├── models.py            # Pydantic数据模型
├── database.py          # SQLite数据库层
├── requirements.txt     # Python依赖
├── Dockerfile           # Docker镜像配置
├── docker-compose.yml   # Docker Compose配置
├── data/                # 数据库文件目录（自动创建）
│   └── bookstore.db     # SQLite数据库
└── README.md            # 本文档
```

---

## 🎯 项目特点

✅ **完整的全栈应用**
- 前端：现代化的HTML5界面（嵌入在FastAPI中）
- 后端：FastAPI RESTful API
- 数据库：SQLite（轻量级，适合学习）

✅ **Docker容器化**
- 一键构建镜像
- 数据持久化（挂载到本地）
- 生产环境就绪

✅ **功能完善**
- 图书CRUD操作
- 分页查询
- 表单验证
- 响应式设计

---

## 🚀 快速开始

### 方式一：本地运行（开发模式）

#### 1. 安装依赖

```bash
# 进入项目目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 安装依赖（使用你的Python环境）
pip install -r requirements.txt
```

#### 2. 运行应用

```bash
# 方式1：使用uvicorn直接运行
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 方式2：直接运行main.py
python main.py
```

#### 3. 访问应用

- **前端界面**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **ReDoc文档**：http://localhost:8000/redoc

---

### 方式二：Docker部署（推荐）

#### 前置要求

- 安装Docker Desktop（Windows）
- Docker Desktop处于运行状态

#### 步骤1：构建Docker镜像

```powershell
# 进入项目目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 构建镜像
docker build -t bookstore-api .
```

#### 步骤2：运行容器

```powershell
# 使用docker run运行（手动）
docker run -d `
  --name bookstore `
  -p 8000:8000 `
  -v "${PWD}/data:/app/data" `
  bookstore-api

# 查看容器日志
docker logs -f bookstore

# 停止容器
docker stop bookstore

# 删除容器
docker rm bookstore
```

#### 步骤3：使用Docker Compose（更简单）

```powershell
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

---

## 📊 数据持久化说明

### 数据存储位置

```
项目目录/data/bookstore.db
```

Docker容器通过**卷挂载（Volume Mount）**将数据库文件映射到本地：

```yaml
volumes:
  - ./data:/app/data  # 本地data目录 → 容器/app/data目录
```

**优点**：
- ✅ 容器删除后数据不会丢失
- ✅ 可以直接在本地查看和备份数据库文件
- ✅ 多次重启容器保持数据一致性

### 查看数据库

```bash
# 安装SQLite工具
# Windows: 从 https://www.sqlite.org/download.html 下载

# 查看数据库
sqlite3 data/bookstore.db

# 查询所有图书
sqlite> SELECT * FROM books;

# 退出
sqlite> .quit
```

---

## 🛠️ Docker命令速查

### 镜像管理

```bash
# 查看所有镜像
docker images

# 删除镜像
docker rmi bookstore-api

# 清理未使用的镜像
docker image prune
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 进入容器内部
docker exec -it bookstore /bin/bash

# 查看容器资源使用
docker stats bookstore

# 重启容器
docker restart bookstore
```

### 日志和调试

```bash
# 实时查看日志
docker logs -f bookstore

# 查看最近100行日志
docker logs --tail 100 bookstore

# 检查容器健康状态
docker inspect bookstore --format='{{.State.Health.Status}}'
```

---

## 🔧 常见问题

### Q1: 端口已被占用

**错误信息**：
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解决方案**：
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 终止进程（替换PID）
taskkill /PID <进程ID> /F

# 或者使用不同的端口
docker run -p 8001:8000 bookstore-api
```

### Q2: 数据库权限问题

**解决方案**：
```bash
# 确保data目录存在并有写权限
mkdir data
icacls data /grant Everyone:F
```

### Q3: 构建镜像失败

**解决方案**：
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建（不使用缓存）
docker build --no-cache -t bookstore-api .
```

---

## 📈 性能优化

### 使用多阶段构建（高级）

创建 `Dockerfile.multistage`：

```dockerfile
# 阶段1：构建
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 阶段2：运行
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 使用多阶段构建
docker build -f Dockerfile.multistage -t bookstore-api:optimized .
```

---

## 🎓 学习要点

通过这个项目，你将学会：

1. ✅ **FastAPI开发**
   - RESTful API设计
   - Pydantic数据验证
   - 自动生成API文档

2. ✅ **SQLite数据库**
   - 数据库初始化
   - CRUD操作
   - 数据持久化

3. ✅ **Docker容器化**
   - Dockerfile编写
   - 镜像构建
   - 容器运行
   - 卷挂载
   - Docker Compose

4. ✅ **前后端协作**
   - HTML/CSS/JavaScript
   - Fetch API调用
   - 异步数据更新

---

## 🚢 部署到生产环境

### 使用云服务器

```bash
# 1. 推送镜像到Docker Hub
docker tag bookstore-api yourusername/bookstore-api
docker push yourusername/bookstore-api

# 2. 在服务器上拉取并运行
docker pull yourusername/bookstore-api
docker run -d -p 80:8000 --name bookstore yourusername/bookstore-api
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📝 下一步

- [ ] 添加用户认证（JWT）
- [ ] 集成PostgreSQL替代SQLite
- [ ] 添加Redis缓存
- [ ] 实现图书搜索功能
- [ ] 添加单元测试
- [ ] 配置CI/CD流水线

---

**🎉 恭喜！你已经掌握了完整的FastAPI应用Docker部署流程！**
