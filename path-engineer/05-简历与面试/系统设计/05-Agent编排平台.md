# 系统设计 · 05 Agent 编排平台

> 🎯 **题目**：设计一个类似 Dify / Coze 的 Agent 编排平台，支持流程编排、版本管理、监控
>
> 💡 **核心价值**：把"代码定义工作流"变成"配置定义工作流"，非技术人员也能落地 AI 应用

---

## 一、需求澄清

```
业务定位：To 内部 5 BG 产品/运营，月需求 50 个 AI 应用，目标自助率 80%

功能：
  - 拖拽编辑器（Web）：节点 + 连线
  - 节点类型：LLM / 代码 / HTTP / 知识库 / 条件 / 循环 / 子流程
  - 变量传递（前后节点数据流转）
  - 调试器（单步 / 断点 / 变量查看）
  - 版本管理（草稿/测试/生产，可回滚）
  - 灰度 + A/B 测试
  - 评测集（防版本升级退化）
  - 全链路 trace + 监控
  - 计费（接 Token 计费系统）

非功能：
  - 单流程 ≤ 100 节点
  - 单租户 ≤ 1k 应用
  - 平台 QPS 5k
  - P99 < 5s
  - 99.95% 可用
```

---

## 二、整体架构

```
┌──────────────────────────────────────────────────────┐
│            控制台 Web（React Flow）                    │
│   流程编辑器 / 调试器 / 监控大盘                       │
└──────────────────────────┬───────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│         控制平面 Control Plane                        │
│  • 流程 CRUD / 版本管理 / 灰度发布                    │
│  • 节点市场（内置 + 自定义）                          │
│  • 评测集管理 + 自动跑                               │
│  存储：MySQL (DSL) + Redis (路由)                    │
└──────────────────────────┬───────────────────────────┘
                           ↓ DSL（JSON）
┌──────────────────────────────────────────────────────┐
│         数据平面 Workflow Engine                      │
│  • DSL 解析 → 拓扑排序 → 调度                         │
│  • 节点执行器池                                       │
│  • 状态机 + 重试 + 超时                               │
│  • Trace + 计费                                       │
│                                                       │
│  下游：LLM Gateway / 知识库 / 内部 API / 沙箱         │
│  存储：Redis（运行态）+ ClickHouse（历史）             │
└──────────────────────────────────────────────────────┘
```

---

## 三、关键设计

### 3.1 流程 DSL ⭐⭐⭐ 平台灵魂

```json
{
  "id": "wf_001",
  "version": "v3",
  "name": "智能客服流程",
  "trigger": { "type": "http", "path": "/customer-service" },
  "variables": {
    "user_query": { "type": "string", "from": "input.query" }
  },
  "nodes": [
    {
      "id": "n1",
      "type": "intent_classifier",
      "config": { "model": "qwen-turbo", "prompt": "..." },
      "input": { "text": "${user_query}" },
      "output": { "intent": "$.intent" }
    },
    {
      "id": "n2",
      "type": "branch",
      "condition": "${n1.intent}",
      "branches": {
        "FAQ":      { "next": "n3" },
        "ORDER":    { "next": "n4" },
        "_default": { "next": "n5" }
      }
    },
    {
      "id": "n3",
      "type": "knowledge_base",
      "config": { "kb_id": "kb_faq", "top_k": 3 },
      "input": { "query": "${user_query}" },
      "output": { "answer": "$.answer" },
      "next": "end"
    }
  ],
  "edges": [
    { "from": "n1", "to": "n2" }
  ]
}
```

**4 个核心抽象**：

| 概念 | 作用 |
|------|------|
| **Trigger** | 入口（HTTP / 定时 / 消息）|
| **Variables** | 全局变量定义 + 来源 |
| **Nodes** | 节点列表 + 各自配置 |
| **Edges / Branches** | 流转关系（含条件分支）|

**变量引用**：`${node_id.field}` / `${variables.xxx}`，支持 JSONPath。

### 3.2 节点抽象（统一接口）

