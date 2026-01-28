"""
🚀 AI工程师训练营 - Web展示界面

运行方式：
    cd "i:\Study FastAPI"
    D:\Anaconda\envs\pytorch_Gpu\python.exe -m uvicorn webapp.app:app --reload --port 8080

访问：http://localhost:8080
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

app = FastAPI(title="AI工程师2026速成训练营")

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent


def read_markdown(path: str) -> str:
    """读取Markdown文件"""
    full_path = BASE_DIR / path
    if full_path.exists():
        return full_path.read_text(encoding='utf-8')
    return "文件未找到"


def get_curriculum():
    """获取课程大纲"""
    return {
        "week1": {
            "title": "🔧 第1周：Python高级特性 + AI工程环境",
            "tutorials": [
                ("异步编程核心概念", "week1/tutorials/01_async_basics.md"),
                ("Pydantic数据验证", "week1/tutorials/04_pydantic_basics.md"),
                ("FastAPI快速入门", "week1/tutorials/05_fastapi_quickstart.md"),
                ("Docker基础入门", "week1/tutorials/07_docker_basics.md"),
            ],
            "projects": [
                ("图书管理API", "week1/projects/project1_structured_api/README.md"),
            ]
        },
        "week2": {
            "title": "🤖 第2周：大模型API深度控制",
            "tutorials": [
                ("DeepSeek API快速入门", "week2/tutorials/01_openai_api_basics.md"),
                ("结构化输出详解", "week2/tutorials/02_structured_output.md"),
                ("Function Calling详解", "week2/tutorials/04_function_calling_intro.md"),
            ],
            "projects": []
        },
        "week3": {
            "title": "🔌 第3周：MCP协议深度剖析",
            "tutorials": [
                ("MCP协议入门", "week3/tutorials/01_mcp_introduction.md"),
            ],
            "projects": [
                ("MCP文件系统服务器", "week3/projects/mcp_filesystem/mcp_server.py"),
            ]
        }
    }


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI工程师2026速成训练营</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.0/github-markdown-dark.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .gradient-text {
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }
        .markdown-body {
            background: transparent !important;
        }
        .week-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
</head>
<body class="text-white">
    <div class="flex min-h-screen">
        <!-- 侧边栏 -->
        <nav class="w-80 glass-card p-6 overflow-y-auto">
            <div class="mb-8">
                <h1 class="text-2xl font-bold gradient-text">🚀 AI工程师训练营</h1>
                <p class="text-gray-400 text-sm mt-2">12周从入门到精通</p>
            </div>
            
            <div id="nav-content">
                <!-- 动态生成导航 -->
            </div>
        </nav>
        
        <!-- 主内容区 -->
        <main class="flex-1 p-8 overflow-y-auto">
            <div id="content" class="markdown-body max-w-4xl mx-auto p-8 glass-card rounded-2xl">
                <!-- 动态加载内容 -->
                <h1 class="gradient-text text-4xl font-bold mb-6">欢迎来到AI工程师训练营！</h1>
                <p class="text-xl text-gray-300 mb-8">选择左侧的课程开始学习</p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="glass-card p-6 rounded-xl">
                        <div class="text-3xl mb-4">🔧</div>
                        <h3 class="font-bold text-lg mb-2">第1周</h3>
                        <p class="text-gray-400 text-sm">Python异步编程、FastAPI、Docker</p>
                    </div>
                    <div class="glass-card p-6 rounded-xl">
                        <div class="text-3xl mb-4">🤖</div>
                        <h3 class="font-bold text-lg mb-2">第2周</h3>
                        <p class="text-gray-400 text-sm">DeepSeek API、结构化输出、Function Calling</p>
                    </div>
                    <div class="glass-card p-6 rounded-xl">
                        <div class="text-3xl mb-4">🔌</div>
                        <h3 class="font-bold text-lg mb-2">第3周</h3>
                        <p class="text-gray-400 text-sm">MCP协议、智能体开发</p>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        const curriculum = CURRICULUM_DATA;
        
        // 生成导航
        function renderNav() {
            const nav = document.getElementById('nav-content');
            let html = '';
            
            for (const [key, week] of Object.entries(curriculum)) {
                html += `
                    <div class="mb-6">
                        <h2 class="text-lg font-bold mb-3 flex items-center">
                            <span class="week-badge px-2 py-1 rounded text-xs mr-2">${key.toUpperCase()}</span>
                            ${week.title.split('：')[1] || week.title}
                        </h2>
                        <div class="space-y-1">
                `;
                
                week.tutorials.forEach(([name, path]) => {
                    html += `
                        <a href="#" onclick="loadContent('${path}')" 
                           class="nav-item block px-4 py-2 rounded-lg text-gray-300 text-sm transition-all">
                            📖 ${name}
                        </a>
                    `;
                });
                
                week.projects.forEach(([name, path]) => {
                    html += `
                        <a href="#" onclick="loadContent('${path}')" 
                           class="nav-item block px-4 py-2 rounded-lg text-green-400 text-sm transition-all">
                            🚀 ${name}
                        </a>
                    `;
                });
                
                html += '</div></div>';
            }
            
            nav.innerHTML = html;
        }
        
        // 加载内容
        async function loadContent(path) {
            const content = document.getElementById('content');
            content.innerHTML = '<p class="text-center text-gray-400">加载中...</p>';
            
            try {
                const response = await fetch(`/api/content?path=${encodeURIComponent(path)}`);
                const data = await response.json();
                
                if (path.endsWith('.py')) {
                    content.innerHTML = `<pre class="language-python"><code>${escapeHtml(data.content)}</code></pre>`;
                } else {
                    content.innerHTML = marked.parse(data.content);
                }
            } catch (e) {
                content.innerHTML = '<p class="text-red-400">加载失败</p>';
            }
        }
        
        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;")
                       .replace(/</g, "&lt;")
                       .replace(/>/g, "&gt;");
        }
        
        renderNav();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """主页"""
    curriculum = get_curriculum()
    html = HTML_TEMPLATE.replace("CURRICULUM_DATA", str(curriculum).replace("'", '"'))
    return html


@app.get("/api/content")
async def get_content(path: str):
    """获取内容API"""
    content = read_markdown(path)
    return {"content": content}


@app.get("/api/curriculum")
async def get_curriculum_api():
    """获取课程大纲"""
    return get_curriculum()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
