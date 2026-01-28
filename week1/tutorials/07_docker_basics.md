# 🐳 Docker 基础入门

> **学习目标**：理解容器化概念，学会用Docker部署Python应用

---

## 1. 为什么需要Docker？

**问题**："在我机器上能运行啊！" 😅

**解决**：Docker让环境一致，无论在哪运行都相同！

---

## 2. 核心概念

| 概念 | 类比 | 说明 |
|------|------|------|
| **镜像(Image)** | 安装包 | 应用的只读模板 |
| **容器(Container)** | 运行中的软件 | 镜像的运行实例 |
| **Dockerfile** | 安装说明书 | 构建镜像的脚本 |

---

## 3. 安装Docker

### Windows
下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 验证安装
```bash
docker --version
docker run hello-world
```

---

## 4. 编写Dockerfile

为FastAPI应用创建Dockerfile：

```dockerfile
# 使用Python基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. 构建和运行

### 构建镜像
```bash
docker build -t my-fastapi-app .
```

### 运行容器
```bash
docker run -d -p 8000:8000 my-fastapi-app
```

### 查看运行状态
```bash
docker ps
```

访问 http://localhost:8000 即可！

---

## 6. 常用命令速查

| 命令 | 说明 |
|------|------|
| `docker build -t name .` | 构建镜像 |
| `docker run -d -p 8000:8000 name` | 运行容器 |
| `docker ps` | 查看运行中容器 |
| `docker stop <id>` | 停止容器 |
| `docker logs <id>` | 查看日志 |
| `docker images` | 查看镜像列表 |

---

## 7. Docker Compose

多容器管理：

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
```

运行：`docker-compose up`

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 狂神说Java | Docker最新超详细版教程（推荐⭐） | https://www.bilibili.com/video/BV1og4y1q7M4 |
| 尚硅谷 | Docker入门到精通 | https://www.bilibili.com/video/BV1Ls411n7mx |

---

## 8. 继续学习

🎉 **恭喜！你已完成Week 1基础课程！**

📌 **Week 1 学习顺序**：
1. ✅ 异步编程核心概念
2. ✅ Pydantic数据验证
3. ✅ FastAPI快速入门
4. ✅ Docker基础入门（本教程）

在左侧菜单选择 **Week 2** 的教程继续学习大模型API！

---

**Docker = 一次构建，到处运行！💪**

