# Day 4 · 混合检索与 Reranker（让检索不再"跑偏"）

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解为什么纯向量不够，能写一个"BM25 + 向量 + 重排"的检索流水线

---

## 0. 心法（5 分钟）

> **纯向量检索是"语义近似"，但有时候你需要"精确命中"。**

举个真实例子：

```
用户问：  "请帮我查一下订单 X-2024-0815 的物流状态"

纯向量召回 Top-3：
  ① "订单查询接口的设计文档…"          ← 跟 "订单" 语义近，但没用
  ② "X-2024 系列产品发布…"             ← 跟 "X-2024" 表面像，但完全错
  ③ "物流追踪服务架构…"                 ← 跟 "物流" 语义近，但没用

正确答案应该是：含 "X-2024-0815" 这个精确 token 的文档
```

**纯向量的弱点**：

- 对**精确词**（订单号、人名、商品 SKU）不敏感
- 对**否定**（"不是 RAG 的项目"）经常翻车
- 长文本检索时**关键短语会被稀释**

**解法**：**混合检索 = 向量召回 + 关键词召回 + 重排**。

---

## 1. 一图速记：RAG 检索三段论 ⭐（10 分钟）

```
                    用户问题
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
   ┌──────────┐                 ┌──────────┐
   │ 向量召回 │                 │  BM25    │   ← 第一阶段：召回（要快、要全）
   │ (语义)   │                 │ (关键词) │
   │ Top-30   │                 │ Top-30   │
   └─────┬────┘                 └─────┬────┘
         │                            │
         └─────────────┬──────────────┘
                       ▼
                 ┌──────────┐
                 │   合并   │      ← RRF / 加权合并
                 │ Top-50   │
                 └─────┬────┘
                       │
                       ▼
              ┌──────────────────┐
              │   Reranker 重排  │   ← 第二阶段：精排（要准）
              │ (Cross-Encoder)  │
              │   Top-5          │
              └─────────┬────────┘
                        │
                        ▼
                  喂给 LLM 生成
```

> 💡 **三段论口诀**：**召回拿 Top-30 + Top-30，合并到 Top-50，重排到 Top-5**。

---

## 2. BM25：经典关键词召回（15 分钟）

> BM25 是 ES 默认排序算法，**搜了 25 年的搜索仍然是它**——非常稳。

### 2.1 直觉

BM25 给每个文档算一个分数：

```
某个 query word 在文档里出现得越多 → 加分
但出现越多边际收益递减     → 加分有上限
文档越长，单纯"出现多"越廉价 → 长度归一化
```

不需要会推导公式，**知道它擅长"精确词命中"**就够。

### 2.2 在 Spring AI 里怎么做

| 选项 | 怎么做 |
|------|--------|
| **A：Elasticsearch 8 BM25** ⭐ | ES 自带，混合最丝滑（也支持向量）|
| B：Lucene 直接用 | 有 Java 库，可单机跑 |
| C：自己写简易 BM25 | 中小项目可行 |

> 🎯 **简历项目推荐路线**：**Milvus（向量）+ ES（BM25）+ 自己写合并** 或 **直接用 ES 8 同时管两路**。
>
> 本周 Day 5 整合时**演示自己写一个简易合并**，让你彻底搞懂原理。

### 2.3 一段简易"伪 BM25"（够用即可）

如果不想引入 ES，可以先用一个朴素打分作占位：

```java
public static double naiveBm25(String query, String content) {
    // ⚠️ 这是教学用的"近似"，生产请用 Lucene/ES
    String q = query.toLowerCase();
    String c = content.toLowerCase();
    double score = 0;
    for (String term : q.split("\\s+")) {
        if (term.isBlank()) continue;
        int count = 0, idx = 0;
        while ((idx = c.indexOf(term, idx)) != -1) { count++; idx++; }
        // 加分上限避免堆词
        score += Math.min(count, 5) * Math.log(1.0 + 100.0 / Math.max(c.length(), 1));
    }
    return score;
}
```

