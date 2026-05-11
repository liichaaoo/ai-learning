# 阶段 4 · Agent 与工程化（4 周）

> 🎯 **目标**：掌握 Agent 框架 + MCP 协议 + 生产工程化
>
> ⏱️ **周期**：4 周
>
> 🧭 **权重**：⭐⭐⭐⭐⭐（高级岗核心考察 + 简历加分项目）

---

## 📌 核心原则

> **从"调 LLM API"升级到"让 LLM 自主决策 + 调用工具"。**
>
> RAG 是"被动读资料回答"，Agent 是"主动思考 + 行动"。

---

## 🗓️ 4 周计划

### Week 1：LangChain4j + Agent 基础

- [ ] **LangChain4j 概览**
  - 与 Spring AI 的对比
  - 核心 API：`ChatLanguageModel`、`AiServices`、`Memory`、`Tools`

- [ ] **Memory 机制**
  - `MessageWindowChatMemory`（窗口记忆）
  - `TokenWindowChatMemory`（按 Token 截断）
  - `SummarizingChatMemory`（摘要式长期记忆）

- [ ] **Tools 进阶**
  - 自定义 Tool（`@Tool`）
  - Tool 参数设计
  - Tool 错误处理

#### 📚 资源
- [LangChain4j 官方文档](https://docs.langchain4j.dev/)
- [LangChain4j Examples](https://github.com/langchain4j/langchain4j-examples)

---

### Week 2：Agent 设计模式

- [ ] **ReAct 模式**（Reasoning + Acting）
  - Thought → Action → Observation 循环
  - Spring AI / LangChain4j 怎么实现
  - 与 CoT（Chain-of-Thought）的区别

- [ ] **Plan-and-Execute**
  - 先规划再执行
  - 适合复杂多步任务

- [ ] **Multi-Agent 协作**
  - 角色分工（Researcher / Coder / Reviewer）
  - 通信协议
  - 简单实践

- [ ] **MCP 协议**（Model Context Protocol）
  - Anthropic 主推，2026 标配
  - 与 Function Calling 的区别
  - Spring AI MCP 集成

📦 **产出**：每个模式至少有一个 demo

---

### Week 3-4：⭐ Agent 项目（加分项目）

#### 🎯 三选一（按你兴趣 + 业务背景选）

##### 选项 A：AI Code Reviewer
- 监听 GitHub / 工蜂 PR Webhook
- 自动拉代码 → LLM 审查 → 评论
- 多步骤推理 + 自定义规则
- 可在团队内部署使用

##### 选项 B：智能数据分析 Agent
- 自然语言 → SQL → 执行 → 解读
- 图表自动生成
- 多轮澄清能力

##### 选项 C：智能运维 Agent
- 日志分析 + 告警诊断
- 故障根因推理
- 多工具协同（K8s API、Prometheus、链路追踪）

#### 📅 实施节奏
- Week 3：项目设计 + 核心功能
- Week 4：完善 + 部署 + 文档

---

## 🔧 工程化必修课

无论做哪个项目，都必须实现：

### 1. 流量与成本控制
- [ ] 限流（Token / 用户 / IP）
- [ ] 降级（LLM 异常时 fallback）
- [ ] Token 用量监控 + 告警
- [ ] 多模型路由（高/低成本切换）

### 2. 安全与合规
- [ ] **Prompt 注入防御**（输入校验、System Prompt 约束）
- [ ] 敏感信息脱敏（手机号、身份证、API Key）
- [ ] 内容审核（输出过滤）
- [ ] 用户隔离（多租户）

### 3. 监控与可观测性
- [ ] 关键指标：TTFT（首字延迟）、Token QPS、缓存命中率
- [ ] 接入 Prometheus + Grafana
- [ ] 链路追踪（每次调用的 LLM 路径）
- [ ] 日志脱敏 + 结构化

### 4. 缓存策略
- [ ] Embedding 缓存（同样的文本不重复算）
- [ ] LLM 响应缓存（语义相似命中）
- [ ] 用户会话缓存（Redis）

---

## ✅ 阶段完成标准

- [ ] LangChain4j 能熟练使用 Memory + Tools
- [ ] 能解释 ReAct / Plan-and-Execute / Multi-Agent
- [ ] 知道 MCP 协议是什么、能写一个 MCP Server
- [ ] **Agent 项目开源 + 部署运行**
- [ ] 项目实现了完整的工程化（限流、监控、安全）
- [ ] 能给团队做 60 分钟的"AI Agent 系统设计"分享

---

## 📁 目录结构

```
04-Agent与工程化/
├── README.md
├── 笔记/
│   ├── LangChain4j入门.md
│   ├── ReAct模式详解.md
│   ├── MCP协议.md
│   ├── PromptInjection防御.md
│   └── ...
└── 项目/
    └── 03-ai-agent/   ⭐ (核心)
```

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 5 · 简历与面试](../05-简历与面试/README.md)
