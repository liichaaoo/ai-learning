# 系统设计 · 01 企业级 RAG 系统

> 🎯 **题目**：设计一个企业级 RAG 知识库系统，支撑 100w+ 文档 / 1w+ QPS 问答 / 多租户 / 多模型 / 全链路可观测
>
> ⏱️ **面试时长**：30-45 分钟
>
> 🧭 **答题结构**（黄金 5 步）：需求澄清 → 容量估算 → 整体架构 → 关键设计 → 演进路线

---

## 一、需求澄清（5 分钟）⭐ 别上来就画图

> 面试官说"设计一个 RAG 系统"，**先问 8 个问题**，体现资深特质。

```
功能需求：
  Q1: 用户量？文档量？QPS？
  Q2: 支持哪些文档类型（PDF/Word/Markdown/网页）？
  Q3: 是否多租户？租户间数据严格隔离？
  Q4: 是否需要流式返回？

非功能需求：
  Q5: P99 延迟要求？（建议端到端 < 3s，首字 < 800ms）
  Q6: 可用性要求？（建议 99.9% = 月度 43 分钟）
  Q7: 数据安全等级？（是否走云上 LLM？）
  Q8: 预算？（影响多模型策略）
```

**假设答案**（用于本设计）：

> "10w 用户 / 100 万文档 / 1w QPS 峰值 / 多租户严格隔离 / 流式 / P99 < 3s / 99.9% 可用 / 数据可走云 LLM 但需脱敏"

---

## 二、容量估算（3 分钟）

```
QPS：1w 峰值 → 平均 2k QPS

Embedding 调用：
  - 每个 query embedding 1 次 = 2k QPS
  - 文档入库每 chunk embedding 1 次

文档量：
  - 100 万文档 × 平均 50 chunk = 5000 万 chunk
  - 每 chunk 1024 维 × 4 字节 = 4 KB → 总 200 GB 向量数据
  - + 原文存储 ≈ 500 GB
  - + MySQL 元数据 ≈ 50 GB

LLM 调用：
  - 假设 30% 缓存命中 → 实际 1.4k QPS
  - 单次 prompt 4k token + completion 500 token
  - 月度 token = 1.4k × 86400 × 30 × 4500 = 16 万亿 token
  - 月度成本（GPT-4o $5/M in + $15/M out）≈ $XXX，换便宜模型省 60%

带宽：
  - 流式响应 1KB/chunk × 50 chunk = 50KB/请求
  - 1w QPS × 50KB = 500 MB/s（必须 CDN + SSE）
```

---

## 三、整体架构图（10 分钟，画图最关键）

```
┌─────────────────────────────────────────────────────────────────┐
│                     接入层 (Gateway)                              │
│   Nginx + JWT 鉴权 + 限流 (Sentinel) + 多租户路由                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────┐  ┌─────────────────────────────────────────┐
│  离线索引流水线        │  │           在线问答服务                    │
│  ──────────────       │  │           (Spring Boot 集群 50 实例)     │
│  1.文档上传(MinIO)    │  │                                         │
│  2.→ Kafka            │  │  ┌─ Cache 层 (语义缓存)                │
│  3.→ Worker 池        │  │  │  Redis Vector + 余弦相似度 0.95      │
│       (10 个 Pod)     │  │  └────────↓ miss                       │
│  4.分片 + Embedding   │  │  ┌─ 检索层 (混合)                       │
│  5.写 Milvus + ES     │  │  │  Milvus(向量) + ES(BM25) + Reranker│
│       + MinIO(原文)    │  │  └────────↓ Top-5                      │
│                       │  │  ┌─ 生成层 (流式)                       │
└──────────────────────┘  │  │  ChatClient + Advisor 链              │
            ↓               │  │     ├ MemoryAdvisor                   │
   ┌──────────────────────┐ │  │     ├ QuestionAnswerAdvisor          │
   │ Milvus 集群           │ │  │     ├ CitationAdvisor                │
   │  (3 master + 5 data)  │ │  │     └ UsageRecorderAdvisor           │
   │ ES 集群 (BM25)        │ │  │  + ModelRouter (多模型)              │
   │ MinIO (原文)          │ │  └────────↓ SSE                       │
   │ MySQL (元数据 + 用户)  │ │      返回前端                           │
   │ Redis (缓存 + 会话)   │ └─────────────────────────────────────────┘
   └──────────────────────┘
                                          ↓
                   ┌──────────────────────────────────────┐
                   │  可观测：Prometheus + Grafana + Loki  │
                   │  追踪：SkyWalking                    │
                   │  日志：ELK                           │
                   └──────────────────────────────────────┘
```

