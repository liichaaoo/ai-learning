# Week 1 · Spring AI 基础（5 天）

> 📅 建议时间：阶段 3 第一周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：**亲手跑起来一个 Spring AI 程序**，并理解每一行在做什么

---

## 🎉 欢迎来到阶段 3（核心阶段）

如果你是提前来看这里（阶段 1-2 还没学完），恭喜你 —— **这才是你的主战场**。

阶段 1-2 的数学、Python、ML 是"弹药库"。
**阶段 3 开始，你会拿起 Java 这把老枪，打真正的战场。**

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **第一个 AI 程序** | 一个 Spring Boot 工程，跑起来就是 AI 聊天机器人 |
| **流式响应** | 像 ChatGPT 那样一个字一个字蹦出来 |
| **Prompt 工程初步** | 会写 System Prompt、用模板注入变量 |
| **结构化输出** | LLM 返回的自然语言自动变 Java 对象 |
| **展示能力** | 能 30 分钟内给同事演示 demo |

---

## ⚠️ 开工前必读：这不是"看完就会"

以下 3 件事你**必须手动完成**，光看教程是学不会的：

1. ✅ **装好 JDK 17+ 和 IntelliJ IDEA**（你已经会 Java，这步本来就该有）
2. ✅ **申请 API Key**（阿里通义千问，5 分钟，免费额度够用一年）
3. ✅ **跟着每个 Day 的代码**，**自己在 IntelliJ 里敲一遍**

**如果你只是"读"教程不写代码，本周学不到东西。**

---

## 📅 5 天计划

| Day | 主题 | 产出 | 时长 |
|-----|------|------|------|
| **Day 1** | [环境准备 + 申请 API Key](./Day1-环境准备.md) | 环境 OK，API Key 在手 | 1-1.5h |
| **Day 2** | [Hello World](./Day2-HelloWorld.md) | 第一个 Spring AI 程序跑起来 | 1.5h |
| **Day 3** | [流式响应（像 ChatGPT）](./Day3-流式响应.md) | `/chat/stream` 接口，SSE 实时返回 | 1.5h |
| **Day 4** | [Prompt 模板 + System Prompt](./Day4-Prompt工程.md) | 能动态注入上下文 | 1.5h |
| **Day 5** | [结构化输出 + 整合 Demo](./Day5-结构化输出与整合.md) | 跑通完整 demo + 能给别人演示 | 2h |

---

## 📦 本周的最终产出

**一个完整的 Spring Boot 工程**：`项目/01-helloai/`

```
01-helloai/
├── pom.xml                  ← Maven 依赖
├── README.md                ← 项目说明
├── src/main/
│   ├── java/.../
│   │   ├── HelloAiApplication.java   ← 启动类
│   │   ├── controller/
│   │   │   └── ChatController.java   ← 所有 HTTP 接口
│   │   ├── service/
│   │   │   └── ChatService.java      ← 核心聊天逻辑
│   │   └── dto/
│   │       └── Recipe.java           ← 结构化输出示例
│   └── resources/
│       └── application.yml           ← 配置（API Key 等）
```

跑起来后能做的事：
- `GET /chat?q=你好` → 一次性返回答复
- `GET /chat/stream?q=帮我写一首诗` → **流式返回**，像 ChatGPT 一样
- `POST /chat/recipe` → 输入一道菜，返回**结构化 Java 对象**（食材列表 + 步骤）

---

## 💡 为什么选 Spring AI 而不是 LangChain4j？

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| **归属** | Spring 官方 | 社区项目 |
| **生态** | 和 Spring Boot 无缝集成 ⭐ | 独立库 |
| **企业用户** | 腾讯内部已大量采用 | 国内偏少 |
| **上手难度** | 你会 Spring = 半天上手 | 需要学一些新概念 |
| **生产就绪** | 2024 GA，生产级 | 也 OK |

**结论**：对你（腾讯 Java 老兵）而言，**Spring AI 性价比最高**。学完 Spring AI 再看 LangChain4j，会很轻松。

---

## 🧭 每日节奏建议

```
周一 Day 1   晚上 1h   装环境 + 申请 Key
周二 Day 2   晚上 1.5h  Hello World 跑起来
周三 Day 3   晚上 1.5h  流式响应
周四 Day 4   晚上 1.5h  Prompt 工程
周五          休息/反思
周六 Day 5   上午 2h    整合 demo + 写 README
周日          写周报
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [环境准备 + API Key](./Day1-环境准备.md)
- [ ] Day 2 · [Hello World](./Day2-HelloWorld.md)
- [ ] Day 3 · [流式响应](./Day3-流式响应.md)
- [ ] Day 4 · [Prompt 工程](./Day4-Prompt工程.md)
- [ ] Day 5 · [结构化输出与整合](./Day5-结构化输出与整合.md)

---

## 🎯 本周出关自测（5 题）

1. Spring AI 的核心对象 `ChatClient` 和 `ChatModel` 有什么区别？
2. 调用同步接口和流式接口，返回类型分别是什么？
3. System Prompt 和 User Prompt 的作用有什么不同？
4. Prompt 模板里用什么语法注入变量？
5. 结构化输出 `.entity(Recipe.class)` 的原理是什么？（Spring AI 怎么让 LLM 返回 JSON 再映射成对象？）

**答对 4+ 题** = 本周通过。

---

## 🚦 一个重要提醒

本周你会**很强烈地想深入下去**（比如"我想自己实现 RetryAdvisor""我想研究 SSE 的 Reactor 底层"）。

**忍住**。

本周的唯一任务是**跑起来**。深入等 Week 2/3/4。

> 💡 **心法**：**Done is better than perfect**。
> 一个能跑的丑陋 demo，胜过一本看完但没落地的 Spring AI 手册。

---

## 🔗 相关资源

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)（收藏！每天会查）
- [笔记/SpringAI入门.md](../笔记/SpringAI入门.md)（本周的"总纲"）
- [阶段 3 总 README](../README.md)

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1：环境准备 + API Key 申请](./Day1-环境准备.md)**
