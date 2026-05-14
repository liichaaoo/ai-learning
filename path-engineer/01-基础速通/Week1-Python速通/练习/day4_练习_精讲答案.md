# Day 4 练习 · 精讲答案（题 7-9）

> 📌 **写给做练习时卡住的你**：
> 这份不是"标准答案"，是**为什么这么写**的深度讲解。
> 建议：**先自己尝试，卡住再翻这里**；翻完后**关掉再写一次**，看能不能复现。
>
> 重点理解的是 NumPy 思维（"形状思考" vs Java 的"步骤分解"）。
>
> 配套教程：[Day4 §6.5 卡点专题](../Day4-NumPy基础.md#65-卡点专题4-个最容易迷的-api-)

---

## 题 7.1：`argmax` 找每个样本的预测类别

### 任务
```python
logits = np.random.randn(8, 5)   # 8 个样本，每行 5 个类别得分
# 求：每个样本预测得分最高的类别
# 期望 shape: (8,)
```

### 答案
```python
predictions = np.argmax(logits, axis=1)
print(predictions.shape)   # (8,)
```

### 为什么这样写

#### `argmax` vs `max`
| 函数 | 返回 |
|------|------|
| `np.max(arr)` | 最大**值** |
| `np.argmax(arr)` | 最大值的**下标** |

#### `axis=1` 的含义

`logits.shape = (8, 5)` → 每行是一个样本，每列是一个类别。

```python
np.argmax(logits, axis=1)
# = "对每一行单独找最大值的列下标"
# = (8,) 8 个样本对应的预测类别
```

记忆法：**`axis=N` 那个维度被"消除"**：
- `axis=1` → `(8, 5)` 变成 `(8,)`
- `axis=0` → `(8, 5)` 变成 `(5,)`

### 这在 AI 里用在哪
**所有分类模型的"取预测结果"都是这一行**：
- 图像分类：从 1000 类得分里选 top → `argmax(axis=1)`
- LLM 生成下一个 token：从词表里选概率最高的 → `argmax(axis=-1)`

---

## 题 7.2：用布尔运算计算准确率

### 任务
```python
predictions = np.argmax(logits, axis=1)
true_labels = np.array([0, 2, 1, 4, 3, 0, 2, 1])

# 求：预测准确率
```

### 答案
```python
accuracy = (predictions == true_labels).mean()
print(f"准确率：{accuracy:.2%}")
```

### 为什么 `(...).mean()` 就是准确率？

#### 第 1 步：`==` 是逐元素比较

```python
predictions = np.array([3, 1, 0, 4, 3, 0, 1, 2])
true_labels = np.array([0, 2, 1, 4, 3, 0, 2, 1])

predictions == true_labels
# array([False, False, False, True, True, True, False, False])
```

⚠️ **NumPy 和 Python list 不同**：
```python
[1, 2, 3] == [1, 2, 3]              # True（整体比较）
np.array([1,2,3]) == np.array([1,2,3])  # array([True, True, True])（逐元素）
```

#### 第 2 步：布尔在数学运算时被当成 0/1

```python
arr = np.array([False, False, False, True, True, True, False, False])
arr.sum()    # 3   （True 的个数）
arr.mean()   # 3/8 = 0.375  （True 的比例 = 准确率！）
```

### 这种写法的扩展

**"布尔条件 + .mean()"** 这个模式在 AI 代码中无处不在：

```python
# 准确率
acc = (predictions == labels).mean()

# 高置信度样本占比
high_conf = (probs.max(axis=1) > 0.9).mean()

# 错误率
err = (predictions != labels).mean()

# 数据中负数占比
neg_ratio = (data < 0).mean()
```

**记下这个模式**，看 AI 代码会反复见。

---

## 题 7.3：手写 Softmax

### 任务
```python
logits = np.random.randn(8, 5)
# 把 logits 沿 axis=1 转成概率（每行加起来=1）
```

### 答案
```python
exp_x = np.exp(logits)
probs = exp_x / exp_x.sum(axis=1, keepdims=True)

print(probs.shape)         # (8, 5)
print(probs.sum(axis=1))   # 8 个 1.0
```

### 为什么这么写

#### Softmax 公式
$$\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}$$

中文版：**每个数取 e 的指数，再除以本组所有数的指数之和**。

#### 一维版（先理解）
```python
x = np.array([2.0, 1.0, 0.0])

exp_x = np.exp(x)            # [7.39, 2.72, 1.00]
probs = exp_x / exp_x.sum()  # [0.665, 0.245, 0.090] 加起来=1 ✅
```

