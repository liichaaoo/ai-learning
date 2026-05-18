# Day 3 · Spring AI VectorStore（一套接口走天下）

> ⏱️ 时间：1.5 小时
> 🎯 目标：用 Spring AI `VectorStore` 抽象操作 Milvus，**告别一堆 SDK 模板代码**

---

## 0. 心法（5 分钟）

> **Spring AI VectorStore = 向量库的 JPA。**

Day 2 你已经体会过 Milvus Java SDK 的"模板代码爽点为 0"——`FieldType.newBuilder()...` 一长串。

Spring AI 把这些封装成**统一接口**：

```java
vectorStore.add(documents);
vectorStore.similaritySearch(query);
vectorStore.delete(ids);
```

底层换 Milvus、PgVector、Redis、Chroma、Pinecone 都是**改一个依赖 + 改一段配置**的事。

---

## 1. 一图速记：抽象关系（10 分钟）

```
┌────────────────────── 你的业务代码 ──────────────────────┐
│                                                         │
│   vectorStore.add(docs)                                 │
│   vectorStore.similaritySearch("...")                   │
│                                                         │
└─────────────────────────┬───────────────────────────────┘
                          │
              ┌───────────▼────────────┐
              │  Spring AI VectorStore │  统一接口
              └───────────┬────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐    ┌──────────────┐
│MilvusVector  │  │PgVectorStore │    │ RedisVector  │
│   Store      │  │              │    │    Store     │
└──────┬───────┘  └──────┬───────┘    └──────┬───────┘
       │                 │                   │
       ▼                 ▼                   ▼
   Milvus 集群       PostgreSQL          Redis Stack
                    + pgvector ext
```

> 💡 业务代码全程只跟 `VectorStore` 打交道——这就是 Spring 的"面向接口"哲学在 AI 里的延续。

---

## 2. 切换到 Spring AI 写法（25 分钟）

### 2.1 加 Spring AI Milvus Starter

`pom.xml`：

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-vector-store-milvus</artifactId>
</dependency>

<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-alibaba-starter</artifactId>
</dependency>
```

### 2.2 配置 `application.yml`

```yaml
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      embedding:
        options:
          model: text-embedding-v3        # 1024 维
    vectorstore:
      milvus:
        client:
          host: localhost
          port: 19530
        databaseName: default
        collectionName: docs_v2
        embeddingDimension: 1024          # 必须跟 embedding 模型对齐
        indexType: HNSW
        metricType: COSINE
        initialize-schema: true           # 自动建 collection
```

> 💡 **`initialize-schema: true`** —— Spring AI 会帮你建好 collection、字段、索引。**Day 2 写的那一堆 ensureCollection 代码可以全删了**。

### 2.3 注入 + 三行操作

```java
package com.demo.docsearch.service;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class DocService {

    private final VectorStore vectorStore;

    public DocService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    /** 写入 */
    public void index(String content, Map<String, Object> metadata) {
        Document doc = new Document(content, metadata);
        vectorStore.add(List.of(doc));
    }

    /** 查询 Top-K */
    public List<Document> search(String query, int topK) {
        return vectorStore.similaritySearch(
                SearchRequest.query(query).withTopK(topK)
        );
    }

    /** 带阈值的查询：分数 < threshold 的结果丢弃 */
    public List<Document> searchWithThreshold(String query, int topK, double threshold) {
        return vectorStore.similaritySearch(
                SearchRequest.query(query)
                        .withTopK(topK)
                        .withSimilarityThreshold(threshold)
        );
    }

    /** 删除 */
    public void delete(List<String> ids) {
        vectorStore.delete(ids);
    }
}
```

> 💡 跟 Day 2 的 `MilvusDemoService` 对比一下——**代码量缩了 80%**。

### 2.4 Document 是什么

`org.springframework.ai.document.Document` 是 Spring AI 的"统一文档对象"：

```java
public class Document {
    private final String id;                 // 自动生成 UUID
    private final String content;            // 文本
    private final Map<String, Object> metadata;  // 任意元数据
    private List<Double> embedding;          // VectorStore 内部填，业务一般不用碰
    // ...
}
```

**Embedding 由 Spring AI 自动调**——你不用再手动调 `embeddingService.embed()`。

---

## 3. metadata：RAG 的"传家宝"（15 分钟）

> 这一节最重要——**Week 5-6 简历项目能不能做到"答案带来源"，全靠 metadata**。

### 3.1 写入时塞 metadata

```java
docService.index(
    "公司 OKR 制度第 3 条：研发线绩效考核以季度为单位…",
    Map.of(
        "source",   "OKR制度.pdf",
        "section",  "第三章",
        "page",     12,
        "createTime", "2025-03-15",
        "department", "research"
    )
);
```

### 3.2 查询时按 metadata 过滤

```java
SearchRequest.query("绩效考核")
        .withTopK(5)
        .withFilterExpression("department == 'research' && page > 10")
