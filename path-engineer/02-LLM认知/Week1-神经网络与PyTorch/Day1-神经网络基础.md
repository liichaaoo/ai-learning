# Day 1 · 神经网络基础（Java 视角理解版）

> ⏱️ 时间：1.5 小时
> 🎯 目标：建立对神经网络的**直觉**，知道每一块在干什么
> 📋 练习：[`练习/day1_练习.py`](./练习/day1_练习.py)

---

## 0. 心法（5 分钟）

> **神经网络的本质：一个能自己调参数的、巨大的复合函数。**

把它想象成一个超级 lambda：

```
y = f(x; θ)
```

- `x`：输入（图片像素、token id、用户特征……）
- `y`：输出（"猫"还是"狗"、下一个 token 是谁）
- `θ`：**参数**（成千上万个浮点数，就是要学习的东西）
- `f`：函数结构（神经网络的"形状"）

**训练 = 找到一组好的 θ，让 f(x; θ) 在我们见过的数据上和真实答案接近。**

> 🧠 **Java 类比**：把神经网络想成一个有 100 万个 `private double field` 的 Bean，训练就是不停地调这些 field 的值，让它对所有 `process(input)` 的输出都符合预期。

---

## 1. 神经元：最小单元（10 分钟）

### 1.1 一个神经元在干什么

```
输入 x1, x2, x3 → [乘权重 w 加偏置 b] → [激活函数] → 输出
```

数学上：

```
z = w1*x1 + w2*x2 + w3*x3 + b      # 加权求和（线性）
a = activation(z)                    # 非线性变换
```

### 1.2 用 NumPy 写一个

```python
import numpy as np

def neuron(x: np.ndarray, w: np.ndarray, b: float) -> float:
    """单个神经元的前向计算"""
    z = np.dot(w, x) + b           # 加权求和
    return max(0, z)               # ReLU 激活

# 测试
x = np.array([1.0, 2.0, 3.0])
w = np.array([0.5, -0.3, 0.8])
b = 0.1
print(neuron(x, w, b))             # 自己算一下：0.5*1 + (-0.3)*2 + 0.8*3 + 0.1 = 2.4
```

> 💡 **关键认知**：一个神经元 = **线性变换 + 非线性激活**。
>
> 没有非线性激活，再多层叠加也只等价于一层（线性变换的组合还是线性变换）。

---

## 2. 激活函数：为什么需要它（15 分钟）

### 2.1 三个最常见的激活函数

| 名字 | 公式（口语版）| 形状 | 用在哪 |
|------|------|------|------|
| **Sigmoid** | 把任何数压到 (0, 1) | S 形 | 老式网络、二分类输出 |
| **ReLU** ⭐ | 负数变 0，正数不变 | 折线 | **当代默认选择** |
| **GeLU** | ReLU 的"光滑版" | 类似 ReLU 但更平滑 | **GPT / BERT / Llama 全用它** |

### 2.2 直观对比

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-5, 5, 100)
sigmoid = 1 / (1 + np.exp(-x))
relu = np.maximum(0, x)
# GeLU 近似公式
gelu = 0.5 * x * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))

plt.figure(figsize=(10, 4))
plt.plot(x, sigmoid, label='Sigmoid')
plt.plot(x, relu,    label='ReLU')
plt.plot(x, gelu,    label='GeLU')
plt.legend(); plt.grid(); plt.title('激活函数对比')
plt.show()
```

### 2.3 为什么需要激活函数

```
没有激活函数：
  y = W3 @ (W2 @ (W1 @ x + b1) + b2) + b3
    = (W3 @ W2 @ W1) @ x + 某个常数
    = 等价于一层线性！                  ← 没有意义

加了激活函数：
  y = W3 @ activation(W2 @ activation(W1 @ x + b1) + b2) + b3
    = 真正的非线性函数                  ← 才有表达能力
```

> 💡 **一句话总结**：激活函数 = **给神经网络加"非线性"**，否则再深也没用。
>
> 🎯 **本周记住**：现代 LLM 几乎全用 **GeLU / SwiGLU**（Llama 用 SwiGLU）。
> Sigmoid 几乎只在二分类输出层用了。

---

## 3. MLP：多层感知机（15 分钟）

### 3.1 把神经元堆起来 = 一层

一层神经网络：多个神经元并行，共享同一组输入。

```
输入向量 x（4 维）→ [神经元 1, 神经元 2, 神经元 3]（每个神经元有自己的 w、b）→ 输出向量 a（3 维）
```

数学上：一层 = **矩阵乘法 + 偏置 + 激活**

```python
def linear_layer(x: np.ndarray, W: np.ndarray, b: np.ndarray) -> np.ndarray:
    """一层全连接：输入 x（n 维），输出（m 维）"""
    z = W @ x + b              # 矩阵乘 + 偏置（W 是 m×n 矩阵）
    return np.maximum(0, z)    # ReLU 激活
