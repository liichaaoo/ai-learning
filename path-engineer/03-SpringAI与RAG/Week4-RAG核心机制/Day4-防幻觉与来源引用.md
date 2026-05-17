# Day 4 · 防幻觉与来源引用（让答案"可信"）

> ⏱️ 时间：1.5 小时
> 🎯 目标：让 RAG 答案带"出自 XX.pdf 第 12 页"，且找不到答案时礼貌拒答

---

## 0. 心法（5 分钟）

> **企业 RAG 不是"答得多"而是"答得稳"。**

3 个等级：

| 等级 | 表现 | 适合 |
|------|------|------|
| 🥉 简陋 RAG | 检索到啥就答啥，不管对不对 | 个人玩具 |
| 🥈 进阶 RAG | 答案有来源引用 | 团队工具 |
| 🥇 **生产 RAG** | **来源引用 + 检索不到时拒答 + 一致性校验** | **简历项目应该到这里** |

今天就让你的 RAG 跨到 🥇 等级。

---

## 1. 幻觉 3 大成因 + 对应解法（10 分钟）

| 成因 | 现象 | 解法 |
|------|------|------|
| 检索召回了不相关文档 | 答案张冠李戴 | **相似度阈值** + Reranker |
| 检索到的文档不足以回答 | 模型"补全"——开始编造 | **System Prompt 强约束** + 拒答模板 |
| 上下文太长，关键信息被埋 | 答非所问 | top_k 控制 + Lost-in-Middle 摆放 |

---

## 2. System Prompt 防幻觉模板 ⭐（15 分钟）

> 这是**最简单也最有效**的一招——好的 system prompt 能干翻 80% 的幻觉。

新建 `src/main/resources/prompts/qa-system.st`：

```
你是公司知识库助手，必须严格遵守以下规则：

【规则】
1. 只能基于"参考文档"中的内容回答用户问题。
2. 如果参考文档没有相关信息，直接回答："我没有在公司知识库里找到相关信息，建议联系 HR 或查阅最新文档。"
3. 不要编造文档中不存在的事实、人名、数字、日期。
4. 答案末尾必须列出所引用的文档来源（标注 [来源: 文件名 第N页/章节]）。
5. 用简洁、专业的中文回答。

【参考文档】
{documents}

【用户问题】
{question}

【回答】
```

在 Java 里使用：

```java
@Service
public class RagService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    @Value("classpath:prompts/qa-system.st")
    private Resource qaTemplate;

    public RagService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder.build();
        this.vectorStore = vectorStore;
    }

    public RagAnswer ask(String question) {
        // ① 检索
        List<Document> docs = vectorStore.similaritySearch(
                SearchRequest.query(question)
                        .withTopK(5)
                        .withSimilarityThreshold(0.5)        // ⭐ 阈值过滤
        );

        // ② 检索不到 → 直接拒答（省 token）
        if (docs.isEmpty()) {
            return new RagAnswer("我没有在公司知识库里找到相关信息。", List.of());
        }

        // ③ 拼接文档（带编号，便于引用）
        String docsText = IntStream.range(0, docs.size())
                .mapToObj(i -> {
                    Document d = docs.get(i);
                    return "[%d] 《%s》第%s页：\n%s".formatted(
                            i + 1,
                            d.getMetadata().getOrDefault("source", "未知"),
                            d.getMetadata().getOrDefault("page_number", "?"),
                            d.getContent()
                    );
                })
                .collect(Collectors.joining("\n\n"));

        // ④ 渲染模板
        var prompt = new PromptTemplate(qaTemplate)
                .create(Map.of("documents", docsText, "question", question));

        // ⑤ 调用 LLM
        String answer = chatClient.prompt(prompt).call().content();

        return new RagAnswer(answer, toCitations(docs));
    }

    private List<Citation> toCitations(List<Document> docs) {
        return docs.stream()
                .map(d -> new Citation(
                        d.getId(),
                        (String) d.getMetadata().getOrDefault("source", "未知"),
                        String.valueOf(d.getMetadata().getOrDefault("page_number", "")),
                        d.getContent().substring(0, Math.min(150, d.getContent().length()))
                ))
                .toList();
    }

    public record Citation(String id, String source, String page, String snippet) {}
    public record RagAnswer(String answer, List<Citation> citations) {}
}
```

---

## 3. 相似度阈值：把"凑数"的 chunks 拒之门外（5 分钟）

```java
SearchRequest.query(q)
        .withTopK(5)
        .withSimilarityThreshold(0.5)   // ⭐ 余弦 < 0.5 的全部丢掉
```

**经验取值**：

| 阈值 | 效果 |
|------|------|
| 0.3 | 太松，几乎没过滤 |
| **0.5** | **工程默认** |
| 0.7 | 严格——只放最相关的，可能频繁拒答 |
| > 0.8 | 一般用不到 |

> 💡 **调阈值的方法**：用 Day 2 写的 20 题测试集，扫一遍找最佳值。

