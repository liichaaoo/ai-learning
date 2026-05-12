# Day 2 · 多工具协作 + 参数校验

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**让 AI 组合 3 个工具完成一个任务**（查订单 → 判断状态 → 发通知）

---

## 🧭 今天的剧情

昨天 AI 能调一个工具。**今天要让它一次调多个工具、还要基于结果决定下一步。**

模拟场景：
```
用户问："查一下订单 12345 是什么状态，如果已经发货了告诉我物流单号"

AI 的思考路径：
  1. 调 getOrderStatus(12345) → 返回 "已发货"
  2. 看到已发货，再调 getShippingInfo(12345) → 返回 "SF1234567"
  3. 综合回答：订单 12345 已发货，物流单号 SF1234567
```

**一次用户请求，AI 内部调了 2 次工具，还做了分支判断**。这就是 Agent 的初级形态。

---

## 一、先准备一个"订单工具集"

新建 `src/main/java/com/fletcher/multitools/tools/OrderTool.java`：

```java
package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 订单工具集
 * 在真实项目里，这里会调数据库、调微服务。本例用内存假数据。
 */
@Service
public class OrderTool {

    // 假数据：订单 ID → 状态
    private final Map<String, String> orderStatusMap = new ConcurrentHashMap<>(Map.of(
            "12345", "已发货",
            "12346", "待发货",
            "12347", "已完成",
            "99999", "已取消"
    ));

    // 假数据：订单 ID → 物流单号
    private final Map<String, String> shippingMap = new ConcurrentHashMap<>(Map.of(
            "12345", "SF1234567890",
            "12347", "YTO9876543210"
    ));

    @Tool(description = """
            查询订单的当前状态。
            当用户询问订单进度、订单状态、订单详情时调用此工具。
            返回值示例：'已发货'、'待发货'、'已完成'、'已取消'、'订单不存在'
            """)
    public String getOrderStatus(
            @ToolParam(description = "订单编号，由数字组成，例如 12345", required = true)
            String orderId
    ) {
        // ⚠️ 参数校验：AI 传参可能不合法
        if (orderId == null || orderId.isBlank()) {
            return "错误：订单编号不能为空";
        }
        return orderStatusMap.getOrDefault(orderId, "订单不存在");
    }

    @Tool(description = """
            查询订单的物流信息（快递单号）。
            只有订单状态为'已发货'或'已完成'时才能查到。
            当用户询问物流信息、快递单号、运单号时调用此工具。
            """)
    public String getShippingInfo(
            @ToolParam(description = "订单编号", required = true)
            String orderId
    ) {
        if (orderId == null || orderId.isBlank()) {
            return "错误：订单编号不能为空";
        }
        return shippingMap.getOrDefault(orderId, "该订单暂无物流信息");
    }

    @Tool(description = """
            给用户发送一条短信通知。
            当用户要求发送通知、提醒、短信时调用。
            ⚠️ 这是一个执行类操作（有副作用），确认用户意图后再调用。
            """)
    public String sendSms(
            @ToolParam(description = "收件人手机号，11 位", required = true)
            String phone,

            @ToolParam(description = "短信内容，不超过 70 字", required = true)
            String content
    ) {
        // 参数校验
        if (phone == null || !phone.matches("^1[3-9]\\d{9}$")) {
            return "错误：手机号格式不对";
        }
        if (content == null || content.length() > 70) {
            return "错误：短信内容超长";
        }

        // 模拟发送（真实场景调短信网关）
        System.out.printf("📱 [模拟发送短信] 发往 %s：%s%n", phone, content);
        return "短信已发送成功到 " + phone;
    }
}
```

### 注册到 ChatService

```java
@Service
public class ChatService {

    private final ChatClient chatClient;
    private final TimeTool timeTool;
    private final OrderTool orderTool;

    public ChatService(ChatClient.Builder builder,
                       TimeTool timeTool,
                       OrderTool orderTool) {
        this.chatClient = builder.build();
        this.timeTool = timeTool;
        this.orderTool = orderTool;
    }

    public String chatWithTools(String question) {
        return chatClient
                .prompt()
                .user(question)
                .tools(timeTool, orderTool)      // ⭐ 传入所有工具
                .call()
                .content();
    }
}
```

---

## 二、测试多工具协作 🎉

