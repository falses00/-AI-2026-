# 📘 第9周：模型微调与优化

> **学习目标**：掌握大模型微调技术，优化模型以适应特定业务场景

---

## 🎯 本周目标

完成本周学习后，你将能够：

- ✅ 理解模型微调的原理与方法
- ✅ 使用LoRA进行高效微调
- ✅ 准备高质量训练数据
- ✅ 评估微调效果
- ✅ 部署微调后的模型

---

## 🤔 为什么需要微调？

| 场景 | 直接使用API | 微调模型 |
|------|------------|---------|
| 通用问答 | ✅ 够用 | ❌ 不必要 |
| 专业术语 | ⚠️ 可能不准 | ✅ 更准确 |
| 特定格式 | ⚠️ 需反复调试 | ✅ 稳定输出 |
| 企业风格 | ❌ 难以统一 | ✅ 一致性好 |
| 成本控制 | ❌ 按token收费 | ✅ 一次投入 |

---

## 📚 学习路径

### Day 1：微调基础概念

#### 📖 教程材料
- [LoRA微调实战](./tutorials/01_lora_finetuning.md) ✅

**学习内容**：
- 预训练 vs 微调
- 全量微调 vs 参数高效微调
- LoRA/QLoRA原理
- 微调适用场景

#### 微调方法对比
```
┌────────────────────────────────────────────────────────────────┐
│                    微调方法对比                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  全量微调 (Full Fine-tuning)                                    │
│  ├── 更新所有参数                                               │
│  ├── 需要大量GPU显存                                            │
│  └── 效果最好，但成本最高                                        │
│                                                                 │
│  LoRA (Low-Rank Adaptation)                                     │
│  ├── 只训练低秩矩阵                                             │
│  ├── 显存需求降低80%+                                           │
│  └── 效果接近全量微调                                           │
│                                                                 │
│  QLoRA (Quantized LoRA)                                         │
│  ├── 基础模型4bit量化                                           │
│  ├── 普通GPU即可训练                                            │
│  └── 成本最低的微调方案                                         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### Day 2：训练数据准备

#### 📖 教程材料
- [数据集构建指南](./tutorials/02_dataset_preparation.md) ✅

**学习内容**：
- 数据格式要求
- 数据清洗技巧
- 数据增强方法
- 质量检验标准

#### 💻 数据格式示例
```python
# 对话格式（推荐）
training_data = [
    {
        "conversations": [
            {"role": "system", "content": "你是一个专业的法律顾问"},
            {"role": "user", "content": "什么是劳动合同？"},
            {"role": "assistant", "content": "劳动合同是劳动者与用人单位之间..."}
        ]
    },
    # 更多样本...
]

# 指令格式
training_data = [
    {
        "instruction": "将以下文本翻译成英文",
        "input": "今天天气很好",
        "output": "The weather is nice today"
    },
    # 更多样本...
]
```

---

### Day 3：LoRA微调实战

#### 📖 教程材料
- [模型部署指南](./tutorials/03_model_deployment.md) ✅

**学习内容**：
- 环境配置（Transformers、PEFT）
- 模型加载与量化
- LoRA配置参数
- 训练过程监控

#### 💻 LoRA训练示例
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

# 加载基础模型
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-llm-7b-chat",
    load_in_4bit=True,  # QLoRA量化
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-llm-7b-chat")

# LoRA配置
lora_config = LoraConfig(
    r=16,                      # LoRA秩
    lora_alpha=32,             # 缩放因子
    target_modules=["q_proj", "v_proj"],  # 目标层
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

# 应用LoRA
model = get_peft_model(model, lora_config)
print(f"可训练参数: {model.print_trainable_parameters()}")

# 训练参数
training_args = TrainingArguments(
    output_dir="./lora_output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
    fp16=True
)

# 开始训练
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
    max_seq_length=2048
)
trainer.train()
```

---

### Day 4：模型评估

#### 📖 教程材料

> [!NOTE]
> 模型评估内容待补充，可参考: [Hugging Face Evaluate库](https://huggingface.co/docs/evaluate)

**学习内容**：
- 评估指标选择
- 人工评估方法
- 自动评估工具
- A/B测试设计

#### 评估维度
| 维度 | 评估方法 | 工具 |
|------|---------|------|
| 准确性 | 正确率计算 | 人工标注 |
| 流畅性 | 困惑度(PPL) | 自动计算 |
| 相关性 | 相似度计算 | BERT Score |
| 安全性 | 敏感词检测 | 规则+AI |

---

### Day 5：模型部署

#### 📖 教程材料

> [!NOTE]
> 部署内容已合并到 Day 3 教程中

**学习内容**：
- 模型合并与导出
- vLLM高性能推理
- API服务封装
- 模型版本管理

#### 💻 模型合并示例
```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

# 加载基础模型
base_model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-llm-7b-chat")

# 加载并合并LoRA权重
model = PeftModel.from_pretrained(base_model, "./lora_output")
merged_model = model.merge_and_unload()

# 保存合并后的模型
merged_model.save_pretrained("./merged_model")
```

---

### Day 6-7：实战项目

#### 🚀 项目：行业知识问答模型

**项目目标**：
微调一个专业领域（如法律、医疗、金融）的问答模型

**项目步骤**：
1. 收集领域问答数据（500-1000条）
2. 数据清洗与格式转换
3. LoRA微调（约2-4小时）
4. 效果评估与对比
5. 部署为API服务

---

## 📺 推荐资源

| 类型 | 资源 | 链接 |
|------|------|------|
| 视频 | LoRA原理详解 | 待补充 |
| 文档 | HuggingFace PEFT | https://github.com/huggingface/peft |
| 工具 | LLaMA Factory | https://github.com/hiyouga/LLaMA-Factory |

---

## 📊 学习检查清单

### 微调基础
- [ ] 理解微调的意义
- [ ] 知道LoRA/QLoRA原理
- [ ] 了解何时需要微调

### 数据准备
- [ ] 会构建训练数据集
- [ ] 能够进行数据清洗
- [ ] 了解数据质量标准

### 训练实战
- [ ] 能够配置训练环境
- [ ] 会设置LoRA参数
- [ ] 能够监控训练过程

### 评估部署
- [ ] 会评估微调效果
- [ ] 能够合并模型权重
- [ ] 会部署微调模型

---

## 🎯 下一步

完成本周学习后，继续前往：

👉 [Week 10: AI产品设计与用户体验](../week10/README.md)

---

**微调让通用模型成为你的专属AI！💪**
