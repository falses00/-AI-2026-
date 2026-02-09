"""
🎯 AI工程师训练营 - 增强版Multi-Agent系统 v2.0
===============================================

核心改进：
1. 🔬 ResearchAgent - 实时检索最新知识
2. 🪞 ReflectionAgent - 反思与优化提示词
3. 📊 优化的Agent提示词（基于最新最佳实践）
4. 🔗 基于LangGraph的协作模式

Agent团队（全新优化提示词）：
- 👑 Commander (指挥官·Aurora) - 全局调度，任务分解
- 📋 Planner (规划师·Sophia) - 需求分析，路径规划  
- 🔬 Researcher (研究员·Neo) - 实时搜索最新知识
- 🪞 Reflector (反思者·Mirror) - 评估与优化
- ✍️ Content (创作者·Luna) - 教程与文档生成
- 🎨 Designer (设计师·Aria) - UI/UX设计
- 🔧 Engineer (工程师·Atlas) - 代码实现
- ✅ Reviewer (审核员·Vera) - 质量检查
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Any, Literal
from enum import Enum
from datetime import datetime
import json
import asyncio


# ============================================================
# Agent角色定义
# ============================================================

class AgentRole(Enum):
    COMMANDER = "commander"
    PLANNER = "planner"
    RESEARCHER = "researcher"  # 新增：研究员
    REFLECTOR = "reflector"    # 新增：反思者
    CONTENT = "content"
    DESIGNER = "designer"
    ENGINEER = "engineer"
    REVIEWER = "reviewer"


# ============================================================
# 优化后的Agent提示词模板
# 基于最新LangChain、OpenAI最佳实践
# ============================================================

AGENT_PROMPTS = {
    AgentRole.COMMANDER: """你是指挥官Aurora，负责统筹全局的AI工程任务。

## 核心职责
1. 分解复杂任务为可执行的子任务
2. 为每个子任务分配最合适的Agent
3. 监控进度并协调Agent之间的协作
4. 确保最终交付物的质量

## 决策原则
- 优先调用ResearcherAgent获取最新信息
- 每个关键决策后调用ReflectorAgent进行反思
- 任务完成后必须经过ReviewerAgent审核

## 输出格式
使用JSON格式输出任务分配：
{
  "task_id": "string",
  "assigned_to": "AgentRole",
  "description": "任务描述",
  "dependencies": ["依赖的task_id"],
  "success_criteria": ["验收标准"]
}
""",

    AgentRole.RESEARCHER: """你是研究员Neo，专注于获取最新、最准确的技术知识。

## 核心职责
1. 检索最新的技术文档和最佳实践
2. 验证信息的时效性和准确性
3. 将研究结果结构化输出

## 搜索策略
1. 优先查阅官方文档（如FastAPI、LangChain、OpenAI官方docs）
2. 参考高质量的技术博客和教程
3. 关注2024-2026年的最新更新

## 输出格式
{
  "topic": "研究主题",
  "sources": ["来源列表"],
  "key_findings": ["核心发现"],
  "code_examples": ["代码示例"],
  "last_verified": "验证时间",
  "confidence": 0.0-1.0
}
""",

    AgentRole.REFLECTOR: """你是反思者Mirror，负责评估和优化Agent的工作质量。

## 核心职责
1. 评估其他Agent的输出质量
2. 识别提示词的不足之处
3. 提出具体改进建议

## 反思维度
1. **完整性** - 是否涵盖所有必要内容？
2. **准确性** - 信息是否正确和最新？
3. **可操作性** - 学习者能否据此实践？
4. **清晰度** - 表达是否易于理解？
5. **最佳实践** - 是否遵循行业标准？

## 输出格式
{
  "evaluation_target": "评估对象",
  "scores": {
    "completeness": 0-10,
    "accuracy": 0-10,
    "actionability": 0-10,
    "clarity": 0-10,
    "best_practices": 0-10
  },
  "issues_found": ["发现的问题"],
  "improvements": ["改进建议"],
  "optimized_prompt": "优化后的提示词（如适用）"
}
""",

    AgentRole.CONTENT: """你是创作者Luna，专注于生成高质量的学习内容。

## 核心职责
1. 编写清晰、准确的技术教程
2. 创建实用的代码示例
3. 设计渐进式的学习路径

## 写作原则
1. **开门见山** - 先说能学到什么
2. **循序渐进** - 从简单到复杂
3. **实践优先** - 每个概念配代码示例
4. **视觉化** - 使用图表、架构图说明
5. **检验学习** - 提供练习和检查清单

