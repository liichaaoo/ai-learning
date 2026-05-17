# Week 2 · Agent 设计模式（5 天）⭐

> 📅 建议时间：阶段 4 第二周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：吃透 ReAct / Plan-and-Execute / Multi-Agent / MCP，做出 4 个模式 demo

---

## 🎉 你即将跨过的"关键分水岭"

Week 1 你的 Agent 能"调单个工具"。

**Week 2 结束后你能**：

```
用户："帮我调研一下电动汽车市场，输出一份 PPT 大纲"

Agent:
  ① 规划：[市场规模] [主要玩家] [技术趋势] [输出 PPT 大纲]
  ② 执行第 1 步：调 searchTool → 拿数据
  ③ 执行第 2 步：调 searchTool → 拿玩家信息
  ④ ……
  ⑤ 整合：生成 PPT 大纲
```

> 💡 **这才是真正的 Agent**——Week 1 的"调一个工具"是 Function Calling，Week 2 的"规划-执行-反思"才是 Agent。

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **ReAct 模式** | Thought / Action / Observation 三段循环 |
| **Plan-and-Execute** | 先规划再执行，适合复杂多步 |
| **Multi-Agent** | 角色分工（Researcher / Writer / Reviewer）|
| **MCP 协议** ⭐ | Anthropic 主推的"工具市场"标准，2026 必会 |
| **Agent 取舍** | 知道什么场景该用哪种模式 |

---

## 📅 5 天计划

| Day | 主题 | 产出 | 时长 |
|-----|------|------|------|
| **Day 1** | [ReAct 模式](./Day1-ReAct模式.md) ⭐ | 自己手写 ReAct 循环 + LC4j 内置版对比 | 1.5h |
| **Day 2** | [Plan-and-Execute](./Day2-Plan-and-Execute.md) | 规划器 + 执行器分离的实现 | 1.5h |
| **Day 3** | [Multi-Agent 协作](./Day3-Multi-Agent协作.md) | 三角色"研究小组"demo | 1.5h |
| **Day 4** | [MCP 协议](./Day4-MCP协议.md) ⭐ | 写一个 MCP Server + 接入 Claude/Spring AI | 2h |
| **Day 5** | [模式对比与整合](./Day5-模式对比与整合.md) | 一份"该选哪个 Agent 模式"决策表 + 综合 demo | 1.5h |

---

## 📦 本周最终产出

`项目/07-agent-patterns/`

```
07-agent-patterns/
├── pom.xml
├── README.md
└── src/main/
    └── java/com/demo/agent/
        ├── react/                     ← Day 1
        │   ├── ManualReActAgent.java
        │   └── Lc4jReActAgent.java
        ├── planexec/                  ← Day 2
        │   ├── Planner.java
        │   └── PlanExecutor.java
        ├── multi/                     ← Day 3
        │   ├── Researcher.java
        │   ├── Writer.java
        │   ├── Reviewer.java
        │   └── Orchestrator.java
        └── mcp/                       ← Day 4
            ├── McpServer.java
            └── McpClientDemo.java
```

---

## 🧭 推荐节奏

```
周一 Day 1   1.5h    ReAct 手撕 + LC4j 内置版
周二 Day 2   1.5h    Plan-and-Execute
周三 Day 3   1.5h    Multi-Agent 三角色
周四 Day 4   2h      MCP 协议 + Server 实现
周五         休息
周六 Day 5   1.5h    模式对比 + 综合 demo
周日         写笔记《ReAct详解》《MCP协议》《PromptInjection防御》
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [ReAct 模式](./Day1-ReAct模式.md)
- [ ] Day 2 · [Plan-and-Execute](./Day2-Plan-and-Execute.md)
- [ ] Day 3 · [Multi-Agent 协作](./Day3-Multi-Agent协作.md)
- [ ] Day 4 · [MCP 协议](./Day4-MCP协议.md)
- [ ] Day 5 · [模式对比与整合](./Day5-模式对比与整合.md)

---

## 🎯 本周出关自测（8 题）

1. ReAct 的三个动作分别是？
2. ReAct 跟 CoT（Chain-of-Thought）的区别？
3. Plan-and-Execute 比 ReAct 适合什么场景？
4. Multi-Agent 的"角色协作"在工程上是怎么实现的？
5. MCP 解决了什么 Function Calling 没解决的问题？
6. MCP Server 跟 RPC Server 有什么相似与差异？
7. 怎么避免 Agent 死循环？
8. Prompt Injection 怎么防？（提示：本周末写专题笔记）

**答对 6+ 题** = 本周通过。

---

## 🚦 重要提醒

### 1. 不要追求"通用 Agent 框架"

工程里**99% 用 ReAct + 自定义工具就够**。Plan-and-Execute / Multi-Agent 是更高级的工具，**有具体场景才用**。

### 2. MCP 一定要学

2025 下半年开始，所有主流模型（Claude / GPT / 通义 / DeepSeek）都开始支持 MCP——**这是 Function Calling 的下一代标准**。

### 3. Prompt Injection 是高级岗必考题

Week 2 末写一份《PromptInjection防御.md》，**面试常问，简历加分**。

---

## 🔗 相关资源

- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Plan-and-Solve 论文](https://arxiv.org/abs/2305.04091)
- [MCP 官方网站](https://modelcontextprotocol.io/)
- [Spring AI MCP](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
- [LangChain4j Agents Tutorial](https://docs.langchain4j.dev/tutorials/tools#agents)

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1 · ReAct 模式](./Day1-ReAct模式.md)**
