# Day 5 · 整合 Demo · 你的第一个 Agent ⭐

> ⏱️ 时间：2 小时
> 🎯 目标：把 Day 1-4 串起来，做一个"能自己规划 + 调工具 + 多轮记忆"的 Agent
> 📂 项目：[`项目/06-langchain4j-hello/`](../项目/06-langchain4j-hello/)

---

## 0. 心法（5 分钟）

> **本周通关 = 一个能自主调多个工具、有记忆、支持多用户的 Java Agent。**

```
传统程序：     用户 → 调 A → 调 B → 拼结果 → 返回
RAG 程序：     用户 → 检索 → LLM → 返回
Agent 程序：   用户 → LLM 思考 → 自主调 A/B/C → 再思考 → 返回   ← 我们今天做这个
```

---

## 1. 项目目标规格

```
项目名：langchain4j-hello
位置：项目/06-langchain4j-hello/

技术栈：
  Spring Boot 3 + LangChain4j 0.36+
  通义 + Ollama 双模型
  Redis（Memory 持久化）

核心能力：
  ① AiService 声明式接口
  ② 多用户隔离的 ChatMemory（Redis 持久化）
  ③ 至少 3 个 Tool（时间、天气、计算器）
  ④ 多模型路由（通义 / Ollama 切换）
  ⑤ 流式对话（TokenStream）

接口：
  POST /api/chat                 同步对话
  POST /api/chat/stream          流式对话（SSE）
  POST /api/admin/clear/{userId} 清空某用户记忆
```

---

## 2. 核心代码（30 分钟）

### 2.1 AssistantService

```java
public interface AssistantService {

    @SystemMessage("""
            你是一个友好的 AI 助手。
            如果用户的问题需要查询天气、时间、做计算，请主动调用对应工具。
            其它问题直接回答即可，不要为了用工具而用工具。
            """)
    String chat(@MemoryId String userId, @UserMessage String message);

    TokenStream chatStream(@MemoryId String userId, @UserMessage String message);
}
```

### 2.2 三个工具

```java
@Component
public class TimeTool {
    @Tool("获取当前北京时间")
    public String now() {
        return LocalDateTime.now(ZoneId.of("Asia/Shanghai")).toString();
    }
}

@Component
public class WeatherTool {
    @Tool("查询某个城市的天气（温度、空气质量）")
    public String getWeather(@P("城市中文名，例如 '上海'") String city) {
        // 实际可以调高德/和风天气 API
        return "%s 当前 24°C 晴，空气质量良".formatted(city);
    }
}

@Component
public class CalculatorTool {
    @Tool("执行数学表达式计算，支持 + - * / 及括号")
    public double calc(@P("数学表达式，例如 '(1+2)*3'") String expr) {
        // 实际用 exp4j / mvel
        return new ScriptEngineManager().getEngineByName("graal.js")
                .eval(expr) instanceof Number n ? n.doubleValue() : 0.0;
    }
}
```

### 2.3 配置：路由 + Memory + 装配

```java
@Configuration
@RequiredArgsConstructor
public class Lc4jConfig {

    private final RedisChatMemoryStore memoryStore;
    private final TimeTool timeTool;
    private final WeatherTool weatherTool;
    private final CalculatorTool calculatorTool;

    @Bean
    @ConfigurationProperties("langchain4j.community.dashscope.chat-model")
    public ChatLanguageModel qwen() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-plus")
                .build();
    }

    @Bean
    public ChatLanguageModel ollama() {
        return OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("qwen2.5:0.5b")
                .build();
    }

    @Bean
    public StreamingChatLanguageModel qwenStream() {
        return QwenStreamingChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-plus")
                .build();
    }

    @Bean
    public AssistantService assistant(@Qualifier("qwen") ChatLanguageModel chat,
                                       @Qualifier("qwenStream") StreamingChatLanguageModel stream) {
        return AiServices.builder(AssistantService.class)
                .chatLanguageModel(chat)
                .streamingChatLanguageModel(stream)
                .chatMemoryProvider(userId -> MessageWindowChatMemory.builder()
                        .id(userId)
                        .maxMessages(20)
                        .chatMemoryStore(memoryStore)
                        .build())
                .tools(timeTool, weatherTool, calculatorTool)
                .build();
    }
}
```

### 2.4 Controller

```java
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class ChatController {

    private final AssistantService assistant;
    private final RedisChatMemoryStore memoryStore;

    @PostMapping("/chat")
    public Map<String, String> chat(@RequestHeader("X-User-Id") String userId,
                                     @RequestBody Map<String, String> body) {
        String reply = assistant.chat(userId, body.get("q"));
        return Map.of("answer", reply);
    }

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@RequestHeader("X-User-Id") String userId,
                                  @RequestBody Map<String, String> body) {
        SseEmitter emitter = new SseEmitter(60_000L);
        assistant.chatStream(userId, body.get("q"))
                .onNext(token -> {
                    try { emitter.send(SseEmitter.event().data(token)); }
                    catch (IOException e) { emitter.completeWithError(e); }
                })
                .onComplete(resp -> emitter.complete())
                .onError(emitter::completeWithError)
                .start();
        return emitter;
    }

    @PostMapping("/admin/clear/{userId}")
    public String clear(@PathVariable String userId) {
        memoryStore.deleteMessages(userId);
        return "cleared";
    }
}
```

