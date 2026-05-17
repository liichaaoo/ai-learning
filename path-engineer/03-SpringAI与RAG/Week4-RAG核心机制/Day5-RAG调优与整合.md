# Day 5 · 整合 Demo · mini-RAG 系统 ⭐

> ⏱️ 时间：2 小时
> 🎯 目标：把 Day 1-4 串成一个能演示的 RAG mini 项目，并完成第一次系统调优
> 📂 项目：[`项目/04-rag-mini/`](../项目/04-rag-mini/)

---

## 0. 心法（5 分钟）

> **本周通关 = 一个能上传文档、流式问答、带来源引用的服务，并且有一组对比调优数据。**

```
Week 3 doc-search：能"找"
+
Week 4 rag-mini：能"答"
=
Week 5-6 知识库项目：能"用"
```

---

## 1. 项目目标规格

```
项目名：rag-mini
位置：项目/04-rag-mini/

技术栈：
  Spring Boot 3 + Spring AI 1.0
  Milvus 2.4
  通义 chat + embedding
  Apache Tika 2.9

接口（最小集）：
  POST /api/docs           上传文档（PDF/Word/MD），自动入库
  GET  /api/docs           列表
  DELETE /api/docs/{id}    删除（含 chunks）
  POST /api/chat           同步问答（含 citations）
  POST /api/chat/stream    流式问答（SSE）
  GET  /api/metrics        本地评测指标
```

---

## 2. 核心代码：RagService（30 分钟）

### 2.1 配置

```yaml
# application.yml
rag:
  top-k: 5
  threshold: 0.5
  chunk-size: 500
  chunk-overlap: 100

spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-plus
          temperature: 0.0           # ⭐ RAG 推荐 0
      embedding:
        options:
          model: text-embedding-v3
    vectorstore:
      milvus:
        client: { host: localhost, port: 19530 }
        collectionName: rag_mini
        embeddingDimension: 1024
        indexType: HNSW
        metricType: COSINE
        initialize-schema: true
```

### 2.2 RagService 主体

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class RagService {

    private final ChatClient.Builder chatClientBuilder;
    private final VectorStore vectorStore;

    @Value("classpath:prompts/qa-system.st")
    private Resource qaTemplate;

    @Value("${rag.top-k:5}")     private int topK;
    @Value("${rag.threshold:0.5}") private double threshold;

    public RagAnswer ask(String question, String tenantId) {
        long t0 = System.currentTimeMillis();

        // ① 检索（带租户过滤）
        var req = SearchRequest.query(question)
                .withTopK(topK).withSimilarityThreshold(threshold);
        if (tenantId != null) {
            req = req.withFilterExpression("tenant_id == '" + tenantId + "'");
        }
        List<Document> docs = vectorStore.similaritySearch(req);

        // ② 拒答兜底
        if (docs.isEmpty()) {
            return new RagAnswer(
                    "我没有在知识库里找到相关信息。",
                    List.of(),
                    System.currentTimeMillis() - t0);
        }

        // ③ 调 LLM
        String answer = chatClientBuilder.build()
                .prompt(new PromptTemplate(qaTemplate).create(Map.of(
                        "documents", renderDocs(docs),
                        "question", question)))
                .call()
                .content();

        long elapsed = System.currentTimeMillis() - t0;
        log.info("RAG ask: q='{}' docs={} elapsed={}ms", question, docs.size(), elapsed);
        return new RagAnswer(answer, toCitations(docs), elapsed);
    }

    public Flux<ServerSentEvent<String>> askStream(String question, String tenantId) {
        var req = SearchRequest.query(question)
                .withTopK(topK).withSimilarityThreshold(threshold);
        if (tenantId != null) {
            req = req.withFilterExpression("tenant_id == '" + tenantId + "'");
        }
        List<Document> docs = vectorStore.similaritySearch(req);

        if (docs.isEmpty()) {
            return Flux.just(ServerSentEvent.<String>builder()
                    .event("answer").data("我没有在知识库里找到相关信息。").build());
        }

        var prompt = new PromptTemplate(qaTemplate).create(Map.of(
                "documents", renderDocs(docs), "question", question));

        Flux<String> answerFlux = chatClientBuilder.build()
                .prompt(prompt).stream().content();

        return answerFlux.map(s -> ServerSentEvent.<String>builder()
                        .event("answer").data(s).build())
                .concatWith(Mono.just(ServerSentEvent.<String>builder()
                        .event("citations")
                        .data(JsonUtil.toJson(toCitations(docs)))
                        .build()));
    }

    private String renderDocs(List<Document> docs) {
        return IntStream.range(0, docs.size())
                .mapToObj(i -> {
                    Document d = docs.get(i);
                    return "[%d] 《%s》第%s页：\n%s".formatted(
                            i + 1,
                            d.getMetadata().getOrDefault("source", "未知"),
                            d.getMetadata().getOrDefault("page_number", "?"),
                            d.getContent());
                })
                .collect(Collectors.joining("\n\n"));
    }

    private List<Citation> toCitations(List<Document> docs) {
        return docs.stream()
                .map(d -> new Citation(
                        d.getId(),
                        (String) d.getMetadata().getOrDefault("source", "未知"),
                        String.valueOf(d.getMetadata().getOrDefault("page_number", "")),
                        d.getContent().substring(0, Math.min(150, d.getContent().length()))))
                .toList();
    }

    public record Citation(String id, String source, String page, String snippet) {}
    public record RagAnswer(String answer, List<Citation> citations, long elapsedMs) {}
}
```

### 2.3 Controller

```java
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class RagController {
    private final IndexingPipeline indexer;
    private final RagService ragService;

    @PostMapping("/docs")
    public Map<String, Object> upload(
            @RequestParam("file") MultipartFile file,
            @RequestHeader(value = "X-Tenant-Id", required = false) String tenantId) throws IOException {
        var resource = new InputStreamResource(file.getInputStream()) {
            @Override public String getFilename() { return file.getOriginalFilename(); }
        };
        Map<String, Object> meta = new HashMap<>();
        meta.put("source", file.getOriginalFilename());
        if (tenantId != null) meta.put("tenant_id", tenantId);
        int n = indexer.index(resource, meta);
        return Map.of("filename", file.getOriginalFilename(), "chunks", n);
    }

    @PostMapping("/chat")
    public RagService.RagAnswer chat(
            @RequestBody Map<String, String> body,
            @RequestHeader(value = "X-Tenant-Id", required = false) String tenantId) {
        return ragService.ask(body.get("q"), tenantId);
    }

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> stream(
            @RequestBody Map<String, String> body,
            @RequestHeader(value = "X-Tenant-Id", required = false) String tenantId) {
        return ragService.askStream(body.get("q"), tenantId);
    }
}
```

---

## 3. 调优实验：RAG 的"对照组"⭐（30 分钟）

> 这一节是**简历项目"准确率提升 30%"数字的来源**——务必做完。

### 3.1 准备测试集

把 Week 4 Day 2 写过的 20 条问题搬来：

```yaml
# tests/eval-set.yaml
- q: "公司晋升流程分几步？"
  expect_keywords: ["三步", "自荐", "述职", "委员会"]
  expect_source: "晋升手册"

