# 八股文 · Spring AI / LangChain4j

> 🎯 **目标**：能用项目语言讲清 Spring AI 与 LangChain4j 的核心抽象与取舍
> 📌 **使用方式**：和你的 Spring AI 项目对照刷，能"指着代码讲"最有效
> 🔁 **关联**：[`03-SpringAI与RAG/`](../../03-SpringAI与RAG/) + [`04-Agent与工程化/`](../../04-Agent与工程化/)

---

## 一、Spring AI 核心抽象 ⭐⭐⭐

### Q1：ChatClient 和 ChatModel 区别？为什么 Spring AI 要分两层？

**60 秒答**：

> 这是 Spring AI **最核心的设计**：
>
> - **`ChatModel`** = 底层模型客户端，**直接发请求给 OpenAI/通义/Ollama**，
>   只负责"我把这个 prompt 发出去，把响应拿回来"，**无状态、无增强**。
>
> - **`ChatClient`** = 高层 Fluent API，**包了一层 Builder + Advisor 链**，
>   提供 prompt 模板、记忆、RAG、Function Calling、流式等开发体验。
>
> **类比**：`ChatModel` ≈ JDBC，`ChatClient` ≈ JdbcTemplate。

**代码对照**：

```java
// ChatModel：底层
ChatModel chatModel = new OpenAiChatModel(...);
ChatResponse response = chatModel.call(new Prompt("你好"));

// ChatClient：高层（推荐）
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultSystem("你是 Java 老兵")
    .defaultAdvisors(new MessageChatMemoryAdvisor(memory))
    .build();
String answer = chatClient.prompt("你好").call().content();
```

**面试加分**：

> "我项目里 90% 场景用 ChatClient，只有需要细粒度控制 token 用量统计、
> 自定义 retry 策略时才直接用 ChatModel。"

---

### Q2：什么是 Advisor？给我一个真实使用场景

**60 秒答**：

> Advisor 是 Spring AI 的**拦截器机制**，类似 Spring AOP，
> 在每次 `chatClient.prompt()` 调用前后插入逻辑，链式增强。
>
> **三大内置 Advisor**：
>
> 1. **`MessageChatMemoryAdvisor`** —— 自动注入历史消息（多轮对话）
> 2. **`QuestionAnswerAdvisor`** —— 自动 RAG 检索 + 注入文档（核心）
> 3. **`SafeGuardAdvisor`** —— 输入审查，命中敏感词直接拦截

**真实场景代码**：

```java
String answer = chatClient.prompt(question)
    .advisors(
        new MessageChatMemoryAdvisor(memory),       // 注入历史
        new QuestionAnswerAdvisor(vectorStore),     // 注入 RAG 文档
        new TokenUsageRecorderAdvisor(meterReg),    // 自定义：token 计费
        new SourceCitationAdvisor()                 // 自定义：抽取来源
    )
    .call().content();
```

**为什么 Advisor 很美**：

> 业务代码只关心"问问题"，**记忆/RAG/计费/审计全在 Advisor 链里**，
> 各自单一职责，按需组合，不污染业务。
> 我项目里写了 4 个自定义 Advisor，**Token 统计 / 来源引用 / Prompt Injection 检测 / 慢查询日志**。

---

### Q3：Spring AI 的 VectorStore 抽象设计如何？

**60 秒答**：

> `VectorStore` 是统一的向量库抽象，把 Milvus / Qdrant / pgvector / ES /
> Redis Stack / Chroma / Weaviate 全部抹平为同一个接口：
>
> ```java
> interface VectorStore extends DocumentWriter {
>     void add(List<Document> documents);
>     void delete(List<String> ids);
>     List<Document> similaritySearch(SearchRequest request);
> }
> ```
>
> **价值**：换向量库 = 换一行配置，业务代码 0 改动。

**对比 LangChain4j**：

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| 接口名 | `VectorStore` | `EmbeddingStore` |
| 写入 | `add(documents)` | `addAll(embeddings, segments)` |
| 检索 | `similaritySearch(req)` | `search(query)` |

**取舍**：Spring AI 把 Embedding 隐藏在背后（自动调 EmbeddingModel），LC4j 暴露给你（更细粒度）。

