# 阶段 ② · Git 操作 + 代码拉取

> ⏱️ 1 天
> 🎯 收到 PR 事件后，能拉到 diff + 关键上下文，喂给 LLM

---

## 0. 任务清单

- [ ] 拉取 PR 的 diff（不要全仓库）
- [ ] 解析每个变更文件 + 行号
- [ ] 按 file / hunk 切分
- [ ] 限制超大 PR（> 1000 行警告）

---

## 1. 用 GitHub API 拉 diff（推荐）

不要 clone 整个仓库——**直接调 API 拿 diff**，省时省空间。

```java
@Service
@RequiredArgsConstructor
public class GitHubApiService {

    @Value("${github.token}") private String token;

    private final WebClient client = WebClient.builder()
            .baseUrl("https://api.github.com")
            .build();

    /** 拉取 PR 的 diff（unified format）*/
    public String fetchPrDiff(String repoFullName, long prNumber) {
        return client.get()
                .uri("/repos/{repo}/pulls/{n}", repoFullName, prNumber)
                .header("Authorization", "Bearer " + token)
                .header("Accept", "application/vnd.github.v3.diff")
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }

    /** 拉取 PR 的文件元数据 */
    public List<PrFile> fetchPrFiles(String repoFullName, long prNumber) {
        JsonNode files = client.get()
                .uri("/repos/{repo}/pulls/{n}/files?per_page=100", repoFullName, prNumber)
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(JsonNode.class)
                .block();

        List<PrFile> result = new ArrayList<>();
        for (JsonNode f : files) {
            result.add(new PrFile(
                f.path("filename").asText(),
                f.path("status").asText(),
                f.path("additions").asInt(),
                f.path("deletions").asInt(),
                f.path("patch").asText("")
            ));
        }
        return result;
    }

    public record PrFile(String filename, String status,
                         int additions, int deletions, String patch) {}
}
```

---

## 2. Diff 解析与切分

```java
@Service
public class DiffSplitter {

    /**
     * 把一个 PR 切成多个 "Hunk"：
     * 一个 Hunk = 一个文件的一段连续变更，便于 LLM 单独审查
     */
    public List<Hunk> split(List<GitHubApiService.PrFile> files, int maxLinesPerHunk) {
        List<Hunk> hunks = new ArrayList<>();
        for (var f : files) {
            if (shouldSkip(f.filename())) continue;       // .lock / 二进制等跳过
            if (f.patch() == null || f.patch().isBlank()) continue;

            // 按 GitHub patch 的 @@ 分段
            String[] sections = f.patch().split("(?m)^@@");
            for (String sec : sections) {
                if (sec.isBlank()) continue;
                String text = "@@" + sec;
                if (countLines(text) > maxLinesPerHunk) {
                    // 太长的再细切
                    for (String chunk : splitByLines(text, maxLinesPerHunk)) {
                        hunks.add(new Hunk(f.filename(), chunk));
                    }
                } else {
                    hunks.add(new Hunk(f.filename(), text));
                }
            }
        }
        return hunks;
    }

    private boolean shouldSkip(String filename) {
        return filename.endsWith(".lock")
            || filename.endsWith(".png")
            || filename.contains("node_modules/")
            || filename.startsWith(".github/");
    }

    public record Hunk(String filename, String content) {}
}
```

---

## 3. 大小限制（重要）

```java
@Service
@RequiredArgsConstructor
public class PrValidator {

    @Value("${reviewer.max-changed-files:50}") private int maxFiles;
    @Value("${reviewer.max-changed-lines:2000}") private int maxLines;

    public ValidationResult validate(List<GitHubApiService.PrFile> files) {
        if (files.size() > maxFiles) {
            return ValidationResult.skip(
                "PR 改了 %d 个文件（超过 %d），不审".formatted(files.size(), maxFiles));
        }
        int totalLines = files.stream().mapToInt(f -> f.additions() + f.deletions()).sum();
        if (totalLines > maxLines) {
            return ValidationResult.skip(
                "PR 改了 %d 行（超过 %d），不审".formatted(totalLines, maxLines));
        }
        return ValidationResult.ok();
    }

    public record ValidationResult(boolean ok, String reason) {
        public static ValidationResult ok() { return new ValidationResult(true, null); }
        public static ValidationResult skip(String r) { return new ValidationResult(false, r); }
    }
}
```

---

## 4. 验收

- [ ] 给一个真 PR URL，能拿到 diff
- [ ] 能切分成多个 Hunk
- [ ] 二进制文件 / .lock 文件被跳过
- [ ] 超大 PR（> 50 文件或 > 2000 行）能识别并跳过
- [ ] 日志清晰记录"切了 N 个 hunks"

---

## 🔗 相关链接

- ⬅️ [阶段 ①](./01-项目骨架与Webhook.md)
- ➡️ [阶段 ③ · 单 Agent 审查器](./03-单Agent审查器.md)
- ⬆️ [Week 3-4 总览](./README.md)
