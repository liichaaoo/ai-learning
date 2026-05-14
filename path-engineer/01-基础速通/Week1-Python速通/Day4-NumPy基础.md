# Day 4 · NumPy 基础

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解 AI 数据的"基础单位" `ndarray`，看懂矩阵运算
> 📋 练习：[`练习/day4_练习.py`](./练习/day4_练习.py)

---

## 0. 心法

> **AI 的"原材料"是张量（tensor），NumPy 的 `ndarray` 是它的简化版。**
>
> 你今天学完，就能：
> - 看懂 `tensor.shape`、`tensor[:, 0]`、`a @ b`
> - 理解 PyTorch 90% 的数据处理代码

---

## 1. 为什么需要 NumPy？（5 分钟）

### Python 原生 list 的问题

```python
# 想给一个列表每个元素 * 2
nums = [1, 2, 3, 4, 5]

# 方法 1：循环（慢 + 啰嗦）
result = []
for x in nums:
    result.append(x * 2)

# 方法 2：推导式（还行）
result = [x * 2 for x in nums]
```

数据量小没问题，但**机器学习数据动辄百万行**，Python 循环慢到无法接受。

### NumPy 解决：向量化运算 ⭐

```python
import numpy as np

nums = np.array([1, 2, 3, 4, 5])
result = nums * 2                # [2, 4, 6, 8, 10]，**一次完成**

# 速度对比：百万元素
# 原生 Python: ~200ms
# NumPy:       ~2ms（快 100 倍）
```

> 💡 **NumPy 底层是 C 写的**，避免了 Python 循环的解释器开销。

---

## 2. 创建 ndarray（10 分钟）

### 安装确认

```bash
python3 -c "import numpy as np; print(np.__version__)"
# 应该看到版本号（你已经装过了）
```

### 创建方式

```python
import numpy as np

# 1. 从 list
a = np.array([1, 2, 3, 4])
print(a)              # [1 2 3 4]
print(type(a))        # <class 'numpy.ndarray'>

# 2. 二维
b = np.array([[1, 2, 3], [4, 5, 6]])
print(b)
# [[1 2 3]
#  [4 5 6]]

# 3. 全 0 / 全 1 数组（指定形状）
zeros = np.zeros((3, 4))      # 3 行 4 列全 0
ones = np.ones((2, 3))         # 2 行 3 列全 1
print(zeros)
# [[0. 0. 0. 0.]
#  [0. 0. 0. 0.]
#  [0. 0. 0. 0.]]

# 4. 单位矩阵
eye = np.eye(3)                # 3x3 单位矩阵
# [[1. 0. 0.]
#  [0. 1. 0.]
#  [0. 0. 1.]]

# 5. 等差数列
seq = np.arange(0, 10, 2)      # [0 2 4 6 8]（类似 range）
linear = np.linspace(0, 1, 5)  # [0. 0.25 0.5 0.75 1.] 等分

# 6. 随机数 ⭐ AI 必用
np.random.seed(42)             # 固定随机种子（保证可复现）
rand = np.random.rand(2, 3)    # 2x3 [0,1) 均匀分布
randn = np.random.randn(2, 3)  # 2x3 标准正态分布
randint = np.random.randint(0, 10, (2, 3))   # 2x3 [0,10) 整数
```

---

## 3. ndarray 的核心属性 ⭐ 必懂（10 分钟）

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.shape         # (2, 3)         形状（行数, 列数）⭐⭐⭐
a.ndim          # 2              维度数（几维）
a.size          # 6              元素总数
a.dtype         # int64          数据类型
a.T             # 转置
```

### 看懂 shape ⭐⭐⭐

> **AI 代码里 90% 的 bug 都和 shape 不匹配有关。**

```python
# 1 维：(n,)
a = np.array([1, 2, 3])
print(a.shape)        # (3,)        长度 3 的向量

# 2 维：(行, 列)
b = np.array([[1, 2, 3], [4, 5, 6]])
print(b.shape)        # (2, 3)      2 行 3 列矩阵

# 3 维：(N, H, W) 或 (batch, height, width)
c = np.zeros((10, 28, 28))
print(c.shape)        # (10, 28, 28)  10 张 28x28 图片

# 4 维：图像 batch (batch, channel, height, width)
d = np.zeros((32, 3, 224, 224))
print(d.shape)        # (32, 3, 224, 224)  32 张 3 通道 224x224 图片

