# 阶段 ④ · Multi-Agent 审查器（升级）

> ⏱️ 1.5 天
> 🎯 把单 Agent 拆成 3 个专家 Agent，提升识别问题的覆盖率

---

## 0. 任务清单

- [ ] 拆分 3 个 Agent：Syntax / Security / Performance
- [ ] 并行执行 + 结果合并去重
- [ ] 每个 Agent 用最匹配的模型（成本路由）
- [ ] 跟单 Agent 对比评测

---

## 1. 三个角色

```java
interface SyntaxReviewer {
    @SystemMessage("""
            你是 Java 语法专家。专注审查：
            - NPE / NullPointerException 风险
            - 异常处理不当（吞异常、过宽 catch）
            - 资源未释放（try-with-resources 缺失）
            - 类型转换错误
            其他类型问题不要提，专注语法。
            """)
    List<ReviewComment> review(@V("filename") String filename, @V("diff") String diff);
}

interface SecurityReviewer {
    @SystemMessage("""
            你是应用安全专家。专注审查：
            - SQL 注入（字符串拼接 SQL）
            - 命令注入（Runtime.exec）
            - 敏感信息泄露（密码、token、密钥写在代码里）
            - 越权访问（缺少权限校验）
            - XSS / CSRF（Web 接口）
            其他问题不要提，专注安全。
            """)
    List<ReviewComment> review(@V("filename") String filename, @V("diff") String diff);
}

interface PerformanceReviewer {
    @SystemMessage("""
            你是性能专家。专注审查：
            - N+1 查询
            - 循环中调用 IO / 数据库
            - 大数据量全量加载
            - 锁滥用 / 死锁风险
            - 缓存策略不当
            其他问题不要提，专注性能。
            """)
    List<ReviewComment> review(@V("filename") String filename, @V("diff") String diff);
}
```

---

## 2. 多模型路由（成本优化）

```java
@Configuration
@RequiredArgsConstructor
public class MultiAgentConfig {

    @Bean("qwenMax") public ChatLanguageModel qwenMax() { /* 贵但准 */ ... }
    @Bean("qwenPlus") public ChatLanguageModel qwenPlus() { /* 便宜 */ ... }

    @Bean
    public SyntaxReviewer syntaxReviewer(@Qualifier("qwenPlus") ChatLanguageModel m) {
        return AiServices.create(SyntaxReviewer.class, m);   // 语法问题简单，用便宜的
    }

    @Bean
    public SecurityReviewer securityReviewer(@Qualifier("qwenMax") ChatLanguageModel m) {
        return AiServices.create(SecurityReviewer.class, m); // 安全要准，用贵的
    }

    @Bean
    public PerformanceReviewer perfReviewer(@Qualifier("qwenMax") ChatLanguageModel m) {
        return AiServices.create(PerformanceReviewer.class, m);
    }
}
```

> 🎯 **简历亮点**：「针对不同审查维度路由不同模型，**月成本节省 ~50%**（语法走便宜模型，安全/性能走顶级模型）」。

---

## 3. 并行 + 去重

```java
@Service
@RequiredArgsConstructor
public class MultiReviewOrchestrator {

    private final SyntaxReviewer syntax;
    private final SecurityReviewer security;
    private final PerformanceReviewer perf;
    private final ExecutorService pool = Executors.newFixedThreadPool(6);

    public List<ReviewComment> reviewHunk(String filename, String diff) {
        // ① 并行调三个 Agent
        var fSyn = CompletableFuture.supplyAsync(() -> safe(() -> syntax.review(filename, diff)), pool);
        var fSec = CompletableFuture.supplyAsync(() -> safe(() -> security.review(filename, diff)), pool);
        var fPerf = CompletableFuture.supplyAsync(() -> safe(() -> perf.review(filename, diff)), pool);

        List<ReviewComment> all = Stream.of(fSyn, fSec, fPerf)
                .map(CompletableFuture::join)
                .flatMap(List::stream)
                .toList();

        // ② 去重（按 filename + line + 关键词）
        return dedupe(all);
    }

    private List<ReviewComment> dedupe(List<ReviewComment> comments) {
        Map<String, ReviewComment> seen = new LinkedHashMap<>();
        for (var c : comments) {
            String key = c.filename() + "#" + c.line() + "#" + c.category();
            // 同位置同类型保留 severity 更高的
            seen.merge(key, c, (a, b) -> a.severity().ordinal() < b.severity().ordinal() ? a : b);
        }
        return new ArrayList<>(seen.values());
    }

    private List<ReviewComment> safe(Supplier<List<ReviewComment>> task) {
        try { return task.get(); } catch (Exception e) { return List.of(); }
    }
}
```

---

## 4. 对比评测（必做，简历数字）

```java
@Test
void compareSingleVsMulti() {
    int singleTotal = 0, multiTotal = 0, singleCorrect = 0, multiCorrect = 0;
    for (PrTestCase tc : loadTestSet()) {
        var single = singleAgent.review(tc.filename(), tc.diff());
        var multi  = multiOrchestrator.reviewHunk(tc.filename(), tc.diff());

        singleTotal += single.size();
        multiTotal  += multi.size();
        singleCorrect += countTruePositives(single, tc.expected());
        multiCorrect  += countTruePositives(multi,  tc.expected());
    }
    System.out.printf("Single: %d/%d (%.1f%%)%n",
        singleCorrect, singleTotal, 100.0 * singleCorrect / singleTotal);
    System.out.printf("Multi:  %d/%d (%.1f%%)%n",
        multiCorrect, multiTotal, 100.0 * multiCorrect / multiTotal);
}
```

预期：

```
Single: 22/40 (55.0%)
Multi:  35/50 (70.0%)   ← 多识别 13 个真问题，准确率提升 15pp
```

---

## 5. 验收

- [ ] 三个 Agent 并行能跑
- [ ] 去重逻辑工作正常
- [ ] 路由：语法→便宜模型，安全/性能→贵模型
- [ ] 对比评测得出数字
- [ ] 简历更新对比数据

---

## 🔗 相关链接

- ⬅️ [阶段 ③](./03-单Agent审查器.md)
- ➡️ [阶段 ⑤ · 评论回写与闭环](./05-评论回写与闭环.md)
- ⬆️ [Week 3-4 总览](./README.md)
