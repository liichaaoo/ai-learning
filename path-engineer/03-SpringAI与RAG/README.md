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

### Week 2：Function Calling + 多模型

- [ ] **Function Calling**
  - `@Tool` 注解
  - `@ToolParam` 参数描述
  - 把现有业务方法暴露给 LLM

- [ ] **多模型接入**
  - OpenAI（标杆）
  - 通义千问（国产首选）
  - Claude
  - Ollama（本地模型）

- [ ] **多模型路由**
  - 同一个 Spring 工程注入多个 ChatModel
  - 按场景路由（成本优化）

📦 **产出**：能调用多个工具的智能助手 demo

---

### Week 3：向量库 + Embedding

- [ ] **Embedding 原理**（够用级）
  - 向量化是什么
  - 余弦相似度
  - bge-m3 / text-embedding-3 等主流模型

- [ ] **向量数据库**
  - Milvus 部署（Docker 一键）
  - 也可选 Qdrant / PgVector
  - Java SDK 基础操作

- [ ] **混合检索**
  - 向量召回（语义）
  - BM25（关键词）
  - 重排（Reranker）

📦 **产出**：能向量化文档 + 召回的 demo

---

### Week 4：RAG 核心机制

- [ ] **文档处理**
  - PDF / Word / Markdown / 网页
  - 分片策略（按段落 / 按 token / 按语义）
  - Metadata 设计（来源、章节、时间）

- [ ] **Spring AI RAG 组件**
  - `DocumentReader`：文档加载
  - `TextSplitter`：分片
  - `VectorStore`：存储
  - `QuestionAnswerAdvisor`：自动 RAG

- [ ] **RAG 调优**
  - top_k 选择
  - 上下文窗口管理
  - 防止幻觉

---

### Week 5-6：⭐ 企业 RAG 知识库（必做核心项目）

> **这是简历上的灵魂项目。**

#### 🎯 项目规格

```
项目名：企业知识库 RAG 系统
位置：./项目/02-rag-知识库/

技术栈：
- Spring Boot 3 + Spring AI
- Milvus（向量库）
- Redis（缓存 + 会话）
- MySQL（用户系统）
- Docker Compose 部署

核心功能：
- 文档上传（PDF/Word/Markdown/网页）
- 自动分片 → 向量化 → 入库
- 流式问答 + 来源引用
- 多用户隔离 + 历史记录
- 多模型路由（GPT-4 / 通义）
- Token 用量统计 + 成本控制
```

#### 📅 6-12 天实施计划

| 阶段 | 任务 | 时间 |
|------|------|------|
| 1 | 项目骨架 + 数据库设计 | 1 天 |
| 2 | 文档上传 + 分片 + 向量化 | 2 天 |
| 3 | 检索 + 流式问答 | 2 天 |
| 4 | 用户系统 + 历史记录 | 1 天 |
| 5 | 来源引用 + 元数据 | 1 天 |
| 6 | Token 统计 + 成本告警 | 1 天 |
| 7 | Docker 部署 + 文档 | 1 天 |
| 8 | 简单前端（或用 Postman） | 1 天 |
| 9 | 性能优化 + 压测 | 1 天 |

#### 📝 简历亮点写法（参考）

> 主导设计基于 Spring AI + Milvus 的企业知识库 RAG 系统，
> 单实例支撑 N00+ QPS，平均首字延迟 < 800ms，
> 接入 GPT-4 / 通义千问双模型路由，月度推理成本节省 ~40%。
> 关键技术：流式响应、混合检索、Token 控制、Docker 一键部署。

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
├── 笔记/
│   ├── SpringAI入门.md  (已有)
│   ├── FunctionCalling详解.md  (Week 2 写)
│   ├── 向量数据库选型.md  (Week 3 写)
│   ├── RAG调优技巧.md  (Week 4 写)
│   └── ...
├── 项目/
│   ├── 01-helloai/        (Week 1 产出)
│   ├── 02-multi-tools/    (Week 2 产出)
│   └── 02-rag-知识库/     ⭐ (Week 5-6 核心)
└── 资料/                  (PDF、cheatsheet)
```

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 4 · Agent 与工程化](../04-Agent与工程化/README.md)