# AI 圈常见 shape 速查
# 文本 batch:   (batch, seq_len)             如 (32, 512)
# 图像 batch:   (batch, channels, H, W)      如 (32, 3, 224, 224)
# Embedding:    (vocab_size, dim)            如 (50000, 768)
# Attention 矩阵:(batch, heads, seq, seq)    如 (32, 12, 512, 512)
```

### 修改 shape：reshape ⭐

```python
a = np.arange(12)
print(a.shape)          # (12,)

b = a.reshape(3, 4)
print(b.shape)          # (3, 4)
print(b)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

# -1 表示"自动计算"
c = a.reshape(2, -1)    # 2 行，列自动算 = 6
d = a.reshape(-1, 3)    # 列固定 3，行自动 = 4

# flatten：变 1 维
e = b.flatten()         # [0, 1, 2, ..., 11]
```

---

## 4. 索引和切片 ⭐⭐⭐（25 分钟）

> **重点中的重点**。看懂这一节 = 看懂 PyTorch 数据预处理代码。

### 1 维索引（和 list 一样）

```python
a = np.array([10, 20, 30, 40, 50])
a[0]            # 10
a[-1]           # 50
a[1:4]          # [20 30 40]
a[::2]          # [10 30 50]
```

### 2 维索引（重点）⭐

```python
a = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
])
print(a.shape)      # (3, 4)

# 第 0 行
a[0]                # [1 2 3 4]
a[0, :]             # 等价

# 第 0 列 ⭐
a[:, 0]             # [1 5 9]

# 子矩阵
a[1:3, 1:3]
# [[6 7]
#  [10 11]]

# 单个元素
a[1, 2]             # 7
```

### 多维切片实战 ⭐

```python
# 假设有一批图片：(10 张, 高 28, 宽 28)
images = np.random.rand(10, 28, 28)

images[0]                # 第 0 张图片，shape (28, 28)
images[0:5]              # 前 5 张，shape (5, 28, 28)
images[:, 0, :]          # 所有图片的第 0 行，shape (10, 28)
images[:, :, 0]          # 所有图片的第 0 列，shape (10, 28)
images[0, 10:20, 10:20]  # 第 0 张图片的中间区域，shape (10, 10)
```

> 💡 看 PyTorch 代码 `tensor[:, 0]` 就是"取所有 batch 的第 0 个特征"。

### 布尔索引（条件筛选）⭐⭐

```python
a = np.array([1, 5, 2, 8, 3, 9])

# 找出 > 3 的元素
mask = a > 3                # [F T F T F T]
result = a[mask]            # [5 8 9]
# 或一行
result = a[a > 3]           # [5 8 9] ⭐

# 用条件修改
a[a > 5] = 0                # 把所有 > 5 的设为 0
```

### 花式索引（用列表选取多个）

```python
a = np.array([10, 20, 30, 40, 50])
a[[0, 2, 4]]            # [10 30 50]   选第 0, 2, 4 个
a[[4, 0, 2]]            # [50 10 30]   顺序可以打乱
```

---

## 5. 数学运算 ⭐⭐（20 分钟）

### 基础运算（向量化）⭐

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

a + b               # [5 7 9]      逐元素加
a - b               # [-3 -3 -3]
a * b               # [4 10 18]    逐元素乘（不是矩阵乘！）
a / b               # [0.25 0.4 0.5]
a ** 2              # [1 4 9]      逐元素平方
np.sqrt(a)          # 平方根

# 标量广播
a + 10              # [11 12 13]
a * 2               # [2 4 6]
```

### 矩阵乘法 vs 逐元素乘法 ⭐⭐⭐ 必区分

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 逐元素乘（同位置相乘）
A * B
# [[5 12]
#  [21 32]]

# 矩阵乘（线代意义上的）⭐ AI 中真正常用
A @ B               # ⭐ Python 3.5+ 的矩阵乘运算符
np.matmul(A, B)     # 等价
A.dot(B)            # 也等价
# [[19 22]
#  [43 50]]
```

> 💡 看 PyTorch 代码 `out = x @ W + b` 就是经典的"全连接层" `y = xW + b`。

### 常用统计函数

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.sum()             # 21       全部相加
a.mean()            # 3.5      平均
a.min() / a.max()   # 1 / 6
a.std()             # 标准差

# 沿某个轴 ⭐
a.sum(axis=0)       # [5 7 9]      沿"行"方向相加（结果是按列）
a.sum(axis=1)       # [6 15]       沿"列"方向相加（结果是按行）
a.mean(axis=0)      # [2.5 3.5 4.5]
```

