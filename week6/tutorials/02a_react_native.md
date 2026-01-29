# ⚡ ReAct框架实现

> **学习目标**：掌握ReAct（Reasoning + Acting）框架的原理与实现

---

## 1. ReAct原理

**ReAct** = Reasoning（推理）+ Acting（行动）

```
Thought: 我需要先搜索FastAPI的信息
Action: search("FastAPI是什么")
Observation: FastAPI是高性能Python Web框架
Thought: 现在我知道了，可以回答用户
Action: finish("FastAPI是高性能Python框架")
```

### ReAct vs 普通Agent

| 普通Agent | ReAct Agent |
|-----------|-------------|
| 直接选择动作 | 先思考再行动 |
| 决策过程不透明 | 思考过程可见 |
| 容易出错 | 更准确可控 |

---

## 2. ReAct Prompt模板

```python
REACT_PROMPT = """你是一个ReAct智能助手。请按照以下格式思考和行动：

Thought: 你的思考过程
Action: 工具名称(参数)
Observation: 工具返回的结果
... (重复Thought/Action/Observation)
Thought: 我现在可以给出最终答案了
Action: finish(最终答案)

可用工具：
{tools_description}

开始！

问题: {question}
{agent_scratchpad}
"""
```

---

## 3. 完整ReAct实现

```python
from openai import OpenAI
import re
import os
from typing import Callable, Any

class ReActAgent:
    """ReAct框架Agent实现"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        
        self.tools: dict[str, Callable] = {}
        self.tool_descriptions: list[str] = []
    
    def register_tool(self, name: str, func: Callable, description: str):
        """注册工具"""
        self.tools[name] = func
        self.tool_descriptions.append(f"- {name}: {description}")
    
    def _build_prompt(self, question: str, scratchpad: str) -> str:
        """构建ReAct Prompt"""
        tools_desc = "\n".join(self.tool_descriptions)
        
        return f"""你是一个ReAct智能助手。请严格按照以下格式思考和行动：

Thought: 你的思考过程（分析问题，决定下一步）
Action: 工具名称(参数)

或者如果你已经可以回答：
Thought: 我现在可以给出最终答案了
Action: finish(答案内容)

## 可用工具

{tools_desc}

## 重要规则

1. 每次只输出一个Thought和一个Action
2. Action格式必须是: 工具名(参数)
3. 如果遇到问题需要更多信息，使用工具获取
4. 得到足够信息后，使用finish()给出最终答案

开始！

问题: {question}

{scratchpad}"""
    
    def _parse_action(self, response: str) -> tuple[str, str]:
        """解析LLM响应中的Action"""
        # 匹配 Action: tool_name(args) 格式
        action_pattern = r"Action:\s*(\w+)\((.*?)\)"
        match = re.search(action_pattern, response, re.DOTALL)
        
        if match:
            tool_name = match.group(1)
            args = match.group(2).strip().strip('"\'')
            return tool_name, args
        
        return None, None
    
    def _execute_tool(self, tool_name: str, args: str) -> str:
        """执行工具"""
        if tool_name not in self.tools:
            return f"错误：未知工具 '{tool_name}'"
        
        try:
            result = self.tools[tool_name](args)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def run(self, question: str, max_steps: int = 10, verbose: bool = True) -> str:
        """执行ReAct循环"""
        scratchpad = ""
        
        for step in range(max_steps):
            # 1. 构建Prompt
            prompt = self._build_prompt(question, scratchpad)
            
            # 2. 调用LLM
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )
            
            llm_output = response.choices[0].message.content
            
            if verbose:
                print(f"\n{'='*50}")
                print(f"Step {step + 1}")
                print(f"{'='*50}")
                print(llm_output)
            
            # 3. 解析Action
            tool_name, args = self._parse_action(llm_output)
            
            if not tool_name:
                scratchpad += f"\n{llm_output}\nObservation: 无法解析动作格式，请使用正确格式。\n"
                continue
            
            # 4. 检查是否完成
            if tool_name.lower() == "finish":
                if verbose:
                    print(f"\n✅ 任务完成!")
                return args
            
            # 5. 执行工具
            observation = self._execute_tool(tool_name, args)
            
            if verbose:
                print(f"Observation: {observation}")
            
            # 6. 更新scratchpad
            scratchpad += f"\n{llm_output}\nObservation: {observation}\n"
        
        return "达到最大步骤数，任务未完成"


# ===== 工具函数 =====

def search(query: str) -> str:
    """模拟搜索引擎"""
    knowledge = {
        "fastapi": "FastAPI是一个现代、快速的Python Web框架，性能与Go和Node.js相当",
        "python": "Python是一种高级编程语言，以简洁易读著称",
        "rag": "RAG(检索增强生成)是一种将检索和生成结合的AI技术",
        "agent": "AI Agent是具有自主决策和行动能力的智能系统",
    }
    
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return value
    
    return "未找到相关信息"

def calculator(expression: str) -> str:
    """计算器"""
    try:
        # 安全的数学计算
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return "表达式包含非法字符"
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

def get_weather(city: str) -> str:
    """模拟天气API"""
    weather_data = {
        "北京": "晴，温度25°C",
        "上海": "多云，温度28°C",
        "深圳": "雨，温度30°C",
    }
    return weather_data.get(city, f"未找到{city}的天气信息")


# ===== 使用示例 =====

if __name__ == "__main__":
    # 创建Agent
    agent = ReActAgent()
    
    # 注册工具
    agent.register_tool("search", search, "搜索信息，参数为查询关键词")
    agent.register_tool("calculator", calculator, "计算数学表达式")
    agent.register_tool("get_weather", get_weather, "获取城市天气")
    
    # 测试1：需要搜索
    print("\n" + "="*60)
    print("测试1: 搜索问题")
    print("="*60)
    result = agent.run("FastAPI是什么？有什么特点？")
    print(f"\n最终答案: {result}")
    
    # 测试2：需要计算
    print("\n" + "="*60)
    print("测试2: 计算问题")
    print("="*60)
    result = agent.run("计算 (100 + 50) * 2 - 80 的结果")
    print(f"\n最终答案: {result}")
    
    # 测试3：组合任务
    print("\n" + "="*60)
    print("测试3: 组合问题")
    print("="*60)
    result = agent.run("北京今天天气怎么样？如果温度大于20度，帮我计算20+5的结果")
    print(f"\n最终答案: {result}")
```

