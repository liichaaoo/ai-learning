# Day 5 · GPT vs BERT vs Llama（三大流派对比 + 现代化三件套）

> ⏱️ 时间：1.5 小时
> 🎯 目标：彻底搞懂三大流派的"长什么样、为什么这样、用在哪"
> 📋 练习：[`练习/day5_流派对比与综合.py`](./练习/day5_流派对比与综合.py)

---

## 0. 心法（5 分钟）

> **同样是 Transformer，三大流派的差别在三件事上：**
>
> ```
> 1. 用了哪部分？      —— Encoder / Decoder / 两者都用
> 2. 训练目标是什么？  —— 完形填空 / 预测下一个词
> 3. 用在什么场景？    —— 理解 / 生成 / 翻译
> ```

一句话记忆口诀：

> **BERT 看两边、GPT 只往左、Llama 是 GPT 的现代化装修版。**

---

## 1. 三大流派一览表（20 分钟，本日核心）⭐

| 维度 | **BERT** | **GPT** | **Llama** |
|------|----------|---------|-----------|
| **结构** | Encoder-only | Decoder-only | Decoder-only（增强版）|
| **Attention** | 双向（看全部）| 因果掩码（只看左边）| 因果掩码（只看左边）|
| **训练目标** | MLM（完形填空）| CLM（预测下一个 token）| CLM（同 GPT）|
| **Position Encoding** | 学习的绝对 PE | 学习的绝对 PE | **RoPE（旋转）⭐** |
| **Norm** | LayerNorm（Post-LN） | LayerNorm（Pre-LN） | **RMSNorm（Pre-LN）⭐** |
| **激活函数** | GELU | GELU | **SwiGLU ⭐** |
| **典型代表** | BERT、RoBERTa | GPT-2/3/4 | Llama 2/3、Qwen、Mistral |
| **典型用途** | 文本理解、分类、检索 | 文本生成、对话 | **开源 LLM 生态、可微调** |
| **能直接对话吗** | ❌ 不能 | ✅ 能（特别是 RLHF 后）| ✅ 能 |

> 🎯 **如果只能记一行**：
> **BERT 是"理解派"，GPT/Llama 是"生成派"，Llama = GPT + 三件现代化装修（RoPE + RMSNorm + SwiGLU）**

---

## 2. BERT：Encoder-only 的代表（15 分钟）

### 2.1 训练目标：MLM（Masked Language Model）

像做完形填空：

```
输入：  小明今天去 [MASK] 买了一本 [MASK]。
目标：  小明今天去 书店  买了一本 小说 。
```

模型同时看**整句话**（包括左右两边），预测被 mask 的词。

### 2.2 BERT 的能力边界

| ✅ 擅长 | ❌ 不擅长 |
|--------|----------|
| 文本分类（情感分析、意图识别）| 生成文本 |
| 命名实体识别（NER）| 续写、对话 |
| 语义检索（句子向量）| 创作 |
| 阅读理解（抽取式 QA）| 生成式 QA |

### 2.3 BERT 在 LLM 时代还重要吗？

**模型本身热度大降，但它的"思想还在"**：

- **句子向量 / 文本检索**：现代 RAG 里的 Embedding 模型大量用 BERT 后裔（如 `bge-m3`）
- **小模型分类**：参数少、推理快，BERT 仍然是工业级文本分类首选

> 💡 **本周认知层**：知道 BERT 是 Encoder-only、用 MLM 训练、强在理解类任务即可。**不需要去学 BERT 微调**——阶段 3 RAG 会接触到它的后代（Embedding 模型）。

---

## 3. GPT：Decoder-only 的鼻祖（15 分钟）

### 3.1 训练目标：CLM（Causal Language Model）

预测下一个 token：

```
输入：  小明今天去 [书店] 买了一本
目标：                          书

输入：  小明今天去 [书店] 买了一本 书
目标：                              。
```

每个位置都根据前面所有 token 预测下一个——**这就是"自回归生成"**。

### 3.2 推理时怎么生成

```python
prompt = "今天天气"
for _ in range(max_new_tokens):
    logits = model(tokens)            # (B, L, vocab_size)
    next_token = sample(logits[:, -1, :])  # 取最后一个位置
    tokens = torch.cat([tokens, next_token], dim=1)
```

> 💡 **重要认知**：GPT 推理是**一次生成一个 token**，下个 token 依赖上个——这是无法并行的，所以 LLM 推理慢。
>
> Week 3 会讲 KV Cache 等推理优化。

### 3.3 GPT 系列演进

| 版本 | 参数量 | 重要节点 |
|------|--------|---------|
| GPT-1 (2018) | 117M | 证明"预训练 + 微调"路线可行 |
| GPT-2 (2019) | 1.5B | "更大模型 + 不微调" 也能 zero-shot |
| GPT-3 (2020) | 175B | **In-context learning 涌现，开启大模型时代** |
| ChatGPT (2022) | — | RLHF 加持，能对话 |
| GPT-4 (2023) | 不公开 | 多模态 + 强推理 |
| GPT-4o (2024) | 不公开 | 端到端语音/图像 |

