# 📘 第2周：大模型API深度控制

> **学习目标**：掌握DeepSeek/OpenAI API的高级用法，包括结构化输出、Function Calling

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 调用DeepSeek/OpenAI API
- ✅ 使用结构化输出（JSON Mode）
- ✅ 掌握Function Calling机制
- ✅ 完成API实战练习

---

## 📚 学习路径

### Day 1-2：API基础与结构化输出

#### 📖 教程材料
- [DeepSeek API快速入门](./tutorials/01_openai_api_basics.md) ✅
- [结构化输出详解](./tutorials/02_structured_output.md) ✅

#### 🎬 推荐视频（B站）
- [DeepSeek API完全攻略 - AI进化论](https://www.bilibili.com/video/BV1XMDXYoExa)
- [Python调用大模型API实战 - 跟李沐学AI](https://www.bilibili.com/video/BV1F94y1f7cz)

#### 💻 练习题
- [exercises/api_exercises.py](./exercises/api_exercises.py) ✅

---

### Day 3-4：Function Calling机制

#### 📖 教程材料
- [Function Calling详解](./tutorials/04_function_calling_intro.md) ✅

#### 🎬 推荐视频（B站）
- [OpenAI Function Calling详解 - 吴恩达AI课](https://www.bilibili.com/video/BV1es4y1G7Dy)
- [大模型工具调用原理与实践 - DataWhale](https://www.bilibili.com/video/BV1Yc41197Xz)

---

### Day 5-7：复习与实践

- 回顾所有教程
- 完成练习题
- 尝试构建自己的API应用

---

## 📊 学习检查清单

### DeepSeek API基础
- [ ] 能够设置API密钥和调用基本API
- [ ] 理解Chat Completions的参数
- [ ] 能够使用`temperature`控制随机性
- [ ] 能够使用`max_tokens`限制输出长度

### 结构化输出
- [ ] 理解JSON Mode的工作原理
- [ ] 能够将Pydantic模型转换为JSON Schema
- [ ] 能够处理结构化输出的错误

### Function Calling
- [ ] 理解Function Calling的工作流程
- [ ] 能够定义函数描述（schema）
- [ ] 能够解析函数调用结果

---

## 🎁 学习资源

### 📚 官方文档
- [DeepSeek API文档](https://platform.deepseek.com/docs) - 原生中文
- [OpenAI API文档](https://platform.openai.com/docs/)

### 📺 B站推荐UP主
- AI进化论-花生
- 跟李沐学AI
- DataWhale

---

## ❓ 常见问题

### Q1: DeepSeek和OpenAI API有什么区别？
**A**: DeepSeek API兼容OpenAI格式，只需更改base_url即可。DeepSeek在中文和推理任务上更强，且成本更低。

### Q2: 如何控制API成本？
**A**: 
1. 使用`max_tokens`限制输出
2. 优化Prompt减少Token
3. 使用更便宜的模型

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 3: MCP协议深度剖析](../week3/README.md)

---

**记住：API调用是AI应用的核心，多练习才能熟练！💪**
