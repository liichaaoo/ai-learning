# 阶段 ③ · 单 Agent 审查器（先跑通主流程）

> ⏱️ 1.5 天
> 🎯 一个能用的 ReviewAgent——先 work 起来，再优化

---

## 0. 任务清单

- [ ] AiService 接口定义 ReviewAgent
- [ ] System Prompt 教会它"按代码审查规则"
- [ ] 结构化输出 `ReviewComment` 列表
- [ ] 跑通：输入 hunk → 输出评论列表

---

## 1. 结构化输出（关键）

```java
public record ReviewComment(
    String filename,
    int line,                  // diff 中的行号
    Severity severity,
    Category category,
    String message,            // 给开发者看的话
    String suggestion          // 修改建议（可选）
) {}

public enum Severity { BLOCKER, MAJOR, MINOR, INFO }
public enum Category { BUG, SECURITY, PERFORMANCE, STYLE, NAMING, DOCUMENTATION }
```

---

## 2. ReviewAgent 接口

```java
public interface ReviewAgent {

    @SystemMessage("""
            你是一名资深 Java 工程师，做代码审查（Code Review）。
            审查规则（按重要性）：
            1. Bug / NPE 风险（最高）
            2. 安全问题（SQL 注入、敏感信息泄露、越权）
            3. 性能问题（N+1、不必要的循环、资源未释放）
            4. 代码风格（命名、长方法、魔法值）

            规则：
            - 只指出实际问题，不要"为评而评"
            - 给出**具体行号**（基于 diff 中的 + 行）
            - 优先 BLOCKER/MAJOR，少 MINOR/INFO
            - 没问题就返回空数组 []

            输出 JSON 数组，每条评论包含：
            { "filename": "...", "line": N, "severity": "...", "category": "...",
              "message": "...", "suggestion": "..." }
            只输出 JSON，不要其他文字。
            """)
    @UserMessage("""
            文件：{{filename}}

            Diff：
            ```diff
            {{diff}}
            ```

            请审查并输出 JSON 评论数组。
            """)
    List<ReviewComment> review(@V("filename") String filename,
                                @V("diff") String diff);
}
```

---

## 3. Bean 装配

```java
@Configuration
@RequiredArgsConstructor
public class AgentConfig {

    @Bean
    public ReviewAgent reviewAgent(ChatLanguageModel model) {
        return AiServices.builder(ReviewAgent.class)
                .chatLanguageModel(model)
                .build();
    }
}
```

---

## 4. Orchestrator：把流程串起来

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class ReviewOrchestrator {

    private final GitHubApiService github;
    private final DiffSplitter splitter;
    private final PrValidator validator;
    private final ReviewAgent reviewer;
    private final GitHubCommentService commenter;

    @Async                               // ⭐ 异步处理
    public void handleAsync(PrEvent pr) {
        long t0 = System.currentTimeMillis();
        try {
            // ① 拉文件
            var files = github.fetchPrFiles(pr.repoFullName(), pr.number());

            // ② 校验
            var v = validator.validate(files);
            if (!v.ok()) {
                commenter.postSummary(pr, "🤖 跳过审查：" + v.reason());
                return;
            }

            // ③ 切 hunk
            var hunks = splitter.split(files, 200);
            log.info("PR #{}: 切出 {} 个 hunks", pr.number(), hunks.size());

            // ④ 并发审查（每个 hunk 一次 LLM）
            List<ReviewComment> all = hunks.parallelStream()
                    .flatMap(h -> {
                        try {
                            return reviewer.review(h.filename(), h.content()).stream();
                        } catch (Exception e) {
                            log.warn("review fail for {}", h.filename(), e);
                            return Stream.empty();
                        }
                    })
                    .toList();

            // ⑤ 回写评论
            commenter.postReviewComments(pr, all);
            long elapsed = System.currentTimeMillis() - t0;
            commenter.postSummary(pr,
                "🤖 审查完成：%d 条评论，耗时 %.1fs".formatted(all.size(), elapsed / 1000.0));

        } catch (Exception e) {
            log.error("PR #{} review failed", pr.number(), e);
            commenter.postSummary(pr, "🤖 审查失败：" + e.getMessage());
        }
    }
}
```

---

## 5. 测试小技巧

```java
@SpringBootTest
class ReviewAgentTest {

    @Autowired ReviewAgent agent;

    @Test
    void detectNpe() {
        String diff = """
                @@ -10,3 +10,5 @@
                 public String getName(User u) {
                +    String upper = u.getName().toUpperCase();   // 可能 NPE
                +    return upper;
                 }
                """;
        List<ReviewComment> comments = agent.review("User.java", diff);
        assertThat(comments).anyMatch(c ->
            c.severity() == Severity.MAJOR && c.message().toLowerCase().contains("null"));
    }
}
```

---

## 6. 验收

- [ ] 单元测试：能检测出明显的 NPE / SQL 注入
- [ ] 真 PR 走完整流程：拉 diff → 审 → 评论
- [ ] 并发审查不会卡死（控制并发度）
- [ ] 评论数量合理（不超过 20 条/PR）
- [ ] 日志清晰可追踪

---

## 🔗 相关链接

- ⬅️ [阶段 ②](./02-Git与代码拉取.md)
- ➡️ [阶段 ④ · Multi-Agent 审查器](./04-MultiAgent审查器.md)
- ⬆️ [Week 3-4 总览](./README.md)
