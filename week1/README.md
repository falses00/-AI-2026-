# 📘 第1周：Python高级特性 + AI工程环境

> **学习目标**：掌握异步编程、类型验证、FastAPI框架和Docker容器化，为构建高性能AI应用做准备

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解并使用Python异步编程（`asyncio`）
- ✅ 使用Pydantic进行数据验证和建模
- ✅ 使用FastAPI构建RESTful API
- ✅ 使用Docker容器化部署应用
- ✅ 完成实战项目

---

## 📚 学习路径

### Day 1-2：Python异步编程基础

#### 📖 教程材料
- [异步编程核心概念](./tutorials/01_async_basics.md) ✅

#### 🎬 推荐视频（B站）
- [Python协程asyncio详解 - 码农高天](https://www.bilibili.com/video/BV1YS4y1D7BA)
- [Python异步编程入门到精通 - 黑马程序员](https://www.bilibili.com/video/BV1184y1V7GV)

#### 💻 练习题
- [exercises/async_exercises.py](./exercises/async_exercises.py) ✅

---

### Day 3-4：Pydantic与FastAPI基础

#### 📖 教程材料
- [Pydantic数据验证](./tutorials/04_pydantic_basics.md) ✅
- [FastAPI快速入门](./tutorials/05_fastapi_quickstart.md) ✅

#### 🎬 推荐视频（B站）
- [FastAPI从入门到精通 - 尚硅谷](https://www.bilibili.com/video/BV1rR4y1b7G5)
- [FastAPI零基础入门 - 千锋教育](https://www.bilibili.com/video/BV1iN4y1e7BR)

#### 💻 项目实践
- [图书管理API项目](./projects/project1_structured_api/) ✅

---

### Day 5-6：Docker容器化基础

#### 📖 教程材料
- [Docker核心概念](./tutorials/07_docker_basics.md) ✅

#### 🎬 推荐视频（B站）
- [尚硅谷2024新版3小时速通Docker](https://www.bilibili.com/video/BV1Yh4y1Y7E1) ⭐推荐
- [Docker从入门到实践](https://www.bilibili.com/video/BV1og4y1q7M4)

---

### Day 7：复习与总结

- 回顾本周所有教程
- 完成所有练习题
- 运行实战项目

---

## 🚀 实战项目

### 项目：FastAPI图书管理API

**目标**：构建一个完整的RESTful API，实现图书的增删改查

**技能点**：
- FastAPI路由设计
- Pydantic模型定义
- 数据验证与错误处理
- 自动文档生成

**项目地址**：[projects/project1_structured_api/](./projects/project1_structured_api/)

**运行方式**：
```bash
cd week1/projects/project1_structured_api
uvicorn main:app --reload
# 访问 http://localhost:8000/docs
```

---

## 📊 学习检查清单

### Python异步编程
- [ ] 理解协程（coroutine）的概念
- [ ] 能够使用`async def`定义异步函数
- [ ] 能够使用`await`等待异步操作
- [ ] 能够使用`asyncio.gather()`并发执行多个任务

### Pydantic
- [ ] 理解`BaseModel`的作用
- [ ] 能够定义包含类型注解的模型
- [ ] 能够使用Field进行字段验证

### FastAPI
- [ ] 能够创建基本的FastAPI应用
- [ ] 能够定义GET、POST、PUT、DELETE路由
- [ ] 能够访问自动生成的Swagger文档

### Docker
- [ ] 理解镜像（Image）和容器（Container）的区别
- [ ] 能够编写基本的Dockerfile
- [ ] 能够构建和运行Docker容器

---

## 🎁 学习资源

### 📄 速查表
- [Python Asyncio速查表](../resources/cheatsheets/asyncio_cheatsheet.md)
- [FastAPI速查表](../resources/cheatsheets/fastapi_cheatsheet.md)

### 📚 官方文档
- [Python Asyncio官方文档](https://docs.python.org/zh-cn/3/library/asyncio.html)
- [FastAPI官方文档（中文）](https://fastapi.tiangolo.com/zh/)
- [Pydantic官方文档](https://docs.pydantic.dev/)
- [Docker官方文档](https://docs.docker.com/)

---

## ❓ 常见问题

### Q1: 异步编程什么时候用？
**A**: 当你的程序需要等待I/O操作（如网络请求、文件读写）时使用。

### Q2: FastAPI和Flask有什么区别？
**A**: FastAPI性能更高、自带数据验证、自动生成API文档。

### Q3: 为什么要用Docker？
**A**: 确保开发环境和生产环境一致，解决"在我电脑上能跑"的问题。

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 2: 大模型API深度控制](../week2/README.md)

---

**记住：每天进步一点点，坚持就是胜利！💪**
