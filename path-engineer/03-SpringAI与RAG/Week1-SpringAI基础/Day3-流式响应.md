# Day 3 · 流式响应（像 ChatGPT 那样"一字一字蹦"）

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**浏览器访问 `/chat/stream?q=...`，看到文字一个字一个字实时蹦出来**

---

## 🧭 今天你要搞懂

1. **什么是流式响应**（Streaming）？
2. **SSE 是啥**？和 WebSocket 差在哪？
3. **Spring AI 里怎么用流式**？
4. **前端怎么接收流式数据**？（简单的 HTML 就够）

---

## 一、为什么要流式？

### 不流式的痛点

昨天你写的 `/chat`：
```java
.call()         // 同步！等 LLM 把整段回复全部生成完
.content();     // 一次性返回
```

**用户体验**：
```
输入问题  →  等 10 秒  →  一次性出来 500 字
          （这 10 秒啥都看不到，用户会以为卡了）
```

### 流式的效果

ChatGPT 这样：
```
输入问题  →  立刻开始蹦字  →  蹦完
           （用户马上有"模型在思考"的反馈）
```

**核心优势**：**首字延迟**从 10 秒降到 500ms（用户体感上快了 20 倍）。

### 为什么能流式？

因为 LLM 本身就是**一个字一个字生成**的（自回归）。模型服务器在生成过程中就能把已生成的部分**先吐出来**，不用等完整答复。

---

## 二、SSE（Server-Sent Events）快速认识

### 什么是 SSE

**一种 HTTP 协议的"流式响应"机制**。
服务器发一个**永不结束**的响应，每隔一段时间往这个响应里写一小段数据。

**对比 WebSocket**：

| | SSE | WebSocket |
|---|-----|-----------|
| **方向** | 只能服务器→客户端 | 双向 |
| **协议** | 标准 HTTP | 升级协议 |
| **复杂度** | 简单，浏览器原生支持（EventSource）| 复杂 |
| **LLM 场景** | ⭐ 够用（只需要服务器推客户端）| 杀鸡用牛刀 |

**LLM 流式用 SSE** —— OpenAI 协议也是 SSE。

### SSE 报文长这样

服务器返回：
```
data: {"choices":[{"delta":{"content":"你"}}]}

data: {"choices":[{"delta":{"content":"好"}}]}

data: {"choices":[{"delta":{"content":"，"}}]}

...

data: [DONE]
```

每段数据用空行隔开，每段一个 JSON 里是**这一小段内容**。

**Spring AI 帮你把这堆 JSON 拼成字符串流**，你不用手动解析。

---

## 三、Spring AI 流式 API

### 3.1 改一下 Controller

在 `ChatController.java` 里**新增**一个方法：

```java
import reactor.core.publisher.Flux;
import org.springframework.http.MediaType;

// ... 已有 imports ...

@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam("q") String question) {
    return chatClient
            .prompt()
            .user(question)
            .stream()          // ⭐ 不再是 .call()，改成 .stream()
            .content();        // 返回 Flux<String>（响应式流）
}
```

### 3.2 关键变化（和昨天的 `/chat` 对比）

| 昨天（同步） | 今天（流式） |
|-------------|-------------|
| `.call()` | `.stream()` |
| 返回 `String` | 返回 `Flux<String>` |
| 一次性拿全部 | 一段一段拿 |
| `produces` 默认 JSON | `produces = TEXT_EVENT_STREAM_VALUE` ⭐ |

### 3.3 什么是 Flux

`Flux<T>` 是 **Project Reactor**（Spring 官方响应式框架）里的**数据流**。

Java 程序员第一次见会懵，但你只要知道：
- `Flux<String>` = "一个会陆续吐出字符串的管道"
- Spring 看到 Controller 返回 Flux + `produces: text/event-stream`，自动帮你用 SSE 协议发给前端
- **你不用写任何异步代码**，Spring AI 和 Spring Web 把异步处理都做好了

---

## 四、测试流式接口

### 4.1 用 curl 测试

```bash
curl -N "http://localhost:8080/chat/stream?q=hello"
```

**重点**：`-N` 是 `--no-buffer`，让 curl 不要等完整响应再显示。
你应该看到：
```
data:你

data:好

data:，

data:秋

...
```

一个字一个字的蹦出来（如果你看到是整块的，说明没用 `-N`）。

### 4.2 用浏览器原生 EventSource

