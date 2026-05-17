# Day 2 · Milvus 部署 + Java SDK 上手

> ⏱️ 时间：1.5 小时
> 🎯 目标：本地一键起 Milvus，用 Java SDK 跑通"建库 → 写入 → 查询 → 删除"

---

## 0. 心法（5 分钟）

> **Milvus 是向量界的 MySQL**——你已有的 ORM/SQL 直觉大部分能迁移过来。

```
MySQL 概念       Milvus 对应
─────────────────────────────────────
Database     →   Database
Table        →   Collection            （表 = 集合）
Row          →   Entity（含 vector 字段）
Column       →   Field
Index        →   Vector Index（IVF_FLAT / HNSW）
Partition    →   Partition
```

唯一新东西：**vector 字段必须建索引**才能高效查询，索引算法跟 B+Tree 不一样。

---

## 1. 一键起本地 Milvus（15 分钟）

### 1.1 用 Docker Compose（推荐）

新建 `docker-compose.yml`（建议放在 `项目/03-doc-search/` 目录）：

```yaml
# 来源：Milvus 官方 standalone 版（单机）
version: '3.5'

services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - ./volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ./volumes/minio:/minio_data
    command: minio server /minio_data

  milvus:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.4.10
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ./volumes/milvus:/var/lib/milvus
    ports:
      - "19530:19530"   # gRPC（Java SDK 用）
      - "9091:9091"     # HTTP / 健康检查
    depends_on:
      - etcd
      - minio
```

启动：

```bash
docker compose up -d

# 看日志
docker compose logs -f milvus
# 看到 "Milvus Proxy successfully started" 就 OK
```

### 1.2 验证：用 Attu 可视化（强烈推荐）

```bash
docker run -d --name attu \
  -p 8000:3000 \
  -e MILVUS_URL=host.docker.internal:19530 \
  zilliz/attu:v2.4
```

