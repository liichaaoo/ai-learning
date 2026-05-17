# Day 3 · Multi-Head Attention（为什么多头 + 张量形状追踪）

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解"多头"是什么、为什么要多头、形状怎么变
> 📋 练习：[`练习/day3_多头注意力.py`](./练习/day3_多头注意力.py)

---

## 0. 心法（5 分钟）

> **Multi-Head Attention = 把 Attention 跑 H 次，每次"角度"不同，最后把结果拼起来。**

一句话：

```
多头 = 让模型同时从多个"角度/侧面"去关注上下文
```

为什么要多头？类比一下：

```
单头 Attention：你拿着一个望远镜看一座城市
              ─→ 只能从一个角度看，信息有限

多头 Attention：你同时有 8 个望远镜，分别对准
              ─→ 一个看交通流量
              ─→ 一个看建筑高度
              ─→ 一个看人口密度
              ─→ 一个看绿化覆盖
              然后把这些视角合成一张全景图
```

每个"头"学习关注一种**不同类型的关系**——有的头学语法、有的头学指代、有的头学语义……

---

## 1. 单头 vs 多头的形状对比（15 分钟）

### 1.1 单头（昨天学的）

```
输入 x:        (B, L, d_model)        例如 (2, 4, 64)

Q = x · W_Q:   (B, L, d_model)        (2, 4, 64)
K, V 同理

scores = Q · K^T:                    (B, L, L)         (2, 4, 4)
scores / √d_k → softmax → · V:        (B, L, d_model)   (2, 4, 64)
```

### 1.2 多头（H=8 个头）

**核心思路**：把 `d_model = 64` 拆成 **8 个头 × 每头 8 维**：

```
d_model = H · d_k
   64   = 8 · 8
```

每个头各自做一遍 Attention，**总参数量不变**——只是把"宽" 改成了"分组"。

```
输入 x:                       (B, L, d_model)        (2, 4, 64)

投影后切分到 H 个头：
  Q: (B, L, d_model) → (B, L, H, d_k) → (B, H, L, d_k)        (2, 8, 4, 8)
  K, V 同理

每个头独立做 Attention：
  scores = Q · K^T:           (B, H, L, L)        (2, 8, 4, 4)
  attn = softmax(scores/√d_k):                    (2, 8, 4, 4)
  head_out = attn · V:        (B, H, L, d_k)      (2, 8, 4, 8)

把 H 个头拼回去：
  concat: (B, H, L, d_k) → (B, L, H·d_k) = (B, L, d_model)    (2, 4, 64)

最后过一个输出投影 W_O：
  output = concat · W_O:      (B, L, d_model)     (2, 4, 64)
```

> 💡 **关键认知**：**多头不是"把模型变大"，而是把同样大小的空间"分组"使用**。
>
> 总参数量：单头 4·d_model² = 4·64² = 16384
> 多头 (H=8)：4·d_model² = 4·64² = 16384  ✅ 完全相等

---

## 2. 为什么要多头（15 分钟）

### 2.1 单头的局限：信息混杂

单头 Attention 在一次计算里要同时关注：
- 语法关系（主谓宾）
- 指代关系（"它"指什么）
- 语义关系（这两个词意思相近吗）
- 位置关系（前后顺序）

**问题**：所有这些信息都被压进**同一个 d_model 维向量**里——容易互相干扰。

### 2.2 多头的好处：分而治之

让每个头**专注一种关系**：

```
Head 1 → 学到"代词指向"      （"它" → "书"）
Head 2 → 学到"主谓搭配"      （"小明" → "看")
Head 3 → 学到"修饰关系"      （"红色的" → "苹果"）
Head 4 → 学到"邻近位置"      （局部依赖）
...
```

> 🔬 **真有论文证实过**：可视化 BERT 不同 head 的注意力图，确实能看到清晰的语言学模式。

### 2.3 工程层面的好处

| 好处 | 说明 |
|------|------|
| **并行性强** | H 个头可以并行计算 |
| **表示能力丰富** | 不是简单加宽，而是多视角 |
| **总参数量不变** | 只是分组使用同样大小的空间 |
| **可解释性提升** | 不同头能可视化看出不同模式 |

---

## 3. PyTorch 完整实现（25 分钟）

### 3.1 自己写一遍（必做）

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, causal: bool = False):
        """
        :param d_model: 总维度（如 512）
        :param n_heads: 头数（如 8），必须能整除 d_model
        :param causal: 是否使用因果掩码（GPT/Llama 用）
        """
        super().__init__()
        assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.causal = causal

        # 一次性投影成 Q/K/V（合并三个 Linear，工程常见写法）
        self.W_qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.W_O = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape

        # ① 一次性投影出 Q/K/V，再切分
        qkv = self.W_qkv(x)                                      # (B, L, 3D)
        qkv = qkv.view(B, L, 3, self.n_heads, self.d_k)          # (B, L, 3, H, d_k)
        qkv = qkv.permute(2, 0, 3, 1, 4)                         # (3, B, H, L, d_k)
        Q, K, V = qkv[0], qkv[1], qkv[2]                         # 各 (B, H, L, d_k)

        # ② 计算注意力分数
        scores = Q @ K.transpose(-2, -1)                         # (B, H, L, L)
        scores = scores / math.sqrt(self.d_k)

        # ③ 因果掩码（GPT 用）
        if self.causal:
            mask = torch.tril(torch.ones(L, L, device=x.device)).bool()
            scores = scores.masked_fill(~mask, float('-inf'))

        attn = F.softmax(scores, dim=-1)                         # (B, H, L, L)

        # ④ 加权求和 V
        out = attn @ V                                           # (B, H, L, d_k)

        # ⑤ 拼回去 + 输出投影
        out = out.transpose(1, 2).contiguous()                   # (B, L, H, d_k)
        out = out.view(B, L, D)                                  # (B, L, D)
        return self.W_O(out)


