# Week 4 · RAG 核心机制（5 天）

> 📅 建议时间：阶段 3 第四周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：把上周的"检索"接上"生成"——做出可演示的 mini-RAG，并理解每一个调优旋钮

---

## 🎉 你即将跨过的"关键分水岭"

Week 3 你做的检索系统能找到"相关片段"。

**Week 4 结束后，你的 AI 能**：

```
用户：什么是公司的工程师晋升流程？

系统：
  1. 识别需要"查公司文档"
  2. 检索 Top-5 相关文档片段（Week 3 已能做）
  3. 拼装 Prompt：「以下是相关文档：xxx。请基于此回答…」
  4. 流式输出回答 + 引用来源："来自《晋升手册.pdf》第 3 章"
  5. 如果检索不到，礼貌拒答而不是胡编
```

> 💡 **Week 4 = RAG 的 "AG"（Augmented Generation）**——把上周的检索缝合到 LLM 上。

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **文档加载** | PDF / Word / Markdown / HTML / 网页都能吃 |
| **智能分片** | 按 token / 段落 / 语义分，避免"断头" |
| **元数据设计** | 给每个 chunk 打标签（来源、页码、章节）|
| **QuestionAnswer Advisor** | Spring AI 的"自动 RAG"魔法盒 |
| **来源引用** | 答案里能告诉用户"出自哪个文档第几章" |
| **防幻觉** | 检索不到时不胡说 |
| **RAG 调优** | top_k / 上下文窗口 / 温度 三个旋钮的取值经验 |

---

## ⚠️ 开工前必读

### 1. 本周不引入新基础设施

复用 Week 3 的 Milvus + 通义。新装的就是几个 Java 库（PDF 解析、Tika）。

### 2. RAG 不是银弹

学完本周你应该知道 **RAG 解决什么 / 不解决什么**：

| RAG 适合 | RAG 不适合 |
|---------|-----------|
| 私域知识问答 | 需要复杂推理的任务 |
| 答案需要引用来源 | 创意生成 |
| 文档定期更新 | 需要"算数"的任务 |
| 防幻觉要求高的场景 | 需要执行动作（用 Function Calling）|

---

## 📅 5 天计划

| Day | 主题 | 产出 | 时长 |
|-----|------|------|------|
| **Day 1** | [文档加载与解析](./Day1-文档加载与解析.md) | PDF/Word/MD/网页全都能读 | 1.5h |
| **Day 2** | [分片策略](./Day2-分片策略.md) ⭐ | 按 token / 段落 / 语义切，对比效果 | 2h |
| **Day 3** | [Spring AI RAG 组件](./Day3-SpringAI-RAG组件.md) | DocumentReader / TextSplitter / Advisor 全套 | 1.5h |
| **Day 4** | [防幻觉 + 来源引用](./Day4-防幻觉与来源引用.md) | 答案可追溯，检索不到时礼貌拒答 | 1.5h |
| **Day 5** | [RAG 调优 + 整合 Demo](./Day5-RAG调优与整合.md) ⭐ | `项目/04-rag-mini/` 上线 | 2h |

---

## 📦 本周的最终产出

**项目**：`项目/04-rag-mini/`

```
04-rag-mini/
├── pom.xml
├── docker-compose.yml          ← 复用 Week 3 的 Milvus
├── README.md
└── src/main/
    ├── java/.../
    │   ├── RagMiniApplication.java
    │   ├── controller/
    │   │   └── RagController.java
    │   ├── service/
    │   │   ├── DocLoaderService.java         ← Day 1：PDF/Word/MD
    │   │   ├── ChunkingService.java          ← Day 2：分片
    │   │   ├── RagService.java               ← Day 3：核心 RAG
    │   │   └── CitationService.java          ← Day 4：来源引用
    │   ├── advisor/
    │   │   └── HardenedQAAdvisor.java        ← Day 4：防幻觉 + 引用
    │   └── config/RagConfig.java
    └── resources/
        ├── application.yml
        └── prompts/
            ├── qa-system.st                  ← System Prompt 模板
            └── citation-format.st            ← 引用格式
```

