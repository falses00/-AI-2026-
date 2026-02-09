# 📊 微调数据集准备

> **学习目标**：掌握高质量训练数据的构建方法

---

## 1. 数据集格式标准

### 1.1 对话格式 (ChatML)

```json
{
  "messages": [
    {"role": "system", "content": "你是一个专业的客服助手。"},
    {"role": "user", "content": "我想退货怎么办？"},
    {"role": "assistant", "content": "好的，请提供您的订单号，我来帮您处理退货申请。"}
  ]
}
```

### 1.2 指令格式

```json
{
  "instruction": "将以下文本翻译成英文",
  "input": "今天天气真好",
  "output": "The weather is really nice today."
}
```

### 1.3 Preference格式 (DPO/RLHF)

```json
{
  "prompt": "解释什么是机器学习",
  "chosen": "机器学习是人工智能的一个分支，通过数据训练模型...",
  "rejected": "机器学习就是让电脑自己学习。"
}
```

---

## 2. 数据收集策略

### 2.1 从日志中提取

```python
from dataclasses import dataclass
from typing import List
import json

@dataclass
class ConversationLog:
    """对话日志"""
    session_id: str
    messages: List[dict]
    user_rating: int  # 1-5
    resolved: bool

class DataExtractor:
    """数据提取器"""
    
    def __init__(self, min_rating: int = 4):
        self.min_rating = min_rating
        self.extracted_data = []
    
    def extract_from_logs(self, logs: List[ConversationLog]) -> List[dict]:
        """从对话日志中提取训练数据"""
        training_data = []
        
        for log in logs:
            # 只使用高评分且已解决的对话
            if log.user_rating >= self.min_rating and log.resolved:
                sample = {
                    "messages": log.messages,
                    "metadata": {
                        "source": "production_logs",
                        "rating": log.user_rating,
                        "session_id": log.session_id
                    }
                }
                training_data.append(sample)
        
        return training_data
    
    def save_jsonl(self, data: List[dict], output_path: str):
        """保存为JSONL格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

# 使用
extractor = DataExtractor(min_rating=4)
data = extractor.extract_from_logs(conversation_logs)
extractor.save_jsonl(data, "training_data.jsonl")
```

### 2.2 人工标注流程

```python
from enum import Enum

class LabelStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class AnnotationPlatform:
    """标注平台"""
    
    def __init__(self):
        self.samples = []
        self.annotations = {}
    
    def add_sample(self, sample: dict) -> str:
        """添加待标注样本"""
        sample_id = f"sample_{len(self.samples)}"
        self.samples.append({
            "id": sample_id,
            "data": sample,
            "status": LabelStatus.PENDING
        })
        return sample_id
    
    def annotate(
        self,
        sample_id: str,
        annotator: str,
        response: str,
        notes: str = ""
    ):
        """标注样本"""
        self.annotations[sample_id] = {
            "annotator": annotator,
            "response": response,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
    
    def review(self, sample_id: str, status: LabelStatus, reviewer: str):
        """审核标注"""
        for sample in self.samples:
            if sample["id"] == sample_id:
                sample["status"] = status
                sample["reviewer"] = reviewer
                break
    
    def export_approved(self) -> List[dict]:
        """导出已审核的数据"""
        approved = []
        for sample in self.samples:
            if sample["status"] == LabelStatus.APPROVED:
                sample_id = sample["id"]
                if sample_id in self.annotations:
                    approved.append({
                        "input": sample["data"],
                        "output": self.annotations[sample_id]["response"]
                    })
        return approved
```

---

## 3. 数据增强技术

### 3.1 使用AI生成样本

