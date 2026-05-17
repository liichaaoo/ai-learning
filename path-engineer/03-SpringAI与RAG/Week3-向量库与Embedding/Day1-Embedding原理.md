# Day 1 · Embedding 原理（够用级）

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解"语义向量化"是什么，能用通义 API 把文字变向量并算相似度

---

## 0. 心法（5 分钟）

> **Embedding 就是把一段文字，映射到一个 N 维浮点向量；向量空间里"距离近 = 语义相似"。**

类比：

```
传统数据库：用主键查询  → "WHERE id = 123"
关键词搜索：用倒排索引  → "WHERE content LIKE '%RAG%'"
向量检索：  按语义找相近 → "WHERE 含义 ≈ '检索增强生成'"
```

---

## 1. 一图速记（10 分钟）

```
        "我喜欢吃苹果"  ───►  Embedding 模型  ───►  [0.12, -0.83, 0.55, ..., 0.04]
                                                            ↑
                                                   1024 维向量（举例）

        "我爱吃 apple" ───►  Embedding 模型  ───►  [0.11, -0.82, 0.56, ..., 0.05]
                                                            ↑
                                                   ↘  这两个向量"距离很近"

        "今天股市跌了"  ───►  Embedding 模型  ───►  [-0.50, 0.30, -0.10, ..., 0.20]
                                                            ↑
                                                            ↘  跟前两个"距离远"
```

> 💡 **Embedding 模型在做的事**：让"语义相近的文本"在向量空间里也靠近。

---

## 2. 通义百炼 Embedding 上手（25 分钟）

### 2.1 申请：用 Week 1 那把 API Key

不用重新申请——Week 1 申请的 `DASHSCOPE_API_KEY` 直接能用。

```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY
```

### 2.2 调通义 Embedding API（最简）

新建一个 Java 类（建议放在 `项目/03-doc-search/` 下，今天没建的话先写在任意一个 Spring Boot 工程里）：

```java
package com.demo.docsearch;

import com.alibaba.dashscope.embeddings.TextEmbedding;
import com.alibaba.dashscope.embeddings.TextEmbeddingParam;
import com.alibaba.dashscope.embeddings.TextEmbeddingResult;
import com.alibaba.dashscope.exception.NoApiKeyException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

@Service
public class EmbeddingService {

    @Value("${spring.ai.dashscope.api-key}")
    private String apiKey;

    /** 调用通义 text-embedding-v3，返回 1024 维向量 */
    public List<Double> embed(String text) throws NoApiKeyException {
        TextEmbeddingParam param = TextEmbeddingParam.builder()
                .apiKey(apiKey)
                .model(TextEmbedding.Models.TEXT_EMBEDDING_V3)  // 维度 1024
                .text(text)
                .build();

        TextEmbeddingResult result = new TextEmbedding().call(param);
        // 取第一条文本的向量
        return result.getOutput().getEmbeddings().get(0).getEmbedding();
    }
}
```

### 2.3 余弦相似度（默写题）⭐

向量近不近，用**余弦相似度**衡量：

$$
\text{cos}(\vec{a}, \vec{b}) = \frac{\vec{a} \cdot \vec{b}}{|\vec{a}| \cdot |\vec{b}|}
$$

通俗版：

```
两个向量的点积  ÷  各自模长的乘积   →  范围 [-1, 1]，越大越相似
```

代码：

```java
public static double cosineSimilarity(List<Double> a, List<Double> b) {
    if (a.size() != b.size()) {
        throw new IllegalArgumentException("dim mismatch: " + a.size() + " vs " + b.size());
    }
    double dot = 0, normA = 0, normB = 0;
    for (int i = 0; i < a.size(); i++) {
        dot += a.get(i) * b.get(i);
        normA += a.get(i) * a.get(i);
        normB += b.get(i) * b.get(i);
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
```

### 2.4 实测一下

```java
@SpringBootTest
class EmbeddingServiceTest {

    @Autowired EmbeddingService svc;

    @Test
    void testSimilarity() throws Exception {
        var v1 = svc.embed("我喜欢吃苹果");
        var v2 = svc.embed("我爱吃 apple");
        var v3 = svc.embed("今天股市跌了");

        System.out.println("v1 vs v2 = " + cosineSimilarity(v1, v2));  // 应该 > 0.7
        System.out.println("v1 vs v3 = " + cosineSimilarity(v1, v3));  // 应该 < 0.4
    }
}
```

