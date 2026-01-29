# 🔧 MCP Tools开发指南

> **学习目标**：深入掌握MCP工具开发，包括参数验证、异步处理和安全实践

---

## 1. Tool的本质

**Tool**是MCP Server暴露给AI的可调用函数：

```
用户: "帮我查一下北京的天气"
         │
         ▼
Claude: 我需要调用 get_weather 工具
         │
         ▼
MCP Server: get_weather("北京") → "晴天，25°C"
         │
         ▼
Claude: "北京今天晴天，气温25°C"
```

---

## 2. 工具定义详解

### 2.1 基础定义

```python
from fastmcp import FastMCP

mcp = FastMCP("我的工具集")

@mcp.tool()
def greet(name: str) -> str:
    """向用户打招呼
    
    Args:
        name: 用户的名字
    
    Returns:
        打招呼的消息
    """
    return f"你好，{name}！"
```

### 2.2 参数类型支持

```python
from typing import Optional, List, Dict, Literal
from datetime import datetime

@mcp.tool()
def complex_tool(
    # 基础类型
    text: str,
    count: int,
    ratio: float,
    enabled: bool,
    
    # 可选参数
    description: Optional[str] = None,
    
    # 列表类型
    tags: List[str] = [],
    
    # 字典类型
    metadata: Dict[str, str] = {},
    
    # 枚举类型
    priority: Literal["low", "medium", "high"] = "medium"
) -> dict:
    """复杂参数示例"""
    return {
        "text": text,
        "count": count,
        "tags": tags,
        "priority": priority
    }
```

### 2.3 自动生成的Schema

上面的工具会生成以下JSON Schema：

```json
{
  "name": "complex_tool",
  "description": "复杂参数示例",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string"},
      "count": {"type": "integer"},
      "ratio": {"type": "number"},
      "enabled": {"type": "boolean"},
      "description": {"type": "string"},
      "tags": {"type": "array", "items": {"type": "string"}},
      "metadata": {"type": "object"},
      "priority": {"type": "string", "enum": ["low", "medium", "high"]}
    },
    "required": ["text", "count", "ratio", "enabled"]
  }
}
```

---

## 3. 异步工具开发

### 3.1 基础异步工具

```python
import asyncio
import aiohttp

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """获取城市天气（异步）"""
    # 模拟API调用
    await asyncio.sleep(0.5)
    
    # 实际场景：调用天气API
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(f"https://api.weather.com/{city}") as resp:
    #         data = await resp.json()
    
    weather_data = {
        "北京": "晴天 25°C",
        "上海": "多云 22°C", 
        "广州": "小雨 28°C"
    }
    return weather_data.get(city, "未知城市")
```

### 3.2 并行执行多个操作

```python
@mcp.tool()
async def batch_process(items: List[str]) -> List[str]:
    """批量处理多个项目（并行执行）"""
    
    async def process_single(item: str) -> str:
        await asyncio.sleep(0.1)  # 模拟处理时间
        return f"已处理: {item}"
    
    # 并行执行所有处理任务
    tasks = [process_single(item) for item in items]
    results = await asyncio.gather(*tasks)
    
    return results
```

### 3.3 超时控制

```python
@mcp.tool()
async def fetch_with_timeout(url: str, timeout: int = 10) -> str:
    """带超时的网络请求"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return await response.text()
    except asyncio.TimeoutError:
        return f"请求超时（{timeout}秒）"
    except Exception as e:
        return f"请求失败: {e}"
```

---

## 4. 错误处理

### 4.1 标准错误处理

```python
@mcp.tool()
def read_file(filepath: str) -> str:
    """读取文件内容"""
    import os
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    # 检查是否是文件
    if not os.path.isfile(filepath):
        raise ValueError(f"路径不是文件: {filepath}")
    
    # 读取文件
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"文件编码错误，请使用其他编码")
```

### 4.2 自定义错误类型

```python
from fastmcp.exceptions import ToolError

class PermissionDenied(ToolError):
    """权限拒绝错误"""
    pass

class ResourceNotFound(ToolError):
    """资源未找到错误"""
    pass

@mcp.tool()
def secure_operation(filepath: str, action: str) -> str:
    """安全操作示例"""
    import os
    
    # 检查权限
    if not os.access(filepath, os.R_OK):
        raise PermissionDenied(f"没有读取权限: {filepath}")
    
    if action == "write" and not os.access(filepath, os.W_OK):
        raise PermissionDenied(f"没有写入权限: {filepath}")
    
    # 执行操作...
    return "操作成功"
```

