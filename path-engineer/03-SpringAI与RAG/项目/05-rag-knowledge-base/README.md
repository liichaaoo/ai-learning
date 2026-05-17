# 05-rag-knowledge-base · 企业 RAG 知识库（Week 5-6 简历项目）⭐

> 配套教程：[Week 5-6 · 企业 RAG 知识库](../../Week5-6-企业RAG知识库/README.md)

---

## 🎯 项目目标

**这是阶段 3 的灵魂项目，简历核心。**

把 04-rag-mini 升级为**生产级**：

- 多租户（部门 / 用户隔离）
- 异步入库 + 进度查询
- 多轮对话 + 历史记忆
- 多模型路由 + 降级
- Token 统计 + 成本告警
- Docker 一键部署
- 简单前端
- **GitHub 开源 + 技术博客**

---

## 🛠 技术栈

| 类别 | 选型 |
|------|------|
| 框架 | Spring Boot 3 + Spring AI 1.0 |
| 模型 | 通义千问 / GPT-4o / Ollama（多模型路由）|
| 向量库 | Milvus 2.4 |
| 数据库 | MySQL 8.4（用户/会话/计费）+ Flyway |
| 缓存 | Redis 7（会话历史 / 答案缓存）|
| 队列 | RabbitMQ（异步入库）|
| 解析 | Apache Tika 2.9 |
| 鉴权 | Spring Security 6 + JWT |
| 部署 | Docker Compose / GitHub Actions |
| 压测 | k6 |

---

## 📁 项目结构（参考）

```
05-rag-knowledge-base/
├── README.md                       ← GitHub 入口（必须有架构图、性能数据、demo 视频）
├── pom.xml
├── Dockerfile                       ← Week 5-6 阶段 ⑧ §1
├── docker-compose.yml               ← Week 5-6 阶段 ⑧ §2
├── docs/
│   ├── architecture.png             ← ⭐ 必有
│   ├── 调优实验报告.md
│   └── api.md
├── eval/
│   ├── eval-set.yaml                ← ≥ 30 题
│   └── results-2025xxxx.csv
├── scripts/
│   ├── load-test.js                 ← k6 脚本
│   └── seed-docs.sh
├── frontend/                         ← 简单前端（任选，单文件 HTML 也行）
└── src/main/
    ├── java/com/yourname/rag/
    │   ├── KbApplication.java
    │   ├── controller/   (Auth / Doc / Chat / Admin)
    │   ├── service/
    │   │   ├── auth/                 ← 阶段 ① 用户系统
    │   │   ├── ingestion/            ← 阶段 ② 异步入库
    │   │   ├── retrieval/            ← Week 3-4 复用
    │   │   ├── chat/                 ← 阶段 ③④
    │   │   │   └── advisor/
    │   │   │       ├── CitationAdvisor.java
    │   │   │       └── UsageRecorderAdvisor.java
    │   │   ├── routing/              ← 阶段 ⑤ 多模型路由
    │   │   └── billing/              ← 阶段 ⑥ Token + 告警
    │   ├── domain/                   ← JPA Entity
    │   ├── repository/
    │   ├── config/
    │   └── infra/                    ← Milvus / Redis / OSS
    └── resources/
        ├── application.yml
        ├── application-prod.yml
        ├── db/migration/             ← Flyway V1__init.sql 等
        └── prompts/
```

---

## 🚀 一键启动

```bash
git clone <your-repo>
cd 05-rag-knowledge-base
cp .env.example .env  # 填 DASHSCOPE_API_KEY 等
docker compose up -d

# 等所有服务 healthy 后
open http://localhost:8080
```

---

## 📊 简历目标数字（边做边记）

| 指标 | 目标 |
|------|------|
| Top-3 召回率 | 90%+（30 题评测）|
| 单实例 P95 延迟 | < 1.6s |
| QPS | 50+ |
| 月度成本节省 | ~40%（路由）|
| 文档量 | 200+ 篇 |
| GitHub Star | 1+（自己也算）|

---

## 📝 9 阶段进度自检

- [ ] [① 项目骨架 + 数据库](../../Week5-6-企业RAG知识库/01-项目骨架与数据库.md)
- [ ] [② 异步入库与进度](../../Week5-6-企业RAG知识库/02-异步入库与进度.md)
- [ ] [③ 检索与流式问答](../../Week5-6-企业RAG知识库/03-检索与流式问答.md)
- [ ] [④ 多轮对话与记忆](../../Week5-6-企业RAG知识库/04-多轮对话与记忆.md)
- [ ] [⑤ 多模型路由](../../Week5-6-企业RAG知识库/05-多模型路由.md)
- [ ] [⑥ Token 统计与成本](../../Week5-6-企业RAG知识库/06-Token统计与成本.md)
- [ ] [⑦ 评测与调优](../../Week5-6-企业RAG知识库/07-评测与调优.md)
- [ ] [⑧ 部署与前端](../../Week5-6-企业RAG知识库/08-部署与前端.md)
- [ ] [⑨ 压测与开源](../../Week5-6-企业RAG知识库/09-压测与开源.md)

---

## 🎤 完成后

1. ✅ GitHub 开源 + README 完整
2. ✅ 写技术博客（思否 / 掘金 / 公司内部）
3. ✅ 录 5-30 分钟演示视频
4. ✅ 简历更新（含 GitHub 链接 + 数字）
5. ✅ 把项目链接补到 [`../../../05-简历与面试/简历/`](../../../05-简历与面试/简历/)

---

## 🔗 相关链接

- ⬆️ [Week 5-6 总览](../../Week5-6-企业RAG知识库/README.md)
- 📋 [对标简历参考](../../../05-简历与面试/简历/对标简历参考.md)
- 📦 [上一项目：04-rag-mini](../04-rag-mini/)
