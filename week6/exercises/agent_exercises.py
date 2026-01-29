"""
Week 6 练习：AI Agent开发
=========================

完成以下练习来掌握Agent开发技术。
"""

import os
import json
from typing import Callable, Dict, Any

# ============================================================
# 练习1: 工具开发
# ============================================================

"""
练习1.1: 实现一个安全的计算器工具

要求：
1. 只允许数学运算符和数字
2. 有错误处理
3. 有输入验证

提示：使用正则表达式验证输入
"""

def exercise_1_1():
    def safe_calculator(expression: str) -> str:
        # TODO: 实现安全计算器
        # 1. 验证输入只包含数字和运算符
        # 2. 计算结果
        # 3. 处理异常
        pass
    
    # 测试
    print(safe_calculator("2 + 3 * 4"))     # 应该返回: 14
    print(safe_calculator("10 / 0"))        # 应该返回错误信息
    print(safe_calculator("import os"))     # 应该返回错误信息


"""
练习1.2: 实现一个文件操作工具

要求：
1. read_file(path) - 读取文件
2. write_file(path, content) - 写入文件
3. list_dir(path) - 列出目录
4. 限制只能访问特定目录
"""

def exercise_1_2():
    ALLOWED_DIR = "./workspace"
    
    def read_file(path: str) -> str:
        # TODO: 安全读取文件
        pass
    
    def write_file(path: str, content: str) -> str:
        # TODO: 安全写入文件
        pass
    
    def list_dir(path: str) -> str:
        # TODO: 安全列出目录
        pass


"""
练习1.3: 实现一个HTTP请求工具

要求：
1. 支持GET和POST
2. 超时处理
3. 错误处理
4. 返回格式化的响应
"""

def exercise_1_3():
    import requests
    
    def http_request(url: str, method: str = "GET", body: str = None) -> str:
        # TODO: 实现HTTP请求工具
        pass


# ============================================================
# 练习2: ReAct实现
# ============================================================

"""
练习2.1: 实现ReAct Prompt解析器

要求：
1. 解析Thought/Action格式
2. 提取工具名和参数
3. 处理各种格式异常

格式：
Thought: 思考过程
Action: tool_name(argument)
"""

def exercise_2_1():
    import re
    
    def parse_react_output(output: str) -> dict:
        """
        解析ReAct输出
        返回: {"thought": str, "action": str, "action_input": str}
        """
        # TODO: 实现解析逻辑
        pass
    
    # 测试
    test_output = """
    Thought: 我需要搜索FastAPI的信息
    Action: search(FastAPI是什么)
    """
    
    result = parse_react_output(test_output)
    print(result)
    # 预期: {"thought": "我需要搜索FastAPI的信息", "action": "search", "action_input": "FastAPI是什么"}


"""
练习2.2: 实现完整的ReAct循环

要求：
1. 维护思考-行动-观察历史
2. 最大步骤限制
3. 支持finish动作退出
4. 详细的执行日志
"""

def exercise_2_2():
    from openai import OpenAI
    
    class SimpleReActAgent:
        def __init__(self, tools: dict):
            self.tools = tools
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1"
            )
        
        def run(self, task: str, max_steps: int = 5) -> str:
            # TODO: 实现ReAct循环
            pass
    
    # 测试
    tools = {
        "search": lambda q: f"搜索结果: {q}",
        "calculate": lambda e: str(eval(e)),
    }
    
    agent = SimpleReActAgent(tools)
    # result = agent.run("计算2+3的结果")


# ============================================================
# 练习3: 多Agent系统
# ============================================================

"""
练习3.1: 实现Agent基类

要求：
1. 统一的接口设计
2. 支持不同角色
3. 消息传递机制
"""

