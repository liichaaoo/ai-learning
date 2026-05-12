# Day 2 · 矩阵乘法与线性变换（Attention 基石）

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**能手算 2×3 矩阵乘法，看懂 Attention 公式里的 QK^T**

---

## 🧭 今天的核心问题

> Transformer 里 Attention 的公式是：
> $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$
>
> 你能看懂每个符号是在做什么吗？

**今天结束后你应该能说**：
- Q、K、V 都是**矩阵**
- $QK^T$ 是**矩阵乘法**，算出的是"token 之间的相似度矩阵"
- softmax 把相似度变成**注意力权重**
- 再乘以 V 得到"加权后的输出"

（softmax 明天讲，今天先吃透**矩阵乘法**）

---

## 一、矩阵乘法（Matrix Multiplication）⭐⭐⭐

### 1.1 基本规则

$(m, n) \times (n, p) = (m, p)$

**中间两个数必须相等**，外面两个数就是结果的形状。

```
(2, 3) @ (3, 4) = (2, 4) ✅
(2, 3) @ (4, 3) = ❌ 报错（中间 3 ≠ 4）
```

### 1.2 手算一遍（非常重要）

$$A = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}, \quad B = \begin{bmatrix} 5 & 6 \\ 7 & 8 \end{bmatrix}$$

计算 $C = A \times B$：

**规则**：C 的第 i 行第 j 列 = A 的第 i 行 · B 的第 j 列（点积）

- $C_{0,0}$ = [1, 2] · [5, 7] = 1×5 + 2×7 = **19**
- $C_{0,1}$ = [1, 2] · [6, 8] = 1×6 + 2×8 = **22**
- $C_{1,0}$ = [3, 4] · [5, 7] = 3×5 + 4×7 = **43**
- $C_{1,1}$ = [3, 4] · [6, 8] = 3×6 + 4×8 = **50**

$$C = \begin{bmatrix} 19 & 22 \\ 43 & 50 \end{bmatrix}$$

### 1.3 Python 验证

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A @ B)
# [[19 22]
#  [43 50]]

# 或者：np.matmul(A, B)、np.dot(A, B) 结果一样
```

### 1.4 Java 工程师视角

本质就是**嵌套循环**：

```java
// 伪代码
for (int i = 0; i < m; i++) {
    for (int j = 0; j < p; j++) {
        double sum = 0;
        for (int k = 0; k < n; k++) {
            sum += A[i][k] * B[k][j];
        }
        C[i][j] = sum;
    }
}
```

但 NumPy / PyTorch 会用 **SIMD + GPU** 加速，比你自己写快 1000 倍。**不要自己写**。

---

## 二、矩阵乘法的常见形状

### 2.1 向量 × 矩阵

```python
x = np.random.randn(1024)        # shape: (1024,)
W = np.random.randn(1024, 512)   # shape: (1024, 512)
y = x @ W                        # shape: (512,)
```

**LLM 含义**：一个 token 的 1024 维向量，通过权重矩阵 W 变成 512 维。这是神经网络"全连接层"的基本操作。

### 2.2 批量：矩阵 × 矩阵

```python
X = np.random.randn(100, 1024)   # 100 个 token，每个 1024 维
W = np.random.randn(1024, 512)
Y = X @ W                        # shape: (100, 512)
```

**LLM 含义**：一批 token 同时过全连接层。**GPU 并行化的精髓**。

### 2.3 Attention 的 QK^T ⭐

```python
# 假设 batch=1, seq_len=10, d_k=64
Q = np.random.randn(10, 64)   # 10 个 token 的 Query
K = np.random.randn(10, 64)   # 10 个 token 的 Key

# QK^T
scores = Q @ K.T              # shape: (10, 10)
# 含义：scores[i, j] = 第 i 个 token 的 Query 和第 j 个 token 的 Key 的相似度
```

`scores` 就是**注意力矩阵**。每一行表示：这个 token 对其他所有 token 的"关注程度"。

> 💡 **深刻理解**：Attention 的 $QK^T$ 本质上就是**每对 token 之间算一次点积（相似度）**。
> 你 Day 1 学的点积，在这里派上了大用处。

---

## 三、线性变换（Linear Transformation）

### 直觉：矩阵 = 一种变换

给一个向量 $x$，乘一个矩阵 $W$，得到一个新向量 $y = Wx$。

**不同的矩阵 → 不同的变换**：
- 旋转矩阵 → 旋转向量
- 缩放矩阵 → 拉伸/压缩向量
- 投影矩阵 → 把高维投到低维

### LLM 里的"变换"

```python
# Embedding 层：把 token ID 变成向量（这是一个"查表"式变换）
emb = EmbeddingTable[token_id]  # shape: (1024,)

# 线性层（全连接层）：一个矩阵变换
y = emb @ W   # W.shape = (1024, 512)