**关键架构决策**：
- **离线索引 ≠ 在线问答**（两条流水线，互不影响）
- **流量进 Gateway 先做 JWT + 限流**（防恶意刷）
- **缓存在最前**（30% 命中省 LLM 成本）
- **检索 + 生成解耦**（检索可独立扩缩容）

---

## 四、关键设计深入（15 分钟）⭐⭐⭐

### 4.1 离线索引流水线

```
用户上传 PDF (10MB)
    ↓ MinIO 持久化（断点续传 + 分片上传）
    ↓ MQ 投递 task_id
    ↓ Worker 消费
    ├─ 1. 文档解析（Apache Tika）→ 纯文本
    ├─ 2. 清洗（去 HTML / 修编码）
    ├─ 3. 切分（Recursive Splitter, chunk=512, overlap=50）
    ├─ 4. Embedding（bge-m3 本地 GPU 集群批处理 16 个/批）
    ├─ 5. 写 Milvus（向量 + 元数据 tenant_id/user_id/doc_id）
    ├─ 6. 写 ES（原文 + IK 分词，给 BM25 用）
    └─ 7. 更新 MySQL 状态（pending → processing → done/failed）
       ↓
    Server-Sent Events 推送进度到前端
```

**设计要点**：
- **解耦**：上传 200ms 返回 task_id，处理后台跑（Kafka 削峰）
- **批处理**：Embedding 16 个/批，吞吐提升 8x
- **幂等**：task_id 唯一，重复消费跳过
- **失败可重试**：Kafka DLQ + 人工复活

### 4.2 检索：三阶段混合 ⭐⭐⭐

```
Query "如何提单据"
    ↓ Embedding
    ↓ 并行
    ├──→ Milvus.search(emb, topK=50, filter=tenant_id) → 50 候选
    └──→ ES.search(query, topK=50, filter=tenant_id)    → 50 候选
    ↓ 合并（RRF 算法）
    ↓ 去重 → 50 候选
    ↓ Reranker (Cross-Encoder, bge-reranker-v2-m3)
    ↓ Top-5
```

**多租户安全的关键**：

```java
// 必须服务端添加 tenant_id 过滤，绝不能信前端
SearchRequest req = SearchRequest.query(query)
    .withFilterExpression("tenant_id == '" + ctx.getTenantId() + "'")
    .withTopK(50);
```

⚠️ **红线**：从 JWT/Session 解出 tenant_id，**不能从请求参数读**（防越权）。

### 4.3 生成层：Advisor 链路

```
ChatClient.prompt(question)
    .advisors(
        new RagAdvisor(retriever, top5),       // 注入文档
        new MemoryAdvisor(redisChatMemory),    // 多轮历史
        new SafeguardAdvisor(promptScanner),   // 输入安全
        new CitationAdvisor(),                 // 引用抽取
        new UsageRecorderAdvisor(metrics)      // Token 计费
    )
    .stream().content()  // SSE 流式
```

每个 Advisor 单一职责，按需组合，业务代码 0 污染。

### 4.4 多模型路由 + 降级

```java
public String chat(String tenantId, String q, Complexity c) {
    return switch (c) {
        case SIMPLE -> qwenTurbo.chat(q);          // ¥0.001/k token
        case NORMAL -> qwenPlus.chat(q);           // ¥0.005/k token
        case COMPLEX -> gpt4o.chat(q);             // ¥0.03/k token
    };
}

// CircuitBreaker 包裹，挂了走下一级
@CircuitBreaker(name = "gpt4o", fallbackMethod = "fallbackToQwen")
```

**复杂度判断**：
- 长度 < 50 字 + 无专有名词 → SIMPLE
- 涉及推理/总结 → NORMAL
- 涉及代码/数学/多步推理 → COMPLEX

**生产实测**：路由策略让月度成本下降 ~40%。

### 4.5 缓存策略

```
L1 精确缓存（Redis String）：
  key = "rag:exact:" + md5(query + tenant_id)
  TTL 1h，命中率 5-10%

L2 语义缓存（Redis Vector）：
  key = "rag:sem:" + tenant_id
  embedding 余弦 > 0.95 命中
  TTL 24h，命中率 20-30%

L3 Embedding 缓存：
  key = "emb:" + md5(text)
  TTL 7d，命中率 50%+（同样 query 多次问）

时效性问题黑名单：
  ["今天", "现在", "实时", "最新"] 命中不缓存
```

