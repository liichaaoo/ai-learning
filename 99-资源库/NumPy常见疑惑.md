# NumPy 常见疑惑速查（跨教程）

> 📌 **使用方式**：写代码遇到 NumPy 报错 / 想不起来怎么写时，按 Ctrl+F 搜索关键词。
>
> 这是跨教程的速查文档（path-engineer 各阶段都可能用），不是从头学的入门教程。

---

## 🧭 速查索引

| 你的困惑 | 跳转 |
|----------|------|
| `axis=0` 还是 `axis=1`？| [§1](#1-axis0-vs-axis1) |
| `keepdims=True` 干嘛的？| [§2](#2-keepdims-为什么需要) |
| 报错 "could not be broadcast"？| [§3](#3-广播报错怎么调试) |
| 怎么做 one-hot？| [§4](#4-one-hot-编码) |
| 怎么算 N×M 距离矩阵？| [§5](#5-两两配对运算nptewaxis-广播) |
| Softmax 怎么写？| [§6](#6-softmax-的写法) |
| `==` 比较得到什么？| [§7](#7--的逐元素比较与mean) |
| `(N,)` 和 `(N, 1)` 区别？| [§8](#8-n-vs-n-1的区别) |
| 怎么调试形状？| [§9](#9-shape-调试技巧) |

---

## 1. axis=0 vs axis=1

### 简短答案

```
axis=0  ↓  纵向（"消除"行维度）
axis=1  →  横向（"消除"列维度）
```

二维数组 `(rows, cols)`：

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])              # (2, 3)

arr.sum(axis=0)   # (3,)  → [5, 7, 9]   ← 第 0 维（rows=2）被消除
arr.sum(axis=1)   # (2,)  → [6, 15]      ← 第 1 维（cols=3）被消除
```

### 在 AI 里的常用对照

| 场景 | 形状 | 用 axis= |
|------|------|---------|
| 对每个样本算预测类别 | `(batch, classes)` | `axis=1`（每行）|
| 算每个特征的均值 | `(samples, features)` | `axis=0`（每列）|
| 取 LLM 下一个 token | `(batch, vocab)` 或 `(batch, seq, vocab)` | `axis=-1`（最后一维）|

> 💡 **`axis=-1` 表示最后一维**，对维度数变化不敏感，AI 代码常用。

---

## 2. `keepdims=True` 为什么需要

### 简短答案

`keepdims=True` 让 reduce 后的维度变成 `1`，**保留维度数**，让广播能继续工作。

```python
arr.shape                                # (2, 3)
arr.sum(axis=1)                          # (2,)     一维
arr.sum(axis=1, keepdims=True)           # (2, 1)   保留为列向量
```

### 什么时候必须用

**reduce 之后还要参与广播运算**时：

```python
# ❌ 不 keepdims：失败
exp_x.shape                              # (8, 5)
sums = exp_x.sum(axis=1)                 # (8,)
exp_x / sums                             # 报错（5 vs 8 对不上）

# ✅ keepdims：成功
sums = exp_x.sum(axis=1, keepdims=True)  # (8, 1)
exp_x / sums                             # ✅ (8,5) / (8,1) → (8,5)
```

### 心法

写 reduce + 后续广播时，**默认加 keepdims=True 不会错**。

---

## 3. 广播报错怎么调试

报错示例：
```
ValueError: operands could not be broadcast together with shapes (8,) (8,5)
```

### 调试三板斧

#### 步骤 1：打印两个数组的 shape

```python
print("a.shape =", a.shape)
print("b.shape =", b.shape)
```

#### 步骤 2：从右往左对齐，逐维度检查

广播规则：从最右边维度开始对齐，每个维度必须满足以下之一：
- 完全相等
- 其中一个是 1
- 其中一个不存在（视为 1）

```
(8, 5)          (8, 5)             (8, 5)
   (5,)         (5,)         vs    (8,)
                ─────                ─────
   ✅ 5=5       从右对齐            ❌ 5 vs 8 错
                 (8,) 等价于 (1,8)
                 然后 1 vs 8 不匹配
```

#### 步骤 3：根据需求修复

| 现状 | 想要 | 解法 |
|------|------|------|
| `(N,)` | `(N, 1)` | `arr[:, np.newaxis]` 或 `arr.reshape(-1, 1)` |
| `(N,)` | `(1, N)` | `arr[np.newaxis, :]` 或 `arr.reshape(1, -1)` |
| `(8, 5)` | `(8, 1)`（用 sum 后）| `sum(axis=1, keepdims=True)` |

---

## 4. One-Hot 编码

### 一行写法

```python
labels = np.array([0, 2, 1, 4, 3])
n_classes = 5
one_hot = np.eye(n_classes)[labels]
# shape: (5, 5)
```

### 原理

1. `np.eye(K)` = 单位矩阵，**第 i 行就是类别 i 的 one-hot**
2. `[labels]` = 花式索引，按 labels 数组**一次性挑多行**

### 反向（one-hot → 类别下标）

```python
np.argmax(one_hot, axis=1)   # 取每行 1 的位置
```

---

## 5. 两两配对运算（np.newaxis 广播）

### 场景

`A.shape = (M, D)`，`B.shape = (N, D)`，想得到 `(M, N)` 的距离矩阵。

### 标准模式

```python
diff = A[:, np.newaxis, :] - B[np.newaxis, :, :]   # (M, N, D)
distances = np.linalg.norm(diff, axis=2)            # (M, N)
```

### 类似模式

```python
# 两两点积（attention 的 QK^T）
A.shape = (M, D), B.shape = (N, D)
scores = A @ B.T                # (M, N)  ← 比 newaxis 更简洁

# 两两余弦相似度
A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
similarities = A_norm @ B_norm.T   # (M, N)
```

### 心法

> 看到 `(M, D)` 和 `(N, D)` 想要 `(M, N)` → **几乎一定是 newaxis + 广播**，或者 `A @ B.T`。

---

## 6. Softmax 的写法

### 一维

```python
def softmax_1d(x):
    exp_x = np.exp(x - x.max())   # 减最大值防溢出
    return exp_x / exp_x.sum()
```

### 二维（沿 axis=1）

```python
def softmax_2d(logits):
    # logits.shape = (batch, classes)
    exp_x = np.exp(logits - logits.max(axis=1, keepdims=True))
    return exp_x / exp_x.sum(axis=1, keepdims=True)
```

### 通用版（任意维度）

```python
def softmax(x, axis=-1):
    exp_x = np.exp(x - x.max(axis=axis, keepdims=True))
    return exp_x / exp_x.sum(axis=axis, keepdims=True)
```

### 注意

- **必须减最大值**（防止 `np.exp(很大的数)` 溢出，工程必备）
- **必须 `keepdims=True`**（否则广播失败）

---

## 7. `==` 的逐元素比较 与 `.mean()`

### 关键差异

```python
# Python list（整体比较）
[1, 2, 3] == [1, 2, 3]              # True

# NumPy（逐元素比较）
np.array([1,2,3]) == np.array([1,2,4])
# array([ True,  True, False])
```

### 算占比 / 准确率的标准模式

```python
# 准确率
acc = (predictions == labels).mean()

# 大于阈值的占比
ratio = (probs > 0.5).mean()

# 满足条件的样本数
count = (data > 0).sum()
```

**记忆**：**布尔数组的 `.mean()` = 满足条件的比例**（True=1, False=0）。

---

## 8. `(N,)` vs `(N, 1)` 的区别

### 形状不同

```python
a = np.array([1, 2, 3])
a.shape           # (3,)    一维向量

b = a.reshape(-1, 1)
b.shape           # (3, 1)  列向量（二维）

c = a.reshape(1, -1)
c.shape           # (1, 3)  行向量（二维）
```

### 哪些场景必须区分

#### sklearn 等库通常要求二维

```python
from sklearn.linear_model import LinearRegression

X = np.array([1, 2, 3, 4])         # (4,)
model.fit(X, y)                    # ❌ 报错：要二维输入

X = np.array([1, 2, 3, 4]).reshape(-1, 1)   # (4, 1)
model.fit(X, y)                    # ✅
```

#### 矩阵乘法

```python
A = np.array([1, 2, 3])         # (3,)
B = np.array([4, 5, 6])         # (3,)
A @ B    # 6+10+18 = 32（标量，点积）

A = A.reshape(-1, 1)            # (3, 1)
B = B.reshape(1, -1)            # (1, 3)
A @ B    # (3, 3) 外积！
```

### 转换 cheatsheet

```python
arr.reshape(-1, 1)         # 任意 → (N, 1)
arr.reshape(1, -1)         # 任意 → (1, N)
arr.reshape(-1)            # 任意 → 一维 (N,)
arr.flatten()              # 任意 → 一维 (N,)（拷贝）
arr.ravel()                # 任意 → 一维 (N,)（视图，更快）
arr[:, np.newaxis]         # (N,) → (N, 1)
arr[np.newaxis, :]         # (N,) → (1, N)
arr.squeeze()              # 移除所有大小为 1 的维度
```

---

## 9. Shape 调试技巧

### 打印一切

```python
def debug_shape(name, arr):
    print(f"{name}: shape={arr.shape}, dtype={arr.dtype}")

debug_shape("logits", logits)
debug_shape("probs", probs)
```

### 用 assert 锁定形状

```python
assert logits.shape == (batch_size, num_classes), \
    f"logits 形状错: {logits.shape}"
```

### 中间过程一步步打

```python
# 不要一行串太长
diff = A[:, None, :] - B[None, :, :]
print("diff:", diff.shape)            # 验证 (M, N, D)

dist = np.linalg.norm(diff, axis=2)
print("dist:", dist.shape)            # 验证 (M, N)

nearest = np.argmin(dist, axis=1)
print("nearest:", nearest.shape)      # 验证 (M,)
```

---

## 🔗 相关文档

- [Day 4 NumPy 基础（含卡点专题）](../path-engineer/01-基础速通/Week1-Python速通/Day4-NumPy基础.md)
- [Day 4 练习精讲答案](../path-engineer/01-基础速通/Week1-Python速通/练习/day4_练习_精讲答案.md)
- [Week 3 数学补盲（向量/矩阵/Softmax）](../path-engineer/01-基础速通/Week3-数学补盲/)

---

## 📌 本文档维护

每次你在做练习/项目时遇到新的 NumPy 卡点，把它**加进来**，这样未来翻这一份就能解决 95% 的疑惑。
