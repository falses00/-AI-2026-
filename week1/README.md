# 📘 第1周：Python高级特性 + AI工程环境

> **学习目标**：掌握异步编程、类型验证、FastAPI框架和Docker容器化，为构建高性能AI应用做准备

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解并使用Python异步编程（`asyncio`）
- ✅ 使用Pydantic进行数据验证和建模
- ✅ 使用FastAPI构建RESTful API
- ✅ 使用Docker容器化部署应用
- ✅ 完成2个完整的实战项目

---

## 📚 学习路径

### Day 1-2：Python异步编程基础

#### 📖 教程材料
- [异步编程核心概念](./tutorials/01_async_basics.md)
- [asyncio实战指南](./tutorials/02_asyncio_practical.md)
- [aiohttp并发请求](./tutorials/03_aiohttp.md)

#### 🎬 推荐视频
- [Python Asyncio 完整教程（中文）](https://www.youtube.com/watch?v=t5Bo1Je9EmE)

#### 💻 练习题
- [exercises/async_exercises.py](./exercises/async_exercises.py)

---

### Day 3-4：Pydantic与FastAPI基础

#### 📖 教程材料
- [Pydantic数据验证](./tutorials/04_pydantic_basics.md)
- [FastAPI快速入门](./tutorials/05_fastapi_quickstart.md)
- [FastAPI请求与响应](./tutorials/06_fastapi_request_response.md)

#### 🎬 推荐视频
- [FastAPI完整教程（中文）](https://www.bilibili.com/video/BV1sL4y1R7MK/)

#### 💻 练习题
- [exercises/pydantic_exercises.py](./exercises/pydantic_exercises.py)
- [exercises/fastapi_exercises.py](./exercises/fastapi_exercises.py)

---

### Day 5-6：Docker容器化基础

#### 📖 教程材料
- [Docker核心概念](./tutorials/07_docker_basics.md)
- [编写Dockerfile](./tutorials/08_dockerfile.md)
- [Docker Compose入门](./tutorials/09_docker_compose.md)

#### 🎬 推荐视频
- [Docker从入门到实践（中文）](https://www.bilibili.com/video/BV1og4y1q7M4/)

#### 💻 练习题
- [exercises/docker_exercises.md](./exercises/docker_exercises.md)

---

### Day 7：复习与总结

- 回顾本周所有教程
- 完成所有练习题
- 准备实战项目

---

## 🚀 实战项目

### 项目1：FastAPI结构化输出服务

**目标**：构建一个API服务，接受用户输入并返回结构化的JSON数据

**技能点**：
- FastAPI路由设计
- Pydantic模型定义
- 数据验证与错误处理
- 自动文档生成

**详细说明**：[projects/project1_structured_api/](./projects/project1_structured_api/)

**预计时间**：4-6小时

---

### 项目2：Docker部署实战

**目标**：将项目1的API服务Docker化并成功运行

**技能点**：
- 编写Dockerfile
- 构建Docker镜像
- 运行容器
- 环境变量配置

**详细说明**：[projects/project2_docker_deployment/](./projects/project2_docker_deployment/)

**预计时间**：3-5小时

---

## 📊 学习检查清单

完成以下清单，确保你掌握了本周的核心内容：

### Python异步编程
- [ ] 理解协程（coroutine）的概念
- [ ] 能够使用`async def`定义异步函数
- [ ] 能够使用`await`等待异步操作
- [ ] 理解事件循环（Event Loop）
- [ ] 能够使用`asyncio.gather()`并发执行多个任务
- [ ] 能够使用`aiohttp`发起异步HTTP请求

### Pydantic
- [ ] 理解`BaseModel`的作用
- [ ] 能够定义包含类型注解的模型
- [ ] 能够使用Field进行字段验证
- [ ] 理解数据序列化与反序列化
- [ ] 能够处理嵌套模型

### FastAPI
- [ ] 能够创建基本的FastAPI应用
- [ ] 能够定义GET、POST、PUT、DELETE路由
- [ ] 能够使用路径参数和查询参数
- [ ] 能够使用Pydantic模型定义请求体
- [ ] 能够访问自动生成的Swagger文档
- [ ] 理解依赖注入的基本概念

### Docker
- [ ] 理解镜像（Image）和容器（Container）的区别
- [ ] 能够编写基本的Dockerfile
- [ ] 能够构建Docker镜像（`docker build`）
- [ ] 能够运行Docker容器（`docker run`）
- [ ] 能够查看运行中的容器（`docker ps`）
- [ ] 能够使用`docker-compose.yml`定义多容器应用

---

## 🎁 学习资源

### 📄 速查表
- [Python Asyncio速查表](../resources/cheatsheets/asyncio_cheatsheet.md)
- [Pydantic速查表](../resources/cheatsheets/pydantic_cheatsheet.md)
- [FastAPI速查表](../resources/cheatsheets/fastapi_cheatsheet.md)
- [Docker命令速查表](../resources/cheatsheets/docker_cheatsheet.md)

### 📚 官方文档
- [Python Asyncio官方文档](https://docs.python.org/3/library/asyncio.html)
- [Pydantic官方文档](https://docs.pydantic.dev/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Docker官方文档](https://docs.docker.com/)

### 🌐 社区资源
- [FastAPI GitHub仓库](https://github.com/tiangolo/fastapi)
- [Awesome FastAPI资源列表](https://github.com/mjhea0/awesome-fastapi)

---

## ❓ 常见问题（FAQ）

### Q1: 异步编程什么时候用？
**A**: 当你的程序需要等待I/O操作（如网络请求、文件读写）时使用。对于CPU密集型任务，使用多进程更合适。

### Q2: FastAPI和Flask有什么区别？
**A**: FastAPI基于异步，性能更高；自带数据验证（Pydantic）；自动生成API文档；更适合构建现代AI应用。

### Q3: 为什么要用Docker？
**A**: Docker确保"在我机器上能运行"的问题不再出现。它让部署更简单、环境更一致。

### Q4: 学习遇到困难怎么办？
**A**: 
1. 先Google搜索错误信息
2. 查看官方文档
3. 在Stack Overflow提问
4. 使用ChatGPT辅助理解
5. 不要放弃，编程就是不断试错的过程！

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 2: 大模型API深度控制](../week2/README.md)

---

**记住：每天进步一点点，坚持就是胜利！💪**