---

## 二、Function Calling 在 Spring AI 中的实现

### Q4：Spring AI 怎么注册 Function？

**60 秒答**：

> 三种方式，**用法递进**：

**方式 1：`@Bean Function<I, O>`**（最早）

```java
@Bean
@Description("查询天气")
public Function<WeatherRequest, WeatherResponse> getWeather() {
    return req -> weatherService.query(req.city());
}
```

**方式 2：`@Tool` 注解**（Spring AI 1.0 推荐）

```java
public class WeatherTools {
    @Tool(description = "查询指定城市的实时天气")
    public WeatherResponse getWeather(@ToolParam(description = "城市名") String city) {
        return weatherService.query(city);
    }
}

// 使用
chatClient.prompt(q).tools(new WeatherTools()).call();
```

**方式 3：动态 ToolCallback**（运行时拼装）

```java
ToolCallback dynamicTool = ToolCallback.builder()
    .name("get_user_orders")
    .description(...)
    .inputSchema(...)
    .toolFunction(args -> orderService.list(args.get("userId")))
    .build();
```

### Q5：Function Calling 的常见坑？

> 4 大坑：
>
> 1. **参数描述不写或写不清** → 模型瞎传参数
>    - ✅ 每个参数都有 `@ToolParam(description=...)`
>
> 2. **大对象当返回值** → 上下文爆炸
>    - ✅ 返回小对象 + 必要字段，过滤掉嵌套的 List<Map>
>
> 3. **Tool 业务异常没兜底** → 整个对话挂掉
>    - ✅ Tool 内部 try-catch，返回 `{"error":"xxx"}` 让模型重试或降级
>
> 4. **Tool 选错没有兜底** → 用户问"今天股市"，模型瞎选 `getWeather`
>    - ✅ 在 system prompt 里强约束"无相关 tool 时直接回答"

---

## 三、Memory 记忆机制 ⭐

### Q6：Spring AI 三种 Memory 实现？

**60 秒答**：

| 实现 | 存储 | 适用 | 局限 |
|------|------|------|------|
| `InMemoryChatMemory` | JVM 堆 | 单机 demo / 测试 | 重启丢失 / 不能集群 |
| `JdbcChatMemory` | MySQL | 中小并发 + 强一致 | 高并发查 DB 慢 |
| **`RedisChatMemory`**（自实现）| Redis List/ZSet | 生产推荐 | 需要持久化策略 |

**Redis 实现的关键设计**：

```java
public class RedisChatMemory implements ChatMemory {
    public void add(String conversationId, List<Message> messages) {
        String key = "chat:msg:" + conversationId;
        redis.opsForList().rightPushAll(key, serialize(messages));
        redis.expire(key, 7, TimeUnit.DAYS);  // 7 天过期
    }
    public List<Message> get(String conversationId, int lastN) {
        String key = "chat:msg:" + conversationId;
        Long size = redis.opsForList().size(key);
        return redis.opsForList().range(key, Math.max(0, size - lastN), size);
    }
}
```

### Q7：Memory 怎么避免 Token 爆炸？

> **3 招组合**：
>
> 1. **窗口截断**：只保留最近 N 轮
> 2. **上下文压缩**：早期对话用模型总结成 200 字摘要 + 最近 3 轮原文
> 3. **关键事实抽取**：抽取"用户说他叫张三、住北京"等事实，永久存
>
> **我项目里**：3 招组合，最近 3 轮原文 + 历史摘要 + 用户档案，平均 prompt 800 token 内。

---

## 四、Spring AI vs LangChain4j 对比 ⭐⭐

### Q8：Spring AI 和 LangChain4j 怎么选？

**60 秒答**：

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| **定位** | Spring 生态深度集成 | 独立 LLM 应用框架 |
| **AOP 增强** | Advisor 机制 ⭐ | 没有同等抽象 |
| **声明式 AI Service** | 有但弱 | **`@AiService` 强大** ⭐ |
| **RAG** | `QuestionAnswerAdvisor` 一行 | 需手动拼 RetrievalAugmentor |
| **Agent 模式** | 弱（只有 Function Calling）| **内置 ReAct / Plan-and-Execute** ⭐ |
| **MCP 支持** | 1.0 已支持 | 已支持 |
| **国内适配** | 通义/DeepSeek/Ollama 都有 | 同样齐全 |