> 💡 **生产请直接走 ES**，这段代码只用来"理解 BM25 大概在干啥"。

---

## 3. 合并策略：RRF（10 分钟）⭐

> RRF（Reciprocal Rank Fusion，互逆排名融合）是工业界融合多路召回的事实标准。

### 3.1 公式（一句话能讲清）

```
对每个候选文档 d：
    score(d) = Σ  1 / (k + rank_i(d))
              i  ↑
                第 i 路召回里 d 的排名（从 1 开始）

k = 60（论文经验值，几乎不用调）
```

### 3.2 为什么这么设计

- 不需要不同召回的分数同尺度（向量 cos 是 [0,1]，BM25 是 [0, ∞]——直接相加会爆）
- 只看**排名**，对异常分数有鲁棒性
- 公式简单，几行代码搞定

### 3.3 Java 实现

```java
public static List<String> rrf(List<List<String>> rankedLists, int k, int topN) {
    Map<String, Double> score = new HashMap<>();
    for (List<String> list : rankedLists) {
        for (int rank = 0; rank < list.size(); rank++) {
            String docId = list.get(rank);
            score.merge(docId, 1.0 / (k + rank + 1), Double::sum);
        }
    }
    return score.entrySet().stream()
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
            .limit(topN)
            .map(Map.Entry::getKey)
            .toList();
}
```

> 🎯 **这 10 行就是工业界 RAG 的"融合层"标准答案**——背下来。

---

## 4. Reranker：精排的灵魂（15 分钟）

### 4.1 召回 vs 重排：本质区别

| 阶段 | 模型类型 | 速度 | 质量 |
|------|---------|------|------|
| **召回** | Bi-Encoder（向量化两边后算余弦）| **极快** | 一般 |
| **重排** | Cross-Encoder（query 和 doc 一起喂模型）| 慢 | **极高** |

直觉：

```
Bi-Encoder：
    query  → vector_q
    doc    → vector_d
    score = cos(vector_q, vector_d)
    （两边各自向量化，速度极快，但精度损失）

Cross-Encoder：
    [query, doc] → 一起喂 BERT → 输出一个相关性分数
    （把 query 和 doc 拼起来一起算，精度极高，但慢）
```

> 🎯 **为什么不直接全部用 Cross-Encoder**？算 100 万文档要算 100 万次 BERT 前向——**慢到不能用**。
>
> **正确做法**：Bi-Encoder 先粗筛 Top-50（快），Cross-Encoder 再精排到 Top-5（准）。

### 4.2 主流 Reranker 模型

| 模型 | 厂商 | 推荐度 |
|------|------|--------|
| **bge-reranker-v2-m3** ⭐ | 智源 | ⭐⭐⭐⭐⭐（开源中文 SOTA）|
| bge-reranker-large | 智源 | ⭐⭐⭐⭐（资源紧时用） |
| Cohere Rerank-v3 | Cohere | ⭐⭐⭐⭐⭐（API，国际）|
| 通义 gte-rerank | 阿里 | ⭐⭐⭐⭐（API，国内首选）|

### 4.3 Spring AI 里调通义 Rerank（最简）

通义有 Rerank API（`gte-rerank`），HTTP 直接调：

```java
@Service
public class RerankService {

    private final WebClient client = WebClient.builder()
            .baseUrl("https://dashscope.aliyuncs.com")
            .build();

    @Value("${spring.ai.dashscope.api-key}")
    private String apiKey;

    public record RerankItem(int index, double score, String text) {}

    /** topN：要返回前几条 */
    public List<RerankItem> rerank(String query, List<String> docs, int topN) {
        Map<String, Object> body = Map.of(
                "model", "gte-rerank",
                "input", Map.of("query", query, "documents", docs),
                "parameters", Map.of("top_n", topN, "return_documents", true)
        );

        Map<?, ?> resp = client.post()
                .uri("/api/v1/services/rerank/text-rerank/text-rerank")
                .header("Authorization", "Bearer " + apiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        // 解析返回（结构以官方文档为准）
        List<Map<String, Object>> results = (List<Map<String, Object>>)
                ((Map<?, ?>) resp.get("output")).get("results");

        List<RerankItem> out = new ArrayList<>();
        for (Map<String, Object> r : results) {
            int idx = ((Number) r.get("index")).intValue();
            double score = ((Number) r.get("relevance_score")).doubleValue();
            String text = docs.get(idx);
            out.add(new RerankItem(idx, score, text));
        }
        return out;
    }
}
```

