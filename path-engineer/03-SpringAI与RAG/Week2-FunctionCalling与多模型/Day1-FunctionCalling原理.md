# Day 1 · Function Calling 原理 + Hello Tool

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**让 AI 能调用你写的一个 Java 方法**（比如问"现在几点？"它自己去调）

---

## 🧭 今天你要搞懂

1. **什么叫 Function Calling**？
2. **AI 是怎么"知道"要调哪个方法的**？（底层原理必须懂）
3. **Spring AI 里怎么用 `@Tool` 暴露一个方法**？
4. **调用的时候发生了什么**（看日志）？

---

## 一、LLM 的天然"短板"

你 Week 1 已经会做 AI 聊天了。但 LLM 有几个天生的毛病：

### 毛病 1：**不知道当前时间**

```
用户：现在几点？
LLM: 我是语言模型，无法获取实时时间。抱歉。
```

因为 LLM 训练时的数据有截止日期，它不知道你现在几月几号。

### 毛病 2：**不能算数**（准确地）

```
用户：1234 * 5678 等于多少？
LLM: 大概是 7006252（其实是 7006652，算错了）
```

### 毛病 3：**不能查真实数据**

```
用户：我的订单 12345 发货了吗？
LLM: 抱歉，我不能访问你们的系统。
```

### 毛病 4：**不能"干事"**

```
用户：帮我重启 prod-service-01
LLM: 我不能执行命令，请找运维同学。
```

### 解法：**Function Calling**（工具调用）⭐

让 LLM **在需要的时候"召唤"外部工具**来弥补这些能力。
你把工具写成 Java 方法，注册给 Spring AI，LLM 就能自主决定**何时调、传什么参数**。

---

## 二、Function Calling 的工作原理（必懂）⭐⭐⭐

面试高频考点。我用一个简单的例子把全流程过一遍。

### 场景

- 你有一个 Java 方法 `getCurrentTime()` 返回"2026-05-12 22:30"
- 你把它注册成 Tool
- 用户问："现在几点？"

