# 系统设计 · 04 Token 计费系统

> 🎯 **题目**：设计一个 LLM Token 计费系统，支持多用户、多模型、多功能模块的精准计量与配额管理
>
> 💡 **类比**：这是 LLM 时代的"计费中台"，类似公有云的 Billing System 简化版

---

## 一、需求澄清

```
业务背景：
  - 公司有 5 个 AI 应用（客服 / 知识库 / Code Reviewer / Agent 平台 / 数据分析）
  - 接入了 8 种模型（GPT-4o / Claude / 通义 / DeepSeek / Ollama 等）
  - 5000 个内部用户 + 50 个企业租户
  - 月度推理成本 ~30 万元，缺乏精细化管理

功能需求：
  - 实时统计每用户/租户/模型/应用的 Token 用量与成本
  - 配额管理（按租户/用户/月度）
  - 超额预警 + 自动限流/拒服务
  - 计费报表（日/周/月，多维度透视）
  - 历史追溯（90 天明细 + 1 年聚合）
  - 多币种（人民币/美元，按汇率算实际成本）

非功能需求：
  - 计量误差 < 0.1%（必须精准）
  - 写入吞吐 ≥ 10w QPS
  - 查询 P99 < 500ms
  - 配额检查延迟 < 10ms（卡在请求路径上）
  - 数据 99.999% 不丢
```

---

## 二、容量估算

```
QPS：5w 峰值（每次 LLM 调用一条计费记录）
日记录数：5w × 86400 × 0.5（平均利用率） = 21 亿条/天
单条大小：约 200 字节
日数据量：21亿 × 200B ≈ 420 GB/天
3 个月明细：约 38 TB
1 年聚合（按用户 × 模型 × 日）：5000 × 8 × 365 ≈ 1500w 行 × 100B = 1.5 GB
```

**结论**：明细必须用列存（ClickHouse），聚合可走 MySQL。

---

## 三、整体架构

```
┌──────────────────────────────────────────────────────────────┐
│   Producers：5 个 AI 应用 + LLM Gateway                        │
│   每次 LLM 调用产生一条 UsageEvent                              │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
            ┌─────────────────────────────┐
            │    Kafka （高吞吐缓冲）       │
            │     topic: llm-usage         │
            │     副本=3，分区=64           │
            └────────────┬────────────────┘
                         ↓
        ┌────────────────┴───────────────────┐
        ↓                ↓                    ↓
┌─────────────┐  ┌──────────────┐   ┌────────────────┐
│ 实时聚合     │  │  明细存储     │   │  在线配额检查   │
│ (Flink)     │  │ (ClickHouse) │   │  (Redis)       │
│             │  │              │   │                │
│ • 1 分钟窗口│  │ • 90 天明细  │   │ • HSET 累加    │
│ • 5 分钟窗口│  │ • 多维 OLAP  │   │ • TTL 月底过期 │
│ • 1 小时窗口│  │ • 报表查询    │   │ • 配额硬卡控   │
│             │  │              │   │                │
└──────┬──────┘  └──────┬───────┘   └────────┬───────┘
       ↓                ↓                     ↓
   告警引擎          BI 报表              请求拦截器
   (RuleEngine)     (Grafana)            (前置校验)
       ↓
   钉钉/邮件/SMS
```

---

## 四、关键设计

### 4.1 UsageEvent 数据模型

```java
public record UsageEvent(
    String eventId,           // UUID，幂等键
    String tenantId,          // 租户
    String userId,            // 用户
    String appCode,           // 应用：customer-service / knowledge-base
    String featureCode,       // 功能：chat / summary / classify
    String model,             // gpt-4o / qwen-plus
    String requestId,         // 网关 traceId
    long promptTokens,        // 输入 token
    long completionTokens,    // 输出 token
    long latencyMs,
    BigDecimal cost,          // 成本（人民币）
    String currency,
    Instant timestamp
) {}
```

**关键字段**：
- **eventId**：幂等键，防止 MQ 重复消费导致重复计费
- **5 个维度**：tenant / user / app / feature / model（聚合分析的基础）
- **cost 提前算好**：上游计算并写入，下游不重算（避免汇率波动）

### 4.2 价格表与计算