### axis 怎么记？⭐

```
axis=0: 沿"行的方向"运算（结果保留列数）
axis=1: 沿"列的方向"运算（结果保留行数）

axis=N: "压缩第 N 个维度"
```

---

## 6. 广播机制（Broadcasting）⭐ 重点（10 分钟）

### 现象：不同 shape 也能运算

```python
a = np.array([[1, 2, 3], [4, 5, 6]])    # shape (2, 3)
b = np.array([10, 20, 30])               # shape (3,)

# Java 思维觉得这不该 work，但 NumPy：
result = a + b
# [[11 22 33]
#  [14 25 36]]
# b 自动"广播"到每一行
```

### 广播规则（简化版）

> 两个 shape 从右往左看，如果对应位置 **相等** 或 **其中一个是 1**，就能广播。

```python
# 例 1：能广播
A.shape = (3, 4)
B.shape = (   4,)         # 看作 (1, 4)，会扩展到 (3, 4)
A + B    ✅

# 例 2：能广播
A.shape = (3, 1)
B.shape = (1, 4)
A + B    ✅  结果 shape (3, 4)

# 例 3：不能广播
A.shape = (3, 4)
B.shape = (3,)
A + B    ❌  从右往左对，4 和 3 不相等也不为 1
```

### 实用：标量减均值（数据归一化）

```python
data = np.random.rand(100, 5)        # 100 条样本，5 个特征
mean = data.mean(axis=0)             # shape (5,) 每列均值
std = data.std(axis=0)               # shape (5,) 每列标准差

# 广播 ⭐
normalized = (data - mean) / std     # shape (100, 5)
# 每个样本都减去对应列的均值，除以对应列的 std
```

> 💡 这就是 sklearn `StandardScaler` 的内部逻辑。

---

## 6.5 卡点专题：4 个最容易迷的 API ⭐⭐⭐

> 这一节是从真实学习反馈整理出来的"4 大卡点"。
> 如果你做练习题 7-9 卡住了，回来读这里。

### 🧱 卡点 1：`axis=0` 和 `axis=1` 到底沿哪个方向？

**最常见的混淆**。规则：

```
axis=0  ↓  纵向（结果"消除"行维度）
axis=1  →  横向（结果"消除"列维度）
```

二维数组形状 `(rows, cols)`，做 `.sum(axis=N)` 时：
- **`axis=N` 那个维度被"压扁"消失**

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])           # shape (2, 3)

arr.sum(axis=0)   # shape (3,)        ← axis=0 消失，剩列方向 [5, 7, 9]
arr.sum(axis=1)   # shape (2,)        ← axis=1 消失，剩行方向 [6, 15]
```

**记忆法**：

| 场景 | 用 `axis=` |
|------|-----------|
| 对每一**行**做 reduce（每个样本算一个值）| `axis=1` |
| 对每一**列**做 reduce（每个特征算一个值）| `axis=0` |

例子（你常见到的 AI 用法）：
```python
logits.shape = (8, 5)             # 8 个样本，每行一个，5 个类别得分

np.argmax(logits, axis=1)         # 每行选 top 类别 → shape (8,)
np.argmax(logits, axis=0)         # 每列选 top 样本 → shape (5,)（很少这么干）
```

---

### 🧱 卡点 2：`keepdims=True` 是干嘛的？

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])              # (2, 3)

arr.sum(axis=1)                          # shape (2,)      ← 一维
arr.sum(axis=1, keepdims=True)           # shape (2, 1)    ← 列向量
```

#### 用在哪？

**只要你 reduce 之后还要参与广播运算，几乎都要 `keepdims=True`**。

举个 softmax 例子：

```python
logits = np.random.randn(8, 5)           # (8, 5)
exp_x = np.exp(logits)                   # (8, 5)

# ❌ 不 keepdims
sums = exp_x.sum(axis=1)                 # (8,) 一维
exp_x / sums                             # 报错：(8,5) 和 (8,) 不能广播

# ✅ keepdims
sums = exp_x.sum(axis=1, keepdims=True)  # (8, 1)
exp_x / sums                             # ✅ (8,5) / (8,1) 广播成 (8,5)
```

#### 为什么广播规则是这样