### 底层 5 步流程

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 你调 chatClient.prompt().tools(timeTool).user("现在几点？") │
│                                                              │
│   Spring AI 把 "现在几点？" + 工具描述 拼成一个请求:            │
│   {                                                          │
│     "messages": [{"role":"user", "content":"现在几点？"}],     │
│     "tools": [                                               │
│       {                                                      │
│         "type": "function",                                  │
│         "function": {                                        │
│           "name": "getCurrentTime",                          │
│           "description": "获取当前日期和时间",                 │
│           "parameters": { ... schema ... }                   │
│         }                                                    │
│       }                                                      │
│     ]                                                        │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: LLM 分析后返回"我要调 getCurrentTime"（不返回文字）      │
│                                                              │
│   {                                                          │
│     "choices": [{                                            │
│       "message": {                                           │
│         "role": "assistant",                                 │
│         "tool_calls": [{                                     │
│           "id": "call_abc",                                  │
│           "function": {                                      │
│             "name": "getCurrentTime",                        │
│             "arguments": "{}"                                │
│           }                                                  │
│         }]                                                   │
│       }                                                      │
│     }]                                                       │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Spring AI 拦截这个响应，发现是 tool_calls            │
│   → 反射调用你的 Java 方法 getCurrentTime()                   │
│   → 拿到返回值 "2026-05-12 22:30"                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Spring AI 把工具返回值再发给 LLM                      │
│                                                              │
│   {                                                          │
│     "messages": [                                            │
│       {"role":"user", "content":"现在几点？"},                 │
│       {"role":"assistant", "tool_calls":[...]},              │
│       {"role":"tool", "tool_call_id":"call_abc",             │
│        "content":"2026-05-12 22:30"}   ← 工具返回注入         │
│     ]                                                        │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: LLM 基于工具返回值，给出最终回答                      │
│                                                              │
│   "现在是 2026 年 5 月 12 日晚上 10:30。"                     │
└─────────────────────────────────────────────────────────────┘
```

### 核心认知（必须记住）

1. **LLM 不会"直接"调用你的方法**，它只会**返回"我要调什么、传什么参数"**
2. **真正调用方法的是 Spring AI**（拿到 LLM 的 tool_calls 后反射执行）
3. **一次用户请求，可能发 2 次 LLM 请求**（第 1 次决定调啥、第 2 次用返回值生成回答）
4. **多工具并行或链式调用**，LLM 会多次返回 tool_calls，Spring AI 循环处理

> 💡 **类比**：LLM 像个项目经理，它不亲自写代码，只**告诉秘书（Spring AI）去调哪个部门、交代什么事**。Spring AI 执行完，再把结果汇报给 LLM，LLM 把事情回复给用户。

---

## 三、Spring AI 里怎么声明一个 Tool（Hello Tool）

> ⚠️ Spring AI 1.x 声明 Tool 有**两种写法**（本教程两个都给，你熟哪个用哪个）：
> 1. **`@Tool` 注解方式**（推荐，最简洁）
> 2. **`FunctionCallback` 方式**（老方式，更灵活）

### 方式 1：@Tool 注解 ⭐ 推荐

新建 `src/main/java/com/fletcher/multitools/tools/TimeTool.java`：

```java
package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
public class TimeTool {

    /**
     * description 极其关键！LLM 就是靠这段话判断什么时候调用这个方法。
     * 写好它 = Function Calling 成功率提高 80%
     */
    @Tool(description = "获取服务器当前的日期和时间。当用户询问'现在几点'、'今天几号'、'当前时间'时调用此工具。")
    public String getCurrentTime() {
        return LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        );
    }

    /**
     * 带参数的例子（以城市为单位查询时间）
     */
    @Tool(description = "获取指定时区的当前时间")
    public String getTimeByZone(
            @ToolParam(description = "时区 ID，例如 Asia/Shanghai、America/New_York", required = true)
            String zoneId
    ) {
        return LocalDateTime.now(java.time.ZoneId.of(zoneId))
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
}
```

### 注册到 ChatClient

修改 `ChatService.java`，把 `TimeTool` 注入进去：

```java
@Service
public class ChatService {

    private final ChatClient chatClient;
    private final TimeTool timeTool;

    public ChatService(ChatClient.Builder builder, TimeTool timeTool) {
        this.chatClient = builder.build();
        this.timeTool = timeTool;
    }

    public String chatWithTools(String question) {
        return chatClient
                .prompt()
                .user(question)
                .tools(timeTool)          // ⭐ 关键：把 Tool 对象传进去
                .call()
                .content();
    }
}
```

### Controller 加个接口

```java
@GetMapping("/chat/agent")
public String agent(@RequestParam String q) {
    return chatService.chatWithTools(q);
}
```

---

## 四、启动测试 🎉

### 4.1 提问："现在几点？"

```bash
curl "http://localhost:8080/chat/agent?q=现在几点"
```

**期望返回**：
> 现在是 2026 年 5 月 12 日晚上 22:30:15。

### 4.2 提问："纽约现在几点？"

```bash
curl "http://localhost:8080/chat/agent?q=纽约现在几点"
```

**期望返回**：
> 纽约现在是 2026 年 5 月 12 日上午 10:30（美东时间）。

**看到这个，你已经完成 Function Calling 的第一步！** 🎉

LLM 正确识别：
- "现在几点" → 调 `getCurrentTime()`（无参）
- "纽约现在几点" → 调 `getTimeByZone("America/New_York")`（传参）

---

## 五、开日志看个仔细（强烈建议）

把 `application.yml` 里的日志级别调到 DEBUG：

```yaml
logging:
  level:
    org.springframework.ai: DEBUG
```

再跑一次 `/chat/agent?q=现在几点`，你会看到日志类似：

```
DEBUG ... Sending chat request: model=qwen-turbo, messages=[...], tools=[getCurrentTime, getTimeByZone]
DEBUG ... Received tool call: getCurrentTime, args={}
DEBUG ... Executing tool: getCurrentTime
DEBUG ... Tool result: "2026-05-12 22:30:15"
DEBUG ... Sending chat request (with tool result): model=qwen-turbo, ...
DEBUG ... Received final text: "现在是 2026 年 5 月 12 日晚上 22:30:15。"
```

**这就是你 Step 1-5 流程的实锤日志**。第一次看到会非常震撼——**你能"看到"AI 是怎么思考的**。

---

## 六、`description` 的玄机（Prompt 工程再次登场）

### 如果 description 写得不好

```java
@Tool(description = "getTime")   // ❌ 写得太简略
public String getCurrentTime() { ... }
```

可能后果：**LLM 不知道什么时候调它**，有时用户问"几点了"它会说"我不知道"。

### 写好 description 的 4 条黄金法则

| 法则 | 例子 |
|------|------|
| **描述功能** | "获取当前日期和时间" |
| **举触发场景** | "用户问'几点'、'今天'时调用" |
| **说明返回** | "返回格式为 yyyy-MM-dd HH:mm:ss" |
| **说明限制** | "只返回服务器本地时间，不是用户时区" |

**完整版**：
```java
@Tool(description = """
        获取服务器当前的日期和时间。
        当用户询问'现在几点'、'今天几号'、'当前时间'、'现在'时调用此工具。
        返回格式：yyyy-MM-dd HH:mm:ss
        注意：返回的是服务器时区（UTC+8），不是用户时区。
        """)
public String getCurrentTime() { ... }
```

> 🎯 **核心心法**：**description 是写给 LLM 看的 Javadoc**。你 Java 的 Javadoc 习惯直接迁移过来。

---

## 七、`@ToolParam` 参数描述

光 `@Tool` 不够，参数也要描述：

```java
@Tool(description = "查询指定订单的状态")
public OrderStatus getOrderStatus(
        @ToolParam(description = "订单的唯一编号，例如 ORD-20260512-0001", required = true)
        String orderId,

        @ToolParam(description = "是否返回详细信息（包含物流轨迹）", required = false)
        boolean includeDetail
) {
    // ...
}
```

LLM 看到 `description` 后能理解**这个参数是什么、怎么填**。
`required = true` 是强制的，LLM 会**一定**传；`false` 则是可选。

---

## 八、常见坑

### ❌ 坑 1：忘了 `@Service`

`@Tool` 的类**必须是 Spring Bean**，否则 `this.timeTool` 拿不到。加 `@Service` 或 `@Component`。

### ❌ 坑 2：description 太短

`description = "查订单"` → LLM 经常不识别。至少写 1-2 句话 + 触发场景。

### ❌ 坑 3：工具方法有副作用但没说清

```java
@Tool(description = "删除订单")   // ⚠️ 不安全
public void deleteOrder(String orderId) { ... }
```

LLM 可能"一激动"就调了。**安全实践**：
- 敏感操作在 description 明确"这是危险操作"
- 加二次确认（"你确认要删除吗？"）
- 记录审计日志

### ❌ 坑 4：在 tool 内部又用 LLM

容易无限递归。**禁止**。

---

## 九、本日小练习

做**两个扩展**：

### 练习 1：加个数学工具

```java
@Tool(description = "计算两个数的乘积，用于精确数学计算（LLM 自己算不准）")
public double multiply(
        @ToolParam(description = "第一个数") double a,
        @ToolParam(description = "第二个数") double b
) {
    return a * b;
}
```

测试：`/chat/agent?q=1234 乘以 5678 等于多少？` 应该返回精确的 `7006652`。

### 练习 2：在 getTimeByZone 里手动写个错误时区，观察 LLM 反应

```java
// 测试: /chat/agent?q=火星上现在几点？
```

LLM 应该识别不到合适的工具，给出"抱歉我没有这个能力"。

---

## ✍️ 本日实战清单

```
[ ] 把 TimeTool.java 写完
[ ] @Tool + @ToolParam 都用上
[ ] ChatService 改成能注入 Tool
[ ] /chat/agent 接口测通
[ ] "现在几点" / "纽约几点" 两个都成功
[ ] 加 DEBUG 日志，亲眼看到 5 步流程
[ ] 完成 multiply 练习，看到 LLM 会"自己算不准就调 Tool"
```

---

## 🎯 今日收官清单

- [ ] 我能 5 步描述 Function Calling 工作原理
- [ ] 我知道"真正调用方法的是 Spring AI，不是 LLM"
- [ ] 我知道 description 写得不好 = Tool 不生效
- [ ] 我会用 `@Tool` + `@ToolParam`
- [ ] 我跑通了 TimeTool
- [ ] 我看过日志，见过 tool_calls 的原始响应

---

## 💡 思考题

### Q：LLM 怎么决定"调不调工具"？

答：**本质是一次文本生成**。它看到 prompt 里有 tools 描述，生成时会按规则产出一个特殊的"我要调工具"的 JSON 格式而不是文本。
这个能力是模型在训练阶段学会的（所以新出的模型 Function Calling 能力通常更强，比如 GPT-4o、Claude 3.5、Qwen-Max 都很强）。

### Q：多个工具放一起会选错吗？

有时候会。**description 越清晰、越不会撞车 → 越不会选错**。
但复杂场景下确实会，这是阶段 4 Agent 要解决的问题（更好的调度机制）。

---

## 🔖 下一步

明天 → [Day 2：多工具协作 + 参数校验](./Day2-多工具协作.md)