**实战选择**：

> - **Spring 生态深度项目**（Spring Boot 3 + Cloud + Security）→ Spring AI
> - **复杂 Agent 场景**（多步推理、多 Agent 协作）→ LangChain4j
> - **生产推荐 Spring AI 做应用主框架，LangChain4j 做 Agent 编排子模块**，
>   两者通过 `ChatModel` / `EmbeddingModel` 共用底层

### Q9：LangChain4j 的 `@AiService` 神在哪？

```java
public interface AssistantService {
    @SystemMessage("你是 Java 资深架构师")
    @UserMessage("根据如下需求生成代码: {{requirement}}")
    String generateCode(@V("requirement") String req);
}

// 使用
AssistantService service = AiServices.builder(AssistantService.class)
    .chatLanguageModel(model)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
    .tools(new WeatherTools())
    .contentRetriever(retriever)
    .build();

String code = service.generateCode("一个生产者消费者");
```

> **声明式 + 类型安全 + 自动注入 Memory/Tools/RAG**，
> Spring 生态里相当于把 OpenFeign 风格搬到 LLM 调用。

---

## 五、Prompt Engineering 在框架里的体现

### Q10：怎么写 Prompt Template？

**Spring AI 写法**：

```java
PromptTemplate template = new PromptTemplate("""
    你是 {role} 助手。
    用户问题：{question}
    请用不超过 {maxLen} 字回答。
    """);
Prompt prompt = template.create(Map.of(
    "role", "Java 资深架构师",
    "question", q,
    "maxLen", 200
));
String answer = chatClient.prompt(prompt).call().content();
```

**关键设计**：
- **占位符** `{var}`
- **多行用 Java 17 文本块**
- **复杂场景用 PromptTemplateRenderer + Mustache/JTE 引擎**

### Q11：System / User / Assistant 三种 Role 区别？

> | Role | 作用 | 工程意义 |
> |------|------|---------|
> | **system** | 模型人设 + 规则 | **业务方写死**，用户改不了 |
> | **user** | 用户输入 | 每次变化 |
> | **assistant** | 模型历史回复 | 拼上下文用 |
> | **tool** | Function Calling 结果 | 模型看到后继续生成 |
>
> **安全性**：很多 Prompt Injection 攻击就是想让用户说的话变成"system"指令——
> 防御方式是 **system 必须由代码硬编码 + 永远不能从用户拼**。

---

## 六、流式实现 ⭐

### Q12：Spring AI 怎么写流式接口？

**WebFlux 版（推荐）**：

```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> streamChat(@RequestParam String q) {
    return chatClient.prompt(q).stream().content();
}
```

**MVC + SseEmitter 版**：

```java
@GetMapping("/chat/stream")
public SseEmitter chat(@RequestParam String q) {
    SseEmitter emitter = new SseEmitter(30_000L);
    chatClient.prompt(q).stream().content()
        .subscribe(
            chunk -> { try { emitter.send(chunk); } catch(IOException e) { emitter.completeWithError(e); } },
            emitter::completeWithError,
            emitter::complete
        );
    return emitter;
}
```

**坑**：

- Nginx 反向代理要 `proxy_buffering off`
- 前端用 `EventSource` API
- 网络断了要兜底（自动重连 + Last-Event-ID）

---

## 七、自测清单 ✅

- [ ] ChatClient vs ChatModel 区别能讲清楚
- [ ] Advisor 机制能用"AOP 类比"讲明白
- [ ] 三种 Function 注册方式能写代码
- [ ] Memory 三种实现的取舍 + 项目实际选择
- [ ] Spring AI vs LangChain4j 选型决策
- [ ] 流式接口 WebFlux/MVC 两种写法都能写
- [ ] 每题能补一句"项目里实际怎么用"

---

## 🔗 下一站

- [`./八股文-RAG与Agent.md`](./八股文-RAG与Agent.md)
- [`./八股文-工程化.md`](./八股文-工程化.md)
- [`../系统设计/`](../系统设计/)
