# 🛠️ 个人AI工作台项目

> **Week 12 毕业项目选项C** - 个人效率AI助手

---

## 🎯 项目概述

构建一个个人AI工作台，整合日常工作流程：
- 日程管理Agent
- 邮件智能处理
- 会议纪要生成
- 任务分解与跟踪

---

## 📊 功能模块

```
┌─────────────────────────────────────────────────────────────────┐
│                     个人AI工作台                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                   智能对话入口                          │    │
│   │   "帮我安排明天的工作" / "总结今天的邮件"              │    │
│   └────────────────────────────────────────────────────────┘    │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│   ┌───────────┐      ┌───────────┐      ┌───────────┐          │
│   │ 日程Agent  │      │ 邮件Agent  │      │ 任务Agent  │          │
│   │           │      │           │      │           │          │
│   │• 日程安排 │      │• 邮件摘要 │      │• 任务拆解 │          │
│   │• 提醒管理 │      │• 自动回复 │      │• 进度跟踪 │          │
│   │• 冲突检测 │      │• 优先排序 │      │• 截止提醒 │          │
│   └───────────┘      └───────────┘      └───────────┘          │
│         │                   │                   │               │
│         └───────────────────┴───────────────────┘               │
│                             │                                    │
│                             ▼                                    │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                    统一数据存储                         │    │
│   │        SQLite + 日历API + 邮件API                      │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
personal_ai_workspace/
├── README.md
├── requirements.txt
├── config.yaml
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── agents/
│   │   ├── scheduler.py      # 日程Agent
│   │   ├── email_agent.py    # 邮件Agent
│   │   └── task_agent.py     # 任务Agent
│   │
│   ├── tools/
│   │   ├── calendar.py       # 日历工具
│   │   ├── email.py          # 邮件工具
│   │   └── todo.py           # 任务工具
│   │
│   ├── services/
│   │   ├── orchestrator.py   # 编排器
│   │   └── memory.py         # 记忆服务
│   │
│   └── database/
│       ├── models.py
│       └── crud.py
│
└── tests/
```

---

## 🔧 核心Agent

### 1. 日程管理Agent

```python
from datetime import datetime, timedelta

class SchedulerAgent:
    """日程管理Agent"""
    
    tools = [
        {
            "name": "create_event",
            "description": "创建日程事件",
            "parameters": {
                "title": "事件标题",
                "start_time": "开始时间 (ISO格式)",
                "duration_minutes": "持续时间（分钟）",
                "reminder_minutes": "提前提醒时间"
            }
        },
        {
            "name": "list_events",
            "description": "列出指定日期的日程",
            "parameters": {
                "date": "日期 (YYYY-MM-DD)"
            }
        },
        {
            "name": "check_conflicts",
            "description": "检查时间冲突",
            "parameters": {
                "start_time": "开始时间",
                "end_time": "结束时间"
            }
        }
    ]
    
    async def process(self, request: str) -> str:
        """处理日程相关请求"""
        # 1. 理解意图
        intent = await self._understand_intent(request)
        
        # 2. 规划执行
        if intent["action"] == "schedule":
            # 检查冲突
            conflicts = await self.check_conflicts(intent["time"])
            if conflicts:
                return f"该时段已有安排：{conflicts}，建议调整到..."
            
            # 创建事件
            event = await self.create_event(intent)
            return f"已为您安排：{event['title']}，时间 {event['time']}"
        
        elif intent["action"] == "query":
            events = await self.list_events(intent["date"])
            return self._format_schedule(events)
    
    async def daily_brief(self) -> str:
        """每日简报"""
        today = datetime.now().strftime("%Y-%m-%d")
        events = await self.list_events(today)
        
        prompt = f"""基于今日日程生成简报：

日程列表：
{self._format_events(events)}

要求：
1. 按时间顺序
2. 提醒重要事项
3. 指出空闲时段"""
        
        return await self.llm.generate(prompt)
```

### 2. 邮件处理Agent

```python
class EmailAgent:
    """邮件处理Agent"""
    
    tools = [
        {
            "name": "fetch_emails",
            "description": "获取未读邮件"
        },
        {
            "name": "summarize_email",
            "description": "总结邮件内容"
        },
        {
            "name": "draft_reply",
            "description": "起草回复"
        },
        {
            "name": "categorize_emails",
            "description": "邮件分类"
        }
    ]
    
    async def process_inbox(self) -> dict:
        """处理收件箱"""
        # 1. 获取未读邮件
        emails = await self.fetch_emails(unread=True)
        
        # 2. 分类
        categorized = await self.categorize(emails)
        
        # 3. 生成摘要
        summaries = []
        for email in emails[:10]:  # Top 10
            summary = await self.summarize(email)
            summaries.append({
                "from": email["from"],
                "subject": email["subject"],
                "summary": summary,
                "priority": await self._assess_priority(email)
            })
        
        return {
            "total_unread": len(emails),
            "categories": categorized,
            "summaries": summaries
        }
    
    async def auto_reply(self, email: dict, template: str = None) -> str:
        """自动生成回复草稿"""
        prompt = f"""为以下邮件生成回复草稿：

发件人: {email['from']}
主题: {email['subject']}
内容: {email['body'][:1000]}

要求：
1. 专业礼貌
2. 直接回应问题
3. 简洁明了

{'使用模板风格: ' + template if template else ''}"""
        
        return await self.llm.generate(prompt)
```

### 3. 任务管理Agent

```python
class TaskAgent:
    """任务管理Agent"""
    
    async def decompose_task(self, task: str) -> list:
        """分解任务"""
        prompt = f"""将以下任务分解为可执行的子任务：

任务: {task}

要求：
1. 每个子任务具体可执行
2. 按逻辑顺序排列
3. 估算每个子任务时间
4. 标注依赖关系

返回JSON格式列表。"""
        
        response = await self.llm.generate(prompt, response_format="json")
        return response
    
    async def track_progress(self, project_id: str) -> dict:
        """跟踪项目进度"""
        tasks = await self.db.get_tasks(project_id)
        
        completed = [t for t in tasks if t.status == "done"]
        in_progress = [t for t in tasks if t.status == "doing"]
        pending = [t for t in tasks if t.status == "todo"]
        
        # 计算进度
        progress = len(completed) / len(tasks) * 100 if tasks else 0
        
        # 估算完成时间
        if in_progress:
            avg_time = sum(t.estimated_hours for t in completed) / len(completed)
            remaining_hours = len(pending) * avg_time
        
        return {
            "progress": progress,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "pending": len(pending),
            "estimated_completion": remaining_hours if in_progress else None
        }
```

---

## 📋 使用场景

| 场景 | 对话示例 | Agent响应 |
|------|---------|-----------|
| 日程查询 | "明天有什么安排？" | 列出明日日程 |
| 任务分解 | "帮我规划这个项目" | 生成子任务列表 |
| 邮件摘要 | "总结今天的重要邮件" | 返回邮件摘要 |
| 智能安排 | "下周找个2小时空闲" | 推荐可用时段 |

---

## 📊 学习目标

- [x] Agent工具设计
- [x] 多Agent协作
- [x] 外部API集成
- [x] 个人助手构建