---

## 4. ReAct输出示例

```
==================================================
Step 1
==================================================
Thought: 用户想知道FastAPI是什么以及它的特点。我需要先搜索相关信息。
Action: search(FastAPI)
Observation: FastAPI是一个现代、快速的Python Web框架，性能与Go和Node.js相当

==================================================
Step 2
==================================================
Thought: 我已经获得了FastAPI的基本信息，现在可以给出最终答案了。
Action: finish(FastAPI是一个现代、快速的Python Web框架。它的主要特点是性能出色，可以与Go和Node.js相媲美。)

✅ 任务完成!

最终答案: FastAPI是一个现代、快速的Python Web框架。它的主要特点是性能出色，可以与Go和Node.js相媲美。
```

---

## 5. 改进：带记忆的ReAct

```python
class ReActAgentWithMemory(ReActAgent):
    """带记忆的ReAct Agent"""
    
    def __init__(self):
        super().__init__()
        self.memory = []  # 历史记录
    
    def run(self, question: str, max_steps: int = 10) -> str:
        # 构建历史上下文
        history = ""
        if self.memory:
            history = "## 历史对话\n"
            for q, a in self.memory[-3:]:  # 保留最近3轮
                history += f"Q: {q}\nA: {a}\n\n"
        
        # 执行ReAct
        result = super().run(question, max_steps)
        
        # 保存到记忆
        self.memory.append((question, result))
        
        return result
```

---

## 6. 异步ReAct

```python
import asyncio

class AsyncReActAgent(ReActAgent):
    """异步ReAct Agent"""
    
    async def run_async(self, question: str, max_steps: int = 10) -> str:
        # 异步执行ReAct循环
        return await asyncio.to_thread(self.run, question, max_steps)
    
    async def run_batch(self, questions: list[str]) -> list[str]:
        """批量执行多个问题"""
        tasks = [self.run_async(q) for q in questions]
        return await asyncio.gather(*tasks)

# 使用
async def main():
    agent = AsyncReActAgent()
    agent.register_tool("search", search, "搜索")
    
    results = await agent.run_batch([
        "什么是Python?",
        "什么是RAG?"
    ])
    for r in results:
        print(r)

asyncio.run(main())
```

---

## 📺 推荐B站视频

搜索：
- **"ReAct Agent 实现"**
- **"LLM 推理框架"**
- **"AI Agent ReAct"**

---

## 7. 继续学习

📌 **Week 6 学习顺序**：
1. ✅ Agent基础概念
2. ✅ ReAct框架实现（本教程）
3. ➡️ 工具使用详解
4. ➡️ 多Agent系统

---

**ReAct让Agent的思考过程透明可控！💪**
