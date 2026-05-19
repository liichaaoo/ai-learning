# 探索专题 · Java Harness Framework（AgentScope Java）

> 🏷️ **归类**：方向 A（AI 应用架构师）/ Spring AI 之上的"驾驭层"补全
>
> ⏱️ **优先级**：P2（有空再深入，非主线；但战略价值高，建议持续追踪）
>
> 🎯 **背景**：2026 年 AI Agent 圈的共识——**`Agent = Model + Harness`**。模型差距在收敛，差距在"驾驭层"。Java 生态在 Harness 工程化上一直空白，**2026-05-15 阿里 AgentScope Java 1.1.0 发布，自称业界首个 Java Harness Framework**，把 OpenClaw / Claude Code 那套工程能力带到 Java 企业场景。

---

## 📌 一句话定位

> **Spring AI 解决"调 LLM"，Spring AI Alibaba Graph 解决"图编排"，AgentScope Java Harness Framework 解决"Agent 长期运行所需的工程基础设施"——工作区、记忆、沙箱、子 Agent 隔离、多租户。它和前两者不是替代关系，而是分层互补。**

---

## 一、先理清"Harness"这个词在 2026 年的两个含义

| 含义 | 指什么 | 出处 | 本文聚焦 |
|---|---|---|---|
| **Harness 平台** | Harness.io 公司的 AI 原生 DevOps/CI/CD 平台 | 商业产品 | ❌ 不是本文话题 |
| **Harness Engineering（驾驭工程）** | 包裹 LLM 的"装备层"——工具、上下文、记忆、沙箱、文件系统 | Thoughtworks Birgitta Böckeler 2026-04 在 Martin Fowler 专栏提出 | ⭐ 本文话题 |

**核心论断**：同一个模型，配好 Harness，性能能差 10 倍。Claude Code、Cursor、OpenClaw 的护城河主要在 Harness 设计，而非底层模型。

---

## 二、为什么 Java 需要专门的 Harness Framework

| 能力 | Python（Claude Code / OpenClaw 等） | Java（Spring AI 时代） |
|------|-----|------|
| LLM 调用 | ✅ | ✅ Spring AI ChatClient |
| Function Calling | ✅ | ✅ Spring AI Function |
| 图编排 | ✅ LangGraph | 🟡 Spring AI Alibaba Graph（追赶中） |
| **工作区驱动**（人格/知识/技能/记忆沉淀为文件） | ✅ | ❌ |
| **抽象文件系统**（本地/远端/沙箱统一接口） | ✅ | ❌ |
| **沙箱隔离执行**（状态可恢复） | ✅ | ❌ |
| **双层记忆 + 全文检索** | ✅ | ❌ 自己造 |
| **多租户隔离**（SESSION/USER/AGENT/GLOBAL） | ✅ | ❌ |
| **子 Agent 编排 + 异步任务** | ✅ | ❌ |

**结论**：Java AI 工程师过去要么用 Python 微服务，要么自己造一堆基础设施。AgentScope Java 1.1.0 试图把这些"轮子"收敛成框架。

---

## 三、AgentScope Java 1.1.0 速览

### 出品背景
- **AgentScope** 是阿里 ModelScope（魔搭）之后在 Agent 层的战略产品
- Python 版 2024 年开源，主打研究/Python 开发者
- **Java 版 1.0** 发布于 2025-12，**1.1.0** 发布于 2026-05-15（首个 Java Harness Framework）

### 核心入口
```java
HarnessAgent agent = HarnessAgent.builder()
    .workspace(Path.of("./workspace"))
    .filesystem(new LocalFilesystemSpec())     // 或 RemoteFilesystemSpec / SandboxSpec
    .model(chatModel)
    .build();

agent.call(message, runtimeContext);
```

### 四大核心能力

| # | 能力 | 一句话说明 |
|---|------|------|
| 1 | **Workspace 驱动** | 人格、记忆、知识、技能、子 Agent 规格全部沉淀在结构化目录，自动加载/回写 |
| 2 | **可插拔文件系统** | 本地磁盘 / 远端共享存储 / 沙箱 共用一套接口 |
| 3 | **开箱即用上下文管理** | 对话压缩 + 双层记忆 + SQLite FTS5 全文检索 |
| 4 | **子 Agent 编排** | 声明式定义、同步/异步、沙箱状态可恢复、多租户隔离 |

---

## 四、核心设计：两大支柱

### 支柱一：Workspace = Source of Truth

```
workspace/
├── AGENTS.md           # Agent 人格与行为约定
├── MEMORY.md           # 长期记忆（精炼后注入 system prompt）
├── knowledge/          # 领域知识
├── skills/             # 可复用技能（每个 SKILL.md）
├── subagents/          # 子 Agent 规格（YAML front matter + Markdown）
├── memory/             # 每日记忆流水账（YYYY-MM-DD.md）
└── agents/<agentId>/
    ├── context/<sessionId>/    # 状态快照
    └── sessions/                # 对话日志（JSONL）
```

