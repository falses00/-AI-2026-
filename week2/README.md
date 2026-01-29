# 📘 第2周：大模型API深度控制

> **学习目标**：掌握DeepSeek/OpenAI API的高级用法，包括结构化输出、Function Calling、流式响应和Token优化

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 熟练调用DeepSeek/OpenAI API
- ✅ 使用JSON Mode获取结构化输出
- ✅ 掌握Function Calling实现工具调用
- ✅ 实现流式响应（Streaming）
- ✅ 进行Token计算和成本优化
- ✅ 完成实战项目

---

## 📚 学习路径

### Day 1：API基础入门

#### 📖 教程材料
- [DeepSeek API快速入门](./tutorials/01_openai_api_basics.md) ✅

**今日目标**：
- 配置API密钥
- 发送第一个Chat请求
- 理解messages格式

#### 🎬 推荐视频（B站）
| UP主 | 视频 | 链接 |
|------|------|------|
| AI进化论 | DeepSeek API完全攻略 | https://www.bilibili.com/video/BV1XMDXYoExa |
| 跟李沐学AI | Python调用大模型实战 | https://www.bilibili.com/video/BV1F94y1f7cz |

---

### Day 2-3：结构化输出

#### 📖 教程材料
- [结构化输出详解](./tutorials/02_structured_output.md) ✅
- [Response Format深度解析](./tutorials/03_response_format.md) ✅

**学习重点**：
- JSON Mode启用方法
- 在Prompt中定义输出格式
- 使用Pydantic验证AI输出
- 错误处理与重试机制

#### 💻 实战练习
```python
# 练习：从商品描述中提取结构化信息
# 输入："iPhone 15 Pro，128GB，售价7999元，黑色"
# 输出：{"name": "iPhone 15 Pro", "storage": "128GB", "price": 7999, "color": "黑色"}
```

---

### Day 4：Function Calling

#### 📖 教程材料
- [Function Calling详解](./tutorials/04_function_calling_intro.md) ✅

**学习重点**：
- 函数定义（tools参数）
- AI自动选择函数
- 执行函数并返回结果
- 多函数并行调用
- 安全性考虑

#### 💻 实战案例
```python
# 实现一个能查天气、搜索网页、发邮件的AI助手
tools = [
    {"type": "function", "function": {"name": "get_weather", ...}},
    {"type": "function", "function": {"name": "search_web", ...}},
    {"type": "function", "function": {"name": "send_email", ...}}
]
```

---

### Day 5：流式响应

#### 📖 教程材料
- [Streaming流式响应](./tutorials/05_streaming.md) ✅

**学习重点**：
- 流式API调用方法
- SSE（Server-Sent Events）原理
- FastAPI流式端点实现
- 前端接收与实时展示
- 错误处理与超时控制

#### 💻 实战项目
搭建一个类ChatGPT的流式聊天界面：
- 后端：FastAPI + SSE
- 前端：HTML + JavaScript
- 实现打字机效果

---

### Day 6：Token优化

#### 📖 教程材料
- [Token计算与成本优化](./tutorials/06_token_optimization.md) ✅

**学习重点**：
- Tiktoken库使用
- Token计数方法
- 成本估算技巧
- Prompt压缩策略
- 上下文窗口管理

#### 💡 成本对比
| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| DeepSeek-Chat | ¥1/百万Token | ¥2/百万Token |
| GPT-4o | $5/百万Token | $15/百万Token |
| GPT-3.5 | $0.5/百万Token | $1.5/百万Token |

---

### Day 7：复习与实战

#### 📖 练习题
- [API综合练习](./exercises/api_exercises.py) ✅

#### 🚀 本周项目
**智能文档解析器**：
- 输入：任意文本（简历、发票、名片等）
- 输出：结构化JSON数据
- 功能：自动识别文档类型，提取关键信息

---

## 📊 学习检查清单

### API基础
- [ ] 能够配置API密钥和base_url
- [ ] 理解messages的role（system/user/assistant）
- [ ] 能够控制temperature和max_tokens

### 结构化输出
- [ ] 会使用response_format启用JSON Mode
- [ ] 能够在Prompt中定义JSON结构
- [ ] 会用Pydantic验证输出

### Function Calling
- [ ] 能够定义tools参数
- [ ] 理解tool_choice的作用
- [ ] 能够处理函数调用结果

### 流式响应
- [ ] 能够使用stream=True调用API
- [ ] 理解SSE协议
- [ ] 能够实现FastAPI流式端点

### Token优化
- [ ] 会使用tiktoken计算Token
- [ ] 能够估算API成本
- [ ] 知道常用的Prompt压缩技巧

---

## 🎁 学习资源

### 📚 官方文档
- [DeepSeek API文档](https://platform.deepseek.com/docs) - 原生中文
- [OpenAI API文档](https://platform.openai.com/docs/)
- [Tiktoken GitHub](https://github.com/openai/tiktoken)

### 📺 B站推荐UP主
- AI进化论-花生
- 跟李沐学AI
- DataWhale

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 3: MCP协议深度剖析](../week3/README.md)

---

**API是AI应用的基础，熟练掌握才能构建强大应用！💪**