打开 [http://localhost:8000](http://localhost:8000) → 连接 → 你将拥有一个"Milvus 版的 Navicat"。

> 💡 整周建议**让 Attu 一直开着**，每次写完代码就能看到数据写没写进去。

---

## 2. Java SDK 上手（35 分钟）

### 2.1 加依赖（Maven）

```xml
<dependency>
    <groupId>io.milvus</groupId>
    <artifactId>milvus-sdk-java</artifactId>
    <version>2.4.4</version>
</dependency>
```

### 2.2 配置 `application.yml`

```yaml
milvus:
  host: localhost
  port: 19530

# Day 1 已有的通义 key
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
```

### 2.3 一份"全套增删改查"代码（背模板）

```java
package com.demo.docsearch.config;

import io.milvus.client.MilvusServiceClient;
import io.milvus.param.ConnectParam;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MilvusConfig {
    @Value("${milvus.host}") String host;
    @Value("${milvus.port}") int port;

    @Bean
    public MilvusServiceClient milvusClient() {
        return new MilvusServiceClient(
                ConnectParam.newBuilder().withHost(host).withPort(port).build()
        );
    }
}
```

```java
package com.demo.docsearch.service;

import io.milvus.client.MilvusServiceClient;
import io.milvus.grpc.DataType;
import io.milvus.grpc.SearchResults;
import io.milvus.param.IndexType;
import io.milvus.param.MetricType;
import io.milvus.param.collection.*;
import io.milvus.param.dml.*;
import io.milvus.param.index.CreateIndexParam;
import io.milvus.response.SearchResultsWrapper;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.*;

@Service
public class MilvusDemoService {

    private static final String COLLECTION = "docs_demo";
    private static final int DIM = 1024;            // ⚠️ 跟 Embedding 模型对齐
    private final MilvusServiceClient client;

    public MilvusDemoService(MilvusServiceClient client) { this.client = client; }

    /** ① 建 Collection（应用启动时确保存在） */
    @PostConstruct
    public void ensureCollection() {
        boolean exists = client.hasCollection(
                HasCollectionParam.newBuilder().withCollectionName(COLLECTION).build()
        ).getData();
        if (exists) return;

        FieldType id = FieldType.newBuilder()
                .withName("id").withDataType(DataType.Int64)
                .withPrimaryKey(true).withAutoID(true).build();

        FieldType content = FieldType.newBuilder()
                .withName("content").withDataType(DataType.VarChar)
                .withMaxLength(2000).build();

        FieldType vector = FieldType.newBuilder()
                .withName("vector").withDataType(DataType.FloatVector)
                .withDimension(DIM).build();

        CreateCollectionParam createParam = CreateCollectionParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withFieldTypes(List.of(id, content, vector))
                .build();

        client.createCollection(createParam);

        // ② 给 vector 字段建索引（必须，否则查询超慢）
        client.createIndex(CreateIndexParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withFieldName("vector")
                .withIndexType(IndexType.HNSW)              // 工业界主流
                .withMetricType(MetricType.COSINE)          // 余弦相似度
                .withExtraParam("{\"M\":16,\"efConstruction\":200}")
                .build());

        // ③ 加载到内存（不 load 不能查）
        client.loadCollection(
                LoadCollectionParam.newBuilder().withCollectionName(COLLECTION).build()
        );
    }

    /** ④ 写入 */
    public void insert(String text, List<Float> vec) {
        InsertParam param = InsertParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withFields(List.of(
                        new InsertParam.Field("content", List.of(text)),
                        new InsertParam.Field("vector",  List.of(vec))
                ))
                .build();
        client.insert(param);
    }

    /** ⑤ 查询：返回 topK 相似的 content + 分数 */
    public List<Map<String, Object>> search(List<Float> queryVec, int topK) {
        SearchParam param = SearchParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withMetricType(MetricType.COSINE)
                .withOutFields(List.of("content"))
                .withTopK(topK)
                .withVectors(List.of(queryVec))
                .withVectorFieldName("vector")
                .build();

        SearchResults resp = client.search(param).getData();
        SearchResultsWrapper w = new SearchResultsWrapper(resp.getResults());

        List<Map<String, Object>> hits = new ArrayList<>();
        for (int i = 0; i < topK; i++) {
            try {
                String content = (String) w.getFieldData("content", 0).get(i);
                float score = w.getIDScore(0).get(i).getScore();
                hits.add(Map.of("content", content, "score", score));
            } catch (Exception ignore) {}
        }
        return hits;
    }

    /** ⑥ 删除（按 id） */
    public void deleteById(long id) {
        client.delete(DeleteParam.newBuilder()
                .withCollectionName(COLLECTION)
                .withExpr("id == " + id)
                .build());
    }
}
```

### 2.4 写个 Controller 验证

```java
@RestController
@RequiredArgsConstructor
public class MilvusTestController {
    private final EmbeddingService embeddingService;
    private final MilvusDemoService milvusService;

    @PostMapping("/test/insert")
    public String insert(@RequestParam String text) throws Exception {
        var vec = embeddingService.embedFloat(text);   // 注意转 Float
        milvusService.insert(text, vec);
        return "OK";
    }

    @GetMapping("/test/search")
    public List<Map<String, Object>> search(@RequestParam String q) throws Exception {
        var vec = embeddingService.embedFloat(q);
        return milvusService.search(vec, 3);
    }
}
```

> 💡 **注意**：通义 SDK 默认返回 `List<Double>`，Milvus Java SDK 要 `List<Float>`，做一次类型转换：
>
> ```java
> public List<Float> embedFloat(String text) throws Exception {
>     return embed(text).stream().map(Double::floatValue).toList();
> }
> ```

### 2.5 跑一遍

```bash
# 写入几条
curl -X POST "http://localhost:8080/test/insert?text=苹果是一种水果"
curl -X POST "http://localhost:8080/test/insert?text=Apple 公司发布新 iPhone"
curl -X POST "http://localhost:8080/test/insert?text=今天股市大跌"

# 查询
curl "http://localhost:8080/test/search?q=我想吃水果"
# 期望第 1 条：苹果是一种水果（分数最高）
```

打开 Attu 看看，应该能看到 3 条数据 + HNSW 索引建好了。

---

## 3. 索引算法浅尝辄止（10 分钟）

> 不需要会推导，但**面试可能被问**。

| 索引类型 | 一句话原理 | 速度 | 召回 | 内存 | 用在哪 |
|---------|-----------|------|------|------|--------|
| **FLAT** | 暴力扫描，全部算一遍 | 慢 | 100% | 低 | 数据量 < 1 万 |
| **IVF_FLAT** | 先聚类，只查最近的几桶 | 中 | 95%+ | 中 | 100 万级 |
| **HNSW** ⭐ | 多层图，邻居跳着找 | **快** | 95%+ | **高** | **生产首选** |
| IVF_PQ | IVF + 量化压缩 | 快 | 90% | 低 | 上亿条但内存紧 |

> 🎯 **本系列默认 HNSW**——在我们百万级以下的场景里没有理由不用它。

### HNSW 两个关键参数

```
M = 16             每个节点连多少个邻居（越大越准但越慢）
efConstruction = 200    建索引时探索的邻居数（越大建索引越慢但质量越高）
ef（查询时） = 64    查询时探索的邻居数（越大越准但越慢）
```

**一行经验值**：M=16, efConstruction=200, ef=64——**绝大部分场景的工程默认**。

---

## 4. Milvus 部署形态对比（5 分钟）

| 形态 | 用法 | 适合 |
|------|------|------|
| **Lite**（嵌入式）| 单进程，无需 Docker | 学习 / 单元测试 |
| **Standalone** ⭐ | 单容器，本周用这个 | **学习 / 小规模生产** |
| Cluster（分布式）| 多节点，K8s 部署 | 上亿数据 / 高可用 |
| **Zilliz Cloud** | 托管 SaaS | 不想运维就用这个 |

---

## 5. 检查清单

- [ ] `docker compose up -d` 起来，`docker ps` 能看到 milvus / etcd / minio
- [ ] Attu 能连上 localhost:19530
- [ ] Java SDK 跑通 ensureCollection、insert、search
- [ ] 解释 Collection / Field / Index / Partition 各对应 MySQL 什么概念
- [ ] 默写 HNSW 三参数（M / efConstruction / ef）

完成了 ➡️ [Day 3 · Spring AI VectorStore](./Day3-SpringAI-VectorStore.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · Embedding 原理](./Day1-Embedding原理.md)
- ➡️ [Day 3 · Spring AI VectorStore](./Day3-SpringAI-VectorStore.md)
- ⬆️ [Week 3 总览](./README.md)
- 📚 [Milvus Standalone 文档](https://milvus.io/docs/install_standalone-docker.md)
- 🛠️ [Attu GUI](https://github.com/zilliztech/attu)