新建 `src/main/resources/static/index.html`（Spring Boot 会自动把 static 目录当静态资源）：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hello Spring AI</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; }
        input { width: 70%; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #output { margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 8px; min-height: 100px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>🤖 Hello Spring AI</h1>
    <input id="q" placeholder="问点什么..." value="用三句话介绍苹果公司" />
    <button onclick="send()">发送</button>
    <div id="output"></div>

    <script>
        function send() {
            const q = document.getElementById('q').value;
            const output = document.getElementById('output');
            output.textContent = '';

            // 用浏览器原生 EventSource，支持 SSE
            const source = new EventSource(`/chat/stream?q=${encodeURIComponent(q)}`);

            source.onmessage = (e) => {
                output.textContent += e.data;   // 每次追加一小段
            };

            source.onerror = () => {
                source.close();   // 服务器流结束后关闭
            };
        }
    </script>
</body>
</html>
```

### 4.3 用浏览器打开

重启服务后访问：
```
http://localhost:8080/index.html
```

在输入框里敲问题，点发送。
你会看到文字**一个字一个字蹦出来**，和 ChatGPT 一样。

---

## 五、深入理解："蹦字"是怎么实现的

### 完整链路

```
前端 index.html
  │ new EventSource('/chat/stream?q=...')
  │ 建立一个 SSE 长连接
  ▼
Spring Boot ChatController
  │ 返回 Flux<String>
  │ Spring 把每个 element 包装成 SSE 格式 "data: xxx\n\n"
  ▼
Spring AI
  │ 调用通义千问的 /chat/completions（带 stream=true）
  ▼
通义千问服务器
  │ 模型每生成一个 token（或几个），立即 push
  │ SSE: data: {"delta":{"content":"你"}}
  │ SSE: data: {"delta":{"content":"好"}}
  ▼
Spring AI 解析每段，转成 Java 字符串
  ▼
Flux 往前端推
  ▼
前端 source.onmessage 触发
  │ output.textContent += "你"
  │ output.textContent += "好"
  ▼
用户看到文字在"长出来"
```

**全过程是非阻塞的**，不占用 Tomcat 线程池。

---

## 六、生产级的一些注意

### 6.1 错误处理

```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam("q") String question) {
    return chatClient
            .prompt()
            .user(question)
            .stream()
            .content()
            .onErrorResume(e -> {
                // 错误时返回一段错误提示，不让前端挂
                return Flux.just("【出错了】" + e.getMessage());
            });
}
```

### 6.2 超时控制

```java
.timeout(Duration.ofSeconds(60))   // 60 秒没完就断
```

### 6.3 Token 计数（了解即可）

流式模式下，可以边收边统计 Token。Week 5-6 做 RAG 项目时会用到（成本监控）。

---

## 七、"内容 Flux" vs "完整 ChatResponse Flux"

Spring AI 的 `.stream()` 之后，有两种方式：

```java
// 方式 1：只要文本流 ⭐ 简单
.stream().content()              // Flux<String>

// 方式 2：要完整的 ChatResponse 流（含 usage、finish_reason 等）
.stream().chatResponse()         // Flux<ChatResponse>
```

**今天用方式 1**，方式 2 以后做成本统计、日志时会用。

---

## 八、一个工程习惯建议

上面的 `ChatController` 已经挺长了，建议**把业务逻辑抽到 Service 层**（你是资深 Java，这对你是肌肉记忆）：

```java
// ChatService.java
@Service
public class ChatService {
    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String chat(String question) {
        return chatClient.prompt().user(question).call().content();
    }

    public Flux<String> chatStream(String question) {
        return chatClient.prompt().user(question).stream().content();
    }
}