```java
public interface NodeExecutor {
    String type();    // "llm" / "http" / "knowledge_base"
    NodeOutput execute(NodeContext ctx, NodeConfig config, NodeInput input);
}

@Component
public class LlmNodeExecutor implements NodeExecutor {
    public String type() { return "llm"; }
    public NodeOutput execute(NodeContext ctx, NodeConfig cfg, NodeInput in) {
        String prompt = renderTemplate(cfg.prompt(), in.variables());
        ChatResponse resp = chatClient.prompt(prompt)
            .options(cfg.toChatOptions())
            .call().chatResponse();
        ctx.recordTokens(resp.usage());
        return NodeOutput.of("text", resp.content());
    }
}
```

**内置节点类型**（10+）：
- `llm` —— LLM 调用
- `knowledge_base` —— RAG 检索
- `http` —— 调外部 API
- `code` —— Python/JS 沙箱
- `branch` —— 条件分支
- `loop` —— 循环
- `subflow` —— 子流程
- `human` —— 人工审核
- `code_review_agent` —— 内置业务 Agent
- `custom` —— 用户自定义

### 3.3 调度引擎

```java
public class WorkflowEngine {
    public WorkflowResult run(String workflowId, Map<String, Object> input) {
        Workflow wf = workflowRepo.load(workflowId);
        WorkflowContext ctx = new WorkflowContext(traceId(), input);
        
        // 拓扑排序节点
        List<Node> sortedNodes = topologicalSort(wf.nodes(), wf.edges());
        
        for (Node node : sortedNodes) {
            // 1. 检查前置依赖（branch 是否走到这）
            if (!ctx.shouldExecute(node.id())) continue;
            
            // 2. 渲染输入（替换变量）
            NodeInput nodeInput = renderInput(node.input(), ctx);
            
            // 3. 选执行器
            NodeExecutor executor = executorRegistry.get(node.type());
            
            // 4. 执行（带重试 + 超时）
            NodeOutput output = executeWithRetry(executor, node, nodeInput, ctx);
            
            // 5. 写回 context
            ctx.put(node.id(), output);
            
            // 6. trace
            traceLogger.log(node, nodeInput, output, ctx);
        }
        
        return ctx.toResult();
    }
}
```

**关键能力**：
- **拓扑排序**：保证依赖顺序
- **DAG 校验**：拒绝循环依赖（除非显式标记 loop 节点）
- **重试**：节点级 + 流程级（指数退避）
- **超时**：单节点 30s 默认，流程总 5min

### 3.4 调试器

```
单步执行：
  POST /api/v1/workflows/{id}/debug
  Body: { input, breakpoints: [n1, n3], step: true }
  
  → 后端走到 n1 暂停，返回当前 ctx 给前端
  → 前端展示变量、可手改
  → 用户点"继续"，后端继续到下一个断点
```

**实现**：用 Redis 暂存 ctx + 命令队列；引擎每次执行节点前 check 是否在断点。

### 3.5 版本管理 + 灰度

```
状态机：草稿 → 测试 → 生产

发布流程：
  1. 编辑器改 → 自动存"草稿"版本
  2. 测试通过 → 发布"测试"版本（test 域名）
  3. 评测集跑 → 通过 → 发布"生产"版本

灰度路由（Redis）：
  workflow:wf_001:version
    -> { "v2": 90, "v3": 10 }   # v2:v3 = 9:1
  
  请求来时：
    hash = (user_id) % 100
    if hash < 10: 走 v3
    else:        走 v2
```

**回滚**：一键改 Redis 比例 → 立即生效。

### 3.6 评测集

```yaml
# 评测集定义
test_set:
  - input: { query: "怎么退款" }
    expected:
      - contains: "退款"
      - score_gpt4: ">= 4.0"   # GPT-4 当评委打分

  - input: { query: "查订单 123" }
    expected:
      - tool_called: "queryOrder"
      - tool_args: { orderId: "123" }
```

**自动评测流程**：
1. 改了 DSL → 提交"发布"
2. 平台自动跑评测集（异步 5 分钟）
3. 通过率 ≥ 95% → 允许发布
4. 不通过 → 列出失败 case + 给改进建议

### 3.7 Trace 与监控

```
每次流程执行写一条 ClickHouse 记录：
  trace_id, workflow_id, version, user_id,
  total_latency, total_tokens, total_cost,
  status (success / failed / timeout),
  failed_node_id, failed_reason

每个节点写一条：
  trace_id, node_id, node_type, latency, tokens, status

业务大盘（Grafana）：
  - 各流程 QPS / P99 / 错误率
  - 各节点平均耗时（找瓶颈）
  - 各模型 Token 用量
  - Top 慢流程 / 高费流程
```

