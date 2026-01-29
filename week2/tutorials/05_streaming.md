# 📡 Streaming 流式响应

> **学习目标**：实现类ChatGPT的实时打字效果，掌握SSE协议和FastAPI流式端点

---

## 1. 为什么需要流式响应？

### 普通响应 vs 流式响应

| 对比项 | 普通响应 | 流式响应 |
|--------|----------|----------|
| 用户体验 | 等待后一次性显示 | 实时逐字显示 |
| 首字延迟 | 高（等待完整生成） | 低（立即开始显示） |
| 适用场景 | 短文本、API调用 | 聊天、长文本生成 |

---

## 2. 流式API调用

### 2.1 基础用法

```python
from config.deepseek_client import get_client

client = get_client()

# 开启流式响应
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "写一首关于春天的诗"}],
    stream=True  # 关键参数！
)

# 逐块处理
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 2.2 完整处理

```python
def stream_chat(messages: list) -> str:
    """流式聊天，返回完整内容"""
    client = get_client()
    
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )
    
    full_content = ""
    for chunk in stream:
        delta = chunk.choices[0].delta
        
        # 检查是否有内容
        if delta.content:
            content = delta.content
            full_content += content
            print(content, end="", flush=True)
        
        # 检查是否结束
        if chunk.choices[0].finish_reason:
            print()  # 换行
            break
    
    return full_content
```

---

## 3. SSE协议详解

### 3.1 什么是SSE？

**Server-Sent Events**是一种服务器向客户端推送数据的技术：

```
客户端 ----请求----> 服务器
客户端 <---数据1---- 服务器
客户端 <---数据2---- 服务器
客户端 <---数据3---- 服务器
...
```

### 3.2 SSE数据格式

```
data: {"content": "你好"}

data: {"content": "世界"}

data: [DONE]
```

**规则**：
- 每条消息以 `data: ` 开头
- 消息之间用空行分隔
- `[DONE]` 表示结束

---

## 4. FastAPI流式端点

### 4.1 基础实现

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from config.deepseek_client import get_client
import json

app = FastAPI()

async def generate_stream(message: str):
    """生成SSE流"""
    client = get_client()
    
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            # SSE格式
            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
    
    yield "data: [DONE]\n\n"

@app.get("/chat/stream")
async def chat_stream(message: str):
    """流式聊天端点"""
    return StreamingResponse(
        generate_stream(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

### 4.2 POST请求支持

```python
from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat/stream")
async def chat_stream_post(request: ChatRequest):
    """POST方式的流式聊天"""
    messages = [m.model_dump() for m in request.messages]
    
    async def generate():
        client = get_client()
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## 5. 前端接收

### 5.1 使用EventSource（简单）

```html
<!DOCTYPE html>
<html>
<head>
    <title>流式聊天</title>
</head>
<body>
    <div id="output"></div>
    <script>
        const output = document.getElementById('output');
        const message = "写一首关于春天的诗";
        
        // 创建EventSource连接
        const eventSource = new EventSource(`/chat/stream?message=${encodeURIComponent(message)}`);
        
        eventSource.onmessage = function(event) {
            if (event.data === '[DONE]') {
                eventSource.close();
                return;
            }
            
            const data = JSON.parse(event.data);
            output.textContent += data.content;
        };
        
        eventSource.onerror = function(error) {
            console.error('连接错误:', error);
            eventSource.close();
        };
    </script>
</body>
</html>
```

### 5.2 使用fetch（支持POST）

```html
<script>
async function streamChat(message) {
    const output = document.getElementById('output');
    output.textContent = '';
    
    const response = await fetch('/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            messages: [{role: 'user', content: message}]
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') return;
                
                try {
                    const json = JSON.parse(data);
                    output.textContent += json.content;
                } catch (e) {}
            }
        }
    }
}
</script>
```

---

## 6. 错误处理

### 6.1 超时处理

```python
import asyncio
from fastapi import HTTPException

async def generate_with_timeout(message: str, timeout: int = 60):
    """带超时的流式生成"""
    client = get_client()
    
    try:
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": message}],
            stream=True,
            timeout=timeout  # API级别超时
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
```

### 6.2 连接中断处理

```python
from starlette.requests import Request

@app.post("/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    async def generate():
        try:
            for chunk in stream:
                # 检查客户端是否断开
                if await request.is_disconnected():
                    print("客户端断开连接")
                    break
                
                yield f"data: {...}\n\n"
        except GeneratorExit:
            print("生成器被关闭")
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 7. 完整示例项目

```python
# streaming_chat.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import List
import json
from config.deepseek_client import get_client

app = FastAPI(title="流式聊天Demo")

# 前端页面
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>流式聊天</title>
        <style>
            body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #output { background: #f5f5f5; padding: 20px; min-height: 200px; white-space: pre-wrap; }
            input { width: 80%; padding: 10px; }
            button { padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h1>🤖 流式聊天</h1>
        <input type="text" id="input" placeholder="输入消息...">
        <button onclick="send()">发送</button>
        <h3>回复：</h3>
        <div id="output"></div>
        
        <script>
            async function send() {
                const input = document.getElementById('input');
                const output = document.getElementById('output');
                output.textContent = '';
                
                const response = await fetch('/chat/stream?message=' + encodeURIComponent(input.value));
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value);
                    for (const line of text.split('\\n')) {
                        if (line.startsWith('data: ') && line.slice(6) !== '[DONE]') {
                            try {
                                const data = JSON.parse(line.slice(6));
                                output.textContent += data.content;
                            } catch(e) {}
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        client = get_client()
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": message}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📺 推荐B站视频

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 技术胖 | 大模型流式输出实现 | https://www.bilibili.com/video/BV1xK411o7aG |
| 编程不良人 | SSE协议详解 | https://www.bilibili.com/video/BV1tZ4y1E7cT |

---

## 8. 继续学习

📌 **Week 2 学习顺序**：
1. ✅ DeepSeek API快速入门
2. ✅ 结构化输出详解
3. ✅ Response Format深度解析
4. ✅ Function Calling详解
5. ✅ Streaming流式响应（本教程）
6. ➡️ Token计算与优化

---

**流式响应让AI对话更自然流畅！💪**
