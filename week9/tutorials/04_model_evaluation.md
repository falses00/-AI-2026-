# 📊 模型评估与效果验证

> **学习目标**：掌握微调模型的评估方法，确保模型质量达到上线标准

---

## 1. 为什么需要评估？

微调后的模型需要系统评估才能确定：
- ✅ 是否达到预期效果
- ✅ 与基础模型相比是否有提升
- ✅ 是否引入了新问题（如遗忘、偏见）
- ✅ 是否可以部署上线

---

## 2. 评估维度

| 维度 | 定义 | 评估方法 |
|-----|------|---------|
| **准确性** | 回答是否正确 | 人工标注 / 自动匹配 |
| **流畅性** | 语言是否通顺 | 困惑度 (PPL) |
| **相关性** | 回答是否切题 | BERT Score / 余弦相似度 |
| **安全性** | 是否有害内容 | Guardrails检测 |
| **一致性** | 风格是否统一 | 人工评估 |

---

## 3. 自动评估方法

### 3.1 困惑度 (Perplexity)

困惑度衡量模型对文本的"惊讶程度"，值越低表示模型越好。

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import math

def calculate_perplexity(model, tokenizer, text: str) -> float:
    """计算单个文本的困惑度"""
    encodings = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
        loss = outputs.loss
    
    return math.exp(loss.item())

# 使用
model = AutoModelForCausalLM.from_pretrained("your-model")
tokenizer = AutoTokenizer.from_pretrained("your-model")

test_texts = [
    "这是一段测试文本，用于评估模型质量。",
    "微调后的模型应该在领域内有更低的困惑度。"
]

for text in test_texts:
    ppl = calculate_perplexity(model, tokenizer, text)
    print(f"PPL: {ppl:.2f} | {text[:30]}...")
```

### 3.2 BERT Score

BERT Score 使用预训练模型计算生成文本与参考文本的语义相似度。

```python
from bert_score import score

def evaluate_bert_score(predictions: list[str], references: list[str]) -> dict:
    """计算BERT Score"""
    P, R, F1 = score(
        predictions, 
        references, 
        lang="zh",
        verbose=True
    )
    
    return {
        "precision": P.mean().item(),
        "recall": R.mean().item(),
        "f1": F1.mean().item()
    }

# 使用
predictions = [
    "北京是中国的首都城市",
    "机器学习是人工智能的一个分支"
]
references = [
    "北京是中华人民共和国的首都",
    "机器学习是AI的重要组成部分"
]

scores = evaluate_bert_score(predictions, references)
print(f"BERT Score F1: {scores['f1']:.4f}")
```

### 3.3 ROUGE Score

ROUGE 评估文本的重叠程度，常用于摘要任务。

```python
from rouge_chinese import Rouge

def evaluate_rouge(predictions: list[str], references: list[str]) -> dict:
    """计算ROUGE Score"""
    rouge = Rouge()
    scores = rouge.get_scores(predictions, references, avg=True)
    
    return {
        "rouge-1": scores["rouge-1"]["f"],
        "rouge-2": scores["rouge-2"]["f"],
        "rouge-l": scores["rouge-l"]["f"]
    }

# 使用
scores = evaluate_rouge(predictions, references)
print(f"ROUGE-L: {scores['rouge-l']:.4f}")
```

---

## 4. 人工评估

### 4.1 评估模板

```python
from pydantic import BaseModel
from typing import Literal
from enum import Enum

class QualityScore(int, Enum):
    VERY_BAD = 1
    BAD = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5

class HumanEvaluation(BaseModel):
    """人工评估记录"""
    sample_id: str
    question: str
    base_answer: str
    finetuned_answer: str
    
    # 评分维度
    accuracy_score: QualityScore
    fluency_score: QualityScore
    relevance_score: QualityScore
    
    # 偏好选择
    preferred: Literal["base", "finetuned", "tie"]
    
    # 备注
    notes: str = ""
    evaluator: str

