# Spring AI 入门笔记

## 一、Spring AI 是什么

**Spring 官方推出的 AI 应用开发框架**，类似 Java 版的 LangChain。

- 🏢 出品方：Pivotal / VMware / Spring 官方团队
- 📅 发布：2024 年 GA
- 🔧 当前版本：1.0.x（2026.5 已稳定）
- 🎯 定位：**让 Java 开发者用 Spring 的方式接入 AI 能力**

### 它解决了什么问题

| 之前痛点 | Spring AI 怎么解决 |
|---------|------------------|
| 不同模型 SDK 不兼容（OpenAI/Claude/通义...） | 统一 `ChatClient` 抽象 |
| 流式响应难处理 | 原生支持 Reactor `Flux` |
| RAG 流程复杂 | 内置 `VectorStore`、`DocumentReader`、`Advisor` |
| Function Calling 各家不一样 | 统一 `@Tool` 注解 |
| Prompt 模板硬编码 | `PromptTemplate` |

---

## 二、核心抽象（必懂）

### 1. ChatClient（对话客户端）⭐ 用得最多

```java
@Autowired
private ChatClient chatClient;

String response = chatClient.prompt()
    .user("你好，介绍下自己")
    .call()
    .content();
```

### 2. ChatModel（底层模型接口）
直接对接具体模型，一般通过 ChatClient 间接使用。

### 3. EmbeddingModel
把文本转成向量，用于 RAG。
```java
EmbeddingResponse response = embeddingModel.embedForResponse(
    List.of("Spring AI 真好用")
);
```

### 4. VectorStore
向量存储抽象，已支持 Milvus、Qdrant、Redis、PgVector 等。

### 5. ImageModel / TranscriptionModel
图片生成、语音转文字。

### 6. Advisor（拦截器/增强器）
在请求前后做加工，比如自动加 RAG 上下文、记忆等。

---

## 三、5 分钟跑通 Hello World

### 1. 项目依赖（Maven）

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</parent>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>1.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <!-- 选一个模型起步：OpenAI / 通义 / Claude / Ollama -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
    </dependency>
</dependencies>
```

### 2. 配置（application.yml）

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      base-url: https://api.openai.com   # 国产替代可改这里
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.7
```

### 3. Controller

```java
@RestController
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    @GetMapping("/chat")
    public String chat(@RequestParam String q) {
        return chatClient.prompt()
            .user(q)
            .call()
            .content();
    }
}
```

### 4. 启动 + 测试
```bash
curl "http://localhost:8080/chat?q=用一句话介绍 Spring AI"
```

✅ 你的第一个 AI 应用就跑起来了。

---

## 四、必学进阶用法

### 1. 流式响应（让用户看到字一个一个蹦出来）

```java
@GetMapping(value = "/chat-stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> stream(@RequestParam String q) {
    return chatClient.prompt()
        .user(q)
        .stream()
        .content();
}
```

### 2. Prompt 模板（参数化）

```java
String response = chatClient.prompt()
    .user(u -> u.text("把 {language} 翻译成中文：{text}")
                .param("language", "English")
                .param("text", "Hello World"))
    .call()
    .content();
```

### 3. 系统提示词（System Prompt）

```java
String response = chatClient.prompt()
    .system("你是一个专业的 Java 资深工程师，回答简洁专业")
    .user(question)
    .call()
    .content();
```

### 4. Function Calling（让 AI 调你的方法）⭐ 重点

```java
@Service
public class WeatherService {

    @Tool(description = "查询某个城市的天气")
    public String getWeather(@ToolParam(description = "城市名") String city) {
        // 调用真实天气 API
        return city + " 当前 25°C，晴天";
    }
}

// 使用：
String response = chatClient.prompt()
    .user("北京今天天气怎么样？")
    .tools(weatherService)        // 把 Service 注册为工具
    .call()
    .content();
// AI 会自动调用 getWeather("北京")
```

### 5. 输出转 Java 对象

```java
record ActorFilms(String actor, List<String> films) {}

ActorFilms result = chatClient.prompt()
    .user("生成一个虚构演员和他的 5 部电影")
    .call()
    .entity(ActorFilms.class);     // 直接拿到 Java 对象
```

### 6. RAG 增强（最有用的功能之一）

