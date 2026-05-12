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
curl -N "http://localhost:8080/chat/stream?q=写一首关于秋天的七言绝句"
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

- [ ] 我能说出同步 vs 流式的差别和价值
- [ ] 我知道 SSE 是什么（和 WebSocket 的区别）
- [ ] 我会用 Spring AI 的 `.stream()` 和 `Flux<String>`
- [ ] 我写了一个简单前端能和后端交互
- [ ] 我理解"首字延迟" 对用户体验的意义

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
