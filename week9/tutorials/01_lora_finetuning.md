# 📘 LoRA微调技术详解

> **学习目标**：掌握LoRA高效微调技术，以最小成本训练专属模型

---

## 🎯 本教程目标

完成本教程后，你将能够：

- ✅ 理解LoRA的工作原理
- ✅ 配置LoRA训练参数
- ✅ 准备微调数据集
- ✅ 执行模型微调
- ✅ 合并和部署微调模型

---

## 📚 核心概念

### 什么是LoRA？

**LoRA (Low-Rank Adaptation)** 是一种参数高效的微调方法，通过训练低秩矩阵来适应新任务。

```
┌─────────────────────────────────────────────────────────────────┐
│                        LoRA原理图解                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  传统微调：更新所有参数 W                                         │
│  ┌───────────────┐                                               │
│  │    W (大矩阵)  │  ← 需要大量显存                               │
│  │   d × d       │                                               │
│  └───────────────┘                                               │
│                                                                  │
│  LoRA：W = W₀ + ΔW = W₀ + BA                                    │
│  ┌───────────────┐   ┌─────┐   ┌─────┐                          │
│  │   W₀ (冻结)   │ + │  B  │ × │  A  │  ← 只训练A和B            │
│  │   d × d       │   │ d×r │   │ r×d │                          │
│  └───────────────┘   └─────┘   └─────┘                          │
│                      低秩分解，r << d                            │
│                                                                  │
│  例：d=4096, r=16                                                │
│  原参数量：4096×4096 = 16M                                       │
│  LoRA参数：4096×16×2 = 128K  (减少99%!)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 为什么选择LoRA？

| 方法 | 显存需求 | 训练速度 | 效果 |
|------|---------|---------|------|
| 全量微调 | 非常高 | 慢 | 最好 |
| LoRA | 低 | 快 | 接近全量 |
| QLoRA | 最低 | 较快 | 略低于LoRA |
| Prompt Tuning | 最低 | 最快 | 中等 |

---

## 💻 代码实现

### 1. 环境准备

```bash
# 安装必要库
pip install transformers peft trl accelerate bitsandbytes datasets
```

### 2. 加载模型（4bit量化）

```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
import torch

# 量化配置（QLoRA）
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# 加载模型
model_name = "deepseek-ai/deepseek-llm-7b-chat"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
```

### 3. 配置LoRA

```python
from peft import LoraConfig, get_peft_model, TaskType

# LoRA配置
lora_config = LoraConfig(
    r=16,                          # 秩（rank），越大效果越好但参数越多
    lora_alpha=32,                 # 缩放因子
    target_modules=[               # 要应用LoRA的模块
        "q_proj", "k_proj", "v_proj",  # 注意力层
        "o_proj", "gate_proj",
        "up_proj", "down_proj"
    ],
    lora_dropout=0.05,             # Dropout
    bias="none",                   # 不训练bias
    task_type=TaskType.CAUSAL_LM   # 任务类型
)

# 应用LoRA
model = get_peft_model(model, lora_config)

# 查看可训练参数
model.print_trainable_parameters()
# 输出示例: trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622
```

### 4. 准备数据集

```python
from datasets import Dataset

# 训练数据格式
training_data = [
    {
        "instruction": "你是一个法律顾问",
        "input": "什么是劳动合同？",
        "output": "劳动合同是劳动者与用人单位确立劳动关系、明确双方权利和义务的协议..."
    },
    # 更多数据...
]

def format_prompt(example):
    """格式化为对话格式"""
    return {
        "text": f"""### 指令
{example['instruction']}

### 输入
{example['input']}

### 回答
{example['output']}"""
    }

# 创建数据集
dataset = Dataset.from_list(training_data)
dataset = dataset.map(format_prompt)
```

### 5. 训练配置与执行

```python
from transformers import TrainingArguments
from trl import SFTTrainer

# 训练参数
training_args = TrainingArguments(
    output_dir="./lora_output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none"
)

# 创建训练器
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=False
)

# 开始训练
trainer.train()

# 保存LoRA权重
trainer.save_model("./lora_output/final")
```

### 6. 模型合并与推理

```python
from peft import PeftModel

# 加载基础模型（不量化）
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 加载LoRA权重
model = PeftModel.from_pretrained(base_model, "./lora_output/final")

# 合并权重
merged_model = model.merge_and_unload()

# 保存合并后的模型
merged_model.save_pretrained("./merged_model")
tokenizer.save_pretrained("./merged_model")

# 推理测试
def generate(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = merged_model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

---

## 📊 参数调优指南

| 参数 | 建议值 | 说明 |
|------|-------|------|
| r (rank) | 8-64 | 越大效果越好，但训练越慢 |
| lora_alpha | 2×r | 通常设为r的2倍 |
| learning_rate | 1e-4 ~ 3e-4 | LoRA通常用较大学习率 |
| epochs | 1-5 | 数据量小时增加epoch |
| batch_size | 4-16 | 根据显存调整 |

---

## 📊 学习检查清单

- [ ] 理解LoRA的低秩分解原理
- [ ] 会配置LoRA参数
- [ ] 能够准备微调数据
- [ ] 会合并LoRA权重

---

## 🎯 下一步

继续学习：[训练数据准备](./02_data_preparation.md)