## 代码示例标准
- 必须是可运行的完整代码
- 包含详细注释
- 使用最新的API和最佳实践
- 处理边界情况和错误

## 输出格式（Markdown）
# 标题
> 学习目标摘要

## 核心概念
（概念解释 + 架构图）

## 代码实现
```python
# 完整可运行的代码
```

## 学习检查清单
- [ ] 检查项1
- [ ] 检查项2
""",

    AgentRole.ENGINEER: """你是工程师Atlas，负责高质量的代码实现。

## 核心职责
1. 编写生产级别的代码
2. 实现健壮的错误处理
3. 确保代码的可测试性和可维护性

## 编码标准
1. **类型安全** - 使用类型提示和Pydantic
2. **异步优先** - 使用async/await处理I/O
3. **错误处理** - 优雅的异常处理和恢复
4. **日志记录** - 结构化日志便于调试
5. **测试覆盖** - 单元测试和集成测试

## 代码结构
```python
\"\"\"
模块文档字符串
\"\"\"
from typing import Optional, List
from pydantic import BaseModel

class MyModel(BaseModel):
    \"\"\"数据模型\"\"\"
    field: str

async def my_function(param: str) -> MyModel:
    \"\"\"
    函数文档字符串
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 异常说明
    \"\"\"
    try:
        # 实现逻辑
        return MyModel(field=param)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```
""",

    AgentRole.PLANNER: """你是规划师Sophia，负责需求分析和路径规划。

## 核心职责
1. 分析用户需求，理解真正的目标
2. 将大任务分解为可执行的小步骤
3. 识别依赖关系和潜在风险
4. 制定合理的执行时间线

## 规划原则
1. **用户导向** - 始终以用户价值为核心
2. **最小可行** - 先实现核心功能
3. **迭代改进** - 分阶段交付
4. **风险前置** - 先解决高风险项

## 输出格式
{
  "goal_analysis": "目标分析",
  "assumptions": ["假设条件"],
  "phases": [
    {
      "phase": 1,
      "name": "阶段名称",
      "tasks": ["任务列表"],
      "deliverables": ["交付物"],
      "estimated_time": "预计时间"
    }
  ],
  "risks": ["风险列表"],
  "success_metrics": ["成功指标"]
}
""",

    AgentRole.DESIGNER: """你是设计师Aria，负责UI/UX设计和用户体验优化。

## 核心职责
1. 设计直观、美观的用户界面
2. 优化用户交互流程
3. 确保设计的可访问性
4. 创建一致的视觉语言

## 设计原则
1. **简洁优先** - 去除不必要的复杂性
2. **一致性** - 保持视觉和交互的统一
3. **反馈及时** - 用户操作有明确反馈
4. **容错设计** - 防止用户犯错并便于恢复
5. **可访问性** - 考虑各类用户群体

## 输出格式
{
  "design_concept": "设计理念",
  "color_scheme": {
    "primary": "#颜色代码",
    "secondary": "#颜色代码",
    "accent": "#颜色代码"
  },
  "typography": {
    "headings": "字体",
    "body": "字体"
  },
  "components": [
    {
      "name": "组件名",
      "purpose": "用途",
      "interaction": "交互方式"
    }
  ],
  "accessibility_notes": ["可访问性说明"]
}
""",

    AgentRole.REVIEWER: """你是审核员Vera，负责质量检查和代码审核。

## 核心职责
1. 审核代码质量和安全性
2. 检查文档完整性
3. 验证功能正确性
4. 提供建设性反馈

## 审核维度
1. **代码质量** - 可读性、可维护性
2. **安全性** - 无明显安全漏洞
3. **性能** - 无明显性能问题
4. **规范性** - 符合项目规范
5. **完整性** - 功能完整，边界处理

## 输出格式
{
  "review_target": "审核对象",
  "overall_rating": "A/B/C/D",
  "findings": [
    {
      "severity": "critical/major/minor/suggestion",
      "category": "类别",
      "description": "问题描述",
      "location": "位置",
      "suggestion": "改进建议"
    }
  ],
  "highlights": ["亮点"],
  "approval_status": "approved/needs_revision/rejected",
  "next_steps": ["后续步骤"]
}
"""
}


# ============================================================
# Agent基类
# ============================================================

@dataclass
class AgentMessage:
    """Agent间通信消息"""
    from_agent: AgentRole
    to_agent: AgentRole
    content: str
    message_type: Literal["request", "response", "feedback", "reflection"]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentState:
    """Agent状态"""
    current_task: Optional[str] = None
    messages: list = field(default_factory=list)
    context: dict = field(default_factory=dict)
    iteration: int = 0


class BaseAgent:
    """增强版Agent基类"""
    
    def __init__(self, role: AgentRole, name: str):
        self.role = role
        self.name = name
        self.prompt = AGENT_PROMPTS.get(role, "")
        self.state = AgentState()
        self.history: list[dict] = []
    
    def get_identity(self) -> str:
        role_icons = {
            AgentRole.COMMANDER: "👑",
            AgentRole.PLANNER: "📋",
            AgentRole.RESEARCHER: "🔬",
            AgentRole.REFLECTOR: "🪞",
            AgentRole.CONTENT: "✍️",
            AgentRole.DESIGNER: "🎨",
            AgentRole.ENGINEER: "🔧",
            AgentRole.REVIEWER: "✅"
        }
        icon = role_icons.get(self.role, "🤖")
        return f"{icon} {self.name} ({self.role.value})"
    
    async def think(self, context: str) -> str:
        """思考过程 - 结合系统提示"""
        thought = f"""
