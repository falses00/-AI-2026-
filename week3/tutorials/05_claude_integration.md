# 🖥️ Claude Desktop集成教程

> **学习目标**：将开发的MCP Server与Claude Desktop集成，实现AI工具调用

---

## 1. Claude Desktop简介

**Claude Desktop**是Anthropic提供的桌面应用，支持MCP协议：

```
┌──────────────────────────────────────────┐
│           Claude Desktop                  │
│  ┌───────────────────────────────────┐   │
│  │                                    │   │
│  │      👋 你好，我是Claude          │   │
│  │                                    │   │
│  │  🔧 我已连接以下MCP服务：         │   │
│  │     - 文件助手                    │   │
│  │     - 数据库工具                  │   │
│  │     - Web搜索                     │   │
│  │                                    │   │
│  └───────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

---

## 2. 安装Claude Desktop

### 2.1 下载安装

1. 访问 [Claude官网](https://claude.ai/download)
2. 下载对应系统版本（Windows/Mac）
3. 安装并登录Anthropic账号

### 2.2 验证安装

启动Claude Desktop，确认可以正常对话。

---

## 3. 配置MCP Server

### 3.1 配置文件位置

| 系统 | 配置文件路径 |
|------|-------------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### 3.2 配置格式

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {
        "OPTIONAL_ENV_VAR": "value"
      }
    }
  }
}
```

### 3.3 完整示例

```json
{
  "mcpServers": {
    "file-assistant": {
      "command": "python",
      "args": ["D:/projects/mcp/file_assistant.py"]
    },
    "database-tools": {
      "command": "python", 
      "args": ["D:/projects/mcp/db_tools.py"],
      "env": {
        "DATABASE_URL": "sqlite:///data.db"
      }
    },
    "web-search": {
      "command": "D:/anaconda/python.exe",
      "args": ["-m", "mcp_server_web"]
    }
  }
}
```

---

## 4. 启动与测试

### 4.1 重启Claude Desktop

修改配置后，需要**完全重启**Claude Desktop：
1. 关闭Claude Desktop
2. 确保进程完全退出（检查任务管理器）
3. 重新启动

### 4.2 验证连接

启动后，在Claude对话中输入：
```
列出你可以使用的工具
```

Claude应该回复类似：
```
我可以使用以下工具：
- file-assistant: 文件操作工具
  - list_directory: 列出目录
  - read_file: 读取文件
  - write_file: 写入文件
...
```

### 4.3 测试工具调用

```
请帮我列出 D:/projects 目录下的文件
```

---

## 5. 调试与日志

### 5.1 查看MCP日志

**Windows**：
```
%APPDATA%\Claude\logs\mcp*.log
```

**macOS**：
```
~/Library/Logs/Claude/mcp*.log
```

### 5.2 添加调试日志

在MCP Server中添加日志：

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@mcp.tool()
def my_tool(param: str) -> str:
    logger.debug(f"my_tool called with param: {param}")
    try:
        result = do_something(param)
        logger.info(f"my_tool completed successfully")
        return result
    except Exception as e:
        logger.error(f"my_tool failed: {e}")
        raise
```

### 5.3 控制台调试

直接运行MCP Server查看输出：

```bash
python file_assistant.py
```

然后在另一个终端测试：

```bash
# 发送测试请求
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python file_assistant.py
```

---

## 6. 常见问题排查

### 6.1 Server无法启动

**问题**：Claude显示MCP Server连接失败

**检查清单**：
- [ ] Python路径是否正确？
- [ ] Server脚本路径是否正确？
- [ ] 是否有语法错误？
- [ ] 依赖是否安装？

**验证方法**：
```bash
# 直接运行看是否报错
python D:/projects/mcp/file_assistant.py
```

### 6.2 工具不显示

**问题**：Server连接成功但工具不显示

**可能原因**：
- 工具没有docstring（描述）
- 装饰器语法错误
- 工具名称冲突

**解决方法**：
```python
# 确保每个工具都有描述
@mcp.tool()
def my_tool(param: str) -> str:
    """这是工具描述，必须有！"""  # 重要！
    return "result"
```

### 6.3 权限问题

**问题**：工具执行时报权限错误

**Windows解决**：
```json
{
  "mcpServers": {
    "my-server": {
      "command": "cmd",
      "args": ["/c", "python", "D:/projects/server.py"]
    }
  }
}
```

**路径问题**：使用绝对路径，避免相对路径。

### 6.4 编码问题

**问题**：中文显示乱码

**解决方法**：
```python
import sys
import io

# 强制UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

## 7. 高级配置

### 7.1 多Python环境

```json
{
  "mcpServers": {
    "conda-server": {
      "command": "D:/Anaconda/envs/mcp/python.exe",
      "args": ["D:/projects/mcp/server.py"]
    },
    "venv-server": {
      "command": "D:/projects/.venv/Scripts/python.exe",
      "args": ["D:/projects/mcp/server.py"]
    }
  }
}
```

### 7.2 环境变量

```json
{
  "mcpServers": {
    "api-server": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "API_KEY": "your-api-key",
        "DEBUG": "true",
        "DATABASE_URL": "postgresql://localhost/db"
      }
    }
  }
}
```

### 7.3 使用uvx运行

```json
{
  "mcpServers": {
    "uvx-server": {
      "command": "uvx",
      "args": ["--from", "my-mcp-package", "mcp-server"]
    }
  }
}
```

---

## 8. 实战：集成文件助手

### 8.1 创建Server

```python
# file_assistant.py
from fastmcp import FastMCP
import os

mcp = FastMCP("文件助手")

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """列出目录下的文件"""
    try:
        items = os.listdir(directory)
        return "\n".join(items)
    except Exception as e:
        return f"错误: {e}"

@mcp.tool()
def read_file(filepath: str) -> str:
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"错误: {e}"

if __name__ == "__main__":
    mcp.run()
```

### 8.2 配置Claude

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "file-assistant": {
      "command": "D:/Anaconda/python.exe",
      "args": ["D:/projects/mcp/file_assistant.py"]
    }
  }
}
```

### 8.3 测试对话

重启Claude Desktop后，尝试：

```
帮我列出 D:/projects 目录下的文件

读取 D:/projects/readme.md 的内容
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | Claude Desktop MCP配置 | https://www.bilibili.com/video/BV1C5411X7Kg |
| 技术胖 | MCP本地部署完整教程 | https://www.bilibili.com/video/BV1nB4y1J7Jz |

---

## 9. 完成！

🎉 **恭喜！你已完成Week 3所有教程！**

📌 **Week 3 学习顺序**：
1. ✅ MCP协议入门
2. ✅ FastMCP基础教程
3. ✅ MCP Tools开发指南
4. ✅ MCP Resources开发指南
5. ✅ Claude Desktop集成（本教程）

在左侧菜单选择 **Week 4** 继续学习RAG系统！

---

**MCP让你的工具无缝集成到AI工作流中！💪**