### 4.6 流式 SSE

```java
@GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> chat(@RequestParam String q) {
    return ragService.streamChat(q)
        .map(chunk -> ServerSentEvent.builder(chunk).build())
        .onErrorResume(e -> Flux.just(ServerSentEvent.builder("[ERROR]" + e.getMessage()).build()));
}
```

**Nginx 配置**：

```nginx
location /chat {
    proxy_pass http://rag-backend;
    proxy_buffering off;          # SSE 必须关
    proxy_read_timeout 300s;       # 长流式不能超时
    proxy_set_header X-Accel-Buffering no;
}
```

---

## 五、可观测设计

### 5.1 三大支柱

| 支柱 | 工具 | 关键指标 |
|------|------|---------|
| **Metrics** | Prometheus + Grafana | QPS / TTFT / P99 / 缓存命中率 / Token 用量 |
| **Tracing** | SkyWalking | 端到端 trace_id 串联：Gateway → 检索 → LLM |
| **Logging** | ELK + Loki | 结构化日志 `[METRIC]` 标签 |

### 5.2 业务大盘

```
首页：实时 QPS 曲线 + P99 延迟 + 错误率
检索页：召回率 / Top-K score 分布 / 慢查询
模型页：各模型成本占比 + 调用量 + 平均延迟
告警：P99 > 3s / 错误率 > 1% / 单用户 1h > 100 次 → 钉钉
```

---

## 六、可用性 / 容灾

```
多 AZ 部署：3 个可用区，每区 16 实例 + Milvus 分片
Milvus 副本：3 副本，自动故障切换
Redis 哨兵 + Cluster
LLM 降级：通义 → GPT-4o → Ollama → 模板回答
熔断 + 限流：Resilience4j (CircuitBreaker + RateLimiter)
监控告警：P99 异常自动通知 + 一键扩容
```

---

## 七、演进路线（5 分钟，体现规划力）

```
v1.0（4 周）：MVP
  - 单租户、单模型、单机部署
  - 跑通"上传 → 入库 → 问答"基础流程
  - 30 题人工评测，Top-5 召回率 70%

v2.0（4 周）：生产级
  - 多租户隔离、Milvus 集群、Kafka 异步入库
  - 加缓存层 + 语义缓存
  - 多模型路由 + 监控

v3.0（4 周）：性能 + 评测
  - 加 Reranker，召回率 70% → 90%
  - 离线评测集 100 题 + CI 自动跑
  - 流式 + 引用前端组件库

v4.0（未来）：智能化
  - 多模态（图片/表格 RAG）
  - GraphRAG（知识图谱增强）
  - Agent 化（自主调工具回答复杂问题）
```

---

## 八、答题加分点 ⭐⭐⭐

> 同样答完 6 个步骤，**这些细节让你脱颖而出**：

1. **必聊"父文档-子切片"二级索引**（绝大部分候选人不会）
2. **聊语义缓存的"时效性黑名单"**（体现工程经验）
3. **聊 RRF 算法 + 不需要 score 归一化**（体现深度）
4. **聊多租户 filter 必须服务端加**（体现安全意识）
5. **聊 TTFT 这个流式独有指标**（体现做过流式系统）
6. **聊 30 题人工评测集 + CI 自动跑**（体现质量意识）
7. **聊月度成本下降 40% 的路由策略**（体现成本意识）

---

## 九、可能被追问的问题

> | 追问 | 关键答点 |
> |------|---------|
> | 100w 文档怎么做到秒级检索？| Milvus HNSW 索引 + 分片（按 tenant_id）|
> | 突然来了 5w QPS？| 限流 + 缓存 + 降级 + 排队 |
> | 用户问"今天股价"怎么办？| RAG 检索不到 → 降级走 Tool/Web Search |
> | 文档更新了怎么办？| `doc_id` 唯一，更新 = 删 + 重新入库 |
> | 怎么知道答案对不对？| 离线评测集 + 在线👍👎 + LLM 自评 |
> | Embedding 模型升级怎么办？| 全量重 embed（耗时操作，分批 + 灰度切流量）|

---

## 🔗 下一站

- [`./02-多模型路由网关.md`](./02-多模型路由网关.md)
- [`./03-AI客服系统.md`](./03-AI客服系统.md)
- [`./04-Token计费系统.md`](./04-Token计费系统.md)
- [`./05-Agent编排平台.md`](./05-Agent编排平台.md)
