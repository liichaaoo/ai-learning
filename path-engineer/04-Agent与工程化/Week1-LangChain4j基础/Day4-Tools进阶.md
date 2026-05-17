# Day 4 · Tools 进阶（参数校验 + 异常 + 选错兜底）

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 Function Calling 从"能跑"做到"能上生产"

---

## 0. 心法（5 分钟）

> **Tool 不是写完就完事——LLM 会传错参数、会选错工具、会一直调同一个工具。**

阶段 3 Week 2 你做的 Tool 是"快乐路径"。今天补**异常路径**：

```
快乐路径 ：参数对 → 调用成功 → 返回结果
异常路径 ：
  ① 参数类型错（要 long 传了 String）
  ② 参数值非法（订单 ID = -1）
  ③ 业务异常（订单不存在）
  ④ LLM 选错工具（明明问天气却调了订单）
  ⑤ LLM 死循环（一直调同一个工具）
```

---

## 1. LangChain4j Tool 速记（5 分钟）

```java
@Component
public class WeatherTool {

    @Tool("根据城市查询当前天气")           // ← 描述
    public String getWeather(
        @P("城市名，如 '上海'") String city
    ) {
        return "晴，24°C";
    }
}
```

```java
// 注入到 AiService
AiServices.builder(Assistant.class)
        .chatLanguageModel(model)
        .tools(new WeatherTool(), new CalculatorTool())
        .build();
```

> 跟 Spring AI 的 `@Tool` 几乎一样，**注解多了 `@P` 用来描述参数**。

---

## 2. 参数校验：第一道防线（15 分钟）

### 2.1 类型校验：交给框架

LangChain4j 已自动把 LLM 输出 JSON 反序列化成 Java 类型——传错类型直接 LLM 重试。

### 2.2 业务校验：必须自己加

```java
@Tool("根据订单 ID 查询订单状态")
public String getOrderStatus(@P("订单 ID，正整数") long orderId) {
    if (orderId <= 0) {
        return "参数错误：订单 ID 必须为正整数，您给的是 " + orderId;
    }
    Order order = orderRepo.findById(orderId).orElse(null);
    if (order == null) {
        return "订单 " + orderId + " 不存在，请核实后重试";
    }
    return order.getStatus();
}
```

> 💡 **关键认知**：**校验失败要 return 一个 LLM 看得懂的错误字符串**，不要 throw 异常。
>
> LLM 会读你的错误信息，向用户道歉并重试。

### 2.3 用 Bean Validation（推荐）

```java
@Tool("查询订单")
public String getOrder(
    @P("订单 ID") @Min(1) long orderId,
    @P("用户邮箱") @Email String email
) {
    // ...
}
```

需要在 AiService builder 启用：

```java
.toolProvider(toolProvider)
```

或者最直接的：**自己在方法体里手动校验**——也行。

---

## 3. 异常处理：让 LLM 知道"出错了"（10 分钟）

```java
@Tool("查询订单状态")
public String getOrderStatus(@P("订单 ID") long orderId) {
    try {
        return orderService.getStatus(orderId);
    } catch (OrderNotFoundException e) {
        // ✅ 业务异常：返回友好提示，LLM 会处理
        return "订单不存在，可能是 ID 错误";
    } catch (Exception e) {
        log.error("getOrderStatus failed", e);
        // ✅ 系统异常：告诉 LLM 这是临时问题
        return "查询服务暂时异常，请稍后再试";
    }
}
```

### 三种异常的"返回话术"

| 异常类型 | 返回什么 |
|---------|---------|
| 参数错 | "参数 X 必须 Y，您传的是 Z" |
| 业务异常 | "订单不存在 / 用户没权限 / 库存为 0" |
| 系统异常 | "暂时不可用，稍后再试" |
| 超时 | "查询超时，请简化问题" |

> 🎯 **原则**：**对 LLM 永远讲人话**——它会基于你的话给用户讲人话。

---

## 4. 工具描述：决定 LLM 选不选对（15 分钟）⭐

