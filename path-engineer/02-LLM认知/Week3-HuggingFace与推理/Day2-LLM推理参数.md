# Day 2 · LLM 推理参数（面试 + 工程双高频）⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：吃透 5 大推理参数，能根据场景报出工程默认值
> 📋 练习：[`练习/day2_采样参数实验.py`](./练习/day2_采样参数实验.py)

---

## 0. 心法（5 分钟）

> **LLM 推理 = 一次次"在概率分布里挑一个 token"。推理参数就是控制怎么挑的旋钮。**

回顾 Week 2：GPT 是自回归生成——每一步输出一个 `(vocab_size,)` 的概率分布，从中**挑**一个 token，再继续算下一步。

```
                                  ┌─ 挑选策略 ──┐
模型输出 logits ─→ softmax ─→ 概率分布 ─→ 挑一个 token
                              ↑                ↑
                              Temperature    Top-p / Top-k
                              控制锐利度      控制候选池
```

**5 个参数控制 5 件事**：

| 参数 | 控制 |
|------|------|
| **Temperature** | 概率分布有多"锐"（大概率有多压倒一切）|
| **Top-k** | 只在概率前 k 个候选里挑 |
| **Top-p** | 只在累计概率到 p 的候选里挑 |
| **max_tokens** | 最多生成多少个新 token |
| **Context Window** | 模型一次能看多少 token |

---

## 1. 一图速记：本日要刻进脑子的总表 ⭐（10 分钟）

| 参数 | 作用 | 调高的影响 | 工程默认值 |
|------|------|-----------|-----------|
| **Temperature** | 输出"创造性" | 更随机、更发散 | **0.7（聊天）/ 0.0（事实/RAG）** |
| **Top-p**（核采样）| 候选词概率累积阈值 | 候选池更大 | **0.9** |
| **Top-k** | 只在 Top-k 个候选词里采样 | 候选池更大 | 40 ~ 50 |
| **max_tokens** | 最大输出长度 | 更长（更慢、更贵）| 按场景设 |
| **repetition_penalty** | 抑制重复 | 减少复读 | 1.0（不开）~ 1.1 |
| **Context Window** | 模型一次能"看到"多少 token | — | GPT-4o: 128K，Llama-3: 8K~128K |

> 🎯 **本日最重要的一行口诀**：
>
> **"事实场景 T=0；聊天场景 T=0.7 配 Top-p=0.9；二选一就用 Top-p。"**

---

## 2. Temperature：温度怎么调（20 分钟）

### 2.1 数学上 Temperature 在做什么

softmax 之前**先把 logits 除以 T**：

$$P(token_i) = \frac{\exp(\text{logits}_i / T)}{\sum_j \exp(\text{logits}_j / T)}$$

### 2.2 直观感受：T 控制概率分布的"锐利度"

假设模型输出 logits = `[2.0, 1.0, 0.0]`，对应 3 个候选 token：

| T | softmax 后概率 | 行为 |
|---|---------------|------|
| **T = 0.1**（接近 0）| `[0.999, 4e-5, 2e-9]` | **几乎只可能选第一个** ← 趋于贪婪 |
| **T = 0.5** | `[0.87, 0.12, 0.01]` | 偶尔选第二个 |
| **T = 1.0** | `[0.67, 0.24, 0.09]` | 标准 softmax |
| **T = 2.0** | `[0.51, 0.31, 0.19]` | 三个都可能选 ← 趋于均匀 |
| **T → ∞** | `[0.33, 0.33, 0.33]` | 完全随机 |

### 2.3 工程取值（务必记住）

| 场景 | T 取值 | 原因 |
|------|--------|------|
| **RAG / 事实问答 / 代码生成** | **0.0** | 要确定性、可复现 |
| **客服 / 闲聊** | 0.5 ~ 0.7 | 自然但不出格 |
| **创意写作 / 头脑风暴** | 0.8 ~ 1.0 | 鼓励多样性 |
| **诗歌 / 故事生成** | 1.0 ~ 1.3 | 要"灵气" |
| > 1.5 | 不推荐 | 容易胡说 |

### 2.4 一个误区

> ⚠️ **`temperature=0` 不一定真的完全确定**——某些 API 内部仍可能有微小随机性，**真正确定要用 `do_sample=False`（贪婪解码）**。

```python
# ✅ 真正的确定性
outputs = model.generate(**inputs, do_sample=False)

# ⚠️ 接近但不保证
outputs = model.generate(**inputs, do_sample=True, temperature=0.0)
```

