# Day 4 · 多模型路由策略

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**一个"AI 路由器"，根据问题自动挑最合适的模型 + 主模型挂了自动降级**

---

## 🧭 今天做什么

昨天你有 2 个模型（通义 + Ollama），但得写死代码选用哪个。
今天让系统**自动选**：

```
用户："今天天气怎样？"             → 路由到【便宜模型】（简单问题）
用户："帮我写一段算法代码"          → 路由到【聪明模型】（复杂）
用户："这份合同 PDF 有什么风险？"  → 路由到【本地模型】（敏感数据）
```

**这就是生产环境的真实做法**，也是简历上的一个亮点。

---

## 一、路由策略分类

### 策略 1：按成本路由（最常见）⭐

```
用户请求
  ↓
[简单任务] → 便宜模型（qwen-turbo）    ← 省钱
[复杂任务] → 贵模型（qwen-max/gpt-4o）  ← 保证质量
```

### 策略 2：按场景路由

```
代码问题     → GPT-4 或 Claude（代码强）
中文对话     → 通义
敏感问题     → 本地 Ollama
图文问题     → 多模态模型
```

### 策略 3：按用户等级

```
VIP 用户     → 好模型
普通用户     → 便宜模型
白嫖用户     → 更便宜
```

### 策略 4：按健康度（降级）

```
主模型可用   → 主模型
主模型挂了   → 备模型兜底
```

### 策略 5：混合路由

真实生产 = **以上策略的组合**。比如：

```
if VIP → GPT-4
elif 简单 → qwen-turbo
elif 代码 → GPT-4-mini
else → qwen-plus

任何模型挂了 → 降级到 Ollama 本地
```

---

## 二、实现一个简单路由器

### 2.1 定义路由"复杂度"

先做一个**很简单**的规则："按 token 长度判断复杂度"。
（真实项目会更复杂，有的会用小模型分类）

### 2.2 新建 ModelRouterService

```java
package com.fletcher.multitools.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

/**
 * AI 模型路由器
 * 根据问题特征自动选择最合适的模型
 */
@Service
public class ModelRouterService {

    private final ChatClient qwenClient;      // 便宜
    private final ChatClient ollamaClient;    // 本地

    // 如果你接了 OpenAI，再加一个
    // private final ChatClient openAiClient;    // 聪明贵

    public ModelRouterService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            @Qualifier("ollamaClient") ChatClient ollamaClient) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
    }

    /**
     * 按复杂度路由
     */
    public String routeByComplexity(String question) {
        Complexity c = judgeComplexity(question);
        return switch (c) {
            case SIMPLE -> {
                System.out.println("[ROUTER] SIMPLE → qwen-turbo");
                yield qwenClient.prompt().user(question).call().content();
            }
            case COMPLEX -> {
                System.out.println("[ROUTER] COMPLEX → qwen-max（如已接入）或通义");
                // 这里为了简化，依然用 qwenClient 但可以切换模型配置
                yield qwenClient.prompt().user(question).call().content();
            }
            case SENSITIVE -> {
                System.out.println("[ROUTER] SENSITIVE → Ollama 本地");
                yield ollamaClient.prompt().user(question).call().content();
            }
        };
    }

    /**
     * 按"敏感词"判断是否走本地
     */
    public String routeByPrivacy(String question) {
        boolean sensitive = containsSensitiveKeyword(question);
        if (sensitive) {
            System.out.println("[ROUTER] SENSITIVE → Ollama");
            return ollamaClient.prompt().user(question).call().content();
        }
        System.out.println("[ROUTER] PUBLIC → qwen");
        return qwenClient.prompt().user(question).call().content();
    }

    /**
     * 带降级的调用：主模型挂了自动切备用
     */
    public String callWithFallback(String question) {
        try {
            return qwenClient.prompt().user(question).call().content();
        } catch (Exception e) {
            System.err.println("[FALLBACK] 通义挂了，切 Ollama: " + e.getMessage());
            return ollamaClient.prompt().user(question).call().content();
        }
    }

    // ================ 内部判断逻辑 ================

    private enum Complexity { SIMPLE, COMPLEX, SENSITIVE }

    private Complexity judgeComplexity(String question) {
        if (containsSensitiveKeyword(question)) return Complexity.SENSITIVE;

        int len = question.length();
        boolean hasCodeKeyword = question.contains("代码") || question.contains("算法")
                || question.contains("实现") || question.contains("写一段");

        // 简单规则：长文本 or 带代码关键词 = 复杂
        if (len > 100 || hasCodeKeyword) return Complexity.COMPLEX;
        return Complexity.SIMPLE;
    }

    private boolean containsSensitiveKeyword(String q) {
        if (q == null) return false;
        return q.contains("合同") || q.contains("内部") || q.contains("密码")
                || q.contains("身份证") || q.contains("薪资");
    }
}
```

