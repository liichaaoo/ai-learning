# Day 3 · 多模型接入（一个工程多个 LLM）

> ⏱️ 目标时间：1.5-2 小时
> 🎯 产出：**一个 Spring Boot 工程同时跑通通义千问 + 本地 Ollama**

---

## 🧭 今天的目标

你会把 Week 1 的 "只接通义" 升级为 "同时接 2-4 个模型"：

```
你的工程
   │
   ├── 通义千问（云端 / 便宜 / 中文好）
   ├── Ollama  （本地 / 免费 / 私有化）
   ├── OpenAI  （可选，国际强模型）
   └── Claude  （可选，高质量推理）
```

**为什么要多模型？**
- 🟢 **成本优化**：便宜模型做简单任务，贵模型只在复杂时用
- 🟢 **数据安全**：内部数据用本地模型，不传云
- 🟢 **高可用**：一个挂了切另一个
- 🟢 **效果兜底**：A/B 对比，选更适合的

---

## 一、概念：ChatModel vs ChatClient

多模型之前先搞清楚这对概念（面试必问）：

### `ChatModel`
**底层 API**，直接和某个厂商的 LLM 通信。
```
OpenAiChatModel     - 连 OpenAI 或通义（兼容协议）
OllamaChatModel     - 连本地 Ollama
AnthropicChatModel  - 连 Claude
```

每个厂商一个。**不带记忆、不带 Advisor、不带 Tool，只管发请求收响应**。

### `ChatClient`
**上层封装**，在 ChatModel 基础上加了：
- Prompt 构造器（`.prompt().user().system()`）
- Advisor 机制（记忆、RAG、日志）
- Tools 注册
- Fluent API

### 关系

```
你代码里用 ChatClient（上层）
          ↓
ChatClient 内部调 ChatModel（底层）
          ↓
ChatModel 发 HTTP 请求给 LLM 服务器
```

### 一个 ChatClient 对应一个 ChatModel

```java
ChatClient clientA = ChatClient.builder(openAiChatModel).build();    // 连 OpenAI
ChatClient clientB = ChatClient.builder(ollamaChatModel).build();    // 连 Ollama
```

所以**多模型的本质 = 创建多个 ChatModel + 多个 ChatClient**。

---

## 二、先装 Ollama（15 分钟）

### 2.1 下载安装

Mac 一行命令：
```bash
brew install ollama
# 或从 https://ollama.com/ 下载安装包
```

启动 Ollama 后台服务：
```bash
ollama serve
# 默认监听 http://localhost:11434
```

### 2.2 下载一个模型

```bash
# 下载 qwen2.5 7B（质量不错，约 4.4 GB）
ollama pull qwen2.5:7b

# 更小更快（2 GB，质量稍逊）
ollama pull qwen2.5:3b

# 或 llama3
ollama pull llama3.2:3b
```

下载后列出：
```bash
ollama list
```

### 2.3 命令行测试

```bash
ollama run qwen2.5:7b
# 进入交互式，输入"你好"，看能不能回复
# Ctrl+D 退出
```

能回复 → 本地模型装好了。

---

## 三、一个工程接 2 个模型（通义 + Ollama）

### 3.1 加依赖

在 `pom.xml` **新增** Ollama 的 starter：

```xml
<!-- 已有：OpenAI starter（用于调通义） -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-openai</artifactId>
</dependency>

<!-- 新增：Ollama starter -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-ollama</artifactId>
</dependency>
```

### 3.2 挑战：两个 starter 一起加会怎样？

**会出问题**：两个 starter 都想自动创建 `ChatClient.Builder`，Spring 会报**冲突**：
```
org.springframework.beans.factory.NoUniqueBeanDefinitionException
```

**解法**：**手动关闭自动配置**，自己定义两个 `ChatModel` 和对应的 `ChatClient`。

### 3.3 application.yml 完整配置

```yaml
server:
  port: 8080

spring:
  application:
    name: multi-tools

  ai:
    # ============ 通义千问（走 OpenAI 兼容协议）============
    openai:
      base-url: https://dashscope.aliyuncs.com/compatible-mode
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-turbo
          temperature: 0.7

    # ============ 本地 Ollama ============
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: qwen2.5:7b       # 和你 ollama pull 的模型一致
          temperature: 0.7

    # ⭐ 关键：让 Spring AI 不要默认把 ChatClient 自动装配成其中某一个
    # （不同 Spring AI 版本写法略有差异，以官方文档为准）
```

