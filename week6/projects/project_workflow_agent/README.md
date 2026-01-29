# 🤖 Week 6 项目：智能工作流Agent

> **项目目标**：构建一个能够自动完成复杂工作流的多Agent系统

---

## 🎯 项目要求

### 业务场景

**内容创作工作流**：用户提供主题 → 自动完成调研+撰写+审核+发布

### 功能需求

1. **任务分解**：自动将复杂任务分解为子任务
2. **多角色协作**：研究员、撰稿人、审核员分工
3. **ReAct执行**：每个Agent使用ReAct框架思考
4. **工具调用**：支持搜索、写入文件、发送通知
5. **流程控制**：顺序执行+条件分支

### 技术亮点

- 多Agent协作架构
- ReAct推理框架
- 工具链设计
- 状态管理
- 异常处理

---

## 📁 项目结构

```
project_workflow_agent/
├── main.py                  # 入口
├── config.py                # 配置
├── agents/
│   ├── base_agent.py        # Agent基类
│   ├── researcher.py        # 研究Agent
│   ├── writer.py            # 撰写Agent
│   ├── reviewer.py          # 审核Agent
│   └── manager.py           # 管理Agent
├── tools/
│   ├── search.py            # 搜索工具
│   ├── file_ops.py          # 文件操作
│   └── notify.py            # 通知工具
├── workflow/
│   ├── task.py              # 任务定义
│   └── executor.py          # 执行器
├── output/                  # 输出目录
└── requirements.txt
```

---

## 💻 核心代码

### config.py

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    OUTPUT_DIR: str = "./output"
    MAX_AGENT_STEPS: int = 10
    MAX_RETRIES: int = 3

settings = Settings()
```

### agents/base_agent.py

```python
from openai import OpenAI
from abc import ABC, abstractmethod
import re
import os
from config import settings

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, role_prompt: str, tools: dict = None):
        self.name = name
        self.role_prompt = role_prompt
        self.tools = tools or {}
        
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
    
    def _build_react_prompt(self, task: str, scratchpad: str) -> str:
        tools_desc = "\n".join([
            f"- {name}: {func.__doc__ or '无描述'}"
            for name, func in self.tools.items()
        ])
        
        return f"""{self.role_prompt}

请使用ReAct格式思考和行动：

Thought: 你的思考过程
Action: 工具名(参数)

完成任务时：
Thought: 任务完成
Action: finish(最终结果)

可用工具：
{tools_desc}
- finish: 完成任务并返回结果

任务: {task}

{scratchpad}
请继续："""
    
    def _parse_action(self, response: str) -> tuple:
        match = re.search(r"Action:\s*(\w+)\((.+?)\)", response, re.DOTALL)
        if match:
            return match.group(1), match.group(2).strip().strip('"\'')
        return None, None
    
    def run(self, task: str) -> str:
        """执行ReAct循环"""
        scratchpad = ""
        
        for step in range(settings.MAX_AGENT_STEPS):
            prompt = self._build_react_prompt(task, scratchpad)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            output = response.choices[0].message.content
            print(f"\n[{self.name}] Step {step + 1}:\n{output}")
            
            action, args = self._parse_action(output)
            
            if action == "finish":
                return args
            
            if action and action in self.tools:
                try:
                    result = self.tools[action](args)
                    scratchpad += f"\n{output}\nObservation: {result}\n"
                except Exception as e:
                    scratchpad += f"\n{output}\nObservation: 错误 - {e}\n"
            else:
                scratchpad += f"\n{output}\nObservation: 未知工具或格式错误\n"
        
        return "达到最大步骤数"
```

### tools/search.py

```python
def search(query: str) -> str:
    """搜索信息（模拟）"""
    knowledge = {
        "fastapi": "FastAPI是现代Python Web框架，性能卓越，支持异步，自动生成API文档。",
        "python": "Python是广泛使用的编程语言，简洁易读，生态丰富。",
        "rag": "RAG(检索增强生成)结合检索和生成，提高AI回答准确性。",
        "agent": "AI Agent是具有自主决策能力的智能系统，可使用工具完成任务。"
    }
    
    query_lower = query.lower()
    results = []
    for key, value in knowledge.items():
        if key in query_lower:
            results.append(value)
    
    return "\n".join(results) if results else "未找到相关信息"
```

### tools/file_ops.py

```python
import os
from config import settings

def save_file(args: str) -> str:
    """保存文件。格式：文件名|内容"""
    parts = args.split("|", 1)
    if len(parts) != 2:
        return "格式错误，使用：文件名|内容"
    
    filename, content = parts
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return f"已保存到 {filepath}"

def read_file(filepath: str) -> str:
    """读取文件内容"""
    full_path = os.path.join(settings.OUTPUT_DIR, filepath)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"文件不存在: {filepath}"
```

### agents/researcher.py

```python
from agents.base_agent import BaseAgent
from tools.search import search

class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="研究员",
            role_prompt="""你是一个专业的研究员。
你的职责是：
1. 分析研究主题
2. 搜索相关信息
3. 整理研究发现
4. 输出结构化的调研报告

请深入调研，提供有价值的信息。""",
            tools={"search": search}
        )