---

## 3. Top-k 和 Top-p：候选池怎么截（20 分钟）

> Temperature 控制了"概率有多锐"，但万一第一个的概率就是 0.5、剩下 50% 散在 5 万个 token 里，模型还是可能选到一些**完全不相关的"长尾垃圾"**。
>
> Top-k 和 Top-p 就是来**砍掉长尾**的。

### 3.1 Top-k：只看排名前 k 的

```
模型输出概率（举例 vocab=10）：
  [0.40, 0.20, 0.15, 0.10, 0.05, 0.04, 0.03, 0.02, 0.005, 0.005]
   token1, token2, ..., token10

Top-k = 3：
  只在前 3 个里采样 → [0.40, 0.20, 0.15] 重新归一化 → [0.53, 0.27, 0.20]
```

**问题**：固定 k 不灵活——如果分布很尖（第一名 0.95），其实只该选 1 个；如果分布很平（前 30 个都差不多），k=3 又太少。

### 3.2 Top-p（核采样）：动态候选池 ⭐

**思路**：从大到小累加概率，直到累计到 p（如 0.9），就停。

```
排序后概率：
  [0.40, 0.20, 0.15, 0.10, 0.05, 0.04, 0.03, 0.02, 0.005, 0.005]
   累积：0.40, 0.60, 0.75, 0.85, 0.90 ←  到这里停！

Top-p = 0.9 → 候选池 = 前 5 个 token
```

**优点**：自适应——分布尖时只留几个，分布平时留很多。

> 🎯 **结论**：**生产环境优先用 Top-p**（默认 0.9），Top-k 多用于和 Top-p 配合（先 Top-k=50 砍长尾，再 Top-p 精修）。

### 3.3 三种采样在工程里的搭配

```python
# ① 严格事实场景：贪婪
do_sample=False

# ② 通用聊天场景（最常见）：T + Top-p
temperature=0.7, top_p=0.9, do_sample=True

# ③ 高创造场景：T 调高 + Top-p 放宽
temperature=1.0, top_p=0.95, do_sample=True

# ④ 老式组合（仍有效）：Top-k + Top-p
temperature=0.7, top_k=50, top_p=0.9, do_sample=True
```

---

## 4. 用 HuggingFace 实测三种采样（20 分钟）

> 跑一遍这段代码，**亲眼看到**参数对输出的影响——比看 100 篇文章都印象深刻。

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto"
)