**自动化机制**：
- 推理前 `WorkspaceContextHook` → 注入 `AGENTS.md` + `MEMORY.md` + `knowledge/` 到 system prompt
- 推理后 `MemoryFlushHook` → 提炼新事实写入 `memory/YYYY-MM-DD.md`
- 后台 `MemoryConsolidator` → 周期性合并流水账为精炼长期记忆

> **设计哲学**：把 Agent 配置从代码迁移到文件，Agent 像人一样在工作区里"成长"。

### 支柱二：AbstractFilesystem 统一接口

`read / write / ls / grep` 一套 API，下面挂三种实现：

| 模式 | 配置 | 适用场景 | Shell 工具 |
|---|---|---|---|
| **本机 + Shell** | `LocalFilesystemSpec` | 个人助手、开发测试 | ✅ 默认开放 |
| **远端共享存储** | `RemoteFilesystemSpec(redis/oss)` | 多副本在线服务（如交易 Agent） | ❌ 默认禁用（安全设计） |
| **沙箱执行** | `SandboxSpec` | DataAgent、Coding Agent | ✅ 隔离环境内 |

> **关键安全设计**：远端模式刻意不暴露 Shell。Agent 只能用业务工具，避免不可信输入直达宿主机。

---

## 五、和已有 Java AI 框架的关系

### 和 Spring AI 的关系：分层而非替代

```
┌──────────────────────────────────────────┐
│  Harness 层（AgentScope Java）            │
│  - Workspace / Memory / Sandbox / Subagent │
├──────────────────────────────────────────┤
│  编排层（Spring AI Alibaba Graph / LangGraph4j）│
│  - Graph / 状态机 / 条件分支               │
├──────────────────────────────────────────┤
│  调用层（Spring AI / LangChain4j）         │
│  - ChatClient / Function / Advisor        │
├──────────────────────────────────────────┤
│  模型层                                    │
└──────────────────────────────────────────┘
```

**配套使用方式**：
- 简单 RAG / 单轮 → Spring AI 直接搞
- ReAct Agent + 工具调用 → Spring AI Function Calling
- 复杂图编排 → Spring AI Alibaba Graph
- **长期运行 / 多租户 / 沙箱执行 / 持续记忆** → AgentScope Java HarnessAgent ⭐

### 和 Solon AI Harness 的"运行时层之争"

2026 年 Java AI Agent 框架三足鼎立：

| 框架 | 出品 | 特点 | 适用 |
|---|---|---|---|
| **AgentScope Java** | 阿里 | 主打 Harness、企业分布式、多租户 | 中大型企业、阿里系 |
| **Solon AI Harness** | 杭州无耳（Solon 作者） | 轻量运行时、Solon 生态绑定 | 中小项目、Solon 用户 |
| **Spring AI Alibaba Agent Framework** | 阿里 + Spring | Spring 生态、ReactAgent + Graph | Spring 全家桶 |

> 注意：Spring AI Alibaba 和 AgentScope Java **都是阿里出的**，但定位不同——前者是 Spring 生态的 Agent 编排，后者是更下沉的 Harness 驾驭层。两个团队不同战略产品，可以互相组合用。

---

## 六、典型应用场景对照

| 场景 | 代表产品 | 关键诉求 | 推荐配置 |
|------|----------|----------|----------|
| **个人代理 Agent** | OpenClaw 类 | 持续记忆、本地 Shell、工作区即配置 | 本机 + Shell 模式 |
| **企业级数据服务** | DataAgent / SRE Agent | 沙箱隔离、多轮状态恢复、子 Agent 并行 | 沙箱模式 |
| **企业在线服务** | 淘天交易 Agent / 客服 Agent | 默认安全边界、多实例共享记忆 | 远端共享存储模式 |

**核心卖点**：**写一套 Agent 逻辑，按需切换形态**——通过配置而非改代码。

---

## 七、技术选型决策树（面试可用）

```
你的 Java AI 应用需要做什么？
│
├─ 单轮问答 / 简单 RAG
│   └─→ Spring AI 直接上，别过度设计
│
├─ 工具调用 / ReAct
│   └─→ Spring AI + Function Calling
│
├─ 多步流程 + 条件分支 + HITL
│   └─→ Spring AI Alibaba Graph 或 Flowable + Spring AI
│
├─ 长期运行 + 持续记忆 + 多用户
│   ├─ 个人助手 → AgentScope Java（本机模式）
│   ├─ 企业在线服务 → AgentScope Java（远端模式）
│   └─ 数据/代码 Agent → AgentScope Java（沙箱模式）
│
└─ 跨语言团队 / 想要原汁原味 LangGraph
    └─→ Python LangGraph 微服务 + Java 主系统
```

---

## 八、学习路线