### 3.4 写 ModelConfig 显式定义多个 ChatClient

新建 `config/ModelConfig.java`：

```java
package com.fletcher.multitools.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ModelConfig {

    /**
     * 通义千问 ChatClient（走 OpenAI 兼容协议）
     * 使用 name="qwenClient" 以便注入时区分
     */
    @Bean("qwenClient")
    public ChatClient qwenClient(OpenAiChatModel openAiChatModel) {
        return ChatClient.builder(openAiChatModel).build();
    }

    /**
     * Ollama 本地模型 ChatClient
     */
    @Bean("ollamaClient")
    public ChatClient ollamaClient(OllamaChatModel ollamaChatModel) {
        return ChatClient.builder(ollamaChatModel).build();
    }
}
```

### 3.5 在 ChatService 里注入两个 ChatClient

```java
@Service
public class ChatService {

    private final ChatClient qwenClient;
    private final ChatClient ollamaClient;
    private final TimeTool timeTool;
    private final OrderTool orderTool;

    public ChatService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            @Qualifier("ollamaClient") ChatClient ollamaClient,
            TimeTool timeTool,
            OrderTool orderTool) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
        this.timeTool = timeTool;
        this.orderTool = orderTool;
    }

    // 云端（便宜）
    public String chatCheap(String q) {
        return qwenClient.prompt().user(q).call().content();
    }

    // 本地（免费 + 私有）
    public String chatLocal(String q) {
        return ollamaClient.prompt().user(q).call().content();
    }

    // 云端 + 工具
    public String chatCheapWithTools(String q) {
        return qwenClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }

    // 本地 + 工具（注意：并非所有本地小模型都支持 Function Calling）
    public String chatLocalWithTools(String q) {
        return ollamaClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }
}
```

### 3.6 Controller 加接口

```java
@GetMapping("/chat/cheap")
public String cheap(@RequestParam String q) {
    return chatService.chatCheap(q);
}

@GetMapping("/chat/local")
public String local(@RequestParam String q) {
    return chatService.chatLocal(q);
}

@GetMapping("/chat/agent-cheap")
public String agentCheap(@RequestParam String q) {
    return chatService.chatCheapWithTools(q);
}

@GetMapping("/chat/agent-local")
public String agentLocal(@RequestParam String q) {
    return chatService.chatLocalWithTools(q);
}
```

---

## 四、启动测试

确保 Ollama 在 11434 端口跑着：
```bash
curl http://localhost:11434/api/tags
# 应该返回你装过的模型列表
```

再启动 Spring Boot 工程：
```bash
mvn spring-boot:run
```

### 测试 1：通义（云）

```bash
time curl "http://localhost:8080/chat/cheap?q=用一句话介绍 Spring AI"
```
**预期**：快速返回（1-2 秒），高质量中文。

### 测试 2：Ollama（本地）

```bash
time curl "http://localhost:8080/chat/local?q=用一句话介绍 Spring AI"
```
**预期**：稍慢（本地推理 3-10 秒，看你电脑），也能答。

### 测试 3：用本地模型调工具

```bash
curl "http://localhost:8080/chat/agent-local?q=现在几点？"
```

**可能的两种结果**：
- ✅ 成功：Ollama 的 qwen2.5:7b 支持 Function Calling，会调 TimeTool
- ⚠️ 失败：某些小模型 FC 能力弱，可能直接回答"我不知道"

**教训**：**Function Calling 对模型能力有要求**，不是所有 LLM 都支持。
- 支持良好：GPT-4o、Claude 3.5、Qwen-Max、Qwen2.5:7b+
- 有限支持：Qwen2.5:3b、Llama 3.2 小版本
- 不支持：老版本模型

---

## 五、（可选）加第 3 个模型：OpenAI

如果你有 OpenAI Key，**直接加一个**。但注意：通义已经用 openai-starter 的"占位"了，OpenAI 本身也要用 openai-starter，**同一个 starter 不能配置两套**。

### 解法：用 Spring 的条件化配置 / 或者自己构造 ChatModel

一种可行做法（**Spring AI 1.x 具体 API 以版本为准**）：