> **Tool 描述是 LLM "选哪个工具"的唯一依据**——写不好，再多工具也选错。

### 4.1 好描述 vs 烂描述

```java
// ❌ 烂描述
@Tool("查询")
public String query(@P("ID") long id) { ... }
// LLM 会"看心情"选——容易选错

// ✅ 好描述
@Tool("根据订单 ID 查询订单的当前状态（已发货/待发货/已完成等）。" +
      "仅用于查询单个订单。批量查询请用 batchGetOrders。")
public String getOrderStatus(
    @P("订单的数字 ID，例如 12345") long orderId
) { ... }
```

### 4.2 描述写作清单

```
✅ 一句话说清楚"什么场景调"
✅ 明确"用户问 X 时调我"
✅ 避免"不能"——用"建议替换"代替（"批量请用 xxx"）
✅ 参数描述给例子（"例如 12345"）
✅ 跟其他相似 Tool 区分（"查单个" vs "批量"）

❌ 太通用（"工具"、"查询"、"接口"）
❌ 含技术术语（"调用 ORM 查 DB"）
❌ 描述 < 10 字
```

### 4.3 实战例子

```java
@Tool("""
    根据中国城市名查询实时天气（温度、湿度、空气质量）。
    用户问"今天天气""明天会下雨吗""空气好不好"时调用我。
    支持城市格式：上海、北京、广州等中文名。
    """)
public WeatherInfo getWeather(@P("城市中文名，例如 '上海'") String city) { ... }
```

---

## 5. 工具选错的兜底（10 分钟）

### 5.1 用 SystemPrompt 加约束

```java
@SystemMessage("""
    你有以下工具可用：weather / order / calculator
    使用规则：
    1. 问天气一定用 weather
    2. 问订单一定用 order
    3. 问算术一定用 calculator
    4. 这三类之外的问题，不要调任何工具，直接回答

    不要为了用工具而用工具。
    """)
String chat(@UserMessage String message);
```

### 5.2 限制最大调用次数

LangChain4j 不直接限制，可以用 `Result<T>` 自己看：

```java
Result<String> r = assistant.chatWithMetadata(...);
List<ToolExecution> calls = r.toolExecutions();
if (calls.size() > 5) {
    // 触发兜底：可能是死循环
    log.warn("Too many tool calls: {}", calls.size());
}
```

### 5.3 监控异常率

```java
@Tool("...")
public String getOrder(long orderId) {
    Counter.builder("tool.call")
           .tag("tool", "getOrder")
           .register(meterRegistry)
           .increment();
    // ...
}
```

---

## 6. 测试 Tool 的方法（5 分钟）

```java
@Test
void testToolCalledAutomatically() {
    String reply = assistant.chat("帮我查订单 12345");
    assertThat(reply).contains("已发货");        // 模型应该自动调了 getOrder
}

@Test
void testInvalidParam() {
    String reply = assistant.chat("帮我查订单 -1");
    assertThat(reply).containsAnyOf("不存在", "错误");  // LLM 应该礼貌告知
}
```

---

## 7. 检查清单

- [ ] 写一个 `@Tool`，加 @P 参数描述
- [ ] 故意传非法参数，验证 LLM 能看到错误并道歉
- [ ] 写两个相似 Tool（如查单个/批量），通过描述让 LLM 区分
- [ ] 加 SystemPrompt 约束工具使用范围
- [ ] 测试一次"工具被自动调用"
- [ ] 写一句话总结你的 Tool 描述心法

完成了 ➡️ [Day 5 · 你的第一个 Agent](./Day5-第一个Agent.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · Memory 机制](./Day3-Memory机制.md)
- ➡️ [Day 5 · 第一个 Agent](./Day5-第一个Agent.md)
- ⬆️ [Week 1 总览](./README.md)
- 📚 [LangChain4j Tools 文档](https://docs.langchain4j.dev/tutorials/tools)
- 📝 [笔记/FunctionCalling详解.md（阶段 3）](../../03-SpringAI与RAG/笔记/FunctionCalling详解.md)
