# Codex CLI + Mermaid MCP 架构图快速使用说明

> 目的：下次在 Codex CLI 里，直接用自然语言描述系统架构，让助手生成 Mermaid 架构图并渲染为图片（全程使用本地免费工具）。

---

## 1. 前置条件

- 已安装 Node.js（建议 ≥ 18）
- 正常使用 Codex CLI（可以跑 MCP server）

---

## 2. 安装免费 Mermaid MCP 服务器

这里以开源免费的 `mcp-mermaid` 为例（本地运行，无外部付费服务）。

```bash
# 全局安装
npm install -g mcp-mermaid
```

装完后本机就有一个可执行的 `mcp-mermaid`，可以作为 MCP server 被 Codex CLI 调用。

---

## 3. 在 Codex CLI 中配置 MCP 服务器

> 具体配置文件路径依你本机 Codex CLI 而定，这里只给一个通用 JSON 片段示例。  
> 你只需要在 Codex 的 MCP 配置中增加这一段。

```jsonc
{
  "mcpServers": {
    "mcp-mermaid": {
      "command": "mcp-mermaid",
      "args": []
    }
  }
}
```

如果你更习惯用 `npx` 方式（不想全局装），也可以这样：

```jsonc
{
  "mcpServers": {
    "mcp-mermaid": {
      "command": "npx",
      "args": ["-y", "mcp-mermaid"]
    }
  }
}
```

保存配置后，重启 Codex CLI，让它重新加载 MCP server。

---

## 4. 推荐使用流程（对话模式）

整体流程分三步：

1. 你用自然语言描述系统架构
2. 助手根据描述生成 Mermaid 代码（逻辑在 LLM 内，本身免费）
3. 助手调用 `mcp-mermaid` 渲染出 PNG/SVG 图像，返回文件路径或图内容

### 4.1 典型对话模板

你可以直接对 Codex 说（示例）：

> 帮我画一个电商系统的高层架构图，要求：
> - 用户通过 Web 和 App 访问
> - 前端走 API Gateway
> - 后端有用户服务、商品服务、订单服务
> - 订单服务访问 MySQL 和 Redis
> 用 Mermaid 画一个组件关系图就行。

助手内部会大致按下面两个步骤来做：

1. 先生成 Mermaid 代码，例如：

   ```mermaid
   graph LR
     user_web["User (Web)"]
     user_app["User (App)"]
     api_gw["API Gateway"]

     user_web --> api_gw
     user_app --> api_gw

     user_svc["User Service"]
     product_svc["Product Service"]
     order_svc["Order Service"]

     api_gw --> user_svc
     api_gw --> product_svc
     api_gw --> order_svc

     mysql["MySQL"]
     redis["Redis"]

     order_svc --> mysql
     order_svc --> redis
   ```

2. 然后调用 `mcp-mermaid` 提供的渲染工具，把这段 Mermaid 转成 PNG / SVG 图片，并在终端里告诉你：
   - 图像文件写到哪里（例如 `./diagrams/ecommerce_arch.png`）
   - 同时保留 Mermaid 源码方便下次修改

---

## 5. 建议的图文件管理方式

在你的项目里，可以约定一个专门目录存放图：

```bash
mkdir -p diagrams
```

之后让助手渲染时统一写入 `diagrams/` 下，例如：

- `diagrams/system_arch_overview.png`
- `diagrams/system_arch_overview.mmd`（Mermaid 源码，可选）

---

## 6. 下次使用速查

1. 确认：`mcp-mermaid` 已安装 & Codex CLI MCP 配置已生效  
2. 在 Codex CLI 中发起请求：
   - 描述目标架构 / 流程
   - 指定「用 Mermaid 画图」并「输出 PNG/SVG 到某个路径」
3. 从 `diagrams/` 目录查看生成的图片；需要修改结构时，让助手改 Mermaid 代码并重新渲染即可。

