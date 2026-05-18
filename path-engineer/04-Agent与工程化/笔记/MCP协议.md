# MCP 协议（Model Context Protocol）速查

> 服务于 Week 2 Day 4。2026 必会。

---

## 1. 一句话本质

> **MCP = "工具市场"的统一协议——把 Function Calling 从"每家自定义"升级为"全行业标准"。**

类比：JDBC 之于数据库、USB 之于外设。

---

## 2. 三大对象

| 对象 | 是什么 |
|------|--------|
| **Tools** | 工具（类似 Function Calling，跨厂商）|
| **Resources** | 只读资源（文件、DB 视图、API 数据）|
| **Prompts** | 预设 Prompt 模板 |

---

## 3. 跟 Function Calling 区别

| 维度 | FC | MCP |
|------|----|----|
| 标准化 | 各家自定义 | **跨厂商统一** |
| 位置 | 应用代码内 | **独立 Server** |
| 部署 | 跟应用一起 | **独立进程** |
| 发现 | 写死 | **运行时 list_tools** |
| 复用 | 一对一 | **一对多** |

> 💡 **不是替代**：MCP Server 内部还是用 Function Calling 跟 LLM 通信。**MCP 是上层协议，FC 是底层**。

---

## 4. 写 Server（Spring AI）

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server</artifactId>
</dependency>
```

```yaml
spring.ai.mcp.server:
  name: my-mcp
  type: SYNC
  capabilities:
    tool: true
```

```java
@Service
public class MyTools {
    @Tool("...")
    public String doX(@P("...") String arg) { ... }
}

@Bean
public List<ToolCallback> mcpTools(MyTools tools) {
    return ToolCallbacks.from(tools).toList();
}
```

---

## 5. 接入 Claude Desktop

```json
{
  "mcpServers": {
    "my-mcp": {
      "command": "java",
      "args": ["-jar", "/path/to/my-mcp.jar"]
    }
  }
}
```

重启 Claude Desktop → 看到工具图标 → 自动可用。

---

## 6. 写 Client（Spring AI 消费别人的 MCP Server）

```yaml
spring.ai.mcp.client.stdio.servers:
  github:
    command: "java"
    args: ["-jar", "github-mcp.jar"]
```

```java
@Autowired SyncMcpToolCallbackProvider mcpTools;

ChatClient chatClient = builder
        .defaultTools(mcpTools.getToolCallbacks())   // ⭐ 跟普通 Tool 一样用
        .build();
```

---

## 7. 通信方式

| 方式 | 适合 |
|------|------|
| **stdio** | 本地 server，最简 |
| **SSE** | 远程 server，单向流 |
| **WebSocket** | 双向通信 |

---

## 8. 生态（2026）

| 阵营 | 状态 |
|------|------|
| Anthropic Claude | ⭐ 原生支持 |
| Spring AI 1.0 | ⭐ 一等公民 |
| OpenAI / 通义 / DeepSeek | 跟进中 |
| 官方 Server 目录 | 50+（GitHub / Slack / Postgres / FS 等）|

---

## 9. 高频面试题

**Q：MCP 和 FC 区别？**
FC 是单厂商工具调用；MCP 是跨厂商工具协议。Server 独立部署，多客户端共享。

**Q：MCP 会取代 FC 吗？**
不会。MCP Server 内部仍用 FC。**MCP 是上层协议，FC 是底层**。

**Q：怎么鉴权？**
stdio：环境变量传 token；SSE：HTTP Header Bearer Token。

**Q：MCP 解决了什么痛点？**
工具复用难、分发难、能力发现难——把 LLM 工具变成"像 npm 一样安装"。

---

## 🔗 相关链接

- 📖 [Week 2 Day 4 · MCP 协议](../Week2-Agent设计模式/Day4-MCP协议.md)
- 📚 [MCP 官方](https://modelcontextprotocol.io/)
- 📚 [Spring AI MCP](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
- 📚 [官方 Server 目录](https://github.com/modelcontextprotocol/servers)
