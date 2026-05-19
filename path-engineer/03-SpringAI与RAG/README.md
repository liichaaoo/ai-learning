# 阶段 3 · Spring AI 与 RAG（6 周）⭐ 核心阶段

> 🎯 **目标**：用 Spring AI 搭出一个**简历级**企业 RAG 知识库系统
>
> ⏱️ **周期**：6 周
>
> 🧭 **权重**：⭐⭐⭐⭐⭐（你 80% 面试题来源 + 简历核心项目）

---

## 📌 核心原则

> **这是整个 6 个月规划中最重要的 6 周。**
>
> 这阶段的产出 = 简历的灵魂 = 涨薪 30% 的底气。

不要被前两个阶段的"理论"吸引而延期，**该来阶段 3 就来阶段 3**。

> 💎 **做项目前先看一眼**：[`../05-简历与面试/简历/对标简历参考.md`](../05-简历与面试/简历/对标简历参考.md)
> 这份文档包含派聪明 RAG 项目模板和"项目数字怎么埋"的方法。
> **本阶段每完成一个项目，回去对照那份模板，看自己的指标差在哪**。

---

## 🗓️ 6 周计划

### Week 1：Spring AI 基础 ✅ 已开放

> 📘 **完整 5 天教程** → [`Week1-SpringAI基础/README.md`](./Week1-SpringAI基础/README.md)
> 📦 **代码骨架** → [`项目/01-helloai/`](./项目/01-helloai/)（开箱即用，只需填 API Key）

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | 环境准备 + 申请通义千问 API Key | [📖 Day1](./Week1-SpringAI基础/Day1-环境准备.md) |
| Day 2 | Hello World（跑起第一个 Spring AI）| [📖 Day2](./Week1-SpringAI基础/Day2-HelloWorld.md) |
| Day 3 | 流式响应（SSE，像 ChatGPT）| [📖 Day3](./Week1-SpringAI基础/Day3-流式响应.md) |
| Day 4 | Prompt 工程（System + 模板）| [📖 Day4](./Week1-SpringAI基础/Day4-Prompt工程.md) |
| Day 5 | 结构化输出 + 整合 Demo | [📖 Day5](./Week1-SpringAI基础/Day5-结构化输出与整合.md) |

