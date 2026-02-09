# 📘 GPT-4V / Vision模型使用指南

> **学习目标**：掌握视觉语言模型的调用方法，实现图像理解功能

---

## 🎯 本教程目标

完成本教程后，你将能够：

- ✅ 调用Vision API处理图像
- ✅ 实现图像描述和OCR
- ✅ 构建图像问答系统
- ✅ 处理多图像输入

---

## 📚 核心概念

### 什么是Vision模型？

Vision模型（如GPT-4V、DeepSeek-Vision）是能够同时理解文本和图像的多模态大模型。

```
┌─────────────────────────────────────────────────────────┐
│                   Vision模型工作流程                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   输入                      处理                输出     │
│                                                          │
│  ┌─────┐                                                 │
│  │图像 │ ──┐                                             │
│  └─────┘   │     ┌──────────────┐     ┌──────────┐     │
│            ├───► │ Vision LLM   │ ──► │ 文本回答  │     │
│  ┌─────┐   │     │  (多模态)    │     └──────────┘     │
│  │文本 │ ──┘     └──────────────┘                       │
│  └─────┘                                                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 代码实现

### 1. 基础图像分析

```python
import base64
from openai import OpenAI

def encode_image_to_base64(image_path: str) -> str:
    """将图像文件编码为Base64字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

class VisionAnalyzer:
    """视觉分析器"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def analyze_image(self, image_path: str, question: str) -> str:
        """分析单张图像"""
        base64_image = encode_image_to_base64(image_path)
        
        response = self.client.chat.completions.create(
            model="deepseek-vision",  # 或 gpt-4-vision-preview
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # low, high, auto
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def analyze_url_image(self, image_url: str, question: str) -> str:
        """分析URL图像"""
        response = self.client.chat.completions.create(
            model="deepseek-vision",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
```

### 2. OCR文字识别

```python
class VisionOCR:
    """基于Vision模型的OCR"""
    
    def __init__(self, analyzer: VisionAnalyzer):
        self.analyzer = analyzer
    
    def extract_text(self, image_path: str) -> str:
        """提取图像中的文字"""
        prompt = """请仔细识别图像中的所有文字内容。
要求：
1. 按照原始布局输出文字
2. 保持段落结构
3. 如果有表格，请用Markdown表格格式输出
4. 如果文字模糊，请标注[模糊]"""
        
        return self.analyzer.analyze_image(image_path, prompt)
    
    def extract_structured(self, image_path: str, fields: list[str]) -> dict:
        """提取结构化信息"""
        fields_str = ", ".join(fields)
        prompt = f"""请从图像中提取以下字段信息：
{fields_str}

以JSON格式输出，如果某字段无法识别，值设为null。"""
        
        result = self.analyzer.analyze_image(image_path, prompt)
        # 解析JSON（实际使用时需要更健壮的解析）
        import json
        try:
            return json.loads(result)
        except:
            return {"raw": result}
```

### 3. 多图像对比分析

```python
def compare_images(client, image_paths: list[str], question: str) -> str:
    """对比多张图像"""
    content = [{"type": "text", "text": question}]
    
    for i, path in enumerate(image_paths):
        base64_img = encode_image_to_base64(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_img}"
            }
        })
    
    response = client.chat.completions.create(
        model="deepseek-vision",
        messages=[{"role": "user", "content": content}],
        max_tokens=1500
    )
    
    return response.choices[0].message.content

# 使用示例
result = compare_images(
    client,
    ["before.jpg", "after.jpg"],
    "请对比这两张图片的区别，详细说明变化之处。"
)
```

---

## 🎯 实战应用场景

| 场景 | 描述 | 提示词示例 |
|------|------|-----------|
| 商品识别 | 识别商品信息 | "识别这个商品的名称、品牌、价格" |
| 文档OCR | 提取文档文字 | "提取文档中的所有文字内容" |
| 图表分析 | 解读图表数据 | "分析这个图表展示的数据趋势" |
| 界面理解 | 理解UI截图 | "描述这个界面的布局和功能" |

---

## 📊 学习检查清单

- [ ] 会将图像编码为Base64
- [ ] 能够调用Vision API
- [ ] 理解detail参数的作用
- [ ] 会处理多图像输入

---

## 🎯 下一步

继续学习：[CLIP图像Embedding](./02_image_embedding.md)
