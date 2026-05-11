# Java + AI 学习路径

> 🎯 **目标读者**：有 5 年+ Java 经验的工程师，想转 AI 但不想扔掉母语武器
>
> 💰 **目标岗位**：大厂 / AI 公司「Java 大模型应用开发工程师」/「AI 应用平台架构师」
>
> 📅 **学习周期**：6 周入门 + 持续深耕

---

## 一、为什么要走这条路（市场依据）

### 1. 纯 Java CRUD 在贬值
2026 年大厂招聘的明确信号：
- **字节跳动**：2026 春招 5000+ 岗位，**AI 相关占比近半**，优先后端经验
- **百度**：AI 岗位占比 **90%+**
- 阿里、腾讯、美团、京东**都在大规模建 AI 应用平台**

### 2. 「Java + AI」反而是稀缺品种
- 99% 的 AI demo 是 Python 写的
- 但 99% 的企业系统是 Java 的
- **能把 AI 接入企业系统的 Java 工程师** = 极度稀缺
- 真实 JD 明确写着：**精通 Spring Boot + Spring AI + LangChain4j + RAG**

### 3. 薪资数据
- **字节大模型应用架构专家**：年薪最高 **128 万**
- **Java + 大模型应用**：P7 = 80-130W，P8 = 130-200W
- 顶尖 AI 应用架构师：**150-300W**

---

## 二、技术栈全景图

```
应用框架
├── Spring Boot 3.x          ← 你已会
├── Spring AI ⭐⭐⭐⭐⭐         ← 必学（Spring 官方 AI 框架）
└── LangChain4j ⭐⭐⭐⭐         ← 重要（社区主流）

模型接入
├── OpenAI / Anthropic API
├── 国产：通义千问 / 文心 / 混元 / DeepSeek
├── Ollama（本地模型）
└── HuggingFace Inference API

数据层
├── 向量数据库：Milvus ⭐⭐⭐⭐⭐ / Qdrant / pgvector
├── Embedding 模型：bge-m3 / text-embedding-3
└── 文档处理：Apache Tika / PDF 解析

中间件（你的强项，复用即可）
├── Redis（KV Cache、会话）
├── Kafka（异步任务）
└── MySQL / PostgreSQL

观测 & 运维（你的强项）
├── Prometheus + Grafana
├── 链路追踪（Jaeger / SkyWalking）
└── K8s 部署

辅助（懂即可）
├── Python 速成 ← 看懂代码就行
└── Docker / Linux ← 你已会
```

---

## 三、6 周学习计划

### Week 1：Python 速成（3 天） + AI 基础概念

**目标**：能看懂 Python AI 代码 + 理解 LLM 是怎么回事

| 天数 | 内容 |
|------|------|
| Day 1 | Python 语法速成（廖雪峰前 30%）|
| Day 2 | NumPy + pandas 基础 |
| Day 3 | 看懂 HuggingFace Hello World |
| Day 4-5 | LLM 工作原理（Token、推理、Prompt）|
| Day 6-7 | 调用 OpenAI / Claude API（用 Java + curl）|

📚 推荐：《动手学深度学习》前两章 + Andrej Karpathy 的 [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)

---

### Week 2：Spring AI 入门（重头戏）

**目标**：能用 Spring AI 写一个 Hello World 聊天应用

| 天数 | 内容 |
|------|------|
| Day 1 | Spring AI 官方文档通读 |
| Day 2 | ChatClient API + Stream 流式响应 |
| Day 3 | Prompt Template + Output Parser |
| Day 4 | Function Calling（Tool 调用）|
| Day 5 | Multi-modal（图片输入）|
| Day 6-7 | **实战**：写一个 Spring Boot 智能客服 |

📚 文档：https://docs.spring.io/spring-ai/reference/

---

### Week 3：向量库 + RAG

**目标**：能搭建一个企业知识库 RAG 系统