# 多层堆叠：变换套变换
h1 = x @ W1
h2 = h1 @ W2
h3 = h2 @ W3
# 这就是神经网络
```

**一句话**：神经网络 = **多个矩阵乘法 + 非线性激活函数** 串起来。

---

## 四、特殊矩阵（听过就行，不深挖）

| 矩阵 | 形状 | 长啥样 | 作用 |
|------|-----|-------|-----|
| **单位矩阵 I** | $n \times n$ | 对角线全 1，其他全 0 | $IA = A$，像数字里的 1 |
| **零矩阵** | 任意 | 全 0 | $0 + A = A$ |
| **对角矩阵** | $n \times n$ | 只有对角线有值 | 表示"各维独立的缩放" |
| **对称矩阵** | $n \times n$ | $A^T = A$ | Attention 的某些矩阵会是对称的 |

```python
I = np.eye(3)
print(I)
# [[1. 0. 0.]
#  [0. 1. 0.]
#  [0. 0. 1.]]
```

**本周其他的矩阵分解（特征值分解、SVD）跳过**，等真的要深入算法再回来。

---

## 五、广播（Broadcasting）⭐⭐

### 为什么需要广播

想象这个场景：

```python
X = np.random.randn(100, 1024)   # 100 条向量，每条 1024 维
bias = np.random.randn(1024)     # 一个 1024 维的偏置

# 你想让每一条向量都加上 bias，怎么写？
```

**C 语言/Java 思维**：

```python
for i in range(100):
    X[i] = X[i] + bias   # 累
```

**NumPy 思维**：

```python
X = X + bias   # 一行完事！NumPy 自动把 bias 广播到 100 行上
```

### 广播规则（简化版）

两个数组做运算时，如果形状不同：
1. 从后往前对齐形状
2. **缺失的维度用 1 补齐**
3. 如果某个维度一个是 1、另一个是 n → 把 1 的那个**复制 n 份**
4. 如果维度完全匹配不上 → 报错

### 常见广播案例

```python
# 案例 1：(100, 1024) + (1024,)  →  每行都加
X = np.random.randn(100, 1024)
b = np.random.randn(1024)
Y = X + b                     # ✅ shape: (100, 1024)

# 案例 2：(100, 1024) + (100, 1)  →  每行加一个不同的标量
scale = np.random.randn(100, 1)
Y = X * scale                 # ✅ 每一行乘不同的数

# 案例 3：(100, 1024) + (100,)   →  ❌ 不匹配（后面不对齐）
```

### 为啥你必须懂广播

LLM 代码里广播**无处不在**：
- 加位置编码（每个序列位置加一个向量）
- 加 bias
- LayerNorm / RMSNorm 的归一化参数
- mask 操作

看不懂广播 → 看 LLM 代码时寸步难行。

---

## 六、Attention 公式"带你走一遍"（Preview）

不用看懂细节，感受一下你已经学了多少：

```python
# 假设：batch=1（省略）, seq_len=10, d_k=64

Q = ...   # shape: (10, 64)  ← 线性变换得到的 Query
K = ...   # shape: (10, 64)  ← Key
V = ...   # shape: (10, 64)  ← Value

# 第 1 步：Q 和 K^T 相乘得到相似度矩阵
scores = Q @ K.T             # shape: (10, 10)

# 第 2 步：除以 sqrt(d_k) 缩放（防止值过大）
scores = scores / np.sqrt(64)

# 第 3 步：softmax 归一化成概率（明天 Day 3 讲）
weights = softmax(scores)    # shape: (10, 10)

# 第 4 步：用权重加权 V
output = weights @ V         # shape: (10, 64)
```

**你今天学完已经能看懂 3/4 了**：
- ✅ Q、K、V 是矩阵
- ✅ $QK^T$ 是矩阵乘法
- ✅ 矩阵形状
- ✅ 第 4 步 weights @ V 也是矩阵乘法
- ⏳ softmax 明天讲

---

## 📚 延伸阅读（选做）

- [path-research 的矩阵基础练习](../../../path-research/01-数学与编程基础/1.1-线性代数/练习题/02-矩阵基础.md) — **必看概念部分**
- [path-research 张量与 einsum](../../../path-research/01-数学与编程基础/1.1-线性代数/练习题/07-张量与einsum.md) — 选读（见过 einsum 就行）

> ⚠️ 同样只看概念，不做全部习题。

---

## ✍️ 本日练习

完成 [`练习/day2_练习.py`](./练习/day2_练习.py)：
- 手算矩阵乘法并验证
- 形状对齐判断题
- 模拟 Attention 的 QK^T 计算
- 广播机制测试

---

## 🎯 今日收官清单

- [ ] 我能手算 2×2 矩阵乘法
- [ ] 我能判断 $(3, 5) \times (5, 2)$ 结果形状是啥
- [ ] 我知道 $QK^T$ 在算的是"token 之间的相似度矩阵"
- [ ] 我理解广播机制（至少能看懂 `X + bias`）
- [ ] 我能读懂 `(32, 512, 768)` 这种形状
- [ ] 我知道"神经网络 = 多个矩阵乘法 + 激活函数"

---

## 🔖 下一步

明天 → [Day 3：概率与信息论](./Day3-概率与信息论.md)（学 Softmax 和交叉熵）
