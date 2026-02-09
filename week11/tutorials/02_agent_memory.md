# 💾 Agent记忆系统

> **学习目标**：为Agent实现短期和长期记忆，支持上下文理解

---

## 1. 记忆系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent记忆系统架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    短期记忆 (Working Memory)              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │ 当前对话    │  │ 会话上下文  │  │ 临时变量    │       │  │
│  │  │ (最近N轮)   │  │ (用户意图)  │  │ (计算结果)  │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ 重要信息提取                      │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    长期记忆 (Long-term Memory)            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │ 用户画像    │  │ 历史摘要    │  │ 知识积累    │       │  │
│  │  │ (偏好/习惯) │  │ (重要事件)  │  │ (学到的)    │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 短期记忆实现

### 2.1 滑动窗口记忆

```python
from collections import deque
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Message:
    """消息"""
    role: str
    content: str
    timestamp: str
    metadata: dict = None

class SlidingWindowMemory:
    """滑动窗口记忆"""
    
    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.messages: deque = deque(maxlen=max_messages)
    
    def add(self, role: str, content: str, metadata: dict = None):
        """添加消息"""
        self.messages.append(Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        ))
    
    def get_context(self, include_system: bool = True) -> list[dict]:
        """获取上下文消息"""
        context = []
        total_tokens = 0
        
        # 从最新消息开始，直到达到token限制
        for msg in reversed(self.messages):
            msg_tokens = len(msg.content) // 4  # 粗略估计
            if total_tokens + msg_tokens > self.max_tokens:
                break
            
            context.insert(0, {
                "role": msg.role,
                "content": msg.content
            })
            total_tokens += msg_tokens
        
        return context
    
    def clear(self):
        """清空记忆"""
        self.messages.clear()

# 使用
memory = SlidingWindowMemory(max_messages=20)
memory.add("user", "你好")
memory.add("assistant", "你好！有什么我可以帮助你的吗？")
context = memory.get_context()
```

### 2.2 带摘要的记忆

```python
from openai import OpenAI

class SummarizedMemory:
    """带摘要压缩的记忆"""
    
    def __init__(self, recent_limit: int = 10, summary_threshold: int = 20):
        self.client = OpenAI()
        self.recent_limit = recent_limit
        self.summary_threshold = summary_threshold
        self.recent_messages: list = []
        self.summary: str = ""
    
    def add(self, role: str, content: str):
        """添加消息"""
        self.recent_messages.append({"role": role, "content": content})
        
        # 如果消息过多，进行摘要压缩
        if len(self.recent_messages) > self.summary_threshold:
            self._compress()
    
    def _compress(self):
        """压缩历史消息为摘要"""
        # 保留最近的消息
        to_summarize = self.recent_messages[:-self.recent_limit]
        self.recent_messages = self.recent_messages[-self.recent_limit:]
        
        # 生成摘要
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}" for m in to_summarize
        ])
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "请总结以下对话的关键信息，保留重要的事实和用户偏好。"},
                {"role": "user", "content": conversation_text}
            ]
        )
        
        new_summary = response.choices[0].message.content
        
        # 合并新旧摘要
        if self.summary:
            self.summary = f"{self.summary}\n\n最近补充：{new_summary}"
        else:
            self.summary = new_summary
    
    def get_context(self) -> list[dict]:
        """获取带摘要的上下文"""
        context = []
        
        if self.summary:
            context.append({
                "role": "system",
                "content": f"之前对话摘要：\n{self.summary}"
            })
        
        context.extend(self.recent_messages)
        return context

# 使用
memory = SummarizedMemory()
for i in range(30):
    memory.add("user", f"问题{i}")
    memory.add("assistant", f"回答{i}")
context = memory.get_context()
```

---

## 3. 长期记忆实现

### 3.1 用户画像存储