- q: "晋升答辩失败可以重新申请吗？"
  expect_keywords: ["可以", "下个周期", "6个月"]
  expect_source: "晋升手册"

# ... 共 20 条
```

### 3.2 评测脚本

```java
@SpringBootTest
class RagEvaluationTest {

    @Autowired RagService rag;

    @Test
    void evaluateConfigs() throws IOException {
        List<TestCase> cases = loadCases("tests/eval-set.yaml");

        // 扫一组配置
        int[][] configs = {
                {3,  500, 50},
                {5,  500, 100},
                {8,  500, 100},
                {5,  300, 30},
                {5,  800, 150}
        };

        for (int[] c : configs) {
            int topK = c[0], chunkSize = c[1], overlap = c[2];
            rebuildIndex(chunkSize, overlap);

            int hit = 0;
            long sumElapsed = 0;
            for (TestCase tc : cases) {
                var ans = rag.ask(tc.q(), null);
                sumElapsed += ans.elapsedMs();
                if (matches(ans, tc)) hit++;
            }
            System.out.printf(
                    "topK=%d size=%d overlap=%d → 命中 %d/%d (%.1f%%) 平均 %dms%n",
                    topK, chunkSize, overlap, hit, cases.size(),
                    100.0 * hit / cases.size(), sumElapsed / cases.size());
        }
    }

    private boolean matches(RagService.RagAnswer ans, TestCase tc) {
        // 关键词命中 + 来源命中（满足任一即视为命中）
        boolean kw = tc.keywords().stream().anyMatch(k -> ans.answer().contains(k));
        boolean src = ans.citations().stream()
                .anyMatch(c -> c.source().contains(tc.source()));
        return kw && src;
    }

    record TestCase(String q, List<String> keywords, String source) {}
}
```

### 3.3 你应该看到的结果（举例）

```
topK=3 size=500 overlap=50  → 命中 13/20 (65.0%) 平均 1230ms
topK=5 size=500 overlap=100 → 命中 18/20 (90.0%) 平均 1450ms   ← 最佳
topK=8 size=500 overlap=100 → 命中 17/20 (85.0%) 平均 2100ms
topK=5 size=300 overlap=30  → 命中 14/20 (70.0%) 平均 1380ms
topK=5 size=800 overlap=150 → 命中 16/20 (80.0%) 平均 1500ms
```

> 🎯 **简历亮点（直接拷过去）**：
>
> 「通过分片参数与召回数对比实验，将 Top-3 命中率从 65% 提升至 90%（基于 20 题人工评测集），P95 延迟控制在 1.5s 以内。」

---

## 4. 演示脚本（10 分钟）⭐

```bash
# ① 起 Milvus
docker compose up -d

