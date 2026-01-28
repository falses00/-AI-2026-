# 🔌 MCP协议入门

> **学习目标**：理解Model Context Protocol，学会构建AI可调用的工具服务器

---

## 1. 什么是MCP？

**MCP (Model Context Protocol)** 是由Anthropic提出的AI工具标准协议。

**类比**：MCP就像AI的"USB-C接口"，让AI能够即插即用地连接各种工具。

---

## 2. 核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **Tool** | AI可调用的函数 | 搜索、计算、发邮件 |
| **Resource** | AI可读取的数据 | 文件、数据库 |
| **Prompt** | 预设的提示模板 | 代码审查、翻译 |

---

## 3. MCP架构

```
┌─────────────┐     MCP协议      ┌─────────────┐
│   Claude    │ ◄──────────────► │  MCP Server │
│  (Client)   │                  │  (你的代码)  │
└─────────────┘                  └─────────────┘
                                       │
                                       ▼
                                 ┌─────────────┐
                                 │  文件系统    │
                                 │  数据库      │
                                 │  API服务     │
                                 └─────────────┘
```

---

## 4. 使用FastMCP快速入门

### 安装
```bash
pip install fastmcp
```

### 最简示例

```python
from fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("我的工具服务器")

# 定义一个工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

@mcp.tool()
def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 运行服务器
if __name__ == "__main__":
    mcp.run()
```

---

## 5. 连接Claude Desktop

### 配置文件位置
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

### 配置内容

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["D:/path/to/your/mcp_server.py"]
    }
  }
}
```

重启Claude Desktop后，你的工具就可用了！

---

## 6. 实战：文件管理工具

```python
from fastmcp import FastMCP
import os

mcp = FastMCP("文件管理器")

@mcp.tool()
def list_files(directory: str) -> list[str]:
    """列出目录中的文件"""
    return os.listdir(directory)

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"已写入: {path}"

if __name__ == "__main__":
    mcp.run()
```

---

## 7. 下一步

👉 [完整MCP项目实战](../projects/project5_mcp_filesystem/)

**MCP是2026年AI工程师必备技能！💪**