#### 二维版（关键的 keepdims）

`logits.shape = (8, 5)` → 要**对每一行单独做 softmax**。

```python
exp_x = np.exp(logits)                       # (8, 5)，每个数取指数
row_sums = exp_x.sum(axis=1, keepdims=True)  # (8, 1)，每行的总和
probs = exp_x / row_sums                     # (8, 5) / (8, 1) → (8, 5)
```

#### `keepdims=True` 救命的细节

```python
exp_x.sum(axis=1)               # shape: (8,)    ← 一维
exp_x.sum(axis=1, keepdims=True)# shape: (8, 1)  ← 列向量
```

为什么必须 keepdims？广播规则**从右往左对齐**：
```
exp_x   (8, 5)
sums    (8,)        ← 不 keepdims：5 vs 8 → 不匹配，报错
        ─────
exp_x   (8, 5)
sums    (8, 1)      ← keepdims：5 vs 1 → 1 复制 5 份 ✅
        (8, 5)
```

### Bonus：数值稳定版（生产用这个）

```python
exp_x = np.exp(logits - logits.max(axis=1, keepdims=True))
probs = exp_x / exp_x.sum(axis=1, keepdims=True)
```

减去最大值不影响结果（指数除以指数会抵消），但能避免 `np.exp(很大的数)` 溢出。
详细原理见 [Week 3 Day 3](../../Week3-数学补盲/Day3-概率与信息论.md)。

---

## 题 8：One-Hot 编码

### 任务
```python
labels = np.array([0, 2, 1, 4, 3, 0])
n_classes = 5

# 期望 shape: (6, 5)，把每个类别下标变成对应的 one-hot 向量
```

### 答案
```python
one_hot = np.eye(n_classes)[labels]
print(one_hot.shape)   # (6, 5)
```

**1 行搞定**。这就是 NumPy 思维。

### 为什么 `np.eye(5)[labels]` 能做 one-hot？

#### 第 1 步：`np.eye(5)` 是单位矩阵

```python
np.eye(5)
# array([[1., 0., 0., 0., 0.],   ← 第 0 行 = 类别 0 的 one-hot
#        [0., 1., 0., 0., 0.],   ← 第 1 行 = 类别 1 的 one-hot
#        [0., 0., 1., 0., 0.],   ← 第 2 行 = 类别 2 的 one-hot
#        [0., 0., 0., 1., 0.],   ← 第 3 行 = 类别 3 的 one-hot
#        [0., 0., 0., 0., 1.]])  ← 第 4 行 = 类别 4 的 one-hot
```

🤯 关键观察：**单位矩阵的第 i 行**就是**类别 i 的 one-hot 向量**！

#### 第 2 步：花式索引（fancy indexing）

NumPy 允许用一个数组作为下标，**一次挑多行**：

```python
arr = np.array([10, 20, 30, 40, 50])
arr[[0, 2, 4]]    # array([10, 30, 50])
arr[[2, 2, 0]]    # array([30, 30, 10])    ← 可以重复
```

二维同理：
```python
I = np.eye(5)
labels = np.array([0, 2, 1, 4, 3, 0])
I[labels]
# = [I[0], I[2], I[1], I[4], I[3], I[0]]
# = (6, 5) one-hot 矩阵
```

### Java vs NumPy 对比

```python
# Java 思维（7 行）
one_hot = np.zeros((len(labels), n_classes))
for i, label in enumerate(labels):
    one_hot[i, label] = 1

# NumPy 思维（1 行）
one_hot = np.eye(n_classes)[labels]
```

NumPy 思维=**先观察数据的几何结构**（"单位矩阵的行就是 one-hot"），**再用索引语法表达**。

---

## 题 9：1-NN 分类（综合 boss 战）

### 任务
```python
X_train = np.random.randn(100, 4)   # 100 个训练样本
y_train = np.random.randint(0, 3, 100)
X_test = np.random.randn(5, 4)      # 5 个测试样本

# 求：每个测试样本最近的训练样本对应的类别
# 期望 shape: (5,)
```

### 答案（一气呵成）

```python
# 1. 算 5x100 的距离矩阵
diff = X_test[:, np.newaxis, :] - X_train[np.newaxis, :, :]   # (5, 100, 4)
distances = np.linalg.norm(diff, axis=2)                       # (5, 100)

# 2. 每行最小距离的训练样本下标
nearest = np.argmin(distances, axis=1)                         # (5,)

# 3. 取对应训练标签作预测
predictions = y_train[nearest]                                 # (5,)
```

