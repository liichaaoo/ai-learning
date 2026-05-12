# Day 5 · 整合 Demo：智能运维助手

> ⏱️ 目标时间：2 小时（周末做）
> 🎯 产出：**一个能"干真活"的 AI 运维助手，让同事看了想要抄**

---

## 🧭 今天的主线

前 4 天的知识点拼起来：

```
✅ Function Calling（Day 1-2）
  +
✅ 多模型接入（Day 3）
  +
✅ 路由策略（Day 4）
  +
✅ Week 1 的流式输出、Prompt 工程
  =
🎯 一个能处理真实业务的 AI 应用
```

场景：**智能运维助手**。用户用自然语言问运维问题，AI 自动查监控、判断、执行操作。

---

## 一、场景设计

```
用户："线上 prod-api-01 服务最近有点卡，你看看咋回事"

AI 的内心戏（你能在日志里看到）：
  1. 调 getCpuUsage("prod-api-01") → CPU: 85%
  2. 调 getMemoryUsage("prod-api-01") → Memory: 92%
  3. 调 getRecentErrors("prod-api-01", 10) → 返回近 10 条错误日志
  4. 分析：内存快满了、错误日志显示 OOM
  5. 给用户：
     "prod-api-01 状态异常：
        - CPU 85% (偏高)
        - 内存 92% (严重)
        - 近 10 条错误显示 OOM
      建议：1) 立即重启服务；2) 增加 JVM 堆内存；3) 排查内存泄漏
      需要我帮你重启吗？"

用户："重启吧"

AI:
  6. 调 restartService("prod-api-01") → 成功
  7. 调 sendAlert("xxx", "已重启") → 成功
  8. 回复："已重启 prod-api-01，已通知运维群。请 5 分钟后观察。"
```

**这是一个 Agent 的雏形**。完全用你 Week 1-2 学的东西。

---

## 二、工具实现：SystemMonitorTool

新建 `tools/SystemMonitorTool.java`：

