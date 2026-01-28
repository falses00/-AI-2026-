"""
Week 2 练习题：DeepSeek API 基础

完成以下练习，巩固API调用技能

运行方式:
    cd "i:\Study FastAPI"
    D:\Anaconda\envs\pytorch_Gpu\python.exe week2/exercises/api_exercises.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.deepseek_client import get_client, chat_completion
import json


# ============================================================
# 练习1：基础API调用
# ============================================================

def exercise_1_basic_call():
    """
    练习1：基础API调用
    
    任务：
    1. 使用chat_completion函数
    2. 让AI用英文回答问题
    3. 问题："Python有什么优点？"
    
    完成下面的代码：
    """
    # TODO: 调用chat_completion，设置system_prompt为英文回答要求
    # response = chat_completion(...)
    
    # 取消注释下面的代码来测试
    # print("=" * 50)
    # print("练习1：基础API调用")
    # print("=" * 50)
    # print(response)
    pass


# ============================================================
# 练习2：温度参数对比
# ============================================================

def exercise_2_temperature():
    """
    练习2：温度参数对比
    
    任务：
    1. 使用相同的提示词
    2. 分别用temperature=0和temperature=1.5调用
    3. 比较输出的差异
    
    提示词："用一句话描述人工智能"
    """
    client = get_client()
    
    prompt = "用一句话描述人工智能"
    
    # TODO: 调用两次API，分别使用不同的temperature
    # response_low = client.chat.completions.create(...)
    # response_high = client.chat.completions.create(...)
    
    # 取消注释下面的代码来测试
    # print("=" * 50)
    # print("练习2：温度参数对比")
    # print("=" * 50)
    # print(f"低温度(0): {response_low.choices[0].message.content}")
    # print(f"高温度(1.5): {response_high.choices[0].message.content}")
    pass


# ============================================================
# 练习3：多轮对话
# ============================================================

def exercise_3_multi_turn():
    """
    练习3：多轮对话
    
    任务：
    1. 创建一个支持多轮对话的函数
    2. 维护对话历史
    3. 进行3轮对话测试
    
    对话内容：
    - 第1轮："我叫张三，是一名程序员"
    - 第2轮："我最喜欢的编程语言是Python"
    - 第3轮："请总结一下你对我的了解"
    """
    client = get_client()
    messages = [
        {"role": "system", "content": "你是一个友好的聊天助手，会记住用户告诉你的信息。"}
    ]
    
    def chat(user_message: str) -> str:
        # TODO: 实现多轮对话
        # 1. 添加用户消息到messages
        # 2. 调用API
        # 3. 提取并保存助手回复
        # 4. 返回助手回复
        pass
    
    # 取消注释下面的代码来测试
    # print("=" * 50)
    # print("练习3：多轮对话")
    # print("=" * 50)
    # print(f"用户: 我叫张三，是一名程序员")
    # print(f"AI: {chat('我叫张三，是一名程序员')}")
    # print()
    # print(f"用户: 我最喜欢的编程语言是Python")
    # print(f"AI: {chat('我最喜欢的编程语言是Python')}")
    # print()
    # print(f"用户: 请总结一下你对我的了解")
    # print(f"AI: {chat('请总结一下你对我的了解')}")
    pass


# ============================================================
# 练习4：结构化输出
# ============================================================

def exercise_4_structured_output():
    """
    练习4：结构化输出
    
    任务：
    1. 分析一段文本的情感
    2. 返回JSON格式的结果
    3. 包含：sentiment(positive/negative/neutral), score(0-1), reason
    
    测试文本："虽然今天很累，但完成了一个重要项目，感觉很有成就感！"
    """
    client = get_client()
    
    text = "虽然今天很累，但完成了一个重要项目，感觉很有成就感！"
    
    # TODO: 实现结构化输出
    # 1. 设计system_prompt，要求返回指定格式的JSON
    # 2. 启用response_format={"type": "json_object"}
    # 3. 解析JSON结果
    
    # 取消注释下面的代码来测试
    # print("=" * 50)
    # print("练习4：结构化输出")
    # print("=" * 50)
    # print(f"文本: {text}")
    # print(f"分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    pass


# ============================================================
# 练习5：创建专业领域助手
# ============================================================

def exercise_5_specialized_assistant():
    """
    练习5：创建专业领域助手
    
    任务：
    1. 创建一个"Python代码审查助手"
    2. 系统提示词要求：
       - 角色：资深Python开发者
       - 只评审Python代码
       - 指出问题并给出改进建议
       - 使用结构化输出
    3. 输出JSON格式包含：issues(问题列表), suggestions(建议列表), rating(1-10分)
    
    测试代码：
    ```python
    def calc(x,y):
      result=x+y
      return result
    ```
    """
    client = get_client()
    
    code = '''def calc(x,y):
  result=x+y
  return result'''
    
    # TODO: 实现代码审查助手
    
    # 取消注释下面的代码来测试
    # print("=" * 50)
    # print("练习5：Python代码审查助手")
    # print("=" * 50)
    # print(f"待审查代码:\n{code}")
    # print(f"\n审查结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
    pass


# ============================================================
# 参考答案（先自己尝试！）
# ============================================================

def _answer_exercise_1():
    """练习1参考答案"""
    response = chat_completion(
        message="Python有什么优点？",
        system_prompt="Please answer all questions in English."
    )
    return response


def _answer_exercise_2():
    """练习2参考答案"""
    client = get_client()
    prompt = "用一句话描述人工智能"
    
    response_low = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    response_high = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.5
    )
    
    return (
        response_low.choices[0].message.content,
        response_high.choices[0].message.content
    )


def _answer_exercise_3():
    """练习3参考答案"""
    client = get_client()
    messages = [
        {"role": "system", "content": "你是一个友好的聊天助手，会记住用户告诉你的信息。"}
    ]
    
    def chat(user_message: str) -> str:
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    return chat


def _answer_exercise_4():
    """练习4参考答案"""
    client = get_client()
    
    text = "虽然今天很累，但完成了一个重要项目，感觉很有成就感！"
    
    system_prompt = """分析用户提供的文本情感。返回JSON格式：
{
    "sentiment": "positive" 或 "negative" 或 "neutral",
    "score": 0.0到1.0之间的数值,
    "reason": "判断原因的简短说明"
}"""
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    return json.loads(response.choices[0].message.content)


# ============================================================
# 运行入口
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Week 2 练习题：DeepSeek API 基础")
    print("=" * 60)
    print("\n请完成上面的练习函数，然后取消注释测试代码来验证。")
    print("\n运行参考答案：")
    print("-" * 60)
    
    # 运行参考答案示例
    print("\n✅ 练习1答案演示：")
    print(_answer_exercise_1()[:200] + "...")
    
    print("\n✅ 练习4答案演示：")
    result = _answer_exercise_4()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("完成练习后，继续学习下一个教程！")
    print("=" * 60)
