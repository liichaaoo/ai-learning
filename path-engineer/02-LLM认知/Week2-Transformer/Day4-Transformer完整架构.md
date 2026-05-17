# Day 4 · Transformer 完整架构（手画一张图）⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：把所有零件拼成完整 Transformer——能独立画出架构图
> 📋 练习：[`练习/day4_transformer_block.py`](./练习/day4_transformer_block.py)

---

## 0. 心法（5 分钟）

> **整个 Transformer 只有 5 个零件：**
>
> ```
> Embedding + Position → Multi-Head Attention → FFN → LayerNorm → Residual
> ```
>
> 后面三个反复堆 N 次，就是整个模型。

```
今天的终极目标：闭着眼把这张图画出来 + 讲出每条线的作用。
```

---

## 1. 一张图：完整 Transformer 架构（Encoder-Decoder 版）（10 分钟）

```
                         （Encoder 端）                    （Decoder 端）
   ┌───────────────────────────────────┐    ┌───────────────────────────────────┐
   │ 输入序列 ([CLS] I love NLP)       │    │ 输出序列 (我 爱 NLP)              │
   └───────────────┬───────────────────┘    └───────────────┬───────────────────┘
                   ↓                                        ↓
       ┌─────────────────────┐                  ┌─────────────────────┐
       │ Token Embedding     │                  │ Token Embedding     │
       └──────────┬──────────┘                  └──────────┬──────────┘
                  ↓ +                                      ↓ +
       ┌─────────────────────┐                  ┌─────────────────────┐
       │ Position Embedding  │                  │ Position Embedding  │
       └──────────┬──────────┘                  └──────────┬──────────┘
                  ↓                                        ↓
        ┌────────────────────┐                  ┌────────────────────┐
        │  Encoder Block ×N  │                  │ Masked Multi-Head  │
        │                    │                  │ Self-Attention     │ ← 因果掩码
        │ ┌────────────────┐ │                  └─────────┬──────────┘
        │ │ Multi-Head     │ │                            ↓ + 残差 + LN
        │ │ Self-Attention │ │                  ┌────────────────────┐
        │ └────────┬───────┘ │      ┌──────────→│ Cross-Attention    │ ← K, V 来自 Encoder
        │          ↓ +残差+LN │      │           │ (Q 来自 Decoder)   │
        │ ┌────────────────┐ │      │           └─────────┬──────────┘
        │ │  Feed-Forward  │ │      │                     ↓ + 残差 + LN
        │ │  (MLP)         │ │      │           ┌────────────────────┐
        │ └────────┬───────┘ │      │           │  Feed-Forward      │
        │          ↓ +残差+LN │      │           └─────────┬──────────┘
        │     输出 (h_enc)   ├──────┘                     ↓ +残差+LN
        └──────────┬─────────┘                       Decoder Block × N
                   │                                     ↓
                   │                          ┌────────────────────┐
                   │                          │  Linear → Softmax  │
                   │                          └─────────┬──────────┘
                   │                                    ↓
                   │                            预测下一个 token
                   │
              （Encoder 把整个输入序列编码成 h_enc，
               Decoder 通过 Cross-Attention 反复来"问"它）
```

> 💡 这是**原始论文的 Encoder-Decoder 结构**（用于翻译任务）。
>
> **现代 LLM（GPT/Llama）只用右边的 Decoder，去掉 Cross-Attention**。Day 5 会展开。

---

## 2. 拆解 5 大零件（每个 8 ~ 10 分钟）

### 2.1 Token Embedding：把 token id 变成向量（5 分钟）

```python
self.tok_emb = nn.Embedding(vocab_size, d_model)
# 输入: (B, L) 整数 token id
# 输出: (B, L, d_model) 浮点向量
```

> 💡 **本质**：一个**查表**操作——每个 token id 对应一个 d_model 维向量，词表多大表就多大。
>
> GPT-2 的 vocab_size = 50257，d_model = 768 → 这个 Embedding 表本身就有 38M 参数。

---

### 2.2 Position Embedding：让模型知道"顺序"（10 分钟）

#### 为什么需要

Self-Attention 是**完全对称的**——交换两个 token 的位置，输出会原样跟着换。