```java
package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 运维监控工具集
 * （真实项目会对接 Prometheus / ELK / 告警系统，这里用假数据演示）
 */
@Service
public class SystemMonitorTool {

    // 假的服务注册表
    private static final List<String> ALLOWED_SERVICES = List.of(
            "prod-api-01", "prod-api-02", "prod-api-03",
            "staging-api-01", "dev-api-01"
    );

    // 假的服务状态
    private final Map<String, ServiceState> stateMap = new ConcurrentHashMap<>();

    @Tool(description = """
            获取指定服务的 CPU 使用率。
            当用户询问服务性能、CPU、卡顿、慢等问题时调用。
            返回百分比字符串，例如 "45%"。
            """)
    public String getCpuUsage(
            @ToolParam(description = "服务名，例如 prod-api-01") String serviceName
    ) {
        if (!ALLOWED_SERVICES.contains(serviceName)) {
            return "错误：服务 " + serviceName + " 不在监控列表";
        }
        int cpu = ThreadLocalRandom.current().nextInt(20, 95);
        return cpu + "%";
    }

    @Tool(description = """
            获取指定服务的内存使用率。
            当用户询问内存、OOM、吃内存时调用。
            返回百分比，例如 "62%"。
            """)
    public String getMemoryUsage(
            @ToolParam(description = "服务名") String serviceName
    ) {
        if (!ALLOWED_SERVICES.contains(serviceName)) {
            return "错误：服务不在监控列表";
        }
        int mem = ThreadLocalRandom.current().nextInt(30, 95);
        return mem + "%";
    }

    @Tool(description = """
            获取指定服务最近的 N 条错误日志。
            当用户询问'报错'、'错误'、'异常'、'log'时调用。
            """)
    public List<String> getRecentErrors(
            @ToolParam(description = "服务名") String serviceName,
            @ToolParam(description = "返回最近几条，1-50") int count
    ) {
        if (!ALLOWED_SERVICES.contains(serviceName)) {
            return List.of("错误：服务不在监控列表");
        }
        if (count < 1 || count > 50) count = 10;

        // 假错误日志
        return List.of(
                "2026-05-12 22:31:05 ERROR OutOfMemoryError: Java heap space",
                "2026-05-12 22:31:08 ERROR Connection refused to db-master:3306",
                "2026-05-12 22:31:10 ERROR TimeoutException on GET /api/orders/12345"
        ).subList(0, Math.min(count, 3));
    }

    @Tool(description = """
            重启指定服务。
            ⚠️ 这是危险操作，会造成短暂服务不可用（约 30 秒）。
            只有在用户明确同意（比如说"重启吧"、"执行"、"确认"）后才调用。
            如果用户只是询问状态或请求建议，不要调用此工具。
            """)
    public String restartService(
            @ToolParam(description = "服务名") String serviceName
    ) {
        if (!ALLOWED_SERVICES.contains(serviceName)) {
            return "错误：服务 " + serviceName + " 不在允许操作的白名单";
        }

        // 真实场景调 K8s / Jenkins 等
        System.out.printf("⚠️ [模拟重启] %s ... 成功%n", serviceName);
        stateMap.put(serviceName, new ServiceState(true, System.currentTimeMillis()));
        return "服务 " + serviceName + " 已重启成功";
    }

    @Tool(description = """
            发送告警通知到运维群。
            当发现严重问题或执行重要操作后调用。
            """)
    public String sendAlert(
            @ToolParam(description = "告警级别：INFO, WARN, CRITICAL") String level,
            @ToolParam(description = "告警内容，不超过 200 字") String message
    ) {
        if (message == null || message.length() > 200) {
            return "错误：告警内容超长或为空";
        }
        if (!List.of("INFO", "WARN", "CRITICAL").contains(level)) {
            return "错误：级别必须是 INFO/WARN/CRITICAL";
        }
        System.out.printf("🔔 [%s 告警] %s%n", level, message);
        return "告警已发送（" + level + "）";
    }

    // 简单数据类
    private record ServiceState(boolean healthy, long lastRestartedAt) {}
}
```

---

## 三、Agent Service（集成一切）

新建 `service/OpsAgentService.java`：

```java
package com.fletcher.multitools.service;

import com.fletcher.multitools.tools.SystemMonitorTool;
import com.fletcher.multitools.tools.OrderTool;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

/**
 * AI 智能运维助手
 * Week 2 毕业项目核心服务
 */
@Service
public class OpsAgentService {

    private final ChatClient qwenClient;
    private final ChatClient ollamaClient;
    private final SystemMonitorTool monitorTool;

    private static final String SYSTEM_PROMPT = """
            你是一位资深运维工程师 AI 助手，名叫 OpsAgent。
            
            工作原则：
            1. 用户问服务状态时，主动调用监控工具查询真实数据，不要编造
            2. 发现严重问题（CPU > 80%、内存 > 85%、大量错误）时主动提示风险
            3. 执行危险操作（重启、发告警）前确认用户意图，不要擅自操作
            4. 所有数据查询完后，给出**简洁的分析结论**和**行动建议**（不要只是复述数据）
            5. 回答用 markdown 列表格式，方便用户快速扫读
            
            你可以使用的工具：
            - 查询 CPU / 内存 / 错误日志
            - 重启服务（需用户确认）
            - 发送告警（INFO/WARN/CRITICAL）
            """;

    public OpsAgentService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            @Qualifier("ollamaClient") ChatClient ollamaClient,
            SystemMonitorTool monitorTool) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
        this.monitorTool = monitorTool;
    }

    /**
     * 流式问答（带工具）
     */
    public Flux<String> ask(String question) {
        return qwenClient
                .prompt()
                .system(SYSTEM_PROMPT)
                .user(question)
                .tools(monitorTool)
                .stream()
                .content();
    }

    /**
     * 同步（方便 curl 测试）
     */
    public String askSync(String question) {
        return qwenClient
                .prompt()
                .system(SYSTEM_PROMPT)
                .user(question)
                .tools(monitorTool)
                .call()
                .content();
    }
}
```

