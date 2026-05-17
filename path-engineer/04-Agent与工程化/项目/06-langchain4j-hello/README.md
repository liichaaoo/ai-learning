# 06-langchain4j-hello · 第一个 Agent（Week 1 交付物）

> 配套教程：[Week 1 · LangChain4j 基础](../../Week1-LangChain4j基础/README.md)

---

## 🎯 项目目标

把 Week 1 五天学的串起来：
- AiServices 声明式接口
- 多用户隔离的 Redis ChatMemory
- 3 个工具（时间 / 天气 / 计算器）
- 流式对话
- 多模型切换（通义 / Ollama）

---

## 🛠 技术栈

| 组件 | 用途 |
|------|------|
| Spring Boot 3 | 框架 |
| LangChain4j 0.36+ | AI 库 |
| LangChain4j DashScope Starter | 通义集成 |
| LangChain4j Ollama Starter | 本地模型 |
| Redis 7 | ChatMemory 持久化 |

---

## 🚀 快速开始

```bash
# Redis
docker run -d -p 6379:6379 redis:7

# Ollama（可选）
ollama serve & ollama pull qwen2.5:0.5b

# 起服务
DASHSCOPE_API_KEY=sk-xxx ./mvnw spring-boot:run

# 测试
curl -X POST http://localhost:8080/api/chat \
  -H "X-User-Id: alice" -H "Content-Type: application/json" \
  -d '{"q":"现在几点？上海天气怎么样？"}'
```

---

## 📁 期望目录

```
06-langchain4j-hello/
├── pom.xml
├── README.md
└── src/main/
    ├── java/com/demo/lc4j/
    │   ├── Lc4jApplication.java
    │   ├── controller/ChatController.java       ← Week1 Day5 §2.4
    │   ├── service/AssistantService.java        ← Day5 §2.1
    │   ├── tools/{Time,Weather,Calculator}Tool.java   ← Day5 §2.2
    │   ├── memory/RedisChatMemoryStore.java      ← Day3 §5.1
    │   └── config/Lc4jConfig.java                 ← Day5 §2.3
    └── resources/application.yml
```

---

## 📝 进度自检

- [ ] AiService 接口能跑（不写一行实现）
- [ ] 3 个 Tool 能被自动调用
- [ ] 多用户 memory 隔离
- [ ] Redis 能看到 `lc4j:memory:alice` 等 key
- [ ] 流式接口 SSE 输出
- [ ] 录 5 分钟演示

---

## 🔗 相关链接

- ⬆️ [Week 1 总览](../../Week1-LangChain4j基础/README.md)
- 📖 [Day 5 整合教程（含完整代码）](../../Week1-LangChain4j基础/Day5-第一个Agent.md)
- 📦 [上一项目：05-rag-knowledge-base](../../../03-SpringAI与RAG/项目/05-rag-knowledge-base/)
- 📦 [下一项目：07-agent-patterns](../07-agent-patterns/)
