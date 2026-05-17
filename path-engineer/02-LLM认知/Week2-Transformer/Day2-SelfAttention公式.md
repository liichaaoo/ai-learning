# Day 2 · Self-Attention 公式（一行神奇公式拆解）⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：吃透 `Attention(Q, K, V) = softmax(QK^T / √d_k) V` —— 每一步都讲得出
> 📋 练习：[`练习/day2_自注意力实现.py`](./练习/day2_自注意力实现.py)

---

## 0. 心法（5 分钟）

> **整个 Transformer 的灵魂，就是这一行：**
>
> $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

今天不是学新东西，而是**把 Day 1 的"图书馆类比"翻译成数学**。

5 个动作要刻进脑子：

```
1. 每个 token 投影成 Q、K、V                ← 准备阶段
2. Q 和 K 做矩阵乘 → 相似度矩阵            ← 打分
3. 除以 √d_k                                ← 防止梯度爆炸
4. softmax 按行归一化                       ← 变权重
5. 跟 V 矩阵乘 → 输出                       ← 加权求和
```

**完成今天的练习后，你应该能不看公式默写 PyTorch 实现。**

---

## 1. 公式逐步拆解（30 分钟）

### 1.1 从一个具体张量形状开始

设：
- 序列长度 `L = 4`（4 个 token）
- 隐藏维度 `d_model = 8`
- Q、K、V 的维度也是 `d_k = d_v = 8`（先不管多头，就一头）

```
输入 x : (4, 8)        ← 4 个 token，每个 8 维
W_Q   : (8, 8)
W_K   : (8, 8)
W_V   : (8, 8)
```

### 1.2 第 1 步：投影出 Q / K / V

$$Q = x W_Q,\quad K = x W_K,\quad V = x W_V$$

```python
Q = x @ W_Q   # (4, 8)
K = x @ W_K   # (4, 8)
V = x @ W_V   # (4, 8)
```

> 💡 **Q、K、V 形状都和 x 一样**（`(L, d)`）—— 它们是同一组 token 的"三种角色"。

### 1.3 第 2 步：算相似度矩阵 `Q · K^T`

$$\text{scores} = Q K^T$$

```python
scores = Q @ K.T   # (4, 8) · (8, 4) = (4, 4)
```

**形状关键变化**：从 `(L, d)` 变成 `(L, L)` —— **变成一个"每个位置 × 每个位置"的方阵**。

```
       K_0   K_1   K_2   K_3
Q_0  [ s00   s01   s02   s03 ]    第 0 行 = token 0 看其他位置的"未归一化分数"
Q_1  [ s10   s11   s12   s13 ]
Q_2  [ s20   s21   s22   s23 ]
Q_3  [ s30   s31   s32   s33 ]
```

> 💡 **几何解释**：`Q_i · K_j` 是两个向量的点积——**点积越大说明方向越接近，也就是相似度越高**。

### 1.4 第 3 步：除以 `√d_k`（缩放点积）

$$\text{scores} = \frac{Q K^T}{\sqrt{d_k}}$$

```python
scores = (Q @ K.T) / np.sqrt(d_k)   # 假设 d_k = 8，除以 √8
```

#### 为什么要除以 `√d_k`？（高频面试题 ⭐）

**问题**：当 `d_k` 比较大时（比如 64、128），`Q · K^T` 的数值会非常大。

**后果**：softmax 的指数函数对大数极敏感——大的会被指数放大，小的会被压成 0。

```
softmax([1.0, 2.0, 3.0])    ≈ [0.09, 0.24, 0.67]   ← 还算均衡
softmax([10, 20, 30])       ≈ [2e-9, 5e-5, 0.999]  ← 几乎只有最后一个
```

**结果**：softmax 输出几乎是 one-hot —— **梯度变得极小，模型学不动**。

**解决**：除以 `√d_k`，让数值保持在合理范围。

> 🎯 **一句话**：**除以 √d_k 是为了让 softmax 不"过度自信"，保持梯度可以流动。**

### 1.5 第 4 步：softmax（按行归一化）

$$A = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right)$$

```python
attn_weights = softmax(scores, axis=-1)   # (4, 4)，每一行加起来 = 1
```

**关键**：`axis=-1` 是按**行**做 softmax —— 每一行代表"一个 token 看其他位置的权重分布"，所以每行要归一化为概率。

```
       K_0    K_1    K_2    K_3
Q_0  [ 0.1    0.2    0.5    0.2 ]   ← 行加起来 = 1
Q_1  [ 0.3    0.4    0.2    0.1 ]
Q_2  [ 0.05   0.05   0.8    0.1 ]
Q_3  [ 0.1    0.1    0.1    0.7 ]
```

### 1.6 第 5 步：用权重加权求和 V

$$\text{output} = A \cdot V$$

```python
output = attn_weights @ V   # (4, 4) · (4, 8) = (4, 8)
```

**形状回到 `(L, d)`** —— 跟输入 x 一样大，所以 Transformer 可以堆很多层。

---

## 2. 完整 PyTorch 实现（25 分钟）

### 2.1 最简版（不带掩码）

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SelfAttention(nn.Module):
    """单头 Self-Attention"""
    def __init__(self, d_model: int, d_k: int):
        super().__init__()
        self.d_k = d_k
        self.W_Q = nn.Linear(d_model, d_k, bias=False)
        self.W_K = nn.Linear(d_model, d_k, bias=False)
        self.W_V = nn.Linear(d_model, d_k, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, L, d_model)
        Q = self.W_Q(x)                                # (B, L, d_k)
        K = self.W_K(x)                                # (B, L, d_k)
        V = self.W_V(x)                                # (B, L, d_k)

        scores = Q @ K.transpose(-2, -1)               # (B, L, L)
        scores = scores / math.sqrt(self.d_k)          # 缩放
        attn = F.softmax(scores, dim=-1)               # (B, L, L)

        out = attn @ V                                 # (B, L, d_k)
        return out


