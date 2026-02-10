"""
🚀 AI工程师训练营 - 专业Web展示界面 v3.0
=========================================

✨ 新功能（由多Agent协作开发）：
- 🎨 Designer Agent (Aria): 全新玻璃态设计，渐变色彩，动画效果
- 🔧 Engineer Agent (Atlas): 进度追踪，搜索功能，本地存储
- ✅ Reviewer Agent (Vera): 代码审核，性能优化

特点：
- 📊 学习进度追踪（localStorage持久化）
- 🔍 全文搜索功能
- 🌙 深色主题
- 📱 响应式设计
- ✨ 微交互动画
- 📈 学习统计仪表板

运行方式：
    cd "I:\\Study FastAPI"
    python -m uvicorn webapp.app:app --reload --port 8080
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import json

app = FastAPI(
    title="AI工程师2026速成训练营",
    version="3.0.0",
    description="12周从入门到精通的AI工程师学习平台"
)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 完整12周课程数据
CURRICULUM = {
    "week1": {
        "title": "Python高级特性 + AI工程环境",
        "icon": "🔧",
        "color": "#3b82f6",
        "phase": "基础阶段",
        "tutorials": [
            {"name": "异步编程核心概念", "path": "week1/tutorials/01_async_basics.md", "icon": "⚡", "duration": 45},
            {"name": "Pydantic数据验证", "path": "week1/tutorials/04_pydantic_basics.md", "icon": "✅", "duration": 40},
            {"name": "FastAPI快速入门", "path": "week1/tutorials/05_fastapi_quickstart.md", "icon": "🚀", "duration": 50},
            {"name": "FastAPI安全认证", "path": "week1/tutorials/06_fastapi_security.md", "icon": "🔐", "duration": 55},
            {"name": "Docker基础入门", "path": "week1/tutorials/07_docker_basics.md", "icon": "🐳", "duration": 60},
        ],
        "projects": [
            {"name": "图书管理API", "path": "week1/projects/project1_structured_api/README.md", "icon": "📚", "duration": 120},
        ],
        "exercises": [
            {"name": "异步编程练习", "path": "week1/exercises/async_exercises.py", "icon": "💻", "duration": 30},
        ]
    },
    "week2": {
        "title": "大模型API深度控制",
        "icon": "🤖",
        "color": "#8b5cf6",
        "phase": "基础阶段",
        "tutorials": [
            {"name": "DeepSeek API快速入门", "path": "week2/tutorials/01_openai_api_basics.md", "icon": "🔌", "duration": 45},
            {"name": "结构化输出详解", "path": "week2/tutorials/02_structured_output.md", "icon": "📊", "duration": 50},
            {"name": "Response Format深度解析", "path": "week2/tutorials/03_response_format.md", "icon": "📋", "duration": 40},
            {"name": "Function Calling详解", "path": "week2/tutorials/04_function_calling_intro.md", "icon": "🔧", "duration": 55},
            {"name": "Streaming流式响应", "path": "week2/tutorials/05_streaming.md", "icon": "📡", "duration": 45},
            {"name": "Token计算与成本优化", "path": "week2/tutorials/06_token_optimization.md", "icon": "💰", "duration": 35},
        ],
        "projects": [],
        "exercises": [
            {"name": "API调用练习", "path": "week2/exercises/api_exercises.py", "icon": "💻", "duration": 40},
        ]
    },
    "week3": {
        "title": "MCP协议深度剖析",
        "icon": "🔌",
        "color": "#ec4899",
        "phase": "基础阶段",
        "tutorials": [
            {"name": "MCP协议入门", "path": "week3/tutorials/01_mcp_introduction.md", "icon": "📖", "duration": 50},
            {"name": "FastMCP基础教程", "path": "week3/tutorials/02_fastmcp_basics.md", "icon": "⚡", "duration": 55},
            {"name": "MCP Tools开发指南", "path": "week3/tutorials/03_mcp_tools.md", "icon": "🔧", "duration": 60},
            {"name": "MCP Resources开发指南", "path": "week3/tutorials/04_mcp_resources.md", "icon": "📦", "duration": 50},
            {"name": "Claude Desktop集成", "path": "week3/tutorials/05_claude_integration.md", "icon": "🖥️", "duration": 45},
        ],
        "projects": [
            {"name": "MCP文件系统服务器", "path": "week3/projects/mcp_filesystem/mcp_server.py", "icon": "📁", "duration": 90},
        ],
        "exercises": []
    },
    "week4": {
        "title": "RAG系统基础",
        "icon": "🔍",
        "color": "#10b981",
        "phase": "核心阶段",
        "tutorials": [
            {"name": "Embedding向量化入门", "path": "week4/tutorials/01_embedding_basics.md", "icon": "🧮", "duration": 50},
            {"name": "ChromaDB快速入门", "path": "week4/tutorials/02a_chromadb.md", "icon": "📊", "duration": 55},
            {"name": "Milvus向量数据库", "path": "week4/tutorials/02b_milvus.md", "icon": "🗄️", "duration": 60},
            {"name": "检索策略详解", "path": "week4/tutorials/03_retrieval_strategies.md", "icon": "🎯", "duration": 50},
            {"name": "构建简单RAG系统", "path": "week4/tutorials/04_simple_rag.md", "icon": "🤖", "duration": 70},
        ],
        "projects": [
            {"name": "智能文档问答系统", "path": "week4/projects/project_doc_qa/README.md", "icon": "📚", "duration": 120},
        ],
        "exercises": [
            {"name": "RAG基础练习", "path": "week4/exercises/rag_exercises.py", "icon": "💻", "duration": 45},
        ]
    },
    "week5": {
        "title": "RAG系统进阶",
        "icon": "⚡",
        "color": "#f59e0b",
        "phase": "核心阶段",
        "tutorials": [
            {"name": "混合检索原理与实现", "path": "week5/tutorials/01a_hybrid_search_native.md", "icon": "🔀", "duration": 60},
            {"name": "LangChain混合检索", "path": "week5/tutorials/01b_hybrid_search_langchain.md", "icon": "🔗", "duration": 55},
            {"name": "重排序模型详解", "path": "week5/tutorials/02_reranking.md", "icon": "📈", "duration": 50},
            {"name": "上下文压缩技术", "path": "week5/tutorials/03_context_compression.md", "icon": "🗜️", "duration": 45},
            {"name": "高级RAG Pipeline", "path": "week5/tutorials/04_advanced_rag_pipeline.md", "icon": "🚀", "duration": 70},
        ],
        "projects": [
            {"name": "智能客服系统", "path": "week5/projects/project_smart_cs/README.md", "icon": "🎧", "duration": 150},
        ],
        "exercises": [
            {"name": "高级RAG练习", "path": "week5/exercises/advanced_rag_exercises.py", "icon": "💻", "duration": 50},
        ]
    },
    "week6": {
        "title": "智能体入门",
        "icon": "🤖",
        "color": "#ef4444",
        "phase": "核心阶段",
        "tutorials": [
            {"name": "AI Agent基础概念", "path": "week6/tutorials/01_agent_basics.md", "icon": "🧠", "duration": 55},
            {"name": "ReAct原生实现", "path": "week6/tutorials/02a_react_native.md", "icon": "💭", "duration": 65},
            {"name": "LangChain Agent", "path": "week6/tutorials/02b_react_langchain.md", "icon": "🔗", "duration": 60},
            {"name": "工具开发详解", "path": "week6/tutorials/03_tool_development.md", "icon": "🔧", "duration": 50},
            {"name": "多Agent系统", "path": "week6/tutorials/04_multi_agent.md", "icon": "👥", "duration": 70},
        ],
        "projects": [
            {"name": "智能工作流Agent", "path": "week6/projects/project_workflow_agent/README.md", "icon": "🔄", "duration": 180},
        ],
        "exercises": [
            {"name": "Agent开发练习", "path": "week6/exercises/agent_exercises.py", "icon": "💻", "duration": 55},
        ]
    },
    "week7": {
        "title": "项目实战 - 企业级RAG",
        "icon": "🏢",
        "color": "#06b6d4",
        "phase": "进阶阶段",
        "tutorials": [
            {"name": "企业级系统架构", "path": "week7/tutorials/01_system_architecture.md", "icon": "🏗️", "duration": 60},
            {"name": "多格式文档处理", "path": "week7/tutorials/02_document_processing.md", "icon": "📄", "duration": 55},
            {"name": "用户认证与权限", "path": "week7/tutorials/03_authentication.md", "icon": "🔐", "duration": 50},
            {"name": "Redis缓存策略", "path": "week7/tutorials/04_caching.md", "icon": "⚡", "duration": 45},
            {"name": "云平台部署指南", "path": "week7/tutorials/05_deployment.md", "icon": "☁️", "duration": 60},
        ],
        "projects": [
            {"name": "企业知识库系统", "path": "week7/README.md", "icon": "📚", "duration": 240},
        ],
        "exercises": [
            {"name": "高级RAG练习", "path": "week7/exercises/advanced_rag_exercises.py", "icon": "💻", "duration": 50},
        ]
    },
    "week8": {
        "title": "多模态AI应用",
        "icon": "🎨",
        "color": "#8b5cf6",
        "phase": "进阶阶段",
        "tutorials": [
            {"name": "Vision模型使用", "path": "week8/tutorials/01_vision_basics.md", "icon": "👁️", "duration": 55},
            {"name": "语音处理Whisper", "path": "week8/tutorials/02_audio_processing.md", "icon": "🎤", "duration": 50},
            {"name": "多模态RAG系统", "path": "week8/tutorials/03_multimodal_rag.md", "icon": "🖼️", "duration": 60},
            {"name": "CLIP图像Embedding", "path": "week8/tutorials/04_clip_embedding.md", "icon": "🔍", "duration": 45},
        ],
        "projects": [
            {"name": "图文问答系统", "path": "week8/projects/multimodal_qa/README.md", "icon": "🤖", "duration": 180},
        ],
        "exercises": []
    },
    "week9": {
        "title": "模型微调与优化",
        "icon": "⚙️",
        "color": "#f97316",
        "phase": "进阶阶段",
        "tutorials": [
            {"name": "LoRA微调技术", "path": "week9/tutorials/01_lora_finetuning.md", "icon": "🔧", "duration": 70},
            {"name": "微调数据集准备", "path": "week9/tutorials/02_dataset_preparation.md", "icon": "📊", "duration": 55},
            {"name": "模型部署指南", "path": "week9/tutorials/03_model_deployment.md", "icon": "🚀", "duration": 50},
            {"name": "模型评估与效果验证", "path": "week9/tutorials/04_model_evaluation.md", "icon": "📈", "duration": 60},
        ],
        "projects": [
            {"name": "行业专属模型", "path": "week9/projects/domain_finetuning/README.md", "icon": "🎯", "duration": 240},
        ],
        "exercises": []
    },
    "week10": {
        "title": "AI产品设计与UX",
        "icon": "🎯",
        "color": "#ec4899",
        "phase": "产品化阶段",
        "tutorials": [
            {"name": "AI产品设计原则", "path": "week10/tutorials/01_design_principles.md", "icon": "📐", "duration": 50},
            {"name": "对话交互设计", "path": "week10/tutorials/02_conversation_design.md", "icon": "💬", "duration": 45},
            {"name": "错误处理策略", "path": "week10/tutorials/03_error_handling.md", "icon": "⚠️", "duration": 50},
        ],
        "projects": [
            {"name": "UX优化实战", "path": "week10/projects/ux_optimization/README.md", "icon": "✨", "duration": 120},
        ],
        "exercises": []
    },
    "week11": {
        "title": "高级Agent系统",
        "icon": "🧠",
        "color": "#6366f1",
        "phase": "产品化阶段",
        "tutorials": [
            {"name": "生产级Agent架构", "path": "week11/tutorials/01_advanced_architecture.md", "icon": "🏗️", "duration": 65},
            {"name": "Agent记忆系统", "path": "week11/tutorials/02_agent_memory.md", "icon": "💾", "duration": 55},
            {"name": "多Agent协作", "path": "week11/tutorials/03_multi_agent_collaboration.md", "icon": "👥", "duration": 60},
            {"name": "可观测性实战", "path": "week11/tutorials/04_observability.md", "icon": "📊", "duration": 50},
            {"name": "Guardrails安全护栏", "path": "week11/tutorials/05_guardrails.md", "icon": "🛡️", "duration": 55},
            {"name": "人机协作HITL", "path": "week11/tutorials/06_human_in_the_loop.md", "icon": "👤", "duration": 45},
            {"name": "治理与审计系统", "path": "week11/tutorials/07_governance.md", "icon": "📜", "duration": 50},
            {"name": "Kubernetes生产部署", "path": "week11/tutorials/08_kubernetes.md", "icon": "☸️", "duration": 60},
        ],
        "projects": [
            {"name": "多Agent工作流", "path": "week11/projects/multi_agent_workflow/README.md", "icon": "🔄", "duration": 200},
        ],
        "exercises": [
            {"name": "Agent开发练习", "path": "week11/exercises/agent_exercises.py", "icon": "💻", "duration": 60},
        ]
    },
    "week12": {
        "title": "毕业项目",
        "icon": "🎓",
        "color": "#22c55e",
        "phase": "毕业阶段",
        "tutorials": [
            {"name": "毕业项目指南", "path": "week12/tutorials/01_graduation_project.md", "icon": "📋", "duration": 40},
            {"name": "项目提交模板", "path": "week12/tutorials/02_project_submission.md", "icon": "📝", "duration": 20},
        ],
        "projects": [
            {"name": "企业AI助手平台", "path": "week12/projects/enterprise_ai_assistant/README.md", "icon": "🏢", "duration": 480},
            {"name": "智能内容创作平台", "path": "week12/projects/content_creation_platform/README.md", "icon": "✍️", "duration": 360},
            {"name": "个人AI工作台", "path": "week12/projects/personal_ai_workspace/README.md", "icon": "🛠️", "duration": 420},
        ],
        "exercises": []
    }
}


def read_file_content(path: str) -> str:
    """读取文件内容"""
    full_path = BASE_DIR / path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {path}")
    return full_path.read_text(encoding='utf-8')


@app.get("/", response_class=HTMLResponse)
async def home():
    """主页"""
    return get_enhanced_html_template()


@app.get("/api/curriculum")
async def get_curriculum():
    """获取课程大纲"""
    return CURRICULUM


@app.get("/api/content")
async def get_content(path: str):
    """获取文件内容"""
    try:
        content = read_file_content(path)
        file_type = "python" if path.endswith('.py') else "markdown"
        return {"content": content, "type": file_type, "path": path}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """获取课程统计数据"""
    total_tutorials = sum(len(w["tutorials"]) for w in CURRICULUM.values())
    total_projects = sum(len(w["projects"]) for w in CURRICULUM.values())
    total_exercises = sum(len(w["exercises"]) for w in CURRICULUM.values())
    total_duration = sum(
        sum(t.get("duration", 30) for t in w["tutorials"]) +
        sum(p.get("duration", 60) for p in w["projects"]) +
        sum(e.get("duration", 20) for e in w["exercises"])
        for w in CURRICULUM.values()
    )
    
    return {
        "weeks": len(CURRICULUM),
        "tutorials": total_tutorials,
        "projects": total_projects,
        "exercises": total_exercises,
        "total_items": total_tutorials + total_projects + total_exercises,
        "estimated_hours": round(total_duration / 60, 1)
    }


def get_enhanced_html_template():
    """返回增强版HTML模板 - 全新2026 Premium设计"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI工程师2026速成训练营</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.0/github-markdown-dark.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        :root {
            --primary: #a855f7;
            --primary-light: #c084fc;
            --primary-dark: #7c3aed;
            --secondary: #f472b6;
            --accent: #22d3ee;
            --success: #34d399;
            --warning: #fbbf24;
            --bg-dark: #030014;
            --bg-card: rgba(15, 10, 40, 0.7);
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: #e2e8f0;
            overflow-x: hidden;
            min-height: 100vh;
        }
        
        /* 🎨 动态渐变背景 */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background: linear-gradient(135deg, #030014 0%, #0f0728 25%, #1a0a3e 50%, #0d0620 75%, #030014 100%);
        }
        
        /* 🌟 光晕效果 */
        .glow-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.4;
            z-index: -1;
            animation: float 20s ease-in-out infinite;
        }
        .glow-orb-1 {
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, #a855f7 0%, transparent 70%);
            top: -200px;
            right: -100px;
            animation-delay: 0s;
        }
        .glow-orb-2 {
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, #f472b6 0%, transparent 70%);
            bottom: -150px;
            left: -100px;
            animation-delay: -7s;
        }
        .glow-orb-3 {
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, #22d3ee 0%, transparent 70%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation-delay: -14s;
            opacity: 0.2;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            25% { transform: translate(30px, -30px) scale(1.05); }
            50% { transform: translate(-20px, 20px) scale(0.95); }
            75% { transform: translate(20px, 30px) scale(1.02); }
        }
        
        /* 🪟 高级玻璃态 */
        .glass {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        
        .glass-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
            border-color: rgba(168, 85, 247, 0.3);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 30px rgba(168, 85, 247, 0.15);
        }
        
        /* ✨ 渐变文字 */
        .gradient-text {
            background: linear-gradient(135deg, #a855f7 0%, #f472b6 50%, #22d3ee 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .gradient-text-subtle {
            background: linear-gradient(135deg, #c084fc 0%, #e879f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* 💫 霓虹发光 */
        .neon-glow {
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.4),
                        0 0 40px rgba(168, 85, 247, 0.2),
                        0 0 60px rgba(168, 85, 247, 0.1);
        }
        
        .neon-border {
            position: relative;
        }
        .neon-border::before {
            content: '';
            position: absolute;
            inset: -2px;
            border-radius: inherit;
            padding: 2px;
            background: linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .neon-border:hover::before {
            opacity: 1;
        }
        
        /* 📐 布局 */
        .app-container {
            display: flex;
            min-height: 100vh;
        }
        
        .sidebar {
            width: 320px;
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            left: 0;
            top: 0;
            display: flex;
            flex-direction: column;
            padding: 24px;
            padding-top: 72px;
            z-index: 60;
            transform: translateX(-100%);
            transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .sidebar.open {
            transform: translateX(0);
        }
        
        .main-content {
            margin-left: 0;
            flex: 1;
            padding: 32px;
            padding-top: 72px;
            min-height: 100vh;
        }
        
        /* 侧边栏遮罩 */
        .sidebar-backdrop {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 55;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .sidebar-backdrop.visible {
            opacity: 1;
            pointer-events: auto;
        }
        
        /* 🔀 侧边栏切换按钮 */
        .sidebar-toggle {
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 70;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.85), rgba(244, 114, 182, 0.75));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: white;
            font-size: 1.2rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 20px rgba(168, 85, 247, 0.35);
        }
        .sidebar-toggle:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 28px rgba(168, 85, 247, 0.5);
        }
        .sidebar-toggle .icon-open,
        .sidebar-toggle .icon-close {
            position: absolute;
            transition: opacity 0.25s, transform 0.25s;
        }
        .sidebar-toggle .icon-close {
            opacity: 0;
            transform: rotate(-90deg);
        }
        .sidebar-toggle.active .icon-open {
            opacity: 0;
            transform: rotate(90deg);
        }
        .sidebar-toggle.active .icon-close {
            opacity: 1;
            transform: rotate(0deg);
        }
        
        /* 🔍 搜索框 */
        .search-box {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 14px 18px 14px 44px;
            width: 100%;
            color: white;
            font-size: 14px;
            font-weight: 400;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .search-box:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.15), 0 0 20px rgba(168, 85, 247, 0.2);
            background: rgba(0, 0, 0, 0.5);
        }
        
        .search-wrapper {
            position: relative;
        }
        .search-wrapper::before {
            content: '🔍';
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            pointer-events: none;
        }
        
        /* 📊 进度环 */
        .progress-ring-container {
            position: relative;
            width: 80px;
            height: 80px;
        }
        .progress-ring {
            transform: rotate(-90deg);
        }
        .progress-ring-bg {
            fill: none;
            stroke: rgba(255, 255, 255, 0.05);
            stroke-width: 6;
        }
        .progress-ring-fill {
            fill: none;
            stroke: url(#progressGradient);
            stroke-width: 6;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            font-weight: 700;
            color: white;
        }
        
        /* 🧭 导航项 */
        .nav-item {
            padding: 12px 16px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 12px;
            position: relative;
            font-size: 13px;
            font-weight: 450;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .nav-item:hover {
            background: rgba(168, 85, 247, 0.12);
            color: white;
            transform: translateX(4px);
        }
        
        .nav-item.completed {
            color: rgba(52, 211, 153, 0.9);
        }
        .nav-item.completed::after {
            content: '✓';
            position: absolute;
            right: 12px;
            color: var(--success);
            font-weight: 700;
            font-size: 12px;
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(244, 114, 182, 0.1) 100%);
            color: white;
            font-weight: 500;
        }
        .nav-item.active::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 60%;
            background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
            border-radius: 0 3px 3px 0;
        }
        
        /* 🏷️ 徽章 */
        .week-badge {
            font-size: 10px;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        
        .phase-tag {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.06);
            color: rgba(255, 255, 255, 0.5);
            font-weight: 500;
        }
        
        .duration-tag {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.35);
            font-weight: 400;
        }
        
        /* 📝 Markdown美化 */
        .markdown-body {
            background: transparent !important;
            color: #e2e8f0 !important;
            font-size: 15px;
            line-height: 1.8;
        }
        .markdown-body pre {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
        }
        .markdown-body code:not(pre code) {
            background: rgba(168, 85, 247, 0.15) !important;
            color: #e9d5ff !important;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 0.9em;
        }
        .markdown-body h1 {
            font-size: 2em;
            font-weight: 700;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding-bottom: 0.5em;
            margin-top: 1em;
        }
        .markdown-body h2 {
            font-size: 1.5em;
            font-weight: 600;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
            padding-bottom: 0.3em;
        }
        .markdown-body h3 { font-size: 1.25em; font-weight: 600; }
        .markdown-body a { 
            color: var(--primary-light) !important;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }
        .markdown-body a:hover {
            border-bottom-color: var(--primary-light);
        }
        .markdown-body blockquote {
            border-left: 4px solid var(--primary) !important;
            color: #cbd5e1 !important;
            background: rgba(168, 85, 247, 0.08);
            border-radius: 0 12px 12px 0;
            padding: 16px 20px;
            margin: 1em 0;
        }
        .markdown-body table {
            display: table;
            width: 100%;
        }
        .markdown-body table th {
            background: rgba(168, 85, 247, 0.1);
            font-weight: 600;
        }
        .markdown-body table th, .markdown-body table td {
            border-color: rgba(255, 255, 255, 0.08) !important;
            padding: 12px 16px;
        }
        .markdown-body table tr:hover {
            background: rgba(255, 255, 255, 0.02);
        }
        
        /* 📈 统计卡片 */
        .stat-card {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(244, 114, 182, 0.05) 100%);
            border: 1px solid rgba(168, 85, 247, 0.15);
            border-radius: 20px;
            padding: 24px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            transition: left 0.5s;
        }
        .stat-card:hover::before {
            left: 100%;
        }
        .stat-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 40px rgba(168, 85, 247, 0.2);
            border-color: rgba(168, 85, 247, 0.3);
        }
        
        /* 📅 周卡片 */
        .week-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 28px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .week-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        .week-card:hover::after {
            transform: scaleX(1);
        }
        .week-card:hover {
            transform: translateY(-6px);
            background: rgba(255, 255, 255, 0.04);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
            border-color: rgba(168, 85, 247, 0.2);
        }
        
        /* ⏳ 加载动画 */
        .loading {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 300px;
            gap: 16px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(168, 85, 247, 0.1);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .animate-slide-up {
            animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .animate-fade-in {
            animation: fadeIn 0.3s ease forwards;
        }
        
        /* 📜 滚动条 */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { 
            background: rgba(168, 85, 247, 0.4); 
            border-radius: 10px; 
        }
        ::-webkit-scrollbar-thumb:hover { 
            background: rgba(168, 85, 247, 0.6); 
        }
        
        /* 🏠 首页按钮 */
        .home-btn {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(244, 114, 182, 0.1) 100%);
            border: 1px solid rgba(168, 85, 247, 0.2);
            padding: 12px 18px;
            border-radius: 12px;
            color: white;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            font-weight: 500;
        }
        .home-btn:hover {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.25) 0%, rgba(244, 114, 182, 0.15) 100%);
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
        }
        
        /* 📱 响应式适配 */
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                padding: 20px;
                padding-top: 72px;
            }
            .main-content {
                padding: 16px;
                padding-top: 68px;
            }
            .hero-card {
                padding: 24px;
            }
            .hero-card h1 {
                font-size: 1.75rem;
                line-height: 2.2rem;
            }
            .hero-card p {
                font-size: 0.95rem;
            }
            .stat-card {
                padding: 16px;
            }
            .week-card {
                padding: 20px;
            }
        }
        
        @media (min-width: 769px) and (max-width: 1024px) {
            .sidebar {
                width: 300px;
            }
        }
        
        /* 🎉 Hero区域特效 */
        .hero-card {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.12) 0%, rgba(244, 114, 182, 0.08) 50%, rgba(34, 211, 238, 0.05) 100%);
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .hero-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
            animation: rotate 20s linear infinite;
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* 完成按钮 */
        .complete-btn {
            background: linear-gradient(135deg, rgba(52, 211, 153, 0.15), rgba(52, 211, 153, 0.08));
            border: 1px solid rgba(52, 211, 153, 0.3);
            color: var(--success);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .complete-btn:hover {
            background: linear-gradient(135deg, rgba(52, 211, 153, 0.25), rgba(52, 211, 153, 0.15));
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(52, 211, 153, 0.2);
        }
        /* 🧪 代码运行器 */
        .code-runner {
            margin: 16px 0;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(168, 85, 247, 0.2);
            background: rgba(0, 0, 0, 0.4);
        }
        .code-runner-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 14px;
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(244, 114, 182, 0.06));
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .code-runner-header .lang-tag {
            font-size: 11px;
            color: #c084fc;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .code-runner-actions {
            display: flex;
            gap: 6px;
        }
        .run-btn, .reset-btn {
            padding: 5px 14px;
            border-radius: 8px;
            border: none;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .run-btn {
            background: linear-gradient(135deg, #a855f7, #8b5cf6);
            color: white;
            box-shadow: 0 2px 10px rgba(168, 85, 247, 0.3);
        }
        .run-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(168, 85, 247, 0.45);
        }
        .run-btn.running {
            opacity: 0.7;
            pointer-events: none;
        }
        .run-btn.running::after {
            content: '';
            width: 12px;
            height: 12px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .reset-btn {
            background: rgba(255, 255, 255, 0.06);
            color: #9ca3af;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .reset-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        .code-editor-area {
            position: relative;
        }
        .code-editor-area textarea {
            width: 100%;
            min-height: 120px;
            max-height: 400px;
            padding: 16px;
            background: rgba(0, 0, 0, 0.5);
            color: #e2e8f0;
            border: none;
            outline: none;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
            line-height: 1.6;
            resize: vertical;
            tab-size: 4;
        }
        .code-output {
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.6);
            min-height: 40px;
            max-height: 300px;
            overflow-y: auto;
        }
        .code-output-label {
            font-size: 10px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .code-output pre {
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 12px;
            line-height: 1.5;
            color: #34d399;
            white-space: pre-wrap;
            word-break: break-all;
            margin: 0;
        }
        .code-output pre.error {
            color: #f87171;
        }
        .code-output .loading-msg {
            color: #c084fc;
            font-style: italic;
            font-size: 12px;
        }
        
        /* 🖥️ Playground */
        .playground-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .playground-editor {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(168, 85, 247, 0.25);
            background: rgba(0, 0, 0, 0.35);
        }
        .playground-editor textarea {
            width: 100%;
            min-height: 280px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            color: #e2e8f0;
            border: none;
            outline: none;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            tab-size: 4;
        }
        .playground-output {
            margin-top: 16px;
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            min-height: 80px;
        }
        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .template-btn {
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            color: #d1d5db;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.25s ease;
            text-align: left;
        }
        .template-btn:hover {
            background: rgba(168, 85, 247, 0.1);
            border-color: rgba(168, 85, 247, 0.3);
            color: white;
            transform: translateY(-1px);
        }
        .template-btn .tpl-icon {
            font-size: 16px;
            margin-bottom: 4px;
            display: block;
        }
        
        @media (max-width: 768px) {
            .template-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .playground-editor textarea {
                min-height: 200px;
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <!-- 🎨 动态背景 -->
    <div class="animated-bg"></div>
    <div class="glow-orb glow-orb-1"></div>
    <div class="glow-orb glow-orb-2"></div>
    <div class="glow-orb glow-orb-3"></div>
    
    <!-- SVG渐变定义 -->
    <svg width="0" height="0">
        <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#a855f7"/>
                <stop offset="100%" stop-color="#f472b6"/>
            </linearGradient>
        </defs>
    </svg>
    
    <!-- 🔀 侧边栏切换按钮 -->
    <button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" aria-label="切换侧边栏">
        <span class="icon-open">☰</span>
        <span class="icon-close">✕</span>
    </button>
    
    <!-- 侧边栏遮罩层 -->
    <div class="sidebar-backdrop" id="sidebar-backdrop" onclick="toggleSidebar()"></div>
    
    <div class="app-container">
        <!-- 侧边栏 -->
        <aside class="sidebar glass">
            <!-- 头部Logo -->
            <div class="mb-6">
                <h1 class="text-2xl font-bold gradient-text mb-1">🚀 AI工程师训练营</h1>
                <p class="text-gray-500 text-xs font-medium">12周从入门到精通 · 2026版</p>
            </div>
            
            <!-- 进度概览 - 环形进度 -->
            <div id="progress-overview" class="glass-card p-5 mb-5">
                <div class="flex items-center gap-4">
                    <div class="progress-ring-container">
                        <svg class="progress-ring" width="80" height="80">
                            <circle class="progress-ring-bg" cx="40" cy="40" r="34"/>
                            <circle id="progress-ring-fill" class="progress-ring-fill" cx="40" cy="40" r="34" 
                                stroke-dasharray="213.6" stroke-dashoffset="213.6"/>
                        </svg>
                        <span id="progress-percent" class="progress-text">0%</span>
                    </div>
                    <div>
                        <div class="text-sm font-semibold text-white mb-1">学习进度</div>
                        <div id="completed-count" class="text-xs text-gray-400">0 / 0 已完成</div>
                    </div>
                </div>
            </div>
            
            <!-- 搜索框 -->
            <div class="search-wrapper mb-5">
                <input type="text" id="search-input" class="search-box" placeholder="搜索教程、项目...">
            </div>
            
            <!-- 返回首页按钮 -->
            <button class="home-btn mb-5 w-full justify-center" onclick="goHome()">
                <span>🏠</span>
                <span>返回首页概览</span>
            </button>
            
            <!-- 🧪 代码实验室 -->
            <button class="home-btn mb-3 w-full justify-center" onclick="openPlayground()" style="background: linear-gradient(135deg, rgba(34,211,238,0.1), rgba(168,85,247,0.1)); border-color: rgba(34,211,238,0.2);">
                <span>🧪</span>
                <span>代码实验室</span>
            </button>
            
            <!-- 导航菜单 -->
            <nav id="nav-container" class="flex-1 overflow-y-auto pr-1"></nav>
            
            <!-- 底部 -->
            <div class="mt-4 pt-4 border-t border-white/5">
                <a href="https://github.com/falses00/-AI-2026-" target="_blank" 
                   class="flex items-center justify-center gap-2 text-gray-500 hover:text-purple-400 transition-colors text-sm py-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                    <span>GitHub</span>
                </a>
            </div>
        </aside>
        
        <!-- 主内容区 -->
        <main class="main-content">
            <div id="content-container" class="max-w-5xl mx-auto"></div>
        </main>
    </div>
    
    <script>
        // ============================================================
        // 🔧 Engineer Agent (Atlas) 开发的核心逻辑
        // ============================================================
        
        let curriculum = {};
        let currentPath = null;
        let allItems = [];
        
        // 进度管理
        const ProgressManager = {
            KEY: 'ai_training_progress',
            
            getProgress() {
                const data = localStorage.getItem(this.KEY);
                return data ? JSON.parse(data) : { completed: [], lastVisited: null };
            },
            
            saveProgress(progress) {
                localStorage.setItem(this.KEY, JSON.stringify(progress));
            },
            
            markCompleted(path) {
                const progress = this.getProgress();
                if (!progress.completed.includes(path)) {
                    progress.completed.push(path);
                    this.saveProgress(progress);
                }
                this.updateUI();
            },
            
            isCompleted(path) {
                return this.getProgress().completed.includes(path);
            },
            
            setLastVisited(path) {
                const progress = this.getProgress();
                progress.lastVisited = path;
                this.saveProgress(progress);
            },
            
            getCompletionRate() {
                const progress = this.getProgress();
                const total = allItems.length || 1;
                return Math.round((progress.completed.length / total) * 100);
            },
            
            updateUI() {
                const progress = this.getProgress();
                const total = allItems.length;
                const completed = progress.completed.length;
                const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
                
                // 更新进度文字
                document.getElementById('progress-percent').textContent = percent + '%';
                document.getElementById('completed-count').textContent = completed + ' / ' + total + ' 已完成';
                
                // 更新环形进度条 (圆周 = 2 * π * r = 2 * 3.14159 * 34 ≈ 213.6)
                const circumference = 213.6;
                const offset = circumference - (percent / 100) * circumference;
                const ringFill = document.getElementById('progress-ring-fill');
                if (ringFill) {
                    ringFill.style.strokeDashoffset = offset;
                }
                
                // 更新导航项的完成状态
                document.querySelectorAll('.nav-item').forEach(item => {
                    if (progress.completed.includes(item.dataset.path)) {
                        item.classList.add('completed');
                    }
                });
            }
        };
        
        // 搜索功能（改进版：保留Week上下文）
        const SearchManager = {
            search(query) {
                query = query.toLowerCase().trim();
                if (!query) {
                    this.clearHighlight();
                    return;
                }
                
                // 获取所有Week容器
                document.querySelectorAll('#nav-container > div').forEach(weekContainer => {
                    let hasMatch = false;
                    const navItems = weekContainer.querySelectorAll('.nav-item');
                    
                    navItems.forEach(item => {
                        const text = item.textContent.toLowerCase();
                        if (text.includes(query)) {
                            item.style.display = 'flex';
                            item.style.background = 'rgba(139, 92, 246, 0.15)';
                            hasMatch = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });
                    
                    // 如果有匹配项，显示Week标题；否则隐藏整个容器
                    weekContainer.style.display = hasMatch ? 'block' : 'none';
                });
            },
            
            clearHighlight() {
                document.querySelectorAll('#nav-container > div').forEach(weekContainer => {
                    weekContainer.style.display = 'block';
                    weekContainer.querySelectorAll('.nav-item').forEach(item => {
                        item.style.display = 'flex';
                        item.style.background = '';
                    });
                });
            }
        };
        
        // 移动端菜单切换
        function toggleMobileMenu() {
            const sidebar = document.querySelector('.sidebar');
            const btn = document.querySelector('.mobile-menu-btn');
            sidebar.classList.toggle('active');
            btn.textContent = sidebar.classList.contains('active') ? '✕' : '☰';
        }
        
        // 返回首页
        function goHome() {
            renderHome();
            // 关闭移动端菜单
            const sidebar = document.querySelector('.sidebar');
            const btn = document.querySelector('.mobile-menu-btn');
            sidebar.classList.remove('active');
            if (btn) btn.textContent = '☰';
        }
        
        // 键盘导航支持
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                goHome();
            }
        });
        
        // 初始化
        async function init() {
            try {
                const res = await fetch('/api/curriculum');
                curriculum = await res.json();
                
                // 收集所有项目
                for (const week of Object.values(curriculum)) {
                    allItems.push(...week.tutorials.map(t => t.path));
                    allItems.push(...week.projects.map(p => p.path));
                    allItems.push(...week.exercises.map(e => e.path));
                }
                
                renderNav();
                renderHome();
                ProgressManager.updateUI();
                
                // 搜索事件
                document.getElementById('search-input').addEventListener('input', (e) => {
                    SearchManager.search(e.target.value);
                });
            } catch (e) {
                console.error('初始化失败:', e);
            }
        }
        
        // 渲染导航
        function renderNav() {
            const container = document.getElementById('nav-container');
            let html = '';
            
            for (const [weekId, week] of Object.entries(curriculum)) {
                const weekNum = weekId.replace('week', '');
                // 检查是否应该展开
                const isExpanded = localStorage.getItem(`week_expanded_${weekId}`) === 'true';
                const displayStyle = isExpanded ? 'block' : 'none';
                const arrowTransform = isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
                
                html += `
                    <div class="mb-2 border border-white/5 rounded-xl overflow-hidden bg-white/5">
                        <div class="flex items-center justify-between p-3 cursor-pointer hover:bg-white/5 transition-colors" 
                             onclick="toggleWeek('${weekId}')">
                            <div class="flex items-center gap-3">
                                <div class="text-xl">${week.icon}</div>
                                <div>
                                    <div class="flex items-center gap-2 mb-1">
                                        <span class="text-sm font-bold text-gray-200">${week.title}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="week-badge text-[10px] py-0.5 px-1.5" style="background: ${week.color}">${weekNum}</span>
                                        <span class="text-[10px] text-gray-400">${week.tutorials.length + week.projects.length} 任务</span>
                                    </div>
                                </div>
                            </div>
                            <svg id="week-arrow-${weekId}" class="w-4 h-4 text-gray-400 transition-transform duration-300" style="transform: ${arrowTransform}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </div>
                        
                        <div id="week-content-${weekId}" style="display: ${displayStyle}" class="border-t border-white/5 bg-black/20">
                            <div class="space-y-1 p-2">
                `;
                
                // 教程
                for (const item of week.tutorials) {
                    const completed = ProgressManager.isCompleted(item.path) ? 'completed' : '';
                    html += `
                        <div class="nav-item glass-hover text-gray-300 text-sm ${completed}" 
                             data-path="${item.path}" onclick="event.stopPropagation(); loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span class="flex-1 truncate">${item.name}</span>
                        </div>
                    `;
                }
                
                // 项目
                for (const item of week.projects) {
                    const completed = ProgressManager.isCompleted(item.path) ? 'completed' : '';
                    html += `
                        <div class="nav-item glass-hover text-green-400 text-sm ${completed}" 
                             data-path="${item.path}" onclick="event.stopPropagation(); loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span class="flex-1 truncate">${item.name}</span>
                            <span class="text-xs bg-green-500/20 px-2 py-0.5 rounded">项目</span>
                        </div>
                    `;
                }
                
                // 练习
                for (const item of week.exercises) {
                    const completed = ProgressManager.isCompleted(item.path) ? 'completed' : '';
                    html += `
                        <div class="nav-item glass-hover text-yellow-400 text-sm ${completed}" 
                             data-path="${item.path}" onclick="event.stopPropagation(); loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span class="flex-1 truncate">${item.name}</span>
                            <span class="text-xs bg-yellow-500/20 px-2 py-0.5 rounded">练习</span>
                        </div>
                    `;
                }
                
                html += '</div></div></div>';
            }
            
            container.innerHTML = html;
        }
        
        // 渲染首页
        async function renderHome() {
            const container = document.getElementById('content-container');
            
            // 获取统计数据
            let stats = { weeks: 12, tutorials: 30, projects: 12, exercises: 6, estimated_hours: 150 };
            try {
                const res = await fetch('/api/stats');
                stats = await res.json();
            } catch (e) {}
            
            const completionRate = ProgressManager.getCompletionRate();
            
            container.innerHTML = `
                <div class="animate-slide-up">
                    <!-- Hero区域 -->
                    <div class="hero-card mb-10 relative z-10">
                        <h1 class="text-5xl font-extrabold gradient-text mb-4">🚀 AI工程师2026速成训练营</h1>
                        <p class="text-xl text-gray-300 mb-3 font-light">12周从"调API"到"智能体开发"</p>
                        <div class="flex items-center justify-center gap-4 flex-wrap">
                            <span class="px-4 py-2 rounded-full bg-purple-500/20 text-purple-300 text-sm font-medium">MCP协议</span>
                            <span class="px-4 py-2 rounded-full bg-pink-500/20 text-pink-300 text-sm font-medium">RAG系统</span>
                            <span class="px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-300 text-sm font-medium">Agentic Workflows</span>
                        </div>
                    </div>
                    
                    <!-- 统计卡片 -->
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
                        <div class="stat-card group">
                            <div class="text-4xl mb-3 transform group-hover:scale-110 transition-transform">📚</div>
                            <div class="text-3xl font-bold gradient-text-subtle mb-1">${stats.weeks}</div>
                            <div class="text-gray-400 text-sm font-medium">周课程</div>
                        </div>
                        <div class="stat-card group">
                            <div class="text-4xl mb-3 transform group-hover:scale-110 transition-transform">📖</div>
                            <div class="text-3xl font-bold text-blue-400 mb-1">${stats.tutorials}</div>
                            <div class="text-gray-400 text-sm font-medium">教程</div>
                        </div>
                        <div class="stat-card group">
                            <div class="text-4xl mb-3 transform group-hover:scale-110 transition-transform">🚀</div>
                            <div class="text-3xl font-bold text-emerald-400 mb-1">${stats.projects}</div>
                            <div class="text-gray-400 text-sm font-medium">实战项目</div>
                        </div>
                        <div class="stat-card group">
                            <div class="text-4xl mb-3 transform group-hover:scale-110 transition-transform">⏱️</div>
                            <div class="text-3xl font-bold text-pink-400 mb-1">${stats.estimated_hours}h</div>
                            <div class="text-gray-400 text-sm font-medium">预计时长</div>
                        </div>
                    </div>
                    
                    <!-- 课程大纲标题 -->
                    <div class="flex items-center gap-3 mb-6">
                        <h2 class="text-2xl font-bold text-white">📋 课程大纲</h2>
                        <div class="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-transparent"></div>
                    </div>
                    
                    <!-- 周卡片网格 -->
                    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 mb-10 pb-10">
                        ${Object.entries(curriculum).map(([id, week], index) => `
                            <div class="week-card neon-border" onclick="scrollToWeek('${id}')" style="animation-delay: ${index * 50}ms">
                                <div class="flex items-center gap-4 mb-4">
                                    <div class="text-4xl">${week.icon}</div>
                                    <div>
                                        <span class="week-badge text-white" style="background: ${week.color}">${id.toUpperCase()}</span>
                                        <span class="phase-tag ml-2">${week.phase || ''}</span>
                                    </div>
                                </div>
                                <h3 class="font-bold text-lg mb-3 text-white">${week.title}</h3>
                                <div class="flex items-center gap-4 text-sm">
                                    <span class="text-gray-400"><span class="text-purple-400 font-semibold">${week.tutorials.length}</span> 教程</span>
                                    <span class="text-gray-400"><span class="text-emerald-400 font-semibold">${week.projects.length}</span> 项目</span>
                                    <span class="text-gray-400"><span class="text-amber-400 font-semibold">${week.exercises.length}</span> 练习</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <!-- 快速开始 -->
                    <div class="glass-card p-8">
                        <h2 class="text-xl font-bold mb-6 gradient-text">✨ 快速开始</h2>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="flex items-start gap-4 p-5 rounded-2xl bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/10 hover:border-purple-500/30 transition-colors">
                                <span class="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 text-white flex items-center justify-center font-bold text-lg shadow-lg shadow-purple-500/30">1</span>
                                <div>
                                    <h4 class="font-semibold text-white mb-1">选择教程</h4>
                                    <p class="text-sm text-gray-400">从左侧导航选择感兴趣的教程开始学习</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-4 p-5 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/10 hover:border-emerald-500/30 transition-colors">
                                <span class="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 text-white flex items-center justify-center font-bold text-lg shadow-lg shadow-emerald-500/30">2</span>
                                <div>
                                    <h4 class="font-semibold text-white mb-1">完成项目</h4>
                                    <p class="text-sm text-gray-400">每周都有实战项目帮助巩固所学知识</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-4 p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 to-amber-500/5 border border-amber-500/10 hover:border-amber-500/30 transition-colors">
                                <span class="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 text-white flex items-center justify-center font-bold text-lg shadow-lg shadow-amber-500/30">3</span>
                                <div>
                                    <h4 class="font-semibold text-white mb-1">追踪进度</h4>
                                    <p class="text-sm text-gray-400">完成后标记进度，查看学习成果</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 加载内容
        async function loadContent(path) {
            const container = document.getElementById('content-container');
            container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            
            // 更新导航激活状态
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.path === path) {
                    item.classList.add('active');
                }
            });
            
            try {
                const res = await fetch(`/api/content?path=${encodeURIComponent(path)}`);
                const data = await res.json();
                
                if (data.type === 'python') {
                    const escaped = data.content
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;');
                    container.innerHTML = `
                        <div class="glass rounded-xl p-6 animate-slide-in">
                            <div class="flex items-center justify-between mb-4">
                                <h2 class="text-xl font-bold text-gray-200">📄 ${path.split('/').pop()}</h2>
                                <div class="flex items-center gap-3">
                                    <span class="text-xs text-gray-500 bg-gray-700/50 px-2 py-1 rounded">Python</span>
                                    <button onclick="markAsCompleted('${path}')" class="text-xs bg-green-500/20 text-green-400 px-3 py-1 rounded hover:bg-green-500/30 transition">
                                        ✓ 标记完成
                                    </button>
                                </div>
                            </div>
                            <pre class="rounded-lg overflow-auto"><code class="language-python hljs">${escaped}</code></pre>
                        </div>
                    `;
                    hljs.highlightAll();
                } else {
                    container.innerHTML = `
                        <div class="glass rounded-xl p-8 markdown-body animate-slide-in">
                            <div class="flex justify-end mb-4">
                                <button onclick="markAsCompleted('${path}')" class="text-sm bg-green-500/20 text-green-400 px-4 py-2 rounded-lg hover:bg-green-500/30 transition flex items-center gap-2">
                                    <span>✓</span> 标记完成
                                </button>
                            </div>
                            ${marked.parse(data.content)}
                        </div>
                    `;
                    container.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
                
                // 👉 添加“下一步”导航
                const currentIndex = allItems.findIndex(item => item.path === path);
                const prevItem = currentIndex > 0 ? allItems[currentIndex - 1] : null;
                const nextItem = currentIndex >= 0 && currentIndex < allItems.length - 1 ? allItems[currentIndex + 1] : null;
                
                let navHtml = '<div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;">';
                
                if (prevItem) {
                    navHtml += `
                        <button onclick="loadContent('${prevItem.path}')" 
                            style="flex: 1; min-width: 200px; display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03); cursor: pointer; color: white; text-align: left; transition: all 0.3s ease;" 
                            onmouseover="this.style.background='rgba(168,85,247,0.1)'; this.style.borderColor='rgba(168,85,247,0.3)'; this.style.transform='translateY(-2px)';" 
                            onmouseout="this.style.background='rgba(255,255,255,0.03)'; this.style.borderColor='rgba(255,255,255,0.08)'; this.style.transform='translateY(0)';">
                            <span style="font-size: 20px;">⬅</span>
                            <div>
                                <div style="font-size: 11px; color: #9ca3af; margin-bottom: 4px;">上一节</div>
                                <div style="font-size: 14px; font-weight: 600;">${prevItem.icon} ${prevItem.name}</div>
                            </div>
                        </button>
                    `;
                } else {
                    navHtml += '<div></div>';
                }
                
                if (nextItem) {
                    navHtml += `
                        <button onclick="loadContent('${nextItem.path}')" 
                            style="flex: 1; min-width: 200px; display: flex; align-items: center; justify-content: flex-end; gap: 12px; padding: 16px 20px; border-radius: 14px; border: 1px solid rgba(168,85,247,0.2); background: linear-gradient(135deg, rgba(168,85,247,0.08), rgba(244,114,182,0.05)); cursor: pointer; color: white; text-align: right; transition: all 0.3s ease;" 
                            onmouseover="this.style.background='linear-gradient(135deg, rgba(168,85,247,0.18), rgba(244,114,182,0.12))'; this.style.borderColor='rgba(168,85,247,0.4)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 20px rgba(168,85,247,0.2)';" 
                            onmouseout="this.style.background='linear-gradient(135deg, rgba(168,85,247,0.08), rgba(244,114,182,0.05))'; this.style.borderColor='rgba(168,85,247,0.2)'; this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                            <div>
                                <div style="font-size: 11px; color: #c084fc; margin-bottom: 4px;">下一步 →</div>
                                <div style="font-size: 14px; font-weight: 600;">${nextItem.icon} ${nextItem.name}</div>
                            </div>
                            <span style="font-size: 20px;">➡</span>
                        </button>
                    `;
                }
                
                navHtml += '</div>';
                container.innerHTML += navHtml;
                
                currentPath = path;
                ProgressManager.setLastVisited(path);
                window.scrollTo(0, 0);
            } catch (e) {
                container.innerHTML = `
                    <div class="glass rounded-xl p-8 text-center animate-slide-in">
                        <div class="text-6xl mb-4">😢</div>
                        <h2 class="text-xl font-bold text-red-400 mb-2">加载失败</h2>
                        <p class="text-gray-400 mb-4">${e.message || '请检查文件是否存在'}</p>
                        <button onclick="renderHome()" class="px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors">
                            返回首页
                        </button>
                    </div>
                `;
            }
        }
        
        // 标记完成
        function markAsCompleted(path) {
            ProgressManager.markCompleted(path);
            // 更新当前页面的按钮状态
            const btn = document.querySelector(`[onclick="markAsCompleted('${path}')"]`);
            if (btn) {
                btn.innerHTML = '✓ 已完成';
                btn.classList.remove('bg-green-500/20', 'text-green-400');
                btn.classList.add('bg-gray-500/20', 'text-gray-400');
            }
        }
        
        function scrollToWeek(weekId) {
            // 展开对应的周
            toggleWeek(weekId, true);
            
            const week = curriculum[weekId];
            if (week && week.tutorials.length > 0) {
                loadContent(week.tutorials[0].path);
            } else if (week && week.projects.length > 0) {
                loadContent(week.projects[0].path);
            }
        }
        
        // 切换周折叠状态
        function toggleWeek(weekId, forceOpen = false) {
            const content = document.getElementById(`week-content-${weekId}`);
            const arrow = document.getElementById(`week-arrow-${weekId}`);
            
            if (!content) return;
            
            const isClosed = content.style.display === 'none';
            
            if (forceOpen || isClosed) {
                content.style.display = 'block';
                if (arrow) arrow.style.transform = 'rotate(180deg)';
                // 保存状态
                localStorage.setItem(`week_expanded_${weekId}`, 'true');
            } else {
                content.style.display = 'none';
                if (arrow) arrow.style.transform = 'rotate(0deg)';
                localStorage.removeItem(`week_expanded_${weekId}`);
            }
        }
        
        // 🔀 侧边栏切换
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            const toggleBtn = document.getElementById('sidebar-toggle');
            
            const isOpen = sidebar.classList.contains('open');
            
            if (isOpen) {
                sidebar.classList.remove('open');
                backdrop.classList.remove('visible');
                toggleBtn.classList.remove('active');
            } else {
                sidebar.classList.add('open');
                backdrop.classList.add('visible');
                toggleBtn.classList.add('active');
            }
        }
        
        // 点击导航项后自动关闭侧边栏
        const origLoadContent = loadContent;
        loadContent = async function(path) {
            await origLoadContent(path);
            // 自动关闭侧边栏
            const sidebar = document.querySelector('.sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            const toggleBtn = document.getElementById('sidebar-toggle');
            if (sidebar) sidebar.classList.remove('open');
            if (backdrop) backdrop.classList.remove('visible');
            if (toggleBtn) toggleBtn.classList.remove('active');
        };
        
        // ESC键关闭侧边栏
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar && sidebar.classList.contains('open')) {
                    toggleSidebar();
                }
            }
        });
        
        // ============================================================
        // 🧪 Pyodide 代码运行器 (Developer Agent)
        // ============================================================
        
        const PyodideManager = {
            instance: null,
            loading: false,
            loadPromise: null,
            
            async init() {
                if (this.instance) return this.instance;
                if (this.loadPromise) return this.loadPromise;
                
                this.loading = true;
                this.loadPromise = new Promise(async (resolve, reject) => {
                    try {
                        // 动态加载 Pyodide CDN
                        if (!window.loadPyodide) {
                            const script = document.createElement('script');
                            script.src = 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js';
                            script.onload = async () => {
                                this.instance = await loadPyodide({
                                    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/'
                                });
                                this.loading = false;
                                resolve(this.instance);
                            };
                            script.onerror = () => {
                                this.loading = false;
                                reject(new Error('Pyodide CDN 加载失败'));
                            };
                            document.head.appendChild(script);
                        } else {
                            this.instance = await loadPyodide({
                                indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.0/full/'
                            });
                            this.loading = false;
                            resolve(this.instance);
                        }
                    } catch (e) {
                        this.loading = false;
                        reject(e);
                    }
                });
                return this.loadPromise;
            },
            
            async runCode(code, outputEl) {
                outputEl.innerHTML = '<span class="loading-msg">⚙️ 初始化 Python 环境...</span>';
                
                try {
                    const pyodide = await this.init();
                    outputEl.innerHTML = '<span class="loading-msg">📦 检测并加载依赖包...</span>';
                    
                    // 自动检测并加载包
                    try {
                        await pyodide.loadPackagesFromImports(code);
                    } catch(e) { /* 忽略包加载错误 */ }
                    
                    outputEl.innerHTML = '<span class="loading-msg">▶ 执行中...</span>';
                    
                    // 捕获 stdout/stderr
                    let stdout = [];
                    let stderr = [];
                    pyodide.setStdout({ batched: (msg) => stdout.push(msg) });
                    pyodide.setStderr({ batched: (msg) => stderr.push(msg) });
                    
                    // 执行代码
                    let result;
                    try {
                        result = await pyodide.runPythonAsync(code);
                    } catch (pyErr) {
                        stderr.push(pyErr.message);
                    }
                    
                    // 显示输出
                    let output = '';
                    if (stdout.length > 0) {
                        output += stdout.join('\n');
                    }
                    if (result !== undefined && result !== null && result.toString() !== 'undefined') {
                        if (output) output += '\n';
                        output += '>>> ' + result.toString();
                    }
                    if (stderr.length > 0) {
                        outputEl.innerHTML = `<pre class="error">${stderr.join('\n')}</pre>` + 
                            (output ? `<pre>${output}</pre>` : '');
                    } else if (output) {
                        outputEl.innerHTML = `<pre>${output}</pre>`;
                    } else {
                        outputEl.innerHTML = '<pre style="color:#6b7280;">✓ 执行完成（无输出）</pre>';
                    }
                } catch (e) {
                    outputEl.innerHTML = `<pre class="error">❌ ${e.message}</pre>`;
                }
            }
        };
        
        // 代码模板库
        const CODE_TEMPLATES = [
            { name: 'Hello World', icon: '👋', code: 'print("Hello, AI 工程师!")\nprint("欢迎来到 2026 训练营")' },
            { name: '列表推导式', icon: '📝', code: '# 列表推导式\nsquares = [x**2 for x in range(10)]\nprint(f"平方数: {squares}")\n\n# 带条件\nevens = [x for x in range(20) if x % 2 == 0]\nprint(f"偶数: {evens}")' },
            { name: '字典操作', icon: '📖', code: '# 字典推导式\nstudent = {"name": "小明", "age": 22, "课程": ["AI", "Python"]}\n\nfor key, value in student.items():\n    print(f"{key}: {value}")\n\n# 字典合并\nscores = {**student, "成绩": 95}\nprint(f"\n完整信息: {scores}")' },
            { name: 'NumPy 基础', icon: '📊', code: 'import numpy as np\n\narr = np.array([1, 2, 3, 4, 5])\nprint(f"数组: {arr}")\nprint(f"均值: {arr.mean()}")\nprint(f"标准差: {arr.std():.2f}")\n\nmatrix = np.random.rand(3, 3)\nprint(f"\n随机矩阵:\n{matrix.round(2)}")' },
            { name: '异步基础', icon: '⚡', code: 'import asyncio\n\nasync def greet(name, delay):\n    await asyncio.sleep(delay)\n    return f"Hello, {name}!"\n\nasync def main():\n    results = await asyncio.gather(\n        greet("AI", 0.1),\n        greet("Python", 0.2),\n        greet("世界", 0.15)\n    )\n    for r in results:\n        print(r)\n\nawait main()' },
            { name: '数据处理', icon: '🔧', code: '# JSON 数据处理\nimport json\n\ndata = {\n    "users": [\n        {"name": "Alice", "score": 95},\n        {"name": "Bob", "score": 87},\n        {"name": "Charlie", "score": 92}\n    ]\n}\n\n# 排序和过滤\ntop = sorted(data["users"], key=lambda x: x["score"], reverse=True)\nprint("排名:")\nfor i, u in enumerate(top, 1):\n    print(f"  {i}. {u[\"name\"]} - {u[\"score\"]}分")' },
            { name: '装饰器', icon: '🎭', code: 'import functools\nimport time\n\ndef timer(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        elapsed = time.time() - start\n        print(f"{func.__name__} 耗时: {elapsed:.4f}s")\n        return result\n    return wrapper\n\n@timer\ndef compute():\n    return sum(i**2 for i in range(100000))\n\nresult = compute()\nprint(f"结果: {result}")' },
            { name: '类与继承', icon: '🏛️', code: 'from dataclasses import dataclass\n\n@dataclass\nclass Agent:\n    name: str\n    role: str\n    skills: list\n    \n    def introduce(self):\n        return f"I am {self.name}, a {self.role}"\n\nclass AIAgent(Agent):\n    def think(self, task):\n        return f"{self.name} is analyzing: {task}"\n\nagent = AIAgent("Atlas", "Engineer", ["Python", "ML"])\nprint(agent.introduce())\nprint(agent.think("设计系统架构"))\nprint(f"技能: {\", \".join(agent.skills)}")' }
        ];
        
        // 渲染 Playground 页面
        function renderPlayground() {
            const container = document.getElementById('content-container');
            container.innerHTML = `
                <div class="playground-container animate-slide-in">
                    <div class="glass-card p-8 mb-6">
                        <h1 class="text-2xl font-bold gradient-text mb-2">🧪 代码实验室</h1>
                        <p class="text-gray-400 text-sm">直接在浏览器中运行 Python 代码，无需安装任何环境 • 基于 Pyodide (WebAssembly)</p>
                    </div>
                    
                    <div class="glass-card p-6 mb-6">
                        <h3 class="text-sm font-semibold text-gray-300 mb-3">📌 快速模板</h3>
                        <div class="template-grid">
                            ${CODE_TEMPLATES.map((t, i) => `
                                <button class="template-btn" onclick="loadTemplate(${i})">
                                    <span class="tpl-icon">${t.icon}</span>
                                    ${t.name}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="playground-editor">
                        <div class="code-runner-header">
                            <span class="lang-tag">🐍 Python</span>
                            <div class="code-runner-actions">
                                <button class="reset-btn" onclick="document.getElementById('pg-editor').value = '# 在这里输入你的 Python 代码...\\nprint(\'Hello World!\')'">↺ 重置</button>
                                <button class="run-btn" id="pg-run-btn" onclick="runPlayground()">▶ 运行</button>
                            </div>
                        </div>
                        <textarea id="pg-editor" spellcheck="false" placeholder="# 在这里输入你的 Python 代码...\nprint('Hello World!')">print("Hello, AI 工程师! 🚀")\nprint("欢迎来到 2026 训练营代码实验室")</textarea>
                    </div>
                    
                    <div class="playground-output">
                        <div class="code-output-label">💻 输出</div>
                        <div id="pg-output"><pre style="color:#6b7280;">点击 ▶ 运行 按钮执行代码</pre></div>
                    </div>
                </div>
            `;
            
            currentPath = null;
            // Tab键支持
            const editor = document.getElementById('pg-editor');
            editor.addEventListener('keydown', handleTabKey);
        }
        
        function loadTemplate(index) {
            const editor = document.getElementById('pg-editor');
            if (editor) {
                editor.value = CODE_TEMPLATES[index].code;
            }
        }
        
        async function runPlayground() {
            const code = document.getElementById('pg-editor').value;
            const outputEl = document.getElementById('pg-output');
            const btn = document.getElementById('pg-run-btn');
            btn.classList.add('running');
            btn.innerHTML = '运行中';
            await PyodideManager.runCode(code, outputEl);
            btn.classList.remove('running');
            btn.innerHTML = '▶ 运行';
        }
        
        function openPlayground() {
            renderPlayground();
            // 关闭侧边栏
            const sidebar = document.querySelector('.sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            const toggleBtn = document.getElementById('sidebar-toggle');
            if (sidebar) sidebar.classList.remove('open');
            if (backdrop) backdrop.classList.remove('visible');
            if (toggleBtn) toggleBtn.classList.remove('active');
            window.scrollTo(0, 0);
        }
        
        // Tab键处理
        function handleTabKey(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = e.target.selectionStart;
                const end = e.target.selectionEnd;
                e.target.value = e.target.value.substring(0, start) + '    ' + e.target.value.substring(end);
                e.target.selectionStart = e.target.selectionEnd = start + 4;
            }
        }
        
        // 增强教程中的 Python 代码块
        function enhanceCodeBlocks(container) {
            const codeBlocks = container.querySelectorAll('pre code.language-python, pre code.hljs.language-python');
            let blockId = 0;
            
            codeBlocks.forEach(codeEl => {
                const pre = codeEl.parentElement;
                const originalCode = codeEl.textContent;
                const id = 'cr-' + (blockId++);
                
                const runner = document.createElement('div');
                runner.className = 'code-runner';
                runner.innerHTML = `
                    <div class="code-runner-header">
                        <span class="lang-tag">🐍 Python · 可运行</span>
                        <div class="code-runner-actions">
                            <button class="reset-btn" onclick="document.getElementById('${id}').value = decodeURIComponent(this.dataset.original)" data-original="${encodeURIComponent(originalCode)}">↺ 重置</button>
                            <button class="run-btn" onclick="runInlineCode('${id}', this)">▶ 运行</button>
                        </div>
                    </div>
                    <div class="code-editor-area">
                        <textarea id="${id}" spellcheck="false">${originalCode}</textarea>
                    </div>
                    <div class="code-output" id="${id}-output">
                        <div class="code-output-label">输出</div>
                        <pre style="color:#6b7280;">点击 ▶ 运行</pre>
                    </div>
                `;
                
                pre.replaceWith(runner);
                
                // Tab键支持
                document.getElementById(id).addEventListener('keydown', handleTabKey);
            });
        }
        
        async function runInlineCode(id, btn) {
            const code = document.getElementById(id).value;
            const outputEl = document.getElementById(id + '-output');
            btn.classList.add('running');
            btn.textContent = '运行中';
            await PyodideManager.runCode(code, outputEl);
            btn.classList.remove('running');
            btn.innerHTML = '▶ 运行';
        }
        
        // 劫持 loadContent 添加代码块增强
        const _origLoadContent2 = loadContent;
        loadContent = async function(path) {
            await _origLoadContent2(path);
            // 增强 Python 代码块
            const container = document.getElementById('content-container');
            if (container) {
                enhanceCodeBlocks(container);
            }
        };
        
        // 启动应用
        init();
    </script>
</body>
</html>'''


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
