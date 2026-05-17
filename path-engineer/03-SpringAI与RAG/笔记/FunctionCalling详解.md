# Function Calling 详解（速查手册）

> 服务于 Week 2 + 阶段 4 Agent。**3 个月后回来看，5 分钟想起来。**

---

## 1. 一句话本质

> **Function Calling = LLM 输出一段「我要调哪个函数 + 参数」的 JSON，由你的代码去执行，再把结果给回 LLM 续答。**

---

## 2. 工作流程（背下来）

```
用户问： "查一下订单 12345"
   │
   ▼
LLM 收到 prompt + 注册的工具列表
   │
   ▼
LLM 发现要调 getOrder(orderId)
   │
   ▼  返回 tool_call: {name: "getOrder", args: {"orderId": 12345}}
你的代码执行 OrderService.getOrder(12345)
   │
   ▼  返回 "已发货 / 物流单号 SF12345"
把结果作为 tool message 加回 messages
   │
   ▼
LLM 续答："你的订单 12345 已发货，物流单号 SF12345"
```

---

## 3. Spring AI 写法（最简）

### 3.1 用 `@Tool`（推荐）

```java
@Service
public class OrderTools {
    @Tool(description = "根据订单 ID 查询订单状态")
    public String getOrder(@ToolParam(description = "订单 ID") long orderId) {
        return orderService.getStatus(orderId);
    }
}
```

注入到 ChatClient：

```java
chatClient.prompt()
        .user("查一下订单 12345")
        .tools(orderTools)
        .call()
```

### 3.2 用 `FunctionCallback`（旧风格）

```java
.functions("getOrderStatus")    // 通过 name 引用 @Bean FunctionCallback
```

---

## 4. 必须知道的约束

| 项 | 约束 |
|----|------|
| **工具描述** | `description` 写得越清楚，模型选得越准 |
| **参数类型** | `int / long / String / 自定义 record` 都行 |
| **参数校验** | LLM 可能传错——**自己加 @Valid 或手动校验** |
| **执行时间** | LLM 没有超时概念——**自己加超时**（5s 内）|
| **副作用** | 危险操作（删除/支付）必须二次确认 |
| **并行调用** | GPT-4o / 通义都支持 parallel_tool_calls |

---

## 5. 设计原则（提炼版）

1. **小而专**：一个工具只干一件事，不要写"万能查询" Tool
2. **描述清晰**：description 一句话说清楚"什么场景调"
3. **错误友好**：参数错时返回 LLM 看得懂的错误（"订单不存在，请确认 ID"）
4. **幂等优先**：能幂等就幂等，重复调用不出事
5. **审计先行**：每次 tool 调用都记日志（哪个用户、什么参数、什么结果）

---

## 6. 三大主流 LLM 的兼容性

| 模型 | Function Calling | 备注 |
|------|------------------|------|
| GPT-4o / GPT-4 Turbo | ✅ 强 | 原生 + 支持并行 |
| Claude 3.5 | ✅ 强 | 原生 |
| 通义 qwen-max / qwen-plus | ✅ | 阿里官方支持 |
| Llama 3.1+ | ✅ | 需 prompt 模板支持 |
| 通义 qwen-turbo | ⚠️ | 简单场景 OK |

---

## 7. 高频面试题

**Q1：Function Calling 工作原理一句话？**
A：LLM 输出"我想调哪个函数+参数"的 JSON，由我们的代码执行再把结果给回去，让 LLM 续写。

**Q2：`@Tool` 内部怎么注册到 LLM？**
A：Spring AI 用反射读取注解 + 把方法签名转成 OpenAI tools schema，附加到每次 LLM 请求。

**Q3：LLM 选错了工具怎么办？**
A：① 描述写得更清楚 ② 减少同类工具冲突 ③ system prompt 里给规则约束 ④ 必要时加二次校验

**Q4：参数校验失败应该怎么处理？**
A：返回结构化错误信息（"参数 orderId 必须 > 0"）当作 tool message 给 LLM，让它道歉重试。

**Q5：和 Agent 的关系？**
A：Function Calling 是 Agent 的"手"——Agent = Function Calling + 多步规划 + 反思。阶段 4 会展开。

---

## 🔗 相关链接

- 📖 [Week 2 · Function Calling 教程](../Week2-FunctionCalling与多模型/README.md)
- 📚 [Spring AI Tools 官方](https://docs.spring.io/spring-ai/reference/api/tools.html)
- 📚 [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