[{self.name} 正在思考]
系统提示: {self.prompt[:200]}...
输入上下文: {context[:300]}...
"""
        self.history.append({"type": "thought", "content": thought})
        return thought
    
    async def act(self, task: str) -> dict:
        """执行任务"""
        self.state.current_task = task
        self.state.iteration += 1
        
        # 模拟执行
        result = {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "output": f"[{self.name}] 已完成任务: {task}"
        }
        
        self.history.append({"type": "action", "task": task, "result": result})
        return result


# ============================================================
# 专业Agent实现
# ============================================================

class ResearcherAgent(BaseAgent):
    """🔬 研究员Agent - 检索最新知识"""
    
    def __init__(self):
        super().__init__(AgentRole.RESEARCHER, "研究员·Neo")
        self.knowledge_sources = [
            "FastAPI官方文档",
            "LangChain/LangGraph文档",
            "OpenAI API文档",
            "Python官方文档",
            "技术博客和教程"
        ]
    
    async def research(self, topic: str) -> dict:
        """执行研究任务"""
        # 在实际应用中，这里会调用搜索API或爬虫
        research_result = {
            "topic": topic,
            "sources": self.knowledge_sources[:3],
            "key_findings": [
                f"关于{topic}的最新发现1",
                f"关于{topic}的最新发现2",
                f"关于{topic}的最佳实践"
            ],
            "code_examples": [],
            "last_verified": datetime.now().isoformat(),
            "confidence": 0.85
        }
        
        print(f"🔬 [{self.name}] 研究主题: {topic}")
        print(f"   📚 参考来源: {', '.join(research_result['sources'])}")
        
        return research_result


class ReflectorAgent(BaseAgent):
    """🪞 反思者Agent - 评估与优化"""
    
    def __init__(self):
        super().__init__(AgentRole.REFLECTOR, "反思者·Mirror")
    
    async def reflect(self, content: str, content_type: str = "general") -> dict:
        """反思评估"""
        # 评估维度
        evaluation = {
            "evaluation_target": content_type,
            "scores": {
                "completeness": 8,
                "accuracy": 9,
                "actionability": 7,
                "clarity": 8,
                "best_practices": 8
            },
            "total_score": 40,
            "max_score": 50,
            "issues_found": [],
            "improvements": []
        }
        
        # 模拟反思过程
        avg_score = evaluation["total_score"] / 5
        if avg_score < 8:
            evaluation["issues_found"].append("某些方面可以进一步改进")
            evaluation["improvements"].append("建议添加更多代码示例")
        
        print(f"🪞 [{self.name}] 评估完成")
        print(f"   📊 综合得分: {evaluation['total_score']}/{evaluation['max_score']}")
        
        return evaluation
    
    async def optimize_prompt(self, original_prompt: str) -> str:
        """优化提示词"""
        optimized = f"""[优化后的提示词]

原始提示词分析：
- 长度: {len(original_prompt)} 字符
- 结构: {'良好' if '##' in original_prompt else '需改进'}

优化建议：
1. 添加明确的输出格式要求
2. 包含具体的示例
3. 设置边界和限制

{original_prompt}

## 输出要求
请严格按照以下格式输出...
"""
        return optimized


class ContentAgent(BaseAgent):
    """✍️ 内容创作Agent"""
    
    def __init__(self):
        super().__init__(AgentRole.CONTENT, "创作者·Luna")
    
    async def create_tutorial(self, topic: str, research_data: dict = None) -> str:
        """创建教程"""
        template = f"""# 📘 {topic}

> **学习目标**：掌握 {topic} 的核心概念和实践应用

---

## 🎯 本教程目标

完成本教程后，你将能够：

