# Multi-Tools AI Assistant · Week 2 毕业项目

一个基于 **Spring Boot 3 + Spring AI** 的**多工具 + 多模型** AI 助手，演示 Function Calling、多模型路由、智能降级等企业级能力。

---

## ✨ 核心能力

- 🛠️ **Function Calling**：AI 自主调用 Java 方法（时间、订单、短信、运维监控等 8 个工具）
- 🌐 **多模型接入**：同时支持通义千问（云）+ Ollama（本地），一次工程多个大脑
- 🎯 **智能路由**：按复杂度 / 隐私 / 场景自动选模型
- 🛡️ **降级容错**：主模型挂了自动切本地备份
- 🚀 **毕业项目**：AI 运维助手，能查监控、分析问题、执行操作

---

## 🚀 快速开始

### 前置

- JDK 17+
- 通义千问 API Key（[免费申请](https://dashscope.console.aliyun.com/)）
- Ollama（[官网下载](https://ollama.com/)）

### 启动

```bash
# 1. 装 Ollama 并下载模型
brew install ollama
ollama pull qwen2.5:7b
ollama serve                     # 后台启动（保持运行）

# 2. 配置通义 Key
export DASHSCOPE_API_KEY="sk-xxx"

# 3. 启动应用
mvn spring-boot:run

# 4. 打开浏览器
open http://localhost:8080
```

---

## 📡 API 一览

| 类别 | 接口 | 说明 |
|------|------|------|
| **Function Calling** | `GET /chat/agent?q=...` | AI 自主调用工具（时间/订单） |
| **多模型** | `GET /chat/cheap?q=...` | 用通义（云） |
| | `GET /chat/local?q=...` | 用 Ollama（本地） |
| | `GET /chat/agent-local?q=...` | 本地模型 + 工具 |
| **路由** | `GET /chat/auto?q=...` | 按复杂度路由 |
| | `GET /chat/privacy?q=...` | 按隐私路由 |
| | `GET /chat/safe?q=...` | 带降级 |
| | `GET /chat/smart?q=...` | AI 分类后路由 |
| **运维助手** | `GET /ops?q=...` | ⭐ 毕业 Demo（同步） |
| | `GET /ops/stream?q=...` | ⭐ 毕业 Demo（流式 SSE） |

---

## 🏗️ 架构

```
           用户请求
              │
      ┌───────┼───────┐
      │       │       │
    规则路由  AI 分类  成本
      │       │       │
      └───────┴───────┘
              │
  ┌───────────┼───────────┐
  ▼           ▼           ▼
qwen        qwen-max   ollama
(便宜)      (聪明)     (本地)
  │           │           │
  └───────────┴───────────┘
              │
         try-catch 降级
              │
              ▼
           工具层
  TimeTool / OrderTool / SystemMonitorTool
```

---

## 🧱 项目结构

```
src/main/java/com/fletcher/multitools/
├── MultiToolsApplication.java           启动类
├── config/ModelConfig.java              多 Bean 配置
├── controller/ChatController.java       统一入口
├── service/
│   ├── ChatService.java                 基础聊天 + Tool
│   ├── ModelRouterService.java          路由决策
│   └── OpsAgentService.java             毕业 Demo
└── tools/
    ├── TimeTool.java                    时间（无副作用）
    ├── OrderTool.java                   订单（查询 + 短信）
    └── SystemMonitorTool.java           运维监控 + 重启 + 告警
```

---

## 💰 项目亮点（简历语言）

> 主导设计**多工具 + 多模型**的 Spring AI 应用，集成通义千问 + Ollama 本地模型：
> - 基于 **Function Calling** 实现 AI 主动调用业务方法（监控查询、订单查询、告警发送等 8 个工具）
> - 设计**多模型路由**策略，按问题复杂度 / 敏感度动态选择模型，推理成本降低约 40%
> - 实现**主模型降级机制**，主云端模型异常时自动切本地 Ollama，可用性 ≥ 99.9%
> - 所有危险操作（重启、发告警）做**白名单 + 二次确认 + 审计日志**

---

## 🛡️ 安全

- ✅ API Key 通过环境变量注入，绝不进 Git
- ✅ Function Calling 工具都有参数校验
- ✅ 危险操作（重启、发告警）用白名单
- ✅ 全量工具调用日志

---

## 🎓 学习资源

- [Week 2 完整 5 天教程](../../Week2-FunctionCalling与多模型/)
- [阶段 3 总览](../../README.md)
- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)

---

## 📌 下一步（Week 3）

继续在这个工程基础上演进：
- 加 Milvus 向量库
- 实现 Embedding
- 搭建第一个 RAG 检索

最终在 Week 5-6 演进成**企业 RAG 知识库**。