---

## 四、Controller 开放接口

```java
@GetMapping("/ops")
public String ops(@RequestParam String q) {
    return opsAgentService.askSync(q);
}

@GetMapping(value = "/ops/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> opsStream(@RequestParam String q) {
    return opsAgentService.ask(q);
}
```

---

## 五、演示脚本（录制给同事看）

### 演示 1：单工具 - 查监控

```bash
curl "http://localhost:8080/ops?q=prod-api-01 的 CPU 现在多少"
```

**日志观察**：AI 调 `getCpuUsage("prod-api-01")` → 返回。

### 演示 2：多工具组合 - 主动分析

```bash
curl "http://localhost:8080/ops?q=prod-api-02 看起来卡，你看下啥情况"
```

**日志观察**：AI 可能会连续调 CPU、内存、错误日志 3 个工具，然后**给出综合分析**。

### 演示 3：判断 + 建议（不执行）

```bash
curl "http://localhost:8080/ops?q=prod-api-01 CPU 高不高？如果高就给个建议"
```

**关键观察**：AI **应该只查监控 + 给建议，不会主动调 restartService**（System Prompt 里明确了不能擅自操作）。

### 演示 4：明确指令 → 执行

```bash
curl "http://localhost:8080/ops?q=重启 prod-api-01"
```

**AI 应该**：
1. 识别用户明确要求重启
2. 调 restartService
3. 可能还会调 sendAlert（因为 System Prompt 鼓励重要操作后通知）
4. 给出执行结果

### 演示 5：访问不在白名单的服务

```bash
curl "http://localhost:8080/ops?q=重启 prod-db-01"
```

**AI 应该**：调 `restartService("prod-db-01")` → 返回错误 → AI 告诉用户"这个服务不在允许操作列表"。

### 演示 6：流式版（前端看蹦字）

浏览器里写个简单前端连 `/ops/stream` 用 EventSource（模仿 Week 1 Day 3 的 index.html），你能**一个字一个字看 AI 思考 + 给建议**。

---

## 六、前端演示页（整合 02-multi-tools 的 index.html）

用 Week 1 的前端升级版，加个 "🛠️ 运维助手" tab：

```html
<div id="panel-ops" style="display:none">
    <label>自然语言描述运维问题</label>
    <input id="ops-q" value="prod-api-01 现在状况怎么样？" />
    <button onclick="doOps()">问运维助手</button>
    <div class="output" id="ops-out"></div>
</div>

<script>
function doOps() {
    const q = document.getElementById('ops-q').value;
    const out = document.getElementById('ops-out');
    out.textContent = '';
    const src = new EventSource(`/ops/stream?q=${encodeURIComponent(q)}`);
    src.onmessage = e => out.textContent += e.data;
    src.onerror = () => src.close();
}
</script>
```

---

## 七、Week 2 收官：更新项目 README

打开 `项目/02-multi-tools/README.md`（新建），写一个**"简历级"** 的项目介绍：

```markdown
# Multi-Tools AI Assistant

一个基于 Spring AI 的**多工具 + 多模型** AI 助手，演示 Function Calling、多模型路由、智能降级等企业级能力。

## 🎯 核心能力

- 🛠️ **Function Calling**：AI 自主调用 Java 方法（查订单、发短信、重启服务）
- 🌐 **多模型接入**：同时支持通义千问（云）+ Ollama（本地）
- 🎯 **智能路由**：按复杂度 / 隐私级别 / 成本自动选择模型
- 🛡️ **降级容错**：主模型挂了自动切备用
- 🧑‍💻 **毕业项目**：AI 运维助手，能查监控、分析问题、执行动作

## 🚀 快速开始

```bash
# 1. 装 Ollama（本地模型）
brew install ollama
ollama pull qwen2.5:7b
ollama serve

# 2. 配置通义千问
export DASHSCOPE_API_KEY="sk-xxx"

