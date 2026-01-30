# 📘 Docker 部署完全操作手册

> **图书管理系统 - 从零到部署的每一步详解**

---

## 📋 目录

1. [前置准备检查](#1️⃣-前置准备检查)
2. [项目文件准备](#2️⃣-项目文件准备)
3. [开发环境部署](#3️⃣-开发环境部署)
4. [生产环境部署](#4️⃣-生产环境部署)
5. [常用操作命令](#5️⃣-常用操作命令)
6. [监控和日志查看](#6️⃣-监控和日志查看)
7. [停止和清理](#7️⃣-停止和清理)
8. [故障排查](#8️⃣-故障排查)

---

## 1️⃣ 前置准备检查

### 步骤 1.1：检查 Docker 是否安装

```powershell
# 检查 Docker 版本
docker --version

# 预期输出示例：
# Docker version 24.0.7, build afdd53b

# 如果提示命令不存在，需要安装 Docker Desktop
# 下载地址：https://www.docker.com/products/docker-desktop
```

**注释**：Docker 是容器化平台的核心工具

---

### 步骤 1.2：检查 Docker Compose 是否可用

```powershell
# 检查 Docker Compose 版本
docker-compose --version

# 预期输出示例：
# Docker Compose version v2.23.0

# 或者使用新版本命令（推荐）
docker compose version

# 预期输出示例：
# Docker Compose version v2.23.0
```

**注释**：Docker Compose 用于管理多容器应用

---

### 步骤 1.3：检查 Docker Desktop 是否运行

```powershell
# 检查 Docker 守护进程状态
docker ps

# 如果成功，会显示运行中的容器列表（可能为空）
# 如果失败，提示类似：
# error during connect: This error may indicate that the docker daemon is not running.

# 解决方法：打开 Docker Desktop 应用，等待启动完成
```

**注释**：Docker Desktop 必须处于运行状态才能执行 Docker 命令

---

### 步骤 1.4：检查磁盘空间

```powershell
# 查看当前磁盘空间
Get-PSDrive C | Select-Object Used,Free

# 建议至少有 5GB 可用空间用于 Docker 镜像和容器
```

**注释**：Docker 镜像会占用磁盘空间，确保有足够空间

---

## 2️⃣ 项目文件准备

### 步骤 2.1：进入项目目录

```powershell
# 进入项目根目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 确认当前位置
pwd

# 预期输出：
# Path
# ----
# i:\Study FastAPI\week1\projects\project1_structured_api
```

**注释**：所有后续命令都应在此目录下执行

---

### 步骤 2.2：检查必需文件

```powershell
# 列出当前目录文件
ls

# 必需文件检查清单：
# ✅ Dockerfile          - Docker 镜像配置文件
# ✅ requirements.txt    - Python 依赖列表
# ✅ main.py            - FastAPI 主应用
# ✅ models.py          - 数据模型
# ✅ database.py        - 数据库层
# ✅ docker-compose.yml - Docker Compose 基础配置
```

**注释**：这些是运行应用的最小文件集

---

### 步骤 2.3：检查可选配置文件

```powershell
# 检查是否存在高级配置文件
ls docker-compose.*.yml
ls Dockerfile.*
ls nginx/ -ErrorAction SilentlyContinue

# 可选文件：
# - docker-compose.dev.yml  - 开发环境配置
# - docker-compose.prod.yml - 生产环境配置（含 Nginx）
# - Dockerfile.dev          - 开发环境镜像
# - nginx/                  - Nginx 配置目录
```

**注释**：这些文件提供不同的部署选项

---

### 步骤 2.4：创建数据目录

```powershell
# 创建数据存储目录（如果不存在）
mkdir data -ErrorAction SilentlyContinue

# 创建日志目录（可选）
mkdir logs -ErrorAction SilentlyContinue

# 创建 Nginx 日志目录（如果使用 Nginx）
mkdir nginx\logs -ErrorAction SilentlyContinue

# 确认目录创建成功
ls -Directory

# 预期输出包含：
# data/
# logs/
# nginx/
```

**注释**：这些目录用于数据持久化和日志存储

---

## 3️⃣ 开发环境部署

### 场景：快速开发和测试

**特点**：
- ✅ 代码修改立即生效
- ✅ 自动重启服务
- ✅ 详细的调试日志

---

### 步骤 3.1：使用基础配置启动

```powershell
# 启动开发环境（后台运行）
docker-compose up -d

# 命令解析：
# docker-compose  - Docker Compose 工具
# up              - 启动服务
# -d              - detached 模式（后台运行）

# 预期输出：
# [+] Running 2/2
#  ✔ Network project1_structured_api_default  Created
#  ✔ Container bookstore-api                  Started
```

**注释**：
- `up` 会自动构建镜像（如果不存在）
- `-d` 使容器在后台运行，不占用终端

---

### 步骤 3.2：使用开发配置启动（推荐）

```powershell
# 使用开发环境配置启动
docker-compose -f docker-compose.dev.yml up -d

# 命令解析：
# -f docker-compose.dev.yml  - 指定配置文件

# 预期输出：
# [+] Building 45.2s (10/10) FINISHED
# [+] Running 1/1
#  ✔ Container bookstore-dev  Started
```

**注释**：
- 开发配置包含代码热重载
- 修改代码后自动重启应用

---

### 步骤 3.3：查看启动状态

```powershell
# 查看容器状态
docker-compose -f docker-compose.dev.yml ps

# 预期输出：
# NAME            IMAGE                COMMAND                  STATUS
# bookstore-dev   project1_api:latest  "uvicorn main:app ..." Up 2 minutes (healthy)

# 状态说明：
# Up          - 容器正在运行
# (healthy)   - 健康检查通过
# (unhealthy) - 健康检查失败
```

**注释**：`(healthy)` 表示应用已成功启动

---

### 步骤 3.4：查看启动日志

```powershell
# 查看实时日志
docker-compose -f docker-compose.dev.yml logs -f

# 命令解析：
# logs  - 查看日志
# -f    - follow 模式（实时跟踪）

# 预期输出：
# bookstore-dev  | INFO:     Uvicorn running on http://0.0.0.0:8000
# bookstore-dev  | INFO:     Application startup complete.

# 按 Ctrl+C 退出日志查看（不会停止容器）
```

**注释**：
- 日志显示应用启动信息
- 看到 "startup complete" 表示成功

---

### 步骤 3.5：测试访问

```powershell
# 方式1：浏览器访问
# 打开浏览器，访问：http://localhost:8000

# 方式2：命令行测试
curl http://localhost:8000/api

# 预期输出：
# {"message": "API is running"}

# 方式3：访问 API 文档
# 浏览器访问：http://localhost:8000/docs
```

**注释**：
- 如果能看到响应，说明部署成功
- `/docs` 提供交互式 API 文档

---

## 4️⃣ 生产环境部署

### 场景：稳定的生产服务

**特点**：
- ✅ 包含 Nginx 反向代理
- ✅ 负载均衡和缓存
- ✅ SSL 支持（可选）
- ✅ 健康检查和自动重启

---

### 步骤 4.1：构建生产镜像

```powershell
# 构建生产环境镜像
docker-compose -f docker-compose.prod.yml build

# 命令解析：
# build  - 构建镜像（不启动容器）

# 预期输出：
# [+] Building 67.3s (12/12) FINISHED
#  => [api internal] load build definition
#  => => transferring dockerfile: 1.23kB
#  => [api 1/7] FROM docker.io/library/python:3.12-slim
#  => [api 6/7] COPY main.py models.py database.py ./
#  => [api 7/7] RUN mkdir -p /app/data
#  => [api] exporting to image
#  => => exporting layers
#  => => writing image sha256:abc123...
```

**注释**：
- 首次构建需要下载基础镜像，耗时较长
- 后续构建会使用缓存，速度较快

---

### 步骤 4.2：启动生产环境

```powershell
# 启动生产环境（包含 Nginx）
docker-compose -f docker-compose.prod.yml up -d

# 预期输出：
# [+] Running 3/3
#  ✔ Network app-network       Created
#  ✔ Container bookstore-api   Started
#  ✔ Container bookstore-nginx Started
```

**注释**：
- 同时启动 API 和 Nginx 两个容器
- Nginx 会等待 API 健康后才启动

---

### 步骤 4.3：验证服务启动

```powershell
# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 预期输出：
# NAME              IMAGE              STATUS
# bookstore-api     bookstore:latest   Up 1 minute (healthy)
# bookstore-nginx   nginx:1.25-alpine  Up 1 minute (healthy)

# 检查端口映射
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 预期输出：
# NAMES             PORTS
# bookstore-nginx   0.0.0.0:80->80/tcp
# bookstore-api     8000/tcp
```

**注释**：
- Nginx 暴露 80 端口（HTTP）
- API 只在内部可访问（通过 Nginx 代理）

---

### 步骤 4.4：测试 Nginx 代理

```powershell
# 通过 Nginx 访问（80 端口）
curl http://localhost/api

# 预期输出：
# {"message": "API is running"}

# 访问健康检查端点
curl http://localhost/health

# 预期输出：
# healthy

# 浏览器访问主页
# http://localhost  （不需要端口号）
```

**注释**：
- 用户通过 80 端口访问 Nginx
- Nginx 自动转发到后端 API

---

### 步骤 4.5：查看 Nginx 日志

```powershell
# 查看 Nginx 访问日志
Get-Content nginx\logs\access.log -Tail 20

# 预期输出示例：
# 172.20.0.1 - - [30/Jan/2026:16:00:00 +0000] "GET /api HTTP/1.1" 200 31

# 查看 Nginx 错误日志
Get-Content nginx\logs\error.log -Tail 20

# 实时监控日志
Get-Content nginx\logs\access.log -Wait
```

**注释**：
- 访问日志记录所有请求
- 错误日志记录异常情况

---

## 5️⃣ 常用操作命令

### 5.1 容器管理命令

#### 启动容器

```powershell
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d api

# 启动并重新构建镜像
docker-compose up -d --build

# 启动时查看日志（不后台运行）
docker-compose up
# 按 Ctrl+C 停止
```

**注释**：
- `--build` 强制重新构建镜像
- 不加 `-d` 会在前台运行，适合调试

---

#### 停止容器

```powershell
# 停止所有服务
docker-compose stop

# 停止指定服务
docker-compose stop api

# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和网络（保留卷）
docker-compose down

# 停止并删除所有内容（包括卷 ⚠️ 数据会丢失）
docker-compose down -v
```

**注释**：
- `stop` 只停止容器
- `down` 停止并删除容器
- `-v` 会删除数据卷（慎用！）

---

#### 重启容器

```powershell
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart api

# 重启 Nginx（重新加载配置）
docker-compose restart nginx
```

**注释**：
- 修改配置文件后需要重启
- 数据不会丢失

---

### 5.2 镜像管理命令

#### 查看镜像

```powershell
# 查看所有镜像
docker images

# 预期输出：
# REPOSITORY    TAG       IMAGE ID       SIZE
# bookstore     latest    abc123def456   500MB
# nginx         1.25      def789ghi012   150MB
# python        3.12      ghi345jkl678   1GB

# 查看镜像详细信息
docker inspect bookstore:latest
```

**注释**：
- 镜像是容器的模板
- 同一镜像可以创建多个容器

---

#### 删除镜像

```powershell
# 删除指定镜像
docker rmi bookstore:latest

# 删除所有未使用的镜像
docker image prune

# 删除所有镜像（⚠️ 谨慎使用）
docker image prune -a

# 强制删除（即使有容器在使用）
docker rmi -f bookstore:latest
```

**注释**：
- 删除前需要先停止使用该镜像的容器
- `prune` 清理悬空镜像

---

### 5.3 容器交互命令

#### 进入容器内部

```powershell
# 进入正在运行的容器
docker exec -it bookstore-api bash

# 如果容器使用 Alpine Linux（精简版）
docker exec -it bookstore-api sh

# 进入容器后的操作示例：
# ls                    # 查看文件
# cat main.py          # 查看代码
# python -m pip list   # 查看已安装的包
# exit                 # 退出容器
```

**注释**：
- `-it` 启用交互式终端
- `bash` 或 `sh` 是 Shell 程序

---

#### 在容器中执行命令

```powershell
# 查看容器内进程
docker exec bookstore-api ps aux

# 查看 Python 版本
docker exec bookstore-api python --version

# 查看数据库文件
docker exec bookstore-api ls -lh /app/data

# 测试网络连接（从 API 容器 ping Nginx）
docker exec bookstore-api ping nginx -c 3
```

**注释**：
- 不需要进入容器也能执行命令
- 适合快速检查

---

#### 复制文件

```powershell
# 从容器复制文件到宿主机
docker cp bookstore-api:/app/data/bookstore.db ./backup.db

# 从宿主机复制文件到容器
docker cp config.json bookstore-api:/app/config.json

# 复制整个目录
docker cp bookstore-api:/app/logs ./logs-backup
```

**注释**：
- 用于备份或传输文件
- 容器不需要运行

---

### 5.4 日志管理命令

#### 查看日志

```powershell
# 查看所有服务日志
docker-compose logs

# 查看指定服务日志
docker-compose logs api

# 实时跟踪日志
docker-compose logs -f api

# 查看最近 100 行日志
docker-compose logs --tail=100 api

# 显示时间戳
docker-compose logs -t api

# 查看特定时间段日志
docker-compose logs --since="2026-01-30T15:00:00" api
```

**注释**：
- `-f` 实时跟踪（按 Ctrl+C 退出）
- `--tail` 限制行数

---

#### 清理日志

```powershell
# Docker 日志位置（仅供参考）
# Windows: C:\ProgramData\Docker\containers\<container-id>\<container-id>-json.log

# 清理所有容器日志
docker system prune -a

# 限制日志文件大小（修改 Docker daemon 配置）
# 文件：C:\ProgramData\Docker\config\daemon.json
# {
#   "log-driver": "json-file",
#   "log-opts": {
#     "max-size": "10m",
#     "max-file": "3"
#   }
# }
```

**注释**：
- 日志占用磁盘空间
- 定期清理或限制大小

---

### 5.5 网络管理命令

#### 查看网络

```powershell
# 查看所有 Docker 网络
docker network ls

# 预期输出：
# NETWORK ID     NAME          DRIVER    SCOPE
# abc123def456   app-network   bridge    local
# def456ghi789   bridge        bridge    local

# 查看网络详情
docker network inspect app-network
```

**注释**：
- Docker 容器通过网络互相通信
- `bridge` 是默认网络类型

---

#### 连接容器到网络

```powershell
# 创建自定义网络
docker network create my-network

# 将容器连接到网络
docker network connect my-network bookstore-api

# 断开网络连接
docker network disconnect my-network bookstore-api

# 删除网络
docker network rm my-network
```

**注释**：
- 自定义网络提供更好的隔离
- 容器可以同时连接多个网络

---

## 6️⃣ 监控和日志查看

### 6.1 资源使用监控

```powershell
# 实时监控容器资源使用
docker stats

# 预期输出：
# CONTAINER       CPU %   MEM USAGE / LIMIT   NET I/O
# bookstore-api   0.5%    50MiB / 2GiB        1.2kB / 800B
# bookstore-nginx 0.1%    10MiB / 2GiB        800B / 1.2kB

# 监控指定容器
docker stats bookstore-api

# 只显示一次（不持续更新）
docker stats --no-stream
```

**注释**：
- CPU%: CPU 使用百分比
- MEM: 内存使用量
- NET I/O: 网络流量

---

### 6.2 健康检查

```powershell
# 查看容器健康状态
docker ps --format "table {{.Names}}\t{{.Status}}"

# 预期输出：
# NAMES             STATUS
# bookstore-api     Up 10 minutes (healthy)

# 查看健康检查详情
docker inspect bookstore-api --format='{{json .State.Health}}' | ConvertFrom-Json

# 查看健康检查日志
docker inspect bookstore-api --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

**注释**：
- `healthy`: 健康检查通过
- `unhealthy`: 健康检查失败
- `starting`: 启动阶段

---

### 6.3 访问日志分析

```powershell
# 统计 Nginx 访问次数
(Get-Content nginx\logs\access.log).Count

# 统计状态码分布
Get-Content nginx\logs\access.log | Select-String ' 200 ' | Measure-Object | Select-Object Count
Get-Content nginx\logs\access.log | Select-String ' 404 ' | Measure-Object | Select-Object Count

# 查找错误请求
Get-Content nginx\logs\access.log | Select-String ' 5\d\d '

# 统计访问最频繁的 IP
Get-Content nginx\logs\access.log | ForEach-Object { ($_ -split ' ')[0] } | Group-Object | Sort-Object Count -Descending | Select-Object -First 10
```

**注释**：
- 200: 成功
- 404: 未找到
- 5xx: 服务器错误

---

## 7️⃣ 停止和清理

### 7.1 正常停止服务

```powershell
# 停止开发环境
docker-compose -f docker-compose.dev.yml stop

# 预期输出：
# [+] Stopping 1/1
#  ✔ Container bookstore-dev  Stopped

# 停止生产环境（包括 Nginx）
docker-compose -f docker-compose.prod.yml stop

# 预期输出：
# [+] Stopping 2/2
#  ✔ Container bookstore-nginx  Stopped
#  ✔ Container bookstore-api    Stopped
```

**注释**：
- `stop` 优雅停止容器
- 容器可以重新启动
- 数据和配置保留

---

### 7.2 停止并删除容器

```powershell
# 停止并删除容器（保留镜像和数据）
docker-compose -f docker-compose.prod.yml down

# 预期输出：
# [+] Running 3/3
#  ✔ Container bookstore-nginx  Removed
#  ✔ Container bookstore-api    Removed
#  ✔ Network app-network        Removed

# 检查容器是否已删除
docker ps -a
# 不应该看到 bookstore-api 和 bookstore-nginx
```

**注释**：
- `down` 删除容器和网络
- 镜像和数据卷保留
- 可以重新 `up` 启动

---

### 7.3 完全清理

```powershell
# ⚠️ 警告：以下命令会删除数据！

# 删除容器、网络和卷
docker-compose -f docker-compose.prod.yml down -v

# 预期输出：
# [+] Running 4/4
#  ✔ Container bookstore-nginx  Removed
#  ✔ Container bookstore-api    Removed
#  ✔ Volume data                Removed
#  ✔ Network app-network        Removed

# 删除项目相关镜像
docker rmi bookstore:latest nginx:1.25-alpine python:3.12-slim

# 清理所有未使用的资源
docker system prune -a --volumes

# 确认提示：
# WARNING! This will remove:
#  - all stopped containers
#  - all networks not used by at least one container
#  - all images without at least one container associated to them
#  - all build cache
# Are you sure you want to continue? [y/N]
```

**注释**：
- `-v` 删除数据卷（数据会丢失！）
- `system prune -a` 清理所有未使用资源
- 谨慎使用，确保已备份重要数据

---

### 7.4 数据备份

```powershell
# 在完全清理前，备份数据
# 备份数据库文件
Copy-Item data\bookstore.db backup\bookstore_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# 备份整个数据目录
Copy-Item data\ backup\data_$(Get-Date -Format 'yyyyMMdd_HHmmss')\ -Recurse

# 备份日志
Copy-Item nginx\logs\ backup\logs_$(Get-Date -Format 'yyyyMMdd_HHmmss')\ -Recurse

# 确认备份
ls backup\
```

**注释**：
- 定期备份数据
- 备份前测试恢复流程

---

## 8️⃣ 故障排查

### 8.1 容器无法启动

**问题**：`docker-compose up -d` 后容器立即退出

```powershell
# 步骤1：查看容器状态
docker-compose ps

# 如果状态是 Exited (1) 或类似：

# 步骤2：查看容器日志
docker-compose logs api

# 步骤3：尝试前台运行（看详细错误）
docker-compose up

# 常见原因：
# - 端口被占用
# - 配置文件错误
# - 依赖未安装
# - 环境变量缺失
```

**解决方法**：
```powershell
# 检查端口占用
netstat -ano | findstr :8000

# 杀死占用端口的进程
taskkill /PID <进程ID> /F

# 检查配置文件语法
docker-compose -f docker-compose.prod.yml config

# 重新构建镜像
docker-compose build --no-cache
```

---

### 8.2 无法访问服务

**问题**：`curl http://localhost:8000` 无响应

```powershell
# 步骤1：检查容器是否运行
docker ps | findstr bookstore

# 步骤2：检查端口映射
docker port bookstore-api

# 预期输出：
# 8000/tcp -> 0.0.0.0:8000

# 步骤3：检查防火墙
# Windows 防火墙可能阻止访问

# 步骤4：从容器内部测试
docker exec bookstore-api curl http://localhost:8000/api

# 如果能访问，说明是宿主机网络问题
```

**解决方法**：
```powershell
# 重启 Docker Desktop
# 或重新创建容器
docker-compose down
docker-compose up -d
```

---

### 8.3 数据丢失

**问题**：容器重启后数据消失

```powershell
# 检查卷挂载
docker inspect bookstore-api --format='{{json .Mounts}}' | ConvertFrom-Json

# 确认挂载配置
docker-compose config | findstr volumes

# 预期看到：
# volumes:
#   - ./data:/app/data
```

**解决方法**：
```powershell
# 确保 docker-compose.yml 中有卷挂载
# volumes:
#   - ./data:/app/data

# 重新启动
docker-compose down
docker-compose up -d

# 检查数据目录
ls data\
```

---

### 8.4 镜像构建失败

**问题**：`docker build` 报错

```powershell
# 查看详细构建日志
docker-compose build --no-cache

# 常见错误：

# 错误1：网络问题（无法下载依赖）
# 解决：使用国内镜像源
# 修改 Dockerfile:
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 错误2：文件不存在
# 解决：检查 COPY 的文件路径

# 错误3：权限问题
# 解决：确保 Docker Desktop 有足够权限
```

---

### 8.5 Nginx 502 Bad Gateway

**问题**：访问 Nginx 提示 502 错误

```powershell
# 步骤1：检查后端 API 是否运行
docker ps | findstr bookstore-api

# 步骤2：查看 Nginx 错误日志
Get-Content nginx\logs\error.log -Tail 20

# 步骤3：测试网络连接
docker exec bookstore-nginx ping api

# 步骤4：检查 Nginx 配置
docker exec bookstore-nginx cat /etc/nginx/conf.d/bookstore.conf | findstr upstream
```

**解决方法**：
```powershell
# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 检查 depends_on 配置
docker-compose -f docker-compose.prod.yml config | findstr depends_on
```

---

## 📋 快速命令参考卡

```powershell
# ============== 启动相关 ==============
docker-compose up -d                    # 启动（后台）
docker-compose up                       # 启动（前台，看日志）
docker-compose up -d --build            # 重新构建并启动

# ============== 停止相关 ==============
docker-compose stop                     # 停止容器
docker-compose down                     # 停止并删除容器
docker-compose down -v                  # 停止并删除容器和数据（⚠️）

# ============== 查看相关 ==============
docker-compose ps                       # 查看容器状态
docker-compose logs -f                  # 查看日志
docker stats                            # 查看资源使用

# ============== 管理相关 ==============
docker-compose restart                  # 重启容器
docker-compose exec api bash            # 进入容器
docker-compose build                    # 构建镜像

# ============== 清理相关 ==============
docker system prune                     # 清理未使用资源
docker image prune                      # 清理未使用镜像
docker volume prune                     # 清理未使用卷

# ============== 指定配置文件 ==============
docker-compose -f docker-compose.dev.yml up -d    # 开发环境
docker-compose -f docker-compose.prod.yml up -d   # 生产环境
```

---

## 🎯 推荐工作流程

### 日常开发流程

```powershell
# 1. 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 2. 查看日志确认启动成功
docker-compose -f docker-compose.dev.yml logs -f
# 看到 "startup complete" 后按 Ctrl+C

# 3. 开始编码（修改代码自动生效）
code main.py

# 4. 测试
curl http://localhost:8000/api

# 5. 结束工作，停止容器
docker-compose -f docker-compose.dev.yml stop
```

### 生产部署流程

```powershell
# 1. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 3. 验证部署
docker-compose -f docker-compose.prod.yml ps
curl http://localhost/health

# 4. 监控日志
docker-compose -f docker-compose.prod.yml logs -f

# 5. 定期备份数据
Copy-Item data\bookstore.db backup\
```

---

**🎉 恭喜！你已经掌握了 Docker 部署的所有操作！**
