# Day 1 · LangChain4j Hello World

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 LangChain4j 跑起来，理解它和 Spring AI 的差异

---

## 0. 心法（5 分钟）

> **LangChain4j 是"用 Java 写 AI 程序"最舒服的库——尤其是写 Agent。**

跟 Spring AI 的本质差异：

```
Spring AI 风格（命令式）：
  你写：调用 chatClient.prompt().user("...").call().content()

LangChain4j 风格（声明式）：
  你写一个 interface，告诉它"我想问什么"，它自己实现
```

LangChain4j 把"Java 的 Feign 体验"带到了 AI 调用。

---

## 1. 依赖与配置（10 分钟）

### 1.1 Maven 依赖

```xml
<properties>
    <langchain4j.version>0.36.2</langchain4j.version>
</properties>

<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-spring-boot-starter</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>

    <!-- 通义千问 -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-dashscope-spring-boot-starter</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>
</dependencies>
```

### 1.2 application.yml

```yaml
langchain4j:
  community:
    dashscope:
      chat-model:
        api-key: ${DASHSCOPE_API_KEY}
        model-name: qwen-plus
        temperature: 0.7
```

---

## 2. 第一段代码（15 分钟）

### 2.1 最朴素的写法（命令式）

```java
@SpringBootApplication
public class Lc4jApplication implements CommandLineRunner {

    @Autowired
    ChatLanguageModel chatModel;          // 自动注入（来自 starter）

    public static void main(String[] args) {
        SpringApplication.run(Lc4jApplication.class, args);
    }

    @Override
    public void run(String... args) {
        String reply = chatModel.chat("用一句话解释什么是 Agent");
        System.out.println("AI: " + reply);
    }
}
```

跑起来：

```bash
DASHSCOPE_API_KEY=sk-xxx ./mvnw spring-boot:run
# AI: Agent 是能自主感知、决策并执行任务的智能体...
```

> 💡 **跟 Spring AI 几乎一样**——这就是入门门槛低的原因。

### 2.2 用 `Result` 拿元信息

```java
Response<AiMessage> resp = chatModel.generate(UserMessage.from("你好"));
System.out.println(resp.content().text());
System.out.println("tokens used: " + resp.tokenUsage());
// tokens used: TokenUsage { inputTokenCount = 9, outputTokenCount = 25, totalTokenCount = 34 }
```

> 💡 **以后做 Token 计费需要这个对象**。

---

## 3. AiServices：第一次见识"声明式 AI"（25 分钟）

> 这是 LangChain4j 的灵魂——**Java 老兵会真心觉得"这才对啊"**。

### 3.1 朴素的 AiService

```java
public interface Assistant {
    String chat(String userMessage);
}
```

```java
@Configuration
public class AssistantConfig {
    @Bean
    public Assistant assistant(ChatLanguageModel model) {
        return AiServices.create(Assistant.class, model);
    }
}
```

```java
@RestController
public class TestController {
    @Autowired Assistant assistant;

    @GetMapping("/chat")
    public String chat(@RequestParam String q) {
        return assistant.chat(q);
    }
}
```

```bash
curl "http://localhost:8080/chat?q=你好"
# 你好！有什么可以帮你的吗？
```

> 🎯 **看到没有**：你**没写任何调用 LLM 的代码**——`AiServices` 自动给你的接口生成了实现类。

### 3.2 加 System Prompt（注解风格）

```java
public interface Assistant {

    @SystemMessage("你是一个简洁的助手，回答不超过 30 字。")
    String chat(@UserMessage String userMessage);
}
```

```bash
curl "http://localhost:8080/chat?q=介绍 Java"
# Java 是一种跨平台、面向对象的高级编程语言。
```

### 3.3 结构化输出（自动转 Java 对象）⭐

```java
public record Recipe(String name, List<String> ingredients, List<String> steps) {}

public interface ChefAssistant {

    @UserMessage("给我一道 {{dish}} 的食谱")
    Recipe getRecipe(String dish);     // ⭐ 直接返回 Java 对象！
}
```

LangChain4j 自动：
1. 把 `Recipe` 类的 schema 转成 JSON Schema
2. 写进 prompt 让模型按 JSON 输出
3. 反序列化成 `Recipe` 对象

```java
Recipe r = chef.getRecipe("番茄炒蛋");
System.out.println(r.name());           // "番茄炒蛋"
System.out.println(r.ingredients());    // ["番茄", "鸡蛋", "盐", ...]
```

> 💡 **比 Spring AI 的 `.entity(Recipe.class)` 更"自然"**——一个普通方法签名就够了。

---

## 4. AiServices 内部到底做了什么（15 分钟）

> 面试可能问。一句话：**JDK 动态代理 + 反射**。

```
你调用 assistant.chat("你好")
   │
   ▼
AiServices 的代理类拦截
   │
   ▼ 用反射读 @SystemMessage / @UserMessage / 参数注解
拼出 messages = [
    SystemMessage("你是..."),
    UserMessage("你好")
]
   │
   ▼
调用底层 ChatLanguageModel.generate(messages)
   │
   ▼ 拿到 AiMessage
按方法返回类型转换：
  - String   → 直接 text
  - Recipe   → JSON 解析为对象
  - Result<X> → 带元信息（Token 数等）
   │
   ▼
返回给你
```

> 🎯 **Java 老兵的熟悉感**：就像 MyBatis 的 Mapper、Spring Data 的 Repository、Feign 的 Client——**接口即实现**。

---

## 5. 高频面试题预习

**Q1：LangChain4j 跟 Spring AI 选哪个？**
A：写 Agent / 多步骤推理 用 LangChain4j（AiServices 优雅）；
   做集成在 Spring 生态里的 LLM 应用用 Spring AI（Advisor 链强）。
   **常常一个项目混用**。

**Q2：AiServices 怎么实现的？**
A：JDK 动态代理 + 反射读注解 + 把 Java 方法签名翻成 messages 数组。

**Q3：能不能用 Spring AI 的 ChatModel 给 LangChain4j 用？**
A：不能直接用（API 不一样），但可以包一层 adapter。一般同一项目两套并存。

---

## 6. 检查清单

- [ ] 跑通 `chatModel.chat("...")`
- [ ] 跑通最简 `AiServices.create(Assistant.class, model)`
- [ ] 加 `@SystemMessage` 注解能生效
- [ ] 跑通结构化输出（`Recipe` record）
- [ ] 能讲出 AiServices 内部原理（代理 + 反射）

完成了 ➡️ [Day 2 · AiServices 声明式](./Day2-AiServices声明式.md)

---

## 🔗 相关链接

- ⬆️ [Week 1 总览](./README.md)
- ➡️ [Day 2 · AiServices 声明式](./Day2-AiServices声明式.md)
- 📚 [LangChain4j AiServices 文档](https://docs.langchain4j.dev/tutorials/ai-services)