---

## 3. 演示脚本（15 分钟）

```bash
# 起 Redis + Ollama（可选）
docker run -d -p 6379:6379 redis:7
ollama serve & ollama pull qwen2.5:0.5b      # 可选

# 起服务
DASHSCOPE_API_KEY=sk-xxx ./mvnw spring-boot:run

# ─── 演示 1：Tool 自动调用 ───
curl -X POST http://localhost:8080/api/chat \
  -H "X-User-Id: alice" -H "Content-Type: application/json" \
  -d '{"q":"现在几点？"}'
# {"answer":"现在是 2026-05-17 20:30:15"}

curl -X POST http://localhost:8080/api/chat \
  -H "X-User-Id: alice" -H "Content-Type: application/json" \
  -d '{"q":"上海天气怎么样？合不合适散步？"}'
# {"answer":"上海当前 24°C 晴...非常适合散步"}
#  ↑ Agent 自己调了 weatherTool 并基于结果推理

curl -X POST http://localhost:8080/api/chat \
  -H "X-User-Id: alice" -H "Content-Type: application/json" \
  -d '{"q":"帮我算 (12 + 8) * 3 等于多少"}'
# {"answer":"等于 60"}

# ─── 演示 2：多轮记忆 ───
curl -X POST .../chat -d '{"q":"我叫小明"}'
curl -X POST .../chat -d '{"q":"我叫什么名字？"}'    # → "小明"

# ─── 演示 3：多用户隔离 ───
curl -X POST .../chat -H "X-User-Id: bob" -d '{"q":"我叫什么名字？"}'
# → "不知道"（Bob 的 memory 跟 alice 隔离）

# ─── 演示 4：流式 ───
curl -N -X POST http://localhost:8080/api/chat/stream \
  -H "X-User-Id: alice" -H "Content-Type: application/json" \
  -d '{"q":"写一段 5 句话的散文"}'

# ─── 演示 5：清空记忆 ───
curl -X POST http://localhost:8080/api/admin/clear/alice
```

---

## 4. 看一眼"思考过程"日志（10 分钟）

打开 DEBUG 日志：

```yaml
logging:
  level:
    dev.langchain4j: DEBUG
```

你会看到：

```
[ChatRequest] messages: [system, user="上海天气合不合适散步"]
[LLM Output ] toolCalls: [getWeather(city="上海")]
[Tool Exec  ] WeatherTool.getWeather("上海") → "上海 24°C 晴..."
[ChatRequest] messages: [system, user, assistant(toolCall), tool="上海 24°C 晴..."]
[LLM Output ] "上海 24°C 晴，空气良好，非常适合散步！"
```

> 🎯 **看完这段日志 = 真正理解 Agent**。整个"思考→调用→再思考"循环在你眼前发生。

---

## 5. 出关验收

跑通这 6 个动作 = Week 1 通过：

- [ ] AiService 接口正常工作（不写一行实现）
- [ ] 至少 3 个 Tool 能被 LLM 自动调用
- [ ] 多用户 memory 隔离（Alice 知道小明，Bob 不知道）
- [ ] Redis 中能看到 `lc4j:memory:alice` 这种 key
- [ ] 流式接口能 SSE 返回
- [ ] DEBUG 日志能看到"工具调用"行
- [ ] 录了 5 分钟演示视频

---

## 6. 思考与延伸

| 问题 | 提示 |
|------|------|
| Agent 死循环（一直调同一个工具）怎么办？| Day 4 §5；可用最大调用次数限制 |
| 多个 Tool 描述太相似怎么办？| 改描述 + 加 system prompt 约束 |
| Memory 越积越大怎么办？| TokenWindow 或 Summarizing |
| 不同任务用不同模型？| 多 ChatModel Bean + 路由（Week 2 会专门讲）|
| 怎么做 Tool 的权限控制？| 自己写一层 `ToolGuard`，检查当前用户能不能用 |

---

## ✅ Week 1 通关

恭喜！你现在有了一个**会自己想事情、调工具、记得用户**的 Agent。

下周（Week 2）我们把这个 Agent **升级为"会规划复杂多步任务"** 的——
ReAct、Plan-and-Execute、Multi-Agent、MCP 协议全套。

---

## 🔗 相关链接

- ⬅️ [Day 4 · Tools 进阶](./Day4-Tools进阶.md)
- ⬆️ [Week 1 总览](./README.md)
- ➡️ [Week 2 · Agent 设计模式](../Week2-Agent设计模式/README.md)
- 📂 [项目骨架 06-langchain4j-hello](../项目/06-langchain4j-hello/)