```java
@Component
public class PriceTable {
    // 单位：元/千 token
    private final Map<String, ModelPrice> prices = Map.of(
        "gpt-4o",         new ModelPrice(BigDecimal.valueOf(0.025), BigDecimal.valueOf(0.075)),
        "qwen-plus",      new ModelPrice(BigDecimal.valueOf(0.005), BigDecimal.valueOf(0.015)),
        "qwen-turbo",     new ModelPrice(BigDecimal.valueOf(0.001), BigDecimal.valueOf(0.002)),
        "deepseek-chat",  new ModelPrice(BigDecimal.valueOf(0.001), BigDecimal.valueOf(0.002)),
        "ollama-qwen-7b", ModelPrice.FREE
    );
    
    public BigDecimal compute(String model, long inTokens, long outTokens) {
        ModelPrice p = prices.get(model);
        return p.input().multiply(BigDecimal.valueOf(inTokens))
            .add(p.output().multiply(BigDecimal.valueOf(outTokens)))
            .divide(BigDecimal.valueOf(1000), 6, RoundingMode.HALF_UP);
    }
}
```

**配置化**：价格表落 MySQL + Redis 缓存，运营可改不发版。

### 4.3 实时配额检查（卡在请求路径）

```java
public class QuotaChecker {
    // 每次 LLM 调用前，前置检查
    public void checkOrThrow(String tenantId, String userId, String model) {
        String month = YearMonth.now().toString();
        
        // 1. 租户月度配额
        long tenantUsed = redis.opsForHash().get("quota:tenant:" + tenantId, month + ":tokens");
        long tenantLimit = configService.getTenantLimit(tenantId);  // 缓存
        if (tenantUsed >= tenantLimit) throw new QuotaExceeded("tenant");
        
        // 2. 用户日度配额
        String day = LocalDate.now().toString();
        long userUsed = redis.opsForHash().get("quota:user:" + userId, day + ":tokens");
        long userLimit = configService.getUserLimit(userId);
        if (userUsed >= userLimit) throw new QuotaExceeded("user");
        
        // 通过：放行（实际扣额度在 Flink 异步聚合时做）
    }
    
    // 异步增加用量（Flink 1 分钟窗口聚合后批量 update）
    public void increment(UsageEvent event) {
        String month = YearMonth.from(event.timestamp()).toString();
        redis.opsForHash().increment(
            "quota:tenant:" + event.tenantId(),
            month + ":tokens", event.promptTokens() + event.completionTokens()
        );
        redis.expire("quota:tenant:" + event.tenantId(), 70, TimeUnit.DAYS);
    }
}
```

**取舍**：
- 同步检查：保证不超额
- 异步累加：保证不卡请求路径
- 缺点：极端情况可能"瞬间超额一点点"，工程上容忍 < 1%

### 4.4 ClickHouse Schema 设计

```sql
CREATE TABLE llm_usage_events (
    event_id String,
    tenant_id LowCardinality(String),    -- 字典编码
    user_id String,
    app_code LowCardinality(String),
    feature_code LowCardinality(String),
    model LowCardinality(String),
    request_id String,
    prompt_tokens UInt32,
    completion_tokens UInt32,
    total_tokens UInt32 MATERIALIZED prompt_tokens + completion_tokens,
    latency_ms UInt32,
    cost Decimal(18, 6),
    currency LowCardinality(String),
    timestamp DateTime64(3)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)        -- 按月分区，便于过期淘汰
ORDER BY (tenant_id, user_id, timestamp) -- 按租户/用户聚合查询快
TTL timestamp + INTERVAL 90 DAY DELETE   -- 90 天自动过期
SETTINGS index_granularity = 8192;
```

**关键设计**：
- **LowCardinality**：tenant_id/model 等枚举字段字典编码，存储省 80%
- **PARTITION BY 月**：删过期数据 = drop partition，秒级
- **ORDER BY 排序键**：决定查询性能（按租户/用户/时间过滤极快）
- **MATERIALIZED total_tokens**：自动算，省存储

### 4.5 Flink 实时聚合

```java
// 1 分钟窗口聚合，写回 MySQL（看板用）
DataStream<UsageEvent> events = env.fromSource(kafkaSource(...));

events
    .keyBy(e -> Tuple3.of(e.tenantId(), e.model(), 
                           DateUtils.minuteOf(e.timestamp())))
    .window(TumblingProcessingTimeWindows.of(Time.minutes(1)))
    .aggregate(new UsageAgg())
    .addSink(jdbcSink("INSERT INTO usage_minute (...) VALUES (...) " +
                       "ON DUPLICATE KEY UPDATE tokens=tokens+VALUES(tokens), cost=cost+VALUES(cost)"));
```

**3 个聚合层**：

| 粒度 | 存储 | 用途 | 保留期 |
|------|------|------|-------|
| 明细 | ClickHouse | 异常排查 | 90 天 |
| 分钟聚合 | MySQL | 实时大盘 | 7 天 |
| 日/月聚合 | MySQL | 历史报表 | 永久 |