# 试一下
x = torch.randn(2, 4, 8)        # batch=2, L=4, d_model=8
attn = SelfAttention(d_model=8, d_k=8)
y = attn(x)
print(y.shape)                  # torch.Size([2, 4, 8])
```

> 💡 **能默写出这段代码（不看着公式），Day 2 就通关了。**

### 2.2 调用现成 API（PyTorch 2.0+ 内置）

```python
# PyTorch 已经内置了高度优化的 SDPA（Scaled Dot-Product Attention）
y = F.scaled_dot_product_attention(Q, K, V)
# 内部用 FlashAttention 等技术，比手写快 2-5 倍
```

> 💡 **生产环境直接用这个**，**学习阶段必须自己手写一遍才算懂**。

---

## 3. 因果掩码（Causal Mask）：GPT 为什么"只能看左边"（20 分钟）

### 3.1 问题：训练 GPT 时不能"作弊"

GPT 的训练目标是**预测下一个 token**。比如：

```
输入： [The, cat, sat, on, the]
目标： [cat, sat, on, the, mat]
```

但如果 Self-Attention 让位置 `2`（`sat`）能看到位置 `4`（`the`），那预测下一个词时模型就**直接抄答案**了——这就是"作弊"。

**解决**：加一个**下三角的掩码**，把"未来位置"的注意力分数置为 `-∞`，softmax 后就变成 0。

### 3.2 因果掩码长什么样

```
           K_0   K_1   K_2   K_3
Q_0   [    1     0     0     0   ]   ← token 0 只能看到自己
Q_1   [    1     1     0     0   ]   ← token 1 能看 0, 1
Q_2   [    1     1     1     0   ]   ← token 2 能看 0, 1, 2
Q_3   [    1     1     1     1   ]   ← token 3 能看全部
```

代码上：

```python
L = scores.size(-1)
mask = torch.tril(torch.ones(L, L)).bool()        # 下三角矩阵
scores = scores.masked_fill(~mask, float('-inf')) # 上三角填 -inf
attn = F.softmax(scores, dim=-1)                  # softmax 后 -inf → 0
```

### 3.3 三大流派的掩码差异

| 模型 | 是否用因果掩码 | 原因 |
|------|--------------|------|
| **GPT / Llama** | ✅ 用 | 训练目标是预测下一个词 |
| **BERT** | ❌ 不用（双向）| 训练目标是完形填空（MLM），需要看两边 |
| **T5 (Encoder-Decoder)** | Encoder 不用，Decoder 用 | Encoder 看全局，Decoder 自回归生成 |

> 💡 **记忆**：**Decoder-only ⇔ 因果掩码 ⇔ 自回归生成**——这三个词永远绑在一起。

---

## 4. 举一个数字算到底的小例子（10 分钟）

> 不耐烦的话可以跳过，但**亲手算一遍记忆深刻 10 倍**。

设序列长度 L=2，d_k=2：

```
Q = [[1, 0],     K = [[1, 0],     V = [[1, 2],
     [0, 1]]          [1, 1]]          [3, 4]]
```

**Step 1**：`Q · K^T`

```
Q · K^T = [[1·1+0·0,  1·1+0·1],     = [[1, 1],
           [0·1+1·0,  0·1+1·1]]        [0, 1]]
```

**Step 2**：除以 `√d_k = √2 ≈ 1.414`

```
scores = [[0.707, 0.707],
          [0.000, 0.707]]
```

**Step 3**：softmax 按行

```
第 1 行：softmax([0.707, 0.707]) = [0.5, 0.5]
第 2 行：softmax([0.000, 0.707]) = [0.330, 0.670]

A = [[0.500, 0.500],
     [0.330, 0.670]]
```

**Step 4**：`A · V`

```
output[0] = 0.5 * [1, 2] + 0.5 * [3, 4] = [2.0, 3.0]
output[1] = 0.33 * [1, 2] + 0.67 * [3, 4] = [2.34, 3.34]

output = [[2.00, 3.00],
          [2.34, 3.34]]
```

> 💡 **观察**：第二个 token 的输出更偏向 V 的第二行——因为它跟 K 的第二行相似度更高。
>
> **这就是 Attention 全部的秘密。**

---

## 5. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [Jay Alammar - Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/) | 看 "Self-Attention in Detail" + "Matrix Calculation of Self-Attention" 两节 |
| 🥈 [李沐《动手学深度学习》10.6 节](https://zh.d2l.ai/chapter_attention-mechanisms/self-attention-and-positional-encoding.html) | 中文公式版，配本文阅读 |

---

## 6. 检查清单（睡前问自己）

- [ ] 不看资料默写 `Attention(Q, K, V) = softmax(QK^T / √d_k) V`
- [ ] 解释为什么要除以 `√d_k`（梯度+softmax 角度）
- [ ] 解释 softmax 为什么要 `dim=-1` 按行
- [ ] 解释什么是因果掩码、谁用谁不用
- [ ] 跑通 §2 的 PyTorch 代码，输入输出形状一致
- [ ] §4 的数字例子能自己算一遍

完成了 ➡️ [Day 3 · Multi-Head Attention](./Day3-MultiHead多头注意力.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · Attention 直观理解](./Day1-Attention直观理解.md)
- ➡️ [Day 3 · Multi-Head Attention](./Day3-MultiHead多头注意力.md)
- ⬆️ [Week 2 总览](./README.md)
- 📝 [本日练习](./练习/day2_自注意力实现.py)
