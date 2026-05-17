# Day 3 · Spring AI RAG 组件全家桶

> ⏱️ 时间：1.5 小时
> 🎯 目标：用 Spring AI 的 ETL Pipeline + Advisor，把 Day 1-2 的成果丝滑串起来

---

## 0. 心法（5 分钟）

> **Spring AI 把 RAG 流程拆成了 4 类 Bean：Reader / Transformer / Writer / Advisor。**

```
   File / URL                                Question
       │                                         │
       ▼                                         ▼
  DocumentReader        +Advisor──────────►  ChatClient
       │                    │                    │
       ▼                    │                    │
  DocumentTransformer       │   QuestionAnswerAdvisor
       │                    │   = 检索 + 拼 prompt
       ▼                    │
  DocumentWriter            │
  (= VectorStore.add)       │
                            │
                       VectorStore  ◄──────────┘
```

**今天就把这套机制吃透**——Week 5-6 简历项目里你不再需要手写 RAG 主流程。

---

## 1. ETL Pipeline 全家福（25 分钟）

### 1.1 三个接口

| 接口 | 用途 |
|------|------|
| `DocumentReader extends Supplier<List<Document>>` | 读：从文件/URL 拿 Document |
| `DocumentTransformer extends Function<List<Document>, List<Document>>` | 变换：分片、加 metadata、清洗 |
| `DocumentWriter extends Consumer<List<Document>>` | 写：往 VectorStore 写 |

> 🎯 **看到 `Supplier / Function / Consumer` 没有？** Spring AI 故意用 JDK 函数式接口——**任何 lambda 都能当 Reader/Transformer/Writer**。

### 1.2 一个完整 ETL（推荐写法）

```java
@Service
@RequiredArgsConstructor
public class IndexingPipeline {

    private final VectorStore vectorStore;

    public int index(Resource resource, Map<String, Object> extraMeta) {
        // ① Read
        var reader = new TikaDocumentReader(resource);
        List<Document> raw = reader.get();

        // ② Transform：先加元数据
        List<Document> withMeta = raw.stream()
                .map(d -> {
                    Map<String, Object> m = new HashMap<>(d.getMetadata());
                    m.putAll(extraMeta);
                    return new Document(d.getContent(), m);
                })
                .toList();

        // ③ Transform：分片
        var splitter = new TokenTextSplitter(500, 100, 5, 5000, true);
        List<Document> chunks = splitter.apply(withMeta);

        // ④ Write
        vectorStore.add(chunks);
        return chunks.size();
    }
}
```

### 1.3 把 Splitter 升级成自定义的（用 Day 2 写的 Recursive）

```java
public class RecursiveSplitterTransformer implements DocumentTransformer {

    private final RecursiveCharacterSplitter splitter;

    public RecursiveSplitterTransformer(int chunkSize, int overlap) {
        this.splitter = new RecursiveCharacterSplitter(chunkSize, overlap);
    }

    @Override
    public List<Document> apply(List<Document> docs) {
        List<Document> result = new ArrayList<>();
        for (Document d : docs) {
            int seq = 0;
            for (String chunk : splitter.split(d.getContent())) {
                Map<String, Object> meta = new HashMap<>(d.getMetadata());
                meta.put("chunk_seq", seq++);
                result.add(new Document(chunk, meta));
            }
        }
        return result;
    }
}
```

替换前面的 `TokenTextSplitter` 即可：

```java
List<Document> chunks = new RecursiveSplitterTransformer(500, 100).apply(withMeta);
```

---

## 2. Advisor 机制：链式增强 ChatClient（20 分钟）

> Advisor 是 Spring AI 1.0 的核心抽象，**理解了 Advisor，你就理解了 Spring AI 的 80%**。

### 2.1 它在做什么

```java
chatClient.prompt()
        .user("...")
        .advisors(new QuestionAnswerAdvisor(vectorStore))
        .call()
```

**`advisors(...)` 把一个或多个 Advisor 串成一条链**——每个 Advisor 都能：

```
请求时：  改写 prompt（注入 RAG 上下文 / 加权限校验）
响应时：  改写 result（提取引用 / 记录审计日志）
```

### 2.2 类比：你已经懂的 Spring 概念

```
Servlet Filter   ↔  Advisor
HandlerInterceptor ↔ Advisor
AOP @Around    ↔  Advisor
```

> 💡 **Advisor 就是 LLM 调用的 AOP**——你在 Spring 里用过的那个味儿。

### 2.3 内置常用 Advisor

| Advisor | 干什么 |
|---------|-------|
| `QuestionAnswerAdvisor` | RAG：检索 + 拼 prompt |
| `MessageChatMemoryAdvisor` | 多轮对话历史 |
| `PromptChatMemoryAdvisor` | 把历史塞 system prompt |
| `SafeGuardAdvisor` | 黑词过滤 / 越狱防护 |
| `SimpleLoggerAdvisor` | 把 prompt 和 response 打日志 |

### 2.4 一个最简 RAG ChatClient

```java
@Service
public class RagService {

    private final ChatClient chatClient;

    public RagService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
                .defaultSystem("""
                        你是一个公司知识库助手。
                        请基于检索到的资料回答用户问题。
                        如果资料里没有答案，请说"我不确定"。
                        """)
                .defaultAdvisors(
                        new QuestionAnswerAdvisor(vectorStore,
                                SearchRequest.defaults().withTopK(5)),
                        new SimpleLoggerAdvisor()
                )
                .build();
    }

    public String ask(String question) {
        return chatClient.prompt().user(question).call().content();
    }

    public Flux<String> askStream(String question) {
        return chatClient.prompt().user(question).stream().content();
    }
}
```