prompt = "用三句话写一首关于秋天的诗："
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# ─── 实验 1：贪婪解码（do_sample=False）───
print("【贪婪 / 完全确定】")
for i in range(3):
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
    print(f"  第 {i+1} 次:", tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
print("→ 三次输出完全一样\n")

# ─── 实验 2：T=0.7 + Top-p=0.9（推荐配置）───
print("【T=0.7, Top-p=0.9】")
torch.manual_seed(42)
for i in range(3):
    out = model.generate(**inputs, max_new_tokens=80,
                         do_sample=True, temperature=0.7, top_p=0.9)
    print(f"  第 {i+1} 次:", tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
print("→ 三次都不一样，但都还合理\n")

# ─── 实验 3：T=1.5（高创造）───
print("【T=1.5（很发散）】")
torch.manual_seed(42)
for i in range(3):
    out = model.generate(**inputs, max_new_tokens=80,
                         do_sample=True, temperature=1.5, top_p=0.95)
    print(f"  第 {i+1} 次:", tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
print("→ 可能开始胡说")
```

> 💡 **跑完这段你应该能直观感受到**：
> - 贪婪：**稳定但呆板**
> - T=0.7+Top-p=0.9：**多样但合理**（聊天默认）
> - T=1.5：**发散到边界**

---

## 5. max_tokens & Context Window（10 分钟）

### 5.1 max_tokens / max_new_tokens

```python
model.generate(**inputs, max_new_tokens=200)   # 最多生成 200 个新 token
```

**注意区分**：
- `max_length`：**总长度**（含 prompt），容易踩坑
- `max_new_tokens`：**新生成的长度**（推荐用这个）

**取值建议**：

| 场景 | max_new_tokens |
|------|---------------|
| 单句回复 / 标签 | 50 ~ 100 |
| 段落回复 / 普通对话 | 200 ~ 500 |
| 长文生成 / 总结 | 1000 ~ 2000 |
| 文档生成 / 报告 | > 2000 |

> 💡 **越大越慢、越贵**——按 token 计费的 API 直接关联开销。

### 5.2 Context Window（上下文窗口）

**定义**：模型**一次能"看到"多少 token**（包括输入 + 输出）。

| 模型 | Context Window |
|------|---------------|
| GPT-3.5 | 16K |
| GPT-4 | 8K（标准）/ 128K（Turbo）|
| **GPT-4o / Claude 3.5** | **128K** ~ 200K |
| Llama 3.1 | 128K |
| Qwen 2.5 | 32K ~ 128K |
| Gemini 1.5 Pro | **2M** ⭐ |

> 💡 **超过 Context 会怎样**？
> - 早期：直接报错
> - 现在：很多 API 自动截断（裁掉最早的部分）——**RAG 里要特别注意**

### 5.3 工程认知：长 Context ≠ 全能

| 现象 | 解释 |
|------|------|
| **"Lost in the Middle"** | 长 context 里**中间位置**的信息容易被忽略 |
| **复杂度 O(n²)** | Attention 复杂度跟 context 平方相关 → context 翻倍，显存/算力 4 倍 |
| **价格 = token × 单价** | 用 128K context 一次调用就可能烧掉 几毛钱 |

> 🎯 **对工程师的实际影响**：
> - RAG 不是"塞越多越好"——要选**最相关**的 5~10 个 chunks
> - 长 prompt 不是免费的——能精简就精简

---

## 6. 其他常用参数速查（5 分钟）

| 参数 | 作用 | 默认 / 常用 |
|------|------|-----------|
| `do_sample` | 是否采样（False=贪婪）| 通常 True |
| `repetition_penalty` | 抑制重复 | 1.0（关）~ 1.1 |
| `no_repeat_ngram_size` | 禁止 n-gram 重复 | 3 ~ 5 |
| `early_stopping` | beam search 中提前停 | False |
| `num_beams` | beam search 的束宽 | 1（关）~ 5 |
| `seed` | 随机种子（可复现）| — |

> 💡 **现代 LLM 几乎不用 beam search**——它适合翻译这种"求最优解"任务，不适合开放式生成。

---

## 7. OpenAI / 国产 API 的参数对应（5 分钟）

> 让你以后调商用 API 时心里有底。

| HuggingFace | OpenAI / 通用 API | 说明 |
|-------------|------------------|------|
| `temperature` | `temperature` | 完全一致 |
| `top_p` | `top_p` | 完全一致 |
| `max_new_tokens` | `max_tokens` | OpenAI 这名字其实指"新增"长度 |
| `repetition_penalty` | `frequency_penalty` / `presence_penalty` | OpenAI 拆成两个 |
| `do_sample` | （没有）| OpenAI 默认采样，T=0 时近似贪婪 |

```python
# OpenAI 风格（阶段 3 / 4 调云端 API 时会用）
client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0.7,
    top_p=0.9,
    max_tokens=500,
)
```

---

## 8. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [HuggingFace - generation_strategies](https://huggingface.co/docs/transformers/generation_strategies) | 官方文档最全 |
| 🥈 [How to generate text - HuggingFace blog](https://huggingface.co/blog/how-to-generate) | 把所有采样策略可视化讲清楚 |
| 选看 [Lost in the Middle 论文](https://arxiv.org/abs/2307.03172) | 长 context 失效的实证研究 |

---

## 9. 检查清单（睡前问自己）

- [ ] 默写 5 大推理参数总表（含工程默认值）
- [ ] 解释 Temperature 数学上在做什么
- [ ] 解释 Top-p 跟 Top-k 的区别 + 推荐用哪个
- [ ] 三个场景报出参数：RAG / 闲聊 / 创意写作
- [ ] 解释 `max_length` vs `max_new_tokens`
- [ ] 知道长 context 的 3 个工程代价（中间丢失 / O(n²) / 钱）
- [ ] 跑通 §4 的实测代码，亲眼见到 T 的影响

完成了 ➡️ [Day 3 · 训练范式全流程](./Day3-训练范式全流程.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · HuggingFace 三件套](./Day1-HuggingFace三件套.md)
- ➡️ [Day 3 · 训练范式全流程](./Day3-训练范式全流程.md)
- ⬆️ [Week 3 总览](./README.md)
- 📝 [本日练习](./练习/day2_采样参数实验.py)