```

### 3.2 多层 = MLP（Multi-Layer Perceptron）

```python
import numpy as np

# 一个 3 层 MLP：输入 4 维 → 隐藏层 8 维 → 输出 2 维
W1 = np.random.randn(8, 4) * 0.1     # 第 1 层权重
b1 = np.zeros(8)
W2 = np.random.randn(2, 8) * 0.1     # 第 2 层权重
b2 = np.zeros(2)

def mlp_forward(x):
    h = np.maximum(0, W1 @ x + b1)   # 第 1 层 + ReLU
    y = W2 @ h + b2                  # 输出层（不加激活）
    return y

x = np.random.randn(4)
print(mlp_forward(x))                # 一个 2 维向量
```

> 🧠 **Java 类比**：MLP ≈ 一串 `Function<double[], double[]>` 的链式调用：
> ```java
> output = layer3.apply(layer2.apply(layer1.apply(input)));
> ```
> 只是每一层的"权重矩阵"是要学习的，不是写死的。

---

## 4. 前向传播 vs 反向传播（15 分钟）

### 4.1 前向传播（Forward）= 算预测

```
输入 x → 第 1 层 → 第 2 层 → ... → 输出 y_pred
```

我们刚才写的 `mlp_forward(x)` 就是前向传播。

### 4.2 反向传播（Backward）= 算"参数该怎么调"

> ⚠️ **重要：本周你只需要知道它在干嘛，不需要会推。**

直觉：
1. 拿到预测 `y_pred`，和真实答案 `y_true` 比，算出 **Loss**
2. 反向地问每一层："你贡献了多少误差？"
3. 答案就是**梯度**（每个参数应该往哪边、调多少）

```
                       ↓ Loss = (y_pred - y_true)^2
       y_pred = W2 @ h + b2          ← 算 W2、b2 的梯度
       h      = ReLU(W1 @ x + b1)    ← 算 W1、b1 的梯度
       x      = 输入
```

PyTorch 一行代码搞定：

```python
loss.backward()           # 整个反向传播 + 所有参数梯度自动计算
```

> 💡 **关键认知**：反向传播 = **链式法则在自动跑**。你不需要手推，PyTorch 用 `autograd` 帮你做完了。

### 4.3 一张图理解整个流程

```
            前向传播（forward）
    ┌──────────────────────────────────┐
    │                                  ↓
   [输入 x] → [模型 f(x; θ)] → [预测 y_pred]
                  ↑                    │
                  │                    ↓
              [更新 θ]            [Loss = compare(y_pred, y_true)]
                  ↑                    │
                  │                    ↓
              [梯度 ∇θ] ← ─ ─ ─ ─ [反向传播 backward]
            反向传播（backward）
```

**这就是神经网络训练的全部。** 后面 4 天都是把这一张图变成代码。

---

## 5. 损失函数（10 分钟）

> **损失函数（Loss）= 衡量"预测和真实差多远"。值越小越好。**

最常见的两个：

### 5.1 MSE（均方误差）—— 用于回归

```python
def mse_loss(y_pred, y_true):
    return ((y_pred - y_true) ** 2).mean()
```

适用：**预测一个连续数值**（房价、温度）。

### 5.2 交叉熵（Cross Entropy）—— 用于分类

```python
def cross_entropy(logits, label):
    """logits: 模型原始输出（K 维）；label: 整数（0 ~ K-1）"""
    # softmax 把 logits 变成概率
    probs = np.exp(logits) / np.exp(logits).sum()
    # 取真实类别的概率，取对数取负
    return -np.log(probs[label])
```

适用：**预测一个类别**（分类问题）。

> 🎯 **LLM 用什么 Loss？** 答：**交叉熵**（每一步预测下一个 token 是哪个，本质是一个超大词表的分类问题）。
>
> 这就是为什么 [阶段 1 Week 3 Day 3](../../01-基础速通/Week3-数学补盲/Day3-概率与信息论.md) 让你重点学 Softmax + 交叉熵。

---

## 6. 梯度下降：如何更新参数（15 分钟）

> 拿到梯度后，怎么调参数？答：**梯度下降**。

### 6.1 公式

```
θ_new = θ_old - lr × ∇θ
```

- `θ`：参数
- `lr`：学习率（learning rate），通常 0.001 ~ 0.1
- `∇θ`：梯度

> 💡 **直觉**：梯度告诉你"loss 上升最快的方向"，我们就**往反方向走一小步**，loss 就下降了。

### 6.2 NumPy 手动实现一步梯度下降

```python
import numpy as np

# 简化场景：训练一条直线 y = w*x + b 拟合数据
xs = np.array([1.0, 2.0, 3.0, 4.0])
ys = np.array([3.0, 5.0, 7.0, 9.0])     # 真实关系：y = 2x + 1

w, b = 0.0, 0.0          # 初始参数（瞎猜）
lr = 0.01

