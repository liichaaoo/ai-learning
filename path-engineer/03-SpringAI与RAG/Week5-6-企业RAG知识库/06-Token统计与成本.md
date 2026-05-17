# 阶段 ⑥ · Token 统计与成本告警

> ⏱️ 1 天
> 🎯 每次 LLM 调用的 token 都被记录、计费、可视化

---

## 0. 任务清单

- [ ] 用 Advisor 拦截每次调用，记 prompt_tokens / completion_tokens
- [ ] 按模型单价计算 cost_yuan，落到 usage_record
- [ ] 接口：`GET /admin/usage?from=...&to=...&groupBy=tenant|model|day`
- [ ] 阈值告警：单租户日消耗 > X 元 触发邮件/Webhook

---

## 1. UsageRecorderAdvisor

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class UsageRecorderAdvisor implements ResponseAdvisor {

    private final UsageRecordRepository repo;
    private final SecurityContextProvider ctx;

    private static final Map<String, double[]> PRICE = Map.of(
            // 元 / 1k tokens
            "qwen-plus",     new double[]{0.0008, 0.002},
            "qwen-max",      new double[]{0.02, 0.06},
            "qwen-turbo",    new double[]{0.0003, 0.0006},
            "gpt-4o",        new double[]{0.025, 0.075},
            "ollama-llama3", new double[]{0.0,   0.0}
    );

    @Override
    public ChatResponse adviseResponse(ChatResponse resp, Map<String, Object> advCtx) {
        Usage usage = resp.getMetadata().getUsage();
        String model = (String) resp.getMetadata().get("model");
        double[] price = PRICE.getOrDefault(model, new double[]{0.001, 0.002});

        BigDecimal cost = BigDecimal.valueOf(
                usage.getPromptTokens() / 1000.0 * price[0]
                        + usage.getGenerationTokens() / 1000.0 * price[1]
        ).setScale(6, RoundingMode.HALF_UP);

        repo.save(UsageRecord.builder()
                .userId(ctx.userId())
                .tenantId(ctx.tenantId())
                .model(model)
                .promptTokens(usage.getPromptTokens())
                .completionTokens(usage.getGenerationTokens())
                .costYuan(cost)
                .createdAt(Instant.now())
                .build());

        log.info("usage: tenant={} model={} cost=¥{}", ctx.tenantId(), model, cost);
        return resp;
    }

    @Override public String getName() { return "usage-recorder"; }
    @Override public int getOrder() { return Integer.MAX_VALUE - 100; }
}
```

---

## 2. 报表接口

```java
@GetMapping("/admin/usage")
@PreAuthorize("hasRole('ADMIN')")
public List<UsageStat> usage(@RequestParam(defaultValue = "tenant") String groupBy,
                              @RequestParam Instant from,
                              @RequestParam Instant to) {
    return switch (groupBy) {
        case "tenant" -> repo.statsByTenant(from, to);
        case "model"  -> repo.statsByModel(from, to);
        case "day"    -> repo.statsByDay(from, to);
        default -> throw new IllegalArgumentException();
    };
}
```

```java
public interface UsageRecordRepository extends JpaRepository<UsageRecord, Long> {
    @Query("""
        SELECT new com.demo.UsageStat(u.tenantId, COUNT(u), SUM(u.promptTokens),
                                      SUM(u.completionTokens), SUM(u.costYuan))
        FROM UsageRecord u WHERE u.createdAt BETWEEN :from AND :to
        GROUP BY u.tenantId
        """)
    List<UsageStat> statsByTenant(Instant from, Instant to);
    // 类似 statsByModel / statsByDay
}
```

---

## 3. 告警

```java
@Component
@RequiredArgsConstructor
public class CostAlertJob {
    private final UsageRecordRepository repo;
    private final NotifyService notifier;

    @Scheduled(cron = "0 0 9 * * *")    // 每天 9 点
    public void checkDailyCost() {
        var yesterday = LocalDate.now().minusDays(1);
        var stats = repo.statsByTenant(
                yesterday.atStartOfDay().toInstant(ZoneOffset.ofHours(8)),
                yesterday.plusDays(1).atStartOfDay().toInstant(ZoneOffset.ofHours(8)));

        for (UsageStat s : stats) {
            if (s.costYuan().compareTo(BigDecimal.valueOf(50)) > 0) {  // 阈值 50 元
                notifier.alert("租户 %s 昨日消耗 ¥%.2f，请关注".formatted(s.tenantId(), s.costYuan()));
            }
        }
    }
}
```

---

## 4. 验收标准

- [ ] 每次提问后 usage_record 多一行
- [ ] `GET /admin/usage?groupBy=tenant&from=...&to=...` 能看到分租户消耗
- [ ] 故意触发阈值能收到通知（邮件/钉钉/Webhook）
- [ ] **简历亮点**：能讲"基于 Advisor 链做 token 计费 + 成本告警"

---

## 🔗 相关链接

- ⬆️ [Week 5-6 总览](./README.md)
- ⬅️ [阶段 ⑤](./05-多模型路由.md)
- ➡️ [阶段 ⑦ · 评测与调优](./07-评测与调优.md)
