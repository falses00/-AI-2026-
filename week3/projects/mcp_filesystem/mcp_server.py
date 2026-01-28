"""
Week 3 MCP项目：文件系统服务器

功能：
- 列出目录文件
- 读取文件内容
- 搜索文件

安装依赖：
    pip install fastmcp

运行：
    python mcp_server.py
"""

from fastmcp import FastMCP
import os
from pathlib import Path
from datetime import datetime

# 创建MCP服务器
mcp = FastMCP("📁 文件管理助手")


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """
    列出目录中的文件和文件夹
    
    Args:
        path: 目录路径，默认为当前目录
        
    Returns:
        文件列表，包含名称、类型和大小
    """
    try:
        items = []
        for item in Path(path).iterdir():
            item_type = "📁" if item.is_dir() else "📄"
            size = item.stat().st_size if item.is_file() else "-"
            items.append(f"{item_type} {item.name} ({size} bytes)")
        
        return "\n".join(items) if items else "目录为空"
    except Exception as e:
        return f"错误: {e}"


@mcp.tool()
def read_file(path: str) -> str:
    """
    读取文件内容
    
    Args:
        path: 文件路径
        
    Returns:
        文件内容（最多前1000个字符）
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(1000)
            if len(content) == 1000:
                content += "\n...(内容已截断)"
            return content
    except Exception as e:
        return f"读取失败: {e}"


@mcp.tool()
def search_files(directory: str, pattern: str) -> str:
    """
    在目录中搜索文件
    
    Args:
        directory: 搜索的目录
        pattern: 搜索模式（如 *.py, *.md）
        
    Returns:
        匹配的文件列表
    """
    try:
        matches = list(Path(directory).rglob(pattern))
        if not matches:
            return "未找到匹配的文件"
        
        result = [str(m) for m in matches[:20]]  # 最多20个结果
        return "\n".join(result)
    except Exception as e:
        return f"搜索失败: {e}"


@mcp.tool()
def get_file_info(path: str) -> str:
    """
    获取文件详细信息
    
    Args:
        path: 文件路径
        
    Returns:
        文件的详细信息
    """
    try:
        p = Path(path)
        stat = p.stat()
        
        info = {
            "名称": p.name,
            "路径": str(p.absolute()),
            "大小": f"{stat.st_size} bytes",
            "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "类型": "目录" if p.is_dir() else "文件"
        }
        
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    except Exception as e:
        return f"获取信息失败: {e}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    写入文件内容
    
    Args:
        path: 文件路径
        content: 要写入的内容
        
    Returns:
        操作结果
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ 已成功写入: {path}"
    except Exception as e:
        return f"写入失败: {e}"


# 主入口
if __name__ == "__main__":
    print("🚀 MCP文件管理服务器启动中...")
    print("📍 配置Claude Desktop后即可使用")
    mcp.run()