def generate_evaluation_report(evaluations: list[HumanEvaluation]) -> dict:
    """生成评估报告"""
    total = len(evaluations)
    
    # 统计偏好
    preference_counts = {"base": 0, "finetuned": 0, "tie": 0}
    for e in evaluations:
        preference_counts[e.preferred] += 1
    
    # 计算平均分
    avg_accuracy = sum(e.accuracy_score.value for e in evaluations) / total
    avg_fluency = sum(e.fluency_score.value for e in evaluations) / total
    avg_relevance = sum(e.relevance_score.value for e in evaluations) / total
    
    return {
        "total_samples": total,
        "avg_accuracy": avg_accuracy,
        "avg_fluency": avg_fluency,
        "avg_relevance": avg_relevance,
        "win_rate": preference_counts["finetuned"] / total,
        "preference_distribution": preference_counts
    }
```

### 4.2 A/B 盲评

```python
import random

class ABEvaluator:
    """A/B盲评系统"""
    
    def __init__(self, test_cases: list[dict]):
        self.test_cases = test_cases
        self.results = []
    
    def get_random_case(self) -> dict:
        """获取随机测试用例，隐藏来源"""
        case = random.choice(self.test_cases)
        
        # 随机打乱A/B顺序
        if random.random() > 0.5:
            return {
                "question": case["question"],
                "answer_a": case["base_answer"],
                "answer_b": case["finetuned_answer"],
                "order": "base_first"
            }
        else:
            return {
                "question": case["question"],
                "answer_a": case["finetuned_answer"],
                "answer_b": case["base_answer"],
                "order": "finetuned_first"
            }
    
    def record_result(self, case: dict, choice: Literal["a", "b", "tie"]):
        """记录评估结果"""
        if case["order"] == "base_first":
            winner = "base" if choice == "a" else "finetuned" if choice == "b" else "tie"
        else:
            winner = "finetuned" if choice == "a" else "base" if choice == "b" else "tie"
        
        self.results.append(winner)
    
    def get_statistics(self) -> dict:
        """获取统计结果"""
        total = len(self.results)
        return {
            "total": total,
            "base_wins": self.results.count("base") / total if total else 0,
            "finetuned_wins": self.results.count("finetuned") / total if total else 0,
            "ties": self.results.count("tie") / total if total else 0
        }
```

---

## 5. 评估Pipeline

```python
class EvaluationPipeline:
    """完整评估流程"""
    
    def __init__(self, base_model, finetuned_model, tokenizer):
        self.base_model = base_model
        self.finetuned_model = finetuned_model
        self.tokenizer = tokenizer
    
    async def evaluate(self, test_dataset: list[dict]) -> dict:
        """执行完整评估"""
        results = {
            "perplexity": {},
            "bert_score": {},
            "generation_quality": []
        }
        
        # 1. 困惑度评估
        base_ppl = []
        finetuned_ppl = []
        
        for sample in test_dataset:
            base_ppl.append(calculate_perplexity(
                self.base_model, self.tokenizer, sample["reference"]
            ))
            finetuned_ppl.append(calculate_perplexity(
                self.finetuned_model, self.tokenizer, sample["reference"]
            ))
        
        results["perplexity"] = {
            "base": sum(base_ppl) / len(base_ppl),
            "finetuned": sum(finetuned_ppl) / len(finetuned_ppl),
            "improvement": (sum(base_ppl) - sum(finetuned_ppl)) / sum(base_ppl)
        }
        
        # 2. 生成并评估
        predictions = []
        references = []
        
        for sample in test_dataset:
            # 生成回答
            output = self._generate(self.finetuned_model, sample["question"])
            predictions.append(output)
            references.append(sample["reference"])
        
        # 3. BERT Score
        bert_scores = evaluate_bert_score(predictions, references)
        results["bert_score"] = bert_scores
        
        return results
    
    def _generate(self, model, prompt: str) -> str:
        """生成回答"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=256)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

---

## 6. 评估标准参考

| 指标 | 及格线 | 良好 | 优秀 |
|-----|-------|-----|------|
| PPL降低 | >5% | >10% | >20% |
| BERT Score F1 | >0.7 | >0.8 | >0.9 |
| 人工偏好胜率 | >50% | >60% | >70% |
| ROUGE-L | >0.3 | >0.5 | >0.7 |

---

## 7. 学习检查清单

- [ ] 理解各评估指标的含义
- [ ] 能够计算困惑度
- [ ] 会使用BERT Score评估语义相似度
- [ ] 能够设计A/B盲评实验
- [ ] 能够构建完整评估Pipeline

---

**好的评估才能确保模型上线质量！📊**
