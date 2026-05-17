# 07-agent-patterns · 4 种 Agent 模式 Demo（Week 2 交付物）

> 配套教程：[Week 2 · Agent 设计模式](../../Week2-Agent设计模式/README.md)

---

## 🎯 项目目标

每种模式至少一个 demo，最后整合成一个"自适应 Agent"：

- ReAct（手撕 + LC4j 内置）
- Plan-and-Execute（Planner + Executor）
- Multi-Agent（Researcher + Writer + Reviewer）
- MCP（Server + Client）

---

## 📁 期望目录

```
07-agent-patterns/
├── pom.xml
├── README.md
└── src/main/java/com/demo/agent/
    ├── AgentPatternsApplication.java
    ├── react/
    │   ├── ManualReActAgent.java        ← Day1 §3
    │   └── Lc4jReActDemo.java           ← Day1 §4
    ├── planexec/
    │   ├── Planner.java                  ← Day2 §2.1
    │   └── PlanExecutor.java             ← Day2 §2.2
    ├── multi/
    │   ├── Researcher.java               ← Day3 §2.1
    │   ├── Writer.java
    │   ├── Reviewer.java
    │   └── Orchestrator.java             ← Day3 §2.3
    ├── mcp/
    │   ├── McpServerDemo.java            ← Day4 §4.2
    │   └── McpClientDemo.java            ← Day4 §5
    └── adaptive/
        ├── Triager.java                  ← Day5 §4.1
        └── AdaptiveAgent.java            ← Day5 §4.2
```

---

## 🚀 快速测试

```bash
DASHSCOPE_API_KEY=sk-xxx ./mvnw spring-boot:run

# ReAct
curl -X POST .../api/agent/react -d '{"q":"上海天气合不合适散步？"}'

# P&E
curl -X POST .../api/agent/plan -d '{"q":"调研新能源汽车 2024 市场，输出 3 个洞察"}'

# Multi-Agent
curl -X POST .../api/agent/multi -d '{"topic":"量子计算的现状"}'

# 自适应（自动选模式）
curl -X POST .../api/agent/auto -d '{"q":"... 任何问题 ..."}'
```

---

## 📝 进度自检

- [ ] 手写 ReAct 跑通（看到 Thought/Action/Observation）
- [ ] Plan-and-Execute 看到 plan + 逐步执行日志
- [ ] Multi-Agent 三角色 + Reviewer 反馈 → Writer 重写
- [ ] MCP Server 能在 Claude Desktop 中接入
- [ ] 自适应 Agent 能自动选模式

---

## 🔗 相关链接

- ⬆️ [Week 2 总览](../../Week2-Agent设计模式/README.md)
- 📖 [Day 5 整合](../../Week2-Agent设计模式/Day5-模式对比与整合.md)
- 📦 [上一项目：06-langchain4j-hello](../06-langchain4j-hello/)
- 📦 [下一项目：08-ai-code-reviewer](../08-ai-code-reviewer/)
