# 🔧 工具开发详解

> **学习目标**：掌握Agent工具的设计、开发和最佳实践

---

## 1. 工具的重要性

**工具是Agent的手脚**，决定了Agent能做什么：

```
无工具的LLM: 只能回答问题
有工具的Agent: 可以搜索、计算、执行代码、调用API...
```

---

## 2. 工具设计原则

### 2.1 单一职责

```python
# ❌ 不好：功能太多
def do_everything(action, param1, param2):
    if action == "search":
        ...
    elif action == "calculate":
        ...
    elif action == "send_email":
        ...

# ✅ 好：每个工具只做一件事
def search(query: str) -> str: ...
def calculate(expression: str) -> str: ...
def send_email(to: str, content: str) -> str: ...
```

### 2.2 清晰的描述

```python
# ❌ 不好：描述模糊
@tool
def process(x):
    """处理数据"""
    ...

# ✅ 好：描述详细
@tool
def calculate_expression(expression: str) -> str:
    """
    计算数学表达式并返回结果。
    
    参数:
        expression: 数学表达式，如 "2 + 3 * 4"
    
    返回:
        计算结果字符串
    
    示例:
        calculate_expression("2 + 3") -> "5"
    """
    ...
```

### 2.3 错误处理

```python
@tool
def safe_calculator(expression: str) -> str:
    """安全的计算器，处理各种错误情况"""
    try:
        # 验证输入
        if not expression:
            return "错误：表达式不能为空"
        
        # 安全检查
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "错误：表达式包含非法字符"
        
        # 计算
        result = eval(expression)
        return f"结果: {result}"
    
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except SyntaxError:
        return "错误：表达式格式不正确"
    except Exception as e:
        return f"错误：{str(e)}"
```

---

## 3. 常用工具实现

### 3.1 搜索工具

```python
import requests
from typing import Optional

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    搜索网络信息。
    
    参数:
        query: 搜索关键词
        max_results: 最大结果数（默认5）
    """
    try:
        # 使用SerpAPI或其他搜索API
        api_key = os.getenv("SERPAPI_KEY")
        response = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": api_key, "num": max_results}
        )
        
        results = response.json().get("organic_results", [])
        
        output = []
        for r in results[:max_results]:
            output.append(f"- {r['title']}: {r['snippet']}")
        
        return "\n".join(output) if output else "未找到结果"
    
    except Exception as e:
        return f"搜索失败: {e}"
```

### 3.2 代码执行工具

```python
import subprocess
import tempfile

@tool
def execute_python(code: str) -> str:
    """
    执行Python代码并返回输出。
    
    警告：此工具有安全风险，生产环境需要沙箱。
    
    参数:
        code: Python代码字符串
    """
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        # 执行代码（限制时间）
        result = subprocess.run(
            ['python', temp_path],
            capture_output=True,
            text=True,
            timeout=10  # 10秒超时
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n错误: {result.stderr}"
        
        return output if output else "代码执行完成，无输出"
    
    except subprocess.TimeoutExpired:
        return "错误：代码执行超时"
    except Exception as e:
        return f"执行失败: {e}"
```

### 3.3 文件操作工具

```python
import os

@tool
def read_file(filepath: str) -> str:
    """
    读取文件内容。
    
    参数:
        filepath: 文件路径
    """
    try:
        # 安全检查：限制到特定目录
        allowed_dir = "./workspace"
        abs_path = os.path.abspath(filepath)
        if not abs_path.startswith(os.path.abspath(allowed_dir)):
            return "错误：不允许访问该目录"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 限制返回长度
        if len(content) > 5000:
            return content[:5000] + "\n...(内容已截断)"
        
        return content
    
    except FileNotFoundError:
        return f"错误：文件不存在 - {filepath}"
    except Exception as e:
        return f"读取失败: {e}"

@tool
def write_file(filepath: str, content: str) -> str:
    """
    写入文件内容。
    
    参数:
        filepath: 文件路径
        content: 要写入的内容
    """
    try:
        allowed_dir = "./workspace"
        abs_path = os.path.abspath(filepath)
        if not abs_path.startswith(os.path.abspath(allowed_dir)):
            return "错误：不允许写入该目录"
        
        # 创建目录
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功写入 {len(content)} 字符到 {filepath}"
    
    except Exception as e:
        return f"写入失败: {e}"
```

