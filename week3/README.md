# 📘 第3周：MCP协议深度剖析

> **学习目标**：掌握MCP（Model Context Protocol）协议，开发MCP Server并与Claude Desktop集成

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解MCP协议的设计理念
- ✅ 使用FastMCP SDK开发MCP Server
- ✅ 定义Tools、Resources、Prompts
- ✅ 与Claude Desktop集成测试
- ✅ 构建实用的MCP工具服务

---

## 🤔 什么是MCP？

**MCP (Model Context Protocol)** 是Anthropic发布的开放协议，让AI模型能够安全地与外部系统交互：

```
┌─────────────┐     MCP协议      ┌─────────────┐
│   Claude    │ ◄───────────────► │  MCP Server │
│   Desktop   │    (JSON-RPC)     │  (你开发的) │
└─────────────┘                   └─────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  文件系统/数据库  │
                               │  API/任何资源    │
                               └─────────────────┘
```

### MCP vs Function Calling

| 对比项 | Function Calling | MCP |
|--------|------------------|-----|
| 标准化 | 各厂商实现不同 | 统一协议标准 |
| 运行位置 | 服务端执行 | 本地独立进程 |
| 安全性 | 取决于实现 | 内置安全机制 |
| 复用性 | 需要重复定义 | 一次开发多处使用 |

---

## 📚 学习路径

### Day 1：MCP协议基础

#### 📖 教程材料
- [MCP协议入门](./tutorials/01_mcp_introduction.md) ✅

**学习内容**：
- MCP架构与工作原理
- JSON-RPC 2.0通信协议
- 三大核心概念：Tool、Resource、Prompt
- 与Function Calling的对比

---

### Day 2：FastMCP快速上手

#### 📖 教程材料
- [FastMCP基础教程](./tutorials/02_fastmcp_basics.md) ✅

**学习内容**：
- FastMCP SDK安装
- 项目结构规范
- 第一个MCP Server
- 装饰器语法详解

#### 💻 快速示例
```python
from fastmcp import FastMCP

mcp = FastMCP("我的第一个MCP服务")

@mcp.tool()
def greet(name: str) -> str:
    """向用户打招呼"""
    return f"你好，{name}！"

if __name__ == "__main__":
    mcp.run()
```

---

### Day 3：Tool工具开发

#### 📖 教程材料
- [MCP Tools开发指南](./tutorials/03_mcp_tools.md) ✅

**学习内容**：
- 工具定义与参数
- 同步/异步工具
- 错误处理
- 安全性考虑

#### 💻 实战案例
```python
@mcp.tool()
def search_files(directory: str, pattern: str) -> list[str]:
    """搜索指定目录下匹配模式的文件"""
    import glob
    return glob.glob(f"{directory}/**/{pattern}", recursive=True)
```

---

### Day 4：Resource资源暴露

#### 📖 教程材料
- [MCP Resources开发指南](./tutorials/04_mcp_resources.md) ✅

**学习内容**：
- 资源URI设计
- 静态/动态资源
- 文件系统资源
- 数据库资源

#### 💻 实战案例
```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

### Day 5：Claude Desktop集成

#### 📖 教程材料
- [Claude Desktop集成教程](./tutorials/05_claude_integration.md) ✅

**学习内容**：
- Claude Desktop安装
- MCP Server配置
- 调试与日志
- 常见问题排查

#### 🔧 配置示例
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["D:/projects/my_mcp_server.py"]
    }
  }
}
```

---

### Day 6-7：实战项目

#### 📖 项目材料
- [MCP文件系统服务器](./projects/mcp_filesystem/) ✅

**项目功能**：
- 📁 浏览目录结构
- 📄 读取文件内容
- ✏️ 创建/编辑文件
- 🔍 搜索文件
- 📊 获取文件信息

---

## 📊 学习检查清单

### MCP基础
- [ ] 理解MCP的设计目的和优势
- [ ] 了解JSON-RPC 2.0协议基础
- [ ] 区分Tool、Resource、Prompt三种类型

### FastMCP开发
- [ ] 能够安装和配置FastMCP
- [ ] 会使用装饰器定义工具
- [ ] 能够处理工具执行错误

### Tools开发
- [ ] 能够定义参数和类型注解
- [ ] 会开发异步工具
- [ ] 了解安全性最佳实践

### Resources开发
- [ ] 理解资源URI设计
- [ ] 能够暴露文件系统资源
- [ ] 会创建动态资源

### Claude集成
- [ ] 能够配置Claude Desktop
- [ ] 会查看MCP日志
- [ ] 能够排查常见问题

---

## 📺 推荐学习资源

### B站视频
| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | MCP协议完全攻略 | https://www.bilibili.com/video/BV1C5411X7Kg |
| 技术胖 | 手把手开发MCP Server | https://www.bilibili.com/video/BV1nB4y1J7Jz |

### 官方文档
- [MCP官方文档](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Anthropic MCP指南](https://docs.anthropic.com/claude/docs/mcp)

---

## 🎯 下一步

完成本周学习后，你已经掌握了AI工程的基础能力！

继续前往：

👉 [Week 4: RAG系统基础](../week4/README.md)

---

**MCP让AI能够安全地与世界交互，这是构建智能体的关键！💪**
