# 04-rag-mini · RAG 最小完整闭环（Week 4 交付物）

> 配套教程：[Week 4 · RAG 核心机制](../../Week4-RAG核心机制/README.md)

---

## 🎯 项目目标

完整 RAG 闭环：**上传文档 → 流式问答 → 来源引用 → 检索不到时礼貌拒答**。

```
本项目 = 03-doc-search（检索）+ ChatModel（生成）+ 防幻觉机制
```

---

## 🛠 技术栈

| 组件 | 用途 |
|------|------|
| Spring Boot 3 + Spring AI 1.0 | 主框架 |
| Spring AI Alibaba | 通义模型 |
| Milvus 2.4 | 向量库 |
| Apache Tika 2.9 | 文档解析（PDF/Word/MD/HTML/PPT 等）|
| 通义 qwen-plus + text-embedding-v3 | LLM + Embedding |

---

## 🚀 快速开始

```bash
docker compose up -d                # 复用 Week 3 的 Milvus
export DASHSCOPE_API_KEY=sk-xxx
./mvnw spring-boot:run

# ① 上传文档
curl -X POST -F "file=@docs/晋升手册.pdf" http://localhost:8080/api/docs

# ② 同步问答
curl -X POST http://localhost:8080/api/chat \
     -H "Content-Type: application/json" \
     -d '{"q":"晋升流程是什么？"}'

# ③ 流式问答（看一字一字蹦出来）
curl -N -X POST http://localhost:8080/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"q":"晋升流程是什么？"}'
```

---

## 📁 期望目录结构

```
04-rag-mini/
├── pom.xml                    （pending：spring-ai-milvus + tika-parsers + lombok）
├── docker-compose.yml
├── README.md
├── docs/                      ← 测试文档
└── src/main/
    ├── java/com/demo/ragmini/
    │   ├── RagMiniApplication.java
    │   ├── controller/RagController.java                    ← Day 5 §2.3
    │   ├── service/
    │   │   ├── DocLoaderService.java                        ← Day 1 §2.2
    │   │   ├── ChunkingService.java                         ← Day 2
    │   │   ├── IndexingPipeline.java                        ← Day 3 §1.2
    │   │   └── RagService.java                              ← Day 5 §2.2
    │   ├── splitter/RecursiveCharacterSplitter.java          ← Day 2 §3.2
    │   └── advisor/CitationAdvisor.java                     ← Day 4 §4.3
    └── resources/
        ├── application.yml                                   ← Day 5 §2.1
        └── prompts/
            └── qa-system.st                                  ← Day 4 §2
```

---

## 📝 进度自检（Week 4 通关线）

- [ ] 上传 PDF 自动解析 + 分片入库（异步可选）
- [ ] 流式问答：一字一字看到输出
- [ ] 答案末尾显示来源引用（含文件名 + 页码）
- [ ] 找不到相关文档时礼貌拒答
- [ ] 多租户：不同 X-Tenant-Id 看到不同范围
- [ ] 跑过对比实验，得出至少 2 组配置的命中率对比
- [ ] 录了 5 分钟演示视频

---

## 🔗 相关链接

- ⬆️ [Week 4 总览](../../Week4-RAG核心机制/README.md)
- 📖 [Day 5 整合教程（含完整代码）](../../Week4-RAG核心机制/Day5-RAG调优与整合.md)
- 📦 [上一项目：03-doc-search](../03-doc-search/)
- 📦 [下一项目：05-rag-knowledge-base](../05-rag-knowledge-base/)