```
"小明 打 小红"   和  "小红 打 小明"
  → 如果只用 Token Embedding，对 Attention 来说这两个序列结构完全一样
```

显然这不对——**位置信息必须被显式注入**。

#### 三种主流做法

| 方法 | 做法 | 用在哪 |
|------|------|------|
| **绝对位置编码（学习的）** | 给位置 0~max_len 各学一个向量，加到 Embedding 上 | BERT、GPT-2 |
| **正余弦位置编码（固定）** | 用 `sin/cos` 的不同频率构造一个固定向量 | 原版 Transformer |
| **RoPE（旋转位置编码）⭐** | 把 Q/K 在每两个维度上做"旋转"，旋转角度跟位置成正比 | **Llama / Qwen / 现代 LLM** |

#### 你只需要记住

> 🎯 **现代 LLM 几乎都用 RoPE**。
>
> RoPE 的好处：**只在 Q/K 计算时旋转，不用改 Embedding 表**——支持外推（训练 4K 长度，推理可以撑到 8K+）。
>
> **公式细节本周不展开**——你能讲出"旋转、相对位置、可外推"这三个词就够了。

---

### 2.3 FeedForward Network（FFN / MLP）：每个位置独立加工（8 分钟）

```python
class FeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int = 2048):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)        # 升维
        self.fc2 = nn.Linear(d_ff, d_model)        # 降回原维度
        self.act = nn.GELU()                       # 非线性激活

    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))
```

#### 关键认知

| 维度 | 数值（GPT-2 / Llama-2） |
|------|---------------------|
| `d_model` | 768 / 4096 |
| `d_ff` | **4 × d_model** ≈ 3072 / 11008 |

**FFN 的参数量占整个 Transformer 的 ~ 2/3**——它是 Transformer 的"主要计算量来源"。

#### 直观理解

- **Attention**：让位置之间互相"对话"
- **FFN**：每个位置自己"消化"刚才听到的内容

> 💡 **FFN 是 per-position 的**——它对每个位置独立处理，不跨位置混合信息。

#### 现代变种：SwiGLU（Llama 用）

```python
# 标准 FFN（GPT/BERT）
out = fc2(GELU(fc1(x)))

# SwiGLU（Llama）：用门控机制
out = fc2(SiLU(gate_proj(x)) * up_proj(x))
```

> 🎯 你只需记住：**Llama 把 FFN 升级成了 SwiGLU**——表达力更强、训练更稳。

---

### 2.4 LayerNorm：稳定训练的关键（7 分钟）

```python
ln = nn.LayerNorm(d_model)          # 只对最后一维做归一化
out = ln(x)                          # 形状不变 (B, L, D)
```

#### LayerNorm 在做什么

```
对每个位置的向量，减均值除方差，让数值"稳定"在 0 附近
```

```
归一化前： [3.0, 100.0, -5.0, 50.0, ...]   ← 数值乱七八糟
归一化后： [-0.7, 1.5, -0.9, 0.6, ...]      ← 均值≈0，方差≈1
```

#### 为什么必须有

深层网络（GPT-3 是 96 层）里，每层之后数值会越来越漂移——没有 LayerNorm，训练根本收敛不了。

#### Pre-LN vs Post-LN（高频面试题）

```
Post-LN（原版 Transformer）：    LN(x + SubLayer(x))
Pre-LN（现代 LLM 都用）：       x + SubLayer(LN(x))
```

> 💡 **Pre-LN 训练更稳**——梯度有干净的"残差通路"直接流到底层，不会被 LN 阻塞。
>
> **GPT-2 之后所有大模型都用 Pre-LN**。

#### 现代变种：RMSNorm（Llama 用）

```python
# LayerNorm: 减均值再除标准差
out = (x - x.mean()) / x.std()

# RMSNorm: 不减均值，只除 RMS（均方根）
out = x / sqrt(mean(x²) + eps)
```

> 🎯 RMSNorm 比 LayerNorm 快 ~10%，**Llama / Qwen / Gemini 都用它**。

---

### 2.5 残差连接（Residual）：信息高速公路（5 分钟）

```python
out = x + sublayer(x)        # 就这么一行
```

#### 为什么必须有

深层网络（96 层 Transformer）的最大敌人是**梯度消失**——后面的梯度传到前面已经几乎为 0。