| 天数 | 内容 |
|------|------|
| Day 1 | 向量化原理 + Embedding 模型 |
| Day 2 | Milvus 部署 + Java SDK |
| Day 3 | 文档加载 + 分块策略 |
| Day 4 | Spring AI 的 RAG 组件 |
| Day 5 | 召回 + 重排 + 生成 |
| Day 6-7 | **实战**：企业知识库（接入 PDF/Word/网页）|

---

### Week 4：LangChain4j + Agent

**目标**：能写一个能调用工具的 AI Agent

| 天数 | 内容 |
|------|------|
| Day 1 | LangChain4j 概览，对比 Spring AI |
| Day 2 | Memory（短期/长期记忆）|
| Day 3 | Tools（自定义工具）|
| Day 4 | ReAct 模式 + Agent 编排 |
| Day 5 | 流式 + 异步处理 |
| Day 6-7 | **实战**：AI Code Reviewer / 数据分析 Agent |

---

### Week 5：MCP + 工程化

**目标**：理解 MCP 协议 + 上线一个生产可用的 AI 应用

| 天数 | 内容 |
|------|------|
| Day 1 | MCP 协议（Anthropic 主推，2026 标配）|
| Day 2 | 流量控制（限流、降级）|
| Day 3 | Prompt 注入防御 + 内容审核 |
| Day 4 | 成本优化（缓存、批量、模型路由）|
| Day 5 | 监控指标（TTFT、Token 消耗、命中率）|
| Day 6-7 | **实战**：把 Week 3 RAG 项目部署到云上 |

---

### Week 6：简历优化 + 面试准备

**目标**：拿到面试机会

| 天数 | 内容 |
|------|------|
| Day 1-2 | 简历改造（项目包装为 AI 应用平台架构）|
| Day 3 | GitHub 整理 + 写技术博客 |
| Day 4 | 内推渠道梳理（脉脉、KM、内部转岗）|
| Day 5 | 八股文准备（LLM 原理、RAG、Agent）|
| Day 6-7 | 模拟面试 + 投简历 |

---

## 四、必做的 3 个里程碑项目

按价值由低到高排序，**至少完成第 2 个**才有竞争力。

### 🥉 项目 1：Hello AI（Week 1-2）
**Spring Boot + Spring AI + OpenAI/Claude API**

最简单的对话应用，证明你能调通 LLM。

**简历加分**：⭐ （入门级，几乎不算项目）

---

### 🥈 项目 2：企业 RAG 知识库（Week 3-5）⭐ **必做**
**Spring Boot + Spring AI + Milvus + Redis + 流式响应**

特性：
- 支持上传 PDF / Word / 网页
- 文档自动切分 + 向量化
- 流式问答 + 引用溯源
- 多用户隔离 + 历史记录
- Docker 一键部署

**简历亮点写法**：
> 主导设计基于 Spring AI + Milvus 的企业知识库系统，
> 单实例支撑 1000+ QPS，平均首字延迟 < 800ms，
> 接入 GPT-4 / 通义千问双模型路由，月度推理成本节省 40%

**简历加分**：⭐⭐⭐⭐ （这就够你拿到面试了）

---

### 🥇 项目 3：AI Code Reviewer / 智能 Agent（Week 4-6）
**LangChain4j + Function Calling + GitHub Webhook**

特性：
- 监听 GitHub PR 事件
- 自动拉代码 → 调用 LLM 审查 → 评论
- 支持自定义规则
- 多步骤推理（ReAct）

**简历亮点**：
> 设计基于 LangChain4j 的多 Agent 协作系统，
> 实现代码自动审查，准确率 85%+，已在团队 50+ 仓库落地

**简历加分**：⭐⭐⭐⭐⭐ （直接打到 P8 级别）

---

## 五、必读资源（精选不堆砌）

### 📘 文档（按重要性）
1. **Spring AI 官方文档**（必读）：https://docs.spring.io/spring-ai/reference/
2. **LangChain4j 官方文档**：https://docs.langchain4j.dev/
3. **Anthropic Claude API**：https://docs.anthropic.com/