### 2.3 Controller

```java
@GetMapping("/chat/auto")
public String auto(@RequestParam String q) {
    return modelRouterService.routeByComplexity(q);
}

@GetMapping("/chat/privacy")
public String privacy(@RequestParam String q) {
    return modelRouterService.routeByPrivacy(q);
}

@GetMapping("/chat/safe")
public String safe(@RequestParam String q) {
    return modelRouterService.callWithFallback(q);
}
```

### 2.4 测试

```bash
# 简单问题，走便宜
curl "http://localhost:8080/chat/auto?q=你好"
# 日志: [ROUTER] SIMPLE → qwen-turbo

# 复杂问题
curl "http://localhost:8080/chat/auto?q=帮我写一段 Java 快速排序代码"
# 日志: [ROUTER] COMPLEX → qwen-max

# 敏感
curl "http://localhost:8080/chat/privacy?q=帮我分析这份合同"
# 日志: [ROUTER] SENSITIVE → Ollama
```

---

## 三、进阶：用小模型当"路由器"

更"AI 原生"的做法：**用一个小模型去分类**，然后决定走哪个大模型。

```java
public String smartRoute(String question) {
    // 1. 先用一个便宜模型快速分类
    String classification = qwenClient
            .prompt()
            .system("""
                    你是一个任务分类器。下面用户问题属于哪一类？
                    只返回分类 ID，不要多说。
                    分类 ID：
                    - simple：闲聊、问候、事实性问答
                    - code：代码相关
                    - reasoning：数学推理、分析
                    - sensitive：涉及敏感信息（合同、密码、薪资）
                    """)
            .user(question)
            .call()
            .content()
            .trim()
            .toLowerCase();

    // 2. 按分类路由
    return switch (classification) {
        case "simple" -> qwenClient.prompt().user(question).call().content();
        case "code", "reasoning" -> qwenClient.prompt().user(question).call().content();
            // 真实场景这里应该路由到 GPT-4 或 Claude
        case "sensitive" -> ollamaClient.prompt().user(question).call().content();
        default -> qwenClient.prompt().user(question).call().content();
    };
}
```

**优点**：比硬编码规则**更智能**，能覆盖边缘情况。
**缺点**：每次请求要**多调一次 LLM**（+1 延迟 + 1 份成本）。

### 经验平衡

真实生产：**简单规则 + 小模型分类** 混合。
- 命中明确规则（比如包含"合同"） → 直接路由
- 模糊情况 → 用小模型分类

---

## 四、降级（Fallback）的 4 种做法

### 4.1 try-catch 简单降级（上面已演示）

```java
try { primary.call(); }
catch (Exception e) { fallback.call(); }
```

### 4.2 Spring Retry + Fallback

用 Spring 的 `@Retryable` + `@Recover`：

```java
@Retryable(value = Exception.class, maxAttempts = 3, backoff = @Backoff(delay = 1000))
public String callPrimary(String q) {
    return qwenClient.prompt().user(q).call().content();
}

@Recover
public String fallback(Exception e, String q) {
    return ollamaClient.prompt().user(q).call().content();
}
```

### 4.3 Resilience4j 熔断

```
正常 → 主模型
连续失败 3 次 → 熔断打开 → 全部走备用
熔断等一会 → 半开 → 偶尔试探主模型
```

真实生产级推荐用这个。

### 4.4 Spring AI 自带 RetryTemplate / Advisor

Spring AI 内部 retry 机制（**具体 API 以版本为准**）：

```java
ChatClient client = ChatClient.builder(model)
        .defaultAdvisors(
                new SimpleLoggerAdvisor(),
                // 如果有 retry advisor 也可以加
        )
        .build();
```

---

## 五、成本监控（顺便提一下）

多模型最大价值 = **省钱**。所以要能**监控**：

```java
@Service
public class CostMonitor {
    private final AtomicLong qwenTokens = new AtomicLong();
    private final AtomicLong openaiTokens = new AtomicLong();

    public void recordQwen(long tokens) { qwenTokens.addAndGet(tokens); }
    public void recordOpenAi(long tokens) { openaiTokens.addAndGet(tokens); }

    public Map<String, Object> summary() {
        // 通义 qwen-turbo: 约 0.3 元/百万 token
        double qwenCost = qwenTokens.get() / 1_000_000.0 * 0.3;
        // gpt-4o-mini: 约 0.15 美元/百万 token
        double openaiCost = openaiTokens.get() / 1_000_000.0 * 0.15;

        return Map.of(
                "qwenTokens", qwenTokens.get(),
                "openaiTokens", openaiTokens.get(),
                "qwenCostRMB", qwenCost,
                "openaiCostUSD", openaiCost
        );
    }
}
```