def exercise_3_1():
    from abc import ABC, abstractmethod
    
    class BaseAgent(ABC):
        def __init__(self, name: str, role: str):
            self.name = name
            self.role = role
        
        @abstractmethod
        def process(self, message: str) -> str:
            """处理消息并返回结果"""
            pass
    
    # TODO: 实现具体的Agent
    class ResearcherAgent(BaseAgent):
        def process(self, message: str) -> str:
            pass
    
    class WriterAgent(BaseAgent):
        def process(self, message: str) -> str:
            pass


"""
练习3.2: 实现顺序执行的多Agent流水线

要求：
1. Agent A处理 → Agent B处理 → Agent C处理
2. 每个Agent有不同的职责
3. 结果逐步传递
"""

def exercise_3_2():
    class Pipeline:
        def __init__(self, agents: list):
            self.agents = agents
        
        def run(self, initial_input: str) -> str:
            # TODO: 实现流水线执行
            pass
    
    # 测试
    # pipeline = Pipeline([researcher, writer, reviewer])
    # result = pipeline.run("写一篇关于FastAPI的文章")


"""
练习3.3: 实现对话式多Agent系统

要求：
1. 多个Agent轮流发言
2. 支持设定最大轮次
3. 主持人总结
"""

def exercise_3_3():
    class DebateSystem:
        def __init__(self, agents: list):
            self.agents = agents
        
        def debate(self, topic: str, rounds: int = 2) -> str:
            # TODO: 实现辩论系统
            pass


# ============================================================
# 练习4: 综合挑战
# ============================================================

"""
练习4.1: 构建一个任务规划Agent

要求：
1. 接收复杂任务
2. 自动分解成子任务
3. 按顺序执行子任务
4. 汇总结果
"""

def exercise_4_1():
    class PlanningAgent:
        def __init__(self):
            pass
        
        def plan(self, task: str) -> list:
            """将任务分解为子任务列表"""
            pass
        
        def execute(self, task: str) -> str:
            """执行完整任务"""
            pass


"""
练习4.2: 构建一个自我反思Agent

要求：
1. 执行任务
2. 评估结果
3. 如果不满意，改进后重试
4. 最多重试3次
"""

def exercise_4_2():
    class SelfReflectAgent:
        def __init__(self):
            pass
        
        def execute_with_reflection(self, task: str, max_retries: int = 3) -> str:
            # TODO: 实现自我反思逻辑
            pass


# ============================================================
# 参考答案
# ============================================================

def answer_1_1():
    """练习1.1参考答案"""
    import re
    
    def safe_calculator(expression: str) -> str:
        # 验证输入
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含非法字符"
        
        # 禁止关键字
        if any(kw in expression.lower() for kw in ['import', 'exec', 'eval', '__']):
            return "错误：检测到危险操作"
        
        try:
            result = eval(expression)
            return f"计算结果: {result}"
        except ZeroDivisionError:
            return "错误：除数不能为零"
        except SyntaxError:
            return "错误：表达式格式不正确"
        except Exception as e:
            return f"错误：{str(e)}"
    
    print(safe_calculator("2 + 3 * 4"))
    print(safe_calculator("10 / 0"))
    print(safe_calculator("import os"))


def answer_2_1():
    """练习2.1参考答案"""
    import re
    
    def parse_react_output(output: str) -> dict:
        result = {"thought": "", "action": "", "action_input": ""}
        
        # 提取Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", output, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()
        
        # 提取Action
        action_match = re.search(r"Action:\s*(\w+)\((.+?)\)", output)
        if action_match:
            result["action"] = action_match.group(1)
            result["action_input"] = action_match.group(2).strip().strip('"\'')
        
        return result
    
    test_output = """
    Thought: 我需要搜索FastAPI的信息
    Action: search(FastAPI是什么)
    """
    
    result = parse_react_output(test_output)
    print(result)


if __name__ == "__main__":
    print("Week 6 练习")
    print("=" * 50)
    print("请取消注释并运行各个练习函数")
    
    # exercise_1_1()
    # exercise_2_1()
    # exercise_3_1()
    
    # 参考答案
    # answer_1_1()
    # answer_2_1()