### 3.4 数据库工具

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect("./data.db")
    try:
        yield conn
    finally:
        conn.close()

@tool
def query_database(sql: str) -> str:
    """
    执行SQL查询（仅SELECT）。
    
    参数:
        sql: SQL查询语句
    """
    try:
        # 安全检查：只允许SELECT
        if not sql.strip().upper().startswith("SELECT"):
            return "错误：只允许SELECT查询"
        
        with get_db_connection() as conn:
            cursor = conn.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        if not rows:
            return "查询结果为空"
        
        # 格式化输出
        result = " | ".join(columns) + "\n"
        result += "-" * 50 + "\n"
        for row in rows[:20]:  # 限制20行
            result += " | ".join(str(v) for v in row) + "\n"
        
        if len(rows) > 20:
            result += f"...（还有 {len(rows) - 20} 行）"
        
        return result
    
    except Exception as e:
        return f"查询失败: {e}"
```

### 3.5 API调用工具

```python
import requests
import json

@tool
def call_api(
    url: str, 
    method: str = "GET",
    headers: str = "{}",
    body: str = "{}"
) -> str:
    """
    调用HTTP API。
    
    参数:
        url: API地址
        method: HTTP方法 (GET/POST/PUT/DELETE)
        headers: JSON格式的请求头
        body: JSON格式的请求体
    """
    try:
        headers_dict = json.loads(headers)
        body_dict = json.loads(body) if body != "{}" else None
        
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers_dict,
            json=body_dict,
            timeout=10
        )
        
        return f"状态码: {response.status_code}\n响应: {response.text[:1000]}"
    
    except json.JSONDecodeError:
        return "错误：headers或body不是有效的JSON"
    except requests.Timeout:
        return "错误：请求超时"
    except Exception as e:
        return f"请求失败: {e}"
```

---

## 4. 工具组合示例

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# 创建一组协作工具
@tool
def search(query: str) -> str:
    """搜索信息"""
    return f"关于'{query}'的搜索结果：这是一些相关信息..."

@tool
def summarize(text: str) -> str:
    """总结文本"""
    return f"总结：{text[:50]}..."

@tool
def translate(text: str, target_lang: str = "en") -> str:
    """翻译文本"""
    return f"[{target_lang}] {text}"

@tool
def save_to_file(content: str, filename: str) -> str:
    """保存到文件"""
    with open(f"./output/{filename}", 'w') as f:
        f.write(content)
    return f"已保存到 {filename}"

# 组合使用
tools = [search, summarize, translate, save_to_file]

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="your-key",
    openai_api_base="https://api.deepseek.com/v1"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个研究助手。可以：
1. 搜索信息
2. 总结内容
3. 翻译文本
4. 保存结果

请根据用户需求合理组合使用这些工具。"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行复杂任务
result = executor.invoke({
    "input": "搜索FastAPI的信息，总结后翻译成英文，保存到fastapi_info.txt"
})
```

---

## 5. 工具测试

```python
import pytest

# 测试工具函数
def test_calculator():
    result = safe_calculator("2 + 3")
    assert "5" in result

def test_calculator_error():
    result = safe_calculator("1/0")
    assert "错误" in result

def test_file_operations():
    # 写入
    write_result = write_file("./workspace/test.txt", "hello")
    assert "成功" in write_result
    
    # 读取
    read_result = read_file("./workspace/test.txt")
    assert "hello" in read_result

# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 📺 推荐B站视频

搜索：
- **"AI Agent 工具开发"**
- **"LangChain Tools 教程"**
- **"Function Calling 实战"**

---

## 6. 继续学习

📌 **Week 6 学习顺序**：
1. ✅ Agent基础概念
2. ✅ ReAct框架
3. ✅ 工具使用详解（本教程）
4. ➡️ 多Agent系统

---

**好的工具设计是Agent成功的关键！💪**