跑起来后能做的事：

- `POST /docs` （上传 PDF/Word/MD）→ 自动解析 + 分片 + 入库
- `POST /chat`（流式提问）→ 流式返回答案 + 来源引用
- `GET /docs` → 列出已索引的文档

---

## 🧠 RAG 调优速查表（本周建立直觉，最终落地到 Day 5）

| 旋钮 | 范围 | 调高的影响 | 推荐 |
|------|------|-----------|------|
| **chunk_size**（分片大小）| 200~1000 字符 | 上下文更全，但召回更糊 | **500** |
| **chunk_overlap**（重叠）| 0~200 | 防"断头"，但增加冗余 | **50~100** |
| **top_k** | 3~10 | 更全但噪声多 | **5** |
| **similarity_threshold** | 0~1 | 高的放过更多，低的更严 | **0.5** |
| **temperature** | 0~1 | 答案多样但易飘 | **0.0~0.3**（RAG 推荐 0）|
| **max_tokens** | 256~2000 | 答案更长更贵 | **512** |

---

## 🧭 推荐节奏

```
周一 Day 1   1.5h    文档加载（PDF/Word 拆出来）
周二 Day 2   2h      分片策略（一定要做对比实验）
周三 Day 3   1.5h    Spring AI RAG 组件
周四 Day 4   1.5h    防幻觉 + 来源引用（演示亮点）
周五         休息
周六 Day 5   2h      整合 + 调优 + 录 demo 视频
周日         写笔记《RAG调优技巧.md》+ 周报
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [文档加载与解析](./Day1-文档加载与解析.md)
- [ ] Day 2 · [分片策略](./Day2-分片策略.md)
- [ ] Day 3 · [Spring AI RAG 组件](./Day3-SpringAI-RAG组件.md)
- [ ] Day 4 · [防幻觉与来源引用](./Day4-防幻觉与来源引用.md)
- [ ] Day 5 · [RAG 调优与整合](./Day5-RAG调优与整合.md)

---

## 🎯 本周出关自测（8 题）

1. PDF / Word / Markdown 三种文档，处理时各有什么坑？
2. 三种主流分片策略（按 token / 段落 / 语义）各自适合什么场景？
3. chunk_overlap 为什么需要？会带来什么副作用？
4. `QuestionAnswerAdvisor` 内部做了哪几步？
5. RAG 答案里要怎么塞"来源引用"？metadata 怎么设计？
6. 检索分数都低于阈值时，应该怎么处理？
7. RAG 系统出现"幻觉"的常见原因有哪些？
8. top_k = 10 一定比 top_k = 3 好吗？

**答对 6+ 题** = 本周通过。

---

## 🚦 重要提醒

### 1. 分片是 RAG 效果的决定性因素

**分片不好，神仙也救不了**——Day 2 一定要花够时间做对比实验。

### 2. 不要追求"完美 RAG"

本周做出"能演示、答案合理、有引用"就过关。**性能和精度优化留到 Week 5-6 简历项目**。

### 3. 提前准备测试集

本周末抽 30 分钟，**写一份 20~30 条的测试问题**（针对你的文档）。
Week 5-6 这份测试集就是你简历"准确率提升 30%"的依据。

---

## 🔗 相关链接

- [Spring AI RAG 文档](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)
- [LangChain RAG 概念](https://python.langchain.com/docs/tutorials/rag/)（Python 但概念通用）
- [Apache Tika 支持的格式](https://tika.apache.org/2.9.0/formats.html)
- [笔记/RAG调优技巧.md](../笔记/RAG调优技巧.md)（本周末写）

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1：文档加载与解析](./Day1-文档加载与解析.md)**