# 3. 启动
mvn spring-boot:run

# 4. 访问
open http://localhost:8080
```

## 📡 API 精选

| 接口 | 演示能力 |
|------|---------|
| `/ops?q=...` | ⭐ 毕业项目：AI 运维助手 |
| `/chat/agent?q=...` | Function Calling 基础 |
| `/chat/auto?q=...` | 智能路由 |
| `/chat/safe?q=...` | 降级兜底 |

## 🏗️ 架构

见 src/main/java 各层 / 本仓库其他文档。

## 💰 亮点

- 多模型路由设计使推理成本下降约 40%
- 本地模型降级保证 99.9% 可用性
- 全量工具调用审计日志（满足合规）
```

---

## 八、Week 2 出关自测（重做一遍 README 里的 7 题）

1. Function Calling 工作原理（5 步流程）
2. `@Tool` 和 `@ToolParam` 分别干什么？
3. AI 传错参数怎么办？
4. ChatModel 和 ChatClient 的关系？
5. 多模型如何注入区分？
6. 按成本路由的核心思路？
7. 主模型挂了怎么降级？

**答对 5+ 题** = 毕业。

---

## 九、写 Week 2 学习小结（周报）

你的周报里加一段：

```markdown
## Week 2 学习小结

### 本周 4 个最大收获
1. 理解 Function Calling 的 5 步流程（再也不觉得 AI 是魔法）
2. 一个 Spring 工程接多个 LLM 的配置方法
3. Ollama 本地模型跑起来，离线可用
4. 多模型路由 + 降级的设计思路

### 最难的点
- （填你自己的）多模型 Bean 冲突的解决花了我 X 时间

### 最大的"啊哈时刻"
- 看到 AI 自己调 3 个工具、分析、给建议的那一刻，终于理解什么叫 Agent

### Demo 成果
- 运维助手能识别 6 种场景（查状态、建议、执行、告警...）
- 多模型路由平均响应时间 X 秒
- 本地降级成功率 100%

### 下周（Week 3）
- 学向量库 + Embedding（RAG 的基础）
- 装 Milvus
```

---

## 🎯 Week 2 完成检查清单

```
[ ] TimeTool / OrderTool / SystemMonitorTool 三个工具集都可用
[ ] 两个 ChatClient（qwen + ollama）都能调
[ ] ModelRouterService 能按规则路由
[ ] 降级能切 Ollama
[ ] 运维助手接口 /ops 能跑完整场景
[ ] 前端有能交互的演示页
[ ] 项目 README 写完
[ ] 周报里补了 Week 2 小结
```

---

## 🎉 完成 Week 2 后你拥有

```
✅ 完整的 Function Calling 工程能力
✅ 多模型架构思想 + 降级方案
✅ 一个能"讲故事"的 demo（运维助手）
✅ Agent 的基础直觉（阶段 4 会深入）
✅ 简历上第二个亮点项目
```

**从 Week 1 到 Week 2 的跃迁**：

```
Week 1 的你: "我能让 AI 聊天"
Week 2 的你: "我能让 AI 干活，而且干得便宜、安全、不翻车"
```

这是**面试官最想看到的工程能力**。

---

## 🚀 下一步

下周进入 [Week 3：向量库 + Embedding](../) ← RAG 真正开始的地方

Week 3 预告：
- 理解 Embedding 是什么（Week 3 Day 1 数学基础打过底了 ⭐）
- 搭建 Milvus 本地向量数据库
- Spring AI 的 VectorStore 和 DocumentReader
- 手搓第一个 RAG 检索流程

---

> 💌 **写给此刻的你**：
>
> 两周前你对 AI 应用开发只有模糊感觉。
> 现在你能手搓多工具 + 多模型 + 降级的 AI 助手。
>
> 这就是**按节奏学习 + 产出驱动**的力量。
>
> 阶段 3 走完 6 周时，你将拥有一个能面试拿 offer 的企业 RAG 项目。