```java
@Configuration
public class ModelConfig {

    @Bean("openAiRealChatModel")
    public OpenAiChatModel openAiRealChatModel() {
        // 手动构造 OpenAI 真实的 ChatModel（不走自动配置）
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .baseUrl("https://api.openai.com")
                .defaultOptions(OpenAiChatOptions.builder()
                        .model("gpt-4o-mini")
                        .temperature(0.7)
                        .build())
                .build();
    }

    @Bean("openAiClient")
    public ChatClient openAiClient(@Qualifier("openAiRealChatModel") OpenAiChatModel model) {
        return ChatClient.builder(model).build();
    }
}
```

如果 API 不是这样（Spring AI 不同版本差异较大），**查[官方文档](https://docs.spring.io/spring-ai/reference/api/chat/openai-chat.html)**。

---

## 六、各模型的"性格"（生产经验）

| 模型 | 强项 | 短板 | 成本 |
|------|-----|-----|------|
| **OpenAI GPT-4o** | 综合最强、推理最好 | 贵 | $$$$ |
| **OpenAI GPT-4o-mini** | 性价比之王（2024-2026）| 英文为主 | $$ |
| **Claude 3.5 Sonnet** | 代码、长文本、严谨 | 贵，国内访问慢 | $$$$ |
| **通义千问 Max** | 中文强，价格低 | 英文不如 GPT | $$ |
| **通义千问 Turbo** | 特别快，特别便宜 | 质量一般 | $ |
| **Ollama 本地** | 免费、离线、私有 | 依赖你机器性能 | 免费 |

### 选型建议

| 场景 | 推荐 |
|------|------|
| 日常聊天 | qwen-turbo |
| 中文客服 | qwen-plus 或 qwen-max |
| 代码生成 | Claude 3.5 Sonnet 或 GPT-4o |
| 敏感数据 | Ollama 本地 |
| 内网服务 | Ollama |
| A/B 测试 | 多个模型都接，对比 |

---

## 七、常见坑

### ❌ 坑 1：Ollama 模型名写错

`application.yml` 里 `model: qwen2.5:7b` 必须和 `ollama list` 里完全一致，**包括冒号和标签**。

### ❌ 坑 2：本地 Ollama 没启动

```
Connection refused: localhost/127.0.0.1:11434
```
解法：`ollama serve` 跑起来，或者把 Ollama 应用图标点开（Mac 会默认后台启动）。

### ❌ 坑 3：本地模型太大跑不动

- 16GB 内存 Mac：最大跑 7B 模型
- 8GB 内存：只能跑 3B 以下
- 如果卡：降级到更小的模型 `qwen2.5:3b` 或 `qwen2.5:1.5b`

### ❌ 坑 4：Bean 冲突

```
required a single bean, but 2 were found
```
解法：所有注入 ChatClient 的地方都加 `@Qualifier("xxx")`。

---

## 八、本日实战清单

```
[ ] Ollama 已装并能 ollama run 对话
[ ] pom.xml 加了 ollama starter
[ ] application.yml 配置了 ollama 部分
[ ] ModelConfig 显式定义了 qwenClient + ollamaClient
[ ] ChatService 用 @Qualifier 注入两个 client
[ ] /chat/cheap 和 /chat/local 分别能通
[ ] 观察到两个模型的响应速度 / 质量差异
[ ] （可选）Ollama + TimeTool 工具调用也能通
```

---

## 🎯 今日收官清单

- [ ] 我能区分 ChatModel 和 ChatClient
- [ ] 我知道为什么多 starter 会 Bean 冲突，怎么解决
- [ ] 我理解 `@Qualifier` 在多模型场景下的必要性
- [ ] 我本地 Ollama 能跑、能调
- [ ] 我能说出至少 3 个模型的适用场景
- [ ] 我知道不是所有模型都支持 Function Calling

---

## 💡 一个常见的企业现实问题

真实项目会遇到：

> 业务方说："我们敏感数据不能上云，但想用 AI 问答。"

**你的答案**：

1. Embedding 模型：本地 bge-m3（Ollama 或 Docker）
2. LLM：本地 Qwen / Llama（Ollama）
3. 架构：全套 Spring Boot + Milvus 内网部署，零出网
4. 合规：数据不出 VPC，审计日志全量记录

**今天学完你已经具备这个能力雏形**。

---

## 🔖 下一步

明天 → [Day 4：多模型路由策略](./Day4-多模型路由.md)（按成本、按场景、智能选）
