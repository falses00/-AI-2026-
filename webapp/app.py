"""
🚀 AI工程师训练营 - 专业Web展示界面
作者：资深Web开发工程师

特点：
- 响应式设计
- 玻璃态UI风格
- Markdown渲染
- 文件内容动态加载

运行：
    cd "i:\Study FastAPI"
    D:\Anaconda\envs\pytorch_Gpu\python.exe -m uvicorn webapp.app:app --reload --port 8080
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import os

app = FastAPI(
    title="AI工程师2026速成训练营",
    version="2.0.0"
)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 课程数据
CURRICULUM = {
    "week1": {
        "title": "Python高级特性 + AI工程环境",
        "icon": "🔧",
        "color": "#3b82f6",
        "tutorials": [
            {"name": "异步编程核心概念", "path": "week1/tutorials/01_async_basics.md", "icon": "⚡"},
            {"name": "Pydantic数据验证", "path": "week1/tutorials/04_pydantic_basics.md", "icon": "✅"},
            {"name": "FastAPI快速入门", "path": "week1/tutorials/05_fastapi_quickstart.md", "icon": "🚀"},
            {"name": "Docker基础入门", "path": "week1/tutorials/07_docker_basics.md", "icon": "🐳"},
        ],
        "projects": [
            {"name": "图书管理API", "path": "week1/projects/project1_structured_api/README.md", "icon": "📚"},
        ],
        "exercises": [
            {"name": "异步编程练习", "path": "week1/exercises/async_exercises.py", "icon": "💻"},
        ]
    },
    "week2": {
        "title": "大模型API深度控制",
        "icon": "🤖",
        "color": "#8b5cf6",
        "tutorials": [
            {"name": "DeepSeek API快速入门", "path": "week2/tutorials/01_openai_api_basics.md", "icon": "🔌"},
            {"name": "结构化输出详解", "path": "week2/tutorials/02_structured_output.md", "icon": "📊"},
            {"name": "Response Format深度解析", "path": "week2/tutorials/03_response_format.md", "icon": "📋"},
            {"name": "Function Calling详解", "path": "week2/tutorials/04_function_calling_intro.md", "icon": "🔧"},
            {"name": "Streaming流式响应", "path": "week2/tutorials/05_streaming.md", "icon": "📡"},
            {"name": "Token计算与成本优化", "path": "week2/tutorials/06_token_optimization.md", "icon": "💰"},
        ],
        "projects": [],
        "exercises": [
            {"name": "API调用练习", "path": "week2/exercises/api_exercises.py", "icon": "💻"},
        ]
    },
    "week3": {
        "title": "MCP协议深度剖析",
        "icon": "🔌",
        "color": "#ec4899",
        "tutorials": [
            {"name": "MCP协议入门", "path": "week3/tutorials/01_mcp_introduction.md", "icon": "📖"},
            {"name": "FastMCP基础教程", "path": "week3/tutorials/02_fastmcp_basics.md", "icon": "⚡"},
            {"name": "MCP Tools开发指南", "path": "week3/tutorials/03_mcp_tools.md", "icon": "🔧"},
            {"name": "MCP Resources开发指南", "path": "week3/tutorials/04_mcp_resources.md", "icon": "📦"},
            {"name": "Claude Desktop集成", "path": "week3/tutorials/05_claude_integration.md", "icon": "🖥️"},
        ],
        "projects": [
            {"name": "MCP文件系统服务器", "path": "week3/projects/mcp_filesystem/mcp_server.py", "icon": "📁"},
        ],
        "exercises": []
    },
    "week4": {
        "title": "RAG系统基础",
        "icon": "🔍",
        "color": "#10b981",
        "tutorials": [
            {"name": "Embedding向量化入门", "path": "week4/tutorials/01_embedding_basics.md", "icon": "🧮"},
            {"name": "ChromaDB快速入门", "path": "week4/tutorials/02a_chromadb.md", "icon": "📊"},
            {"name": "Milvus向量数据库", "path": "week4/tutorials/02b_milvus.md", "icon": "🗄️"},
            {"name": "检索策略详解", "path": "week4/tutorials/03_retrieval_strategies.md", "icon": "🎯"},
            {"name": "构建简单RAG系统", "path": "week4/tutorials/04_simple_rag.md", "icon": "🤖"},
        ],
        "projects": [
            {"name": "智能文档问答系统", "path": "week4/projects/project_doc_qa/README.md", "icon": "📚"},
        ],
        "exercises": [
            {"name": "RAG基础练习", "path": "week4/exercises/rag_exercises.py", "icon": "💻"},
        ]
    },
    "week5": {
        "title": "RAG系统进阶",
        "icon": "⚡",
        "color": "#f59e0b",
        "tutorials": [
            {"name": "混合检索原理与实现", "path": "week5/tutorials/01a_hybrid_search_native.md", "icon": "🔀"},
            {"name": "LangChain混合检索", "path": "week5/tutorials/01b_hybrid_search_langchain.md", "icon": "🔗"},
            {"name": "重排序模型详解", "path": "week5/tutorials/02_reranking.md", "icon": "📈"},
            {"name": "上下文压缩技术", "path": "week5/tutorials/03_context_compression.md", "icon": "🗜️"},
            {"name": "高级RAG Pipeline", "path": "week5/tutorials/04_advanced_rag_pipeline.md", "icon": "🚀"},
        ],
        "projects": [
            {"name": "智能客服系统", "path": "week5/projects/project_smart_cs/README.md", "icon": "🎧"},
        ],
        "exercises": [
            {"name": "高级RAG练习", "path": "week5/exercises/advanced_rag_exercises.py", "icon": "💻"},
        ]
    },
    "week6": {
        "title": "智能体入门",
        "icon": "🤖",
        "color": "#ef4444",
        "tutorials": [
            {"name": "AI Agent基础概念", "path": "week6/tutorials/01_agent_basics.md", "icon": "🧠"},
            {"name": "ReAct原生实现", "path": "week6/tutorials/02a_react_native.md", "icon": "💭"},
            {"name": "LangChain Agent", "path": "week6/tutorials/02b_react_langchain.md", "icon": "🔗"},
            {"name": "工具开发详解", "path": "week6/tutorials/03_tool_development.md", "icon": "🔧"},
            {"name": "多Agent系统", "path": "week6/tutorials/04_multi_agent.md", "icon": "👥"},
        ],
        "projects": [
            {"name": "智能工作流Agent", "path": "week6/projects/project_workflow_agent/README.md", "icon": "🔄"},
        ],
        "exercises": [
            {"name": "Agent开发练习", "path": "week6/exercises/agent_exercises.py", "icon": "💻"},
        ]
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
    return get_html_template()


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


def get_html_template():
    """返回完整的HTML模板"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI工程师2026速成训练营</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.0/github-markdown-dark.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        .glass {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .glass-hover:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }
        .gradient-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .sidebar {
            width: 320px;
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            left: 0;
            top: 0;
        }
        .main-content {
            margin-left: 320px;
            min-height: 100vh;
            padding: 2rem;
        }
        .week-badge {
            font-size: 0.65rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .nav-item {
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .nav-item.active {
            background: rgba(139, 92, 246, 0.2);
            border-left: 3px solid #8b5cf6;
        }
        .markdown-body {
            background: transparent !important;
            color: #e2e8f0 !important;
        }
        .markdown-body pre {
            background: rgba(0,0,0,0.3) !important;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .markdown-body code {
            background: rgba(139, 92, 246, 0.2) !important;
            color: #e9d5ff !important;
        }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            border-bottom-color: rgba(255,255,255,0.1) !important;
            color: #f1f5f9 !important;
        }
        .markdown-body a { color: #a78bfa !important; }
        .markdown-body blockquote {
            border-left-color: #8b5cf6 !important;
            color: #cbd5e1 !important;
        }
        .markdown-body table th, .markdown-body table td {
            border-color: rgba(255,255,255,0.1) !important;
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(139, 92, 246, 0.3);
            border-top-color: #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
        ::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.5); border-radius: 3px; }
    </style>
</head>
<body class="text-gray-200">
    <!-- 侧边栏 -->
    <aside class="sidebar glass p-6">
        <div class="mb-8">
            <h1 class="text-2xl font-bold gradient-text mb-1">🚀 AI工程师训练营</h1>
            <p class="text-gray-400 text-sm">12周从入门到精通 · 2026版</p>
        </div>
        
        <nav id="nav-container"></nav>
        
        <div class="mt-8 pt-6 border-t border-gray-700/50">
            <a href="https://github.com/falses00/-AI-2026-" target="_blank" 
               class="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                GitHub 仓库
            </a>
        </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="main-content">
        <div id="content-container" class="max-w-4xl mx-auto"></div>
    </main>
    
    <script>
        // 课程数据
        let curriculum = {};
        let currentPath = null;
        
        // 初始化
        async function init() {
            try {
                const res = await fetch('/api/curriculum');
                curriculum = await res.json();
                renderNav();
                renderHome();
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
                html += `
                    <div class="mb-6">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="week-badge text-white" style="background: ${week.color}">${weekId.toUpperCase()}</span>
                            <span class="text-sm font-medium text-gray-300">${week.icon} ${week.title}</span>
                        </div>
                        <div class="space-y-1 pl-2">
                `;
                
                // 教程
                for (const item of week.tutorials) {
                    html += `
                        <div class="nav-item glass-hover text-gray-300 text-sm" 
                             data-path="${item.path}" onclick="loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span>${item.name}</span>
                        </div>
                    `;
                }
                
                // 项目
                for (const item of week.projects) {
                    html += `
                        <div class="nav-item glass-hover text-green-400 text-sm" 
                             data-path="${item.path}" onclick="loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span>${item.name}</span>
                        </div>
                    `;
                }
                
                // 练习
                for (const item of week.exercises) {
                    html += `
                        <div class="nav-item glass-hover text-yellow-400 text-sm" 
                             data-path="${item.path}" onclick="loadContent('${item.path}')">
                            <span>${item.icon}</span>
                            <span>${item.name}</span>
                        </div>
                    `;
                }
                
                html += '</div></div>';
            }
            
            container.innerHTML = html;
        }
        
        // 渲染首页
        function renderHome() {
            const container = document.getElementById('content-container');
            container.innerHTML = `
                <div class="hero-card rounded-2xl p-8 mb-8">
                    <h1 class="text-4xl font-bold gradient-text mb-4">🚀 AI工程师2026速成训练营</h1>
                    <p class="text-xl text-gray-300 mb-2">12周从"调API"到"智能体开发"</p>
                    <p class="text-gray-400">掌握MCP协议 · RAG系统 · Agentic Workflows</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    ${Object.entries(curriculum).map(([id, week]) => `
                        <div class="glass rounded-xl p-6 hover:scale-105 transition-transform cursor-pointer" 
                             onclick="scrollToWeek('${id}')">
                            <div class="text-4xl mb-4">${week.icon}</div>
                            <div class="week-badge text-white mb-3" style="background: ${week.color}">${id.toUpperCase()}</div>
                            <h3 class="font-bold text-lg mb-2">${week.title}</h3>
                            <p class="text-gray-400 text-sm">
                                ${week.tutorials.length} 教程 · 
                                ${week.projects.length} 项目 · 
                                ${week.exercises.length} 练习
                            </p>
                        </div>
                    `).join('')}
                </div>
                
                <div class="glass rounded-xl p-6">
                    <h2 class="text-xl font-bold mb-4">📖 快速开始</h2>
                    <ol class="space-y-3 text-gray-300">
                        <li class="flex items-start gap-3">
                            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm">1</span>
                            <span>从左侧选择一个教程开始学习</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm">2</span>
                            <span>完成每周的实战项目巩固知识</span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm">3</span>
                            <span>通过练习题检验学习效果</span>
                        </li>
                    </ol>
                </div>
            `;
        }
        
        // 加载内容
        async function loadContent(path) {
            const container = document.getElementById('content-container');
            
            // 显示加载状态
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
                    // Python代码
                    const escaped = data.content
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;');
                    container.innerHTML = `
                        <div class="glass rounded-xl p-6">
                            <div class="flex items-center justify-between mb-4">
                                <h2 class="text-xl font-bold text-gray-200">📄 ${path.split('/').pop()}</h2>
                                <span class="text-xs text-gray-500">Python</span>
                            </div>
                            <pre class="rounded-lg overflow-auto"><code class="language-python hljs">${escaped}</code></pre>
                        </div>
                    `;
                    hljs.highlightAll();
                } else {
                    // Markdown
                    container.innerHTML = `
                        <div class="glass rounded-xl p-8 markdown-body">
                            ${marked.parse(data.content)}
                        </div>
                    `;
                    // 高亮代码块
                    container.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
                
                currentPath = path;
                window.scrollTo(0, 0);
            } catch (e) {
                container.innerHTML = `
                    <div class="glass rounded-xl p-8 text-center">
                        <div class="text-6xl mb-4">😢</div>
                        <h2 class="text-xl font-bold text-red-400 mb-2">加载失败</h2>
                        <p class="text-gray-400">${e.message || '请检查文件是否存在'}</p>
                        <button onclick="renderHome()" class="mt-4 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors">
                            返回首页
                        </button>
                    </div>
                `;
            }
        }
        
        function scrollToWeek(weekId) {
            const week = curriculum[weekId];
            if (week && week.tutorials.length > 0) {
                loadContent(week.tutorials[0].path);
            }
        }
        
        // 初始化应用
        init();
    </script>
</body>
</html>'''


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
