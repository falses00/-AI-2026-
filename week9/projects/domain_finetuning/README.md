# 🎯 行业专属模型微调项目

> **Week 9 综合实战项目** - 构建领域专属的微调模型

---

## 🎯 项目目标

构建一个完整的模型微调Pipeline，从数据准备到模型部署：
- 收集和清洗行业数据
- 使用LoRA进行高效微调
- 评估模型效果
- 部署微调后的模型

---

## 📊 项目架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     模型微调Pipeline架构                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      │
│  │   数据收集   │ ───► │  数据清洗   │ ───► │  格式转换   │      │
│  │  (日志/标注) │      │  (质量过滤) │      │  (JSONL)   │      │
│  └─────────────┘      └─────────────┘      └─────────────┘      │
│                                                   │              │
│                                                   ▼              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      │
│  │   模型部署   │ ◄─── │  模型评估   │ ◄─── │  LoRA微调   │      │
│  │  (vLLM)     │      │  (自动+人工) │      │  (Unsloth) │      │
│  └─────────────┘      └─────────────┘      └─────────────┘      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
week9/projects/domain_finetuning/
├── README.md              # 本文件
├── requirements.txt       # 依赖
├── config.yaml           # 训练配置
├── data/
│   ├── raw/              # 原始数据
│   ├── processed/        # 处理后数据
│   └── splits/           # 训练/验证/测试集
├── scripts/
│   ├── prepare_data.py   # 数据准备脚本
│   ├── train.py          # 训练脚本
│   ├── evaluate.py       # 评估脚本
│   └── export.py         # 导出脚本
├── src/
│   ├── __init__.py
│   ├── data_processor.py # 数据处理模块
│   ├── trainer.py        # 训练模块
│   └── evaluator.py      # 评估模块
└── serving/
    ├── app.py            # FastAPI服务
    └── docker-compose.yml
```

---

## 🔧 核心代码

### 1. 数据处理器 (`src/data_processor.py`)

```python
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import random

@dataclass
class Sample:
    """训练样本"""
    instruction: str
    input_text: str
    output: str
    metadata: dict = None

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt or "你是一个专业的行业助手。"
        self.samples: List[Sample] = []
    
    def add_sample(self, instruction: str, input_text: str, output: str):
        """添加样本"""
        self.samples.append(Sample(
            instruction=instruction,
            input_text=input_text,
            output=output
        ))
    
    def load_from_jsonl(self, file_path: str):
        """从JSONL加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                self.add_sample(
                    instruction=data.get('instruction', ''),
                    input_text=data.get('input', ''),
                    output=data.get('output', '')
                )
    
    def filter_quality(self, min_output_len: int = 10, max_output_len: int = 2000):
        """质量过滤"""
        filtered = []
        for sample in self.samples:
            # 检查输出长度
            if len(sample.output) < min_output_len:
                continue
            if len(sample.output) > max_output_len:
                continue
            # 检查是否有空内容
            if not sample.output.strip():
                continue
            filtered.append(sample)
        
        original = len(self.samples)
        self.samples = filtered
        print(f"质量过滤: {original} -> {len(self.samples)} 样本")
    
    def to_chat_format(self) -> List[dict]:
        """转换为聊天格式"""
        formatted = []
        for sample in self.samples:
            user_content = sample.instruction
            if sample.input_text:
                user_content += f"\n\n{sample.input_text}"
            
            formatted.append({
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": sample.output}
                ]
            })
        return formatted
    
    def split_data(self, train_ratio: float = 0.8, val_ratio: float = 0.1):
        """分割数据集"""
        random.shuffle(self.samples)
        n = len(self.samples)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        return {
            "train": self.samples[:train_end],
            "val": self.samples[train_end:val_end],
            "test": self.samples[val_end:]
        }
    
    def export_jsonl(self, samples: List[Sample], output_path: str):
        """导出JSONL"""
        formatted = []
        for sample in samples:
            user_content = sample.instruction
            if sample.input_text:
                user_content += f"\n\n{sample.input_text}"
            formatted.append({
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": sample.output}
                ]
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in formatted:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

### 2. LoRA训练脚本 (`scripts/train.py`)

```python
"""
使用Unsloth进行LoRA微调
支持Qwen2.5、Llama3等模型
"""
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import yaml

# 加载配置
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 模型配置
model_name = config.get("model_name", "Qwen/Qwen2.5-7B")
max_seq_length = config.get("max_seq_length", 2048)
lora_r = config.get("lora_r", 16)
lora_alpha = config.get("lora_alpha", 32)

# 加载模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
    load_in_4bit=True,  # 4bit量化节省显存
)

# 添加LoRA适配器
model = FastLanguageModel.get_peft_model(
    model,
    r=lora_r,
    lora_alpha=lora_alpha,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# 加载数据
dataset = load_dataset("json", data_files={
    "train": "data/splits/train.jsonl",
    "validation": "data/splits/val.jsonl"
})

def formatting_func(examples):
    """格式化函数"""
    return tokenizer.apply_chat_template(
        examples["messages"],
        tokenize=False,
        add_generation_prompt=False
    )

# 训练参数
training_args = TrainingArguments(
    output_dir="./outputs",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    warmup_ratio=0.1,
    logging_steps=10,
    save_steps=100,
    evaluation_strategy="steps",
    eval_steps=100,
    fp16=True,
    report_to="none",
)

# 训练器
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    formatting_func=formatting_func,
    args=training_args,
    max_seq_length=max_seq_length,
)

# 开始训练
trainer.train()

# 保存模型
model.save_pretrained("./outputs/final_model")
tokenizer.save_pretrained("./outputs/final_model")

# 合并LoRA权重（可选）
model.save_pretrained_merged(
    "./outputs/merged_model",
    tokenizer,
    save_method="merged_16bit",
)

print("训练完成！模型已保存到 ./outputs/")
```

### 3. 评估脚本 (`scripts/evaluate.py`)

```python
"""
模型评估脚本
支持自动化评估和LLM-as-Judge
"""
import json
from openai import OpenAI
from datasets import load_dataset
from tqdm import tqdm

# 配置
client = OpenAI()
EVAL_MODEL = "gpt-4o"

def load_test_data(path: str):
    """加载测试数据"""
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def generate_response(model, tokenizer, prompt: str) -> str:
    """使用微调模型生成响应"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def llm_evaluate(question: str, reference: str, candidate: str) -> dict:
    """使用LLM评估"""
    prompt = f"""请评估AI助手的回答质量。

问题: {question}

参考答案: {reference}

待评估回答: {candidate}

请从以下维度评分(1-5)：
1. 准确性 - 信息是否正确
2. 完整性 - 是否完整回答问题
3. 流畅性 - 语言是否通顺
4. 专业性 - 是否体现领域知识

返回JSON格式：
{{"accuracy": X, "completeness": X, "fluency": X, "professionalism": X, "overall": X, "reasoning": "..."}}
"""
    
    response = client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def run_evaluation(test_path: str, model, tokenizer):
    """运行完整评估"""
    test_data = load_test_data(test_path)
    results = []
    
    for item in tqdm(test_data, desc="评估中"):
        messages = item["messages"]
        question = messages[1]["content"]  # user message
        reference = messages[2]["content"]  # assistant message
        
        # 生成响应
        candidate = generate_response(model, tokenizer, question)
        
        # LLM评估
        scores = llm_evaluate(question, reference, candidate)
        
        results.append({
            "question": question,
            "reference": reference,
            "candidate": candidate,
            "scores": scores
        })
    
    # 计算平均分
    avg_scores = {
        "accuracy": sum(r["scores"]["accuracy"] for r in results) / len(results),
        "completeness": sum(r["scores"]["completeness"] for r in results) / len(results),
        "fluency": sum(r["scores"]["fluency"] for r in results) / len(results),
        "professionalism": sum(r["scores"]["professionalism"] for r in results) / len(results),
        "overall": sum(r["scores"]["overall"] for r in results) / len(results),
    }
    
    print("\n========== 评估结果 ==========")
    for metric, score in avg_scores.items():
        print(f"{metric}: {score:.2f}")
    
    # 保存详细结果
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": avg_scores,
            "details": results
        }, f, ensure_ascii=False, indent=2)
    
    return avg_scores

