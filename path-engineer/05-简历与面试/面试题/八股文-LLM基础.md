# 八股文 · LLM 基础

> 🎯 **目标**：每题能用 60-90 秒讲清楚，再用 30 秒补"我项目里怎么用的"
> 📌 **使用方式**：早晚各刷一遍，重点看 ⭐ 题
> 🔁 **关联**：理论部分见 [`02-LLM认知/`](../../02-LLM认知/)

---

## ⚡ 60 秒速答 vs 完整答 —— 答题结构模板

每道题都按这个结构准备：

```
┌─ 1 句话定义（30 秒能讲完）
├─ 关键技术细节（30-60 秒）
├─ 我项目里怎么用 / 踩过什么坑（30 秒，差异化）
└─ 延伸（面试官追问时再补）
```

---

## 一、Token / Tokenization ⭐

### Q1：什么是 Token？

**60 秒答**：

> Token 是 LLM 处理文本的最小单位，**不等于汉字也不等于英文单词**。
> 主流模型用 **BPE（Byte-Pair Encoding）** 算法分词：从字符开始，合并高频字节对成"子词"。
>
> 经验值：
> - 英文 1 个 Token ≈ 0.75 个单词（4 个字符）
> - 中文 1 个 Token ≈ 0.5-1 个汉字（GPT 系）/ 1-1.5 个汉字（Qwen 系）
>
> **为什么重要**：API 按 Token 计费 + 上下文窗口按 Token 限制 + 推理速度按 Token 计算。

**项目关联**：

> "我在 RAG 项目里用 `cl100k_base` tokenizer 做 chunk 切分，
> chunk_size=512 token + overlap=50 token，
> 同时用 `gpt-4o tokenizer` 做请求前的预算估算，避免超 context_window。"

### Q2：tokenizer 选错会怎样？

> - **跨模型用错** tokenizer：比如用 GPT 的 tokenizer 估算通义请求，token 数差 30%+
> - **中文用错**：用 GPT-3.5 的 tokenizer 处理中文，1 个汉字会被拆成 2-3 个 token，**成本翻倍**
> - **正确做法**：每个模型用对应的 tokenizer。比如 OpenAI 用 `tiktoken`，HuggingFace 用 `AutoTokenizer.from_pretrained()`

---

## 二、Embedding ⭐

### Q3：什么是 Embedding？余弦相似度怎么算？

**60 秒答**：

> Embedding 是把文本/图像映射到**固定维度向量**的过程，**语义相近的文本在向量空间中距离近**。
>
> 维度典型值：
> - text-embedding-3-small：1536 维
> - bge-m3：1024 维
> - 通义 text-embedding-v3：1024 维
>
> **余弦相似度** = `cos(θ) = (A·B) / (|A|·|B|)`，范围 [-1, 1]，越大越相似。
> 实际工程里 Embedding 都已**归一化**，所以余弦相似度 = 点积，省一次除法。

**追问**：为什么用余弦不用欧式距离？

> 余弦只看**方向**不看长度，更适合语义相似度。
> 欧式距离受向量长度影响（"我爱你 我爱你 我爱你"和"我爱你"欧式距离很大但语义一样）。

### Q4：Embedding 模型怎么选？

| 场景 | 推荐 |
|------|------|
| 中文为主 + 国内合规 | **bge-m3** / **通义 text-embedding-v3** |
| 多语言（中英混合） | **bge-m3** / **OpenAI text-embedding-3-large** |
| 极致精度 | **OpenAI text-embedding-3-large** (3072 维) |
| 极致便宜 + 本地部署 | **bge-small-zh** (512 维，本地跑) |

**关键考量**：维度（成本）+ 语种（精度）+ 是否能本地部署（合规/成本）+ MTEB 排行榜分数。

---

## 三、Context Window 上下文窗口 ⭐

### Q5：什么是 Context Window？怎么应对超限？

**60 秒答**：

> Context Window 是模型一次能处理的 Token 总数（输入 + 输出）。
>
> 主流模型容量：
> - GPT-4o：128k
> - Claude 3.5 Sonnet：200k
> - Gemini 1.5 Pro：1M-2M
> - Qwen2.5-72B：128k
> - Llama 3.1：128k
>
> **超限时**报 `400 - context_length_exceeded`。

