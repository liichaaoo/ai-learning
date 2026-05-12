# Week 2 · Function Calling + 多模型（5 天）

> 📅 建议时间：阶段 3 第二周
> ⏱️ 每天约 1.5-2 小时
> 🎯 **核心目标**：让 AI 能**自主调用**你的业务方法 + 一个工程同时接入多个 LLM

---

## 🎉 你即将跨过的"关键分水岭"

Week 1 你做的 AI 只能"聊天"：用户说 → AI 回复。

**Week 2 结束后，你的 AI 能**：

```
用户: "帮我查一下订单 12345 的状态，如果是待发货就发个短信提醒仓库"

AI:
  1. 判断：需要"查订单"工具 → 调用 orderService.getStatus(12345)
  2. 收到返回："待发货"
  3. 判断：需要"发短信"工具 → 调用 smsService.send("仓库", "...")
  4. 整合结果告诉用户："订单 12345 待发货，已给仓库发短信提醒"
```

**这就是 Agent 的雏形**。Week 2 是阶段 4（Agent 专题）的预习。

---

## 🎯 本周你会获得

| 能力 | 说明 |
|------|------|
| **Function Calling** | 用 `@Tool` 把现有 Spring Service 暴露给 LLM |
| **参数校验** | AI 出错时的防护（参数类型、范围） |
| **多模型同时接入** | 一个工程接 OpenAI + 通义 + Claude + 本地 Ollama |
| **路由策略** | 按成本、按场景选择最合适的模型 |
| **降级与兜底** | 主模型不可用自动切备用 |

---

## ⚠️ 先说清楚：Function Calling 能不能做什么

### ✅ 能干的（本周要做的）

- 让 AI 自动调用"查天气/查订单/查库存"等查询类工具
- 让 AI 组合多个工具完成任务（先查再做）
- 让 AI 基于返回值决定下一步
- 让 AI 以 JSON 格式接收参数、返回结构化结果

### ❌ 不能干的（要有正确预期）

- AI **不能**"执行任意代码"（只能调你提前用 `@Tool` 注册过的方法）
- AI **不是** 100% 可靠（有时会选错工具、传错参数 → 所以需要参数校验）
- AI **不能自主决策复杂流程**（这是阶段 4 Agent 要深入的）

---

## 📅 5 天计划

| Day | 主题 | 产出 |
|-----|------|------|
| **Day 1** | [Function Calling 原理 + Hello Tool](./Day1-FunctionCalling原理.md) | AI 能调 `getCurrentTime()` |
| **Day 2** | [多工具协作 + 参数校验](./Day2-多工具协作.md) | AI 能组合 3 个工具完成任务 |
| **Day 3** | [多模型接入](./Day3-多模型接入.md) | 同一工程接 OpenAI/通义/Ollama |
| **Day 4** | [多模型路由策略](./Day4-多模型路由.md) | 按场景自动选模型 + 降级 |
| **Day 5** | [整合 Demo：智能运维助手](./Day5-整合Demo.md) | 一个能查 CPU、重启服务、发告警的 AI |

---

## 📦 本周的最终产出

**一个升级版工程**：`项目/02-multi-tools/`

```
02-multi-tools/
├── pom.xml
├── README.md
└── src/main/
    ├── java/.../
    │   ├── MultiToolsApplication.java
    │   ├── controller/ChatController.java
    │   ├── service/
    │   │   ├── ChatService.java
    │   │   └── ModelRouterService.java      ⭐ 多模型路由
    │   ├── tools/
    │   │   ├── TimeTool.java                ⭐ 第一个 Tool
    │   │   ├── OrderTool.java               订单工具
    │   │   └── SystemMonitorTool.java       运维工具
    │   └── config/
    │       └── ModelConfig.java             多模型配置
    └── resources/
        └── application.yml                  多模型 Key 配置
```

演示能力：
- `POST /chat/agent?q=现在几点？` → AI 自动调 `TimeTool`
- `POST /chat/agent?q=查订单12345` → AI 自动调 `OrderTool`
- `POST /chat/agent?q=服务 xxx CPU 高不高？不行就重启` → AI 调 `SystemMonitorTool`，根据返回决定是否调 `restart`
- `POST /chat/cheap` → 用通义（便宜）
- `POST /chat/smart` → 用 GPT-4（聪明）
- `POST /chat/auto` → AI 路由器自己挑

---

## 🎯 本周出关自测（7 题）

1. Function Calling 的工作原理？（一句话描述 AI 是怎么"知道"要调哪个方法的）
2. `@Tool` 和 `@ToolParam` 注解分别干什么？
3. 如果 AI 传的参数类型不对，Spring AI 会怎么处理？
4. `ChatModel` 和 `ChatClient` 有什么关系？
5. 一个 Spring 工程接 2 个不同厂商的 LLM，注入时怎么区分？
6. 路由策略设计，按成本路由的核心思路？
7. 主模型挂了怎么降级？

**答对 5+ 题** = 本周通过。

---

## 🧭 推荐节奏

```
周一 Day 1   1.5h   @Tool 第一次让 AI 调方法
周二 Day 2   1.5h   多工具协作（有惊喜感）
周三 Day 3   1.5h   装 Ollama + 第 3 方模型接入
周四 Day 4   1.5h   路由策略 + 降级
周五         休息
周六 Day 5   2h     做完运维助手 demo
周日         写周报
```

---

## ✅ 本周进度追踪

- [ ] Day 1 · [Function Calling 原理](./Day1-FunctionCalling原理.md)
- [ ] Day 2 · [多工具协作](./Day2-多工具协作.md)
- [ ] Day 3 · [多模型接入](./Day3-多模型接入.md)
- [ ] Day 4 · [多模型路由](./Day4-多模型路由.md)
- [ ] Day 5 · [整合 Demo](./Day5-整合Demo.md)

---

## 🚦 重要提醒

### 1. Function Calling 是本周的灵魂

如果你只学一个东西，学这个。面试常问、工作常用、简历必写。

### 2. 多模型不用贪多

Day 3 最少接入 **通义 + Ollama** 两个即可。
OpenAI / Claude 要国际信用卡，不强求。

### 3. Ollama 建议现在就下载

Day 3 会用到。有 10GB 空间就能跑，[Ollama 官网](https://ollama.com/)一行命令装。

---

## 🚀 下一步

✅ 读完本文
⬇️
🟦 **开始 [Day 1：Function Calling 原理](./Day1-FunctionCalling原理.md)**
