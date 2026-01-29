# MCP服务配置指南

## 需要安装的MCP服务

请将以下配置添加到你的Claude Desktop配置文件：

**配置文件位置**：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

## 配置内容

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-server-fetch"]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@anthropic/chrome-devtools-mcp"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-server-memory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "你的GitHub Token"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-server-filesystem", "I:/Study FastAPI"]
    }
  }
}
```

## 安装步骤

1. **确保Node.js已安装**（版本16+）
   ```bash
   node --version
   npm --version
   ```

2. **打开配置文件**
   - 按 Win+R，输入：`%APPDATA%\Claude`
   - 找到或创建 `claude_desktop_config.json`

3. **粘贴上面的配置**

4. **获取GitHub Token**（可选）
   - 访问 https://github.com/settings/tokens
   - 创建Personal Access Token
   - 替换配置中的 `你的GitHub Token`

5. **重启Claude Desktop**

## 服务说明

| 服务 | 用途 |
|------|------|
| fetch | 获取网页内容 |
| chrome-devtools | 浏览器调试 |
| memory | 持久化记忆 |
| github | GitHub API访问 |
| context7 | 代码文档查询 |
| filesystem | 本地文件访问 |
