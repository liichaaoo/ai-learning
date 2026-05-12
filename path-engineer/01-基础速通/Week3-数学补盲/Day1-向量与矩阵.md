# Day 1 · 向量与矩阵（从 LLM 视角理解）

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**能看懂 Embedding，能手算 cosine 相似度**

---

## 🧭 今天的核心问题

> 用户问 "苹果公司财报"，RAG 系统怎么从 10000 篇文档里找到最相关的 3 篇？

**答案**：把所有文档变成**向量**，用**向量距离**衡量相似度。

**这就是今天要学的**。

---

## 一、向量（Vector）是什么？

### 数学定义
**一组有序的数字**。比如：
$$\mathbf{v} = [3, 1, 4, 1, 5]$$
这是一个 5 维向量。

### Java 工程师的视角

```java
// 向量就像这个：
double[] v = {3, 1, 4, 1, 5};
```

就这么简单。**不要把它想得太"数学"**。

### LLM 里的向量

一段话、一张图、一条商品，都可以变成向量：

```python
# 用 embedding 模型把文本转成向量
text = "苹果公司发布新手机"
vec = embed(text)
# vec.shape = (1024,)   ← 这就是一个 1024 维向量
# 里面是 1024 个小数：[0.03, -0.41, 0.77, ..., 0.12]
```

这个向量是**这句话的"数学表示"**。
相近意思的两句话 → 向量也相近。

---

## 二、向量的基本运算（只学 4 个）

假设两个向量 $\mathbf{a} = [1, 2, 3]$，$\mathbf{b} = [4, 5, 6]$。

### 2.1 加法 / 减法

$$\mathbf{a} + \mathbf{b} = [1+4, 2+5, 3+6] = [5, 7, 9]$$

**一句话**：对应位置相加。

```python
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)   # [5 7 9]
print(a - b)   # [-3 -3 -3]
```

### 2.2 标量乘法

$$2 \cdot \mathbf{a} = [2, 4, 6]$$

**一句话**：每个元素都乘。

```python
print(2 * a)   # [2 4 6]
```

### 2.3 点积 ⭐⭐⭐（今天最重要的运算）

$$\mathbf{a} \cdot \mathbf{b} = 1 \cdot 4 + 2 \cdot 5 + 3 \cdot 6 = 4 + 10 + 18 = 32$$

**一句话**：**对应位置相乘再求和，返回一个数**。

```python
print(np.dot(a, b))      # 32
print(a @ b)             # 32（@ 是 Python 3.5+ 的矩阵乘法符号）
print((a * b).sum())     # 32（手动验算）
```

#### 🎯 点积的含义（必记）

- 点积 **大** → 两个向量**方向相近**
- 点积 **= 0** → 两个向量**互相垂直**（毫不相关）
- 点积 **小/负** → 方向相反

**LLM 里的意义**：点积可以**衡量两个向量的相似度**。

### 2.4 范数（长度）

向量的"长度"。常见两种：

**L2 范数（欧几里得范数，最常用）**：
$$\|\mathbf{a}\|_2 = \sqrt{1^2 + 2^2 + 3^2} = \sqrt{14} \approx 3.74$$

**L1 范数（曼哈顿距离）**：
$$\|\mathbf{a}\|_1 = |1| + |2| + |3| = 6$$

```python
print(np.linalg.norm(a))         # 3.74... (L2)
print(np.linalg.norm(a, ord=1))  # 6      (L1)
```

#### 🎯 L1 vs L2 在 AI 里的区别

| 范数 | 别名 | 特点 | 用在哪 |
|------|-----|------|-------|
| **L1** | 曼哈顿距离 | 把不重要特征压成 0（稀疏） | 特征选择、Lasso |
| **L2** | 欧几里得距离 | 把所有权重都变小但不为 0 | 正则化（Ridge）、梯度计算 |

这对应 Day 4（Week 2）讲的**正则化**。

---

## 三、Cosine 相似度（RAG 的命根）⭐⭐⭐

### 为什么不直接用点积？

假设有两个向量：
- $\mathbf{a} = [1, 0]$
- $\mathbf{b} = [100, 0]$（和 a 方向完全一样，但更长）

它们的点积 $= 1 \cdot 100 + 0 \cdot 0 = 100$，看起来很大。

但实际上 **b 只是 a 的放大版**，语义上应该是"完全相同"。

**结论**：**点积受向量长度影响**。

### Cosine 相似度的定义

$$\text{cos\_sim}(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \cdot \|\mathbf{b}\|}$$

**一句话**：**点积除以两个长度的乘积**，结果在 $[-1, 1]$ 之间，**不受向量长度影响**，只看方向。

| 值 | 含义 |
|----|------|
| 1 | 完全相同方向（最相似） |
| 0 | 互相垂直（毫不相关） |
| -1 | 完全相反方向 |

### 用 Python 算

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

a = np.array([1, 2, 3])
b = np.array([2, 4, 6])   # 是 a 的 2 倍
c = np.array([1, 0, 0])