```

> 💡 **典型用法**：用户问问题时，根据登录身份（`department`）过滤——**实现"多用户隔离"，简历项目必备**。

### 3.3 metadata 的设计原则

| 字段 | 用途 |
|------|------|
| `source` | 文件名（用户答案里展示"出自 XX.pdf"）|
| `section` / `chapter` / `page` | 定位精确位置 |
| `createTime` | 时间过滤（"只看最近一年的文档"）|
| `department` / `tenant_id` | 多租户隔离 |
| `lang` | 中英文文档区分 |
| `tags` | 标签筛选 |

> 🎯 **简历项目里 metadata 设计好坏，直接决定面试答辩时能不能讲出"我们做了多租户隔离 / 时间衰减 / 来源引用"等亮点**。

---

## 4. ChatClient + VectorStore = 简版 RAG（15 分钟）

> 提前预习——**Week 4 才是 RAG 的主战场**，但今天我们用 Spring AI 的"魔法 Advisor"先尝个鲜。

```java
@Service
public class SimpleRagService {

    private final ChatClient chatClient;

    public SimpleRagService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
                .defaultAdvisors(new QuestionAnswerAdvisor(vectorStore))
                .build();
    }

    public String ask(String question) {
        return chatClient.prompt()
                .user(question)
                .call()
                .content();
    }
}
```

```java
@RestController
@RequiredArgsConstructor
public class RagController {
    private final SimpleRagService rag;
    private final DocService docService;

    @PostMapping("/index")
    public String index(@RequestBody String content) {
        docService.index(content, Map.of("source", "manual"));
        return "OK";
    }

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return rag.ask(q);
    }
}
```

测试：

```bash
# 灌点知识
curl -X POST -d "我们公司的工程师休假政策：每年 15 天年假 + 5 天病假" http://localhost:8080/index

curl -X POST -d "试用期员工年假减半" http://localhost:8080/index

# 提问
curl "http://localhost:8080/ask?q=工程师每年有多少天年假？"
# 模型会基于上面写入的内容回答
```

> 🎯 这就是 RAG 最小完整闭环——`QuestionAnswerAdvisor` 做的事：
>
> ```
> 1. 把问题向量化
> 2. similaritySearch 拿 Top-K
> 3. 把检索结果拼到 system prompt 里
> 4. 调 LLM 生成
> ```
>
> Week 4 我们会**手撕这个 Advisor**——本周先体验"接口的爽"。

---

## 5. 为什么不直接用 PgVector / Redis（5 分钟）

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|---------|
| **Milvus** ⭐ | 专业向量库，HNSW 性能强 | 部署组件多（etcd + minio）| **本系列默认 / 中大规模** |
| **PgVector** | 跟现有 PostgreSQL 共用，运维简单 | 大规模性能不如 Milvus | 已有 PG / 数据量 < 100 万 |
| **Redis Stack** | 跟 Redis 共用，延迟极低 | 集群成本高 | 已有 Redis / 实时场景 |
| **Chroma** | 轻量、Python 生态好 | Java 支持一般 | 原型 / 个人项目 |
| **Elasticsearch (8.x)** | 自带向量 + 全文，混合检索好做 | 资源占用大 | 已有 ES |

> 🎯 **简历叙述策略**：
> - 主项目用 **Milvus**（专业感强，面试官认）
> - 在笔记里写一篇《[向量数据库选型.md](../笔记/向量数据库选型.md)》对比理由——**这就是简历加分项的"决策能力"**

---

## 6. 检查清单

- [ ] 切到 Spring AI Starter，删掉 Day 2 的 ensureCollection 代码
- [ ] 跑通 `vectorStore.add()` + `similaritySearch()`
- [ ] 给文档塞 metadata，并能用 `withFilterExpression` 过滤
- [ ] 跑通 `QuestionAnswerAdvisor` 简版 RAG
- [ ] 解释 VectorStore 为什么是抽象接口（讲给面试官听）

完成了 ➡️ [Day 4 · 混合检索与 Reranker](./Day4-混合检索与Reranker.md)

---

## 🔗 相关链接

- ⬅️ [Day 2 · Milvus 部署与上手](./Day2-Milvus部署与上手.md)
- ➡️ [Day 4 · 混合检索与 Reranker](./Day4-混合检索与Reranker.md)
- ⬆️ [Week 3 总览](./README.md)
- 📚 [Spring AI VectorStore 官方文档](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