```

### agents/writer.py

```python
from agents.base_agent import BaseAgent
from tools.file_ops import save_file

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="撰稿人",
            role_prompt="""你是一个专业的内容撰稿人。
你的职责是：
1. 根据调研资料撰写文章
2. 确保内容准确、结构清晰
3. 使用专业但易懂的语言
4. 保存文章到文件

请产出高质量的内容。""",
            tools={"save_file": save_file}
        )
```

### agents/reviewer.py

```python
from agents.base_agent import BaseAgent
from tools.file_ops import read_file

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="审核员",
            role_prompt="""你是一个严格的内容审核员。
你的职责是：
1. 读取文章内容
2. 检查信息准确性
3. 评估结构完整性
4. 提出修改建议

如果通过审核，输出"APPROVED"。否则输出具体问题。""",
            tools={"read_file": read_file}
        )
```

### agents/manager.py

```python
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from agents.reviewer import ReviewerAgent
from config import settings

class ManagerAgent:
    """管理Agent，协调工作流"""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.reviewer = ReviewerAgent()
    
    def run_workflow(self, topic: str) -> dict:
        """执行完整工作流"""
        print(f"\n{'='*60}")
        print(f"开始工作流：{topic}")
        print(f"{'='*60}")
        
        results = {"topic": topic, "steps": []}
        
        # Step 1: 研究
        print("\n📊 [阶段1] 调研中...")
        research_result = self.researcher.run(f"深入调研：{topic}")
        results["steps"].append({"stage": "research", "output": research_result})
        
        # Step 2: 撰写
        print("\n✍️ [阶段2] 撰写中...")
        write_task = f"根据以下调研内容撰写文章并保存为article.md：\n{research_result}"
        write_result = self.writer.run(write_task)
        results["steps"].append({"stage": "write", "output": write_result})
        
        # Step 3: 审核（带重试）
        for attempt in range(settings.MAX_RETRIES):
            print(f"\n🔍 [阶段3] 审核中... (第{attempt + 1}次)")
            review_result = self.reviewer.run("读取article.md并审核内容质量")
            results["steps"].append({"stage": f"review_{attempt + 1}", "output": review_result})
            
            if "APPROVED" in review_result.upper():
                results["status"] = "success"
                results["final_review"] = review_result
                break
            
            # 需要修改
            print("\n📝 [阶段3b] 修改中...")
            rewrite_task = f"修改文章，需要改进：{review_result}\n原调研内容：{research_result}"
            self.writer.run(rewrite_task)
        else:
            results["status"] = "needs_human_review"
            results["final_review"] = "多次审核未通过，需要人工介入"
        
        print(f"\n{'='*60}")
        print(f"工作流完成！状态：{results['status']}")
        print(f"{'='*60}")
        
        return results
```

### main.py

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents.manager import ManagerAgent
import os

app = FastAPI(title="智能工作流Agent系统")

# 确保输出目录
os.makedirs("./output", exist_ok=True)

manager = ManagerAgent()

class WorkflowRequest(BaseModel):
    topic: str

class WorkflowResponse(BaseModel):
    topic: str
    status: str
    steps: list

@app.post("/workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    """执行工作流"""
    result = manager.run_workflow(request.topic)
    return WorkflowResponse(
        topic=result["topic"],
        status=result.get("status", "unknown"),
        steps=result["steps"]
    )

@app.get("/")
async def index():
    return {"message": "智能工作流Agent系统", "endpoint": "/workflow"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
```

### requirements.txt

```
fastapi>=0.100.0
uvicorn>=0.23.0
openai>=1.0.0
pydantic-settings>=2.0.0
```

---

## 🚀 运行项目

```bash
cd week6/projects/project_workflow_agent
pip install -r requirements.txt
export DEEPSEEK_API_KEY=your-key
python main.py
```

### 测试API

```bash
curl -X POST http://localhost:8003/workflow \
  -H "Content-Type: application/json" \
  -d '{"topic": "FastAPI框架入门指南"}'
```

---

## 📋 工作流示例

```
开始工作流：FastAPI框架入门指南
============================================================

📊 [阶段1] 调研中...
[研究员] Step 1:
Thought: 我需要搜索FastAPI的相关信息
Action: search(fastapi)
Observation: FastAPI是现代Python Web框架...

[研究员] Step 2:
Thought: 已获取信息，整理调研报告
Action: finish(FastAPI调研报告：...)

✍️ [阶段2] 撰写中...
[撰稿人] Step 1:
Thought: 根据调研内容撰写文章
Action: save_file(article.md|# FastAPI入门指南...)

🔍 [阶段3] 审核中... (第1次)
[审核员] Step 1:
Thought: 读取并审核文章
Action: read_file(article.md)
Observation: # FastAPI入门指南...

[审核员] Step 2:
Thought: 文章内容完整，质量合格
Action: finish(APPROVED - 文章结构清晰，内容准确)

============================================================
工作流完成！状态：success
============================================================
```

---

## ✅ 验收标准

- [ ] 三个Agent能正确协作
- [ ] ReAct推理过程清晰
- [ ] 工具调用正常
- [ ] 审核不通过时能重试
- [ ] 文章正确保存

---

## 🔥 进阶挑战

1. **添加更多工具**：网络搜索、代码执行
2. **并行Agent**：同时执行多个调研任务
3. **人工介入**：支持人工确认关键步骤
4. **可视化界面**：展示Agent思考过程
5. **LangGraph集成**：使用图结构管理工作流