print(cosine_similarity(a, b))   # 1.0  ← 方向完全一致
print(cosine_similarity(a, c))   # 0.27 ← 有一定相似
```

### 🎯 RAG 中的完整用法

```python
# 1. 把用户问题转向量
query_vec = embed("苹果公司财报")

# 2. 所有文档向量已经预先算好存在向量库
doc_vecs = load_from_vector_db()   # shape: (10000, 1024)

# 3. 逐个算相似度
similarities = [cosine_similarity(query_vec, doc_vec) for doc_vec in doc_vecs]

# 4. 取相似度最高的 Top-3
top_3_idx = np.argsort(similarities)[-3:]
```

**这就是 RAG 检索的核心**。你已经懂了底层数学。

---

## 四、矩阵（Matrix）

### 数学定义
**一堆数排成的长方形阵列**：
$$A = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix}$$

这是一个 **2 行 3 列** 的矩阵，记作 $A \in \mathbb{R}^{2 \times 3}$。

### Java 工程师视角

```java
double[][] A = {
    {1, 2, 3},
    {4, 5, 6}
};
// A.length       = 2  (行数)
// A[0].length    = 3  (列数)
```

就是**二维数组**。

### NumPy 中的矩阵

```python
A = np.array([[1, 2, 3],
              [4, 5, 6]])
print(A.shape)   # (2, 3)  ← 2 行 3 列
print(A.ndim)    # 2       ← 2 维
```

---

## 五、AI 里的矩阵都有啥？

下面这些是你在 LLM 世界会**反复见到**的：

### 5.1 一批样本

```python
# 100 条文本，每条 1024 维 embedding
batch = np.random.randn(100, 1024)   # shape: (100, 1024)
# 第 i 条文本的向量： batch[i]  或  batch[i, :]
```

### 5.2 神经网络的权重矩阵

```python
# 输入 768 维，输出 512 维的全连接层
W = np.random.randn(768, 512)   # shape: (768, 512)
# 前向传播： output = input @ W
```

### 5.3 Attention 中的 Q/K/V 矩阵

后面 Transformer 里会学到，现在只要知道**它们都是矩阵**。

---

## 六、矩阵的形状（极其重要）⭐

工程里**80% 的 bug 来自形状不匹配**。必须会读：

| 形状 | 在 LLM 里通常意思 |
|------|-----------------|
| `(batch_size, dim)` | 一批向量（每行一个样本） |
| `(batch_size, seq_len, dim)` | 一批文本（每条文本是 seq_len 个 token，每个 token 是 dim 维）|
| `(num_heads, seq_len, seq_len)` | Multi-head Attention 的注意力矩阵 |

你看论文、看代码时**先看形状**，比看公式还重要。

```python
# 总是第一件事：打印形状
x = some_tensor
print(x.shape)   # 先看形状，再理解
```

---

## 七、转置（Transpose）

把矩阵的行和列交换：

$$A = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix}, \quad A^T = \begin{bmatrix} 1 & 4 \\ 2 & 5 \\ 3 & 6 \end{bmatrix}$$

原来 $(2, 3)$，转置后变 $(3, 2)$。

```python
A = np.array([[1, 2, 3], [4, 5, 6]])
print(A.T)
# [[1 4]
#  [2 5]
#  [3 6]]
print(A.T.shape)   # (3, 2)
```

**记忆法**：转置 = "躺着变站着"。符号 $A^T$ 或 `.T`。

Attention 公式 $QK^T$ 就用到了转置，明天讲。

---

## 📚 延伸阅读（30 分钟内读完即可）

- **必读**：[path-research 的向量练习题](../../../path-research/01-数学与编程基础/1.1-线性代数/练习题/01-向量.md)（只看概念部分，练习题挑 1-2 题做即可）
- **选读**：[path-research 线代 README](../../../path-research/01-数学与编程基础/1.1-线性代数/README.md)

> ⚠️ **提醒**：`path-research/` 里内容深度是"6 周学习计划"，你本周**只有 1 天**。
> **只看概念、跳过证明、挑 1-2 道练习题做**即可。

---

## ✍️ 本日练习

完成 [`练习/day1_练习.py`](./练习/day1_练习.py)：
- 手算点积、范数、cosine 相似度
- 用 NumPy 验证
- 模拟一个"迷你 RAG 检索"

---

## 🎯 今日收官清单

- [ ] 我能用一句话解释什么是向量、什么是矩阵
- [ ] 我能手算两个 3 维向量的点积
- [ ] 我知道 cosine 相似度的计算公式
- [ ] 我知道为什么 RAG 用 cosine 不用点积
- [ ] 我能看 `x.shape = (100, 1024)` 知道是什么意思
- [ ] 我知道 $A^T$ 是什么

---

## 🔖 下一步

明天 → [Day 2：矩阵乘法与线性变换](./Day2-矩阵乘法与线性变换.md)