---

## 4. Llama：现代化三件套 ⭐（25 分钟，必记）

> Llama 的结构和 GPT 几乎一样，**差别全在 3 个"装修升级"**——这三件套是现代 LLM 的标配。

### 4.1 RoPE（旋转位置编码）

#### 解决的问题

GPT-2 用的是"学习的绝对位置编码"——位置 0~max_len 各学一个向量。

**问题**：
- 训练时 max_len 是固定的（如 1024），**推理时想用更长的序列就完了**
- 是"绝对位置"，不利于模型学习"相对距离"

#### RoPE 的做法（直觉版）

```
不在 Embedding 上加位置向量，
而是在 Q 和 K 计算时，把它们"旋转"一个跟位置成正比的角度。
```

```
位置 0 的 Q：不旋转
位置 1 的 Q：每两个维度旋转 θ
位置 2 的 Q：每两个维度旋转 2θ
位置 t 的 Q：每两个维度旋转 tθ

→ 两个位置的 Q·K^T 自然带上"位置相对差"
```

#### RoPE 的好处

| 好处 | 说明 |
|------|------|
| ✅ **支持外推** | 训练 4K 长度，推理时可以用到 8K+（搭配 NTK / YaRN 等扩展技巧） |
| ✅ **天然相对** | Q·K 直接体现两个 token 的相对距离 |
| ✅ **不增加参数** | 不需要学一个 PE 表 |

> 🎯 **本周记住**：**Llama 用 RoPE，因为它支持长上下文外推**——这是现在 LLM 都在卷"长 context"的技术基础。
>
> 公式细节（复数旋转、欧拉公式）**不展开**，知道是怎么回事就够。

### 4.2 RMSNorm

#### 跟 LayerNorm 的差别

```python
# LayerNorm: 减均值再除标准差（带可学习的 γ, β）
out = γ * (x - x.mean(-1)) / x.std(-1) + β

# RMSNorm: 不减均值，只除均方根（带可学习的 γ）
out = γ * x / sqrt(mean(x²) + eps)
```

#### RMSNorm 的好处

| 好处 | 数值 |
|------|------|
| ✅ 计算更简单（少一次减均值） | 速度快 ~10% |
| ✅ 实证效果不输 LayerNorm | 几乎所有现代 LLM 都换了 |
| ✅ 训练更稳 | 经验性结论 |

> 🎯 **本周记住**：**Llama 用 RMSNorm，比 LayerNorm 快**。

### 4.3 SwiGLU

#### 跟 GELU FFN 的差别

```python
# 标准 FFN（GPT/BERT）：一条线性路径
out = fc2( GELU( fc1(x) ) )
# 参数量 ≈ 2 · d_model · d_ff

# SwiGLU FFN（Llama）：两条线性路径相乘（门控）
out = fc2( SiLU(gate_proj(x)) * up_proj(x) )
# 参数量 ≈ 3 · d_model · d_ff
# 为了对齐参数量，d_ff 通常调小到 ~2/3 · 4d_model
```

> 💡 **直觉**：SwiGLU 引入了"门控"机制——一条路径决定"放多少信息过去"，另一条路径提供"信息内容"——表达力更强。

#### SwiGLU 的好处

| 好处 | 说明 |
|------|------|
| ✅ 实证比 GELU 好 | 同等参数下 PPL 更低 |
| ✅ 门控机制 | 更细粒度的信息选择 |

> 🎯 **本周记住**：**Llama 用 SwiGLU，FFN 变两条路径相乘**。
>
> 公式（SiLU(x) = x · sigmoid(x)）记不住没关系。

### 4.4 三件套速记口诀

| 升级 | 替代了 | 一句话好处 |
|------|--------|-----------|
| **RoPE** | 学习的绝对 PE | 支持长 context 外推 |
| **RMSNorm** | LayerNorm | 算得快 |
| **SwiGLU** | GELU FFN | 门控表达力强 |

> 🧠 **记忆助手**：「**绳子+扔了均值+开闸放水**」（绳子=RoPE，扔了均值=RMSNorm，开闸=SwiGLU 门控）

---

## 5. 三大模型在工作中怎么选（10 分钟）

| 你的场景 | 选谁 | 原因 |
|---------|------|------|
| 文本分类 / 实体识别 / 短文本分析 | **BERT 系**（如中文 RoBERTa）| 推理快、参数少、效果稳 |
| RAG 检索时算句向量 | **BGE / M3E 等 BERT 后裔** | 专门优化向量空间 |
| 闭源云端对话 | **GPT-4o / Claude** | 效果天花板 |
| **本地部署 / 私有化 / 微调** | **Llama / Qwen 系** ⭐ | 开源生态成熟，可微调 |
| 中文场景为主 | **Qwen 2.5 / GLM-4** | 中文训练充分 |
| 端侧 / 极致轻量 | **Qwen-0.5B / Llama-3.2-1B** | 几百 MB 能跑 |

