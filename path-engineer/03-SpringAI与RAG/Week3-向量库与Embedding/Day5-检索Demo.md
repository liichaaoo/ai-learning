# Day 5 · 整合 Demo · 文档检索系统 ⭐

> ⏱️ 时间：2 小时
> 🎯 目标：把 Day 1-4 全部串起来，做出一个能演示的"内部文档语义搜索"
> 📂 项目：[`项目/03-doc-search/`](../项目/03-doc-search/)

---

## 0. 心法（5 分钟）

> **本周通关 = 跑出一个真的能搜内部文档的服务，并且演示给同事看 5 分钟。**

具体说，今天结束你应该能：

1. 启动 Milvus + 启动 Spring Boot
2. 调 `POST /index` 把 5~10 篇内部文档（自己写的也行）灌进去
3. 调 `GET /search?q=...` 看到返回 Top-5 文档片段，**带相似度分数**
4. 调 `GET /search/hybrid?q=...` 看到向量 + BM25 + 重排的最终结果
5. 在群里发一个 5 分钟视频/截图证明它能跑

---

## 1. 项目目标规格（10 分钟）

```
项目名：doc-search
位置：项目/03-doc-search/

技术栈：
  Spring Boot 3.x + Spring AI 1.0.x
  Milvus 2.4（Docker）
  通义 text-embedding-v3
  通义 gte-rerank（可选）

接口：
  POST /index/text         单条文本入库
  POST /index/dir          扫描 docs/ 目录批量入库
  GET  /search             纯向量 Top-K
  GET  /search/hybrid      向量 + BM25 + RRF + Reranker
  DELETE /index/{id}       删除一条
```

---

## 2. 项目骨架（25 分钟）

> 完整骨架文件在 [`项目/03-doc-search/`](../项目/03-doc-search/)（本周补全）。下面是关键代码 review。

### 2.1 `pom.xml`

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-alibaba-starter</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-milvus-store-spring-boot-starter</artifactId>
    </dependency>

    <!-- 简易 BM25：这里直接用 Lucene -->
    <dependency>
        <groupId>org.apache.lucene</groupId>
        <artifactId>lucene-core</artifactId>
        <version>9.10.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.lucene</groupId>
        <artifactId>lucene-queryparser</artifactId>
        <version>9.10.0</version>
    </dependency>

    <!-- 工具 -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

### 2.2 配置 `application.yml`

```yaml
server:
  port: 8083

spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      embedding:
        options:
          model: text-embedding-v3
    vectorstore:
      milvus:
        client:
          host: localhost
          port: 19530
        databaseName: default
        collectionName: doc_search
        embeddingDimension: 1024
        indexType: HNSW
        metricType: COSINE
        initialize-schema: true
```

### 2.3 IndexService：入库

```java
@Service
@RequiredArgsConstructor
public class IndexService {
    private final VectorStore vectorStore;
    private final BM25Service bm25Service;       // Day 4 简易 / Lucene 都行

    /** 单条入库 */
    public String indexText(String content, Map<String, Object> meta) {
        Document doc = new Document(content, meta);
        vectorStore.add(List.of(doc));
        bm25Service.add(doc.getId(), content);
        return doc.getId();
    }

    /** 批量目录入库 */
    public int indexDirectory(Path dir) throws IOException {
        AtomicInteger count = new AtomicInteger();
        try (Stream<Path> paths = Files.walk(dir)) {
            paths.filter(Files::isRegularFile)
                 .filter(p -> p.toString().endsWith(".md") || p.toString().endsWith(".txt"))
                 .forEach(p -> {
                     try {
                         String content = Files.readString(p);
                         // 简单按段落切分（Week 4 会做更智能的 splitter）
                         for (String chunk : content.split("\n\n+")) {
                             if (chunk.length() < 20) continue;
                             indexText(chunk, Map.of(
                                     "source", p.getFileName().toString(),
                                     "path",   p.toString()
                             ));
                             count.incrementAndGet();
                         }
                     } catch (IOException e) {
                         log.warn("read fail: {}", p, e);
                     }
                 });
        }
        return count.get();
    }
}
```

### 2.4 SearchService：纯向量