```java
@Bean
public ChatClient chatClient(ChatClient.Builder builder, VectorStore vectorStore) {
    return builder
        .defaultAdvisors(new QuestionAnswerAdvisor(vectorStore))  // 自动 RAG
        .build();
}

// 之后所有 chatClient 调用都会自动从向量库检索相关内容
```

---

## 五、常见模型接入

### OpenAI（标杆）
```yaml
spring.ai.openai.api-key: sk-xxx
spring.ai.openai.chat.options.model: gpt-4o-mini
```

### 通义千问（国产首选）
```xml
<dependency>
    <groupId>com.alibaba.cloud.ai</groupId>
    <artifactId>spring-ai-alibaba-starter</artifactId>
    <version>1.0.0-M3.1</version>
</dependency>
```

### Claude（Anthropic）
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-anthropic-spring-boot-starter</artifactId>
</dependency>
```

### Ollama（本地模型，免费）
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-ollama-spring-boot-starter</artifactId>
</dependency>
```
配合本地 `ollama run llama3.2` 就能用。

### 多模型路由（一个工程混用）
```java
// 可以同时注入多个 ChatModel，按场景选
@Autowired private OpenAiChatModel gptModel;
@Autowired private OllamaChatModel localModel;
```

---

## 六、和 LangChain4j 的对比

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| 出品方 | Spring 官方 | 社区（Java 版 LangChain） |
| Spring 整合 | 原生 ⭐⭐⭐⭐⭐ | 也支持 ⭐⭐⭐⭐ |
| 功能丰富度 | 中等 | 更多（Agent 更强） |
| 学习曲线 | 平缓 | 中等 |
| 中文资料 | 越来越多 | 少 |
| 适合场景 | **企业级、Spring 体系** | **复杂 Agent、多步推理** |

**实战建议**：**两个都学**，主用 Spring AI，复杂 Agent 用 LangChain4j。两者可在同一项目共存。

---

## 七、避坑指南

### ⚠️ 坑 1：JDK 版本
Spring AI 要求 **JDK 17+**，确认 `java -version`。

### ⚠️ 坑 2：API Key 泄漏
不要写在代码里，用环境变量：
```yaml
api-key: ${OPENAI_API_KEY}
```

### ⚠️ 坑 3：流式响应被 Spring MVC 阻塞
确保用 `produces = MediaType.TEXT_EVENT_STREAM_VALUE` 且返回 `Flux`。

### ⚠️ 坑 4：版本不匹配
Spring AI 1.0.x 和 0.8.x API 差异巨大，注意看版本号。

### ⚠️ 坑 5：Token 超限
长对话或大文档 RAG 时会超 context window，要做切分或摘要。

### ⚠️ 坑 6：成本失控
开发期一定限制 max-tokens，别让 LLM 输出 4000 token。

---

## 八、推荐学习路径

```
Day 1：跑通 Hello World（30 分钟）
   ↓
Day 2：流式 + Prompt 模板（2 小时）
   ↓
Day 3：Function Calling 实战（半天）
   ↓
Day 4-5：接入 Milvus 做 RAG（1-2 天）
   ↓
Day 6-7：写一个完整知识库 demo（周末）
   ↓
Week 2 起：进阶 LangChain4j + Agent
```

---

## 九、参考资料

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [Spring AI Examples GitHub](https://github.com/spring-projects/spring-ai-examples)
- [Spring AI Alibaba（国内 Fork，国产模型支持）](https://github.com/alibaba/spring-ai-alibaba)
- [LangChain4j 文档](https://docs.langchain4j.dev/)

---

## 十、面试常考点速记

1. ChatClient 和 ChatModel 区别？→ 一个是高层封装，一个是底层接口
2. 怎么实现流式响应？→ 返回 `Flux<String>` + SSE
3. Function Calling 怎么写？→ `@Tool` 注解 + `.tools()` 注册
4. Prompt 注入怎么防？→ 输入校验 + 系统提示约束 + 输出审核
5. 怎么做 RAG？→ DocumentReader → 切分 → Embedding → VectorStore → QuestionAnswerAdvisor
6. 上下文记忆怎么实现？→ `ChatMemory` + `MessageChatMemoryAdvisor`
7. 多轮对话怎么管理？→ 用 conversationId + ChatMemory

---

**记住一句话**：Spring AI 不是要你成为 AI 专家，是让你**用 Spring 工程师的姿势**接入 AI。