// ChatController.java 瘦身
@RestController
public class ChatController {
    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @GetMapping("/chat")
    public String chat(@RequestParam String q) {
        return chatService.chat(q);
    }

    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestParam String q) {
        return chatService.chatStream(q);
    }
}
```

这是你做了 7 年 Java 的本能，今天**一起把项目结构打好**，Week 5-6 做大项目时会非常感谢自己。

---

## ✍️ 本日实战清单

```
[ ] 新增了 /chat/stream 接口
[ ] curl -N 测试能看到流式输出
[ ] 写了 index.html，浏览器打开能交互
[ ] 看到文字一个字一个字蹦出来（像 ChatGPT）
[ ] 把逻辑抽到 ChatService（工程习惯）
```

---

## 🎯 今日收官清单

- [x] 我能说出同步 vs 流式的差别和价值
- [x] 我知道 SSE 是什么（和 WebSocket 的区别）
- [x] 我会用 Spring AI 的 `.stream()` 和 `Flux<String>`
- [x] 我写了一个简单前端能和后端交互
- [x] 我理解"首字延迟" 对用户体验的意义

---

## 💡 思考题（不用写答案，想想就好）

1. 如果前端想**中途取消**生成（用户按了"停止"按钮），后端怎么做？
   - 提示：关闭 EventSource → Spring Reactor 的 Flux 会收到 cancel 信号
2. 如果我想记录**每次对话的总 Token 用量**，流式模式下该怎么做？
   - 提示：用 `.stream().chatResponse()`，拿每段的 `usage`

这些都是**面试 Spring AI 常考题**，你已经能答出一半了。

---

## 🔖 下一步

明天 → [Day 4：Prompt 模板 + System Prompt](./Day4-Prompt工程.md)

---

## 📎 补充：流式响应进阶（TTFT、速率控制、生产实践）

> 这一节回答两个常见疑问：
> 1. **首字延迟（TTFT）有多重要？怎么优化？**
> 2. **业务里要不要主动控制流式输出的速率？**

---

### A. 首字延迟（TTFT, Time To First Token）

流式体验的核心指标。用户等 1 秒和等 3 秒的体感差别，比从 5 秒压到 3 秒大得多。

#### A.1 TTFT 由什么决定

| 阶段 | 影响 | 优化手段 |
|---|---|---|
| Prompt prefill（模型一次性读完 prompt） | prompt 越长越慢 | 控长度、prompt 缓存、KV cache 复用 |
| 网络往返 | 跨地域明显 | 服务就近、HTTP/2、连接复用 |
| 服务端缓冲 | Tomcat、Spring、网关都可能 buffer | 后面 A.3 单独讲 |
| 业务前置操作 | RAG 检索、鉴权、审计同步阻塞 | 先吐占位、检索改成异步并行 |

#### A.2 "假首字" 技巧（产品级套路）

ChatGPT、Claude、Gemini 都用这个，把感知 TTFT 从 1.5s 压到 100ms 内：

```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam("q") String q) {
    return Flux.concat(
            Flux.just(" "),                           // 立刻 flush 一个空格，欺骗感知
            chatService.chatStream(q)                 // 真实模型流
    );
}
```

更进一步：在前端先渲染一个"思考中"的动画，收到第一个真实 token 时再替换掉。

#### A.3 关闭中间链路的缓冲（最容易踩坑）

流式失败 9 成是被某层 buffer 了，整段一次性返回。

**Spring Boot 自身**：返回 `Flux<String>` + `produces = TEXT_EVENT_STREAM_VALUE` 默认就是 flush 的，不用配。

**Nginx**（最常见的坑）：
```nginx
location /chat/stream {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_buffering off;          # ⭐ 关键
    proxy_cache off;              # ⭐ 关键
    proxy_set_header Connection '';
    chunked_transfer_encoding on;
    proxy_read_timeout 300s;      # SSE 是长连接，超时拉长
}
```

**响应头里加一行**（绕过部分代理的 buffer，比如 Nginx 的 `X-Accel-Buffering`）：
```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public ResponseEntity<Flux<String>> chatStream(@RequestParam String q) {
    return ResponseEntity.ok()
            .header("X-Accel-Buffering", "no")
            .header("Cache-Control", "no-cache")
            .body(chatService.chatStream(q));
}
```

---

### B. 要不要主动控制输出速率？

**简短答案：默认不要管，让模型全速吐。少数场景需要"反向节流"——也就是放慢。**

#### B.1 默认全速最好

- 越快越好，用户感知吞吐高、等待短。
- 前端有自己的渲染节流（CSS 打字机、`requestAnimationFrame` 批量更新），**显示流畅度由前端控制，和后端速率无关**。
- 后端主动 sleep 既浪费连接，又拉长总耗时。

#### B.2 少数需要主动放慢的场景

| 场景 | 为什么慢 | 做法 |
|---|---|---|
| **TTS 边吐边读** | 语音播放速度有上限，token 来太快堆积/丢弃 | 按句号/逗号 buffer 后再发 |
| **下游有 RPM/TPM 限额** | 防止瞬时打爆配额 | 服务端令牌桶限流 |
| **演示 / Demo / 录屏** | 真实模型太快看不清 | 加固定 delay |
| **付费档位差异化**（免费用户限速） | 商业策略 | 网关层限速 |
| **背压**：客户端慢、网络差 | 防止内存堆积 OOM | Reactor 的 `onBackpressureBuffer` |

#### B.3 Reactor 速率控制写法（备用）

```java
import java.time.Duration;
import reactor.core.publisher.BufferOverflowStrategy;

// 1. 每个 token 之间间隔 50ms（Demo 用，生产慎用）
chatClient.prompt().user(q).stream().content()
    .delayElements(Duration.ofMillis(50));

// 2. 背压保护：缓冲不超过 256，超了丢最旧
chatClient.prompt().user(q).stream().content()
    .onBackpressureBuffer(256, BufferOverflowStrategy.DROP_OLDEST);