### 短期（不打乱主线）
- [ ] 30 分钟：读 [AgentScope Java 官网](https://java.agentscope.io) 概览 + Quick Start
- [ ] 1 小时：跑通 `agentscope-examples/harness-example/QuickstartExample`
- [ ] 30 分钟：能在面试时讲清楚 "Harness 是什么 / 解决什么 / 和 Spring AI 什么关系"

### 中期（上岗 2-3 个月后）
- [ ] 用 Workspace + 本机模式实现一个**个人 Coding Agent**（替代/补充 Claude Code）
- [ ] 跟踪 1.1.0 之后的版本演进（重点关注 sandbox 实现细节、记忆压缩算法）
- [ ] 对比阅读：AgentScope Python 版 vs Java 版的设计差异

### 长期（6 个月+）
- [ ] 真做企业 Agent 时，把它作为**多租户 + 沙箱**的标准底座评估
- [ ] 写一篇深度博客：**"为什么 2026 年 Java Agent 工程师必须懂 Harness"**
- [ ] 关注是否有"Spring AI + AgentScope Java 整合 Starter"出现（机会窗口）

---

## 九、可探索的实验项目

> 上岗后挑一个做，**每个都是高质量博客素材**。

1. **🟢 入门**：用 HarnessAgent + 本机模式做一个**带长期记忆的命令行助手**
2. **🟢 入门**：把现有的 Spring AI ReAct Agent 迁移到 HarnessAgent，对比代码量
3. **🟡 进阶**：用沙箱模式做一个**Java 版 Coding Agent**（参考 OpenClaw）
4. **🟡 进阶**：用远端模式 + Redis 做一个**多副本客服 Agent**，验证状态共享
5. **🔴 高阶**：做一个**Spring Boot Starter for AgentScope**——把它的 HarnessAgent 适配到 Spring Bean 体系
6. **🔴 高阶**：评测对比 AgentScope Java vs Solon AI Harness vs Spring AI Alibaba Agent Framework，写技术报告

---

## 十、为什么这是机会

> **2026 年 Java AI 圈的下一个红利窗口：Harness 工程化基础设施。**

- **时机**：1.1.0 刚发布（2026-05-15），生态尚未沉淀，社区位置空着
- **趋势**：Harness Engineering 是 2026 年 AI 圈的共识方向（Thoughtworks / OpenAI / Anthropic 都在公开实践）
- **企业拉力**：多租户、沙箱、长期记忆是企业 Agent 的硬需求，Spring AI 不解决
- **个人品牌**：现在写 AgentScope Java 的最佳实践博客 / Spring 整合 Starter，**有机会成为 Java AI 圈"Harness 派"的早期声音**

---

## 十一、关键资源

### 官方
- [AgentScope Java 官网](https://java.agentscope.io)
- [GitHub `agentscope-ai/agentscope-java`](https://github.com/agentscope-ai/agentscope-java)
- [Harness 概览文档（中文）](https://github.com/agentscope-ai/agentscope-java/blob/main/docs/zh/harness/overview.md)
- [Filesystem 文档](https://github.com/agentscope-ai/agentscope-java/blob/main/docs/zh/harness/filesystem.md)

### 发布文章
- 阿里技术 · [《首个 Java Harness Framework 来了｜AgentScope 把 OpenClaw 带到企业分布式场景》](https://news.qq.com/rain/a/20260515A02FZG00)（2026-05-15）
- Alibaba Cloud Blog · [The First Java Harness Framework Is Here](https://www.alibabacloud.com/blog/the-first-java-harness-framework-is-here-%7C-agentscope-brings-openclaw-to-enterprise-distributed-scenarios_603139)
- 阿里云开发者社区 · [Harness Agent：2026 年 Java AI Agent 开发的终极框架](https://developer.aliyun.com/article/1727711)

### 概念铺垫（Harness Engineering）
- Thoughtworks · Birgitta Böckeler · Martin Fowler 专栏 "Harness Engineering"（2026-04-02）
- [《2026 年，AI 编程 Agent 的真正分水岭——Harness 详解》](https://cloud.tencent.com/developer/article/2653784)
- [《一文讲透 Harness：AI 从"聪明"到"靠谱"的关键跃迁》](https://cloud.tencent.cn/developer/article/2654873)

### 横向对比
- [《agentscope-harness vs solon-ai-harness：Java 智能体「运行时层」的竞赛》](https://www.cnblogs.com/noear/p/20030725)
- [Spring AI Alibaba Agent Framework](https://github.com/alibaba/spring-ai-alibaba/tree/main/spring-ai-alibaba-agent-framework)

---

## 📝 备忘

- **不要现在 all-in**——主线仍是 Spring AI 基础 + RAG，先把岗位拿下
- **保持高频追踪**：1.1.0 是首发版本，预计未来半年版本演进会很快
- 上岗后遇到"长期记忆 / 多租户 / 沙箱执行"需求时，**优先回来翻这份文档做技术选型**
- 每 3 个月回顾：版本到几了？社区案例多了吗？Spring 生态有整合方案了吗？

---

## 🔗 相关链接

- ⬆️ [阶段 6 · 持续提升](./README.md)
- 📋 [Java 版 LangGraph（图编排层）](./topic-java-langgraph.md)（与本文互补：编排 vs 驾驭）
- 📋 [Go 语言的企业级 AI 应用现状](./topic-go-ai-stack.md)（跨语言视角）