for step in range(1000):
    # 1. 前向：计算预测
    y_pred = w * xs + b

    # 2. 计算 loss（MSE）
    loss = ((y_pred - ys) ** 2).mean()

    # 3. 算梯度（这里手推过了，本周后面 PyTorch 自动算）
    dw = 2 * ((y_pred - ys) * xs).mean()
    db = 2 * (y_pred - ys).mean()

    # 4. 更新参数
    w -= lr * dw
    b -= lr * db

    if step % 100 == 0:
        print(f"step {step}: loss={loss:.4f}, w={w:.4f}, b={b:.4f}")

print(f"\n最终：w ≈ {w:.4f}, b ≈ {b:.4f}（真实值 w=2, b=1）")
```

跑一下，你会看到 `w` 慢慢逼近 2，`b` 慢慢逼近 1。

> 🎉 **这就是神经网络训练的核心过程**。差别只是：
>
> 1. 真实模型有几百万参数，不是 2 个
> 2. 梯度由 PyTorch `loss.backward()` 自动算，不用手推
> 3. 用 Adam 等优化器代替朴素 SGD（Day 3 讲）

---

## 7. 概念串起来：训练循环（10 分钟）

把上面所有概念串成一个循环：

```python
# 伪代码：神经网络训练的"四步圣经"
for epoch in range(N):                    # 把数据集过 N 遍
    for batch in data_loader:             # 每次取一小批数据
        # 1. 前向传播
        y_pred = model(batch.x)

        # 2. 计算 loss
        loss = loss_fn(y_pred, batch.y)

        # 3. 反向传播（自动求梯度）
        loss.backward()

        # 4. 更新参数
        optimizer.step()
        optimizer.zero_grad()             # 梯度清零（PyTorch 不会自动清）
```

> ⭐ **这四步循环是本周的核心**，Day 4 跑 MNIST 就是把它具体化。
>
> 之后所有 LLM 训练（包括 GPT-4 训练）都是这四步的放大版。

---

## 8. 常见疑惑 FAQ（5 分钟）

### Q1：为什么是"层"？为什么不是写一个超大函数？

A：分层是为了：
1. **复用结构**：每层内部逻辑相同（矩阵乘 + 激活），方便堆叠
2. **梯度好算**：链式法则配分层最自然
3. **表达能力强**：理论上 2 层 MLP 可以拟合任意连续函数（万能近似定理）

### Q2：参数（权重）是怎么初始化的？

A：常见方案：
- **随机小数**：`np.random.randn() * 0.01`（最朴素）
- **Xavier 初始化** / **Kaiming 初始化**（按层维度自适应）
- PyTorch 的 `nn.Linear` 默认就是 Kaiming 初始化，**你不用管**

### Q3：神经网络和传统机器学习的关系？

A：神经网络是机器学习的一个分支（深度学习）。
- **传统 ML**（决策树、SVM）：手工设计特征 + 简单模型
- **深度学习**：让模型自己学特征 + 复杂模型

### Q4：什么是"深度"？

A："深"指**层数多**。
- 1 层：单层感知机（很弱）
- 2-3 层：MLP（能解决简单问题）
- 100+ 层：现代深度网络（GPT、ResNet）

---

## 📋 今日任务清单

完成下面 5 件事就算今天达标：

- [ ] 通读本文档，把 7 个核心概念在脑里串一遍
- [ ] 把 §1.2、§3.2、§6.2 的代码**手敲一遍**（不要复制！）
- [ ] 跑一下 §6.2 的"用 NumPy 训练一条直线"，看看 loss 怎么下降
- [ ] 完成 [`练习/day1_练习.py`](./练习/day1_练习.py)
- [ ] 在笔记里画出 §4.3 的"前向 + 反向"流程图（手画也行）

---

## 🎯 自测：今天你应该能...

- [ ] 用一句话回答："神经网络是什么？"
- [ ] 解释为什么需要激活函数
- [ ] 默写 MLP 的前向传播公式
- [ ] 解释 forward / backward / loss / optimizer 这 4 个词在干嘛
- [ ] 知道梯度下降的公式：`θ -= lr × ∇θ`

---

## 🆘 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| matplotlib 画图弹不出窗口 | Mac 后端问题 | 加 `import matplotlib; matplotlib.use('TkAgg')` |
| `(y_pred - ys) * xs` 维度对不上 | shape 不匹配 | 用 `print(arr.shape)` 调试，回看 [阶段 1 Week 1 Day 4](../../01-基础速通/Week1-Python速通/Day4-NumPy基础.md) |
| 训练时 loss 不降反升 | 学习率太大 | `lr` 调小 10 倍试试（如 0.01 → 0.001）|

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 2 · PyTorch 入门（上）](./Day2-PyTorch入门上.md)。

> 预告：明天你会发现今天手写的"梯度下降一条直线"，PyTorch 几行代码就搞定，而且能扩展到几百万参数。