// 3. 按句号聚合后再发（适合 TTS / 句子级翻译）
chatClient.prompt().user(q).stream().content()
    .bufferUntil(t -> t.contains("。") || t.contains("\n"))
    .map(list -> String.join("", list));
```

---

### C. SSE 心跳（防止网关 60s 断连）

许多反向代理会把空闲超过 60s 的连接掐掉。流式里如果模型 prefill 很慢（比如 prompt 巨长），TTFT 就可能踩到这个超时。

加心跳：
```java
public Flux<String> chatStream(String q) {
    Flux<String> heartbeat = Flux.interval(Duration.ofSeconds(15))
            .map(i -> ":ping");                 // SSE 注释行，浏览器 EventSource 会忽略
    Flux<String> body = chatService.chatStream(q);
    return Flux.merge(body, heartbeat).takeUntilOther(body.ignoreElements());
}
```

> SSE 协议里以 `:` 开头的行是注释，浏览器 EventSource 自动忽略，但能让中间网关感知到连接活跃。

---

### D. 客户端断线 → 释放后端 LLM 调用（省钱）

用户关页面后，模型还在继续吐，要白白付费几秒到几十秒的 token 钱。
Reactor 的 `Flux` 会在客户端断开时收到 cancel 信号，业务里可以挂钩：

```java
public Flux<String> chatStream(String q) {
    return chatClient.prompt().user(q).stream().content()
            .doOnCancel(() -> log.info("client disconnected, q={}", q))
            .doOnError(e -> log.warn("stream error", e))
            .doFinally(sig -> log.info("stream end, signal={}", sig));
}
```

Spring AI 的 OpenAI/DashScope client 在 Flux 被 cancel 时会关闭底层 HTTP 连接，模型那边随之停止生成。**前提是不要在中间加 `.cache()` / `.publish()` 这种把流"留住"的操作符。**

---

### E. 错误也要"流式"地告诉前端

如果半截出错直接抛 500，前端 EventSource 只会收到 `onerror`，看不到原因。
最佳实践是把错误转成一段 SSE 数据：

```java
public Flux<String> chatStream(String q) {
    return chatClient.prompt().user(q).stream().content()
            .onErrorResume(e -> Flux.just("\n[ERROR] " + safeMsg(e)));
}

private String safeMsg(Throwable e) {
    // 别把堆栈、API key、内部地址泄露给前端
    return e instanceof TimeoutException ? "请求超时，请重试"
         : "服务繁忙，请稍后再试";
}
```

---

### F. 监控三件套（生产必备）

只看"总耗时"会丢失流式的核心体验信息，至少埋三个指标：

| 指标 | 含义 | 报警阈值参考 |
|---|---|---|
| **TTFT** | 请求开始到第一个 token 的耗时 | P95 > 2s 报警 |
| **TPS / Tokens per second** | 每秒输出 token 数 | 模型类型决定，掉一半要查 |
| **Total latency** | 总耗时 | P95 > 30s 报警 |

Reactor 里实现：
```java
public Flux<String> chatStream(String q) {
    long start = System.currentTimeMillis();
    AtomicLong firstTokenAt = new AtomicLong(0);
    AtomicInteger tokens = new AtomicInteger(0);

    return chatClient.prompt().user(q).stream().content()
            .doOnNext(t -> {
                if (firstTokenAt.compareAndSet(0, System.currentTimeMillis())) {
                    metrics.recordTtft(firstTokenAt.get() - start);
                }
                tokens.incrementAndGet();
            })
            .doFinally(sig -> {
                long total = System.currentTimeMillis() - start;
                metrics.recordTotal(total);
                if (firstTokenAt.get() > 0) {
                    long gen = total - (firstTokenAt.get() - start);
                    if (gen > 0) metrics.recordTps(tokens.get() * 1000.0 / gen);
                }
            });
}
```

---

### G. 一句话总结

> **TTFT 优化是必修课，速率节流是选修课。**
> 业务默认全速吐字 + 关掉中间 buffer + 加心跳和断线回收，体验和成本就同时拿到了。

---

### 📋 生产 Checklist

```
[ ] /chat/stream 关闭了 Nginx proxy_buffering
[ ] 响应头加了 X-Accel-Buffering: no
[ ] 加了 SSE 心跳防 60s 断连
[ ] doOnCancel 释放了 LLM 调用（断线省钱）
[ ] 错误用 SSE 数据返回，不抛 500
[ ] 埋了 TTFT / TPS / total latency 三个指标
[ ] 超时设置 .timeout(Duration.ofSeconds(60))
[ ] 敏感错误信息脱敏后再返回前端
```