---

## 4. 来源引用 ⭐（20 分钟）

> 这是**简历项目最容易出彩**的细节——展示时让面试官看到答案下方一行：「来源：晋升手册.pdf 第 12 页」。

### 4.1 让模型自己输出引用

让模型在回答时**主动标注 [1][2]**，前端再用 metadata 渲染成卡片。

修改 system prompt：

```
回答时请用 [n] 标注引用，n 对应参考文档编号。
例如：晋升流程分三步 [1][2]，自荐需在每年 6 月或 12 月前提交 [1]。
```

返回的 JSON 看起来这样：

```json
{
  "answer": "晋升流程分三步 [1][2]，自荐需在每年 6 月或 12 月前提交 [1]。",
  "citations": [
    {"id": "1", "source": "晋升手册.pdf", "page": "3", "snippet": "晋升流程分三步：自荐..."},
    {"id": "2", "source": "晋升手册.pdf", "page": "5", "snippet": "委员会评审在每..."}
  ]
}
```

### 4.2 前端渲染（提示，不强制做）

```javascript
// 把答案里的 [1] 替换成可点击的角标
const rendered = answer.replace(/\[(\d+)\]/g, (_, n) =>
  `<sup class="cite" data-id="${n}">[${n}]</sup>`
);
```

### 4.3 自定义 Advisor 自动加引用

不想每次手动拼 docs 怎么办？写一个 `CitationAdvisor`：

```java
public class CitationAdvisor implements RequestAdvisor, ResponseAdvisor {
    private final VectorStore vectorStore;

    public CitationAdvisor(VectorStore vs) { this.vectorStore = vs; }

    @Override
    public AdvisedRequest adviseRequest(AdvisedRequest req, Map<String, Object> ctx) {
        var docs = vectorStore.similaritySearch(
                SearchRequest.query(req.userText()).withTopK(5).withSimilarityThreshold(0.5));
        ctx.put("citations_docs", docs);

        if (docs.isEmpty()) {
            return req.withUserText("__NO_DOCS__:" + req.userText());
        }
        String enriched = renderPrompt(req.userText(), docs);
        return req.withUserText(enriched);
    }

    @Override
    public ChatResponse adviseResponse(ChatResponse resp, Map<String, Object> ctx) {
        // 把 docs 塞到 response 元数据里，Controller 还能拿出来
        @SuppressWarnings("unchecked")
        List<Document> docs = (List<Document>) ctx.get("citations_docs");
        resp.getMetadata().put("citations", docs);
        return resp;
    }
    // ... renderPrompt / getName / getOrder 略
}
```

使用：

```java
ChatClient.Builder builder ...
        .defaultAdvisors(new CitationAdvisor(vectorStore))
```

---

## 5. 内容一致性校验（高级技巧，5 分钟）

> **生产 RAG 的最后一道护城河**：让模型自己检查"答案是不是真的来自给定文档"。

```
你刚才的回答是："xxx"
请检查这个回答是否完全来自参考文档。
如果有任何编造内容，列出哪一句不在文档里。
```

实战中 90% 的项目不做（成本高），但**面试时能讲出来**就是亮点：

> "我们用 LLM-as-Judge 做了一个 Reflection 校验层，覆盖关键场景，把幻觉率从 X% 降到 Y%。"

---

## 6. 查询改写：Day 4 的彩蛋（5 分钟）

> 用户问得太短/太口语化时，直接拿去 embed 检索效果差。

简单的 **HyDE / Query Rewrite** 思路：

```java
// 让 LLM 先把短问题改写成详细查询
String detailed = chatClient.prompt()
        .system("把用户的简短问题改写成更详细、便于检索的查询。只输出改写后的查询。")
        .user(question)
        .call()
        .content();

// 用改写后的去检索
var docs = vectorStore.similaritySearch(SearchRequest.query(detailed).withTopK(5));
```

> 💡 **Week 5-6 简历项目可以加这个**——5 分钟代码 + 一句简历亮点：「实现 HyDE 查询改写，长尾问题召回率提升 X%」。

---

## 7. 检查清单

- [ ] 写一份 system prompt，包含"找不到时拒答"的明确规则
- [ ] 加上 `withSimilarityThreshold(0.5)`
- [ ] 答案里能看到 `[1][2]` 标注 + citations 数组
- [ ] 故意问一个"知识库里没有"的问题，验证拒答
- [ ] 自己写一个 `CitationAdvisor`（理解 Advisor 的两个钩子）

完成了 ➡️ [Day 5 · RAG 调优与整合](./Day5-RAG调优与整合.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · Spring AI RAG 组件](./Day3-SpringAI-RAG组件.md)
- ➡️ [Day 5 · RAG 调优与整合](./Day5-RAG调优与整合.md)
- ⬆️ [Week 4 总览](./README.md)
- 📚 [HyDE 论文（Hypothetical Document Embeddings）](https://arxiv.org/abs/2212.10496)
