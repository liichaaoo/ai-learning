# Day 2 · 分片策略（RAG 效果的决定性因素）⭐

> ⏱️ 时间：2 小时（多花一点值）
> 🎯 目标：理解三种主流分片策略，能根据文档类型做出选择

---

## 0. 心法（5 分钟）

> **分片不好，神仙也救不了 RAG。**

为什么分片这么重要？

- 分太大 → 一个 chunk 含多个主题，检索时**召回模糊**
- 分太小 → 上下文不够，**回答片面**
- 切错地方 → 句子断头、表格被劈、代码被拆

**分片的目标**：每个 chunk **语义自洽**，**长度可控**，**保留上下文**。

---

## 1. 三种主流策略 ⭐（10 分钟）

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ① 按 Token 切（Token-based）                                   │
│     最简单：每 N 个 token 切一刀                                │
│     优点：可控、跟模型 context window 对齐                      │
│     缺点：句子可能被截断                                        │
│     适合：长文档、技术文章                                      │
│                                                                 │
│  ② 按结构切（Structure-based）                                  │
│     按段落 / 标题 / 章节切                                      │
│     优点：语义完整                                              │
│     缺点：长度不均（有的 50 字、有的 5000 字）                  │
│     适合：Markdown / Word                                       │
│                                                                 │
│  ③ 按语义切（Semantic-based）                                   │
│     用 Embedding 找"语义边界"                                   │
│     优点：最聪明                                                │
│     缺点：贵、慢（每句要 embed 一次）                           │
│     适合：高价值文档（合同 / 论文）                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> 🎯 **工程默认**：**①+②混合**——先按结构切粗的，再按 token 切细的，最后保留 overlap。

---

## 2. Spring AI 内置 Splitter（20 分钟）

### 2.1 `TokenTextSplitter`（最常用）

```java
import org.springframework.ai.transformer.splitter.TokenTextSplitter;

@Service
public class ChunkingService {

    /** Spring AI 默认实现 */
    public List<Document> splitByToken(List<Document> raw) {
        TokenTextSplitter splitter = new TokenTextSplitter(
                500,        // chunkSize（约多少 token）
                100,        // minChunkSizeChars（最小字符数，避免太碎）
                10,         // minChunkLengthToEmbed（embed 阈值）
                5000,       // maxNumChunks
                true        // keepSeparator
        );
        return splitter.apply(raw);
    }
}
```

**默认参数（默认构造函数 `new TokenTextSplitter()`）**：

```
chunkSize = 800
minChunkSizeChars = 350
minChunkLengthToEmbed = 5
maxNumChunks = 10000
keepSeparator = true
```

> 💡 **本系列推荐**：`chunkSize=500, overlap≈100` —— 给一会儿讲的"递归 splitter"用。

### 2.2 Markdown 专用：`MarkdownDocumentReader`

它内部已经按 `#`、`##`、`段落` 自动切了——**MD 文档基本不用再写 splitter**。

### 2.3 自己写一个"按段落切"

```java
public List<Document> splitByParagraph(Document raw, int maxChars) {
    String content = raw.getContent();
    List<Document> chunks = new ArrayList<>();

    StringBuilder buf = new StringBuilder();
    for (String para : content.split("\n\n+")) {
        if (buf.length() + para.length() > maxChars && buf.length() > 0) {
            chunks.add(new Document(buf.toString(), new HashMap<>(raw.getMetadata())));
            buf.setLength(0);
        }
        if (buf.length() > 0) buf.append("\n\n");
        buf.append(para);
    }
    if (buf.length() > 0) {
        chunks.add(new Document(buf.toString(), new HashMap<>(raw.getMetadata())));
    }
    return chunks;
}
```

---

## 3. Recursive Character Splitter（推荐）⭐（25 分钟）

> LangChain 的 `RecursiveCharacterTextSplitter` 是工业界事实标准。Spring AI 没内置，**我们自己写一个**。

### 3.1 算法直觉