### 4.6 告警引擎

```yaml
# 配置化规则
- name: 单租户日成本告警
  condition: "tenant_daily_cost > 5000"
  channel: [钉钉, 邮件]
  cooldown: 1h
  
- name: 单用户突发流量
  condition: "user_minute_tokens > 100000"
  action: 自动限流（熔断 5 分钟）
  channel: [钉钉]
  
- name: 模型异常成本
  condition: "model_hourly_cost > avg(7d) * 3"
  channel: [钉钉, 短信]
```

引擎每 1 分钟扫一次聚合表，命中规则 → 触发动作。

### 4.7 BI 报表

```sql
-- 例 1：本月各应用成本 Top 10
SELECT app_code, sum(cost) AS total_cost
FROM llm_usage_events
WHERE timestamp >= toStartOfMonth(now())
GROUP BY app_code
ORDER BY total_cost DESC
LIMIT 10;

-- 例 2：模型成本占比 + 调用量
SELECT 
    model,
    sum(cost) AS cost,
    count(*) AS calls,
    avg(latency_ms) AS avg_latency
FROM llm_usage_events
WHERE timestamp >= today() - 7
GROUP BY model;

-- 例 3：用户配额使用率排行
SELECT
    user_id,
    sum(total_tokens) AS used,
    max(quota) AS quota,
    used / quota * 100 AS rate
FROM llm_usage_events u JOIN user_quota q ON u.user_id = q.user_id
WHERE timestamp >= toStartOfMonth(now())
GROUP BY user_id, quota
ORDER BY rate DESC
LIMIT 20;
```

挂在 **Grafana** 上，业务/财务自助查询。

---

## 五、可靠性设计

### 5.1 数据不丢

```
1. AI 应用 → 本地 buffer + Kafka producer
   - acks=all
   - retries=Integer.MAX_VALUE
   - enable.idempotence=true（exactly-once）

2. Kafka 副本=3，min.insync.replicas=2

3. Flink checkpoint 1 分钟一次（精确一次语义）

4. ClickHouse 副本表 + 写入幂等（基于 event_id 去重）
```

### 5.2 配额数据一致性

> 极端场景：Redis 配额累加后，Kafka 消息丢了 → 配额"虚高"
>
> **兜底**：每天凌晨从 ClickHouse 跑全量 → 修正 Redis 累计值

```sql
-- 每日 00:30 跑
INSERT INTO redis_correction
SELECT tenant_id, sum(total_tokens), 'YYYY-MM'
FROM llm_usage_events
WHERE timestamp >= toStartOfMonth(now())
GROUP BY tenant_id;
```

---

## 六、监控与可观测

```
关键指标：
  - Kafka lag（消息积压）< 1000
  - Flink checkpoint 成功率 = 100%
  - ClickHouse 写入延迟 P99 < 1s
  - Redis 配额查询 P99 < 5ms

业务指标：
  - 全公司日成本（实时）
  - Top 10 高费应用 / 用户
  - 配额超限拒绝率 < 1%
  - 计量误差（明细 vs Redis）< 0.1%
```

---

## 七、可能被追问

| 追问 | 关键答点 |
|------|---------|
| 流式响应怎么计 token？| 监听 stream end 事件，从上游 usage 字段取（权威）|
| Token 数本地估算 vs 上游返回？| 上游 usage 是权威，本地用 tiktoken 估算只用于**前置预算检查** |
| 用户偷偷绕过 Gateway 直连模型？| 模型 API Key 只发给 Gateway，应用不能直连 |
| Kafka 消息重复消费？| event_id 幂等，ClickHouse insert ignore |
| 月底配额跨年怎么处理？| Redis Key 含 yearMonth，Cron 1 号 0 点初始化新月份 |
| 一次调用要不要扣两次（in + out）？| 一次写一条记录，但 cost = in_cost + out_cost 一起算 |

---

## 八、答题加分点

1. **明细 + 聚合 + 实时缓存 三级架构**（行业最佳实践）
2. **ClickHouse + LowCardinality + 月分区 TTL**（具体到字段设计，体现深度）
3. **同步配额检查 + 异步累加**（卡请求 vs 不卡请求的取舍）
4. **每日全量校准**（数据一致性兜底）
5. **价格表配置化**（运营自助改）
6. **Kafka exactly-once + Flink checkpoint**（数据不丢）

---

## 🔗 下一站

- [`./05-Agent编排平台.md`](./05-Agent编排平台.md)