```java
@Service
@RequiredArgsConstructor
public class SearchService {
    private final VectorStore vectorStore;

    public List<Hit> searchVector(String query, int topK) {
        List<Document> docs = vectorStore.similaritySearch(
                SearchRequest.query(query).withTopK(topK)
        );
        return docs.stream()
                .map(d -> new Hit(
                        d.getId(),
                        d.getContent(),
                        (Double) d.getMetadata().getOrDefault("distance", 0.0),
                        d.getMetadata()))
                .toList();
    }

    public record Hit(String id, String content, double score, Map<String, Object> metadata) {}
}
```

### 2.5 HybridSearchService：完整流水线 ⭐

```java
@Service
@RequiredArgsConstructor
public class HybridSearchService {
    private final VectorStore vectorStore;
    private final BM25Service bm25Service;
    private final RerankService rerankService;   // Day 4 通义 / 本地 bge

    public List<SearchService.Hit> hybridSearch(String query, int topK) {
        // ① 双路召回各 Top-30
        List<Document> vec = vectorStore.similaritySearch(
                SearchRequest.query(query).withTopK(30));
        List<String> bm25 = bm25Service.search(query, 30);

        // ② RRF 合并
        List<String> vecIds = vec.stream().map(Document::getId).toList();
        List<String> mergedIds = rrf(List.of(vecIds, bm25), 60, 30);

        // ③ 拉原文
        Map<String, Document> idMap = vec.stream()
                .collect(Collectors.toMap(Document::getId, d -> d, (a, b) -> a));
        // BM25 命中但向量未命中的，需要从存储里再拉一次（这里简化：略过）
        List<Document> candidates = mergedIds.stream()
                .map(idMap::get).filter(Objects::nonNull).toList();
        List<String> texts = candidates.stream().map(Document::getContent).toList();

        // ④ Reranker 精排到 Top-K
        List<RerankService.RerankItem> reranked = rerankService.rerank(query, texts, topK);

        // ⑤ 组装最终结果
        List<SearchService.Hit> result = new ArrayList<>();
        for (var item : reranked) {
            Document d = candidates.get(item.index());
            result.add(new SearchService.Hit(d.getId(), d.getContent(), item.score(), d.getMetadata()));
        }
        return result;
    }

    /* 来自 Day 4 §3.3 */
    private static List<String> rrf(List<List<String>> rankedLists, int k, int topN) {
        Map<String, Double> score = new HashMap<>();
        for (List<String> list : rankedLists) {
            for (int rank = 0; rank < list.size(); rank++) {
                score.merge(list.get(rank), 1.0 / (k + rank + 1), Double::sum);
            }
        }
        return score.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .limit(topN)
                .map(Map.Entry::getKey)
                .toList();
    }
}
```

### 2.6 Controller

```java
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class SearchController {
    private final IndexService indexService;
    private final SearchService searchService;
    private final HybridSearchService hybridSearchService;

    @PostMapping("/index/text")
    public String indexText(@RequestBody Map<String, Object> body) {
        String content = (String) body.get("content");
        Map<String, Object> meta = (Map<String, Object>) body.getOrDefault("metadata", Map.of());
        return indexService.indexText(content, meta);
    }

    @PostMapping("/index/dir")
    public Map<String, Object> indexDir(@RequestParam String path) throws IOException {
        int n = indexService.indexDirectory(Path.of(path));
        return Map.of("indexed", n);
    }

    @GetMapping("/search")
    public List<SearchService.Hit> search(@RequestParam String q,
                                          @RequestParam(defaultValue = "5") int topK) {
        return searchService.searchVector(q, topK);
    }

    @GetMapping("/search/hybrid")
    public List<SearchService.Hit> hybrid(@RequestParam String q,
                                          @RequestParam(defaultValue = "5") int topK) {
        return hybridSearchService.hybridSearch(q, topK);
    }
}
```

---

## 3. 灌点测试数据（10 分钟）

在 `项目/03-doc-search/docs/` 下放几篇 `.md`，建议**真的用你工作中的文档**（脱敏）：

```
docs/
├── 公司年假制度.md
├── 出差报销流程.md
├── 入职须知.md
├── OKR评分规则.md
└── 工程师面试流程.md
```

启动后：

