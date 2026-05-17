# Day 2 · AiServices 声明式 API（爽点最高）⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 AiServices 的全部"花活"过一遍，建立"用 interface 写 AI"的肌肉记忆

---

## 0. 心法（5 分钟）

> **AiServices 让 Java 程序员把 AI 当成一个 RPC：定义接口 → 自动实现 → 调用即用。**

3 个核心动作：

| 动作 | 用什么 |
|------|--------|
| 给 LLM 设定角色 | `@SystemMessage` |
| 把用户输入塞进 prompt | `@UserMessage` + `{{var}}` |
| 接收结构化结果 | 返回类型 = POJO / Record / List / 枚举 |

---

## 1. 8 种典型用法（30 分钟）

### 1.1 最简

```java
interface Assistant {
    String chat(String message);
}
```

### 1.2 加 System Prompt

```java
interface Assistant {
    @SystemMessage("你是公司知识库助手，简洁回答。")
    String chat(String message);
}
```

### 1.3 多参数 + 模板变量

```java
interface Translator {
    @SystemMessage("你是专业翻译。")
    @UserMessage("把以下内容从 {{from}} 翻译成 {{to}}：{{text}}")
    String translate(@V("from") String from,
                     @V("to") String to,
                     @V("text") String text);
}

// 调用
translator.translate("中文", "英文", "你好世界");
```

### 1.4 返回 POJO（自动 JSON 反序列化）⭐

```java
record SentimentResult(String label, double confidence, String reason) {}

interface SentimentAnalyzer {
    @SystemMessage("分析以下文本的情感倾向。")
    SentimentResult analyze(String text);
}

SentimentResult r = analyzer.analyze("这家餐厅服务太差了");
// SentimentResult[label=负面, confidence=0.95, reason=用户表达了对服务的不满]
```

### 1.5 返回 List

```java
interface ItemExtractor {
    @UserMessage("从下面这段话中提取出所有提到的商品名：{{text}}")
    List<String> extract(@V("text") String text);
}

List<String> items = extractor.extract("我买了 iPhone 和 AirPods 还有充电器");
// [iPhone, AirPods, 充电器]
```

### 1.6 返回枚举（分类任务）

```java
enum Priority { URGENT, NORMAL, LOW }

interface Classifier {
    @UserMessage("判断这条工单的优先级：{{ticket}}")
    Priority classify(@V("ticket") String ticket);
}
```

### 1.7 返回 Result&lt;T&gt;（带元信息）

```java
interface Assistant {
    Result<String> chatWithMetadata(String message);
}

Result<String> r = assistant.chatWithMetadata("你好");
r.content();         // 答案
r.tokenUsage();      // Token 计费
r.sources();         // RAG 时来源
r.finishReason();    // 结束原因
```

### 1.8 流式输出（返回 `TokenStream`）

```java
interface Assistant {
    TokenStream stream(String message);
}

assistant.stream("写一首关于春天的诗")
    .onNext(token -> System.out.print(token))
    .onComplete(resp -> System.out.println("\n完成"))
    .onError(Throwable::printStackTrace)
    .start();
```

> 💡 **8 种用法 = 80% 场景**——熟练这 8 个，AiServices 你就吃透了。

---

## 2. Prompt 模板里能塞什么（10 分钟）

```java
@SystemMessage(fromResource = "/prompts/system.txt")     // 从文件加载
@UserMessage("""
        当前时间：{{current_date}}
        用户提问：{{question}}
        请详细回答。
        """)
String ask(@V("question") String q);
```

### 几个常用占位符（LangChain4j 内置）

```
{{current_date}}        当前日期
{{current_time}}        当前时间
{{current_date_time}}   两个一起
```

---

## 3. AiServices 装配方式（10 分钟）

### 3.1 单一 ChatModel

```java
@Bean
public Assistant assistant(ChatLanguageModel model) {
    return AiServices.create(Assistant.class, model);
}
```

### 3.2 完整 builder（推荐）

```java
@Bean
public Assistant assistant(ChatLanguageModel model, ChatMemory memory) {
    return AiServices.builder(Assistant.class)
            .chatLanguageModel(model)
            .chatMemory(memory)                    // 多轮对话
            .tools(new WeatherTool(), new TimeTool())  // 工具
            .systemMessageProvider(memId -> "你是助手")  // 动态 system
            .build();
}
```

### 3.3 多用户隔离的 Memory

```java
interface Assistant {
    String chat(@MemoryId String userId, @UserMessage String message);
}

@Bean
public Assistant assistant(ChatLanguageModel model) {
    return AiServices.builder(Assistant.class)
            .chatLanguageModel(model)
            .chatMemoryProvider(userId ->                          // ⭐ 每个用户独立 memory
                MessageWindowChatMemory.withMaxMessages(20))
            .build();
}

// 调用：
assistant.chat("user-001", "我叫小明");
assistant.chat("user-001", "我叫什么？");    // → 记得：小明
assistant.chat("user-002", "我叫什么？");    // → 不知道（隔离）
```

> 🎯 **多用户场景必备**——这就是简历项目里"多租户对话"的实现底层。

---

## 4. 看一个真实场景：AI 工单分诊（15 分钟）

```java
// 1. 定义结构化输出
public record TicketTriage(
    Priority priority,
    String category,          // "billing" / "tech" / "account"
    String summary,           // 1 句话总结
    List<String> suggestedTags,
    boolean needsHumanFallback
) {}

public enum Priority { URGENT, HIGH, NORMAL, LOW }

// 2. AiService
interface TicketAgent {
    @SystemMessage("""
            你是工单分诊助手。请根据用户描述输出 JSON：
            - priority：紧急程度
            - category：billing/tech/account 三选一
            - summary：一句话总结
            - suggestedTags：3 个标签
            - needsHumanFallback：若涉及金钱/隐私则 true

            只输出 JSON，不要其他文字。
            """)
    TicketTriage triage(@UserMessage String ticket);
}

// 3. 业务里直接用
@RestController
class TicketController {
    @Autowired TicketAgent agent;

    @PostMapping("/triage")
    public TicketTriage triage(@RequestBody String content) {
        return agent.triage(content);
    }
}
```

测试：

```bash
curl -X POST -d "我的账单显示扣了 9999 元！" http://localhost:8080/triage
# {
#   "priority": "URGENT",
#   "category": "billing",
#   "summary": "用户反馈账单异常大额扣费",
#   "suggestedTags": ["billing", "complaint", "high_value"],
#   "needsHumanFallback": true
# }
```

> 🎯 **这就是声明式 AI 的魅力**：5 行接口 + 1 行 Bean = 一个生产可用的 AI 服务。

---

## 5. 检查清单

- [ ] 8 种用法每个跑过一次
- [ ] 知道 `@V` 注解什么时候必填、什么时候可省（参数只有 1 个时可省）
- [ ] 跑通 `@MemoryId` 多用户隔离
- [ ] 写一个返回 POJO 的 AiService 并跑通
- [ ] 解释 AiServices 内部原理（Day 1 的 §4 复习）

完成了 ➡️ [Day 3 · Memory 机制](./Day3-Memory机制.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · Hello World](./Day1-LangChain4j-HelloWorld.md)
- ➡️ [Day 3 · Memory 机制](./Day3-Memory机制.md)
- ⬆️ [Week 1 总览](./README.md)
- 📚 [AiServices 官方文档](https://docs.langchain4j.dev/tutorials/ai-services)