# ② 起服务
./mvnw spring-boot:run

# ③ 上传几个文档（用真实公司文档脱敏后的版本）
curl -X POST -F "file=@docs/晋升手册.pdf" http://localhost:8080/api/docs
curl -X POST -F "file=@docs/OKR制度.pdf" http://localhost:8080/api/docs
curl -X POST -F "file=@docs/年假规定.md"  http://localhost:8080/api/docs

# ④ 同步问答
curl -X POST http://localhost:8080/api/chat \
     -H "Content-Type: application/json" \
     -d '{"q":"公司晋升流程是什么？"}'
# 期望：答案 + 引用《晋升手册.pdf 第 3 页》

# ⑤ 流式问答（SSE）
curl -N -X POST http://localhost:8080/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"q":"年假怎么算？"}'

# ⑥ 多租户验证（不同 tenant 看到不同文档）
curl -X POST http://localhost:8080/api/chat \
     -H "X-Tenant-Id: research" \
     -H "Content-Type: application/json" \
     -d '{"q":"研发线考核规则"}'

# ⑦ 故意问个没有的问题，验证拒答
curl -X POST http://localhost:8080/api/chat \
     -d '{"q":"我们公司股票代码是多少？"}'
# 期望："我没有在知识库里找到相关信息。"
```

---

## 5. 录视频 + 写笔记（15 分钟）

### 5.1 录 5 分钟演示视频

简单脚本：

```
1. 介绍项目（30s）："这是一个企业 RAG 知识库 mini 版，做了 X、Y、Z 几件事"
2. 上传文档（30s）：展示 PDF 自动入库 + 分片数
3. 流式提问（90s）：show 流式输出 + 末尾的 citations
4. 拒答演示（30s）：故意问无关问题
5. 性能截图（30s）：测试集上 90% 命中
6. 结尾（30s）："下周会做用户系统、Token 成本控制、压测"
```

### 5.2 在笔记里沉淀

更新 [`笔记/RAG调优技巧.md`](../笔记/RAG调优技巧.md)（本周末写，下周补完）：

- 我的最佳分片配置 + 实验数据
- 我的 system prompt 模板（防幻觉版）
- 评测集设计经验

---

## 6. 出关验收（Week 4 通过线）

跑通 7 个动作 = Week 4 通过：

- [ ] 上传 PDF 自动解析 + 分片入库
- [ ] 流式问答：用户看到一个字一个字输出
- [ ] 答案末尾显示来源引用（含文件名 + 页码）
- [ ] 找不到相关文档时礼貌拒答
- [ ] 多租户：不同 X-Tenant-Id 看到不同范围
- [ ] 跑过对比实验，得出至少 2 组配置的命中率对比
- [ ] 录了 5 分钟演示视频

---

## 7. 思考与延伸

| 问题 | 提示 |
|------|------|
| 大文件上传卡顿怎么办？| 异步入库 + 状态查询接口（Week 5-6 做） |
| 怎么做"答案缓存"？| Redis + (问题向量, answer)（Week 5-6 做）|
| 上传重复文件怎么去重？| 文件哈希 + 段落哈希双重校验 |
| 知识库太大查询慢？| Partition 分区 / 提前过滤 metadata |
| 答案"看起来对但实际错"怎么办？| LLM-as-Judge / 关键事实抽取校验 |

---

## ✅ Week 4 通关

恭喜！这一周你做出了完整的 mini RAG。

**下周（Week 5-6）**：基于这个 mini 版升级为**简历项目级**——

```
新增能力：
+ 多用户系统（注册 / 登录 / JWT）
+ 历史对话（持久化 + 多轮）
+ 多模型路由（GPT-4 / 通义按场景）
+ Token 用量统计 + 成本告警
+ 异步入库 + 任务进度
+ 简单前端（React 或 Postman 都行）
+ Docker Compose 一键部署
+ 性能压测报告
+ GitHub 开源 + 技术博客
```

**这是你简历的灵魂项目。**

---

## 🔗 相关链接

- ⬅️ [Day 4 · 防幻觉与来源引用](./Day4-防幻觉与来源引用.md)
- ⬆️ [Week 4 总览](./README.md)
- ➡️ [Week 5-6 · 企业 RAG 知识库](../Week5-6-企业RAG知识库/README.md)
- 📂 [项目骨架 04-rag-mini](../项目/04-rag-mini/)