### 🎬 视频
1. **Spring 官方 Spring AI 介绍**（YouTube）
2. **Andrej Karpathy** - Let's build GPT（B 站有翻译）
3. **吴恩达 LangChain 短课程**（DeepLearning.AI）

### 📖 书籍
1. 《Spring 实战》第 6 版 - 复习 Spring Boot
2. 《大模型应用开发极简入门》- 概念扫盲
3. 《LangChain 实战》- 虽然是 Python，但思路通用

### 🛠️ 实战项目（参考代码）
- **Spring AI 官方 Examples**: https://github.com/spring-projects/spring-ai-examples
- **LangChain4j Examples**: https://github.com/langchain4j/langchain4j-examples
- **AIBaby（国人优秀开源）**: 搜索 "spring-ai-alibaba"

### 📰 持续关注
- 公众号：`Spring 中文社区`、`InfoQ`、`阿里云开发者`
- 知乎：搜索"Spring AI"
- GitHub Trending（Java 类目）

---

## 六、面试准备：高频考点

### Java + AI 高频面试题

#### 基础概念
1. LLM 的 Token、Embedding、上下文窗口分别是什么？
2. 解释 Temperature、Top-p、Top-k 参数
3. 流式响应（SSE）和普通响应的区别？怎么用 Spring 实现？

#### 框架使用
1. Spring AI 的 `ChatClient` 和 `ChatModel` 区别？
2. 如何在 Spring AI 中实现 Function Calling？
3. LangChain4j 的 Memory 有哪几种实现？

#### RAG
1. RAG 的完整流程？
2. 文档切分有哪些策略？长文档怎么处理？
3. 向量检索 vs BM25，怎么混合？
4. Embedding 模型怎么选？什么时候要微调？
5. RAG 答非所问怎么排查？

#### Agent
1. ReAct 模式是什么？和 CoT 区别？
2. Function Calling vs MCP 协议？
3. 多 Agent 协作有哪些坑？

#### 工程化
1. LLM 应用怎么做缓存？哪些层可以缓存？
2. 怎么防御 Prompt 注入攻击？
3. 怎么控制 API 成本？
4. 模型 A/B 测试怎么设计？
5. 怎么监控 LLM 应用质量？

#### 系统设计（高级岗必考）
1. 设计一个企业级 RAG 系统，要支持 100W+ 文档、1W+ QPS
2. 设计一个多模型路由网关（GPT-4 / Claude / 通义混合调度）
3. 设计一个 AI 客服系统的高可用方案

---

## 七、行动清单（今天就开始）

- [ ] **今晚**：在本机装 IntelliJ IDEA + JDK 17（Spring AI 要求 JDK 17+）
- [ ] **明天**：注册 OpenAI / Claude API Key（或用国产替代）
- [ ] **本周**：跟着 Spring AI 官方教程跑通 Hello World
- [ ] **第 2 周**：开始项目 2（企业 RAG 知识库）
- [ ] **第 4 周**：把项目放 GitHub，写技术博客
- [ ] **第 6 周**：开始投简历

---

## 八、目录结构

```
07-Java-AI路径/
├── README.md                       ← 你正在看的这个
├── 笔记/
│   ├── SpringAI入门.md
│   ├── LangChain4j入门.md
│   ├── RAG原理与实践.md
│   ├── Agent与MCP.md
│   └── Prompt工程.md
├── 项目/
│   ├── 01-helloai/                 ← Spring AI Hello World
│   ├── 02-rag-knowledge/           ← 企业知识库 RAG
│   └── 03-ai-agent/                ← Agent 项目
└── 资料/
    ├── 面试题集.md
    └── 简历模板.md
```

---

## 九、最后一句话

> **你不是在「转行」，你是在「升级」。**
>
> 7 年 Java 是地基，AI 能力是新长出来的高层。
> 那些天天喊"Java 没落"的人，往往是没能力同时驾驭两者。
> 你只需要 6 周，就能站在大多数人还在徘徊的位置之上。

干就完了 🚀