# 测试
mha = MultiHeadAttention(d_model=64, n_heads=8, causal=True)
x = torch.randn(2, 10, 64)        # batch=2, L=10, d=64
y = mha(x)
print(y.shape)                    # torch.Size([2, 10, 64])

# 数一下参数量
n_params = sum(p.numel() for p in mha.parameters())
print(f"参数量: {n_params}")     # 64*64*4 = 16384（W_qkv 是 3D, W_O 是 D）
```

### 3.2 用 PyTorch 内置版本（生产环境用）

```python
mha = nn.MultiheadAttention(embed_dim=64, num_heads=8, batch_first=True)

# 注意：内置 API 要分别传 query/key/value（即使是 self-attention 也得传三遍 x）
y, attn_weights = mha(x, x, x)
```

> 💡 **学习阶段必须自己写一版**——能默写出 §3.1 的代码，本周通关 50%。

---

## 4. 张量形状练习：把每一行的 shape 标出来（15 分钟）

> **新手最容易卡的就是张量形状**。每次看 Transformer 代码，**手动 print 每一行的 shape**：

```python
def trace_shapes(x: torch.Tensor, n_heads=8):
    B, L, D = x.shape
    d_k = D // n_heads

    print(f"输入 x          {x.shape}")

    # 假设我们已经投影出 Q
    Q = x.clone()                           # 这里偷个懒
    print(f"Q (投影后)      {Q.shape}")

    # 切分到多头
    Q = Q.view(B, L, n_heads, d_k)
    print(f"Q (切分头)      {Q.shape}    ← (B, L, H, d_k)")

    Q = Q.transpose(1, 2)
    print(f"Q (转置后)      {Q.shape}    ← (B, H, L, d_k)，让 Attention 在 L 上算")

    # 算 scores
    scores = Q @ Q.transpose(-2, -1)
    print(f"scores          {scores.shape}    ← (B, H, L, L)")

    # 后续 softmax → 加权 → 拼接 → 投影 ...

# 跑一下
trace_shapes(torch.randn(2, 10, 64), n_heads=8)
```

输出：

```
输入 x          torch.Size([2, 10, 64])
Q (投影后)      torch.Size([2, 10, 64])
Q (切分头)      torch.Size([2, 10, 8, 8])    ← (B, L, H, d_k)
Q (转置后)      torch.Size([2, 8, 10, 8])    ← (B, H, L, d_k)
scores          torch.Size([2, 8, 10, 10])   ← (B, H, L, L)
```

> 🎯 **任何时候看不懂 Transformer 代码，第一招永远是"全程 print shape"。**

---

## 5. 现代 LLM 的 Attention 变种（认知级，5 分钟）

> 不需要会做，但要"听过"——阶段 5 微调时会回来看。

| 变种 | 简介 | 用在哪 |
|------|------|------|
| **MHA**（标准多头）| 每头独立 Q/K/V | 经典 Transformer |
| **MQA**（Multi-Query）| 所有头共享一份 K/V，只有 Q 多头 | PaLM、推理优化 |
| **GQA**（Grouped-Query）⭐ | 折中：N 个头共享一份 K/V | **Llama 2/3 用这个** |
| **FlashAttention** | 数学等价，IO 优化的实现 | 几乎所有现代 LLM 训练 |

> 💡 **本周只需记住**：**Llama 用 GQA**——目的是**减少 KV Cache 显存占用，加速推理**。

```
        H_q (Query 头数)    H_kv (KV 头数)
MHA       8                    8        ← 一对一
MQA       8                    1        ← 全部共享
GQA       8                    2        ← 4 个 Q 头共享 1 组 KV
```

---

## 6. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [Jay Alammar - Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/) | "The Beast With Many Heads" 一节 |
| 🥈 [Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) | 1:00:00 ~ 1:30:00 段（多头实现） |

---

## 7. 检查清单（睡前问自己）

- [ ] 解释多头的意义（为什么不直接加宽）
- [ ] 默写 Multi-Head 的核心张量形状变化（B, L, D → B, H, L, d_k）
- [ ] 解释 `d_k = d_model / n_heads`
- [ ] 解释多头的总参数量为什么和单头一样
- [ ] 听过 MQA / GQA / FlashAttention（不需要会做）
- [ ] 跑通 §3.1 的 PyTorch 实现

完成了 ➡️ [Day 4 · Transformer 完整架构](./Day4-Transformer完整架构.md)

---

## 🔗 相关链接

- ⬅️ [Day 2 · Self-Attention 公式](./Day2-SelfAttention公式.md)
- ➡️ [Day 4 · Transformer 完整架构](./Day4-Transformer完整架构.md)
- ⬆️ [Week 2 总览](./README.md)
- 📝 [本日练习](./练习/day3_多头注意力.py)
