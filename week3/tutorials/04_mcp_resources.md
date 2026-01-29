# 📦 MCP Resources开发指南

> **学习目标**：掌握MCP资源暴露，让AI能够读取文件、数据库等各种数据源

---

## 1. Resource的本质

**Resource**是MCP Server暴露的只读数据，AI可以通过URI访问：

```
Tool（工具）：执行操作，有副作用
Resource（资源）：读取数据，无副作用
```

### 对比

| 特性 | Tool | Resource |
|------|------|----------|
| 用途 | 执行操作 | 读取数据 |
| 副作用 | 可能有 | 无 |
| 调用方式 | 函数调用 | URI访问 |
| 示例 | `send_email()` | `file://readme.md` |

---

## 2. Resource URI设计

### 2.1 URI格式

```
scheme://path
  │        │
  │        └─ 资源路径（可包含参数）
  └───────── 协议/类型
```

**示例**：
- `file://documents/readme.md` - 文件资源
- `db://users/123` - 数据库记录
- `config://app/settings` - 配置资源
- `api://weather/beijing` - API数据

### 2.2 静态URI

```python
from fastmcp import FastMCP

mcp = FastMCP("资源服务")

@mcp.resource("config://app")
def get_app_config() -> str:
    """获取应用配置"""
    import json
    config = {
        "app_name": "我的应用",
        "version": "1.0.0",
        "debug": True
    }
    return json.dumps(config, indent=2, ensure_ascii=False)
```

### 2.3 动态URI（带参数）

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """读取指定文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.resource("user://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """获取用户资料"""
    # 从数据库获取用户
    users = {
        "1": {"name": "张三", "email": "zhangsan@example.com"},
        "2": {"name": "李四", "email": "lisi@example.com"}
    }
    user = users.get(user_id, {"error": "用户不存在"})
    return json.dumps(user, ensure_ascii=False)
```

---

## 3. 文件系统资源

### 3.1 单文件资源

```python
import os
import mimetypes

@mcp.resource("file://{filepath}")
def file_resource(filepath: str) -> str:
    """读取文件内容"""
    # 安全检查
    if ".." in filepath:
        return "错误：不允许路径穿越"
    
    if not os.path.exists(filepath):
        return f"错误：文件不存在 {filepath}"
    
    # 检测文件类型
    mime_type, _ = mimetypes.guess_type(filepath)
    
    # 文本文件直接读取
    if mime_type and mime_type.startswith("text/"):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    # 二进制文件返回信息
    size = os.path.getsize(filepath)
    return f"[二进制文件] 类型: {mime_type}, 大小: {size} bytes"
```

### 3.2 目录列表资源

```python
import json
from datetime import datetime

@mcp.resource("dir://{dirpath}")
def directory_resource(dirpath: str) -> str:
    """获取目录内容列表"""
    if not os.path.isdir(dirpath):
        return f"错误：不是目录 {dirpath}"
    
    items = []
    for name in os.listdir(dirpath):
        full_path = os.path.join(dirpath, name)
        stat = os.stat(full_path)
        
        items.append({
            "name": name,
            "type": "directory" if os.path.isdir(full_path) else "file",
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return json.dumps(items, indent=2, ensure_ascii=False)
```

---

## 4. 数据库资源

### 4.1 SQLite资源

```python
import sqlite3
import json

DATABASE_PATH = "data.db"

@mcp.resource("db://tables")
def list_tables() -> str:
    """列出所有数据表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return json.dumps(tables)

@mcp.resource("db://table/{table_name}")
def get_table_data(table_name: str) -> str:
    """获取表数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = [dict(row) for row in cursor.fetchall()]
        return json.dumps(rows, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        return f"错误: {e}"
    finally:
        conn.close()

@mcp.resource("db://table/{table_name}/row/{row_id}")
def get_row(table_name: str, row_id: str) -> str:
    """获取单行数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (row_id,))
        row = cursor.fetchone()
        if row:
            return json.dumps(dict(row), indent=2, ensure_ascii=False, default=str)
        return "未找到记录"
    finally:
        conn.close()
```

### 4.2 异步数据库资源

```python
import aiosqlite