---

## 5. 安全最佳实践

### 5.1 路径安全

```python
import os

ALLOWED_BASE_DIR = "/safe/directory"

@mcp.tool()
def safe_read_file(filepath: str) -> str:
    """安全读取文件（防止路径穿越）"""
    
    # 获取绝对路径
    abs_path = os.path.abspath(filepath)
    
    # 检查是否在允许的目录内
    if not abs_path.startswith(ALLOWED_BASE_DIR):
        raise PermissionDenied("不允许访问该路径")
    
    with open(abs_path, 'r') as f:
        return f.read()
```

### 5.2 命令执行安全

```python
import subprocess
import shlex

ALLOWED_COMMANDS = ["ls", "cat", "head", "tail", "wc"]

@mcp.tool()
def safe_execute(command: str) -> str:
    """安全执行命令（白名单限制）"""
    
    # 解析命令
    parts = shlex.split(command)
    if not parts:
        raise ValueError("命令不能为空")
    
    # 检查命令是否在白名单
    cmd = parts[0]
    if cmd not in ALLOWED_COMMANDS:
        raise PermissionDenied(f"不允许执行命令: {cmd}")
    
    # 执行命令
    result = subprocess.run(
        parts,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return result.stdout or result.stderr
```

### 5.3 输入验证

```python
import re
from pydantic import BaseModel, validator

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    
    @validator('recipient')
    def validate_email(cls, v):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, v):
            raise ValueError('无效的邮箱地址')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        if len(v) > 200:
            raise ValueError('主题过长')
        return v

@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """发送邮件（带验证）"""
    # 使用Pydantic验证
    request = EmailRequest(
        recipient=recipient,
        subject=subject,
        body=body
    )
    
    # 发送邮件...
    return f"邮件已发送到 {request.recipient}"
```

---

## 6. 实战示例：系统工具集

```python
from fastmcp import FastMCP
import os
import psutil
import platform
from datetime import datetime

mcp = FastMCP("系统工具")

@mcp.tool()
def get_system_info() -> dict:
    """获取系统信息"""
    return {
        "操作系统": platform.system(),
        "版本": platform.version(),
        "架构": platform.machine(),
        "处理器": platform.processor(),
        "Python版本": platform.python_version()
    }

@mcp.tool()
def get_cpu_usage() -> str:
    """获取CPU使用率"""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    return f"CPU使用率: {cpu_percent}% (共{cpu_count}核)"

@mcp.tool()
def get_memory_usage() -> str:
    """获取内存使用情况"""
    mem = psutil.virtual_memory()
    total = mem.total / (1024**3)  # GB
    used = mem.used / (1024**3)
    percent = mem.percent
    return f"内存: {used:.1f}GB / {total:.1f}GB ({percent}%)"

@mcp.tool()
def get_disk_usage(path: str = "/") -> str:
    """获取磁盘使用情况"""
    disk = psutil.disk_usage(path)
    total = disk.total / (1024**3)
    used = disk.used / (1024**3)
    percent = disk.percent
    return f"磁盘 {path}: {used:.1f}GB / {total:.1f}GB ({percent}%)"

@mcp.tool()
def list_processes(limit: int = 10) -> list:
    """列出占用CPU最高的进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # 按CPU使用率排序
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    return processes[:limit]

if __name__ == "__main__":
    mcp.run()
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | MCP工具开发实战 | https://www.bilibili.com/video/BV1C5411X7Kg |
| 编程浪子 | Python系统监控工具 | https://www.bilibili.com/video/BV1tZ4y1E7cT |

---

## 7. 继续学习

📌 **Week 3 学习顺序**：
1. ✅ MCP协议入门
2. ✅ FastMCP基础教程
3. ✅ MCP Tools开发指南（本教程）
4. ➡️ MCP Resources开发指南
5. ➡️ Claude Desktop集成

---

**掌握Tool开发，让AI拥有强大的执行能力！💪**