在 `ChatClient.call().chatResponse()` 可以拿到 `usage` 字段，累加进去。

**简历上的亮点 JD**：
> "设计多模型路由，按成本动态选择，**月度推理成本降低 40%**"
> （这个 40% 不是瞎编，真实项目这个范围很常见）

---

## 六、本日的完整 Controller 应该长这样

把 Week 1 Day 5 到现在积累的所有接口汇总（你的 `ChatController` 现在应该像个控制台）：

```java
@RestController
public class ChatController {

    private final ChatService chatService;
    private final ModelRouterService routerService;

    public ChatController(ChatService chatService, ModelRouterService routerService) {
        this.chatService = chatService;
        this.routerService = routerService;
    }

    // ========== Week 1 功能 ==========
    @GetMapping("/chat")              public String chat(@RequestParam String q) { return chatService.chat(q); }
    @GetMapping("/chat/expert")       public String expert(@RequestParam String q) { return chatService.chatAsExpert(q); }
    // ... /chat/stream、/chat/recipe 等

    // ========== Week 2 Day 1-2 ==========
    @GetMapping("/chat/agent")        public String agent(@RequestParam String q) { return chatService.chatCheapWithTools(q); }

    // ========== Week 2 Day 3 ==========
    @GetMapping("/chat/cheap")        public String cheap(@RequestParam String q) { return chatService.chatCheap(q); }
    @GetMapping("/chat/local")        public String local(@RequestParam String q) { return chatService.chatLocal(q); }

    // ========== Week 2 Day 4 ==========
    @GetMapping("/chat/auto")         public String auto(@RequestParam String q) { return routerService.routeByComplexity(q); }
    @GetMapping("/chat/privacy")      public String privacy(@RequestParam String q) { return routerService.routeByPrivacy(q); }
    @GetMapping("/chat/safe")         public String safe(@RequestParam String q) { return routerService.callWithFallback(q); }
    @GetMapping("/chat/smart")        public String smart(@RequestParam String q) { return routerService.smartRoute(q); }
}
```

---

## 七、一个真实生产的路由示意图（简历可以画）

```
              用户请求
                 │
      ┌──────────┼──────────┐
      │          │          │
    规则筛       AI 分类    成本约束
      │          │          │
      └──────────┴──────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
  qwen-turbo  qwen-max    ollama
  (快+便宜)   (聪明+稍贵)  (免费+本地)
     │           │           │
     └───────────┼───────────┘
                 │
           Resilience4j 熔断
                 │
                 ▼
              返回响应

  旁路：审计日志、成本监控、Token 统计
```

---

## 八、本日实战清单

```
[ ] ModelRouterService 写完
[ ] 3 种路由策略（复杂度、隐私、降级）都实现
[ ] 对应的 /chat/auto /chat/privacy /chat/safe 测通
[ ] 日志里能看到路由决策（[ROUTER] xxx → yyy）
[ ] 测试"故意拔掉 Ollama" 看降级是否生效
[ ] （选做）实现 smartRoute - 用小模型做分类
[ ] （选做）CostMonitor 记录一下 token 用量
```

---

## 🎯 今日收官清单

- [ ] 我能说出至少 3 种路由策略的适用场景
- [ ] 我写了一个 ModelRouterService
- [ ] 我知道"小模型分类" vs "规则路由"的 trade-off
- [ ] 我的系统有降级机制（主模型挂了能切备用）
- [ ] 我理解为什么多模型路由能"降本 40%"
- [ ] 我能在简历上写出多模型架构的亮点

---

## 💡 心得

你今天做的多模型路由 + 降级 + 成本监控，**已经超过 80% 的外面所谓"AI 应用开发者"**。

大多数人做 AI 项目：
- ❌ 只接一个模型
- ❌ 硬编码模型名
- ❌ 挂了就挂了

你做的：
- ✅ 接多个模型
- ✅ 动态路由
- ✅ 有降级兜底
- ✅ 能成本监控

**这是高级工程师的 AI 落地能力**，也是你 7 年 Java 工程经验的**复用变现**。

---

## 🔖 下一步

明天（周末）→ [Day 5：整合 Demo - 智能运维助手](./Day5-整合Demo.md) ⭐ 毕业项目