@mcp.resource("async-db://table/{table_name}")
async def async_get_table(table_name: str) -> str:
    """异步获取表数据"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT * FROM {table_name} LIMIT 100") as cursor:
            rows = await cursor.fetchall()
            data = [dict(row) for row in rows]
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
```

---

## 5. API资源

### 5.1 RESTful API资源

```python
import aiohttp

@mcp.resource("api://weather/{city}")
async def weather_resource(city: str) -> str:
    """获取城市天气（从外部API）"""
    # 模拟（实际应调用真实API）
    weather_data = {
        "beijing": {"city": "北京", "temp": 25, "condition": "晴"},
        "shanghai": {"city": "上海", "temp": 22, "condition": "多云"},
        "guangzhou": {"city": "广州", "temp": 28, "condition": "小雨"}
    }
    
    data = weather_data.get(city.lower())
    if data:
        return json.dumps(data, ensure_ascii=False)
    return f"未找到城市: {city}"

@mcp.resource("api://github/{owner}/{repo}")
async def github_repo_resource(owner: str, repo: str) -> str:
    """获取GitHub仓库信息"""
    async with aiohttp.ClientSession() as session:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return json.dumps({
                    "name": data["name"],
                    "description": data["description"],
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "language": data["language"]
                }, ensure_ascii=False, indent=2)
            return f"获取失败: {response.status}"
```

---

## 6. 动态资源模板

### 6.1 资源发现

```python
@mcp.resource("template://list")
def list_templates() -> str:
    """列出所有可用的资源模板"""
    templates = [
        {"uri": "file://{path}", "description": "读取文件内容"},
        {"uri": "dir://{path}", "description": "列出目录内容"},
        {"uri": "db://table/{name}", "description": "获取数据表"},
        {"uri": "api://weather/{city}", "description": "获取天气"}
    ]
    return json.dumps(templates, indent=2, ensure_ascii=False)
```

### 6.2 资源元数据

```python
from dataclasses import dataclass

@dataclass
class ResourceMetadata:
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"

@mcp.resource("meta://{resource_type}")
def get_resource_metadata(resource_type: str) -> str:
    """获取资源元数据"""
    metadata = {
        "file": ResourceMetadata(
            uri="file://{path}",
            name="文件资源",
            description="读取本地文件内容",
            mime_type="text/plain"
        ),
        "db": ResourceMetadata(
            uri="db://table/{name}",
            name="数据库资源",
            description="读取数据库表数据",
            mime_type="application/json"
        )
    }
    
    meta = metadata.get(resource_type)
    if meta:
        return json.dumps(meta.__dict__, ensure_ascii=False, indent=2)
    return f"未知资源类型: {resource_type}"
```

---

## 7. 完整示例：知识库资源服务

```python
from fastmcp import FastMCP
import os
import json
from pathlib import Path

mcp = FastMCP("知识库服务")

KNOWLEDGE_BASE = "./knowledge"  # 知识库目录

@mcp.resource("kb://categories")
def list_categories() -> str:
    """列出所有知识分类"""
    categories = []
    for item in os.listdir(KNOWLEDGE_BASE):
        path = os.path.join(KNOWLEDGE_BASE, item)
        if os.path.isdir(path):
            doc_count = len([f for f in os.listdir(path) if f.endswith('.md')])
            categories.append({
                "name": item,
                "document_count": doc_count
            })
    return json.dumps(categories, indent=2, ensure_ascii=False)

@mcp.resource("kb://category/{category}")
def list_documents(category: str) -> str:
    """列出分类下的所有文档"""
    category_path = os.path.join(KNOWLEDGE_BASE, category)
    if not os.path.isdir(category_path):
        return f"分类不存在: {category}"
    
    documents = []
    for filename in os.listdir(category_path):
        if filename.endswith('.md'):
            filepath = os.path.join(category_path, filename)
            stat = os.stat(filepath)
            documents.append({
                "name": filename[:-3],  # 去掉.md后缀
                "filename": filename,
                "size": stat.st_size,
                "uri": f"kb://doc/{category}/{filename}"
            })
    
    return json.dumps(documents, indent=2, ensure_ascii=False)

@mcp.resource("kb://doc/{category}/{filename}")
def get_document(category: str, filename: str) -> str:
    """获取文档内容"""
    filepath = os.path.join(KNOWLEDGE_BASE, category, filename)
    
    if not os.path.exists(filepath):
        return f"文档不存在: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.resource("kb://search/{keyword}")
def search_documents(keyword: str) -> str:
    """搜索包含关键词的文档"""
    results = []
    
    for root, dirs, files in os.walk(KNOWLEDGE_BASE):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        rel_path = os.path.relpath(filepath, KNOWLEDGE_BASE)
                        results.append({
                            "path": rel_path,
                            "matches": content.lower().count(keyword.lower())
                        })
    
    results.sort(key=lambda x: x["matches"], reverse=True)
    return json.dumps(results[:10], indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| AI进化论 | MCP资源暴露实战 | https://www.bilibili.com/video/BV1C5411X7Kg |
| 技术胖 | Python文件系统操作 | https://www.bilibili.com/video/BV1nB4y1J7Jz |

---

## 8. 继续学习

📌 **Week 3 学习顺序**：
1. ✅ MCP协议入门
2. ✅ FastMCP基础教程
3. ✅ MCP Tools开发指南
4. ✅ MCP Resources开发指南（本教程）
5. ➡️ Claude Desktop集成

---

**Resource让AI能够读取任何数据源！💪**