```
分隔符优先级（从粗到细）：
  ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]

递归过程：
  1. 用最粗的分隔符（"\n\n"）切
  2. 如果某个 chunk 仍然超 max_size：
       用次粗的（"\n"）继续切
  3. 继续递归直到所有 chunk ≤ max_size
  4. 最后做 overlap 重叠
```

### 3.2 Java 实现

```java
public class RecursiveCharacterSplitter {

    private final int chunkSize;
    private final int chunkOverlap;
    private final List<String> separators;

    public RecursiveCharacterSplitter(int chunkSize, int chunkOverlap) {
        this.chunkSize = chunkSize;
        this.chunkOverlap = chunkOverlap;
        this.separators = List.of("\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", "");
    }

    public List<String> split(String text) {
        List<String> finalChunks = new ArrayList<>();
        recurse(text, separators, finalChunks);
        return mergeWithOverlap(finalChunks);
    }

    private void recurse(String text, List<String> seps, List<String> result) {
        if (text.length() <= chunkSize) {
            if (!text.isBlank()) result.add(text);
            return;
        }
        if (seps.isEmpty()) {
            // 实在切不开，硬切
            for (int i = 0; i < text.length(); i += chunkSize) {
                result.add(text.substring(i, Math.min(text.length(), i + chunkSize)));
            }
            return;
        }
        String sep = seps.get(0);
        List<String> remaining = seps.subList(1, seps.size());

        if (sep.isEmpty()) {
            // 兜底：硬切
            for (int i = 0; i < text.length(); i += chunkSize) {
                result.add(text.substring(i, Math.min(text.length(), i + chunkSize)));
            }
            return;
        }

        String[] parts = text.split(java.util.regex.Pattern.quote(sep), -1);
        StringBuilder buf = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            String p = parts[i] + (i < parts.length - 1 ? sep : "");
            if (buf.length() + p.length() <= chunkSize) {
                buf.append(p);
            } else {
                if (buf.length() > 0) {
                    if (buf.length() <= chunkSize) result.add(buf.toString());
                    else recurse(buf.toString(), remaining, result);
                    buf.setLength(0);
                }
                if (p.length() > chunkSize) {
                    recurse(p, remaining, result);
                } else {
                    buf.append(p);
                }
            }
        }
        if (buf.length() > 0) {
            if (buf.length() <= chunkSize) result.add(buf.toString());
            else recurse(buf.toString(), remaining, result);
        }
    }

    /** 给相邻 chunk 加重叠 */
    private List<String> mergeWithOverlap(List<String> chunks) {
        if (chunkOverlap <= 0 || chunks.size() < 2) return chunks;
        List<String> merged = new ArrayList<>(chunks.size());
        merged.add(chunks.get(0));
        for (int i = 1; i < chunks.size(); i++) {
            String prev = chunks.get(i - 1);
            String tail = prev.length() > chunkOverlap
                    ? prev.substring(prev.length() - chunkOverlap)
                    : prev;
            merged.add(tail + chunks.get(i));
        }
        return merged;
    }
}
```

> 🎯 **生产推荐**：把这个 splitter 抽成 util，**整个简历项目都用它**。

### 3.3 跑一下

```java
@Test
void test() {
    String text = """
            # 公司晋升流程

            晋升流程分三步：

            1. 自荐 / 主管推荐
            2. 述职会答辩
            3. 委员会评审

            ## 详细规则

            自荐需在每年 6 月或 12 月前提交，附带：
            - 业绩自评
            - 主管反馈
            - 协作方评价
            """;

    var splitter = new RecursiveCharacterSplitter(80, 20);
    splitter.split(text).forEach(c -> System.out.println("─── " + c.length() + " 字 ───\n" + c));
}
```

观察输出：每段大致 80 字以内，相邻段有 20 字重叠，**句子不会断头**。

---

## 4. chunk_overlap 的取值经验（10 分钟）

