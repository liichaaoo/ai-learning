# Day 3 · 三种 Memory 机制（按场景选）

> ⏱️ 时间：1.5 小时
> 🎯 目标：吃透 LangChain4j 三种 Memory 实现 + 自己写一个 Redis 持久化版

---

## 0. 心法（5 分钟）

> **Memory = 多轮对话历史的"压缩与裁剪"策略。**

为什么需要：LLM 每次调用是无状态的——你不传历史，它就忘了。但**全传又会超 Context、加钱、变慢**。

```
策略 = 在"记住多少"和"花多少 Token"之间找平衡。
```

---

## 1. 三种 Memory 对比 ⭐（10 分钟）

| Memory | 裁剪策略 | 何时用 |
|--------|---------|--------|
| **`MessageWindowChatMemory`** | 按**条数**截断（保留最近 N 条）| **大多数场景** ⭐ |
| **`TokenWindowChatMemory`** | 按 **token 数**截断（更精准）| Token 成本敏感 |
| **`SummarizingChatMemory`** | 老历史 **LLM 摘要**，新历史保留 | 超长对话（>50 轮）|

---

## 2. MessageWindowChatMemory（默认首选）

```java
ChatMemory memory = MessageWindowChatMemory.withMaxMessages(20);

// 第 21 条进来时，最早一条会被踢
// 内部用 LinkedList 实现，时间复杂度 O(1)
```

接到 AiService：

```java
@Bean
public Assistant assistant(ChatLanguageModel model) {
    return AiServices.builder(Assistant.class)
            .chatLanguageModel(model)
            .chatMemory(MessageWindowChatMemory.withMaxMessages(20))
            .build();
}
```

> 💡 **20 条是工程经验值**：能覆盖 90% 对话场景；超出可调到 50。

---

## 3. TokenWindowChatMemory（精准计费）

```java
import dev.langchain4j.model.Tokenizer;

Tokenizer tokenizer = new OpenAiTokenizer("gpt-4o");

ChatMemory memory = TokenWindowChatMemory.builder()
        .maxTokens(2000, tokenizer)
        .build();
```

> 💡 **比 MessageWindow 更精准**——一条 5000 字的消息 ≈ 几十条短消息的 token，按条数无法控制。

### 适合场景

- 上 Cost-sensitive 场景（按 token 计费的 SaaS）
- 用户能粘贴超长文本的对话
- 需要严格的 prompt 长度上限

---

## 4. SummarizingChatMemory（超长对话杀手锏）⭐

> 当对话超过 100 轮、加起来几万 token 时——**MessageWindow 会丢早期信息，TokenWindow 会让上下文不全**。

**思路**：老对话 LLM 自动总结，新对话保留原文。

```
原始历史：
  [user] 我叫小明
  [ai] 你好小明
  [user] 我家有 3 只猫
  [ai] 真好玩
  [user] 我最喜欢的是橘猫
  [ai] 嗯嗯
  ... 又过了 30 轮 ...

压缩后：
  [system] 【历史摘要】用户名叫小明，养 3 只猫，最爱橘猫。讨论过宠物食品、行为习惯...
  [user] 最近这一两轮的对话
  [ai] ...
```

代码：

```java
ChatMemory memory = SummarizingChatMemory.builder()
        .chatLanguageModel(model)              // 用来做摘要
        .maxMessages(20)                        // 超过 20 条就压缩
        .build();
```

> ⚠️ **代价**：每次压缩都要多调 1 次 LLM，**多花钱 + 多延迟**。
>
> 工程上：只在"长对话场景"开。

---

## 5. 自己写一个 RedisChatMemoryStore（必做）

> 内置三种 Memory 默认存在内存——**重启就丢**。生产必须持久化。

`ChatMemoryStore` 是 LangChain4j 的存储抽象：

```java
public interface ChatMemoryStore {
    List<ChatMessage> getMessages(Object memoryId);
    void updateMessages(Object memoryId, List<ChatMessage> messages);
    void deleteMessages(Object memoryId);
}
```

### 5.1 Redis 实现

```java
@Component
@RequiredArgsConstructor
public class RedisChatMemoryStore implements ChatMemoryStore {

    private final StringRedisTemplate redis;

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String json = redis.opsForValue().get(key(memoryId));
        if (json == null) return new ArrayList<>();
        return ChatMessageDeserializer.messagesFromJson(json);
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        String json = ChatMessageSerializer.messagesToJson(messages);
        redis.opsForValue().set(key(memoryId), json, Duration.ofDays(7));
    }

    @Override
    public void deleteMessages(Object memoryId) {
        redis.delete(key(memoryId));
    }

    private String key(Object memoryId) {
        return "lc4j:memory:" + memoryId;
    }
}
```

### 5.2 接到 AiService

```java
@Bean
public Assistant assistant(ChatLanguageModel model, RedisChatMemoryStore store) {
    return AiServices.builder(Assistant.class)
            .chatLanguageModel(model)
            .chatMemoryProvider(memoryId ->
                MessageWindowChatMemory.builder()
                    .id(memoryId)
                    .maxMessages(20)
                    .chatMemoryStore(store)        // ⭐ 注入持久化
                    .build())
            .build();
}
```

```java
interface Assistant {
    String chat(@MemoryId String userId, @UserMessage String message);
}
```

> 🎯 **这一段你将来 90% 概率会写**——任何"多用户多轮"的 AI 应用都需要。

---

## 6. Memory 的"窗口大小"经验值

| 场景 | maxMessages | 备注 |
|------|-------------|------|
| 工单分诊（单轮）| 0 (不开 memory) | 不需要历史 |
| 简单 FAQ | 6 ~ 10 | 节省 token |
| **通用客服** | **20** | **默认值** |
| 复杂咨询（如医生）| 40 | 多记一些 |
| 超长会话（小说续写）| Summarizing | 否则 token 爆炸 |

---

## 7. 高频面试题

**Q1：LLM 是无状态的，多轮对话是怎么实现的？**
A：每次调用都把历史消息一起传进 prompt。Memory 就是历史管理。

**Q2：用 Window 还是 Token？**
A：默认 Window（简单）；如果消息长度差异巨大（用户会粘贴文档）改 Token。

**Q3：Summarizing 适合什么？代价？**
A：超长对话（> 50 轮）。代价：每次压缩多调一次 LLM，慢且贵。

**Q4：多用户隔离怎么做？**
A：`chatMemoryProvider(memoryId -> ...)` + 接口加 `@MemoryId` 参数。

**Q5：怎么持久化？**
A：实现 `ChatMemoryStore` 接口，常用 Redis / MySQL / MongoDB。

---

## 8. 检查清单

- [ ] 三种 Memory 都跑过，看到"超过窗口最早条被丢"的行为
- [ ] 跑通 `@MemoryId` 多用户隔离
- [ ] 自己实现 `RedisChatMemoryStore`（必做，能讲给面试官听）
- [ ] 知道 Summarizing 的代价是什么
- [ ] 给三个不同场景报出 Window 大小

完成了 ➡️ [Day 4 · Tools 进阶](./Day4-Tools进阶.md)

---

## 🔗 相关链接

- ⬅️ [Day 2 · AiServices](./Day2-AiServices声明式.md)
- ➡️ [Day 4 · Tools 进阶](./Day4-Tools进阶.md)
- ⬆️ [Week 1 总览](./README.md)
- 📚 [LangChain4j Memory 文档](https://docs.langchain4j.dev/tutorials/chat-memory)