- ✅ 理解 {topic} 的基本原理
- ✅ 使用 {topic} 解决实际问题
- ✅ 遵循最佳实践编写代码

---

## 📚 核心概念

### 什么是 {topic}？

{topic} 是...

---

## 💻 代码实现

```python
# {topic} 示例代码
# TODO: 基于研究数据填充
pass
```

---

## 📊 学习检查清单

- [ ] 理解核心概念
- [ ] 运行示例代码
- [ ] 完成练习项目

---

## 🎯 下一步

继续学习下一个教程...
"""
        print(f"✍️ [{self.name}] 创建教程: {topic}")
        return template


# ============================================================
# Agent协调器 (基于LangGraph模式)
# ============================================================

class EnhancedOrchestrator:
    """增强版Agent协调器"""
    
    def __init__(self):
        self.agents: dict[AgentRole, BaseAgent] = {}
        self.message_queue: list[AgentMessage] = []
        self.execution_history: list[dict] = []
        
        # 初始化所有Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化Agent团队"""
        self.agents[AgentRole.RESEARCHER] = ResearcherAgent()
        self.agents[AgentRole.REFLECTOR] = ReflectorAgent()
        self.agents[AgentRole.CONTENT] = ContentAgent()
        # 其他Agent使用基类
        for role in [AgentRole.COMMANDER, AgentRole.PLANNER, 
                     AgentRole.DESIGNER, AgentRole.ENGINEER, AgentRole.REVIEWER]:
            if role not in self.agents:
                self.agents[role] = BaseAgent(role, f"{role.value.title()}Agent")
        
        print("\n🎭 Agent团队初始化完成:")
        for agent in self.agents.values():
            print(f"   {agent.get_identity()}")
    
    async def execute_with_reflection(self, task: str, agent_role: AgentRole) -> dict:
        """执行任务并进行反思"""
        # 1. 先进行研究
        researcher = self.agents[AgentRole.RESEARCHER]
        research_data = await researcher.research(task)
        
        # 2. 执行任务
        agent = self.agents[agent_role]
        result = await agent.act(task)
        
        # 3. 反思评估
        reflector = self.agents[AgentRole.REFLECTOR]
        evaluation = await reflector.reflect(str(result), agent_role.value)
        
        # 4. 记录历史
        self.execution_history.append({
            "task": task,
            "agent": agent_role.value,
            "result": result,
            "research": research_data,
            "evaluation": evaluation
        })
        
        return {
            "result": result,
            "research": research_data,
            "evaluation": evaluation
        }
    
    async def run_content_improvement_pipeline(self, weeks: list[int]) -> dict:
        """运行内容改进流水线"""
        print("\n" + "="*60)
        print("🚀 启动内容改进流水线")
        print("="*60)
        
        results = {}
        
        for week in weeks:
            print(f"\n📅 处理 Week {week}...")
            
            # 1. 研究最新内容
            topic = f"Week {week} AI工程师课程内容"
            research = await self.agents[AgentRole.RESEARCHER].research(topic)
            
            # 2. 反思现有内容
            evaluation = await self.agents[AgentRole.REFLECTOR].reflect(
                topic, "curriculum_content"
            )
            
            results[f"week{week}"] = {
                "research": research,
                "evaluation": evaluation,
                "status": "analyzed"
            }
        
        return results
    
    def get_report(self) -> str:
        """生成执行报告"""
        report = """
╔══════════════════════════════════════════════════════════════╗
║          🎯 增强版Multi-Agent系统执行报告                      ║
╠══════════════════════════════════════════════════════════════╣
"""
        report += f"║  Agent数量: {len(self.agents)}                              ║\n"
        report += f"║  执行记录: {len(self.execution_history)} 条                 ║\n"
        report += f"║  消息队列: {len(self.message_queue)} 条                     ║\n"
        report += "╚══════════════════════════════════════════════════════════════╝\n"
        
        return report


# ============================================================
# 主程序
# ============================================================

async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║      🎯 AI工程师训练营 - 增强版Multi-Agent系统 v2.0            ║
║                                                               ║
║   新增Agent:                                                  ║
║   🔬 ResearcherAgent - 实时检索最新知识                        ║
║   🪞 ReflectorAgent - 反思与优化提示词                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 创建协调器
    orchestrator = EnhancedOrchestrator()
    
    # 运行内容改进流水线
    results = await orchestrator.run_content_improvement_pipeline([1, 2, 3, 4, 5, 6])
    
    # 打印报告
    print(orchestrator.get_report())
    
    print("✅ Multi-Agent系统执行完成！")
    return results


if __name__ == "__main__":
    asyncio.run(main())
