# Ch7 张量与 einsum

> 对应学习：[Einsum is All You Need](https://rockt.github.io/2018/04/30/einsum)、PyTorch Tensor 教程
> 目标：**为 Transformer 打底**——能用 einsum 写出任意张量运算

---

## 📝 概念题

### 7.1 ⭐
解释**张量**在 ML 中的含义：
- 0 阶张量 = ?
- 1 阶张量 = ?
- 2 阶张量 = ?
- 3 阶张量（举个深度学习的例子）= ?
- 4 阶张量（举个深度学习的例子）= ?

### 7.2 ⭐
**形状（Shape）语义**：下列张量的每一维代表什么？
- `(batch, features)` — 表格数据
- `(batch, channels, height, width)` — 图像
- `(batch, seq_len, embed_dim)` — 序列数据（**Transformer 输入！**）
- `(batch, num_heads, seq_len, head_dim)` — Multi-Head Attention

### 7.3 ⭐⭐
**广播（Broadcasting）规则**：能否广播？为什么？
- (a) `(3, 4)` + `(4,)` → ?
- (b) `(3, 4)` + `(3,)` → ?（提示：不行！）
- (c) `(3, 1, 5)` + `(1, 4, 5)` → ?
- (d) `(3, 4)` + `()` → ?

### 7.4 ⭐⭐
**einsum 的核心规则**：
- 重复的下标 → 求和并消除（收缩）
- 只出现一次的下标 → 保留（输出维度）
- 下标顺序 → 决定输出形状

举例解释：
- `'ij,jk->ik'` = ?（矩阵乘法）
- `'ij,ij->'` = ?（Frobenius 内积）
- `'ii->'` = ?（迹）

---

## ✍️ einsum 翻译题

### 7.5 ⭐ — 基础操作
用 einsum 表达式替代下列操作：

| 操作 | 等价 einsum |
|------|------------|
| 向量点积 `u · v` | `'i,i->'` |
| 矩阵转置 `A^T` | ? |
| 矩阵迹 `tr(A)` | ? |
| 矩阵-向量乘 `Ax` | ? |
| 矩阵乘法 `AB` | ? |
| 外积 `u v^T` | ? |
| 批量矩阵乘 `(B,i,j) × (B,j,k)` | ? |
| 逐元素乘 | ? |
| 沿某轴求和 | ? |

### 7.6 ⭐⭐ — Attention 机制中的张量运算

**Self-Attention**:
- Q, K, V 形状都是 `(batch, seq_len, d_k)`
- 计算 attention scores: `QK^T / √d_k`
- softmax → 权重矩阵 `(batch, seq_len, seq_len)`
- 乘 V → `(batch, seq_len, d_k)`

请用 einsum 写出：
- (a) `scores = QK^T`
- (b) `output = weights @ V`（weights 形状 `(batch, seq_len, seq_len)`）

### 7.7 ⭐⭐⭐ — Multi-Head Attention

Q, K, V 形状：`(batch, num_heads, seq_len, head_dim)`
- (a) Attention scores: `(batch, num_heads, seq_len, seq_len)` — 用 einsum 写出
- (b) 加权求和 V: `(batch, num_heads, seq_len, head_dim)` — 用 einsum 写出

### 7.8 ⭐⭐⭐ — 复杂张量运算
把下列循环代码向量化 + einsum 化：
```python
# A: (B, M, K)
# B: (B, K, N)
# 结果 C: (B, M, N)，且 C[b,i,j] = sum_k A[b,i,k] * B[b,k,j]
C = np.zeros((B_size, M, N))
for b in range(B_size):
    for i in range(M):
        for j in range(N):
            for k in range(K):
                C[b,i,j] += A[b,i,k] * B[b,k,j]
```

---

## 💻 编程题

### 7.9 ⭐⭐ — einsum 对比实验
对以下每个操作，分别用 `NumPy 原生函数` 和 `np.einsum` 实现，验证结果一致：

```python
import numpy as np
np.random.seed(42)
A = np.random.randn(100, 50)
B = np.random.randn(50, 80)

# 1. 矩阵乘法
r1 = A @ B
r2 = np.einsum('ij,jk->ik', A, B)
assert np.allclose(r1, r2)

# 你的任务：补完下列 8 个
# - Hadamard（同形矩阵逐元素乘）
# - 外积（100-维向量 × 50-维向量）
# - batch 矩阵乘（shape (10, 3, 4) × (10, 4, 5)）
# - 沿第 1 轴求和
# - 双线性：v^T A u
# - Frobenius 内积：sum(A * B)
# - 对角线提取
# - 矩阵迹
```

### 7.10 ⭐⭐⭐ — 手写 Self-Attention

```python
def scaled_dot_product_attention(Q, K, V):
    """
    Q, K, V: shape (batch, seq_len, d_k)
    返回: attention 输出 (batch, seq_len, d_k) 和权重 (batch, seq_len, seq_len)
    """
    d_k = Q.shape[-1]
    # 用 einsum 写
    scores = np.einsum(...)  # (batch, seq_len, seq_len)
    scores = scores / np.sqrt(d_k)
    weights = softmax(scores, axis=-1)
    output = np.einsum(...)  # (batch, seq_len, d_k)
    return output, weights
```

测试：`Q = K = V = np.random.randn(2, 10, 64)`

### 7.11 ⭐⭐⭐ — Reshape vs einsum

Multi-Head Attention 中常见的操作：把 `(batch, seq, embed)` 拆成 `(batch, heads, seq, head_dim)`。
- 方法 A：`.reshape + .transpose`
- 方法 B：einsum？（思考：einsum 能表达维度重排，但不能改变总元素数）

哪种更好？为什么实际代码里用 reshape？

### 7.12 ⭐⭐ — PyTorch 迁移

把上面所有 `np.einsum` 的题目换成 `torch.einsum`，
验证 GPU 上是否能加速（如果有 GPU）。

---

## 🎯 应用题

### 7.13 ⭐⭐⭐
**阅读 Transformer 源码**：去 [nanoGPT](https://github.com/karpathy/nanoGPT) 看 `model.py` 中的 attention 实现，
找出 einsum 或等价运算的位置，理解每一步形状如何变化。
