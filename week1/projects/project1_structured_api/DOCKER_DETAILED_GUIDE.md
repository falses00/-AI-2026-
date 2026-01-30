# 🐳 Docker 配置详解与部署方案对比

> 深入理解 Dockerfile 和 docker-compose.yml 的每一个配置项

---

## 📚 目录

1. [Dockerfile 逐行详解](#dockerfile-逐行详解)
2. [docker-compose.yml 配置详解](#docker-composeyml-配置详解)
3. [部署方案对比](#部署方案对比)
4. [数据库部署方案](#数据库部署方案)
5. [最佳实践建议](#最佳实践建议)

---

## 1️⃣ Dockerfile 逐行详解

### 当前的 Dockerfile

```dockerfile
# 使用Python 3.12官方镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据库目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 逐行解析

#### `FROM python:3.12-slim`

**作用**：指定基础镜像

**选项对比**：

| 镜像类型 | 大小 | 优点 | 缺点 | 使用场景 |
|---------|------|------|------|---------|
| `python:3.12` | ~1GB | 完整工具链 | 体积大 | 开发环境 |
| `python:3.12-slim` | ~150MB | 体积小，包含基本工具 | 缺少编译工具 | ✅ **生产推荐** |
| `python:3.12-alpine` | ~50MB | 极小体积 | 兼容性问题多 | 极端优化场景 |

**为什么选择 slim**：
- ✅ 体积适中（150MB vs 1GB）
- ✅ 包含必要的系统库
- ✅ 兼容性好
- ✅ glibc 基础（比 alpine 的 musl 兼容性好）

---

#### `WORKDIR /app`

**作用**：设置容器内的工作目录

**原理**：
```bash
# 相当于执行：
cd /app
# 后续的 COPY、RUN 等命令都在这个目录下执行
```

**为什么用 /app**：
- ✅ 符合 Linux 惯例
- ✅ 避免污染系统目录
- ✅ 路径简短清晰

---

#### `COPY requirements.txt .`

**作用**：只复制依赖文件

**为什么分两次 COPY**？（这是关键优化！）

```dockerfile
# ❌ 错误做法：一次性复制所有文件
COPY . .
RUN pip install -r requirements.txt

# ✅ 正确做法：先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # 再复制其他文件
```

**原理：Docker 分层缓存**

```
[Layer 1] FROM python:3.12-slim          ← 基础层（最大）
[Layer 2] COPY requirements.txt          ← 依赖文件（很少变化）
[Layer 3] RUN pip install                ← 安装依赖（耗时）
[Layer 4] COPY . .                       ← 应用代码（经常变化）
```

**优势**：
- ✅ 代码改动时，不需要重新安装依赖
- ✅ 构建速度提升 10-100 倍
- ✅ 节省带宽和存储

**示例**：
```bash
# 第一次构建：10分钟
docker build -t app .

# 修改 main.py 后重新构建：只需 10秒！
# 因为 Layer 1-3 都使用缓存
docker build -t app .
```

---

#### `RUN pip install --no-cache-dir -r requirements.txt`

**作用**：安装 Python 依赖

**参数详解**：

```dockerfile
RUN pip install \
    --no-cache-dir \    # 不缓存下载的包
    -r requirements.txt  # 从文件读取依赖
```

**为什么用 --no-cache-dir**：
```bash
# 不加此参数：
pip install fastapi    # 下载后缓存在 ~/.cache/pip (500MB+)

# 加此参数：
pip install fastapi --no-cache-dir  # 下载后立即删除临时文件

# 结果：
镜像体积减少 50-200MB！
```

**其他优化选项**：

```dockerfile
# 方案1：指定国内镜像源（加速）
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt

# 方案2：分组安装（分层优化）
RUN pip install --no-cache-dir \
    fastapi uvicorn  # 基础依赖
RUN pip install --no-cache-dir \
    pydantic        # 其他依赖

# 方案3：使用 pip-tools（锁定版本）
COPY requirements.in .
RUN pip install pip-tools
RUN pip-compile requirements.in
RUN pip install -r requirements.txt
```

---

#### `COPY . .`

**作用**：复制所有项目文件

**优化：使用 .dockerignore**

创建 `.dockerignore` 文件：
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git/
.gitignore
data/           # 不复制数据库文件！
*.db
*.sqlite
.env            # 不复制环境变量文件
node_modules/
```

**效果**：
- ✅ 减少镜像体积
- ✅ 加快构建速度
- ✅ 避免敏感文件进入镜像

---

#### `RUN mkdir -p /app/data`

**作用**：创建数据目录

**为什么需要**：
```python
# database.py 中会写入文件：
DB_FILE = Path(__file__).parent / "data" / "bookstore.db"

# 如果目录不存在，会报错：
# FileNotFoundError: [Errno 2] No such file or directory
```

**-p 参数**：
```bash
mkdir -p /app/data
# -p: 如果目录已存在，不报错
#     如果父目录不存在，自动创建
```

---

#### `EXPOSE 8000`

**作用**：声明容器监听的端口

**重要**：这只是文档说明，不会实际暴露端口！

```dockerfile
EXPOSE 8000  # 只是声明，没有实际作用
```

**真正暴露端口**：
```bash
# 使用 docker run 时指定
docker run -p 8000:8000 app

# 或在 docker-compose.yml 中指定
ports:
  - "8000:8000"
```

**为什么还要写**：
- ✅ 文档作用（告诉使用者端口）
- ✅ 工具识别（某些部署平台会读取）

---

#### `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`

**作用**：容器启动时执行的命令

**CMD vs ENTRYPOINT**：

```dockerfile
# CMD：可以被 docker run 覆盖
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# ENTRYPOINT：不能被覆盖（更严格）
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0"]
```

**为什么用 0.0.0.0**：
```python
# ❌ 错误：只监听本地
uvicorn main:app --host 127.0.0.1  # 外部无法访问！

# ✅ 正确：监听所有网络接口
uvicorn main:app --host 0.0.0.0   # 可以从外部访问
```

**参数详解**：
```bash
uvicorn main:app \
  --host 0.0.0.0 \    # 监听所有IP
  --port 8000 \       # 端口
  --workers 4 \       # 工作进程数（生产环境）
  --log-level info    # 日志级别
```

---

## 2️⃣ docker-compose.yml 配置详解

### 当前配置

```yaml
version: '3.8'

services:
  bookstore-api:
    build: .
    container_name: bookstore-api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 逐行解析

#### `version: '3.8'`

**作用**：指定 Compose 文件格式版本

**版本对比**：

| 版本 | 发布时间 | 特性 | Docker版本要求 |
|------|---------|------|----------------|
| 2.x | 2016 | 基础功能 | Docker 1.10+ |
| 3.0-3.7 | 2017-2019 | Swarm支持 | Docker 17.04+ |
| **3.8** | 2020 | 最新稳定版 | Docker 19.03+ ✅ |

**为什么选 3.8**：
- ✅ 功能完善
- ✅ 兼容性好
- ✅ 文档丰富

---

#### `services:`

**作用**：定义服务（容器）

```yaml
services:
  service1:  # 第一个服务
    ...
  service2:  # 第二个服务
    ...
```

**服务 vs 容器**：
- **服务**：逻辑概念（如"数据库"）
- **容器**：服务的实例（可以有多个）

---

#### `build: .`

**作用**：指定如何构建镜像

**简写 vs 完整形式**：

```yaml
# 简写：
build: .

# 完整形式：
build:
  context: .              # Dockerfile 所在目录
  dockerfile: Dockerfile  # Dockerfile 文件名
  args:                   # 构建参数
    - PYTHON_VERSION=3.12
  cache_from:            # 缓存来源
    - myapp:latest
```

**使用场景**：

```yaml
# 场景1：使用现有镜像（不构建）
image: python:3.12-slim

# 场景2：构建自定义镜像
build: .

# 场景3：两者结合（先构建，再push）
build: .
image: myusername/bookstore:latest
```

---

#### `container_name: bookstore-api`

**作用**：指定容器名称

**有无的区别**：

```yaml
# 有 container_name：
container_name: bookstore-api
# 容器名：bookstore-api（固定）

# 无 container_name：
# （留空）
# 容器名：project1_bookstore-api_1（自动生成）
```

**优劣对比**：

| 方式 | 优点 | 缺点 |
|------|------|------|
| **指定名称** | 名称固定，易于管理 | 不能启动多个实例 |
| **自动生成** | 支持扩展（多实例） | 名称不确定 |

**建议**：
- ✅ 单实例服务：指定名称
- ✅ 需要扩展的服务：不指定

---

#### `ports: - "8000:8000"`

**作用**：端口映射

**格式详解**：

```yaml
ports:
  - "宿主机端口:容器端口"
  - "8000:8000"
  
# 例子：
ports:
  - "80:8000"     # 外部访问80端口 → 容器8000端口
  - "8000:8000"   # 外部访问8000 → 容器8000
  - "127.0.0.1:8000:8000"  # 只允许本机访问
```

**完整形式**：

```yaml
ports:
  - target: 8000      # 容器端口
    published: 8000   # 宿主机端口
    protocol: tcp     # 协议
    mode: host        # 模式
```

---

#### `volumes: - ./data:/app/data`

**作用**：挂载数据卷（最重要的配置！）

**格式**：

```yaml
volumes:
  - "宿主机路径:容器路径"
  - "./data:/app/data"
```

**卷类型对比**：

```yaml
# 1. 绑定挂载（Bind Mount）- 当前使用
volumes:
  - ./data:/app/data  # 本地目录 → 容器目录

# 2. 命名卷（Named Volume）
volumes:
  - db-data:/app/data
volumes:
  db-data:  # 在顶层定义

# 3. 匿名卷（Anonymous Volume）
volumes:
  - /app/data  # Docker自动管理
```

**对比表格**：

| 类型 | 位置 | 优点 | 缺点 | 使用场景 |
|------|------|------|------|----------|
| **绑定挂载** | 本地目录 | 易于访问和备份 | 路径依赖系统 | ✅ 开发环境 |
| **命名卷** | Docker管理 | 跨平台、高性能 | 不易直接访问 | ✅ 生产环境 |
| **匿名卷** | Docker管理 | 简单 | 难以管理 | 临时数据 |

**数据流向**：

```
宿主机（Windows）          容器（Linux）
├── i:\Study FastAPI\     ├── /app/
│   └── data/             │   └── data/
│       └── bookstore.db  │       └── bookstore.db
                         ↕ 实时同步
```

**权限设置**：

```yaml
volumes:
  - ./data:/app/data              # 读写（默认）
  - ./data:/app/data:ro           # 只读
  - ./data:/app/data:rw           # 读写（显式）
  - ./config:/app/config:ro       # 配置只读
```

---

#### `environment:`

**作用**：设置环境变量

**三种方式**：

```yaml
# 方式1：直接设置
environment:
  - PYTHONUNBUFFERED=1
  - DATABASE_URL=sqlite:///app/data/db.sqlite

# 方式2：从文件读取
env_file:
  - .env

# 方式3：键值对形式
environment:
  PYTHONUNBUFFERED: 1
  DATABASE_URL: sqlite:///app/data/db.sqlite
```

**PYTHONUNBUFFERED=1 的作用**：

```python
# 不设置（默认）：
print("Hello")  # 输出被缓冲，可能看不到实时日志

# 设置后：
print("Hello")  # 立即输出到 docker logs
```

**常用环境变量**：

```yaml
environment:
  # Python相关
  - PYTHONUNBUFFERED=1      # 禁用缓冲
  - PYTHONPATH=/app         # 模块搜索路径
  
  # 应用相关
  - DEBUG=False             # 调试模式
  - SECRET_KEY=xxx          # 密钥
  
  # 数据库相关
  - DATABASE_URL=postgresql://user:pass@db:5432/mydb
```

---

#### `restart: unless-stopped`

**作用**：容器重启策略

**选项对比**：

| 策略 | 说明 | 使用场景 |
|------|------|----------|
| `no` | 不自动重启 | 临时容器 |
| `always` | 总是重启 | 关键服务 |
| `on-failure` | 失败时重启 | 一般服务 |
| **`unless-stopped`** | 除非手动停止，否则重启 | ✅ **推荐** |

**示例**：

```yaml
restart: unless-stopped

# Docker Desktop 重启 → 容器自动启动 ✅
# 容器崩溃 → 自动重启 ✅
# docker stop bookstore → 不会自动启动 ✅
```

---

#### `healthcheck:`

**作用**：健康检查

**配置详解**：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s      # 每30秒检查一次
  timeout: 10s       # 超时时间
  retries: 3         # 重试3次才判定为不健康
  start_period: 40s  # 启动宽限期
```

**test 的多种写法**：

```yaml
# 方式1：shell 形式
test: curl -f http://localhost:8000/ || exit 1

# 方式2：exec 形式（推荐）
test: ["CMD", "curl", "-f", "http://localhost:8000/"]

# 方式3：使用 wget
test: ["CMD", "wget", "--spider", "http://localhost:8000/"]

# 方式4：Python 脚本
test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/')"]
```

**健康状态流转**：

```
starting → healthy → unhealthy
   ↓          ↑          ↓
   └──────────┴──────────┘
   
starting: 启动阶段（start_period内）
healthy: interval内检查通过
unhealthy: 连续retries次失败
```

**查看健康状态**：

```bash
docker ps  # 查看 STATUS 列
# healthy / unhealthy / starting
```

---

## 3️⃣ 部署方案对比

### 方案1：当前方案（SQLite + 单容器）

```yaml
# docker-compose.yml
services:
  api:
    build: .
    volumes:
      - ./data:/app/data  # SQLite文件
```

**架构图**：

```
┌─────────────────────────────┐
│  Docker Container           │
│  ┌─────────────────────┐   │
│  │  FastAPI App        │   │
│  │  ┌──────────────┐   │   │
│  │  │  SQLite DB   │   │   │
│  │  └──────────────┘   │   │
│  └─────────────────────┘   │
└─────────────────────────────┘
         ↕
    ./data/db.sqlite (本地文件)
```

**优点**：
- ✅ 简单，一个容器搞定
- ✅ 无需网络配置
- ✅ 适合学习和小项目
- ✅ 数据文件在本地，易于备份

**缺点**：
- ❌ 性能有限
- ❌ 不支持并发写入
- ❌ 不适合生产环境
- ❌ 无法横向扩展

**适用场景**：
- 学习项目 ✅
- 个人小工具 ✅
- 快速原型 ✅

---

### 方案2：PostgreSQL + 多容器

```yaml
# docker-compose.yml
services:
  api:
    build: .
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
  
  db:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb

volumes:
  postgres-data:
```

**架构图**：

```
┌─────────────────┐      ┌─────────────────┐
│  API Container  │ ───→ │  DB Container   │
│                 │      │                 │
│  FastAPI        │      │  PostgreSQL     │
└─────────────────┘      └─────────────────┘
                               ↕
                         postgres-data (卷)
```

**优点**：
- ✅ 生产级数据库
- ✅ 支持高并发
- ✅ 数据一致性强
- ✅ 可横向扩展
- ✅ 备份和恢复工具完善

**缺点**：
- ❌ 配置复杂
- ❌ 资源占用大
- ❌ 需要了解SQL和连接管理

**完整配置示例**：

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: bookstore-api
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy  # 等待数据库健康
    environment:
      - DATABASE_URL=postgresql://bookstore:secret@db:5432/bookstore
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    container_name: bookstore-db
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # 初始化脚本
    environment:
      POSTGRES_USER: bookstore
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: bookstore
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bookstore"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

**代码改动**（使用SQLAlchemy）：

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/bookstore.db"  # 默认SQLite
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # PostgreSQL需要
)
SessionLocal = sessionmaker(bind=engine)
```

**适用场景**：
- 生产环境 ✅
- 多用户系统 ✅
- 数据重要性高 ✅

---

### 方案3：Redis + PostgreSQL + 多容器（完整方案）

```yaml
services:
  api:
    build: .
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - api
```

**架构图**：

```
         Internet
            ↓
      ┌─────────┐
      │  Nginx  │ (反向代理)
      └─────────┘
            ↓
      ┌─────────┐
      │   API   │
      └─────────┘
        ↙     ↘
  ┌──────┐   ┌───────┐
  │ Redis│   │Postgres│
  └──────┘   └───────┘
```

**优点**：
- ✅ 高性能（Redis缓存）
- ✅ 高可用（负载均衡）
- ✅ 生产就绪

**缺点**：
- ❌ 非常复杂
- ❌ 资源需求高
- ❌ 运维成本高

---

## 4️⃣ 数据库部署方案深度对比

### SQLite（当前方案）

**部署方式**：

```yaml
# 1. 文件直接挂载
volumes:
  - ./data:/app/data

# 2. 应用代码中创建
# database.py
DB_FILE = Path(__file__).parent / "data" / "bookstore.db"
conn = sqlite3.connect(DB_FILE)
```

**数据流动**：

```
Container                   Host (Windows)
/app/data/bookstore.db  ←→  i:\...\data\bookstore.db
                        (实时同步)
```

**优点**：
- ✅ **零配置**：无需单独数据库服务
- ✅ **轻量级**：整个数据库就是一个文件
- ✅ **便携性**：复制文件即可备份
- ✅ **开发友好**：本地直接查看修改

**限制**：
- ❌ 并发写入差（同时只能一个写）
- ❌ 无网络访问（只能本地）
- ❌ 文件损坏风险
- ❌ 不适合大数据量（>GB级）

---

### PostgreSQL（分离部署）

**部署方式**：

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypass
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"  # 可选：暴露给宿主机

volumes:
  postgres-data:  # 命名卷
```

**数据流动**：

```
API Container          DB Container
    ↓                      ↓
TCP连接             PostgreSQL进程
    ↓                      ↓
db:5432 ────────→ /var/lib/postgresql/data
                         ↕
                  postgres-data卷
                  (Docker管理的存储)
```

**网络连接**：

```python
# API容器中：
DATABASE_URL = "postgresql://myuser:mypass@db:5432/mydb"
#                                         ↑
#                                    容器名（Docker DNS解析）
```

**数据持久化层级**：

```
物理硬盘
    ↓
Docker卷管理器
    ↓
postgres-data卷
    ↓
容器文件系统 /var/lib/postgresql/data
    ↓
PostgreSQL数据文件
```

**优点**：
- ✅ **高性能**：优化的查询引擎
- ✅ **高并发**：MVCC支持
- ✅ **事务完整**：ACID保证
- ✅ **可扩展**：主从复制、分区

**复杂度**：
- ❌ 需要额外容器
- ❌ 需要网络配置
- ❌ 需要学习SQL连接池
- ❌ 备份恢复更复杂

---

### MySQL（替代方案）

```yaml
services:
  db:
    image: mysql:8
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: bookstore
      MYSQL_USER: user
      MYSQL_PASSWORD: pass
```

**vs PostgreSQL**：

| 特性 | PostgreSQL | MySQL |
|------|-----------|-------|
| 并发性能 | 更好（MVCC） | 好 |
| 复杂查询 | 更强 | 一般 |
| JSON支持 | 原生强大 | 较弱 |
| 生态 | Python友好 | PHP友好 |
| 学习曲线 | 陡 | 平缓 |

---

## 5️⃣ 最佳实践建议

### 开发环境

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  api:
    build:
      context: .
      target: development  # 多阶段构建
    volumes:
      - .:/app             # 代码热重载
      - /app/__pycache__   # 排除缓存
    environment:
      - DEBUG=True
      - HOT_RELOAD=True
    command: uvicorn main:app --reload --host 0.0.0.0
```

### 生产环境

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: myregistry/bookstore:latest  # 使用预构建镜像
    deploy:
      replicas: 3        # 多实例
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 安全建议

```yaml
services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password  # 使用secrets
    secrets:
      - db_password
    networks:
      - backend  # 不暴露到公网

  api:
    networks:
      - backend
      - frontend

networks:
  backend:
    internal: true  # 内部网络
  frontend:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

---

## 📊 总结对比表

| 方案 | 复杂度 | 性能 | 成本 | 可扩展性 | 推荐场景 |
|------|--------|------|------|----------|----------|
| **SQLite单容器** | ⭐ | ⭐⭐ | ⭐ | ⭐ | 学习、原型 |
| **PostgreSQL** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 生产环境 |
| **完整微服务** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 大型系统 |

---

## 🎓 学习路径建议

1. **第一周**：掌握当前的 SQLite 单容器方案
2. **第二周**：尝试添加 PostgreSQL 容器
3. **第三周**：学习 Redis 缓存和 Nginx 反向代理
4. **第四周**：实践生产环境部署（云服务器）

---

**现在你应该完全理解每一行配置的作用了！🎉**
