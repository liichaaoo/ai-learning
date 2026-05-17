# Week 3-4 · Agent 简历加分项目（4 周）⭐⭐

> 📅 阶段 4 第三、四周（共 ~10 个工作日）
> 🎯 **目标**：做出一个**简历"加分项目"**——和阶段 3 的 RAG 主项目互补，证明你能做"主动型" AI
> 💎 价值：**面试官最爱看的就是"你做过 Agent 项目"**——目前市面上能讲清的人很少

---

## 🎯 三选一

> **按你的兴趣 + 业务背景选 1 个**，4 周内做完一个比做半个三个强。

### 选项 A：AI Code Reviewer ⭐ 默认推荐（Java 工程师本命）

```
能力：监听 GitHub / 工蜂 PR Webhook，自动拉代码 → LLM 审查 → 留评论
难度：⭐⭐⭐
亮点：自动化 / 多角色 Agent（语法/安全/性能） / 团队真能用上
```

### 选项 B：智能数据分析 Agent

```
能力：自然语言 → SQL → 执行 → 解读 + 图表
难度：⭐⭐⭐⭐
亮点：NL2SQL / Function Calling / 数据可视化
```

### 选项 C：智能运维 Agent

```
能力：日志/指标分析 → 故障定位 → 触发自动修复
难度：⭐⭐⭐⭐
亮点：多工具协同（K8s / Prometheus / 链路追踪）/ 生产实用
```

---

## 🗓️ 10 天实施计划（以选项 A 为模板，B/C 类比即可）

| 阶段 | 任务 | 时间 | 任务卡 |
|------|------|------|--------|
| ① | 项目骨架 + Webhook 接入 | 1 天 | [📖](./01-项目骨架与Webhook.md) |
| ② | Git 操作 + 代码拉取 | 1 天 | [📖](./02-Git与代码拉取.md) |
| ③ | 单 Agent 审查器（先跑通主流程）| 1.5 天 | [📖](./03-单Agent审查器.md) |
| ④ | Multi-Agent 升级（语法/安全/性能）| 1.5 天 | [📖](./04-MultiAgent审查器.md) |
| ⑤ | 评论回写 + 流程闭环 | 1 天 | [📖](./05-评论回写与闭环.md) |
| ⑥ | 工程化：限流 / 监控 / 缓存 | 1.5 天 | [📖](./06-工程化护城河.md) |
| ⑦ | 安全：Prompt 注入防御 + 密钥管理 | 1 天 | [📖](./07-安全与PromptInjection.md) |
| ⑧ | 评测集 + Docker 部署 + 开源 | 1.5 天 | [📖](./08-评测部署与开源.md) |

> 💡 **首次实施推荐路径**：阶段 ①②③⑤⑧ 是必做主线；④⑥⑦ 是简历亮点。**先把主线跑通**。

---

## 📦 项目目录（参考 / 选项 A）

```
项目/08-ai-code-reviewer/
├── README.md                       ← GitHub 入口（架构图/演示视频/数字）
├── pom.xml
├── Dockerfile + docker-compose.yml
├── docs/
│   ├── architecture.png
│   └── 评测报告.md
├── eval/
│   └── pr-test-set/               ← 真实 PR 样例 + 期望反馈
└── src/main/
    └── java/com/yourname/reviewer/
        ├── ReviewerApplication.java
        ├── webhook/GitHubWebhookController.java
        ├── git/GitOperationService.java
        ├── agent/
        │   ├── ReviewOrchestrator.java
        │   ├── SyntaxReviewer.java        ← Agent 1
        │   ├── SecurityReviewer.java      ← Agent 2
        │   └── PerformanceReviewer.java   ← Agent 3
        ├── comment/GitHubCommentService.java
        ├── safety/PromptInjectionGuard.java
        └── infra/RedisRateLimiter.java
```

---

## 🎯 简历亮点数字目标

| 指标 | 目标 |
|------|------|
| 处理速度 | 单 PR < 30s |
| 准确率 | 评测集上 80%+ 真正发现问题 |
| 误报率 | < 20% |
| Multi-Agent 提升 | 比单 Agent 多识别 X% 问题 |
| 覆盖语言 | Java / Python / TypeScript |
| 已审 PR | 演示账号能看到 50+ PR 真实评论 |

---

## 📝 简历叙述模板

```markdown
**AI Code Reviewer [Java / LangChain4j / Multi-Agent]**（个人项目，开源 GitHub）

- 设计基于 LangChain4j 的多角色 Code Review Agent，监听 GitHub Webhook
  自动审查 PR 并留评论，覆盖语法/安全/性能 3 个维度。
- **Multi-Agent 协作架构**：3 个专家 Agent 并行审查，
  相比单 Agent 多识别 35% 潜在问题（基于 50 个真实 PR 评测集）。
- 实现 **Prompt Injection 防御** + **LLM Output Validation**，
  攻击样本拦截率 95%+。
- **工程化能力**：Redis 限流 / 缓存 / 多模型路由（GPT-4o 复杂代码、qwen-plus 简单代码）
  / Prometheus + Grafana 监控。
- 单 PR 平均审查时间 < 30s，月成本 ~ $X。
- GitHub: github.com/yourname/ai-code-reviewer
```

---

## ✅ 通关验收

完成项目 = 阶段 4 通关：

- [ ] 项目能 `docker compose up` 一键启动
- [ ] 给一个真 PR 能收到 AI 评论
- [ ] Multi-Agent 三角色都能跑（哪怕初级版本）
- [ ] Prompt Injection 测试用例能挡住
- [ ] 评测集 ≥ 30 个 PR
- [ ] **GitHub 开源** + README 含演示截图
- [ ] 简历更新（数字 + 链接 + GIF）
- [ ] 写一篇技术博客

---

## 🚦 重要提醒

### 1. 不要追求"工业级 LGTM"

阶段 4 的项目是**简历加分项**，不是要替代 Sonar。**80 分流畅 demo > 100 分卡半年**。

### 2. 选 A 用 GitHub 不用工蜂

简历给外部看时，工蜂链接不通用。建议本地 mock + 公开演示在 GitHub。

### 3. 阶段 3 RAG 项目优先级 > 阶段 4

如果时间紧，**先确保阶段 3 RAG 项目质量**，阶段 4 可以做"小而美"版本。

### 4. 写笔记最值钱

阶段 4 结束至少写：
- 《ReAct 详解》
- 《MCP 协议》
- 《Prompt Injection 防御》⭐
- 《LangChain4j 入门》

---

## 🔗 8 个阶段任务卡

| 阶段 | 任务卡 |
|------|--------|
| ① | [项目骨架与 Webhook](./01-项目骨架与Webhook.md) |
| ② | [Git 与代码拉取](./02-Git与代码拉取.md) |
| ③ | [单 Agent 审查器](./03-单Agent审查器.md) |
| ④ | [Multi-Agent 审查器](./04-MultiAgent审查器.md) |
| ⑤ | [评论回写与闭环](./05-评论回写与闭环.md) |
| ⑥ | [工程化护城河](./06-工程化护城河.md) |
| ⑦ | [安全与 Prompt Injection](./07-安全与PromptInjection.md) |
| ⑧ | [评测部署与开源](./08-评测部署与开源.md) |

---

## 🔗 相关链接

- ⬆️ [阶段 4 总览](../README.md)
- ⬅️ [Week 2 · Agent 设计模式](../Week2-Agent设计模式/README.md)
- 📦 [项目骨架 08-ai-code-reviewer](../项目/08-ai-code-reviewer/)
- 📋 [对标简历参考](../../05-简历与面试/简历/对标简历参考.md)
