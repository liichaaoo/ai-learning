# Day 2 · Spring AI Hello World

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**一个能跑的 Spring Boot 工程，访问 `/chat?q=你好` 能得到 AI 回复**

---

## 🧭 今天你要做什么

```
1. 用 IntelliJ 创建一个 Spring Boot 3 工程
2. 加 Spring AI + OpenAI 的依赖（用它调通义千问）
3. 写一个 ChatController，暴露 /chat 接口
4. 启动！访问 http://localhost:8080/chat?q=你好 看到 AI 回复
```

---

## 一、创建 Spring Boot 工程

### 方式 A：用 IntelliJ 新建

1. **File → New → Project**
2. 左侧选 **Spring Boot**（或 Spring Initializr）
3. 填写：
   - Language: **Java**
   - Build: **Maven**
   - JDK: **17 或 21**
   - Group: `com.fletcher`（或你喜欢的）
   - Artifact: `helloai`
   - Spring Boot: **3.2.x** 或 **3.3.x**
4. **Dependencies 选**：
   - **Spring Web**（做 REST 接口）
   - **Spring Boot DevTools**（自动重启，方便开发）

点 **Create**，等待下载依赖。

### 方式 B：用命令行（一样的）

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,devtools \
  -d bootVersion=3.3.5 \
  -d type=maven-project \
  -d language=java \
  -d javaVersion=17 \
  -d groupId=com.fletcher \
  -d artifactId=helloai \
  -o helloai.zip
unzip helloai.zip -d helloai
cd helloai
```

---

## 二、加 Spring AI 依赖

打开 `pom.xml`，**在 `<dependencies>` 里新增**：

```xml
<!-- Spring AI OpenAI Starter (也支持通义千问，因为通义兼容 OpenAI 协议) -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

**然后在 `<dependencyManagement>` 里加**（如果没有这个标签就新建）：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>1.0.0</version>    <!-- 或查最新版 -->
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