**残差连接** = 给梯度一条"直达通路"：

```
y = x + F(x)
∂y/∂x = 1 + ∂F/∂x      ← 永远有 1 这一项，梯度不会消失
```

> 💡 **残差是 ResNet 的发明**，2015 年来深度学习一切大模型的基石。

---

## 3. 一个完整的 Transformer Block（25 分钟）

把上面 5 个零件按 **Pre-LN** 结构拼起来：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class TransformerBlock(nn.Module):
    """现代 LLM 风格的 Decoder Block (Pre-LN + 因果)"""
    def __init__(self, d_model: int, n_heads: int, d_ff: int = None):
        super().__init__()
        d_ff = d_ff or 4 * d_model
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads, causal=True)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x):
        # ① Attention 子层（带残差）
        x = x + self.attn(self.ln1(x))
        # ② FFN 子层（带残差）
        x = x + self.ffn(self.ln2(x))
        return x

# 上面用到的 MultiHeadAttention 是 Day 3 实现的那个
```

### 整个 GPT 的样子

```python
class TinyGPT(nn.Module):
    def __init__(self, vocab_size, d_model=128, n_heads=4, n_layers=4, max_len=128):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)        # 简化：用学习的绝对 PE
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads) for _ in range(n_layers)
        ])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, idx):
        B, L = idx.shape
        pos = torch.arange(L, device=idx.device)
        x = self.tok_emb(idx) + self.pos_emb(pos)            # (B, L, D)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.head(x)                                # (B, L, vocab_size)
        return logits

# 试一下
model = TinyGPT(vocab_size=1000, d_model=64, n_heads=4, n_layers=2)
idx = torch.randint(0, 1000, (2, 10))
logits = model(idx)
print(logits.shape)        # torch.Size([2, 10, 1000])

n_params = sum(p.numel() for p in model.parameters())
print(f"参数量: {n_params:,}")
```

> 💡 **这就是一个完整的 GPT 了**——和 GPT-2/3/4 的区别只是规模、词表、训练数据。结构完全一样。

---

## 4. Encoder vs Decoder：本质差异（10 分钟）

| 维度 | Encoder | Decoder |
|------|---------|---------|
| **Attention** | 双向（看全部） | 因果掩码（只看左边） |
| **是否有 Cross-Attention** | ❌ 没有 | ✅ 翻译任务里有，纯 LLM 里没有 |
| **典型用法** | 文本理解、分类、检索 | 文本生成、对话 |
| **典型代表** | BERT、RoBERTa | GPT、Llama、Qwen |
| **本周重点** | 知道存在即可 | **现代 LLM 全是它，必须吃透** |

> 🎯 **现代 LLM 99% 是 Decoder-only**——Encoder 已经在 LLM 时代式微（虽然在 Embedding/检索领域还很活跃）。

---

## 5. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [Jay Alammar - Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/) | 完整看完后半部分 + 残差和 LN 的图 |
| 🥈 [Attention Is All You Need 论文图 1](https://arxiv.org/abs/1706.03762) | **就看那张架构图**，对照本文复盘 |
| 🥉 [Karpathy - nanoGPT 仓库](https://github.com/karpathy/nanoGPT) | model.py 不到 300 行，把今天讲的都用上了 |

---

## 6. 检查清单（睡前问自己）

- [ ] **手画一张完整 Transformer 架构图**（Encoder + Decoder 都画）
- [ ] 解释每个零件的作用（PE / Attention / FFN / LN / 残差）
- [ ] 解释 Pre-LN vs Post-LN，现代 LLM 用哪个
- [ ] 默写 `TransformerBlock` 的 `forward`（5 行）
- [ ] 解释为什么 d_ff 通常是 4 × d_model
- [ ] 跑通 §3 的 TinyGPT，输出形状正确

完成了 ➡️ [Day 5 · GPT vs BERT vs Llama](./Day5-三大流派对比.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · Multi-Head Attention](./Day3-MultiHead多头注意力.md)
- ➡️ [Day 5 · 三大流派对比](./Day5-三大流派对比.md)
- ⬆️ [Week 2 总览](./README.md)
- 📝 [本日练习](./练习/day4_transformer_block.py)
