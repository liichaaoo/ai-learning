# Day 4 · Prompt 工程（System Prompt + 模板）

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**用 System Prompt 把通用 LLM 变成"专业角色"，用模板动态注入变量**

---

## 🧭 今天的核心问题

**同样一个 LLM，怎么让它：**
- 回答医学问题时像医生
- 回答代码问题时像资深工程师
- 只答指定领域，别的问题拒绝

**答案**：**Prompt 工程**。

---

## 一、三种角色（Role）

LLM 对话里每条消息有一个 **role**，一共 3 种：

| Role | 作用 | 举例 |
|------|-----|------|
| **system** | 给 AI 设定人设/规则 | "你是资深 Java 架构师，回答要专业简洁" |
| **user** | 用户的提问 | "我该用 MySQL 还是 PostgreSQL？" |
| **assistant** | AI 的回答 | "这取决于你的场景..." |

### 完整对话长这样（底层 JSON 格式）

```json
{
  "messages": [
    {"role": "system",    "content": "你是资深 Java 架构师，回答要专业简洁"},
    {"role": "user",      "content": "我该用 MySQL 还是 PostgreSQL？"},
    {"role": "assistant", "content": "这取决于你的场景..."},
    {"role": "user",      "content": "我想做一个社交 App"}
  ]
}
```

**多轮对话**：把之前的所有消息拼一起发过去。**LLM 本身无记忆**，记忆是应用层拼上去的。

---

## 二、System Prompt：最便宜的"专业化"⭐

### 2.1 直接上代码

改你的 `ChatService.java`，加一个新方法：

```java
public String chatAsExpert(String question) {
    return chatClient
        .prompt()
        .system("你是一位资深 Java 架构师，有 15 年经验。" +
                "回答问题必须：1) 给出明确结论；2) 说清理由；3) 总字数不超过 200。")
        .user(question)
        .call()
        .content();
}
```

对应的 Controller：
```java
@GetMapping("/chat/expert")
public String expert(@RequestParam String q) {
    return chatService.chatAsExpert(q);
}
```

### 2.2 对比体验

问同一个问题 "我该用 MySQL 还是 PostgreSQL？"：

**`/chat?q=...`（无 system）**：
> "MySQL 和 PostgreSQL 都是关系型数据库... 巴拉巴拉写 500 字科普..."

**`/chat/expert?q=...`（有 system）**：
> "选 PostgreSQL。
> 理由：1) JSONB 类型对现代业务更友好；2) 并发控制 MVCC 更成熟；3) 扩展性更强..."

**同一个模型，通过一句 system 就"变了个人"**。这就是 Prompt 工程的魔力。

### 2.3 System Prompt 的常见套路

```
# 人设型
你是一位 [XX 领域] 的 [YY 角色]，有 [N] 年经验。

# 约束型
你只回答 [领域] 相关问题。其他问题一律回复："这不在我的专业范围内"。

# 格式型
请用 Markdown 回答。每段不超过 3 行。

# 风格型
用轻松的语气，适当加 emoji 🚀。

# 思维型
先分析问题、再列选项、最后给建议。
```

---

## 三、Prompt 模板（动态注入变量）⭐⭐

### 3.1 场景：商品客服

想让 LLM 对每个用户说：
> "你好 [用户名]，欢迎来到 [商品名] 的客服。"

问题是：用户名和商品名是**变量**，要每次注入。

### 3.2 Spring AI 的模板语法：`{变量名}`

```java
public String welcome(String userName, String product) {
    return chatClient
        .prompt()
        .user(spec -> spec
            .text("你好 {name}，欢迎来到 {product} 的客服，有什么可以帮你？")
            .param("name", userName)
            .param("product", product)
        )
        .call()
        .content();
}
```

Spring AI 会把 `{name}` 替换成 `userName` 的值，`{product}` 同理。

### 3.3 更常见用法：System Prompt 里用模板

**场景**：同一个服务支持不同行业的客服，`industry` 是变量：