### 测试 1：单工具（巩固）

```bash
curl "http://localhost:8080/chat/agent?q=查下订单12345"
```
**期望**：AI 调 `getOrderStatus("12345")` → 返回"订单 12345 已发货"

### 测试 2：链式两工具 ⭐

```bash
curl "http://localhost:8080/chat/agent?q=查订单12345的状态，如果已发货告诉我物流单号"
```
**期望的 AI 内部流程**：
```
第 1 轮：调 getOrderStatus("12345") → 返回"已发货"
第 2 轮：看到"已发货"，调 getShippingInfo("12345") → 返回"SF1234567890"
第 3 轮：综合回答："订单 12345 已发货，物流单号是 SF1234567890"
```

### 测试 3：分支判断

```bash
curl "http://localhost:8080/chat/agent?q=查订单99999的状态，发货了就告诉我单号"
```
**期望**：订单已取消，AI 判断"没发货"，就不去调 shipping 工具，只回复状态。

### 测试 4：带执行动作

```bash
curl "http://localhost:8080/chat/agent?q=查下订单12346状态，如果还没发货，给 13800001234 发短信提醒仓库"
```
**期望**：AI 调 3 个工具（查状态 → 判断没发货 → 发短信），最后汇报。

---

## 三、开 DEBUG 日志看戏

再次强调用 DEBUG 日志，你会看到：

```
[Round 1]
  tools request: getOrderStatus args={"orderId":"12345"}
  tool result: "已发货"

[Round 2]
  tools request: getShippingInfo args={"orderId":"12345"}
  tool result: "SF1234567890"

[Round 3]
  final text: "订单 12345 已发货，物流单号是 SF1234567890..."
```

每一轮都是**独立的 LLM 请求**。

---

## 四、参数校验：AI 会传错参数怎么办

### 常见故障场景

1. **参数类型错了**
```
用户: "查订单 1234.5"
AI 可能: getOrderStatus("1234.5")   ← 本来该是字符串整数
```

2. **参数漏传**
```
用户: "发个短信"
AI 可能: sendSms("", "...")   ← 手机号没给
```

3. **参数胡编**
```
用户: "给我老板发短信说我请假"
AI 可能: sendSms("13800000000", "...")   ← 手机号是瞎编的
```

### 防护策略 1：Tool 内部校验（代码层）

**一定不要相信 AI 传的参数**：

```java
@Tool(description = "...")
public String sendSms(
        @ToolParam(description = "手机号", required = true) String phone,
        @ToolParam(description = "内容", required = true) String content) {

    // 1. 空值校验
    if (phone == null || phone.isBlank()) {
        return "错误：手机号不能为空";
    }

    // 2. 格式校验
    if (!phone.matches("^1[3-9]\\d{9}$")) {
        return "错误：手机号格式不正确";
    }

    // 3. 业务校验
    if (!isPhoneInWhitelist(phone)) {
        return "错误：该手机号不在允许列表中";
    }

    // 4. 长度校验
    if (content == null || content.length() > 70) {
        return "错误：短信内容超过 70 字限制";
    }

    // 真正执行
    smsGateway.send(phone, content);
    return "发送成功";
}
```

**思路**：**错误情况返回一个 String 错误描述**，AI 看到错误会在下一轮：
- 自我纠正（再传一次正确的参数）
- 或者告诉用户"你给的手机号格式不对"

> 💡 **心法**：**AI 能看懂错误消息**。写得友好点，AI 能利用这些信息给用户更好的反馈。

### 防护策略 2：Jakarta Validation（声明式）

更"Spring"的方式：

```java
import jakarta.validation.constraints.*;

@Tool(description = "...")
public String sendSms(
        @ToolParam(description = "手机号", required = true)
        @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式错误")
        String phone,

        @ToolParam(description = "内容", required = true)
        @NotBlank @Size(max = 70, message = "短信不超过 70 字")
        String content
) { ... }
```

**注意**：Spring AI 1.0 对 Jakarta Validation 的集成还在完善，**写法可能随版本变化**。推荐先用策略 1（代码校验），稳定。

### 防护策略 3：白名单 + 审计日志

