# Week 5-6 · 企业 RAG 知识库（简历核心项目）⭐⭐⭐

> 📅 **2 周 / 9-12 个有效工作日**
> 🎯 **核心目标**：把 Week 4 的 mini-RAG **升级为简历级生产项目**——开源、有数字、有压测、能讲 30 分钟
> 💰 **价值**：这是 6 个月规划里"涨薪 30%"的核心底气

---

## 🎉 你即将完成的项目

```
项目名：enterprise-rag-knowledge-base（建议名，可改）
位置：项目/05-rag-knowledge-base/
开源：GitHub（必须）+ 技术博客 1 篇

最终能力：
✅ 多租户（按部门 / 按用户隔离知识库）
✅ 文档上传 → 异步分片 → 入库（含进度查询）
✅ 流式问答 + 来源引用（带页码、可点击）
✅ 多轮对话历史 + 上下文记忆
✅ 多模型路由（GPT / 通义 / Ollama 按场景）
✅ Token 用量统计 + 成本告警
✅ 检索调优：分片对比、混合检索、Reranker
✅ Docker Compose 一键部署
✅ 简单前端（React / Vue / 甚至 Vanilla 都行）
✅ 性能压测报告 + 评测集（至少 30 题）
```

---

## 🪜 学习起点

完成 Week 1-4 后你已经具备：

- ✅ Spring AI ChatClient / Tools / Advisor（Week 1-2）
- ✅ Embedding + Milvus + 混合检索（Week 3）
- ✅ ETL Pipeline + RAG 完整闭环（Week 4）

> 💡 这意味着：**Week 5-6 90% 是工程化和打磨——技术上没有"全新概念"了**。剩下的就是把活干漂亮。

---

## 🗓️ 12 天实施计划

> 时间是参考；做到 90 分胜过 100% 完成。

| 阶段 | 任务 | 时间 | 可交付物 |
|------|------|------|---------|
| ① | 项目骨架 + 数据库设计 + 用户系统 | 1.5 天 | [📖 阶段 1](./01-项目骨架与数据库.md) |
| ② | 文档上传 + 异步入库 + 进度查询 | 1.5 天 | [📖 阶段 2](./02-异步入库与进度.md) |
| ③ | 检索 + 流式问答 + 来源引用 | 1.5 天 | [📖 阶段 3](./03-检索与流式问答.md) |
| ④ | 多轮对话 + 历史记忆 | 1 天 | [📖 阶段 4](./04-多轮对话与记忆.md) |
| ⑤ | 多模型路由 + 降级 | 1 天 | [📖 阶段 5](./05-多模型路由.md) |
| ⑥ | Token 统计 + 成本告警 | 1 天 | [📖 阶段 6](./06-Token统计与成本.md) |
| ⑦ | 评测集 + 检索调优 | 1 天 | [📖 阶段 7](./07-评测与调优.md) |
| ⑧ | Docker 一键部署 + 简单前端 | 1.5 天 | [📖 阶段 8](./08-部署与前端.md) |
| ⑨ | 性能压测 + GitHub + 博客 | 1 天 | [📖 阶段 9](./09-压测与开源.md) |

> 📂 **9 个阶段文档**：先放一份占位骨架（本周 5-6 是"长期项目"，不强求一次性把 9 个 .md 都打满，**优先保证主 README + 阶段 1/3/9 这三篇关键节点**——其他随做随写）。

---

## 📦 项目最终目录（参考）

