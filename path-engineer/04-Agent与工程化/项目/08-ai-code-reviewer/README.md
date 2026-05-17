# 08-ai-code-reviewer · AI 代码审查 Agent（Week 3-4 简历加分项目）⭐

> 配套教程：[Week 3-4 · Agent 项目](../../Week3-4-Agent项目/README.md)

---

## 🎯 项目目标

**简历加分项目**。监听 GitHub PR Webhook，自动审查 + 留评论。

- Multi-Agent 三角色（语法 / 安全 / 性能）
- Prompt Injection 防御 + 攻击样本测试
- 限流 / 缓存 / 多模型路由 / 监控
- Docker 一键部署 + GitHub 开源

---

## 🛠 技术栈

| 类别 | 选型 |
|------|------|
| 框架 | Spring Boot 3 + LangChain4j 0.36 |
| Agent | Multi-Agent + Function Calling |
| 模型 | 通义 qwen-max（贵）+ qwen-plus（便宜）按场景路由 |
| 数据 | Redis 7（缓存 + 限流状态）|
| Git 操作 | GitHub REST API + JGit |
| 韧性 | Resilience4j（限流 + 断路器）|
| 监控 | Micrometer + Prometheus + Grafana |
| 部署 | Docker Compose / GitHub Actions |

---

## 📁 项目结构

```
08-ai-code-reviewer/
├── README.md                       ← GitHub 入口（架构图/性能数据/演示）
├── pom.xml
├── Dockerfile
├── docker-compose.yml
├── docs/
│   ├── architecture.png            ← ⭐ 必有
│   ├── evaluation.md               ← 评测报告
│   ├── security.md                 ← Prompt Injection 防御
│   └── grafana.png                 ← 监控看板截图
├── eval/
│   ├── pr-test-set/                ← 30+ 真 PR 评测样本
│   ├── attack-set/                 ← 20+ 攻击样本
│   └── results-2025xxxx.csv
└── src/main/java/com/yourname/reviewer/
    ├── ReviewerApplication.java
    ├── webhook/GitHubWebhookController.java        ← 阶段①
    ├── git/
    │   ├── GitHubApiService.java                   ← 阶段②
    │   ├── DiffSplitter.java
    │   └── PrValidator.java
    ├── agent/
    │   ├── ReviewOrchestrator.java                 ← 阶段③
    │   ├── single/ReviewAgent.java
    │   ├── multi/
    │   │   ├── SyntaxReviewer.java                 ← 阶段④
    │   │   ├── SecurityReviewer.java
    │   │   ├── PerformanceReviewer.java
    │   │   └── MultiReviewOrchestrator.java
    │   └── adaptive/MultiAgentConfig.java
    ├── comment/GitHubCommentService.java           ← 阶段⑤
    ├── infra/
    │   ├── RedisRateLimiter.java                   ← 阶段⑥
    │   ├── CachedReviewer.java
    │   └── ReviewMetrics.java
    ├── safety/PromptInjectionGuard.java            ← 阶段⑦
    └── eval/EvaluationTest.java                    ← 阶段⑧
```

---

## 📊 简历目标数字

| 指标 | 目标 |
|------|------|
| 真正发现问题率 | 85%+ |
| Multi-Agent 提升 | +30% 问题识别 |
| Prompt Injection 拦截 | 95%+ |
| 单 PR 耗时 P95 | < 35s |
| 月成本节省（vs 全用 qwen-max）| 50%+ |

---

## 🚀 一键启动

```bash
git clone https://github.com/yourname/ai-code-reviewer
cd ai-code-reviewer
cp .env.example .env  # 填 DASHSCOPE_API_KEY / GITHUB_TOKEN / GITHUB_WEBHOOK_SECRET
docker compose up -d

# 配置 GitHub Webhook：
# Payload URL: https://your-domain/webhook/github
# Content-Type: application/json
# Secret: $GITHUB_WEBHOOK_SECRET
# Events: Pull requests
```

---

## 📝 8 阶段进度自检

- [ ] [① 项目骨架 + Webhook](../../Week3-4-Agent项目/01-项目骨架与Webhook.md)
- [ ] [② Git 与代码拉取](../../Week3-4-Agent项目/02-Git与代码拉取.md)
- [ ] [③ 单 Agent 审查器](../../Week3-4-Agent项目/03-单Agent审查器.md)
- [ ] [④ Multi-Agent 审查器](../../Week3-4-Agent项目/04-MultiAgent审查器.md)
- [ ] [⑤ 评论回写与闭环](../../Week3-4-Agent项目/05-评论回写与闭环.md)
- [ ] [⑥ 工程化护城河](../../Week3-4-Agent项目/06-工程化护城河.md)
- [ ] [⑦ 安全与 Prompt Injection](../../Week3-4-Agent项目/07-安全与PromptInjection.md)
- [ ] [⑧ 评测部署与开源](../../Week3-4-Agent项目/08-评测部署与开源.md)

---

## 🎤 完成后

1. ✅ GitHub 开源 + README 完整
2. ✅ 录 5 分钟演示视频 / GIF
3. ✅ 写技术博客
4. ✅ 简历更新（数字 + 链接）
5. ✅ 投出第一份简历

---

## 🔗 相关链接

- ⬆️ [Week 3-4 总览](../../Week3-4-Agent项目/README.md)
- 📋 [对标简历参考](../../../05-简历与面试/简历/对标简历参考.md)
- 📦 [上一项目：07-agent-patterns](../07-agent-patterns/)