```python
from openai import OpenAI

class DataAugmentor:
    """数据增强器"""
    
    def __init__(self):
        self.client = OpenAI()
    
    def generate_variations(
        self,
        original: dict,
        n_variations: int = 3
    ) -> List[dict]:
        """生成变体样本"""
        prompt = f"""基于以下对话样本，生成{n_variations}个语义相似但表达不同的变体：

原始样本：
用户: {original['user']}
助手: {original['assistant']}

要求：
1. 保持核心语义不变
2. 改变表达方式、用词、句式
3. 每个变体都是独立完整的
4. 返回JSON数组格式

{{
  "variations": [
    {{"user": "...", "assistant": "..."}},
    ...
  ]
}}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("variations", [])
    
    def paraphrase(self, text: str) -> str:
        """改写文本"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个文本改写专家，保持语义不变但改变表达方式。"},
                {"role": "user", "content": f"请改写以下文本：\n\n{text}"}
            ]
        )
        return response.choices[0].message.content

# 使用
augmentor = DataAugmentor()
variations = augmentor.generate_variations({
    "user": "我想退货",
    "assistant": "好的，请提供订单号"
})
```

### 3.2 负样本生成

```python
def generate_negative_samples(positive_samples: List[dict]) -> List[dict]:
    """生成用于DPO训练的负样本"""
    client = OpenAI()
    negative_samples = []
    
    for sample in positive_samples:
        prompt = f"""基于以下问题，生成一个质量较差的回答（用于对比训练）：

问题: {sample['user']}
优质回答: {sample['assistant']}

请生成一个回答，存在以下一个或多个问题：
- 过于简短或模糊
- 信息不够准确
- 语气不够友好
- 没有解决用户问题

返回JSON: {{"rejected_response": "..."}}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        negative_samples.append({
            "prompt": sample['user'],
            "chosen": sample['assistant'],
            "rejected": result['rejected_response']
        })
    
    return negative_samples
```

---

## 4. 数据质量检验

```python
class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.issues = []
    
    def validate_sample(self, sample: dict) -> bool:
        """验证单个样本"""
        issues = []
        
        # 检查必要字段
        if "messages" in sample:
            messages = sample["messages"]
            if len(messages) < 2:
                issues.append("对话轮数过少")
            
            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    issues.append("消息格式不完整")
                if msg.get("content", "").strip() == "":
                    issues.append("存在空消息")
        
        # 检查长度
        total_length = sum(len(m.get("content", "")) for m in sample.get("messages", []))
        if total_length < 20:
            issues.append("内容过短")
        if total_length > 10000:
            issues.append("内容过长")
        
        if issues:
            self.issues.append({"sample": sample, "issues": issues})
            return False
        return True
    
    def validate_dataset(self, dataset: List[dict]) -> dict:
        """验证整个数据集"""
        valid_count = 0
        invalid_count = 0
        
        for sample in dataset:
            if self.validate_sample(sample):
                valid_count += 1
            else:
                invalid_count += 1
        
        return {
            "total": len(dataset),
            "valid": valid_count,
            "invalid": invalid_count,
            "valid_ratio": valid_count / len(dataset) if dataset else 0,
            "issues": self.issues
        }

# 使用
validator = DataValidator()
report = validator.validate_dataset(training_data)
print(f"有效样本比例: {report['valid_ratio']:.2%}")
```

---

## 5. 数据集分割

```python
from sklearn.model_selection import train_test_split

def split_dataset(
    data: List[dict],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42
) -> tuple:
    """分割数据集"""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01
    
    # 先分出测试集
    train_val, test = train_test_split(
        data,
        test_size=test_ratio,
        random_state=seed
    )
    
    # 再分出验证集
    val_size = val_ratio / (train_ratio + val_ratio)
    train, val = train_test_split(
        train_val,
        test_size=val_size,
        random_state=seed
    )
    
    return train, val, test

# 使用
train, val, test = split_dataset(all_data)
print(f"训练集: {len(train)}, 验证集: {len(val)}, 测试集: {len(test)}")
```

---

## 6. 学习检查清单

- [ ] 理解常用数据集格式
- [ ] 能够从日志中提取训练数据
- [ ] 会使用AI进行数据增强
- [ ] 能够验证数据质量

---

## 继续学习

📌 **Week 9 学习顺序**：
1. ✅ LoRA微调技术
2. ✅ 微调数据集准备（本教程）
3. ➡️ 模型评估与部署