NumPy 广播**从右往左**对齐维度：

```
(8, 5)
   (8,)        ← 不 keepdims 时，对齐 5 vs 8 → 不匹配 ❌
─────
(8, 5)
(8, 1)        ← keepdims 时，5 vs 1 → 1 自动复制 5 份 ✅
─────
(8, 5)
```

**一句话**：`keepdims=True` 让 reduce 后的维度变成 `1`（不是消失），这样广播能继续工作。

---

### 🧱 卡点 3：`np.eye(K)[labels]` 为什么能做 one-hot？

#### 第 1 步：`np.eye(K)` = 单位矩阵

```python
np.eye(5)
# array([[1., 0., 0., 0., 0.],   ← 第 0 行 = 类别 0 的 one-hot
#        [0., 1., 0., 0., 0.],   ← 第 1 行 = 类别 1 的 one-hot
#        [0., 0., 1., 0., 0.],
#        [0., 0., 0., 1., 0.],
#        [0., 0., 0., 0., 1.]])
```

🤯 关键观察：**单位矩阵的第 i 行就是类别 i 的 one-hot 向量**！

#### 第 2 步：花式索引（fancy indexing）

NumPy 允许用一个**数组**作为下标，按这个数组**一次性挑多行**：

```python
arr = np.array([10, 20, 30, 40, 50])
arr[[0, 2, 4]]    # array([10, 30, 50])
arr[[2, 2, 0]]    # array([30, 30, 10])    ← 可重复
```

二维数组同理：
```python
I = np.eye(5)
labels = np.array([0, 2, 1, 4, 3, 0])
I[labels]
# 等价于 [I[0], I[2], I[1], I[4], I[3], I[0]]
# 结果 shape: (6, 5)
```

正好就是 one-hot 编码！

#### 完整代码（生产可用）

```python
def one_hot(labels: np.ndarray, num_classes: int) -> np.ndarray:
    return np.eye(num_classes)[labels]

one_hot(np.array([0, 2, 1]), 5)
# array([[1., 0., 0., 0., 0.],
#        [0., 0., 1., 0., 0.],
#        [0., 1., 0., 0., 0.]])
```

> 💡 这种"利用单位矩阵 + 花式索引"的写法，就是 **NumPy 思维替代 for 循环**的典型例子。

---

### 🧱 卡点 4：`np.newaxis` / `None` 加维度做"批量配对运算"

最难但最实用的一招。

#### 场景

5 个测试样本 vs 100 个训练样本，**两两算距离**（5×100 = 500 对距离）。
不写 for 循环怎么办？

#### 核心技巧：扩展维度让广播帮忙

```python
X_test.shape    # (5, 4)
X_train.shape   # (100, 4)

# 给 X_test 在中间插一个维度
X_test[:, np.newaxis, :].shape    # (5, 1, 4)
# 等价: X_test[:, None, :]

# 给 X_train 在最前插一个维度
X_train[np.newaxis, :, :].shape   # (1, 100, 4)
# 等价: X_train[None, :, :]

# 两者相减，广播自动扩展
diff = X_test[:, None, :] - X_train[None, :, :]
diff.shape    # (5, 100, 4)
```

#### 广播过程图解

```
(5,   1, 4)   ← X_test[:, None, :]
(1, 100, 4)   ← X_train[None, :, :]
─────────────  逐维度对齐：
                第 0 维  5 vs 1  → 5（1 复制成 5）
                第 1 维  1 vs 100 → 100（1 复制成 100）
                第 2 维  4 vs 4   → 4 ✅
(5, 100, 4)
```

`diff[i, j, :]` 就是 "第 i 个测试样本 - 第 j 个训练样本" 的差向量。

#### 然后算距离 + 找最近

```python
# 欧氏距离矩阵 (5, 100)
distances = np.linalg.norm(diff, axis=2)
# 等价: np.sqrt((diff ** 2).sum(axis=2))

# 每行最近的训练样本下标
nearest = np.argmin(distances, axis=1)   # (5,)

# 取对应训练标签作为预测
predictions = y_train[nearest]           # (5,)
```

**6 行代码 = 一个完整的 1-NN 分类器**。
对应 for 循环写法约 15 行 + 慢 100 倍。

> 💡 **`np.newaxis` 心法**：
> "**我有 (5,4) 和 (100,4)，想要 (5,100) 的结果**" → 几乎一定是用 newaxis + 广播。
> 这是 PyTorch、Transformer 里 attention 操作的同款思路。