> ⚠️ **版本注意**：Spring AI 1.0.0 是 2025 年 5 月发布的正式版。如果写教程时版本已经更新，去 [Maven Central](https://central.sonatype.com/artifact/org.springframework.ai/spring-ai-bom) 查最新。

### 添加 Spring Milestones 仓库（如果 Maven 找不到包）

如果你用的是 Spring AI 的 M 版（里程碑版本），需要在 `pom.xml` 加：

```xml
<repositories>
    <repository>
        <id>spring-milestones</id>
        <name>Spring Milestones</name>
        <url>https://repo.spring.io/milestone</url>
        <snapshots><enabled>false</enabled></snapshots>
    </repository>
</repositories>
```

**1.0 正式版后通常就在 Maven Central，不需要这个**。

### 刷新 Maven

点 IntelliJ 右上角的 Maven 刷新按钮（或 `Cmd+Shift+I` reload project）。

---

## 三、配置文件 `application.yml`

在 `src/main/resources/` 里**删除原来的 `application.properties`**，**新建 `application.yml`**：

```yaml
server:
  port: 8080

spring:
  application:
    name: helloai

  # Spring AI 的 OpenAI 配置（我们用它来调通义千问）
  ai:
    openai:
      # ⭐ 通义千问的 Base URL（兼容 OpenAI 协议）
      base-url: https://dashscope.aliyuncs.com/compatible-mode

      # ⭐ 从环境变量读取 API Key，避免硬编码
      api-key: ${DASHSCOPE_API_KEY}

      chat:
        options:
          model: qwen-turbo        # 通义千问模型（快+便宜）
          temperature: 0.7
```

### 📌 关键点解读

| 配置 | 作用 |
|------|------|
| `base-url` | Spring AI 默认连 `https://api.openai.com`，我们改成通义千问的地址 |
| `api-key: ${DASHSCOPE_API_KEY}` | `${}` 是 Spring 读环境变量的语法 |
| `model: qwen-turbo` | 通义的快速模型（也可以用 `qwen-plus`、`qwen-max`） |

> 💡 **注意**：Spring AI 自动把 `/compatible-mode` 后面拼上 `/v1/chat/completions`，所以这里 base-url **不要**写全 `/v1`。

---

## 四、写一个 ChatController

在 `src/main/java/com/fletcher/helloai/` 下新建 `controller/ChatController.java`：

```java
package com.fletcher.helloai.controller;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ChatController {

    private final ChatClient chatClient;

    // Spring 自动注入 ChatClient.Builder，我们 build 出一个 ChatClient
    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    /**
     * 同步调用 LLM
     * 访问：http://localhost:8080/chat?q=你好
     */
    @GetMapping("/chat")
    public String chat(@RequestParam("q") String question) {
        return chatClient
                .prompt()                    // 开始构造 prompt
                .user(question)              // 设置用户输入
                .call()                      // 同步调用
                .content();                  // 取出文本结果
    }
}
```

### 📌 流式 API 讲解

Spring AI 的 `ChatClient` 用的是 **Fluent API（链式调用）**，读起来很像自然语言：

```java
chatClient
    .prompt()          // "开始造一个 prompt"
    .user("你好")       // "用户说：你好"
    .call()            // "发出去！同步等结果"
    .content();        // "拿到文本内容"
```

**Java 程序员看会很亲切**，像 Spring Data 的 Criteria、像 Mockito。

---

## 五、启动！

### 5.1 确认环境变量已生效

```bash
echo $DASHSCOPE_API_KEY
# 应该输出 sk-xxx...
```

### 5.2 IntelliJ 里启动

找到 `HelloaiApplication.java`（带 `@SpringBootApplication` 的类），点左边的绿色小三角 → Run。

### 5.3 看启动日志

应该看到：
```
Started HelloaiApplication in 3.xxx seconds
Tomcat started on port 8080 (http)
```

### 5.4 测试！

浏览器访问：
```
http://localhost:8080/chat?q=你好
```

或者 curl：
```bash
curl "http://localhost:8080/chat?q=用三个成语形容今天的天气"
```

**看到 AI 返回 = 你完成了今天的任务 ✅**

---

## 六、常见问题排查

### ❌ 启动时报 `Cannot resolve symbol 'ChatClient'`
- Maven 依赖没下载成功
- 右键 `pom.xml` → Maven → Reload Project

### ❌ 启动报 `Connection refused` 或 `401 Unauthorized`
- API Key 没设置对
- IntelliJ 启动时**没读到环境变量**（需要在 Run Configuration 里手动加）

**IntelliJ 加环境变量**：
1. Run → Edit Configurations
2. 找你的 Spring Boot 启动配置
3. Environment variables → 加 `DASHSCOPE_API_KEY=sk-xxx`

### ❌ 报 `model not found`
- `model: qwen-turbo` 写错了，去[这里](https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-api)查最新支持的模型名

### ❌ 报 `insufficient_quota`
- 免费额度用完（一般新用户不会）
- 或 Key 的权限不对

---

## 七、理解一下"刚发生了什么"

当你点访问 `/chat?q=你好`：

```
浏览器
  │ GET /chat?q=你好
  ▼
Spring Boot (Tomcat)
  │ 路由到 ChatController
  ▼
ChatController.chat()
  │ 调用 chatClient.prompt().user("你好").call()
  ▼
Spring AI 框架
  │ 转换成 OpenAI API 格式的 HTTP POST 请求
  │ POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
  │ Body: { "model": "qwen-turbo", "messages": [...] }
  ▼
通义千问服务器
  │ 推理...
  ▼
返回 JSON
  │ { "choices": [{"message": {"content": "你好！..."}}] }
  ▼
Spring AI 解析出 .content()
  │
  ▼
返回给浏览器
```

**你看到的"一句 Java 调用"底下，其实是一次完整的 HTTP RPC**。和 Day 1 你 curl 的请求是**一模一样的底层行为**。

---

## 八、"看懂了" vs "跑通了"的区别

| 看懂了 | 跑通了 |
|--------|--------|
| 我知道 `chatClient.prompt().user(q).call().content()` 在干什么 | 我电脑上现在就有个 Spring Boot 在 8080 端口跑着 |

**今天的任务是后者**。如果只看懂没跑通，明天会非常挫败（后面的内容都基于今天的 demo）。

---

## ✍️ 本日实战清单

```
[ ] 工程创建成功
[ ] pom.xml 加了 Spring AI 依赖
[ ] application.yml 配置对了 base-url 和 api-key
[ ] ChatController.java 写好了
[ ] 启动成功（看到 "Started HelloaiApplication"）
[ ] 访问 /chat?q=xxx 能看到 AI 回复
[ ] （加分）提交到 Git（但记得 .gitignore 保护 Key）
```

---

## 🎯 今日收官清单

- [ ] 我有一个跑着的 Spring AI Hello World 工程
- [ ] 我知道 `ChatClient.Builder` 怎么用
- [ ] 我理解 `.prompt().user().call().content()` 每一步在做什么
- [ ] 我知道 Spring AI 底层其实是发 HTTP 请求
- [ ] 我的 Key 不在代码里、在环境变量里

---

## 💡 进阶小彩蛋（选做）

改一下 `application.yml` 的 `temperature`：

```yaml
temperature: 0.1     # 试试改成 0.1（保守）
temperature: 1.5     # 再改成 1.5（发散）
```

问同一个问题"用 3 句话描述海边"，观察回答的变化。

**这就是 Week 3 Day 3 学过的 temperature**，今天亲手体验到了。

---

## 🔖 下一步

明天 → [Day 3：流式响应](./Day3-流式响应.md)（像 ChatGPT 那样一个字一个字蹦）
