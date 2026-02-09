# 💬 对话交互设计

> **学习目标**：设计自然、高效的AI对话体验

---

## 1. 对话设计原则

### 1.1 用户期望管理

```
┌─────────────────────────────────────────────────────────────────┐
│                    对话设计金字塔                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────┐                              │
│                    │   愉悦感    │ ← 个性化、幽默感             │
│                    └──────┬──────┘                              │
│                   ┌───────┴───────┐                             │
│                   │    效率感     │ ← 快速解决问题              │
│                   └───────┬───────┘                             │
│              ┌────────────┴────────────┐                        │
│              │       可控感            │ ← 能修改、能中断        │
│              └────────────┬────────────┘                        │
│         ┌─────────────────┴─────────────────┐                   │
│         │          可预测感                  │ ← 知道AI能做什么  │
│         └─────────────────┬─────────────────┘                   │
│    ┌──────────────────────┴──────────────────────┐              │
│    │                 信任感                        │ ← 正确、安全  │
│    └─────────────────────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 对话流程设计

### 2.1 开场设计

```python
class ConversationOpener:
    """对话开场设计"""
    
    def __init__(self, product_name: str, capabilities: list[str]):
        self.product_name = product_name
        self.capabilities = capabilities
    
    def generate_greeting(self, user_name: str = None, time_of_day: str = "day") -> str:
        """生成个性化问候"""
        time_greetings = {
            "morning": "早上好",
            "afternoon": "下午好",
            "evening": "晚上好",
            "day": "你好"
        }
        
        greeting = time_greetings.get(time_of_day, "你好")
        
        if user_name:
            greeting = f"{greeting}，{user_name}"
        
        # 展示能力
        cap_list = "、".join(self.capabilities[:3])
        
        return f"""{greeting}！👋

我是{self.product_name}，可以帮你{cap_list}等。

有什么我可以帮助你的吗？"""

# 使用
opener = ConversationOpener(
    "智能助手",
    ["回答问题", "文档分析", "代码编写", "翻译"]
)
greeting = opener.generate_greeting("张三", "morning")
```

### 2.2 引导式对话

```python
class GuidedConversation:
    """引导式对话"""
    
    def __init__(self):
        self.conversation_tree = {
            "start": {
                "message": "请问您需要什么帮助？",
                "options": [
                    {"text": "📄 文档处理", "next": "document"},
                    {"text": "💬 问答咨询", "next": "qa"},
                    {"text": "🔧 技术支持", "next": "support"}
                ]
            },
            "document": {
                "message": "您想对文档做什么操作？",
                "options": [
                    {"text": "📖 文档总结", "next": "summarize"},
                    {"text": "🔍 信息提取", "next": "extract"},
                    {"text": "📝 文档问答", "next": "doc_qa"}
                ]
            }
        }
    
    def get_node(self, node_id: str) -> dict:
        """获取对话节点"""
        return self.conversation_tree.get(node_id, self.conversation_tree["start"])
    
    def format_options(self, node: dict) -> str:
        """格式化选项"""
        message = node["message"]
        options = node.get("options", [])
        
        if options:
            message += "\n\n请选择："
            for i, opt in enumerate(options, 1):
                message += f"\n{i}. {opt['text']}"
        
        return message

# 使用
guide = GuidedConversation()
node = guide.get_node("start")
print(guide.format_options(node))
```

---

## 3. 回复设计模式

### 3.1 结构化回复

```python
class ResponseFormatter:
    """回复格式化器"""
    
    def format_answer(
        self,
        answer: str,
        sources: list[str] = None,
        confidence: float = None,
        follow_ups: list[str] = None
    ) -> str:
        """格式化回答"""
        response = answer
        
        # 添加置信度提示
        if confidence is not None and confidence < 0.7:
            response = "⚠️ 我对这个回答不太确定：\n\n" + response
        
        # 添加来源
        if sources:
            response += "\n\n📚 **参考来源**："
            for i, src in enumerate(sources, 1):
                response += f"\n{i}. {src}"
        
        # 添加追问建议
        if follow_ups:
            response += "\n\n💡 **您可能还想问**："
            for q in follow_ups[:3]:
                response += f"\n• {q}"
        
        return response
    
    def format_error(self, error_type: str, suggestion: str) -> str:
        """格式化错误提示"""
        error_messages = {
            "not_found": "抱歉，我没能找到相关信息。",
            "unclear": "抱歉，我不太理解您的问题。",
            "out_of_scope": "抱歉，这个问题超出了我的能力范围。"
        }
        
        message = error_messages.get(error_type, "抱歉，出现了一些问题。")
        return f"{message}\n\n💡 **建议**：{suggestion}"

# 使用
formatter = ResponseFormatter()
response = formatter.format_answer(
    "Python是一门高级编程语言...",
    sources=["Python官方文档", "维基百科"],
    confidence=0.95,
    follow_ups=["Python适合做什么？", "如何学习Python？"]
)
```

### 3.2 渐进式展示

```python
async def stream_with_sections(answer: str):
    """分段流式输出"""
    sections = answer.split("\n\n")
    
    for section in sections:
        # 先显示标题
        if section.startswith("#"):
            yield section + "\n\n"
            await asyncio.sleep(0.3)
        else:
            # 逐字显示正文
            for char in section:
                yield char
                await asyncio.sleep(0.01)
            yield "\n\n"
```

---

## 4. 错误处理设计

### 4.1 优雅降级

```python
class GracefulDegradation:
    """优雅降级处理"""
    
    def __init__(self):
        self.fallback_responses = {
            "api_error": "系统繁忙，请稍后再试。您也可以尝试简化问题重新提问。",
            "timeout": "响应时间较长，我正在处理中。您可以稍等或换个问法试试。",
            "no_result": "没有找到相关信息。您可以换个关键词搜索，或提供更多细节。",
            "sensitive": "抱歉，这个话题我无法讨论。有其他我可以帮助的吗？"
        }
    
    def handle_error(self, error_type: str, context: dict = None) -> dict:
        """处理错误"""
        message = self.fallback_responses.get(
            error_type,
            "出现了一点问题，请稍后再试。"
        )
        
        return {
            "message": message,
            "show_options": True,
            "options": [
                "重新提问",
                "换个话题",
                "联系人工客服"
            ]
        }

# 使用
degradation = GracefulDegradation()
fallback = degradation.handle_error("timeout")
```

---

## 5. 学习检查清单

- [ ] 理解对话设计金字塔
- [ ] 能够设计引导式对话流程
- [ ] 会格式化结构化回复
- [ ] 能够实现优雅降级

---

## 继续学习

📌 **Week 10 学习顺序**：
1. ✅ AI产品设计原则
2. ✅ 对话交互设计（本教程）
3. ➡️ 错误处理策略