```
05-rag-knowledge-base/
├── README.md                         ← 项目说明 + 演示截图 + 简历素材
├── docker-compose.yml                ← 一键起 Milvus / Redis / MySQL
├── pom.xml
│
├── docs/                             ← 文档与图
│   ├── architecture.png              ← 架构图（必有）
│   ├── api.md
│   └── 调优实验报告.md                ← Week 4 + 阶段 7 的实验
│
├── eval/                             ← 评测集
│   ├── eval-set.yaml                 ← 30+ 测试题
│   └── results-2025xxxx.csv
│
├── src/main/
│   ├── java/com/yourname/rag/
│   │   ├── KbApplication.java
│   │   ├── controller/
│   │   │   ├── AuthController.java
│   │   │   ├── DocController.java
│   │   │   ├── ChatController.java
│   │   │   └── AdminController.java
│   │   ├── service/
│   │   │   ├── auth/
│   │   │   ├── ingestion/            ← 入库流水线（异步）
│   │   │   │   ├── DocumentParser.java
│   │   │   │   ├── ChunkingService.java
│   │   │   │   ├── EmbeddingService.java
│   │   │   │   └── IngestionWorker.java
│   │   │   ├── retrieval/
│   │   │   │   ├── HybridSearchService.java
│   │   │   │   └── RerankService.java
│   │   │   ├── chat/
│   │   │   │   ├── RagService.java
│   │   │   │   ├── ChatHistoryService.java
│   │   │   │   └── advisor/
│   │   │   │       ├── CitationAdvisor.java
│   │   │   │       └── TokenStatsAdvisor.java
│   │   │   ├── routing/
│   │   │   │   └── ModelRouter.java
│   │   │   └── billing/
│   │   │       ├── UsageRecorder.java
│   │   │       └── CostAlertService.java
│   │   ├── domain/                   ← JPA 实体
│   │   ├── repository/
│   │   ├── config/
│   │   └── infra/                    ← Milvus / Redis / OSS 等
│   └── resources/
│       ├── application.yml
│       ├── application-prod.yml
│       ├── db/migration/             ← Flyway 脚本
│       └── prompts/
│
├── frontend/                         ← 简单前端（任选）
│   ├── README.md
│   └── ...
│
└── scripts/
    ├── load-test.sh                  ← 压测脚本
    └── seed-docs.sh                  ← 一键灌测试文档
```

---

## 🏗️ 系统架构图（必画）

> 简历项目的"灵魂截图"——务必画一张放到 `docs/architecture.png`。

```
              ┌──────────────┐
              │   前端（H5/  │
              │   桌面端）    │
              └──────┬───────┘
                     │ HTTP / SSE
              ┌──────▼───────┐
              │ Spring Boot  │
              │ + Spring AI  │
              ├──────────────┤
              │ Auth(JWT) ──►│  MySQL
              │ Doc Ingest───┼─►│ MySQL ─► RabbitMQ ─► IngestionWorker
              │ Chat Service │       │                 │
              │ Model Router │       │                 ▼ Embedding API
              │ Cost Tracker │       │           Milvus
              └──────┬───────┘       │
                     │               ▼
                     ▼          ChatHistory(Redis)
              ┌────────────┐
              │ LLM 网关    │
              │ ChatModel   │── 通义千问
              │             │── GPT-4o
              │             │── Ollama 本地
              └─────────────┘
```

---

## 🎯 简历亮点埋点速查（边做边记）⭐

> 这一节最重要——**每完成一个阶段，回来对照、记录数字**。

### 量化指标（数字越具体越好）

| 维度 | 怎么得到 | 示例 |
|------|---------|------|
| **QPS / 延迟** | k6 / ab / wrk 压测 | 单实例 80 QPS，P95 1.2s |
| **召回率提升** | 阶段 7 评测集对比 | 混合检索使 Top-3 召回率从 65% → 90% |
| **Token 成本节省** | 路由策略 | 多模型路由后月度推理成本节省 ~40% |
| **首字延迟** | 流式接口的 TTFB | 平均首字 <800ms |
| **吞吐量** | 异步入库 + 批量 embed | 入库吞吐 1500 chunks/min |
| **多租户隔离** | metadata 过滤 | 支持 N 个独立知识库租户 |
| **故障恢复** | 主备切换演示 | 主模型不可用时 200ms 切备用，无业务感知 |
| **覆盖率** | 测试集 + 文档量 | 30 题人工评测 / 200+ 内部文档 |

### 简历叙述模板（直接拷贝改）

```markdown
**企业 RAG 知识库系统 [Java / Spring AI / Milvus]**（个人项目，开源 GitHub）

- 主导设计基于 Spring AI + Milvus 的企业级 RAG 知识库系统，
  支持 PDF/Word/Markdown 等格式文档检索问答，覆盖 200+ 内部文档。
- 实现 **混合检索（向量召回 + BM25 + Rerank）**，相比纯向量检索
  Top-3 召回率从 65% 提升至 90%（基于 30 题人工评测集）。
- 设计 **多模型路由策略**（通义千问 / GPT-4o / Ollama），
  按场景成本/质量自动选择，**月度推理成本节省 ~40%**。
- 基于 Spring AI Advisor 链实现 **Token 用量统计、成本告警、
  审计日志**等横切能力。
- 单实例 P95 首字延迟 < 800ms，支撑 80+ QPS（k6 压测）；
  Docker Compose 一键部署。
- 链接：github.com/yourname/enterprise-rag-kb
```

