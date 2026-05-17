# Week 1 · LangChain4j + Agent 基础（5 天）

> 📅 建议时间：阶段 4 第一周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：从 Spring AI 平滑切到 LangChain4j，掌握 Memory + Tools，搞出第一个能"自主决策"的 Agent

---

## 🎉 你即将跨过的"关键分水岭"

阶段 3 Spring AI 你做的程序是"被动应答"：

```
用户问 → 检索 → 生成 → 返回。  程序"乖"，不主动想事情。
```

**Week 1 结束后你的程序能**：

```
用户："今天上海几度？合不合适去黄浦江散步？"

Agent:
  1. 思考：要先调 weatherTool 拿温度
  2. 调用 → 得到 24°C，多云
  3. 再思考：24°C 多云，对散步很友好
  4. 整合回答："上海 24°C 多云，非常适合散步"

整个过程模型自己规划、自己调工具、自己整合。
```

> 💡 **Spring AI 是"Web 框架"思维，LangChain4j 是"Agent 框架"思维**——两个工具适合不同场景，今后你两个都要会。

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **LangChain4j 心智模型** | `ChatLanguageModel` / `AiServices` / `Memory` / `Tools` 四件套 |
| **AiServices 声明式 API** | 用接口定义 Agent，Java 老兵最熟悉的 Feign 风格 |
| **三种 Memory** | MessageWindow / TokenWindow / Summarizing，按场景选 |
| **Tools 进阶** | 参数校验、错误处理、Tool 选错的兜底 |
| **多模型注入** | 同一工程接通义 / GPT / Ollama / DeepSeek |

---

## ⚠️ 开工前必读

### 1. Spring AI vs LangChain4j：什么时候用哪个

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| 风格 | 命令式（你写流程）| **声明式（接口 + 注解）** ⭐ |
| Advisor 链 | ⭐⭐⭐ 强 | 有但弱 |
| AiServices | 没有 | **⭐⭐⭐ 杀手锏** |
| Agent 编排 | 偏简单 | **⭐⭐⭐ 内置 ReAct/Plan** |
| Spring Boot 集成 | **⭐⭐⭐ 原生** | ⭐⭐ 也有 starter |
| 社区中文资料 | 较新 | 更丰富（早 1 年） |

> 🎯 **混用策略**：阶段 3 项目继续用 Spring AI；本阶段的 Agent 项目用 LangChain4j——**面试时能讲"为什么我两个都会"** 是加分项。

### 2. 不要从零换框架

把 Week 2 Function Calling 工程基础上加 LangChain4j 依赖，**两套并存** 就行。

---

## 📅 5 天计划

| Day | 主题 | 产出 | 时长 |
|-----|------|------|------|
| **Day 1** | [LangChain4j Hello World](./Day1-LangChain4j-HelloWorld.md) | 第一个 AiService 跑起来 | 1.5h |
| **Day 2** | [AiServices 声明式 API](./Day2-AiServices声明式.md) ⭐ | 用接口 + 注解定义 Agent | 1.5h |
| **Day 3** | [三种 Memory 机制](./Day3-Memory机制.md) | Window / Token / Summary 三种都跑过 | 1.5h |
| **Day 4** | [Tools 进阶](./Day4-Tools进阶.md) | 参数校验 + 异常 + 工具选错的兜底 | 1.5h |
| **Day 5** | [整合 Demo：你的第一个 Agent](./Day5-第一个Agent.md) ⭐ | `项目/06-langchain4j-hello/` 上线 | 2h |

---

## 📦 本周最终产出

`项目/06-langchain4j-hello/`

```
06-langchain4j-hello/
├── pom.xml
├── README.md
└── src/main/
    ├── java/com/demo/lc4j/
    │   ├── Lc4jApplication.java
    │   ├── service/
    │   │   ├── AssistantService.java         ← AiService 接口
    │   │   └── ModelRouter.java              ← 多模型路由
    │   ├── tools/
    │   │   ├── WeatherTool.java
    │   │   ├── CalculatorTool.java
    │   │   └── DateTimeTool.java
    │   ├── memory/RedisMemoryStore.java
    │   └── config/Lc4jConfig.java
    └── resources/application.yml
```

跑起来能做：

- 多轮对话 + 自动调用工具
- 切换 Memory 类型
- 切换底层模型（通义 / Ollama）
- 看到工具调用日志

---

## 🧭 推荐节奏

```
周一 Day 1   1.5h    Hello World，跑通第一行 LangChain4j
周二 Day 2   1.5h    AiServices 声明式 API（爽点最高）
周三 Day 3   1.5h    三种 Memory 实测
周四 Day 4   1.5h    Tools 异常 + 校验 + 选错兜底
周五         休息
周六 Day 5   2h      整合 Demo + 录视频
周日         写笔记《LangChain4j入门.md》
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [LangChain4j Hello World](./Day1-LangChain4j-HelloWorld.md)
- [ ] Day 2 · [AiServices 声明式](./Day2-AiServices声明式.md)
- [ ] Day 3 · [Memory 机制](./Day3-Memory机制.md)
- [ ] Day 4 · [Tools 进阶](./Day4-Tools进阶.md)
- [ ] Day 5 · [第一个 Agent](./Day5-第一个Agent.md)

---

## 🎯 本周出关自测（7 题）

1. `ChatLanguageModel` 和 `AiServices` 的关系？
2. 一个 `@AiService` 接口里的方法被调用时，背后发生了什么？
3. `MessageWindowChatMemory` 和 `TokenWindowChatMemory` 各自适合什么场景？
4. `SummarizingChatMemory` 解决了什么问题？代价是？
5. LangChain4j 里 `@Tool` 和 Spring AI 的 `@Tool` 有什么区别？
6. 工具被 LLM 选错怎么办？三种兜底策略说出来。
7. 同一个工程接两个不同厂商的 LLM，LangChain4j 怎么写？

**答对 5+ 题** = 本周通过。

---

## 🚦 重要提醒

### 1. 不要"忘掉 Spring AI"

LangChain4j 适合 Agent，Spring AI 适合"集成在 Spring 生态里的 LLM 应用"。**两个共存，按场景挑**。

### 2. AiServices 是杀手锏

```java
@SystemMessage("你是 ...")
String chat(@UserMessage String msg);
```

这一行抵 Spring AI 三段——**今后 Agent 代码 90% 都是这种风格**。

### 3. Ollama 提前装

Week 1 Day 4-5 会用到本地 Ollama。

```bash
# Mac
brew install ollama
ollama serve &
ollama pull qwen2.5:0.5b   # 仅 ~400MB
```

---

## 🔗 相关资源

- [LangChain4j 官方文档](https://docs.langchain4j.dev/)
- [LangChain4j Spring Boot Starter](https://docs.langchain4j.dev/tutorials/spring-boot-integration)
- [LangChain4j Examples](https://github.com/langchain4j/langchain4j-examples)
- [笔记/LangChain4j入门.md](../笔记/LangChain4j入门.md)（本周末写）

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1 · LangChain4j Hello World](./Day1-LangChain4j-HelloWorld.md)**