**应对策略 4 招**：

1. **截断（Truncation）**：保留最近 N 轮对话 / 最近 M token
2. **总结（Summarization）**：把早期对话用模型压缩成 200 字摘要
3. **RAG 检索**：长文档不全塞，先 Embedding 检索 Top-K 相关片段
4. **滑动窗口**：长文档分段处理 + 段间 overlap

**项目关联**：

> "RAG 项目里我用了第 1+3 招组合：
> 历史消息保留最近 3 轮 + RAG 检索 Top-5 文档片段，
> 总 prompt 控制在 8k token 内，留 4k 给生成。"

---

## 四、采样参数 ⭐⭐⭐ 高频考点

### Q6：Temperature / Top-p / Top-k 区别？

**60 秒答**：

| 参数 | 作用 | 取值 | 调高效果 |
|------|------|------|---------|
| Temperature | softmax 温度，缩放 logits | 0~2 | **更随机** |
| Top-k | 只从概率前 k 个 token 采样 | 0~100 | k 大 → 更随机 |
| Top-p | 累计概率达 p 的最小 token 集合 | 0~1 | p 大 → 更随机 |

**Temperature 公式**：`P_i = exp(logits_i / T) / Σ exp(logits_j / T)`

- T → 0：贪心（永远选最大概率）
- T = 1：原始分布
- T → ∞：均匀分布（完全随机）

### Q7：什么场景用什么参数？

```
代码生成 / SQL 生成 / 数学推理：
  Temperature = 0.0 ~ 0.2  ← 要稳定，不要发散

知识问答 / 事实摘要：
  Temperature = 0.2 ~ 0.5  ← 略有变化，事实性强

闲聊 / 创意写作：
  Temperature = 0.7 ~ 1.0  ← 多样性

诗歌 / 头脑风暴：
  Temperature = 1.0 ~ 1.3  ← 高随机
```

**Top-p 默认 0.9，Temperature 调时一般固定 Top-p**。

### Q8：还有哪些常见参数？

- **max_tokens**：最大生成 token 数（控制成本 + 截断长度）
- **frequency_penalty**：[-2, 2]，惩罚已出现的 token，**降低重复**
- **presence_penalty**：[-2, 2]，惩罚已出现过的 token（不管次数），**鼓励新话题**
- **stop**：碰到指定字符串就停止生成
- **seed**：固定随机种子，**让结果可复现**（GPT-4o / Qwen 都支持）

---

## 五、流式响应 SSE ⭐

### Q9：流式响应原理是什么？为什么用 SSE 不用 WebSocket？

**60 秒答**：

> LLM 是**逐 token 自回归生成**的，每生成 1 个 token 就可以推给客户端，让用户看到"打字机效果"，
> 这样**首字延迟 < 1s**（vs 整段返回的 5-10s）。
>
> **协议选 SSE 不选 WebSocket**：
>
> | 维度 | SSE | WebSocket |
> |------|-----|-----------|
> | 方向 | 服务端 → 客户端单向 | 双向 |
> | 协议 | HTTP/1.1（基于 chunked）| 升级协议 |
> | 实现复杂度 | 低（curl 都能调试）| 高 |
> | 浏览器支持 | EventSource API 原生 | WebSocket API |
> | 反向代理 | Nginx 直接支持 | 需要特殊配置 |
> | 断线重连 | 自动 + Last-Event-ID | 需手写心跳 |
>
> **LLM 流式是单向场景，SSE 完美匹配**。

### Q10：SSE 后端怎么实现？

**Spring 写法**（WebFlux 版）：

```java
@GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chat(@RequestParam String q) {
    return chatClient.prompt(q).stream().content();
    // 自动按 chunk 分批 flush
}
```

**Spring MVC 写法**（SseEmitter 版）：

```java
@GetMapping("/chat")
public SseEmitter chat(@RequestParam String q) {
    SseEmitter emitter = new SseEmitter(60_000L);
    executor.submit(() -> {
        chatClient.prompt(q).stream().content()
            .doOnNext(chunk -> emitter.send(chunk))
            .doOnComplete(emitter::complete)
            .doOnError(emitter::completeWithError)
            .subscribe();
    });
    return emitter;
}
```

