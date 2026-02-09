# 🚀 模型评估与部署

> **学习目标**：掌握微调模型的评估方法和生产部署流程

---

## 1. 模型评估方法

### 1.1 LLM-as-Judge评估

```python
from openai import OpenAI
import json

def llm_evaluate(question: str, reference: str, candidate: str) -> dict:
    """使用LLM评估回答质量"""
    client = OpenAI()
    
    prompt = f"""请评估以下AI回答的质量。

问题: {question}
参考答案: {reference}
待评估回答: {candidate}

请从以下维度评分（1-5分）：
1. 准确性: 信息是否正确
2. 相关性: 是否切题
3. 流畅性: 语言是否通顺
4. 帮助性: 是否真正解决问题

返回JSON格式。"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## 2. vLLM高性能部署

### 2.1 安装

```bash
pip install vllm
```

### 2.2 启动服务

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --port 8000 \
    --tensor-parallel-size 1
```

### 2.3 Python调用

```python
from openai import OpenAI

# vLLM兼容OpenAI API
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="/path/to/your/model",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)
print(response.choices[0].message.content)
```

---

## 3. Docker部署

### 3.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制模型和代码
COPY model/ /app/model/
COPY app.py .

EXPOSE 8000

CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/app/model", "--port", "8000"]
```

### 3.2 docker-compose.yml

```yaml
version: '3.8'

services:
  llm-api:
    build: .
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./model:/app/model:ro
```

---

## 4. FastAPI封装

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Custom LLM API")

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    messages = [{"role": "system", "content": "你是一个专业助手。"}]
    messages.extend(request.history)
    messages.append({"role": "user", "content": request.message})
    
    try:
        response = client.chat.completions.create(
            model="your-model",
            messages=messages
        )
        return ChatResponse(response=response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 5. 学习检查清单

- [ ] 能够使用LLM评估模型质量
- [ ] 会使用vLLM部署模型
- [ ] 能够用Docker容器化部署
- [ ] 会封装FastAPI接口

---

## 继续学习

📌 **Week 9 学习顺序**：
1. ✅ LoRA微调技术
2. ✅ 微调数据集准备
3. ✅ 模型评估与部署（本教程）
