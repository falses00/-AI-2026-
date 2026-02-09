# ✍️ 智能内容创作平台项目

> **Week 12 毕业项目选项B** - AI驱动的内容创作工具

---

## 🎯 项目概述

构建一个AI驱动的内容创作平台，帮助用户高效创作高质量内容：
- 长文写作辅助
- SEO优化建议
- 多语言翻译
- 图文配合生成

---

## 📊 功能模块

```
┌──────────────────────────────────────────────────────────────────┐
│                    智能内容创作平台                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  写作助手   │  │  SEO优化    │  │  多语翻译   │              │
│  │             │  │             │  │             │              │
│  │ • 大纲生成  │  │ • 关键词分析│  │ • 实时翻译  │              │
│  │ • 段落扩写  │  │ • 标题优化  │  │ • 风格保持  │              │
│  │ • 风格调整  │  │ • 可读性评估│  │ • 术语一致  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  图片生成   │  │  内容审核   │  │  版本管理   │              │
│  │             │  │             │  │             │              │
│  │ • 配图生成  │  │ • 原创检测  │  │ • 历史版本  │              │
│  │ • 封面设计  │  │ • 敏感词过滤│  │ • 对比还原  │              │
│  │ • 风格统一  │  │ • 事实核查  │  │ • 协作编辑  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
content_creation_platform/
├── README.md
├── requirements.txt
├── docker-compose.yml
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── services/
│   │   ├── writer.py         # 写作服务
│   │   ├── seo.py            # SEO服务
│   │   ├── translator.py     # 翻译服务
│   │   ├── image_gen.py      # 图片生成
│   │   └── reviewer.py       # 审核服务
│   │
│   ├── api/
│   │   ├── articles.py       # 文章API
│   │   ├── translations.py   # 翻译API
│   │   └── images.py         # 图片API
│   │
│   └── models/
│       ├── article.py
│       └── project.py
│
└── tests/
```

---

## 🔧 核心服务

### 1. 智能写作服务

```python
class WritingService:
    """写作辅助服务"""
    
    async def generate_outline(self, topic: str, style: str = "professional") -> dict:
        """生成文章大纲"""
        prompt = f"""为以下主题生成详细的文章大纲：

主题: {topic}
风格: {style}

要求：
1. 包含引言、主体、结论
2. 每个章节有2-3个要点
3. 预估每部分字数

返回JSON格式大纲。"""
        
        response = await self.llm.generate(prompt, response_format="json")
        return response
    
    async def expand_paragraph(self, outline_section: str, context: str = "") -> str:
        """扩写段落"""
        prompt = f"""请基于以下大纲要点扩写成完整段落：

大纲要点: {outline_section}
上下文: {context}

要求：
1. 内容充实，有具体例子
2. 逻辑清晰，过渡自然
3. 字数200-300字"""
        
        return await self.llm.generate(prompt)
    
    async def adjust_style(self, content: str, target_style: str) -> str:
        """调整文风"""
        styles = {
            "formal": "正式、专业、严谨",
            "casual": "轻松、口语化、亲切",
            "academic": "学术、客观、有引用",
            "marketing": "吸引人、有说服力、行动导向"
        }
        
        prompt = f"""将以下内容调整为{styles.get(target_style, target_style)}的风格：

原文：
{content}

保持核心意思不变，调整表达方式。"""
        
        return await self.llm.generate(prompt)
```

### 2. SEO优化服务

```python
class SEOService:
    """SEO优化服务"""
    
    async def analyze_content(self, content: str, target_keywords: list) -> dict:
        """分析内容SEO"""
        # 关键词密度
        keyword_density = self._calculate_density(content, target_keywords)
        
        # 可读性评分
        readability = self._calculate_readability(content)
        
        # 标题优化建议
        title_suggestions = await self._optimize_title(content, target_keywords)
        
        return {
            "keyword_density": keyword_density,
            "readability_score": readability,
            "title_suggestions": title_suggestions,
            "improvements": await self._get_improvements(content)
        }
    
    async def _optimize_title(self, content: str, keywords: list) -> list:
        """优化标题"""
        prompt = f"""基于以下内容和关键词，生成5个SEO友好的标题：

内容摘要：{content[:500]}
目标关键词：{', '.join(keywords)}

要求：
1. 包含关键词
2. 吸引点击
3. 50字符以内"""
        
        response = await self.llm.generate(prompt)
        return response.split('\n')
    
    def _calculate_readability(self, content: str) -> float:
        """计算可读性分数"""
        sentences = content.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # 简化的可读性公式
        if avg_sentence_length < 20:
            return 90
        elif avg_sentence_length < 30:
            return 75
        else:
            return 60
```

### 3. 多语言翻译服务

```python
class TranslationService:
    """翻译服务"""
    
    SUPPORTED_LANGUAGES = ["zh", "en", "ja", "ko", "fr", "de", "es"]
    
    async def translate(
        self,
        content: str,
        source_lang: str,
        target_lang: str,
        preserve_format: bool = True
    ) -> str:
        """翻译内容"""
        prompt = f"""将以下{source_lang}内容翻译成{target_lang}：

{content}

要求：
1. 保持原文风格和语气
2. {'保持原有格式（标题、列表等）' if preserve_format else '可以调整格式'}
3. 专业术语使用目标语言的通用表达"""
        
        return await self.llm.generate(prompt)
    
    async def translate_batch(self, contents: list, source: str, target: str) -> list:
        """批量翻译"""
        results = []
        for content in contents:
            result = await self.translate(content, source, target)
            results.append(result)
        return results
```

---

## 📋 API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/write/outline` | 生成大纲 |
| POST | `/api/write/expand` | 扩写段落 |
| POST | `/api/write/style` | 调整风格 |
| POST | `/api/seo/analyze` | SEO分析 |
| POST | `/api/translate` | 翻译内容 |
| POST | `/api/image/generate` | 生成配图 |

---

## 📊 学习目标

完成此项目后掌握：
- [x] 结构化输出应用
- [x] 多服务编排
- [x] 批量处理优化
- [x] 内容质量评估