---

## 四、关键技术挑战

### 挑战 1：动态 DSL 怎么编译执行？

**两种方式**：

| 方式 | 优点 | 缺点 |
|------|------|------|
| 解释执行 | 改 DSL 立即生效 | 慢一点（每次解析）|
| 编译执行 | 极快 | 改 DSL 要重编译 |

**生产推荐**：解释执行 + DSL 缓存 + 节点执行器预热（快得很）。

### 挑战 2：循环节点怎么避免死循环？

```yaml
loop:
  max_iterations: 10        # 硬上限
  break_condition: "${result.done}"   # 退出条件
  timeout_seconds: 60       # 总超时
```

**3 道护栏**：迭代上限 + 退出条件 + 超时。

### 挑战 3：自定义代码节点的安全？

**沙箱方案对比**：

| 方案 | 隔离性 | 性能 | 复杂度 |
|------|--------|------|--------|
| 同进程 + SecurityManager | 弱 | 高 | 低 |
| **Docker 容器** ⭐ | 强 | 中 | 中 |
| Firecracker microVM | 极强 | 中 | 高 |
| WebAssembly | 中 | 高 | 中 |

**生产推荐**：Docker 池 + 资源限制（CPU/内存/网络/超时），用 gVisor 加固。

### 挑战 4：5k QPS 怎么扛？

```
- 控制平面无状态 → 水平扩展
- 数据平面（引擎）按 workflow_id 一致性 hash → 同流程在同实例（warm cache）
- DSL 缓存 + 节点执行器单例
- 异步节点（HTTP / LLM）→ Reactor / WebFlux
- Redis 集群（运行态）
- ClickHouse 集群（历史）
```

---

## 五、可能被追问

| 追问 | 答点 |
|------|------|
| Dify / Coze 你研究过吗？区别？| 平台思路类似，差异在国内合规 + 与公司业务深度集成 |
| 怎么做"流程升级不影响在跑流程"？| 流程实例启动时锁定 version，全程不变；新流量按灰度走新版 |
| 节点失败重试，但 LLM 已扣费怎么办？| 计费系统去重（基于 trace_id + node_id 幂等）|
| 用户写了死循环代码节点？| 沙箱 timeout + CPU 限额 + 重试上限 |
| 流程能调用流程吗？| subflow 节点支持，但有深度上限（默认 5 层防递归）|
| 怎么做权限？| RBAC：流程级"创建/编辑/发布/调用"四种权限，可分配给角色/组 |
| 跨租户共享节点市场怎么做？| 节点定义 + 用户自定义代码 + 审核机制（人工）|

---

## 六、答题加分点

1. **DSL 设计是平台灵魂**（先说 DSL 体现架构思维）
2. **节点抽象 + 执行器注册**（开闭原则，新节点零改动）
3. **拓扑排序 + DAG 校验 + 循环节点 3 道护栏**
4. **版本管理 + 灰度路由 + 自动评测**（产品化思维）
5. **沙箱 4 方案对比**（深度思考）
6. **trace_id + node_id 幂等防重计费**（细节体现资深）
7. **一致性 hash 路由 warm cache**（性能优化）

---

## 七、与 Dify / Coze 的差异化

> **面试时强调"我们的平台不是简单复刻 Dify/Coze"**：

| 维度 | Dify/Coze | 我们的平台 |
|------|-----------|-----------|
| 客户群 | 通用开发者 | 内部 5 BG 业务 |
| 模型生态 | 偏开源 | 接公司私有部署 |
| 数据合规 | 部分需出海 | 100% 内网 |
| 计费 | 通用 | 接公司 Token 计费系统 |
| 评测 | 弱 | 必跑评测集才能上线 |

---

## 🔗 回到目录

- [`./01-企业RAG系统.md`](./01-企业RAG系统.md)
- [`./02-多模型路由网关.md`](./02-多模型路由网关.md)
- [`./03-AI客服系统.md`](./03-AI客服系统.md)
- [`./04-Token计费系统.md`](./04-Token计费系统.md)
- [`../面试题/`](../面试题/)
