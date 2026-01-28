"""
DeepSeek API 配置和工具类

使用方法:
    from config.deepseek_client import get_client, chat_completion
    
    # 获取客户端
    client = get_client()
    
    # 或直接调用
    response = chat_completion("你好，请介绍一下自己")
"""

import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def get_client() -> OpenAI:
    """
    获取配置好的DeepSeek客户端
    
    DeepSeek API兼容OpenAI格式，只需更改base_url
    
    Returns:
        OpenAI: 配置好的客户端实例
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
    
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )


def chat_completion(
    message: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    system_prompt: str = "你是一个有帮助的AI助手。"
) -> str:
    """
    发送聊天请求并获取响应
    
    Args:
        message: 用户消息
        model: 模型名称，可选 "deepseek-chat" 或 "deepseek-reasoner"
        temperature: 随机性控制 (0-2)
        max_tokens: 最大输出token数
        system_prompt: 系统提示词
        
    Returns:
        str: AI的响应文本
    """
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content


def chat_completion_structured(
    message: str,
    response_format: dict,
    model: str = "deepseek-chat",
    system_prompt: str = "你是一个有帮助的AI助手。请按照要求的JSON格式返回结果。"
) -> dict:
    """
    发送聊天请求并获取结构化JSON响应
    
    Args:
        message: 用户消息
        response_format: JSON Schema格式定义
        model: 模型名称
        system_prompt: 系统提示词
        
    Returns:
        dict: 结构化的响应数据
    """
    import json
    
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


# 测试连接
if __name__ == "__main__":
    print("测试 DeepSeek API 连接...")
    print("-" * 50)
    
    try:
        response = chat_completion("你好！请用一句话介绍自己。")
        print(f"✅ API连接成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"❌ API连接失败: {e}")
