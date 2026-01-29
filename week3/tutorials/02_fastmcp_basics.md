# ⚡ FastMCP基础教程

> **学习目标**：使用FastMCP SDK快速开发MCP Server

---

## 1. 什么是FastMCP？

**FastMCP**是一个Python SDK，让你用最简单的方式开发MCP Server：

```python
# 只需几行代码！
from fastmcp import FastMCP

mcp = FastMCP("我的工具")

@mcp.tool()
def hello(name: str) -> str:
    return f"你好，{name}！"

mcp.run()
```

**优势**：
- ✅ 装饰器语法，类似FastAPI
- ✅ 自动生成JSON Schema
- ✅ 内置类型验证
- ✅ 支持异步

---

## 2. 安装与配置

### 2.1 安装FastMCP

```bash
pip install fastmcp
```

### 2.2 验证安装

```python
import fastmcp
print(fastmcp.__version__)
```

### 2.3 项目结构推荐

```
my_mcp_server/
├── server.py          # 主入口
├── tools/             # 工具模块
│   ├── __init__.py
│   ├── file_tools.py
│   └── web_tools.py
├── resources/         # 资源模块
│   └── __init__.py
├── config.py          # 配置
└── requirements.txt
```

---

## 3. 第一个MCP Server

### 3.1 创建Server

```python
# server.py
from fastmcp import FastMCP

# 创建Server实例
mcp = FastMCP(
    name="计算器助手",           # Server名称
    version="1.0.0",             # 版本号
    description="一个简单的计算器MCP服务"  # 描述
)

# 定义工具
@mcp.tool()
def add(a: float, b: float) -> float:
    """两数相加
    
    Args:
        a: 第一个数
        b: 第二个数
    
    Returns:
        两数之和
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """两数相乘"""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """两数相除"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 运行Server
if __name__ == "__main__":
    mcp.run()
```

### 3.2 运行测试

```bash
# 运行Server
python server.py

# 或使用fastmcp命令
fastmcp run server.py
```

---

## 4. 装饰器详解

### 4.1 @mcp.tool() 工具装饰器

```python
from typing import Optional

@mcp.tool()
def search_files(
    directory: str,
    pattern: str = "*.py",
    recursive: bool = True,
    max_results: Optional[int] = None
) -> list[str]:
    """搜索文件
    
    在指定目录中搜索匹配模式的文件。
    
    Args:
        directory: 搜索的根目录
        pattern: 文件匹配模式，支持通配符
        recursive: 是否递归搜索子目录
        max_results: 最大返回结果数，None表示不限制
    
    Returns:
        匹配的文件路径列表
    """
    import glob
    import os
    
    if recursive:
        path = os.path.join(directory, "**", pattern)
    else:
        path = os.path.join(directory, pattern)
    
    results = glob.glob(path, recursive=recursive)
    
    if max_results:
        results = results[:max_results]
    
    return results
```

**关键点**：
- 函数名 → 工具名
- 参数类型注解 → 自动生成Schema
- docstring → 工具描述
- 返回值类型 → 输出格式

### 4.2 @mcp.resource() 资源装饰器

```python
@mcp.resource("config://app")
def get_app_config() -> str:
    """获取应用配置"""
    import json
    config = {"debug": True, "version": "1.0"}
    return json.dumps(config, indent=2)

@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """读取指定路径的文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

**URI模式**：
- `config://app` - 固定URI
- `file://{path}` - 动态URI，path从URI中提取

### 4.3 @mcp.prompt() 提示词装饰器

```python
@mcp.prompt()
def code_review() -> str:
    """代码审查提示词"""
    return """请对以下代码进行审查，关注：
1. 代码质量和可读性
2. 潜在的bug和安全问题
3. 性能优化建议
4. 最佳实践遵循情况

请用中文回复。"""

@mcp.prompt()
def summarize_document(language: str = "中文") -> str:
    """文档总结提示词"""
    return f"""请用{language}总结以下文档的主要内容：
- 核心观点
- 关键信息
- 重要结论"""
```

---

## 5. 异步支持

FastMCP完全支持异步函数：

```python
import aiohttp
import asyncio

@mcp.tool()
async def fetch_url(url: str) -> str:
    """异步获取网页内容"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

@mcp.tool()
async def parallel_fetch(urls: list[str]) -> list[str]:
    """并行获取多个网页"""
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.text() for r in responses]
```

---

## 6. 错误处理

### 6.1 基础错误处理

```python
@mcp.tool()
def safe_divide(a: float, b: float) -> float:
    """安全除法"""
    if b == 0:
        raise ValueError("除数不能为零！")
    return a / b
```

### 6.2 自定义错误信息

```python
from fastmcp import ToolError

@mcp.tool()
def process_file(filepath: str) -> str:
    """处理文件"""
    import os
    
    if not os.path.exists(filepath):
        raise ToolError(f"文件不存在: {filepath}")
    
    if not os.access(filepath, os.R_OK):
        raise ToolError(f"没有读取权限: {filepath}")
    
    with open(filepath, 'r') as f:
        return f.read()
```

---

## 7. 完整示例：文件助手

```python
# file_assistant.py
from fastmcp import FastMCP
import os
import json
from datetime import datetime

mcp = FastMCP(
    name="文件助手",
    description="帮助你管理和操作文件"
)

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """列出目录内容
    
    Args:
        path: 目录路径，默认为当前目录
    """
    try:
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else 0
            items.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size": size
            })
        return json.dumps(items, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"错误: {e}"

@mcp.tool()
def read_file(filepath: str, encoding: str = "utf-8") -> str:
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {e}"

@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """写入文件内容"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入 {len(content)} 字符到 {filepath}"
    except Exception as e:
        return f"写入失败: {e}"

@mcp.tool()
def get_file_info(filepath: str) -> str:
    """获取文件详细信息"""
    try:
        stat = os.stat(filepath)
        info = {
            "路径": filepath,
            "大小": f"{stat.st_size} bytes",
            "创建时间": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "修改时间": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "是否可读": os.access(filepath, os.R_OK),
            "是否可写": os.access(filepath, os.W_OK)
        }
        return json.dumps(info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"获取信息失败: {e}"

@mcp.resource("file://{path}")
def file_content(path: str) -> str:
    """作为资源读取文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | FastMCP快速入门 | https://www.bilibili.com/video/BV1C5411X7Kg |
| 技术胖 | Python MCP开发实战 | https://www.bilibili.com/video/BV1nB4y1J7Jz |

---

## 8. 继续学习

📌 **Week 3 学习顺序**：
1. ✅ MCP协议入门
2. ✅ FastMCP基础教程（本教程）
3. ➡️ MCP Tools开发指南
4. ➡️ MCP Resources开发指南
5. ➡️ Claude Desktop集成

---

**FastMCP让MCP开发像写Flask一样简单！💪**