> 💡 **本地化部署路线**：下载 `bge-reranker-v2-m3` ONNX，用 `onnxruntime-java` 推理；或者部署 `xinference` 提供 OpenAI 兼容接口。

### 4.4 Reranker 的"实战取值"

| 阶段 | 数量 | 备注 |
|------|------|------|
| 向量召回 | Top-20 ~ Top-30 | 别少于 20 |
| BM25 召回 | Top-20 ~ Top-30 | 同上 |
| RRF 合并 | Top-30 ~ Top-50 | 留足重排余量 |
| Reranker 输出 | **Top-3 ~ Top-5** | **最终塞 Prompt 的就这几条** |

---

## 5. 完整流水线（Java 伪码）

```java
public List<String> hybridSearch(String query) {
    // ① 向量召回
    List<Document> vecHits = vectorStore.similaritySearch(
            SearchRequest.query(query).withTopK(30)
    );
    List<String> vecIds = vecHits.stream().map(Document::getId).toList();

    // ② BM25 召回（自己写或调 ES）
    List<String> bm25Ids = bm25Service.search(query, 30);

    // ③ RRF 合并
    List<String> mergedIds = rrf(List.of(vecIds, bm25Ids), 60, 30);

    // ④ 拉取原文（按 id）
    List<String> mergedDocs = docRepo.fetchByIds(mergedIds);

    // ⑤ Reranker 精排
    List<RerankItem> finalHits = rerankService.rerank(query, mergedDocs, 5);

    return finalHits.stream().map(RerankItem::text).toList();
}
```

> 🎯 **这就是工业级 RAG 检索层**——Week 5-6 简历项目里你会真做一遍。

---

## 6. 你应该建立的"语感"

| 现象 | 解释 |
|------|------|
| 用户问"订单 X-2024-0815"，纯向量找不准 | 精确串靠 BM25，向量负责"语义" |
| 重排后 Top-3 比直接 Top-3 准很多 | Cross-Encoder 真的能干 Bi-Encoder 干不了的事 |
| RRF 比"分数加权"更稳 | 不同召回分数尺度天差地别，RRF 只看排名 |
| Top-K 越大不一定越好 | 噪声多，反而干扰 LLM 生成 |
| Reranker 一定要在召回之后 | 顺序不能反，否则速度爆炸 |

---

## 7. 检查清单

- [ ] 默写检索三段论：召回 → 合并 → 重排
- [ ] 解释为什么纯向量不够（举一个精确词检索的反例）
- [ ] 默写 RRF 公式 + 写一遍 Java 实现
- [ ] 解释 Bi-Encoder 和 Cross-Encoder 的根本区别
- [ ] 调通通义 Rerank API（或本地 bge-reranker），输入 query + 5 个 doc，输出排序

完成了 ➡️ [Day 5 · 检索 Demo](./Day5-检索Demo.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · Spring AI VectorStore](./Day3-SpringAI-VectorStore.md)
- ➡️ [Day 5 · 检索 Demo](./Day5-检索Demo.md)
- ⬆️ [Week 3 总览](./README.md)
- 📚 [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- 📚 [通义 Rerank API](https://help.aliyun.com/zh/dashscope/developer-reference/text-rerank-api-details)
- 📚 [RRF 论文（Cormack 2009）](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
