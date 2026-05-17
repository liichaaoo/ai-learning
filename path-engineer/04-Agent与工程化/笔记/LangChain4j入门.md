# LangChain4j 入门（速查手册）

> 服务于 Week 1-2。**3 个月后回看，5 分钟想起来。**

---

## 1. 核心四件套

| 概念 | 一句话 |
|------|--------|
| `ChatLanguageModel` | 底层模型客户端 |
| **`AiServices`** ⭐ | **声明式 API（用 interface 写 Agent）** |
| `ChatMemory` | 多轮对话历史管理 |
| `Tools`（@Tool） | Function Calling |

---

## 2. AiServices 8 种用法

```java
// ① 最简
interface A { String chat(String m); }

// ② 加 system
@SystemMessage("...")
String chat(String m);

// ③ 模板变量
@UserMessage("把 {{t}} 翻译成 {{lang}}")
String translate(@V("t") String t, @V("lang") String lang);

// ④ 返回 POJO
SentimentResult analyze(String text);

// ⑤ 返回 List/Map
List<String> extract(String text);

// ⑥ 返回枚举
Priority classify(String ticket);

// ⑦ Result<T> 带元信息
Result<String> chatWithMeta(String m);

// ⑧ 流式
TokenStream stream(String m);
```

---

## 3. Memory 三种

| 类型 | 用法 | 适合 |
|------|------|------|
| `MessageWindowChatMemory.withMaxMessages(20)` | 按条数 | **默认** |
| `TokenWindowChatMemory.builder().maxTokens(2000, tokenizer).build()` | 按 token | 成本敏感 |
| `SummarizingChatMemory.builder().chatLanguageModel(...).maxMessages(20).build()` | LLM 摘要 | 超长对话 |

**持久化**：实现 `ChatMemoryStore` 接口（Redis / MySQL 都行）。

**多用户隔离**：
```java
.chatMemoryProvider(userId -> MessageWindowChatMemory.builder()
    .id(userId).maxMessages(20).chatMemoryStore(store).build())
```

接口里加 `@MemoryId String userId`。

---

## 4. Tools 进阶心法

| 心法 | 说明 |
|------|------|
| 描述写"什么场景调" | LLM 选不选对工具，全看描述 |
| 参数校验失败 → **return** 友好提示，**不** throw | LLM 看得懂的话术 |
| 工具描述要相互区分 | "查单个" vs "批量" 写清楚 |
| `@P("参数说明，举例 12345")` | 给 LLM 看的描述 + 给开发者看的例子 |
| 加 `@SystemMessage` 约束工具使用 | "只在 X 场景调；其他不要调" |

---

## 5. 跟 Spring AI 的混用策略

| 场景 | 用哪个 |
|------|--------|
| RAG / 集成 Spring 生态 | **Spring AI**（Advisor 链强）|
| Agent / 复杂工作流 | **LangChain4j**（AiServices 优雅）|
| 简单 LLM 调用 | 都行 |
| 同一项目两套并存 | **常见** |

---

## 6. 配置速查

```yaml
langchain4j:
  community:
    dashscope:
      chat-model:
        api-key: ${DASHSCOPE_API_KEY}
        model-name: qwen-plus
        temperature: 0.7
        max-tokens: 2000
  ollama:
    chat-model:
      base-url: http://localhost:11434
      model-name: qwen2.5:0.5b
```

---

## 7. 高频面试题

**Q：AiServices 怎么实现的？**
A：JDK 动态代理 + 反射读注解 + 把方法签名翻成 messages。

**Q：怎么做多用户隔离？**
A：`chatMemoryProvider` + 接口加 `@MemoryId`。

**Q：跟 Spring AI 区别？**
A：哲学不同——SA 命令式 + Advisor 链；LC4j 声明式 + AiServices。**生产常混用**。

**Q：Tool 选错怎么办？**
A：① 描述写清 ② SystemPrompt 加约束 ③ 减少同类 Tool ④ 监控异常率。

---

## 🔗 相关链接

- 📖 [Week 1 · LangChain4j 基础](../Week1-LangChain4j基础/README.md)
- 📚 [LangChain4j 官方](https://docs.langchain4j.dev/)
