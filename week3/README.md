# 📘 第3周：MCP协议深度剖析

> **学习目标**：掌握Model Context Protocol (MCP)，学会构建MCP Server并与Claude集成

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解MCP协议的设计理念和架构
- ✅ 掌握JSON-RPC 2.0通信协议
- ✅ 使用FastMCP SDK构建MCP Server
- ✅ 实现Tool、Resource、Prompt三大核心功能
- ✅ 将MCP Server与Claude Desktop集成
- ✅ 完成2个实战项目

---

## 📚 学习路径

### Day 1-2：MCP协议基础

#### 📖 教程材料
- [MCP协议简介](./tutorials/01_mcp_introduction.md)
- [JSON-RPC 2.0详解](./tutorials/02_json_rpc.md)
- [MCP核心概念](./tutorials/03_mcp_concepts.md)

#### 🎬 推荐视频
- [MCP in 10 Minutes](https://www.youtube.com/watch?v=XXX)

#### 💻 练习题
- [exercises/json_rpc_exercises.py](./exercises/json_rpc_exercises.py)

---

### Day 3-4：使用FastMCP构建Server

#### 📖 教程材料
- [FastMCP快速入门](./tutorials/04_fastmcp_quickstart.md)
- [实现MCP Tools](./tutorials/05_mcp_tools.md)
- [实现MCP Resources](./tutorials/06_mcp_resources.md)
- [实现MCP Prompts](./tutorials/07_mcp_prompts.md)

#### 💻 练习题
- [exercises/fastmcp_exercises.py](./exercises/fastmcp_exercises.py)

---

### Day 5-6：Claude集成与调试

#### 📖 教程材料
- [配置Claude Desktop](./tutorials/08_claude_setup.md)
- [MCP Server调试技巧](./tutorials/09_debugging.md)
- [安全与权限管理](./tutorials/10_security.md)

#### 💻 练习题
- [exercises/integration_exercises.md](./exercises/integration_exercises.md)

---

### Day 7：复习与总结

- 回顾MCP三大核心组件
- 完成所有练习
- 准备实战项目

---

## 🚀 实战项目

### 项目5：MCP文件系统服务器

**目标**：构建一个MCP Server，向Claude暴露文件系统操作能力

**功能**：
- 🔍 文件搜索（按名称、类型）
- 📖 文件读取
- ✏️ 文件写入
- 📁 目录列表
- 📊 文件元数据获取

**技能点**：
- FastMCP框架
- Tool定义与实现
- Resource暴露
- 错误处理

**详细说明**：[projects/project5_mcp_filesystem/](./projects/project5_mcp_filesystem/)

**预计时间**：5-7小时

---

### 项目6：Claude集成测试

**目标**：将项目5的MCP Server接入Claude Desktop，实现完整对话

**测试场景**：
- Claude通过MCP搜索文件
- Claude读取并总结文件内容
- Claude创建新文件
- Claude分析项目结构

**技能点**：
- Claude Desktop配置
- MCP调试
- 工具调用验证
- 实际使用场景测试

**详细说明**：[projects/project6_claude_integration/](./projects/project6_claude_integration/)

**预计时间**：3-5小时

---

## 📊 学习检查清单

### MCP协议理解
- [ ] 理解MCP解决的"N×M问题"
- [ ] 了解MCP vs 传统API的区别
- [ ] 理解Client-Server架构
- [ ] 知道主流MCP Client（Claude、Cursor等）

### JSON-RPC 2.0
- [ ] 理解请求-响应格式
- [ ] 能够手写JSON-RPC请求
- [ ] 理解错误处理机制
- [ ] 能够使用调试工具测试

### MCP三大核心
- [ ] **Tool**: 能够定义和实现工具函数
- [ ] **Resource**: 能够暴露数据资源
- [ ] **Prompt**: 能够提供预设提示词

### FastMCP SDK
- [ ] 能够初始化FastMCP应用
- [ ] 能够使用装饰器注册工具
- [ ] 能够实现异步工具
- [ ] 能够处理工具参数验证

### Claude集成
- [ ] 能够配置claude_desktop_config.json
- [ ] 能够启动MCP Server
- [ ] 能够在Claude中测试工具
- [ ] 能够查看和分析日志

---

## 🎁 学习资源

### 📄 速查表
- [MCP协议速查表](../resources/cheatsheets/mcp_protocol_cheatsheet.md)
- [FastMCP API速查表](../resources/cheatsheets/fastmcp_cheatsheet.md)
- [Claude Desktop配置指南](../resources/cheatsheets/claude_config_cheatsheet.md)

### 📚 官方文档
- [MCP官方文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [Claude Desktop文档](https://claude.ai/desktop)

### 🌐 社区资源
- [Awesome MCP](https://github.com/punkpeye/awesome-mcp)
- [MCP Server示例](https://github.com/modelcontextprotocol/servers)

---

## ❓ 常见问题（FAQ）

### Q1: MCP和API有什么区别？
**A**: MCP是专为AI设计的协议，支持工具发现、上下文管理和双向通信。传统API需要手写集成代码。

### Q2: 为什么要学MCP？
**A**: MCP是2026年AI应用的标准化协议，企业级AI应用都在采用。掌握它是找工作的加分项。

### Q3: Claude Desktop如何调试MCP？
**A**: 
1. 查看日志文件（`~/Library/Logs/Claude/`）
2. 使用MCP Inspector工具
3. 在Server中添加print调试
4. 使用日志库记录详细信息

### Q4: MCP Server可以用其他语言吗？
**A**: 可以！MCP有Python、TypeScript、Go等多种SDK。本课程使用Python（FastMCP）。

---

## 🎯 第一阶段总结

完成第1-3周学习后，你已经掌握：

- ✅ Python异步编程
- ✅ FastAPI Web框架
- ✅ Pydantic数据验证
- ✅ Docker容器化
- ✅ OpenAI API调用
- ✅ MCP协议实现

**恭喜你完成第一阶段！🎉**

继续前往：

👉 [第二阶段：生产级RAG系统架构](../stage2/README.md)

---

**MCP是AI工程师的"新标准"，掌握它让你领先一步！💪**