```bash
curl -X POST "http://localhost:8083/api/index/dir?path=./docs"
# {"indexed": 23}
```

---

## 4. 演示脚本（15 分钟）⭐

> 这一段直接录屏 5 分钟视频发群里，**就是你简历"项目演示"的素材**。

```bash
# ─── 场景 1：纯向量检索的"语义跨语言"能力 ───
curl "http://localhost:8083/api/search?q=怎么报销"
# 预期：召回"出差报销流程.md" Top-1，即使原文没"怎么"二字

# ─── 场景 2：BM25 救场（精确词）───
curl "http://localhost:8083/api/search?q=OKR"
# 看 Top-K 里 "OKR评分规则.md" 是不是 Top-1

curl "http://localhost:8083/api/search/hybrid?q=OKR"
# 混合检索：精确词命中应该明显更稳

# ─── 场景 3：Reranker 修复"假相关" ───
curl "http://localhost:8083/api/search?q=新员工第一天该做什么"
# 纯向量可能召回入职须知 + 一些跑题文档

curl "http://localhost:8083/api/search/hybrid?q=新员工第一天该做什么"
# Reranker 后 Top-3 应该全是"入职"相关
```

---

## 5. 性能 & 简历数字（10 分钟）

> 简历项目要会"埋数字"——Week 5-6 简历项目正式做之前，本周先采集第一批基线数据。

### 5.1 写一个最简压测脚本

```bash
# 用 ab 或 k6
ab -n 200 -c 10 "http://localhost:8083/api/search?q=报销"
```

记录三个数：

| 指标 | 你的本周值（写到笔记里）|
|------|---------|
| 单次纯向量检索 P95 延迟 | _____ ms |
| 单次混合检索 P95 延迟 | _____ ms |
| 100 篇文档入库总耗时 | _____ s |

### 5.2 简历数字的"可信叙述"

```
❌ 不可信："我做了一个超快的 RAG 系统"

✅ 可信："基于 Spring AI + Milvus 实现 RAG 检索层，
        单实例 P95 延迟 < 200ms，混合检索 (向量+BM25+Rerank)
        相比纯向量 Top-3 准确率提升约 30%（基于 50 题人工评测集）"
```

> 🎯 **本周末把"50 题评测集"的事记起来**——Week 5-6 我们会真做一份。

---

## 6. 出关验收

跑通这 5 个动作 = Week 3 通过：

- [ ] Milvus + Spring Boot 正常启动
- [ ] `POST /api/index/dir` 能批量入库 ≥ 20 条
- [ ] `GET /api/search` 能返回 Top-5（带分数）
- [ ] `GET /api/search/hybrid` 跟纯向量结果**有可见的差异**
- [ ] 在 Attu 里能看到 Collection 数据 + 索引
- [ ] 能解释完整流水线：召回 → RRF → Reranker

---

## 7. 思考与延伸（休息时想）

| 问题 | 提示 |
|------|------|
| 为什么我们没有做"分片优化"？| 留给 Week 4 |
| 多用户隔离怎么加？| Week 5-6 用 metadata 过滤 |
| 文档更新了怎么办？| 删除旧 chunk + 重新索引（Week 4 会讲）|
| Reranker 太慢怎么办？| 缓存 / 减少候选 / 用更小模型 |
| 怎么评估检索效果？| Recall@K / MRR / NDCG（Week 5-6 会做） |

---

## ✅ Week 3 通关

恭喜！这一周你已经掌握了 RAG 系统的"R"（Retrieval）。

**沉淀**（建议今天就写）：

- 在 [`笔记/向量数据库选型.md`](../笔记/向量数据库选型.md) 里写下你为什么选 Milvus
- 把本周的 demo 录一段 5 分钟视频，**这是简历项目的预热**

下周（Week 4）我们做完整 RAG 闭环：**文档处理 + 智能分片 + Advisor + 调优**。

---

## 🔗 相关链接

- ⬅️ [Day 4 · 混合检索与 Reranker](./Day4-混合检索与Reranker.md)
- ⬆️ [Week 3 总览](./README.md)
- ➡️ [Week 4 · RAG 核心机制](../Week4-RAG核心机制/README.md)
- 📂 [项目骨架 03-doc-search](../项目/03-doc-search/)
