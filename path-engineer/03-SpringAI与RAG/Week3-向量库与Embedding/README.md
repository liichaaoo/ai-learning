# Week 3 · 向量库 + Embedding（5 天）

> 📅 建议时间：阶段 3 第三周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：理解"语义检索"是怎么做出来的——能用 Milvus + Spring AI 把一堆文档搜起来

---

## 🎉 你即将跨过的"关键分水岭"

Week 1-2 你做的 AI 只能"凭脑子答"——它知道的全是预训练数据里有的东西。

**Week 3 结束后，你的 AI 能**：

```
用户: "我们公司去年发布的 OKR 制度文档里，研发线的考核怎么算？"

AI:
  1. 把问题向量化
  2. 在公司内部知识库里"语义检索"出 Top-3 最相关的段落
  3. （Week 4 会做）把这些段落塞进 Prompt
  4. （Week 4 会做）让 AI 基于这些段落作答
```

> 💡 **本周做的就是 RAG 的"R"（Retrieval）**——下周才做"AG"（生成）。
>
> 别小看检索，**RAG 系统 80% 的效果差异都在检索环节**。

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **Embedding 直觉** | 知道一段文字怎么变成一个向量，向量空间里"近 = 语义相似" |
| **余弦相似度** | RAG 检索的算分公式，能默写 |
| **Milvus 部署** | Docker 一行起，Java SDK 增删改查 |
| **Spring AI VectorStore** | 跨 Milvus / PgVector / Redis 的统一抽象 |
| **混合检索** | 向量召回 + BM25 关键词，工业界事实标准 |
| **Reranker 认知** | 知道为什么要重排，bge-reranker 怎么用 |

---

## ⚠️ 开工前必读

### 这周会用到 Docker

如果你还没装 Docker Desktop，**今天就装**——本周和后两周都需要。

```bash
# Mac
brew install --cask docker

# 或去官网下载：https://www.docker.com/products/docker-desktop
```

### Embedding API 哪里来？

**两条路线**（推荐 A）：

| 路线 | 速度 | 成本 | 备注 |
|------|------|------|------|
| **A：通义百炼 text-embedding-v3** ⭐ | 快 | 免费额度多 | 跟 Week 1 同一个 API Key |
| B：本地 ONNX（HuggingFace bge-small-zh）| 慢 | 0 | 不需要 Key，但要下 200MB+ 模型 |

> 💡 **强烈推荐用通义**——Week 1 那个 Key 直接能用，省心。

---

## 📅 5 天计划

| Day | 主题 | 产出 | 时长 |
|-----|------|------|------|
| **Day 1** | [Embedding 原理（够用级）](./Day1-Embedding原理.md) | 用通义 API 把一句话变向量并算相似度 | 1.5h |
| **Day 2** | [Milvus 部署 + Java SDK](./Day2-Milvus部署与上手.md) | Docker 一键起，写入 + 查询 | 1.5h |
| **Day 3** | [Spring AI VectorStore](./Day3-SpringAI-VectorStore.md) | 用 Spring AI 抽象层操作 Milvus，丝滑 | 1.5h |
| **Day 4** | [混合检索与 Reranker](./Day4-混合检索与Reranker.md) | 向量 + BM25 + 重排 | 1.5h |
| **Day 5** | [整合：文档检索 Demo](./Day5-检索Demo.md) ⭐ | `项目/03-doc-search/` 跑通 | 2h |

---

## 📦 本周的最终产出

**项目**：`项目/03-doc-search/`

```
03-doc-search/
├── pom.xml
├── docker-compose.yml          ← Milvus 一键启停
├── README.md
└── src/main/
    ├── java/.../
    │   ├── DocSearchApplication.java
    │   ├── controller/SearchController.java
    │   ├── service/
    │   │   ├── EmbeddingService.java       ⭐ 调通义 embedding
    │   │   ├── IndexService.java           ⭐ 文档入库
    │   │   └── SearchService.java          ⭐ 混合检索
    │   └── config/MilvusConfig.java
    └── resources/
        ├── application.yml
        └── docs/                            ← 测试用的几篇内部文档
```