#### 📚 资源
- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [SpringAI 入门笔记](./笔记/SpringAI入门.md)（已有）
- [Spring AI Examples](https://github.com/spring-projects/spring-ai-examples)

📦 **产出**：`项目/01-helloai/` —— 能跑、能演示、可以写进简历的 Spring AI Hello World

---

### Week 2：Function Calling + 多模型 ✅ 已开放

> 📘 **完整 5 天教程** → [`Week2-FunctionCalling与多模型/README.md`](./Week2-FunctionCalling与多模型/README.md)
> 📦 **代码骨架** → [`项目/02-multi-tools/`](./项目/02-multi-tools/)（含运维助手毕业 Demo）

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | Function Calling 原理 + Hello Tool | [📖 Day1](./Week2-FunctionCalling与多模型/Day1-FunctionCalling原理.md) |
| Day 2 | 多工具协作 + 参数校验 | [📖 Day2](./Week2-FunctionCalling与多模型/Day2-多工具协作.md) |
| Day 3 | 多模型接入（通义 + Ollama）| [📖 Day3](./Week2-FunctionCalling与多模型/Day3-多模型接入.md) |
| Day 4 | 多模型路由策略 + 降级 | [📖 Day4](./Week2-FunctionCalling与多模型/Day4-多模型路由.md) |
| Day 5 | 整合 Demo：智能运维助手 ⭐ | [📖 Day5](./Week2-FunctionCalling与多模型/Day5-整合Demo.md) |

📦 **产出**：`项目/02-multi-tools/` —— AI 运维助手，能查监控、分析问题、执行操作（简历级）

---

### Week 3：向量库 + Embedding ✅ 已开放

> 📘 **完整 5 天教程** → [`Week3-向量库与Embedding/README.md`](./Week3-向量库与Embedding/README.md)
> 📦 **代码骨架** → [`项目/03-doc-search/`](./项目/03-doc-search/)（文档语义搜索）

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | Embedding 原理（够用级）| [📖 Day1](./Week3-向量库与Embedding/Day1-Embedding原理.md) |
| Day 2 | Milvus 部署 + Java SDK | [📖 Day2](./Week3-向量库与Embedding/Day2-Milvus部署与上手.md) |
| Day 3 | Spring AI VectorStore | [📖 Day3](./Week3-向量库与Embedding/Day3-SpringAI-VectorStore.md) |
| Day 4 | 混合检索与 Reranker | [📖 Day4](./Week3-向量库与Embedding/Day4-混合检索与Reranker.md) |
| Day 5 | 整合 Demo：文档检索系统 ⭐ | [📖 Day5](./Week3-向量库与Embedding/Day5-检索Demo.md) |

📦 **产出**：`项目/03-doc-search/` —— 能向量化 + 混合检索的内部文档语义搜索

---

### Week 4：RAG 核心机制 ✅ 已开放

> 📘 **完整 5 天教程** → [`Week4-RAG核心机制/README.md`](./Week4-RAG核心机制/README.md)
> 📦 **代码骨架** → [`项目/04-rag-mini/`](./项目/04-rag-mini/)（mini-RAG）

5 天计划速览：

| Day | 主题 | 教程 |
|-----|------|------|
| Day 1 | 文档加载与解析（PDF/Word/MD/HTML）| [📖 Day1](./Week4-RAG核心机制/Day1-文档加载与解析.md) |
| Day 2 | 分片策略 ⭐（Recursive Splitter）| [📖 Day2](./Week4-RAG核心机制/Day2-分片策略.md) |
| Day 3 | Spring AI RAG 组件（Advisor 机制）| [📖 Day3](./Week4-RAG核心机制/Day3-SpringAI-RAG组件.md) |
| Day 4 | 防幻觉与来源引用 | [📖 Day4](./Week4-RAG核心机制/Day4-防幻觉与来源引用.md) |
| Day 5 | RAG 调优与整合 ⭐ | [📖 Day5](./Week4-RAG核心机制/Day5-RAG调优与整合.md) |

📦 **产出**：`项目/04-rag-mini/` —— 流式问答 + 来源引用 + 拒答兜底的 mini-RAG

---

### Week 5-6：⭐ 企业 RAG 知识库（简历核心项目）✅ 已开放

> **这是简历上的灵魂项目。**
>
> 📘 **完整实施手册** → [`Week5-6-企业RAG知识库/README.md`](./Week5-6-企业RAG知识库/README.md)
> 📦 **代码骨架** → [`项目/05-rag-knowledge-base/`](./项目/05-rag-knowledge-base/)

9 阶段任务卡（12 天计划）：

| 阶段 | 任务 | 时间 | 任务卡 |
|------|------|------|--------|
| ① | 项目骨架 + 数据库设计 + 用户系统 | 1.5 天 | [📖](./Week5-6-企业RAG知识库/01-项目骨架与数据库.md) |
| ② | 异步入库 + 进度查询 | 1.5 天 | [📖](./Week5-6-企业RAG知识库/02-异步入库与进度.md) |
| ③ | 检索 + 流式问答（多租户）| 1.5 天 | [📖](./Week5-6-企业RAG知识库/03-检索与流式问答.md) |
| ④ | 多轮对话 + 历史记忆 | 1 天 | [📖](./Week5-6-企业RAG知识库/04-多轮对话与记忆.md) |
| ⑤ | 多模型路由 + 降级 | 1 天 | [📖](./Week5-6-企业RAG知识库/05-多模型路由.md) |
| ⑥ | Token 统计 + 成本告警 | 1 天 | [📖](./Week5-6-企业RAG知识库/06-Token统计与成本.md) |
| ⑦ | 评测集 + 检索调优 | 1 天 | [📖](./Week5-6-企业RAG知识库/07-评测与调优.md) |
| ⑧ | Docker 一键部署 + 前端 | 1.5 天 | [📖](./Week5-6-企业RAG知识库/08-部署与前端.md) |
| ⑨ | 性能压测 + GitHub 开源 + 博客 | 1 天 | [📖](./Week5-6-企业RAG知识库/09-压测与开源.md) |

#### 🎯 项目规格

```
项目名：enterprise-rag-knowledge-base
位置：./项目/05-rag-knowledge-base/

技术栈：
- Spring Boot 3 + Spring AI 1.0
- Milvus（向量库）+ MySQL（用户/会话）+ Redis（缓存）+ RabbitMQ（异步入库）
- 通义 + GPT-4o + Ollama（多模型路由）
- Docker Compose 一键部署

核心功能：
- 多租户文档上传 + 异步分片 + 进度查询
- 流式问答 + 来源引用（含页码）
- 多轮对话 + 历史记忆
- 多模型路由（成本节省 ~40%）
- Token 用量统计 + 成本告警
- 评测集 + 调优实验（Top-3 召回 65% → 90%）
```

#### 📝 简历亮点写法

> 主导设计基于 Spring AI + Milvus 的企业 RAG 知识库系统，覆盖 200+ 内部文档：
> - 实现混合检索（向量+BM25+Rerank），**Top-3 召回率 65% → 90%**（基于 30 题人工评测集）
> - 多模型路由（通义/GPT-4o/Ollama），**月度推理成本节省 ~40%**
> - 单实例 P95 首字延迟 < 800ms，**支撑 50+ QPS**（k6 压测）
> - Docker Compose 一键部署 / 多租户 / Token 计费 / 异步入库

> 💡 **数字怎么埋** → 见 [`笔记/简历项目数字埋点.md`](./笔记/简历项目数字埋点.md)

---

## ✅ 阶段完成标准

- [ ] Spring AI Hello World 跑通 ✅
- [ ] Function Calling 能写出有用的工具
- [ ] Milvus 能独立部署 + 写入 + 检索
- [ ] **企业 RAG 知识库项目开源到 GitHub**（必须）
- [ ] 写一篇技术博客介绍这个项目
- [ ] 能在 30 分钟内给面试官演示这个 demo

---

## 📁 目录结构

```
03-SpringAI与RAG/
├── README.md          ← 你正在看
├── Week1-SpringAI基础/             ✅
├── Week2-FunctionCalling与多模型/  ✅
├── Week3-向量库与Embedding/        ✅
├── Week4-RAG核心机制/              ✅
├── Week5-6-企业RAG知识库/          ✅（9 阶段任务卡）
├── 笔记/
│   ├── SpringAI入门.md
│   ├── FunctionCalling详解.md
│   ├── 向量数据库选型.md
│   ├── RAG调优技巧.md
│   ├── SpringAI多模态-面试够用版.md   ← 1-2 小时读完，会聊不会做
│   └── 简历项目数字埋点.md
└── 项目/
    ├── 01-helloai/                 (Week 1 产出)
    ├── 02-multi-tools/             (Week 2 产出)
    ├── 03-doc-search/              (Week 3 产出)
    ├── 04-rag-mini/                (Week 4 产出)
    └── 05-rag-knowledge-base/      ⭐ (Week 5-6 简历核心)
```

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 4 · Agent 与工程化](../04-Agent与工程化/README.md)