### 这题考的全部知识点

| 用到的 | 干什么 |
|--------|------|
| `np.newaxis` | 加一个维度让广播能工作 |
| 广播 | (5,1,4) 和 (1,100,4) → (5,100,4) |
| `np.linalg.norm(axis=2)` | 沿"特征"维度算欧氏距离 |
| `argmin(axis=1)` | 每行找最小值下标 |
| 花式索引 `y_train[nearest]` | 用下标数组挑标签 |

### 关键魔法：`np.newaxis` 让广播帮你"两两配对"

#### 你想要的效果
```
对每对 (i, j)，算 X_test[i] - X_train[j]
共 5×100 = 500 对差向量
```

#### 不用 for 循环怎么做？

**给两个数组分别"插一维"**，让广播帮你"两两组合"：

```python
X_test.shape   # (5, 4)
X_train.shape  # (100, 4)

# 给 X_test 在中间插一维
X_test[:, np.newaxis, :].shape    # (5, 1, 4)

# 给 X_train 在最前插一维
X_train[np.newaxis, :, :].shape   # (1, 100, 4)

# 相减，广播
diff = X_test[:, np.newaxis, :] - X_train[np.newaxis, :, :]
diff.shape    # (5, 100, 4)
```

#### 广播图解

```
(5,   1, 4)   ← X_test
(1, 100, 4)   ← X_train
─────────────  从右往左逐维对齐：
                第 2 维  4 = 4   ✅
                第 1 维  1 vs 100 → 1 复制成 100
                第 0 维  5 vs 1   → 1 复制成 5
(5, 100, 4)   ← 结果
```

`diff[i, j, :]` 正好就是"测试样本 i 和训练样本 j 的差向量"。

### 算欧氏距离（一行）

```python
# 每对差向量的范数（沿最后一维特征做 reduce）
distances = np.linalg.norm(diff, axis=2)   # (5, 100)
# 等价：
# distances = np.sqrt((diff ** 2).sum(axis=2))
```

### 找最近 + 取标签

```python
nearest = np.argmin(distances, axis=1)   # 每行最小距离下标 (5,)
predictions = y_train[nearest]           # 用下标取标签（花式索引）(5,)
```

### 性能对比（建议自己跑）

```python
import time

# NumPy 向量化
t0 = time.time()
for _ in range(100):
    diff = X_test[:, None, :] - X_train[None, :, :]
    dist = np.linalg.norm(diff, axis=2)
    pred = y_train[np.argmin(dist, axis=1)]
print(f"NumPy: {time.time() - t0:.4f}s")

# 朴素 for 循环
t0 = time.time()
for _ in range(100):
    pred = []
    for x in X_test:
        d = [np.linalg.norm(x - xt) for xt in X_train]
        pred.append(y_train[np.argmin(d)])
print(f"For: {time.time() - t0:.4f}s")
```

通常 NumPy 比 for 快 **10-100 倍**。

### 这题为什么重要

`X_test[:, None, :] - X_train[None, :, :]` 这个模式在 AI 代码里**反复出现**：
- KNN / K-Means
- Attention 里的 `Q[i] · K[j]`（每对算一次相似度）
- 推荐系统的 user-item 距离

**今天能写出来 → AI 工程代码大门已开**。

---

## 🎯 通过自测

闭卷答下面 3 题，能回答即"题 7-9 真正掌握"：

1. `np.argmax(arr, axis=1)` 中 `axis=1` 是什么含义？为什么不是 `axis=0`？
2. 写 softmax 时为什么要 `keepdims=True`？
3. `np.eye(5)[labels]` 第一步发生了什么？第二步发生了什么？

如果答不出，回到 [Day4 §6.5 卡点专题](../Day4-NumPy基础.md#65-卡点专题4-个最容易迷的-api-)。

---

## 📚 心法收尾

> Java 思维：**步骤分解**（先做 A，再做 B，再做 C...）
> NumPy 思维：**形状思考**（我有 (X, Y)，要变成 (P, Q)，怎么操作维度？）

这种思维转变要 **2-3 周反复练习**才能形成。今天写不出来很正常。
**关键是看完讲解后，能复现一次**——下次再见到类似题，就有"啊这是 newaxis 的活"的本能。

加油。