跑起来后能做的事：

- `POST /index` → 把 `docs/` 下所有文件分片、向量化、入库
- `GET /search?q=去年的OKR制度` → 返回 Top-5 相关文档片段（含相似度分数）
- `GET /search/hybrid?q=...` → 向量 + BM25 混合检索

---

## 💡 RAG 的两种心智模型

很多人把 RAG 想得很玄。其实就两种心智：

### ① 检索增强（Retrieval-Augmented）

```
"知识在外面，不在模型脑子里"
   ↓
查到相关知识 → 塞给模型 → 让它基于这些知识回答
```

### ② 私域问答（你公司的内部知识）

```
公司内部文档 → 切片 + 向量化 → 存进 Milvus
                                     ↓
                                提问时检索 → 拼接 Prompt → LLM 回答
```

> 💡 本周做的就是 **②** 的左半边。下周做右半边。

---

## 🧭 推荐节奏

```
周一 Day 1   1.5h    Embedding 直觉 + 通义 API
周二 Day 2   1.5h    Milvus 部署 + Java SDK 增删改查
周三 Day 3   1.5h    Spring AI VectorStore 抽象
周四 Day 4   1.5h    混合检索 + Reranker
周五         休息
周六 Day 5   2h      做完 doc-search demo
周日         写笔记 / 写周报
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [Embedding 原理](./Day1-Embedding原理.md)
- [ ] Day 2 · [Milvus 部署与上手](./Day2-Milvus部署与上手.md)
- [ ] Day 3 · [Spring AI VectorStore](./Day3-SpringAI-VectorStore.md)
- [ ] Day 4 · [混合检索与 Reranker](./Day4-混合检索与Reranker.md)
- [ ] Day 5 · [检索 Demo](./Day5-检索Demo.md)

---

## 🎯 本周出关自测（7 题）

1. 用一句话解释 Embedding 是什么、做完之后语义相似的两段文本会怎样？
2. 余弦相似度的公式是？为什么 RAG 几乎都用它而不是欧氏距离？
3. Milvus 里的 Collection / Partition / Index 三个概念怎么对应到 MySQL 的 Table / Partition / Index？
4. 为什么要建索引（如 IVF_FLAT / HNSW）？暴力扫描不行吗？
5. Spring AI 的 `VectorStore` 抽象底下能换哪些实现？
6. 为什么需要"混合检索"？纯向量检索的弱点在哪？
7. Reranker 是什么时候介入的？它跟"召回"有什么本质区别？

**答对 5+ 题** = 本周通过。

---

## 🚦 重要提醒

### 1. 不要陷在 Milvus 的高级特性里

本周只学：**建库 → 写入 → 查询 → 删除**。
Partition / 多副本 / 一致性级别 / GPU 索引 …… 这些**生产场景再看**。

### 2. Embedding 模型不要乱换

**整个项目从头到尾用同一个 embedding 模型**——换模型 = 全部数据要重新向量化。

### 3. 别忘了 dimension 对齐

```
通义 text-embedding-v3   维度 1024
OpenAI text-embedding-3-large 维度 3072
bge-m3                     维度 1024
```

**Milvus 的 Collection 创建时维度必须跟 embedding 模型一致**——这是新手最常踩的坑。

---

## 🔗 相关资源

- [Spring AI VectorStore 文档](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
- [Milvus 中文文档](https://milvus.io/docs/zh)
- [bge-m3 模型卡](https://huggingface.co/BAAI/bge-m3)（中文 Embedding 首选开源模型）
- [笔记/向量数据库选型.md](../笔记/向量数据库选型.md)（本周写）

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1：Embedding 原理](./Day1-Embedding原理.md)**