```python
from pydantic import BaseModel
from datetime import datetime

class UserProfile(BaseModel):
    """用户画像"""
    user_id: str
    name: str = ""
    preferences: dict = {}
    interaction_history: list = []
    learned_facts: list = []
    last_updated: datetime = None

class UserProfileStore:
    """用户画像存储"""
    
    def __init__(self, db_path: str = "user_profiles.json"):
        self.db_path = db_path
        self.profiles: dict[str, UserProfile] = {}
        self._load()
    
    def _load(self):
        """加载数据"""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                for user_id, profile_data in data.items():
                    self.profiles[user_id] = UserProfile(**profile_data)
        except FileNotFoundError:
            pass
    
    def _save(self):
        """保存数据"""
        data = {uid: p.model_dump() for uid, p in self.profiles.items()}
        with open(self.db_path, 'w') as f:
            json.dump(data, f, default=str)
    
    def get_or_create(self, user_id: str) -> UserProfile:
        """获取或创建用户画像"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id=user_id)
            self._save()
        return self.profiles[user_id]
    
    def update_preference(self, user_id: str, key: str, value):
        """更新用户偏好"""
        profile = self.get_or_create(user_id)
        profile.preferences[key] = value
        profile.last_updated = datetime.now()
        self._save()
    
    def add_learned_fact(self, user_id: str, fact: str):
        """添加学习到的事实"""
        profile = self.get_or_create(user_id)
        if fact not in profile.learned_facts:
            profile.learned_facts.append(fact)
            self._save()

# 使用
store = UserProfileStore()
store.update_preference("user123", "language", "zh-CN")
store.add_learned_fact("user123", "用户是软件工程师")
```

### 3.2 向量化长期记忆

```python
import chromadb
from openai import OpenAI

class VectorMemory:
    """向量化长期记忆"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = OpenAI()
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection(
            name=f"user_{user_id}_memory"
        )
    
    def store(self, content: str, memory_type: str = "general"):
        """存储记忆"""
        # 生成嵌入
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )
        embedding = response.data[0].embedding
        
        # 存储到向量数据库
        memory_id = f"mem_{datetime.now().timestamp()}"
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "type": memory_type,
                "timestamp": datetime.now().isoformat()
            }]
        )
    
    def recall(self, query: str, n_results: int = 5) -> list[str]:
        """回忆相关记忆"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results["documents"][0] if results["documents"] else []

# 使用
memory = VectorMemory("user123")
memory.store("用户喜欢Python编程", "preference")
memory.store("用户正在学习机器学习", "context")

related = memory.recall("推荐什么编程项目？")
print(related)  # ['用户喜欢Python编程', '用户正在学习机器学习']
```

---

## 4. 综合记忆系统

```python
class AgentMemorySystem:
    """Agent综合记忆系统"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term = SummarizedMemory()
        self.long_term = VectorMemory(user_id)
        self.profile = UserProfileStore().get_or_create(user_id)
    
    def process_interaction(self, user_input: str, agent_response: str):
        """处理交互，更新记忆"""
        # 更新短期记忆
        self.short_term.add("user", user_input)
        self.short_term.add("assistant", agent_response)
        
        # 提取并存储重要信息到长期记忆
        important_info = self._extract_important_info(user_input, agent_response)
        if important_info:
            self.long_term.store(important_info)
    
    def _extract_important_info(self, user_input: str, response: str) -> str:
        """提取重要信息"""
        # 可以用LLM提取关键信息
        client = OpenAI()
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "提取对话中值得长期记住的关键信息。如果没有重要信息，返回空字符串。"},
                {"role": "user", "content": f"用户: {user_input}\nAI: {response}"}
            ]
        )
        return result.choices[0].message.content.strip()
    
    def get_full_context(self, current_query: str) -> str:
        """获取完整上下文"""
        # 相关的长期记忆
        related_memories = self.long_term.recall(current_query, n_results=3)
        
        context = f"用户信息: {self.profile.name}, 偏好: {self.profile.preferences}\n"
        
        if related_memories:
            context += f"相关记忆: {'; '.join(related_memories)}\n"
        
        return context

# 使用
memory_system = AgentMemorySystem("user123")
memory_system.process_interaction(
    "我最近在学习FastAPI",
    "太好了！FastAPI是一个很棒的框架..."
)
```

---

## 5. 学习检查清单

- [ ] 理解短期和长期记忆的区别
- [ ] 能够实现滑动窗口记忆
- [ ] 会实现带摘要压缩的记忆
- [ ] 能够构建向量化长期记忆

---

## 继续学习

📌 **Week 11 学习顺序**：
1. ✅ 生产级Agent架构
2. ✅ Agent记忆系统（本教程）
3. ➡️ 多Agent协作
