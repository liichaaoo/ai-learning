# Day 5 · Agent 模式对比与整合（决策表 + 综合 demo）

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 4 种模式串起来；写一份"该选哪个 Agent 模式"决策表（笔记）

---

## 0. 心法（5 分钟）

> **Agent 模式不是"哪个最先进"，而是"哪个最匹配你的场景"。**

本周学了 4 种：

```
ReAct                单 Agent + 多工具，走一步看一步
Plan-and-Execute     先规划再执行，适合多步任务
Multi-Agent          多个专家分工
MCP                  上层协议，让工具跨模型/跨应用复用
```

今天就把它们摆在一起对比，并做一个**综合 demo**。

---

## 1. 终极对比表 ⭐（15 分钟）

| 维度 | ReAct | P&E | Multi-Agent | MCP |
|------|-------|-----|-------------|------|
| **本质** | "想-做-看"循环 | "先规划再执行" | 多角色分工 | 工具通信协议 |
| **粒度** | 单步 | 任务 | 任务 | 工具 |
| **延迟** | 低 | 中 | 高 | 取决于工具 |
| **Token** | 中 | **高** | **高** | 低（不直接耗 Token）|
| **调试** | 中 | **易** | **易** | 易 |
| **适合任务** | 简单查询 | 复杂多步 | 创作 / 评审 | 跨应用工具复用 |
| **生产成熟度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐（2026 新晋）|

---

## 2. 决策树（5 分钟）

```
任务能 1-2 步搞定？
  ├─ 是 → 直接 ReAct（LangChain4j 默认）
  └─ 否 → 需要给用户中途进度？
         ├─ 是 → Plan-and-Execute（每步推送）
         └─ 否 → 需要不同"专家视角"？
                ├─ 是 → Multi-Agent
                └─ 否 → 仍然 P&E

另外：
  工具跨应用复用？ → MCP（独立维度，可以叠加任何模式）
```

---

## 3. 几个真实场景配什么模式（10 分钟）

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| AI 客服回答常见问题 | **RAG + ReAct** | 单轮、低延迟 |
| 代码 Review 工具 | **Multi-Agent**（Reader + Reviewer + Suggester）| 多视角 |
| 自动调研报告 | **Plan-and-Execute** | 多步、要进度推送 |
| 智能运维（查日志→分析→操作）| **ReAct** | 边查边定位 |
| 编程助手（Cursor/Cline）| **MCP** + ReAct | 工具市场 |
| 数据分析（NL → SQL → 图表）| **Plan-and-Execute** | 步骤清晰 |
| 法律合同审查 | **Multi-Agent**（条款分析 / 风险评估 / 总结）| 专家分工 |
| 论文综述 | **Multi-Agent** + P&E | 多领域 + 多步骤 |

---

## 4. 综合 Demo：写一个"自适应 Agent"（30 分钟）

> 让一个调度层根据任务复杂度，自动选模式。

### 4.1 任务复杂度分类器

```java
interface Triager {
    @SystemMessage("""
            你是任务复杂度分类器。判断用户任务属于：
            - SIMPLE：1-2 步可完成（查天气/算数/单查询）
            - MULTI_STEP：3+ 步需规划（调研/分析/报告）
            - MULTI_ROLE：需多个专家视角（创作/评审）

            只输出枚举名称，无其他文字。
            """)
    TaskComplexity classify(@UserMessage String task);
}

enum TaskComplexity { SIMPLE, MULTI_STEP, MULTI_ROLE }
```

### 4.2 调度器

```java
@Service
@RequiredArgsConstructor
public class AdaptiveAgent {

    private final Triager triager;
    private final AssistantService reactAgent;       // Week 1 写的
    private final PlanExecutor planAgent;            // Day 2 写的
    private final Orchestrator multiAgent;           // Day 3 写的

    public String handle(String userId, String task) throws Exception {
        TaskComplexity type = triager.classify(task);
        log.info("Task '{}' classified as {}", task, type);

        return switch (type) {
            case SIMPLE     -> reactAgent.chat(userId, task);
            case MULTI_STEP -> planAgent.run(task);
            case MULTI_ROLE -> multiAgent.produceArticle(task);
        };
    }
}
```

### 4.3 测试

```bash
# SIMPLE → ReAct
curl ... -d '{"q":"上海现在几度？"}'

# MULTI_STEP → P&E
curl ... -d '{"q":"调研一下新能源汽车 2024 年市场份额并输出 3 个关键洞察"}'

# MULTI_ROLE → Multi-Agent
curl ... -d '{"q":"写一篇关于量子计算的科普文章，要审稿到 Reviewer 评分 8 分以上"}'
```

观察控制台分类日志 + 不同模式的执行轨迹——**这就是一个"自适应 Agent"**。

> 🎯 **简历亮点**：「实现自适应 Agent 调度层，根据任务复杂度自动选 ReAct / P&E / Multi-Agent，
> 复杂任务成功率从 X% 提升至 Y%」。

---

## 5. 输出本周笔记 3 篇（15 分钟）

> **不写笔记，本周等于白学**。

### 5.1 [`笔记/LangChain4j入门.md`](../../笔记/LangChain4j入门.md)

主要内容：
- AiServices 4 种用法速查
- 三种 Memory 对比
- Tools 进阶心法
- 跟 Spring AI 的混用策略

### 5.2 [`笔记/ReAct详解.md`](../../笔记/ReAct详解.md)

主要内容：
- 三段论原理
- 跟 CoT 的对比
- 手写 ReAct 模板
- 死循环 4 种防御

### 5.3 [`笔记/MCP协议.md`](../../笔记/MCP协议.md)

主要内容：
- 三大对象（Tools/Resources/Prompts）
- Server 怎么写
- Client 怎么接
- 生态现状

### 5.4 [`笔记/PromptInjection防御.md`](../../笔记/PromptInjection防御.md)（高级岗必考）

主要内容：
- 攻击的 5 种形态（直接注入 / 间接注入 / 越狱 / 数据泄露 / 工具滥用）
- 防御 5 招（System 加固 / 输入清洗 / 输出校验 / 工具白名单 / 最小权限）
- 简历亮点写法

---

## 6. 出关验收

跑通这 5 个动作 = Week 2 通过：

- [ ] §1 决策表能默写
- [ ] 4 种模式各跑过一个 demo
- [ ] §4 综合 demo 能自动调度
- [ ] 写出 4 篇笔记
- [ ] 用 30 秒话术解释"为什么 MCP 重要"
- [ ] 录一个 5 分钟视频展示自适应 Agent

---

## ✅ Week 2 通关

恭喜！你已经掌握了 Agent 的全套设计模式。

**下两周（Week 3-4）你要做出一个简历级的 Agent 项目**，三选一：

- AI Code Reviewer（推荐 Java 工程师）
- 智能数据分析 Agent（推荐数据/BI 背景）
- 智能运维 Agent（推荐运维/SRE 背景）

> 🚦 项目选定后，进入 [Week 3-4 实施手册](../Week3-4-Agent项目/README.md)

---

## 🔗 相关链接

- ⬅️ [Day 4 · MCP 协议](./Day4-MCP协议.md)
- ⬆️ [Week 2 总览](./README.md)
- ➡️ [Week 3-4 · Agent 项目](../Week3-4-Agent项目/README.md)
- 📝 [笔记/ReAct详解.md（本周末写）](../../笔记/ReAct详解.md)