**关键点**：
- `Content-Type: text/event-stream`
- 后端必须及时 flush（不能缓冲）
- Nginx 要关闭 `proxy_buffering`，否则会聚合 chunk

---

## 六、Function Calling ⭐⭐

### Q11：Function Calling 工作原理？

**60 秒答**：

> Function Calling 不是"模型真的调用了函数"，而是模型按照你给的 **JSON Schema** 输出
> 一段**结构化的 JSON**，告诉你"我决定调用 `get_weather`，参数 city=北京"。
>
> 真正的调用还是你自己的代码做。流程：
>
> ```
> 1. 用户问"北京天气怎么样"
> 2. 把 user 消息 + tools schema 一起发给模型
> 3. 模型返回 {"tool_calls": [{"name":"get_weather","args":{"city":"北京"}}]}
> 4. 你的代码执行 get_weather("北京")，得到结果
> 5. 把结果作为 role=tool 的消息再发给模型
> 6. 模型生成最终回复"北京今天 25 度晴"
> ```

### Q12：Function Calling vs MCP 区别？

| 维度 | Function Calling | MCP |
|------|------------------|-----|
| 定义层 | 模型 API 层 | 协议层（独立于模型）|
| 工具发现 | 应用代码硬编码 | 客户端通过 MCP Server 发现 |
| 复用性 | 每个项目重写一遍 | 一次写好，所有 MCP 客户端共享 |
| 跨语言 | 跟着 SDK 走 | 标准化协议，跨语言天然 |
| 类比 | 类似函数调用 | 类似"USB 协议"|

**记忆口诀**：FC 是"语言级"，MCP 是"协议级"，**MCP 是 FC 的标准化升级版**。

---

## 七、其他高频概念

### Q13：什么是 RLHF / DPO？

**60 秒答**：

> 训练 LLM 三阶段：
> 1. **Pre-training**（预训练）：海量语料无监督学习，"知道"
> 2. **SFT**（监督微调）：人工标注的指令 → 回答对，"听懂指令"
> 3. **RLHF / DPO**（人类偏好对齐）：人评价 A 答案比 B 答案好，**让模型符合人类偏好**
>
> - **RLHF**：用强化学习（PPO 算法）+ 奖励模型，**复杂、贵、不稳定**
> - **DPO**：直接优化偏好，**不需要奖励模型**，更轻量，2024 年成为主流

### Q14：什么是幻觉（Hallucination）？怎么减少？

**60 秒答**：

> 幻觉 = 模型一本正经地胡说八道（编造不存在的事实）。
> 根因：模型只是统计学规律，没有"事实数据库"。
>
> **5 大解法**（按效果排序）：
>
> 1. **RAG**：把权威资料注入 prompt，**最有效**
> 2. **明确拒答**：prompt 里写"不知道就说不知道"
> 3. **降温度**：T = 0.0 ~ 0.2
> 4. **强约束输出**：JSON Schema / 引用必带 source
> 5. **后处理校验**：用规则/模型再扫一遍

### Q15：长文档怎么处理（>128k）？

> 4 招：
>
> 1. **分段 + Map-Reduce**：按章节切，每段总结，再合并总结
> 2. **滑动窗口**：步长 < 窗口，覆盖全文
> 3. **RAG 检索**：不全塞，按问题检索 Top-K 段
> 4. **大上下文模型**：用 Gemini 1.5 Pro（1M）/ Claude（200k），但**贵 + 慢 + 远端易丢失中间信息（lost in the middle）**

---

## 八、自测清单 ✅

刷完后能做到：

- [ ] 60 秒讲清 Token / Embedding / Context Window
- [ ] Temperature 不同值的效果区别能举例
- [ ] SSE vs WebSocket 选型理由
- [ ] Function Calling vs MCP 区别
- [ ] 幻觉 5 大解法都能讲
- [ ] 每题都能补一句"我项目里怎么用的"

---

## 🔗 下一站

- [`./八股文-SpringAI.md`](./八股文-SpringAI.md) ← Spring AI 框架题
- [`./八股文-RAG与Agent.md`](./八股文-RAG与Agent.md) ← RAG / Agent 题
- [`./八股文-工程化.md`](./八股文-工程化.md) ← 高级岗高频
- [`../系统设计/`](../系统设计/) ← 5 题系统设计
