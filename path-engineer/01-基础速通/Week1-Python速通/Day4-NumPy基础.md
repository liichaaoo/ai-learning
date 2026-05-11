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
