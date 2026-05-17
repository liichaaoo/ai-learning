# 阶段 4 · Agent 与工程化（4 周）

> 🎯 **目标**：从"调 LLM API"升级到"让 LLM 自主决策 + 调用工具" + 一个简历加分项目
>
> ⏱️ **周期**：4 周
>
> 🧭 **权重**：⭐⭐⭐⭐⭐（高级岗核心 + 简历差异化加分）

---

## 📌 核心原则

> **RAG 是"被动读资料回答"，Agent 是"主动思考 + 行动"。**
>
> 阶段 3 的 RAG 项目是简历"主项目"；阶段 4 的 Agent 项目是简历"加分项目"——两个项目互补，证明你能做不同形态的 LLM 应用。

> 💎 **做项目前先看一眼**：[`../05-简历与面试/简历/对标简历参考.md`](../05-简历与面试/简历/对标简历参考.md)

---

## 🗓️ 4 周计划

### Week 1：LangChain4j + Agent 基础 ✅ 已开放

> 📘 **完整 5 天教程** → [`Week1-LangChain4j基础/README.md`](./Week1-LangChain4j基础/README.md)
> 📦 **代码骨架** → [`项目/06-langchain4j-hello/`](./项目/06-langchain4j-hello/)

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | LangChain4j Hello World | [📖 Day1](./Week1-LangChain4j基础/Day1-LangChain4j-HelloWorld.md) |
| Day 2 | AiServices 声明式 API ⭐ | [📖 Day2](./Week1-LangChain4j基础/Day2-AiServices声明式.md) |
| Day 3 | 三种 Memory 机制（含 Redis 持久化）| [📖 Day3](./Week1-LangChain4j基础/Day3-Memory机制.md) |
| Day 4 | Tools 进阶（参数校验 / 异常 / 选错兜底）| [📖 Day4](./Week1-LangChain4j基础/Day4-Tools进阶.md) |
| Day 5 | 整合 Demo：你的第一个 Agent ⭐ | [📖 Day5](./Week1-LangChain4j基础/Day5-第一个Agent.md) |

📦 **产出**：`项目/06-langchain4j-hello/` —— AiService + Memory + 3 个 Tool 的 mini Agent

---

### Week 2：Agent 设计模式 ⭐ ✅ 已开放

> 📘 **完整 5 天教程** → [`Week2-Agent设计模式/README.md`](./Week2-Agent设计模式/README.md)
> 📦 **代码骨架** → [`项目/07-agent-patterns/`](./项目/07-agent-patterns/)

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | ReAct 模式 ⭐（手撕 + 内置版）| [📖 Day1](./Week2-Agent设计模式/Day1-ReAct模式.md) |
| Day 2 | Plan-and-Execute | [📖 Day2](./Week2-Agent设计模式/Day2-Plan-and-Execute.md) |
| Day 3 | Multi-Agent 协作（三角色研究小组）| [📖 Day3](./Week2-Agent设计模式/Day3-Multi-Agent协作.md) |
| Day 4 | MCP 协议 ⭐ 2026 必会 | [📖 Day4](./Week2-Agent设计模式/Day4-MCP协议.md) |
| Day 5 | 模式对比与自适应 Agent | [📖 Day5](./Week2-Agent设计模式/Day5-模式对比与整合.md) |

📦 **产出**：`项目/07-agent-patterns/` —— 4 种模式 demo + 1 个自适应调度

---

### Week 3-4：⭐ Agent 简历加分项目 ✅ 已开放

> **这是阶段 4 的最终产出，简历加分项目。**
>
> 📘 **完整实施手册** → [`Week3-4-Agent项目/README.md`](./Week3-4-Agent项目/README.md)
> 📦 **代码骨架** → [`项目/08-ai-code-reviewer/`](./项目/08-ai-code-reviewer/)

#### 🎯 三选一

| 选项 | 难度 | 适合 |
|------|------|------|
| **A：AI Code Reviewer** ⭐ 默认推荐 | ⭐⭐⭐ | Java 工程师 |
| B：智能数据分析 Agent | ⭐⭐⭐⭐ | 数据/BI 背景 |
| C：智能运维 Agent | ⭐⭐⭐⭐ | 运维/SRE 背景 |

#### 📅 8 阶段任务卡（以选项 A 为模板）

