# 📘 第2周：大模型API深度控制

> **学习目标**：掌握OpenAI/DeepSeek API的高级用法，包括结构化输出、Function Calling、Token优化和流式响应

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 使用OpenAI/DeepSeek API实现结构化输出
- ✅ 掌握Function Calling机制
- ✅ 进行Token计算和成本优化
- ✅ 实现流式响应（Streaming）
- ✅ 完成2个实战项目

---

## 📚 学习路径

### Day 1-2：API基础与结构化输出

#### 📖 教程材料
- [OpenAI API快速入门](./tutorials/01_openai_api_basics.md)
- [结构化输出详解](./tutorials/02_structured_output.md)
- [Response Format与Pydantic集成](./tutorials/03_response_format.md)

#### 💻 练习题
- [exercises/api_basics_exercises.py](./exercises/api_basics_exercises.py)

---

### Day 3-4：Function Calling机制

#### 📖 教程材料
- [Function Calling原理](./tutorials/04_function_calling_intro.md)
- [多Function调用](./tutorials/05_function_calling_advanced.md)
- [实战：构建工具调用系统](./tutorials/06_tool_system.md)

#### 💻 练习题
- [exercises/function_calling_exercises.py](./exercises/function_calling_exercises.py)

---

### Day 5-6：Token优化与流式响应

#### 📖 教程材料
- [Token计算与成本优化](./tutorials/07_token_optimization.md)
- [Streaming响应实现](./tutorials/08_streaming.md)
- [前端集成SSE](./tutorials/09_sse_frontend.md)

#### 💻 练习题
- [exercises/token_optimization_exercises.py](./exercises/token_optimization_exercises.py)

---

### Day 7：复习与总结

- 回顾所有教程
- 完成练习题
- 准备实战项目

---

## 🚀 实战项目

### 项目3：智能文档解析工具

**目标**：构建一个能够从文本中提取结构化信息的API服务

**技能点**：
- OpenAI API调用
- 结构化输出（JSON Schema）
- 错误处理与重试
- Token计数

**详细说明**：[projects/project3_document_parser/](./projects/project3_document_parser/)

**预计时间**：4-6小时

---

### 项目4：流式响应前端集成

**目标**：实现一个支持流式输出的聊天界面

**技能点**：
- FastAPI流式响应
- Server-Sent Events (SSE)
- HTML/JavaScript前端
- 实时数据展示

**详细说明**：[projects/project4_streaming_chat/](./projects/project4_streaming_chat/)

**预计时间**：4-6小时

---

## 📊 学习检查清单

### OpenAI API基础
- [ ] 能够设置API密钥和调用基本API
- [ ] 理解Chat Completions的参数
- [ ] 能够使用`temperature`控制随机性
- [ ] 能够使用`max_tokens`限制输出长度

### 结构化输出
- [ ] 理解JSON Mode的工作原理
- [ ] 能够使用Response Format定义输出结构
- [ ] 能够将Pydantic模型转换为JSON Schema
- [ ] 能够处理结构化输出的错误

### Function Calling
- [ ] 理解Function Calling的工作流程
- [ ] 能够定义函数描述（schema）
- [ ] 能够解析函数调用结果
- [ ] 能够实现多轮对话

### Token优化
- [ ] 能够使用tiktoken计算Token数
- [ ] 理解不同模型的定价
- [ ] 能够通过Prompt优化减少Token消耗
- [ ] 能够估算API成本

### 流式响应
- [ ] 能够实现FastAPI流式端点
- [ ] 理解Server-Sent Events (SSE)
- [ ] 能够在前端接收流式数据
- [ ] 能够处理流式错误

---

## 🎁 学习资源

### 📄 速查表
- [OpenAI API速查表](../resources/cheatsheets/openai_api_cheatsheet.md)
- [Function Calling速查表](../resources/cheatsheets/function_calling_cheatsheet.md)
- [Tiktoken使用指南](../resources/cheatsheets/tiktoken_cheatsheet.md)

### 📚 官方文档
- [OpenAI API文档](https://platform.openai.com/docs/)
- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [Tiktoken文档](https://github.com/openai/tiktoken)

---

## ❓ 常见问题（FAQ）

### Q1: OpenAI API和DeepSeek API有什么区别？
**A**: DeepSeek API兼容OpenAI格式，只需更改base_url即可。DeepSeek在中文和推理任务上更强，且成本更低。

### Q2: 如何控制API成本？
**A**: 
1. 使用`max_tokens`限制输出
2. 优化Prompt减少Token
3. 使用更小的模型（如gpt-3.5）
4. 实现缓存机制

### Q3: 流式响应什么时候用？
**A**: 当需要提供实时反馈时使用，如聊天、长文本生成。对于短响应，普通方式即可。

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 3: MCP协议深度剖析](../week3/README.md)

---

**记住：API调用是AI应用的核心，多练习才能熟练！💪**