```java
@Tool(description = "重启指定服务（危险操作）")
public String restartService(@ToolParam(description = "服务名") String serviceName) {
    // 1. 白名单校验
    if (!ALLOWED_SERVICES.contains(serviceName)) {
        return "错误：服务 " + serviceName + " 不在可操作列表";
    }

    // 2. 记录审计日志
    auditLog.record("AI_RESTART", serviceName, System.currentTimeMillis());

    // 3. 真正执行
    // ...
    return "重启成功";
}
```

---

## 五、上下文与工具调用次数上限

### Spring AI 默认会限制调用轮数

防止 AI 无限循环（一直调工具但不给答案）。

```yaml
# application.yml
spring:
  ai:
    openai:
      chat:
        options:
          # 可配置单次请求内最多调几次工具（Spring AI 1.x 的选项名可能随版本变化）
          # 检查你当前 Spring AI 版本的文档
          # 常见范围 5-10 轮
```

### 如何 debug

如果 AI "陷入循环"（反复调同一个工具），常见原因：
1. Tool 返回值 LLM 看不懂
2. Tool 返回空或报错但没说清
3. description 不清晰让 LLM 以为没调对

**解法**：检查 Tool 返回值，做成**对 LLM 友好**的字符串：
```java
// ❌ 不好
return null;
return "";
return new Object();

// ✅ 好
return "订单 12345 当前状态为：已发货";
return "查询失败：订单不存在";
```

---

## 六、Tool 返回值可以是对象（Spring AI 自动 JSON 化）

```java
public record OrderDetail(
        String orderId,
        String status,
        String shipping,
        double total
) {}

@Tool(description = "查询订单完整详情")
public OrderDetail getOrderDetail(@ToolParam(description = "订单号") String orderId) {
    return new OrderDetail(orderId, "已发货", "SF1234567", 299.0);
}
```

Spring AI 会把 `OrderDetail` 序列化成 JSON 给 LLM 看，LLM 能读懂每个字段。

---

## 七、本日练习

### 练习 1：扩展 OrderTool

加一个 `cancelOrder(orderId, reason)` 工具，要求：
- 只能取消"待发货"状态的订单
- 取消后把状态改成"已取消"
- reason 必填，长度 5-200 字

### 练习 2：观察链式调用

跑下面 5 个问题，在日志里**数一数 LLM 分别调了几次工具**：

```
1. "现在几点？"                              → 应该 1 次
2. "查订单 12345"                           → 应该 1 次
3. "查订单 12345，发货了告诉我物流单号"        → 应该 2 次
4. "取消订单 12346，理由是我不想要了"          → 应该 1 次（如果写了 cancelOrder）
5. "取消订单 12345，理由是太贵了"              → 应该 1 次（然后工具返回错误）
```

---

## ✍️ 本日实战清单

```
[ ] OrderTool.java 完成（getOrderStatus / getShippingInfo / sendSms）
[ ] ChatService 注册两个 Tool
[ ] 单工具测试通过
[ ] 链式两工具测试通过（关键里程碑 ⭐）
[ ] 参数校验代码完整
[ ] DEBUG 日志看到工具调用的多轮过程
[ ] 练习 1：cancelOrder 工具完成
```

---

## 🎯 今日收官清单

- [ ] 我理解 AI 可以在一次请求里调多个工具
- [ ] 我知道 AI 内部是通过"多轮 LLM 请求"实现工具组合
- [ ] 我的 Tool 都做了参数校验
- [ ] 我知道 Tool 报错时返回友好的字符串让 AI 能纠正
- [ ] 我看到了多轮调用的日志
- [ ] 我理解"AI 传的参数不可信"的安全哲学

---

## 💡 一个有趣的观察

注意这段对话：

```
用户: "查订单 ORD-xxx-001"
AI:  getOrderStatus("ORD-xxx-001")
     → 工具返回："订单不存在"
AI:  "抱歉，系统里找不到这个订单，请确认订单号是否正确。"
```

**AI 没有瞎编一个假状态告诉用户**。这就是 Function Calling 带来的**真实性保障**。

对比一下，不用工具：
```
用户: "查订单 ORD-xxx-001"
AI（无工具）: "您的订单 ORD-xxx-001 正在发货中..."  ← 幻觉！编的！
```

**这就是为什么企业级 AI 应用几乎一定要接工具**：让 AI 说真话。

---

## 🔖 下一步

明天 → [Day 3：多模型接入](./Day3-多模型接入.md)
