# 阶段 ① · 项目骨架 + Webhook 接入

> ⏱️ 1 天
> 🎯 建好工程地基，能接收 GitHub PR Webhook 并打印事件

---

## 0. 任务清单

- [ ] Maven 骨架：Spring Boot 3 + LangChain4j + JGit + Resilience4j
- [ ] Webhook Endpoint：`POST /webhook/github`
- [ ] 签名校验（防伪造）
- [ ] 事件过滤：只处理 `pull_request` 的 opened/synchronize
- [ ] 异步处理（不阻塞 GitHub）

---

## 1. 关键依赖

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-dashscope-spring-boot-starter</artifactId>
        <version>0.36.2</version>
    </dependency>
    <dependency>
        <groupId>org.eclipse.jgit</groupId>
        <artifactId>org.eclipse.jgit</artifactId>
        <version>6.10.0.202406032230-r</version>
    </dependency>
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot3</artifactId>
        <version>2.2.0</version>
    </dependency>
</dependencies>
```

---

## 2. Webhook Controller

```java
@RestController
@RequestMapping("/webhook")
@RequiredArgsConstructor
@Slf4j
public class GitHubWebhookController {

    @Value("${github.webhook.secret}") private String secret;

    private final ReviewOrchestrator orchestrator;

    @PostMapping("/github")
    public ResponseEntity<String> handle(
            @RequestHeader("X-Hub-Signature-256") String signature,
            @RequestHeader("X-GitHub-Event") String event,
            @RequestBody String payload) {

        // ① 签名校验
        if (!verifySignature(payload, signature, secret)) {
            log.warn("Invalid signature");
            return ResponseEntity.status(401).body("bad signature");
        }

        // ② 事件过滤
        if (!"pull_request".equals(event)) {
            return ResponseEntity.ok("ignored: " + event);
        }

        JsonNode body = parse(payload);
        String action = body.path("action").asText();
        if (!Set.of("opened", "synchronize", "reopened").contains(action)) {
            return ResponseEntity.ok("ignored action: " + action);
        }

        PrEvent pr = PrEvent.fromJson(body);
        log.info("📦 Received PR #{}: {} from {}",
                pr.number(), pr.title(), pr.repoFullName());

        // ③ 异步处理（不让 GitHub 等）
        orchestrator.handleAsync(pr);
        return ResponseEntity.ok("accepted");
    }

    private boolean verifySignature(String payload, String signature, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(), "HmacSHA256"));
            String calc = "sha256=" + HexFormat.of().formatHex(mac.doFinal(payload.getBytes()));
            return MessageDigest.isEqual(calc.getBytes(), signature.getBytes());
        } catch (Exception e) {
            return false;
        }
    }
}
```

---

## 3. PrEvent 模型

```java
public record PrEvent(
    long number,
    String title,
    String body,
    String repoFullName,        // "owner/repo"
    String headSha,
    String baseSha,
    String installationToken    // 可选：GitHub App 模式
) {
    public static PrEvent fromJson(JsonNode n) {
        return new PrEvent(
            n.path("pull_request").path("number").asLong(),
            n.path("pull_request").path("title").asText(),
            n.path("pull_request").path("body").asText(""),
            n.path("repository").path("full_name").asText(),
            n.path("pull_request").path("head").path("sha").asText(),
            n.path("pull_request").path("base").path("sha").asText(),
            null
        );
    }
}
```

---

## 4. 配置

```yaml
github:
  webhook:
    secret: ${GITHUB_WEBHOOK_SECRET}
  token: ${GITHUB_TOKEN}       # PAT 或 GitHub App
```

---

## 5. 本地测试（不用真 GitHub）

用 `smee.io` 把外网 webhook 转发到本机：

```bash
npx smee-client --url https://smee.io/your-channel --target http://localhost:8080/webhook/github
```

或直接 curl 模拟：

```bash
curl -X POST http://localhost:8080/webhook/github \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=xxx" \
  -d @sample-pr-payload.json
```

---

## 6. 验收

- [ ] Webhook 接口 200 OK
- [ ] 签名校验通过（错的签名能 401）
- [ ] 只处理 PR 相关事件
- [ ] 异步处理（响应 < 100ms）
- [ ] 日志能看到 PR # / title / repo

---

## 🔗 相关链接

- ⬆️ [Week 3-4 总览](./README.md)
- ➡️ [阶段 ② · Git 与代码拉取](./02-Git与代码拉取.md)
- 📚 [GitHub Webhook 文档](https://docs.github.com/en/webhooks)