> 💡 **作为后端工程师**：90% 概率你会用 **Qwen / Llama 系**——开源、可私有化、可微调，符合企业要求。

---

## 6. 从 GPT 到 Llama 改了哪些代码（综合演练）（15 分钟）

```python
# ─────────────────── GPT 风格（朴素版）───────────────────
class GPTBlock(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)              # ← LayerNorm
        self.attn = MultiHeadAttention(d_model, n_heads, causal=True)
        # 注意：这里没有 RoPE，PE 是加在 input embedding 上的
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),                                 # ← GELU
            nn.Linear(4 * d_model, d_model),
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x

# ─────────────────── Llama 风格（现代版）───────────────────
class LlamaBlock(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.norm1 = RMSNorm(d_model)                  # ← RMSNorm
        self.attn = MultiHeadAttentionWithRoPE(        # ← Attention 内部有 RoPE
            d_model, n_heads, causal=True
        )
        self.norm2 = RMSNorm(d_model)
        self.ffn = SwiGLU_FFN(d_model)                 # ← SwiGLU FFN

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x
```

> 💡 **结构骨架完全一样**——只是把 **LayerNorm → RMSNorm**、**GELU FFN → SwiGLU**、**绝对 PE → RoPE**。
>
> **这就是 Llama 是 "GPT 现代化装修版" 的真正含义。**

---

## 7. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [Jay Alammar - Illustrated GPT-2](http://jalammar.github.io/illustrated-gpt2/) | **必读**，把 GPT 推理过程图解清楚 |
| 🥈 [Llama 2 论文](https://arxiv.org/abs/2307.09288) | 只看 §2.1 Architecture（半页） |
| 🥉 [Karpathy - nanoGPT](https://github.com/karpathy/nanoGPT) + [llama2.c](https://github.com/karpathy/llama2.c) | 对比看 model.py，体会差异 |

---

## 8. 终极自检：30 分钟分享提纲（10 分钟）

> 这是阶段 2 的"通关测试"——**能不能给一个非 AI 同事讲清楚 LLM 工作原理**。

```
1. (3 min)  开场：从 ChatGPT 一句话回答，倒推它的工作流程
2. (5 min)  Token 化与 Embedding：文字怎么变成向量
3. (8 min)  Transformer 架构：Self-Attention + Multi-Head + 残差
4. (5 min)  GPT 生成机制：自回归 + 采样（Temperature / Top-p，Week 3 会学）
5. (5 min)  GPT vs BERT vs Llama：三大流派对比
6. (3 min)  作为工程师，我们关心什么：Context / 成本 / 延迟 / 微调
7. (1 min)  Q&A
```

> 💡 **不一定真去分享**，但要写得出讲得出。

---

## 9. 检查清单（睡前问自己）

- [ ] 默写三大流派对比表（结构 / 训练目标 / 用途 / 代表）
- [ ] 用一句话讲清楚 BERT 的 MLM 和 GPT 的 CLM 各自在干什么
- [ ] 解释什么是因果掩码、谁用谁不用
- [ ] **背下 Llama 三件套（RoPE / RMSNorm / SwiGLU）各自解决什么**
- [ ] 工作场景中能选对模型类型（理解 → BERT，生成 → Llama/GPT）
- [ ] 完成 Week 2 综合练习

---

## 10. Week 2 通关总结

恭喜你完成了**整个阶段最重要的一周**！现在你应该能：

- ✅ 闭着眼画出 Transformer 架构图
- ✅ 用白话 + 公式两种方式讲 Attention
- ✅ 解释 Q / K / V / 缩放 / 掩码 / 多头 的全部细节
- ✅ 区分 BERT / GPT / Llama 三大流派
- ✅ 知道 Llama 的现代化三件套

下周（Week 3）我们就要**真的把模型跑起来**——用 HuggingFace 加载 Qwen / Llama，看推理参数怎么影响输出。这是从"理解原理"到"动手玩"的桥梁。

完成了 ➡️ [Week 3 · HuggingFace + LLM 推理原理](../Week3-HuggingFace与推理/README.md)

---

## 🔗 相关链接

- ⬅️ [Day 4 · Transformer 完整架构](./Day4-Transformer完整架构.md)
- ⬆️ [Week 2 总览](./README.md)
- ➡️ [Week 3 · HuggingFace + LLM 推理原理](../Week3-HuggingFace与推理/README.md)（下周）
- 📝 [本日练习](./练习/day5_流派对比与综合.py)