```java
public Flux<String> industryCustomerService(String industry, String question) {
    return chatClient
        .prompt()
        .system(spec -> spec
            .text("""
                  你是 {industry} 行业的专业客服。
                  回答要简洁、专业，不要超过 3 句话。
                  如果问题不在 {industry} 领域，礼貌拒答。
                  """)
            .param("industry", industry)
        )
        .user(question)
        .stream()
        .content();
}
```

### 3.4 `Resource` 从文件读模板（生产级）

真实项目 prompt 通常很长，**不会硬编码在 Java 里**，而是放文件。

**Step 1**：`src/main/resources/prompts/customer-service.st` （`.st` = String Template）
```
你是 {industry} 行业的专业客服。
回答要简洁、专业，不超过 3 句话。
如果问题不在 {industry} 领域，礼貌拒答。
---
参考信息：
- 店铺名：{shopName}
- 营业时间：{businessHours}
```

**Step 2**：Java 里读
```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;

@Service
public class ChatService {
    // ...

    @Value("classpath:/prompts/customer-service.st")
    private Resource customerServiceTpl;

    public String customerServiceAnswer(
            String industry, String shopName, String businessHours, String question) {
        return chatClient
            .prompt()
            .system(spec -> spec
                .text(customerServiceTpl)
                .param("industry", industry)
                .param("shopName", shopName)
                .param("businessHours", businessHours)
            )
            .user(question)
            .call()
            .content();
    }
}
```

**好处**：
- ✅ 改 prompt 不用改 Java 代码
- ✅ 产品经理 / 运营可以自己改
- ✅ 支持多版本 A/B 测试

**这是生产环境的标准做法**，记下来。

---

## 四、多轮对话（记忆）

### 4.1 问题：LLM 无记忆

```
用户：我叫李华
AI：你好李华！
用户：我叫什么名字？
AI：抱歉，我不知道你的名字。   ← ❌ 忘了
```

因为每次调用都是**独立的 HTTP 请求**，LLM 服务端不存历史。

### 4.2 解法：应用层拼历史

**手动做**（原始版）：
```java
List<Message> history = new ArrayList<>();
history.add(new UserMessage("我叫李华"));
history.add(new AssistantMessage("你好李华！"));
history.add(new UserMessage("我叫什么名字？"));

// 把整个 history 传给 chatClient
```

**Spring AI 推荐**：用 `ChatMemory` 和 `MessageChatMemoryAdvisor`

> ⚠️ Spring AI 1.0.0 GA 起，旧的 `InMemoryChatMemory` 已被移除。
> 现在统一用 `ChatMemory` 接口，默认实现是 `MessageWindowChatMemory`（按消息条数滑窗）。

```java
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;

@Service
public class ChatService {

    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder) {
        // 滑窗默认保留最近 20 条消息
        ChatMemory memory = MessageWindowChatMemory.builder()
                .maxMessages(20)
                .build();

        this.chatClient = builder
                .defaultAdvisors(
                        MessageChatMemoryAdvisor.builder(memory).build()
                )
                .build();
    }

    public String chatWithMemory(String conversationId, String question) {
        return chatClient
            .prompt()
            .user(question)
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
            .call()
            .content();
    }
}
```

用法：
```java
// 用 conversationId 区分不同对话
chatWithMemory("user-123", "我叫李华");        // AI：你好李华！
chatWithMemory("user-123", "我叫什么？");       // AI：你叫李华  ✅ 记住了！
chatWithMemory("user-456", "我叫什么？");       // AI：我不知道   ← 另一个 conversation
```

### 4.3 注意

- `MessageWindowChatMemory` 进程重启就丢（数据存在 JVM 内存）
- 生产用 **Redis / JDBC 后端的 ChatMemoryRepository**（Week 5-6 会做）
- 历史很长时要做**滑窗**或**摘要**（上下文窗口有限）

---

## 五、Advisor 机制（简介，了解即可）

