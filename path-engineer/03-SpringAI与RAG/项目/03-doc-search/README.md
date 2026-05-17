# 03-doc-search · 文档语义搜索（Week 3 交付物）

> 配套教程：[Week 3 · 向量库与 Embedding](../../Week3-向量库与Embedding/README.md)

---

## 🎯 项目目标

把 Week 3 五天学的串起来：

- 灌入 `docs/` 下的 Markdown / TXT
- 一键向量化 + 入 Milvus
- 提供"纯向量"和"混合检索（向量+BM25+Rerank）"两种接口
- 在 Attu 里能直接看到数据 + 索引

---

## 🛠 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| Spring Boot | 3.x | 框架 |
| Spring AI Alibaba | 最新 | 通义模型适配 |
| Milvus | 2.4 | 向量库（Docker）|
| Apache Lucene | 9.10 | BM25（也可换 ES）|
| 通义 text-embedding-v3 | — | 1024 维 Embedding |
| 通义 gte-rerank | — | Reranker（可选）|

---

## 🚀 快速开始

```bash
# 1. 起 Milvus
docker compose up -d

# 2. 配置 API Key
export DASHSCOPE_API_KEY=sk-xxx

# 3. 起服务
./mvnw spring-boot:run

# 4. 灌数据
curl -X POST "http://localhost:8083/api/index/dir?path=./docs"

# 5. 纯向量
curl "http://localhost:8083/api/search?q=年假怎么算"

# 6. 混合检索
curl "http://localhost:8083/api/search/hybrid?q=年假怎么算"
```

---

## 📁 期望目录结构

```
03-doc-search/
├── pom.xml                    （pending：按 Week3 README 添加 Spring AI Milvus + Lucene 依赖）
├── docker-compose.yml          （Week3 Day2 已给出完整内容）
├── README.md                   ← 你正在看
├── docs/                       ← 测试用文档（自己放几篇真实/脱敏的）
│   ├── 公司年假制度.md
│   ├── 出差报销流程.md
│   └── ...
└── src/main/
    ├── java/com/demo/docsearch/
    │   ├── DocSearchApplication.java
    │   ├── controller/SearchController.java        ← Day 5 §2.6
    │   ├── service/
    │   │   ├── EmbeddingService.java               ← Day 1 §2.2
    │   │   ├── IndexService.java                   ← Day 5 §2.3
    │   │   ├── SearchService.java                  ← Day 5 §2.4
    │   │   ├── HybridSearchService.java            ← Day 5 §2.5
    │   │   ├── BM25Service.java                    ← Day 4 §2.3 / Lucene 实现
    │   │   └── RerankService.java                  ← Day 4 §4.3
    │   └── config/MilvusConfig.java                ← Day 2 §2.2
    └── resources/
        └── application.yml                          ← Day 5 §2.2
```

---

## 📝 进度自检

- [ ] Milvus 三件套起来，Attu 能连
- [ ] `application.yml` 填好 + Embedding 维度对齐 1024
- [ ] `IndexService.indexDirectory()` 能扫目录入库
- [ ] `/api/search` 能返回 Top-5 + 分数
- [ ] `/api/search/hybrid` 跟纯向量结果有可见差异
- [ ] **跑过一次延迟测试**（ab / k6），数字记到笔记里

---

## 🔗 相关链接

- ⬆️ [Week 3 总览](../../Week3-向量库与Embedding/README.md)
- 📖 [Day 5 整合教程（含完整代码）](../../Week3-向量库与Embedding/Day5-检索Demo.md)
- 📦 [上一项目：02-multi-tools](../02-multi-tools/)
- 📦 [下一项目：04-rag-mini](../04-rag-mini/)