---

## ✅ 通关验收清单

完成本项目 = 阶段 3 通关：

- [ ] 项目能 `docker compose up` 一键启动
- [ ] 完整跑通：注册 → 上传 → 入库 → 提问 → 流式回答 + 引用
- [ ] 多用户隔离（用 metadata 过滤验证）
- [ ] 异步入库（上传大文件不阻塞，可查进度）
- [ ] 多模型路由（至少 2 个模型 + 1 个降级演示）
- [ ] Token 用量记录到 DB（能查每天 / 每用户消耗）
- [ ] 评测集 ≥ 30 题，跑出对比数据
- [ ] 性能压测报告（k6 / wrk 截图）
- [ ] **GitHub 开源**（README 含演示截图 / 演示视频链接）
- [ ] **写一篇技术博客**（推荐：思否 / 掘金 / 公司内部）
- [ ] 准备好 **30 分钟项目演示**（视频或现场都行）

---

## 🚦 重要提醒

### 1. 不要追求"完美"，追求"能讲"

简历项目的核心不是"代码多完美"，而是**"你能用 30 分钟把它讲漂亮"**。
有 80% 完成度 + 10 分钟流畅讲解 > 100% 完成度 + 5 分钟磕磕绊绊。

### 2. 数字 > 文字

简历上一句"提升性能"等于没说。**任何亮点都要附数字**。

### 3. 边做边写 README

每完成一个阶段，立刻在项目 README 里更新一段——**别等到最后**。

### 4. GitHub 提交节奏

按阶段提交 commit：

```
git commit -m "feat: 阶段 1 项目骨架 + 用户系统"
git commit -m "feat: 阶段 2 异步入库流水线"
...
```

**面试官会看 commit history**——节奏漂亮 = 加分。

### 5. 先跑通主流程再优化

阶段 1-3 是骨架，**先把它们打通**，别在阶段 1 就开始优化。

---

## 🔗 9 个阶段任务卡（按需深入）

| 阶段 | 任务卡 | 预计时间 |
|------|--------|---------|
| ① | [项目骨架与数据库](./01-项目骨架与数据库.md) | 1.5 天 |
| ② | [异步入库与进度](./02-异步入库与进度.md) | 1.5 天 |
| ③ | [检索与流式问答](./03-检索与流式问答.md) | 1.5 天 |
| ④ | [多轮对话与记忆](./04-多轮对话与记忆.md) | 1 天 |
| ⑤ | [多模型路由](./05-多模型路由.md) | 1 天 |
| ⑥ | [Token 统计与成本](./06-Token统计与成本.md) | 1 天 |
| ⑦ | [评测与调优](./07-评测与调优.md) | 1 天 |
| ⑧ | [部署与前端](./08-部署与前端.md) | 1.5 天 |
| ⑨ | [压测与开源](./09-压测与开源.md) | 1 天 |

> 💡 **首次实施建议**：**阶段 1 / 3 / 9 是必做**，其他可以"先做框架后填细节"——9 篇任务卡都已开放，**按你的进度查就行**。

---

## 🎤 完成后的下一步

1. ✅ GitHub 开源 + README 写好
2. ✅ 写技术博客（包含架构图、调优实验、踩坑记录）
3. ✅ 录 5-30 分钟演示视频
4. ✅ 把上面"简历叙述模板"改写成自己的版本
5. 🟦 进入 [阶段 4 · Agent 与工程化](../../04-Agent与工程化/README.md)

> 🎯 **完成本阶段 = 拿到第一个能让面试官眼前一亮的项目**。**简历投出去之前，先回头对照 [`../../05-简历与面试/简历/对标简历参考.md`](../../05-简历与面试/简历/对标简历参考.md) 检查数字埋点**。

---

## 🔗 相关链接

- ⬆️ [阶段 3 总览](../README.md)
- ⬅️ [Week 4 · RAG 核心机制](../Week4-RAG核心机制/README.md)
- 📂 [项目骨架 05-rag-knowledge-base](../项目/05-rag-knowledge-base/)
- 📋 [对标简历参考（数字怎么埋）](../../05-简历与面试/简历/对标简历参考.md)
- 🎓 [path-research 对应章节（可选深入）](../../../path-research/README.md)