| 阶段 | 任务 | 任务卡 |
|------|------|--------|
| ① | 项目骨架 + Webhook 接入 | [📖](./Week3-4-Agent项目/01-项目骨架与Webhook.md) |
| ② | Git 与代码拉取 | [📖](./Week3-4-Agent项目/02-Git与代码拉取.md) |
| ③ | 单 Agent 审查器 | [📖](./Week3-4-Agent项目/03-单Agent审查器.md) |
| ④ | Multi-Agent 升级（语法/安全/性能）| [📖](./Week3-4-Agent项目/04-MultiAgent审查器.md) |
| ⑤ | 评论回写 + 流程闭环 | [📖](./Week3-4-Agent项目/05-评论回写与闭环.md) |
| ⑥ | 工程化护城河（限流/缓存/监控）| [📖](./Week3-4-Agent项目/06-工程化护城河.md) |
| ⑦ | 安全与 Prompt Injection 防御 ⭐ | [📖](./Week3-4-Agent项目/07-安全与PromptInjection.md) |
| ⑧ | 评测部署 + GitHub 开源 | [📖](./Week3-4-Agent项目/08-评测部署与开源.md) |

#### 📝 简历亮点写法

> **AI Code Reviewer [Java / LangChain4j / Multi-Agent]**（个人项目，开源 GitHub）
>
> - 设计基于 LangChain4j 的多角色 Code Review Agent，监听 GitHub Webhook 自动审查 PR。
> - **Multi-Agent 协作架构**（3 个专家 Agent 并行：语法/安全/性能），相比单 Agent **多识别 35% 潜在问题**（基于 30 真实 PR 评测集）。
> - 实现 **Prompt Injection 防御** 5 道防线，攻击样本 **拦截率 95%+**（20 攻击样本）。
> - 多模型路由（贵模型管复杂代码，便宜模型管语法），月成本节省 ~ 50%。
> - 单 PR 平均审查 < 30s；Resilience4j 限流 + Redis 缓存 + Prometheus 监控。

---

## 🔧 工程化必修课（贯穿 Week 3-4）

| 维度 | 关键点 | 任务卡 |
|------|--------|--------|
| 流量与成本 | 限流（Resilience4j）/ 缓存（Redis）/ 多模型路由 | [⑥](./Week3-4-Agent项目/06-工程化护城河.md) |
| 安全与合规 | **Prompt Injection 防御** / 输入清洗 / 工具白名单 | [⑦](./Week3-4-Agent项目/07-安全与PromptInjection.md) |
| 监控与可观测 | Prometheus / Grafana / 审计日志 | [⑥](./Week3-4-Agent项目/06-工程化护城河.md) |
| 评测与部署 | 评测集 / Docker 一键 / GitHub 开源 | [⑧](./Week3-4-Agent项目/08-评测部署与开源.md) |

---

## ✅ 阶段完成标准

- [ ] LangChain4j AiServices + Memory + Tools 熟练
- [ ] 能解释 ReAct / Plan-and-Execute / Multi-Agent / MCP
- [ ] 能写一个 MCP Server，并在 Claude Desktop 接入
- [ ] **Agent 项目开源 + 部署运行**
- [ ] Prompt Injection 防御能讲、能演示
- [ ] 项目实现了完整的工程化（限流、监控、安全）
- [ ] **简历更新**：含 GitHub 链接 + 关键数字

---

## 📁 目录结构

```
04-Agent与工程化/
├── README.md ← 你正在看
├── Week1-LangChain4j基础/        ✅（README + 5 Day）
├── Week2-Agent设计模式/          ✅（README + 5 Day）
├── Week3-4-Agent项目/             ✅（README + 8 阶段任务卡）
├── 笔记/
│   ├── LangChain4j入门.md
│   ├── ReAct详解.md
│   ├── MCP协议.md
│   └── PromptInjection防御.md ⭐
└── 项目/
    ├── 06-langchain4j-hello/      (Week 1 产出)
    ├── 07-agent-patterns/         (Week 2 产出)
    └── 08-ai-code-reviewer/ ⭐    (Week 3-4 简历加分项目)
```

---

## ⏭️ 下一阶段

完成本阶段 = **拥有第二个简历项目** → 进入 [阶段 5 · 简历与面试](../05-简历与面试/README.md)

> 🎯 此时你应该：阶段 3 RAG 项目（主项目）+ 阶段 4 Agent 项目（加分项目）+ 4 篇核心笔记 + 7 年 Java 经验。简历底气十足。

---

## 🔗 相关链接

- ⬆️ [path-engineer 主路径](../README.md)
- ⬅️ [阶段 3 · Spring AI 与 RAG](../03-SpringAI与RAG/README.md)
- ➡️ [阶段 5 · 简历与面试](../05-简历与面试/README.md)
- 📋 [对标简历参考](../05-简历与面试/简历/对标简历参考.md)
