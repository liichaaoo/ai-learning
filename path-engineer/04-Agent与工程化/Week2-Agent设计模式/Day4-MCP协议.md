# Day 4 · MCP 协议（Model Context Protocol）⭐ 2026 必会

> ⏱️ 时间：2 小时
> 🎯 目标：理解 MCP 解决了什么，写一个最简 MCP Server，能在 Claude / Spring AI 里接入

---

## 0. 心法（5 分钟）

> **MCP = "工具市场"的统一协议——把 Function Calling 从"每家自定义"升级为"全行业标准"。**

类比：

```
Function Calling 时代  → 每个 LLM API 一套 tool schema（OpenAI / Claude / 通义都不同）
MCP 时代             → 一份 MCP Server，所有支持 MCP 的客户端都能用
```

像 HTTP / JDBC / USB——**协议统一才有生态**。

---

## 1. MCP 解决的 3 个核心痛点（10 分钟）

| 痛点 | MCP 之前 | MCP 之后 |
|------|---------|---------|
| **工具复用** | 每接一个模型重写一遍 | **一个 Server，多客户端共用** |
| **工具分发** | 集成在每个项目里 | **像 npm 一样安装** |
| **能力发现** | 写死在代码 | **动态 list_tools 发现** |

---

## 2. MCP 三大对象（15 分钟）

```
MCP Server  暴露能力的程序（你写的）
    │
    ├─► Tools         工具（类似 Function Calling，但跨厂商）
    ├─► Resources     资源（文件、数据库、API 的只读视图）
    └─► Prompts       预设 Prompt 模板

MCP Client  调用方（Claude Desktop / Cursor / Spring AI）
    │
    └─► 通过 stdio / SSE / WebSocket 跟 Server 通信
```

### 例子

```
MCP Server "github"：
  Tools:     list_repos, get_issue, create_pr
  Resources: file://README.md, file://CHANGELOG.md
  Prompts:   summarize_changelog, draft_release_notes
```

任何支持 MCP 的客户端（Claude / Cursor / Cline …）安装这个 server 后，**自动获得操作 GitHub 的能力**——不用写代码集成。

---

## 3. 跟 Function Calling 的区别（10 分钟）

| 维度 | Function Calling | MCP |
|------|------------------|------|
| 标准化 | 各家自定义 | **跨厂商统一** |
| 工具位置 | 应用代码内 | **独立 Server** |
| 部署 | 跟应用一起 | **独立进程，可复用** |
| 发现 | 写死在代码 | **运行时 list 发现** |
| 通信 | 进程内 | **stdio / SSE** |
| 生态 | 各做各的 | **正在形成"工具市场"** |

> 🎯 **一句话**：**Function Calling 是工具的"本地实现"，MCP 是工具的"远程协议"**。
>
> 类比：本地 import 一个库 vs 调一个 REST API。

---

## 4. 写一个最简 MCP Server（30 分钟）

> 用 Spring AI MCP 或 Java 原生 MCP SDK 都行。这里用 Spring AI 1.0 的 starter。

### 4.1 加依赖

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-mcp-server-spring-boot-starter</artifactId>
</dependency>
```

### 4.2 暴露工具

```java
@Service
public class GitHubTools {

    @Tool("根据仓库名查 issue 列表")
    public String listIssues(@P("repo 全名，如 spring-projects/spring-ai") String repo,
                              @P("状态：open/closed/all") String state) {
        return githubClient.listIssues(repo, state);
    }

    @Tool("创建一个 PR")
    public String createPr(@P("repo") String repo,
                            @P("title") String title,
                            @P("head 分支") String head,
                            @P("base 分支") String base) {
        return githubClient.createPr(repo, title, head, base);
    }
}
```

### 4.3 启用 MCP Server

```yaml
spring:
  ai:
    mcp:
      server:
        name: github-mcp
        version: 1.0.0
        type: SYNC
        capabilities:
          tool: true
          resource: false
          prompt: false
```

```java
@SpringBootApplication
public class GithubMcpApp {
    public static void main(String[] args) { SpringApplication.run(GithubMcpApp.class, args); }