if __name__ == "__main__":
    # 加载微调后的模型
    from unsloth import FastLanguageModel
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="./outputs/final_model",
        max_seq_length=2048,
    )
    
    run_evaluation("data/splits/test.jsonl", model, tokenizer)
```

### 4. 配置文件 (`config.yaml`)

```yaml
# 模型微调配置

# 基座模型
model_name: "Qwen/Qwen2.5-7B"
max_seq_length: 2048

# LoRA配置
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05

# 训练配置
batch_size: 2
gradient_accumulation_steps: 8
learning_rate: 2e-4
num_epochs: 3
warmup_ratio: 0.1

# 数据配置
system_prompt: "你是一个专业的金融分析助手，提供准确、专业的金融咨询服务。"
min_output_length: 20
max_output_length: 1500

# 评估配置
eval_model: "gpt-4o"
eval_samples: 100
```

---

## 📦 依赖 (`requirements.txt`)

```
torch>=2.1.0
transformers>=4.36.0
datasets>=2.16.0
peft>=0.7.0
trl>=0.7.0
unsloth>=2024.1
accelerate>=0.25.0
bitsandbytes>=0.41.0
openai>=1.12.0
pyyaml>=6.0
tqdm>=4.66.0
```

---

## 🚀 使用流程

```bash
# 1. 准备数据
python scripts/prepare_data.py --input data/raw --output data/splits

# 2. 开始训练
python scripts/train.py

# 3. 评估模型
python scripts/evaluate.py

# 4. 导出部署
python scripts/export.py --format vllm
```

---

## 💡 行业应用场景

| 行业 | 应用 | 数据来源 |
|------|------|---------|
| 金融 | 投研报告生成 | 研报、财报 |
| 医疗 | 病历摘要 | 脱敏病历 |
| 法律 | 合同审查 | 法律文书 |
| 客服 | 智能回复 | 历史对话 |

---

## 📊 学习收获

- [x] 微调数据准备流程
- [x] LoRA高效微调技术
- [x] 模型评估方法
- [x] 微调模型部署
