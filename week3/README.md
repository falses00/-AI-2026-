# 📘 第3周：MCP协议深度剖析

> **学习目标**：理解MCP（Model Context Protocol）协议，使用FastMCP构建自己的工具服务器

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解MCP协议的核心概念
- ✅ 使用FastMCP构建MCP Server
- ✅ 将MCP Server与Claude Desktop集成
- ✅ 完成MCP文件系统项目

---

## 📚 学习路径

### Day 1-2：MCP协议入门

#### 📖 教程材料
- [MCP协议入门](./tutorials/01_mcp_introduction.md) ✅

#### 🎬 推荐视频（B站）
- [MCP协议完全指南 - AI进化论](https://www.bilibili.com/video/BV1ZhDRYgEnM) ⭐推荐
- [什么是MCP？10分钟理解 - AI工程化](https://www.bilibili.com/video/BV1Lw4m1a7YS)
- [Claude Desktop + MCP实战 - 技术宅阿豪](https://www.bilibili.com/video/BV1dR4y1M7Dk)

---

### Day 3-4：MCP Server开发

#### 📖 实战项目
- [MCP文件系统服务器](./projects/mcp_filesystem/) ✅

#### 🎬 推荐视频（B站）
- [从零构建MCP Server - DataWhale](https://www.bilibili.com/video/BV1mk4y1U7xP)
- [FastMCP框架实战 - 码农高天](https://www.bilibili.com/video/BV1Nm4y1S7Rn)

**运行项目**：
```bash
cd week3/projects/mcp_filesystem
pip install fastmcp
python mcp_server.py
```

---

### Day 5-7：集成与实践

- 将MCP Server与Claude Desktop集成
- 测试工具调用功能
- 扩展更多工具

---

## 🚀 实战项目

### 项目：MCP文件系统服务器

**目标**：构建一个MCP服务器，让Claude能够操作本地文件

**功能**：
- 📁 列出目录文件
- 📄 读取文件内容
- 🔍 搜索文件
- 📝 写入文件

**项目地址**：[projects/mcp_filesystem/](./projects/mcp_filesystem/)

---

## 📊 学习检查清单

### MCP基础
- [ ] 理解MCP协议的作用
- [ ] 理解Host、Client、Server的关系
- [ ] 理解JSON-RPC 2.0协议

### MCP Server开发
- [ ] 能够使用FastMCP创建Server
- [ ] 能够定义工具（Tool）
- [ ] 能够处理工具调用

### Claude集成
- [ ] 能够配置Claude Desktop
- [ ] 能够测试MCP Server功能

---

## 🎁 学习资源

### 📚 官方文档
- [MCP官方文档](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)

### 📺 B站推荐视频
- MCP协议完全指南 - AI进化论
- MCP工具开发完整教程 - AI进化论

---

## ❓ 常见问题

### Q1: MCP和Function Calling有什么区别？
**A**: MCP是一个标准协议，让不同的AI应用都能调用相同的工具。Function Calling是特定API的功能，每个API实现不同。

### Q2: 为什么要用MCP？
**A**: MCP实现了工具的标准化和复用。写一次MCP Server，可以被Claude、Cursor等多个AI应用使用。

### Q3: MCP Server怎么部署？
**A**: 开发阶段本地运行即可。生产环境可以部署为独立服务。

---

## 🎯 下一步

完成本周学习后，你已经掌握了AI工程师的核心技能！

继续学习：
- Week 4-6: RAG系统开发
- Week 7-9: 智能体开发
- Week 10-12: 企业级应用

---

**记住：MCP是AI工程的未来，掌握它将让你在行业中脱颖而出！💪**