| chunk_size | 推荐 overlap | 比例 | 备注 |
|-----------|--------------|------|------|
| 200 | 20-40 | 10-20% | 短文本 / FAQ |
| **500** | **50-100** | **10-20%** | **本系列默认** |
| 1000 | 100-200 | 10-20% | 长文档 |
| 2000+ | 200-400 | 10-20% | 大模型长 context |

> 💡 **经验法则**：**overlap ≈ 10-20% × chunk_size**，过大浪费存储，过小防不了断头。

---

## 5. 不同文档类型的"分片心法"（10 分钟）

| 文档类型 | 推荐策略 | chunk_size | 备注 |
|---------|---------|-----------|------|
| **技术文档/手册** | RecursiveCharacter | 500 | 通用首选 |
| **Markdown** | MarkdownDocumentReader | — | 按 `##` 切，自带语义 |
| **PDF（多栏论文）** | PagePdfDocumentReader + Recursive | 800 | 保留 page_number |
| **代码** | 按函数 / 类切 | — | 别切碎，否则丢上下文 |
| **法律合同** | 按条款切 + Semantic | 1000 | 高价值，值得 Semantic |
| **聊天记录** | 按对话轮次切 | — | 保留发言人 |
| **HTML 网页** | Jsoup 提正文 + Recursive | 500 | 先去噪 |
| **PPT** | 每页一个 chunk | — | 通常很短 |

---

## 6. 评测：分片好不好怎么知道（15 分钟）

> 这一节是**简历项目"准确率提升"数字的来源**——本周末做一遍。

### 6.1 准备一份小测试集

人工写 20 条"问题 + 期望答案出处"：

```yaml
- question: "公司晋升流程分几步？"
  expected_source: "晋升手册.pdf"
  expected_keywords: ["三步", "自荐", "述职"]

- question: "去年的 OKR 评分怎么算的？"
  expected_source: "OKR制度.pdf"
  expected_keywords: ["季度", "权重", "P0"]

# ... 共 20 条
```

### 6.2 实验：扫一组分片参数

```java
@Test
void compareChunking() {
    int[][] configs = {
            {300, 30}, {500, 50}, {500, 100},
            {800, 100}, {1000, 200}
    };
    for (int[] c : configs) {
        cleanIndex();
        rebuildIndex(c[0], c[1]);    // 用不同参数重建索引
        double recall = evaluate();   // 跑测试集，看 Top-3 命中率
        System.out.printf("size=%d overlap=%d → Recall@3 = %.2f%n", c[0], c[1], recall);
    }
}
```

预期输出：

```
size=300 overlap=30  → Recall@3 = 0.65
size=500 overlap=50  → Recall@3 = 0.85   ← 工程默认
size=500 overlap=100 → Recall@3 = 0.90   ← 推荐
size=800 overlap=100 → Recall@3 = 0.80
size=1000 overlap=200 → Recall@3 = 0.75
```

> 🎯 **简历叙述**：「通过分片参数对比实验（500/100），将 Top-3 召回率从 65% 提升至 90%」 —— 比"提升 RAG 效果"高级 100 倍。

---

## 7. 检查清单

- [ ] 默写三种分片策略 + 各自适合场景
- [ ] 用 `TokenTextSplitter` 跑一遍（看 chunk 数量）
- [ ] 自己实现 `RecursiveCharacterSplitter`（一定要敲一遍，**别复制**）
- [ ] 解释 chunk_overlap 是什么 + 推荐取值
- [ ] **写下你的 20 条测试问题**（Week 5-6 要复用）

完成了 ➡️ [Day 3 · Spring AI RAG 组件](./Day3-SpringAI-RAG组件.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · 文档加载与解析](./Day1-文档加载与解析.md)
- ➡️ [Day 3 · Spring AI RAG 组件](./Day3-SpringAI-RAG组件.md)
- ⬆️ [Week 4 总览](./README.md)
- 📚 [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/how_to/recursive_text_splitter/)（Python 但思路通用）
