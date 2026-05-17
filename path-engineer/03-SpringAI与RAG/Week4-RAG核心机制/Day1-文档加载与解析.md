# Day 1 · 文档加载与解析（让系统能"吃"任意格式）

> ⏱️ 时间：1.5 小时
> 🎯 目标：PDF / Word / Markdown / HTML 都能读进来，统一成纯文本

---

## 0. 心法（5 分钟）

> **RAG 的第一公里是"把文档变成纯文本字符串"——这一步丑活多。**

听起来像 IO，其实坑很多：

```
PDF：扫描件 vs 原生文本 vs 表格 vs 多栏
Word：.doc vs .docx，公式 / 图片 / 批注
Markdown：代码块 / 表格 / front-matter
HTML：脚本 / 样式 / 导航栏（噪声）
PPT：每页图多文字少
```

---

## 1. 工具选型（10 分钟）

| 格式 | 推荐工具 | 备注 |
|------|---------|------|
| **PDF** | **Apache PDFBox** ⭐ / Spring AI `PdfDocumentReader` | 扫描件需要 OCR（不在本周范围）|
| **Word .docx** | Apache POI | 老的 .doc 用 HWPF |
| **Markdown** | 直接读字符串 + 自己处理 front-matter | 最省心 |
| **HTML** | **Jsoup** ⭐ | 能去掉 nav/script |
| **All-in-one** | **Apache Tika** ⭐⭐⭐ | 100+ 格式，**强烈推荐**|
| **网页抓取** | Jsoup + 你自己的爬虫 | 不展开 |

> 🎯 **本系列推荐**：**用 Tika 兜底 + 关键格式（PDF / MD）做精细处理**。

---

## 2. Tika 一招吃所有（25 分钟）

### 2.1 加依赖

```xml
<!-- 一站式文档解析 -->
<dependency>
    <groupId>org.apache.tika</groupId>
    <artifactId>tika-core</artifactId>
    <version>2.9.2</version>
</dependency>
<dependency>
    <groupId>org.apache.tika</groupId>
    <artifactId>tika-parsers-standard-package</artifactId>
    <version>2.9.2</version>
</dependency>

<!-- Spring AI 也内置了 Reader，可以两手准备 -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-tika-document-reader</artifactId>
</dependency>
```

### 2.2 一段万能代码

```java
package com.demo.ragmini.service;

import org.apache.tika.Tika;
import org.apache.tika.exception.TikaException;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.AutoDetectParser;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.sax.BodyContentHandler;
import org.springframework.stereotype.Service;
import org.xml.sax.SAXException;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

@Service
public class DocLoaderService {

    private final Tika tika = new Tika();

    /** 简版：只要文本 */
    public String loadAsText(Path file) throws IOException {
        try (InputStream in = Files.newInputStream(file)) {
            return tika.parseToString(in);
        } catch (TikaException e) {
            throw new IOException("parse fail: " + file, e);
        }
    }

    /** 高级版：拿文本 + 元数据（页数、作者、创建时间……）*/
    public ParsedDoc loadWithMetadata(Path file) throws IOException, TikaException, SAXException {
        // -1 表示不限大小，生产环境建议给个上限
        BodyContentHandler handler = new BodyContentHandler(-1);
        Metadata metadata = new Metadata();

        try (InputStream in = Files.newInputStream(file)) {
            new AutoDetectParser().parse(in, handler, metadata, new ParseContext());
        }

        Map<String, String> meta = new HashMap<>();
        for (String name : metadata.names()) {
            meta.put(name, metadata.get(name));
        }
        return new ParsedDoc(handler.toString(), meta);
    }

    public record ParsedDoc(String content, Map<String, String> metadata) {}
}
```

> 💡 跑一下：

```java
@Test
void testLoad() throws Exception {
    var doc = loaderService.loadWithMetadata(Path.of("docs/晋升手册.pdf"));
    System.out.println("=== 元数据 ===");
    doc.metadata().forEach((k, v) -> System.out.println(k + " = " + v));
    System.out.println("=== 正文前 300 字 ===");
    System.out.println(doc.content().substring(0, Math.min(300, doc.content().length())));
}
```

预期输出（PDF 例）：

```
=== 元数据 ===
Content-Type = application/pdf
xmpTPg:NPages = 24
dc:title = 晋升手册 v3
... 几十条
=== 正文前 300 字 ===
公司晋升体系采用 6 级 / 12 段 ...
```

> 🎯 **`xmpTPg:NPages` 这种字段就是 RAG 项目里能塞进 metadata 的"宝贝"**——后面 Week 5-6 简历项目里"答案带页码"就靠它。

---

## 3. Spring AI 内置 Reader（15 分钟）

Spring AI 已经把常见 Reader 封装好了，**和 VectorStore 无缝串联**。

### 3.1 核心接口

```java
public interface DocumentReader extends Supplier<List<Document>> {
    @Override
    List<Document> get();
}
```

### 3.2 几个开箱即用的实现