> 💡 **跑出来你会真切感觉到**："苹果" 和 "apple" 即使一中一英，向量上也很接近——这就是 Embedding 的魔法。

---

## 3. 主流 Embedding 模型对比（10 分钟）

| 模型 | 厂商 | 维度 | 中文表现 | 推荐场景 |
|------|------|------|---------|---------|
| **text-embedding-v3** ⭐ | 阿里通义 | 1024 | 优秀 | **本系列默认** |
| **text-embedding-3-large** | OpenAI | 3072 | 优秀 | 全球项目，需国际信用卡 |
| **text-embedding-3-small** | OpenAI | 1536 | 良好 | 性价比 |
| **bge-m3** ⭐ | 智源（中国）| 1024 | 优秀 | **本地/私有化首选** |
| bge-large-zh-v1.5 | 智源 | 1024 | 优秀 | 纯中文私有化 |
| **m3e-large** | 国内开源 | 1024 | 良好 | 老牌备选 |
| jina-embeddings-v3 | Jina AI | 1024 | 良好 | 多语言 |

> 🎯 **选型建议**：
> - 走 API：通义 `text-embedding-v3`（本系列用这个）
> - 私有化部署：`bge-m3`（HuggingFace 下载，FlagEmbedding 库一键调用）

### 几个工程参数

```
最大输入长度（一次能编码多少 token）：
  通义 v3   ：8192 tokens
  OpenAI v3 ：8191 tokens
  bge-m3    ：8192 tokens

费用（参考 2025 年）：
  通义 v3   ：0.0007 元 / 1k tokens（白菜价）
  OpenAI 3-large ：$0.13 / 1M tokens
```

---

## 4. 为什么是余弦不是欧氏（10 分钟）

> 这是面试高频题。

**欧氏距离**：测两个点的"绝对距离"。
**余弦相似度**：只看两个向量的"方向"，不管"长度"。

```
向量 A = [1, 1]
向量 B = [2, 2]   ← 跟 A 同方向，但长度 2 倍

欧氏距离：sqrt((2-1)² + (2-1)²) = √2 ≈ 1.41   ← 看起来"远"
余弦相似度：cos = 1.0                          ← 方向完全一致 = 完全相似
```

**对 Embedding 来说**：

- 同样含义的句子，向量**方向**应该一致——长度可能因为词数等因素差异
- 所以 **余弦更稳定**

> 🎯 **绝大部分 Embedding 模型，向量都做了 L2 归一化（模长为 1）**——这种情况下余弦相似度 ≡ 点积，二者等价。
>
> Milvus 的 `metric_type` 选 `IP`（内积，归一化后等价于余弦）或 `COSINE` 都可以。

---

## 5. 一段陷阱代码（5 分钟）

```java
// ❌ 错误：把整篇 PDF 一次性 embed
String pdf = readPdf("公司制度.pdf");  // 50 页
var v = svc.embed(pdf);  // 大概率超 token limit + 即使没超效果也很差
```

为什么效果差？**Embedding 模型只能记一个"中心思想"**——把 50 页文档压缩到 1024 维，等于把小说压成一句话，细节全丢。

**正确做法**：分片（chunking），每片 200~500 字符，**Day 5 整合时会做**，**Week 4 详细讲分片策略**。

---

## 6. 检查清单

- [ ] 默写余弦相似度公式
- [ ] 跑通 §2 的 Embedding 调用，输出向量长度 = 1024
- [ ] 跑通相似度测试，看到"语义相近 → 分高"
- [ ] 知道通义 v3 / bge-m3 / OpenAI v3 各自什么场景用
- [ ] 解释为什么是余弦不是欧氏（对面试官）

完成了 ➡️ [Day 2 · Milvus 部署与上手](./Day2-Milvus部署与上手.md)

---

## 🔗 相关链接

- ⬆️ [Week 3 总览](./README.md)
- ➡️ [Day 2 · Milvus 部署与上手](./Day2-Milvus部署与上手.md)
- 📚 [通义 Embedding 文档](https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-api-details)