---

### 卡点速查表

| 现象 / 困惑 | 解法 |
|------------|------|
| 不知道 axis 选 0 还是 1 | 想"哪个维度被消除" |
| 报错 "cannot be broadcast" | 检查形状，可能要 `keepdims=True` |
| 想做 one-hot | `np.eye(K)[labels]` |
| 想做 (M,) 和 (N,) 两两运算 | `arr1[:, None] op arr2[None, :]` → (M, N) |
| 想算距离矩阵 | `np.linalg.norm(A[:,None,:] - B[None,:,:], axis=2)` |

---

## 7. 实用函数速查（10 分钟）

```python
import numpy as np

# 数组拼接
np.concatenate([a, b], axis=0)   # 按行拼（增加行数）
np.concatenate([a, b], axis=1)   # 按列拼（增加列数）
np.vstack([a, b])                # 垂直堆叠（同 axis=0）
np.hstack([a, b])                # 水平堆叠（同 axis=1）

# 维度操作
a.reshape(-1, 3)                 # 重塑
a.flatten()                      # 拉平成 1 维
a[np.newaxis, :]                 # 增加一个维度（shape 从 (3,) 变 (1, 3)）
a[:, np.newaxis]                 # shape 从 (3,) 变 (3, 1)
np.expand_dims(a, axis=0)        # 等价 a[np.newaxis, :]
np.squeeze(a)                    # 去掉所有大小为 1 的维度

# 找位置
np.argmax(a)                     # 返回最大值的索引
np.argmin(a)
np.argmax(a, axis=1)             # 沿 axis=1 找最大值索引（多分类预测常用）

# 排序
np.sort(a)
np.argsort(a)                    # 返回排序后的索引

# 比较
np.where(a > 5, 1, 0)            # a 中 >5 的变 1，其他变 0（类似三元）
np.isnan(a)                      # 检查 NaN
np.allclose(a, b)                # 浮点数相等比较 ⭐
```

---

## 8. AI 实战的 NumPy 模式（10 分钟）

### 模式 1：one-hot 编码

```python
# 假设有 5 个类别的标签
labels = np.array([0, 2, 1, 4, 3])
n_classes = 5

# 一行 one-hot
one_hot = np.eye(n_classes)[labels]
# array([[1., 0., 0., 0., 0.],
#        [0., 0., 1., 0., 0.],
#        [0., 1., 0., 0., 0.],
#        [0., 0., 0., 0., 1.],
#        [0., 0., 0., 1., 0.]])
```

### 模式 2：余弦相似度（Embedding 必用）⭐

```python
# 两个向量
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print(cos_sim)        # 0.97
```

### 模式 3：批量数据归一化

```python
data = np.random.rand(100, 10)              # 100 个 10 维样本
data_norm = (data - data.mean(axis=0)) / data.std(axis=0)
```

### 模式 4：argmax 取分类结果

```python
# 模型输出：每个样本对 5 个类别的得分
logits = np.random.randn(8, 5)              # 8 个样本，5 类

predictions = np.argmax(logits, axis=1)     # shape (8,) 每个是预测类别
print(predictions)                          # 例如 [3 1 4 0 2 1 4 3]
```

---

## 📋 今日任务清单

- [ ] 装 NumPy（已装）
- [ ] 通读本文档，**所有代码都在 IPython / Jupyter 里跑一遍**
- [ ] 重点掌握：**shape**、**切片**、**broadcasting**、**矩阵乘 `@`**
- [ ] 完成 [`练习/day4_练习.py`](./练习/day4_练习.py)
- [ ] 自测：随便给一个 `(N, 28, 28)` 的数组，能用几种方式获取它的子集？

---

## 🎯 自测：今天你应该能...

- [ ] 看懂 `tensor.shape` 的含义
- [ ] 用 `arr[:, 0]` 取所有行的第 0 列
- [ ] 区分 `*` 和 `@`
- [ ] 解释 broadcasting 是什么
- [ ] 用一行代码给 100x10 的数据做归一化

---

## 🔍 推荐再看

- [NumPy 官方 Quickstart](https://numpy.org/doc/stable/user/quickstart.html)（30 分钟）
- [一图看懂 NumPy 索引](https://numpy.org/doc/stable/user/basics.indexing.html)

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 5 · 综合演练](./Day5-综合演练.md)。