| 类 | 用途 |
|----|------|
| `TikaDocumentReader` | 万能（基于 Tika）⭐ |
| `PagePdfDocumentReader` | PDF，按页切 |
| `JsonReader` | 结构化 JSON |
| `MarkdownDocumentReader` | Markdown，自动按 # 切章节 |

### 3.3 一段标准用法

```java
import org.springframework.ai.reader.tika.TikaDocumentReader;

@Service
public class SpringAiLoaderService {

    public List<Document> load(Resource resource) {
        TikaDocumentReader reader = new TikaDocumentReader(resource);
        return reader.get();
    }
}
```

```java
@Test
void load() {
    var resource = new FileSystemResource("docs/晋升手册.pdf");
    var docs = service.load(resource);
    docs.forEach(d -> System.out.println(
        "[" + d.getMetadata() + "] " + d.getContent().substring(0, 80) + "..."
    ));
}
```

> 💡 注意：默认 `TikaDocumentReader` **整篇文档当一个 Document 返回**——分片是 Day 2 的事。

### 3.4 Reader / Splitter / VectorStore 的角色分工

```
┌─────────────────────────────────────────────────────────────┐
│   File / URL                                                │
│        │                                                    │
│        ▼                                                    │
│  DocumentReader      （Day 1：拆出文本 + 元数据）            │
│        │                                                    │
│        ▼                                                    │
│  List<Document>      每个 Document = 一整篇                 │
│        │                                                    │
│        ▼                                                    │
│  TextSplitter        （Day 2：切成小块）                    │
│        │                                                    │
│        ▼                                                    │
│  List<Document>      每个 Document = 一个 chunk             │
│        │                                                    │
│        ▼                                                    │
│  VectorStore.add()   （Week 3：向量化 + 入库）              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. PDF 进阶：保留页码（15 分钟）

简历项目里"答案附带页码"是高级感。Spring AI 的 `PagePdfDocumentReader` 帮你做到。

```java
import org.springframework.ai.reader.pdf.PagePdfDocumentReader;
import org.springframework.ai.reader.pdf.config.PdfDocumentReaderConfig;
import org.springframework.ai.reader.ExtractedTextFormatter;

public List<Document> loadPdfPerPage(Resource resource) {
    PdfDocumentReaderConfig config = PdfDocumentReaderConfig.builder()
            .withPageTopMargin(0)
            .withPageExtractedTextFormatter(ExtractedTextFormatter.builder()
                    .withNumberOfTopTextLinesToDelete(0)
                    .build())
            .withPagesPerDocument(1)        // ⭐ 每页一个 Document
            .build();

    return new PagePdfDocumentReader(resource, config).get();
}
```

每个返回的 Document 自带 `page_number` 元数据：

```java
docs.forEach(d -> System.out.println(
    "page=" + d.getMetadata().get("page_number") + ", len=" + d.getContent().length()
));
// 输出：page=1, len=523
//       page=2, len=611
//       ...
```

> 🎯 **Week 5-6 简历项目要点**：「答案末尾自动附「来自 XX.pdf 第 12 页」」 —— 就是用这个 `page_number`。

---

## 5. 网页抓取（5 分钟）

```java
@Service
public class WebLoaderService {

    public Document loadFromUrl(String url) throws IOException {
        org.jsoup.nodes.Document html = Jsoup.connect(url).get();
        // 干掉 nav / script / style 等噪声
        html.select("nav, script, style, footer, aside").remove();
        String text = html.body().text();

        return new Document(text, Map.of(
                "source", url,
                "title", html.title()
        ));
    }
}
```

---

## 6. 常见坑速查

| 坑 | 原因 | 解法 |
|----|------|------|
| PDF 解析后**全是空白** | 扫描件（图片）| 先 OCR（PaddleOCR / Azure OCR）再解析 |
| Word 表格内容**串行了** | Tika 默认按段落 | 用 POI 单独处理表格 |
| Markdown 里**代码块被分散** | 普通 splitter 不识别 | 用 `MarkdownDocumentReader` |
| 网页**充满导航文字** | 没去噪 | Jsoup `select(...).remove()` |
| 中文 PDF **乱码** | 字体嵌入问题 | 升级 PDFBox 到 2.0.30+ |
| 大文件 OOM | 默认全读到内存 | Tika 流式 + 分页处理 |

---

## 7. 检查清单

- [ ] 用 Tika 解析至少 3 种格式：PDF / Word / MD
- [ ] 用 `PagePdfDocumentReader` 让 PDF 保留 `page_number`
- [ ] 解释 Reader / Splitter / VectorStore 的分工
- [ ] 知道扫描件 PDF 需要先 OCR
- [ ] 跑通 `WebLoaderService`（任选一个新闻页）

完成了 ➡️ [Day 2 · 分片策略](./Day2-分片策略.md)

---

## 🔗 相关链接

- ⬆️ [Week 4 总览](./README.md)
- ➡️ [Day 2 · 分片策略](./Day2-分片策略.md)
- 📚 [Apache Tika 文档](https://tika.apache.org/)
- 📚 [Spring AI Document Readers](https://docs.spring.io/spring-ai/reference/api/etl-pipeline.html)