    @Bean
    public List<ToolCallback> mcpTools(GitHubTools tools) {
        return ToolCallbacks.from(tools).toList();        // 自动把 @Tool 方法注册为 MCP Tools
    }
}
```

### 4.4 跑起来

```bash
./mvnw spring-boot:run
# Server 监听 stdio（默认）或 SSE
```

### 4.5 在 Claude Desktop 里接入

修改 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "github": {
      "command": "java",
      "args": ["-jar", "/path/to/your/github-mcp.jar"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

重启 Claude Desktop → 在聊天框看到工具图标 → 让 Claude 帮你"列出 spring-projects/spring-ai 的开放 issue"——它会自动调你的 server。

> 🎯 **跑通这段 = 你已经掌握了 2026 最热的 AI 集成方式**。

---

## 5. 在 Spring AI 里作 MCP Client（10 分钟）

反过来：你的 Spring AI 应用消费别人的 MCP Server。

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-mcp-client-spring-boot-starter</artifactId>
</dependency>
```

```yaml
spring:
  ai:
    mcp:
      client:
        stdio:
          servers:
            github:
              command: "java"
              args: ["-jar", "/path/to/github-mcp.jar"]
              env:
                GITHUB_TOKEN: ${GITHUB_TOKEN}
```

```java
@Autowired
SyncMcpToolCallbackProvider mcpTools;            // ⭐ 自动拿到 MCP Server 提供的所有工具

ChatClient chatClient = builder
        .defaultTools(mcpTools.getToolCallbacks())   // 直接当普通 Tool 用
        .build();
```

> 💡 **业务代码完全无感**——Spring AI 把 MCP Tools 翻译成普通 `ToolCallback`，跟本地 `@Tool` 一样用。

---

## 6. MCP 生态现状（5 分钟，2026-05）

| 阵营 | 表现 |
|------|------|
| **Anthropic Claude** | 原生支持，桌面端已用上 |
| **OpenAI GPT** | 跟进中 |
| **微软 Copilot Studio** | 支持 |
| **通义 / DeepSeek** | 跟进中 |
| **Spring AI 1.0** | ⭐ 一等公民 |
| **LangChain / LangGraph** | 支持 |
| **官方 MCP Server 目录** | 已有 GitHub / Slack / Notion / Postgres / Filesystem 等 50+ |

> 🎯 **简历亮点**：「实现 MCP Server 并接入 Claude Desktop / Spring AI 应用，对外提供 XX 能力」——**这就是 2026 高级岗的差异化加分项**。

---

## 7. 高频面试题

**Q1：MCP 和 Function Calling 区别？**
A：FC 是单个 LLM 厂商的工具接入方式；MCP 是跨厂商的"工具市场"协议。Server 独立部署，多客户端共用。

**Q2：MCP Server 怎么部署？**
A：① stdio 进程（最简，本地工具）② SSE Server（远程工具）③ WebSocket（双向）

**Q3：MCP 会取代 Function Calling 吗？**
A：不会取代——MCP Server 内部还是用 Function Calling 跟 LLM 通信。**MCP 是上层协议，FC 是底层调用**。

**Q4：怎么做 MCP 的鉴权？**
A：① stdio 模式：靠环境变量传 token ② SSE 模式：HTTP Header 鉴权（Bearer Token）

---

## 8. 检查清单

- [ ] 解释 MCP 解决了什么 Function Calling 没解决的问题
- [ ] 默写 MCP 三大对象（Tools / Resources / Prompts）
- [ ] 跑通一个 Spring AI MCP Server（暴露至少 2 个工具）
- [ ] 在 Claude Desktop 或 Cline 里成功调用你的 Server
- [ ] 用 MCP Client 消费另一个 Server
- [ ] 知道 MCP 的鉴权方式

完成了 ➡️ [Day 5 · 模式对比与整合](./Day5-模式对比与整合.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · Multi-Agent 协作](./Day3-Multi-Agent协作.md)
- ➡️ [Day 5 · 模式对比与整合](./Day5-模式对比与整合.md)
- ⬆️ [Week 2 总览](./README.md)
- 📚 [MCP 官方](https://modelcontextprotocol.io/)
- 📚 [Spring AI MCP](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
- 📚 [官方 MCP Server 目录](https://github.com/modelcontextprotocol/servers)
