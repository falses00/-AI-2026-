# 🐳 Docker 完全部署指南

> **从零开始的 Windows Docker 部署教程 - 图书管理系统**
>
> 适用环境：Windows 10/11 + Docker Desktop

---

## 📑 目录导航

| 章节 | 内容 | 适合谁 |
|------|------|--------|
| [第一章](#第一章-docker-基础概念) | Docker 基础概念 | 零基础入门 |
| [第二章](#第二章-环境准备与安装) | 环境准备与安装 | 首次安装 Docker |
| [第三章](#第三章-快速启动项目) | 快速启动项目 | 想快速运行 |
| [第四章](#第四章-详细部署流程) | 详细部署流程 | 想深入理解 |
| [第五章](#第五章-日常使用指南) | 日常使用指南 | 日常开发 |
| [第六章](#第六章-故障排查) | 故障排查 | 遇到问题 |
| [附录](#附录-命令速查表) | 命令速查表 | 快速参考 |

---

## 第一章 Docker 基础概念

### 1.1 什么是 Docker？

Docker 是一个容器化平台，可以把你的应用和所有依赖打包成一个"容器"，在任何安装了 Docker 的机器上运行。

```
┌─────────────────────────────────────────────────────────┐
│  传统方式                     Docker 方式               │
├─────────────────────────────────────────────────────────┤
│  你的电脑 → 服务器            你的电脑 → 服务器         │
│  ❌ Python 版本不同           ✅ 完全相同的环境         │
│  ❌ 依赖包冲突                ✅ 隔离的运行环境         │
│  ❌ 配置繁琐                  ✅ 一条命令启动           │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心概念图解

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker 核心概念                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 Dockerfile        →   📦 镜像 (Image)   →   🏃 容器    │
│  (菜谱/配方)               (蛋糕模具)           (烤出的蛋糕) │
│                                                             │
│  描述如何构建环境          可复用的模板          运行中的实例 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 docker-compose.yml  =  同时管理多个容器的配置文件        │
│  (比如同时启动 API + 数据库 + Nginx)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 本项目的 Docker 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      生产环境架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户请求 (HTTP)                                           │
│        ↓                                                    │
│   ┌─────────────┐                                          │
│   │   Nginx     │  ← 端口 80/443                            │
│   │  (反向代理)  │                                          │
│   └──────┬──────┘                                          │
│          ↓                                                  │
│   ┌─────────────┐                                          │
│   │  FastAPI    │  ← 端口 8000 (内部)                       │
│   │   (API)     │                                          │
│   └──────┬──────┘                                          │
│          ↓                                                  │
│   ┌─────────────┐                                          │
│   │   SQLite    │  ← 数据持久化到 ./data 目录               │
│   │  (数据库)   │                                          │
│   └─────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 第二章 环境准备与安装

### 2.1 系统要求检查

在安装 Docker 之前，请确认你的系统满足以下要求：

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10 (版本 2004+) | Windows 11 |
| 内存 | 4 GB | 8 GB+ |
| 磁盘空间 | 10 GB | 20 GB+ |
| CPU | 支持虚拟化 | 多核 CPU |

**检查 Windows 版本：**

```powershell
# 打开 PowerShell，运行以下命令
winver
# 或者
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

### 2.2 启用 Windows 功能

Docker Desktop 需要 WSL2（Windows Subsystem for Linux）支持。

**步骤 1：以管理员身份打开 PowerShell**

```
按 Win + X → 选择 "Windows PowerShell (管理员)" 或 "终端(管理员)"
```

**步骤 2：启用 WSL 功能**

```powershell
# 启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

**步骤 3：重启电脑**

```powershell
# 重启电脑使更改生效
Restart-Computer
```

**步骤 4：设置 WSL 默认版本**

重启后，再次以管理员身份打开 PowerShell：

```powershell
# 设置 WSL 2 为默认版本
wsl --set-default-version 2

# 更新 WSL（如果需要）
wsl --update
```

### 2.3 安装 Docker Desktop

**步骤 1：下载 Docker Desktop**

访问官方下载页面：https://www.docker.com/products/docker-desktop

或直接下载链接：
```
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

**步骤 2：安装 Docker Desktop**

1. 双击下载的 `Docker Desktop Installer.exe`
2. 在安装向导中，确保勾选：
   - ✅ **Use WSL 2 instead of Hyper-V** (推荐)
   - ✅ **Add shortcut to desktop**
3. 点击 **Install** 开始安装
4. 安装完成后，点击 **Close and restart**

**步骤 3：首次配置 Docker Desktop**

1. 重启后，从开始菜单或桌面打开 **Docker Desktop**
2. 接受服务条款
3. 等待 Docker Engine 启动（右下角鲸鱼图标变绿）
4. （可选）登录 Docker Hub 账号

### 2.4 验证安装成功

打开 PowerShell，运行以下命令：

```powershell
# 检查 Docker 版本
docker --version
# 预期输出：Docker version 24.x.x, build xxxxxxx

# 检查 Docker Compose 版本
docker compose version
# 预期输出：Docker Compose version v2.x.x

# 运行测试容器
docker run hello-world
# 预期输出：Hello from Docker! ...
```

> [!TIP]
> 如果 `docker run hello-world` 成功显示欢迎信息，说明 Docker 安装完成！

### 2.5 Docker Desktop 配置优化（可选）

打开 Docker Desktop → 设置（齿轮图标）：

**Resources → WSL Integration：**
- 确保 "Enable integration with my default WSL distro" 已启用

**Resources → Advanced：**
- Memory: 设置为系统内存的 50%（如 8GB 电脑设置 4GB）
- CPUs: 设置为 CPU 核心数的一半

**Docker Engine：**
添加镜像加速（中国大陆用户推荐）：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

---

## 第三章 快速启动项目

> 如果你只想快速运行项目，按照本章操作即可。

### 3.1 一键启动（开发环境）

```powershell
# 步骤 1：进入项目目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 步骤 2：启动开发环境
docker compose -f docker-compose.dev.yml up -d

# 步骤 3：查看状态
docker compose -f docker-compose.dev.yml ps

# 步骤 4：访问应用
# 浏览器打开：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 3.2 一键启动（生产环境）

```powershell
# 步骤 1：进入项目目录
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 步骤 2：启动生产环境（含 Nginx）
docker compose -f docker-compose.prod.yml up -d

# 步骤 3：查看状态
docker compose -f docker-compose.prod.yml ps

# 步骤 4：访问应用
# 浏览器打开：http://localhost
# API 文档：http://localhost/docs
```

### 3.3 一键停止

```powershell
# 停止开发环境
docker compose -f docker-compose.dev.yml down

# 停止生产环境
docker compose -f docker-compose.prod.yml down
```

> [!IMPORTANT]
> **首次启动会比较慢**（需要下载基础镜像），请耐心等待。后续启动会很快。

---

## 第四章 详细部署流程

### 4.1 项目文件说明

进入项目目录后，你会看到以下 Docker 相关文件：

```
project1_structured_api/
├── 📄 Dockerfile              # 生产环境镜像配置
├── 📄 Dockerfile.dev          # 开发环境镜像配置
├── 📄 docker-compose.yml      # 基础配置
├── 📄 docker-compose.dev.yml  # 开发环境配置
├── 📄 docker-compose.prod.yml # 生产环境配置（含 Nginx）
├── 📁 nginx/                  # Nginx 配置目录
│   ├── nginx.conf            # Nginx 主配置
│   └── conf.d/               # 站点配置
├── 📁 data/                   # 数据持久化目录
├── 📄 main.py                 # FastAPI 主程序
├── 📄 requirements.txt        # Python 依赖
└── ...
```

### 4.2 理解配置文件

#### Dockerfile（生产环境）

```dockerfile
# 使用 Python 3.12 官方精简镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**逐行解释：**
| 行 | 作用 |
|----|----|
| `FROM python:3.12-slim` | 使用官方 Python 镜像作为基础 |
| `WORKDIR /app` | 设置容器内的工作目录 |
| `COPY requirements.txt .` | 复制依赖文件到容器 |
| `RUN pip install ...` | 安装 Python 依赖 |
| `COPY . .` | 复制项目所有文件 |
| `EXPOSE 8000` | 声明容器使用 8000 端口 |
| `CMD [...]` | 容器启动时执行的命令 |

#### docker-compose.dev.yml（开发环境）

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev      # 使用开发版 Dockerfile
    container_name: bookstore-dev
    ports:
      - "8000:8000"                   # 映射端口：主机:容器
    volumes:
      - .:/app                        # 挂载代码目录（热重载）
      - /app/__pycache__              # 排除缓存目录
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG=True
      - RELOAD=True
    restart: unless-stopped
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge
```

**关键配置说明：**
| 配置 | 说明 |
|------|------|
| `volumes: - .:/app` | 将本地代码挂载到容器，修改代码立即生效 |
| `ports: "8000:8000"` | 将容器的 8000 端口映射到主机的 8000 端口 |
| `restart: unless-stopped` | 容器意外退出时自动重启 |

### 4.3 开发环境部署详解

**步骤 1：进入项目目录**

```powershell
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# 确认位置
pwd
# 输出：i:\Study FastAPI\week1\projects\project1_structured_api
```

**步骤 2：创建必要目录**

```powershell
# 创建数据目录（如果不存在）
if (!(Test-Path "data")) { New-Item -ItemType Directory -Path "data" }

# 创建 nginx 日志目录（如果不存在）
if (!(Test-Path "nginx\logs")) { New-Item -ItemType Directory -Path "nginx\logs" -Force }
```

**步骤 3：构建并启动**

```powershell
# 构建镜像并启动容器
docker compose -f docker-compose.dev.yml up -d --build

# 参数说明：
# -f docker-compose.dev.yml  指定配置文件
# up                         创建并启动容器
# -d                         后台运行
# --build                    强制重新构建镜像
```

**预期输出：**
```
[+] Building 45.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile.dev
 => [1/6] FROM docker.io/library/python:3.12-slim
 => [2/6] WORKDIR /app
 => ...
[+] Running 2/2
 ✔ Network project1_structured_api_dev-network  Created
 ✔ Container bookstore-dev                      Started
```

**步骤 4：验证启动成功**

```powershell
# 查看容器状态
docker compose -f docker-compose.dev.yml ps

# 预期输出（状态应为 running 或 healthy）：
# NAME            IMAGE                   STATUS
# bookstore-dev   project1_api:latest     Up 2 minutes (healthy)
```

**步骤 5：查看日志**

```powershell
# 查看启动日志
docker compose -f docker-compose.dev.yml logs

# 实时跟踪日志（按 Ctrl+C 退出）
docker compose -f docker-compose.dev.yml logs -f
```

**预期日志内容：**
```
bookstore-dev  | INFO:     Started server process [1]
bookstore-dev  | INFO:     Uvicorn running on http://0.0.0.0:8000
bookstore-dev  | INFO:     Application startup complete.
```

**步骤 6：测试访问**

```powershell
# 命令行测试
curl http://localhost:8000/api

# 或在浏览器中打开：
# - 主页：http://localhost:8000
# - API 文档：http://localhost:8000/docs
```

### 4.4 生产环境部署详解

生产环境增加了 Nginx 作为反向代理，提供更好的性能和安全性。

**步骤 1：检查 Nginx 配置**

```powershell
# 确认 nginx 配置文件存在
Test-Path "nginx\nginx.conf"
Test-Path "nginx\conf.d\bookstore.conf"
```

**步骤 2：构建生产镜像**

```powershell
# 先构建镜像（不启动）
docker compose -f docker-compose.prod.yml build

# 预期输出：
# [+] Building 67.3s (12/12) FINISHED
#  => [api] exporting to image
```

**步骤 3：启动生产服务**

```powershell
# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 预期输出：
# [+] Running 3/3
#  ✔ Network app-network       Created
#  ✔ Container bookstore-api   Started
#  ✔ Container bookstore-nginx Started
```

**步骤 4：验证所有服务**

```powershell
# 查看容器状态
docker compose -f docker-compose.prod.yml ps

# 预期输出：
# NAME              STATUS
# bookstore-api     Up (healthy)
# bookstore-nginx   Up (healthy)

# 查看端口映射
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 预期输出：
# NAMES             PORTS
# bookstore-nginx   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
# bookstore-api     8000/tcp
```

**步骤 5：测试生产环境**

```powershell
# 通过 Nginx 访问（注意：端口 80，不需要写端口号）
curl http://localhost/api

# 浏览器访问：
# - 主页：http://localhost
# - API 文档：http://localhost/docs
# - 健康检查：http://localhost/health
```

> [!NOTE]
> **开发环境 vs 生产环境区别：**
> - 开发环境：直接访问 `localhost:8000`，代码修改自动重载
> - 生产环境：通过 Nginx 访问 `localhost`，更稳定高效

---

## 第五章 日常使用指南

### 5.1 启动与停止

```powershell
# ===== 开发环境 =====
# 启动
docker compose -f docker-compose.dev.yml up -d

# 停止（保留容器）
docker compose -f docker-compose.dev.yml stop

# 停止并删除容器（推荐）
docker compose -f docker-compose.dev.yml down

# ===== 生产环境 =====
# 启动
docker compose -f docker-compose.prod.yml up -d

# 停止
docker compose -f docker-compose.prod.yml down
```

### 5.2 查看状态和日志

```powershell
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看指定项目的容器
docker compose -f docker-compose.dev.yml ps

# 查看日志（最近 100 行）
docker compose -f docker-compose.dev.yml logs --tail=100

# 实时跟踪日志
docker compose -f docker-compose.dev.yml logs -f

# 只看特定服务的日志
docker compose -f docker-compose.dev.yml logs api
```

### 5.3 重启和重建

```powershell
# 重启所有服务
docker compose -f docker-compose.dev.yml restart

# 重启单个服务
docker compose -f docker-compose.dev.yml restart api

# 重建镜像并重启（代码有重大更新时）
docker compose -f docker-compose.dev.yml up -d --build

# 强制重建（清除缓存）
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

### 5.4 进入容器调试

```powershell
# 进入容器的 Shell
docker exec -it bookstore-dev sh

# 在容器内执行命令后退出
# ls              # 查看文件
# python --version # 检查 Python 版本
# pip list        # 查看已安装的包
# exit            # 退出容器

# 不进入容器，直接执行命令
docker exec bookstore-dev python --version
docker exec bookstore-dev pip list
```

### 5.5 资源监控

```powershell
# 实时监控容器资源使用
docker stats

# 输出示例：
# CONTAINER      CPU %   MEM USAGE / LIMIT    NET I/O
# bookstore-dev  0.5%    50MiB / 2GiB         1.2kB / 800B

# 只看一次（不持续更新）
docker stats --no-stream

# 查看 Docker 占用的磁盘空间
docker system df
```

### 5.6 数据备份与恢复

```powershell
# 备份数据库文件
Copy-Item "data\bookstore.db" "backup\bookstore_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"

# 从容器复制文件到本地
docker cp bookstore-dev:/app/data/bookstore.db ./backup.db

# 从本地复制文件到容器
docker cp ./backup.db bookstore-dev:/app/data/bookstore.db
```

### 5.7 清理资源

```powershell
# 清理未使用的资源（推荐定期执行）
docker system prune

# 清理所有未使用的镜像
docker image prune -a

# 清理未使用的卷（⚠️ 慎用，可能丢失数据）
docker volume prune

# 查看当前占用空间
docker system df
```

---

## 第六章 故障排查

### 6.1 Docker Desktop 未运行

**症状：**
```
error during connect: This error may indicate that the docker daemon is not running
```

**解决方法：**
1. 检查任务栏右下角是否有 Docker 鲸鱼图标
2. 如果没有，从开始菜单启动 Docker Desktop
3. 等待图标变绿（表示启动完成）
4. 如果图标是红色/黄色，打开 Docker Desktop 查看错误信息

### 6.2 端口被占用

**症状：**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**解决方法：**

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 输出示例：
# TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    12345

# 找到进程名
tasklist | findstr 12345

# 结束进程（把 12345 换成你的 PID）
taskkill /PID 12345 /F

# 或者修改 docker-compose 中的端口映射
# 把 "8000:8000" 改成 "8001:8000"
```

### 6.3 容器启动后立即退出

**症状：** 容器状态显示 `Exited (1)` 或类似

**排查步骤：**

```powershell
# 1. 查看容器日志
docker compose -f docker-compose.dev.yml logs

# 2. 前台运行查看详细错误
docker compose -f docker-compose.dev.yml up

# 常见原因及解决：
# - 代码语法错误 → 检查 Python 代码
# - 依赖缺失 → 检查 requirements.txt
# - 配置错误 → 检查 docker-compose.yml 语法
```

### 6.4 无法访问服务

**症状：** `curl http://localhost:8000` 超时或拒绝连接

**排查步骤：**

```powershell
# 1. 确认容器在运行
docker ps

# 2. 检查端口映射
docker port bookstore-dev

# 3. 从容器内部测试
docker exec bookstore-dev curl http://localhost:8000/api

# 4. 检查 Windows 防火墙
# 可能需要添加入站规则允许 8000 端口

# 5. 重启 Docker Desktop
# 右击任务栏 Docker 图标 → Restart
```

### 6.5 镜像构建失败

**症状：** `docker build` 报错

**常见问题及解决：**

```powershell
# 问题 1：网络超时（无法下载依赖）
# 解决：使用国内镜像源，修改 Dockerfile：
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 问题 2：磁盘空间不足
# 解决：清理未使用的镜像
docker system prune -a

# 问题 3：文件不存在
# 解决：确认 Dockerfile 中 COPY 的文件存在
ls requirements.txt
ls main.py
```

### 6.6 Nginx 502 Bad Gateway

**症状：** 通过 Nginx 访问返回 502 错误

**排查步骤：**

```powershell
# 1. 检查 API 容器是否运行
docker ps | findstr bookstore-api

# 2. 检查 API 健康状态
docker compose -f docker-compose.prod.yml ps

# 3. 查看 Nginx 错误日志
Get-Content nginx\logs\error.log -Tail 20

# 4. 测试 API 容器内部
docker exec bookstore-api curl http://localhost:8000/api

# 5. 重启所有服务
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### 6.7 数据丢失

**症状：** 重启后数据消失

**原因：** 未正确配置数据卷挂载

**检查方法：**

```powershell
# 检查卷挂载配置
docker inspect bookstore-dev --format='{{json .Mounts}}'

# 确认 docker-compose.yml 中有：
# volumes:
#   - ./data:/app/data

# 确认本地 data 目录存在
ls data
```

---

## 附录 命令速查表

### A.1 Docker 基础命令

| 命令 | 说明 |
|------|------|
| `docker --version` | 查看 Docker 版本 |
| `docker ps` | 查看运行中的容器 |
| `docker ps -a` | 查看所有容器 |
| `docker images` | 查看所有镜像 |
| `docker stats` | 实时监控资源 |
| `docker system df` | 查看磁盘占用 |
| `docker system prune` | 清理未使用资源 |

### A.2 Docker Compose 命令

| 命令 | 说明 |
|------|------|
| `docker compose up -d` | 启动服务（后台） |
| `docker compose up` | 启动服务（前台） |
| `docker compose down` | 停止并删除容器 |
| `docker compose stop` | 停止容器 |
| `docker compose restart` | 重启容器 |
| `docker compose ps` | 查看服务状态 |
| `docker compose logs` | 查看日志 |
| `docker compose logs -f` | 实时跟踪日志 |
| `docker compose build` | 构建镜像 |
| `docker compose up -d --build` | 重建并启动 |
| `docker compose exec api sh` | 进入容器 |

### A.3 本项目专用命令

```powershell
# ============ 进入项目目录 ============
cd "i:\Study FastAPI\week1\projects\project1_structured_api"

# ============ 开发环境 ============
docker compose -f docker-compose.dev.yml up -d        # 启动
docker compose -f docker-compose.dev.yml down         # 停止
docker compose -f docker-compose.dev.yml logs -f      # 日志
docker compose -f docker-compose.dev.yml ps           # 状态

# ============ 生产环境 ============
docker compose -f docker-compose.prod.yml up -d       # 启动
docker compose -f docker-compose.prod.yml down        # 停止
docker compose -f docker-compose.prod.yml logs -f     # 日志
docker compose -f docker-compose.prod.yml ps          # 状态

# ============ 通用操作 ============
docker exec -it bookstore-dev sh                      # 进入开发容器
docker exec -it bookstore-api sh                      # 进入生产容器
```

### A.4 常用 URL

| 环境 | URL | 说明 |
|------|-----|------|
| 开发 | http://localhost:8000 | API 主页 |
| 开发 | http://localhost:8000/docs | Swagger 文档 |
| 开发 | http://localhost:8000/redoc | ReDoc 文档 |
| 生产 | http://localhost | 通过 Nginx 访问 |
| 生产 | http://localhost/docs | Swagger 文档 |
| 生产 | http://localhost/health | 健康检查 |

---

## 🎉 结语

恭喜你完成了 Docker 部署学习！现在你已经掌握了：

- ✅ Docker 基础概念
- ✅ Windows 环境下安装 Docker
- ✅ 开发环境和生产环境部署
- ✅ 日常使用和维护
- ✅ 常见问题排查

**下一步建议：**
1. 多练习日常命令，形成肌肉记忆
2. 尝试修改配置，理解每个参数的作用
3. 学习 Docker 网络和存储的高级知识

如有问题，欢迎随时提问！

---

> 📅 最后更新：2026-01-30
> 📝 作者：AI Assistant