---

## 3. QuestionAnswerAdvisor 内部到底做了什么（15 分钟）

> 这是面试高频题——**能讲清楚等于真懂 RAG**。

伪代码版（Spring AI 1.0.x）：

```java
class QuestionAnswerAdvisor {

    public AdvisedResponse aroundCall(AdvisedRequest req, AdvisorChain chain) {

        // ① 取用户问题
        String question = req.userText();

        // ② 检索
        List<Document> docs = vectorStore.similaritySearch(
                SearchRequest.query(question).withTopK(topK)
        );

        // ③ 拼接成上下文
        String context = docs.stream()
                .map(Document::getContent)
                .collect(Collectors.joining("\n\n"));

        // ④ 改写 user prompt
        String enriched = """
                请根据以下文档回答问题。

                文档：
                %s

                问题：%s
                """.formatted(context, question);

        // ⑤ 把 docs 塞进 advisor context（响应阶段还能拿到）
        req.adviseContext().put("documents", docs);

        // ⑥ 调用下一环
        return chain.nextAroundCall(req.withUserText(enriched));
    }
}
```

> 🎯 **关键认知**：Advisor 在 LLM 调用**之前**改 prompt，**之后**还能拿到检索到的 docs——这就是 Day 4 做"来源引用"的入口。

---

## 4. 自定义一个 Advisor（10 分钟）

> 学到这里你就有"扩展能力"了。

例：写一个 `RequestStatsAdvisor`，记录每次请求的 token 数。

```java
@Component
@Slf4j
public class RequestStatsAdvisor implements RequestAdvisor, ResponseAdvisor {

    @Override
    public AdvisedRequest adviseRequest(AdvisedRequest req, Map<String, Object> ctx) {
        ctx.put("startTime", System.currentTimeMillis());
        ctx.put("userTextLength", req.userText().length());
        return req;
    }

    @Override
    public ChatResponse adviseResponse(ChatResponse resp, Map<String, Object> ctx) {
        long elapsed = System.currentTimeMillis() - (long) ctx.get("startTime");
        Usage usage = resp.getMetadata().getUsage();
        log.info("LLM call: elapsed={}ms, promptTokens={}, generationTokens={}",
                elapsed,
                usage.getPromptTokens(),
                usage.getGenerationTokens());
        return resp;
    }

    @Override public String getName() { return "request-stats"; }
    @Override public int getOrder() { return Integer.MAX_VALUE; }    // 最后执行
}
```

把它加到 ChatClient：

```java
ChatClient.Builder builder ...
        .defaultAdvisors(qaAdvisor, statsAdvisor)
```

> 💡 简历里能写："基于 Spring AI Advisor 链实现请求统计、Token 计费、审计日志、敏感词过滤等横切能力"——**面试官会眼前一亮**。

---

## 5. 最简端到端示例（15 分钟）

把今天学的整合：

```java
@RestController
@RequiredArgsConstructor
public class RagController {

    private final IndexingPipeline indexingPipeline;
    private final RagService ragService;

    @PostMapping("/docs")
    public Map<String, Object> upload(@RequestParam("file") MultipartFile file) throws IOException {
        var resource = new InputStreamResource(file.getInputStream()) {
            @Override public String getFilename() { return file.getOriginalFilename(); }
        };
        int n = indexingPipeline.index(resource, Map.of(
                "filename", file.getOriginalFilename(),
                "uploadedAt", Instant.now().toString()
        ));
        return Map.of("chunks", n);
    }

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestParam String q) {
        return ragService.askStream(q);
    }
}
```

实测：

```bash
# 上传一个 Markdown
curl -X POST -F "file=@docs/晋升手册.md" http://localhost:8080/docs

# 流式问
curl -N "http://localhost:8080/chat/stream?q=晋升流程是什么？"
```

> 🎯 **看到流式输出 + 答案带文档内容 = Day 3 通过**。

---

## 6. 检查清单

- [ ] 用 `Resource → Reader → Transformer → VectorStore` 跑通完整 ETL
- [ ] 解释 Advisor 的角色（用"AOP"或"Filter"类比给面试官听）
- [ ] 默写 `QuestionAnswerAdvisor` 内部 4 步（取问→检索→拼 prompt→调用）
- [ ] 至少自己写过一个 Advisor（哪怕只是打日志）
- [ ] 测一下 `chatClient.stream()` 返回 `Flux<String>`，能 SSE 流式

完成了 ➡️ [Day 4 · 防幻觉与来源引用](./Day4-防幻觉与来源引用.md)

---

## 🔗 相关链接

- ⬅️ [Day 2 · 分片策略](./Day2-分片策略.md)
- ➡️ [Day 4 · 防幻觉与来源引用](./Day4-防幻觉与来源引用.md)
- ⬆️ [Week 4 总览](./README.md)
- 📚 [Spring AI ETL Pipeline](https://docs.spring.io/spring-ai/reference/api/etl-pipeline.html)
- 📚 [Spring AI Advisors API](https://docs.spring.io/spring-ai/reference/api/advisors.html)
