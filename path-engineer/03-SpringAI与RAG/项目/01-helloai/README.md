# Hello Spring AI

> 一个基于 **Spring Boot 3 + Spring AI + 通义千问** 的最小 AI 应用示例。
> 这是 `path-engineer/03-SpringAI与RAG/Week1` 的**毕业项目**，作为后续 Week 2-6 的基础工程。

---

## ✨ 特性

- 💬 **流式对话**（SSE，像 ChatGPT 一样一字一蹦）
- 🎓 **专家模式**（System Prompt 设定角色）
- 🛍️ **行业客服**（Prompt 模板 + 变量注入）
- 🍳 **结构化输出**（LLM 返回值直接映射为 Java 对象）
- 🎨 简洁的 HTML 演示页

---

## 🚀 快速开始

### 1. 环境

- JDK 17+（推荐 JDK 21）
- Maven 3.8+
- 通义千问 API Key（[免费申请](https://dashscope.console.aliyun.com/)）

### 2. 配置 API Key

```bash
export DASHSCOPE_API_KEY="sk-你的真实key"
```

（推荐写进 `~/.zshrc` 或 `~/.bashrc` 永久生效）

### 3. 启动

```bash
mvn spring-boot:run
```

等看到 `Started HelloaiApplication in X seconds`。

### 4. 测试

**浏览器**：`http://localhost:8080`

**或 curl**：
```bash
# 同步
curl "http://localhost:8080/chat?q=你好"

# 流式（一定要 -N）
curl -N "http://localhost:8080/chat/stream?q=写一首诗"

# 专家模式
curl "http://localhost:8080/chat/expert?q=MySQL还是PostgreSQL"

# 行业客服
curl "http://localhost:8080/chat/industry?industry=电子产品&q=保修多久"

# 结构化输出
curl -X POST "http://localhost:8080/chat/recipe?dish=蛋炒饭"
```

---

## 📡 API 一览

| 接口 | 方法 | 功能 |
|------|------|------|
| `/chat?q=xxx` | GET | 同步对话 |
| `/chat/stream?q=xxx` | GET (SSE) | 流式对话 |
| `/chat/expert?q=xxx` | GET | 专家模式（System Prompt） |
| `/chat/industry?industry=xxx&q=xxx` | GET | 行业客服（Prompt 模板） |
| `/chat/recipe?dish=xxx` | POST | 菜谱生成（结构化输出） |

---

## 🏗️ 项目结构

```
helloai/
├── pom.xml
├── README.md (本文件)
├── src/main/
│   ├── java/com/fletcher/helloai/
│   │   ├── HelloaiApplication.java    启动类
│   │   ├── controller/
│   │   │   └── ChatController.java    HTTP 接口
│   │   ├── service/
│   │   │   └── ChatService.java       核心逻辑 ⭐
│   │   └── dto/
│   │       └── Recipe.java            结构化输出 DTO
│   └── resources/
│       ├── application.yml            配置
│       ├── prompts/
│       │   └── customer-service.st    Prompt 模板
│       └── static/
│           └── index.html             演示页
└── .gitignore
```

---

## 🧱 技术栈

| 组件 | 版本 | 作用 |
|------|------|------|
| Spring Boot | 3.3.5 | Web 框架 |
| Spring AI | 1.0.0 | AI 集成 |
| JDK | 17+ | 运行时 |
| Reactor | 随 Spring WebFlux | 流式（Flux） |
| 大模型 | 通义千问 qwen-turbo | 推理后端 |

---

## 🛡️ 安全提醒

- ✅ API Key 通过**环境变量**注入，绝不硬编码
- ✅ `.gitignore` 排除 `.env`、`*.key`、`application-local.yml`
- ✅ 如果 Key 泄露：去[控制台](https://dashscope.console.aliyun.com/)立即删除并重新生成

---

## 💡 下一步（Week 2+）

- **Week 2**：给 AI 加上 Function Calling，让它能调业务方法
- **Week 3**：接入向量库 Milvus，做 Embedding
- **Week 4-6**：在本项目基础上演进成企业 RAG 知识库（简历级项目）

---

## 🎓 学习资源

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [本项目配套教程](../../Week1-SpringAI基础/)
- [阶段 3 总览](../../README.md)