Spring AI 里 `Advisor` 是**拦截器**，可以包装在 prompt 调用前后。

- `MessageChatMemoryAdvisor` - 自动塞历史
- `QuestionAnswerAdvisor` - 自动做 RAG（Week 3 会详讲）
- 自定义 Advisor - 比如加日志、做限流

**本周你只要知道这个机制存在**，Week 3 RAG 会重点用。

---

## 六、Prompt 工程的几个实战原则

### 1. 越具体越好

❌ "写一封邮件"
✅ "写一封给技术面试官的感谢邮件，风格专业，不超过 100 字，感谢他抽出 60 分钟时间"

### 2. Few-shot Learning（给例子）

```
你是一个商品分类助手，任务是把商品名归类。

示例：
商品：iPhone 15 Pro     → 分类：手机
商品：MacBook Air M3    → 分类：笔记本
商品：AirPods Pro 2     → 分类：耳机

现在请分类：商品：{product}
```

模型看几个例子就能模仿，效果远好于纯描述。

### 3. 指定输出格式

```
请回答并严格遵循以下 JSON 格式：
{
  "answer": "你的答案",
  "confidence": 0-100 的数字
}
```

明天 Day 5 会学到 Spring AI 的 `.entity(Class)` 更优雅的做法。

### 4. 分步思考（Chain-of-Thought）

```
请按以下步骤回答：
1. 先分析问题的核心是什么
2. 列出 3 个可能的方案
3. 比较优劣
4. 给出最终建议
```

对复杂问题，这招效果显著。

---

## 七、本日应该改出来的 Controller

整合下你的 `ChatController`，现在应该有这些接口：

```java
@RestController
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    // Day 2 学的
    @GetMapping("/chat")
    public String chat(@RequestParam String q) {
        return chatService.chat(q);
    }

    // Day 3 学的
    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestParam String q) {
        return chatService.chatStream(q);
    }

    // 今天新增
    @GetMapping("/chat/expert")
    public String expert(@RequestParam String q) {
        return chatService.chatAsExpert(q);
    }

    // 今天新增
    @GetMapping("/chat/industry")
    public String industry(@RequestParam String industry, @RequestParam String q) {
        return chatService.industryCustomerService(industry, q);
    }

    // 今天新增（带记忆）
    @GetMapping("/chat/memory")
    public String memory(
            @RequestParam(defaultValue = "default") String convId,
            @RequestParam String q) {
        return chatService.chatWithMemory(convId, q);
    }
}
```

**跑起来一个一个测**，验证每个接口的表现。

---

## ✍️ 本日实战清单

```
[ ] /chat/expert 接口实现并测试（有 system prompt 的）
[ ] /chat/industry 实现（用 .param() 模板）
[ ] 新建 src/main/resources/prompts/customer-service.st
[ ] 从 .st 文件读模板并测试
[ ] 实现 /chat/memory（带 ChatMemory）
[ ] 测试同一个 convId 下能记住上下文，换 convId 不记
```

---

## 🎯 今日收官清单

- [ ] 我能说出 system / user / assistant 三种 role 的区别
- [ ] 我会写 System Prompt 给 LLM 设定角色
- [ ] 我会用 `{变量名}` 模板 + `.param()` 注入变量
- [ ] 我会把 prompt 放到 `.st` 文件里，Java 读取
- [ ] 我理解"LLM 无记忆"的本质，会用 ChatMemory 实现多轮
- [ ] 我能说出 Few-shot、Chain-of-Thought 是啥

---

## 💡 小思考

Prompt 工程的本质是：**通过输入控制输出**，**不改模型**就能改变行为。

这比调模型快 1000 倍、便宜 1000 倍、成功率 1000 倍。**这就是 RAG 能存在的基础**（Week 3 会学，RAG 本质就是"把检索到的文档塞进 Prompt 里"）。

---

## 🔖 下一步

明天 → [Day 5：结构化输出 + 整合 Demo](./Day5-结构化输出与整合.md)
