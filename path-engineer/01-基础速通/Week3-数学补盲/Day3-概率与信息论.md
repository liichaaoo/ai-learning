# Day 3 · 概率与信息论基础

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**能手撸 softmax，能解释交叉熵在 LLM 里干什么**

---

## 🧭 今天的核心问题

1. **LLM 怎么从"下一个 token 是什么"这堆可能里选出一个？** → softmax + 采样
2. **训练 LLM 的 loss 到底在算啥？** → 交叉熵
3. **调 API 时的 `temperature` 和 `top_p` 是什么？** → 概率分布的变形

---

## 一、概率基础（1 分钟速过）

| 术语 | 含义 |
|------|-----|
| **概率** | 某件事发生的"可能性"，范围 $[0, 1]$ |
| **概率分布** | 各种可能事件的概率加起来 = 1 |
| **条件概率** | $P(A \| B)$ = 已知 B 发生时，A 发生的概率 |

例子：
- 扔硬币，正面概率 0.5 → $P(\text{正}) = 0.5$
- 不同城市下雨概率：$P(\text{上海}) = 0.3, P(\text{北京}) = 0.1, P(\text{广州}) = 0.6$，加起来 = 1

### LLM 里的概率分布

**每次生成下一个 token，模型的输出就是一个概率分布**：

```
词表有 10 万个 token，模型输出：
 P("苹") = 0.35
 P("梨") = 0.01
 P("酒") = 0.02
 ...
 （10 万个概率加起来 = 1）
```

然后按这个分布**采样**一个 token 作为输出。这就是 LLM 生成文本的底层。

---

## 二、Softmax ⭐⭐⭐（今天最重要的公式）

### 2.1 为什么需要 Softmax

神经网络最后一层输出的是**任意的实数**（叫 **logits**），比如：

```
[2.0, 1.5, 0.3, -1.2, 4.8]   ← 这是 5 个 logits
```

你想把它们变成**概率**：
- 非负（概率不能负）
- 加起来 = 1
- **大的值变成大的概率，小的值变成小的概率**

**Softmax 就是干这个的函数**。

### 2.2 公式

$$\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}$$

**人话翻译**：
1. 每个数取 $e^{x}$（指数，让它变正且放大差异）
2. 加起来求和
3. 每个数除以总和 → 变成概率

### 2.3 手算一遍

对 $[2, 1, 0]$ 做 softmax：

```
Step 1: e^2 = 7.389, e^1 = 2.718, e^0 = 1.0
Step 2: 总和 = 7.389 + 2.718 + 1.0 = 11.107
Step 3: 除以总和：
  7.389 / 11.107 ≈ 0.665
  2.718 / 11.107 ≈ 0.245
  1.0   / 11.107 ≈ 0.090

→ [0.665, 0.245, 0.090]   加起来 = 1 ✅
```

### 2.4 Python 实现

```python
import numpy as np

def softmax(x):
    """标准 softmax"""
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x)

# 测试
logits = np.array([2.0, 1.0, 0.0])
probs = softmax(logits)
print(probs)         # [0.665, 0.245, 0.090]
print(probs.sum())   # 1.0
```

### 2.5 数值稳定版（工业界必用）

直接用上面实现，遇到 `x = [1000, 999, 998]` 会 **overflow**（`e^1000` 太大）。

**技巧**：每个数先减去最大值（不改变结果，但避免溢出）

```python
def stable_softmax(x):
    x_max = np.max(x)
    exp_x = np.exp(x - x_max)
    return exp_x / np.sum(exp_x)
```

**记住这个细节**，面试会问。

---

## 三、Temperature & Top-p（你调 LLM API 常见参数）

### 3.1 Temperature

**直觉**：温度越高，概率分布越"平"（各种选项机会更平均，越随机）；温度越低，分布越"陡"（模型越确定，越固定）。

**公式**：在 softmax 前把 logits 除以 T
$$\text{softmax}\left(\frac{x}{T}\right)$$

```python
def softmax_with_temp(logits, T=1.0):
    return stable_softmax(logits / T)

logits = np.array([2.0, 1.0, 0.0])

print("T=0.1 (保守):", softmax_with_temp(logits, 0.1))
# [0.99, 0.01, 0.00]    ← 几乎一定选第一个

print("T=1.0 (默认):", softmax_with_temp(logits, 1.0))
# [0.67, 0.24, 0.09]

print("T=2.0 (激进):", softmax_with_temp(logits, 2.0))
# [0.51, 0.31, 0.19]    ← 更均匀，更"有创意"
```

**生产经验**：
| 场景 | 推荐 temperature |
|------|----------------|
| 代码生成、问答（要稳定） | 0.0 - 0.3 |
| 一般对话 | 0.7 - 1.0 |
| 创意写作 | 1.0 - 1.5 |

### 3.2 Top-p (Nucleus Sampling)

**直觉**：从概率最高的 top 一部分 token 里抽，剩下的不要。

**规则**：把 token 按概率排序，累加概率直到超过 p，只在这批里抽。

```
排序后概率: [0.5, 0.2, 0.15, 0.05, 0.04, ...]
top_p = 0.8:
  累加: 0.5 → 0.7 → 0.85 (超过 0.8)
  → 只在前 3 个里抽
```

**生产经验**：`top_p=0.9` 是最常见的默认值。

### 3.3 Top-k

从概率最高的 K 个里随机抽。比 top_p 更粗糙，少用。

---

## 四、交叉熵（Cross Entropy）⭐⭐⭐

### 4.1 用在哪

**所有分类任务的 loss 都是交叉熵**，包括 LLM 训练（本质是"预测下一个 token 是哪个词"，K 分类问题）。

### 4.2 公式（分类场景）

$$\text{CE} = -\sum_i y_i \log(p_i)$$

**翻译**：
- $y_i$ = 真实标签的 one-hot（只有一个位置是 1，其他是 0）
- $p_i$ = 模型预测的概率分布
- 只有真实类别那个位置的 $\log(p_i)$ 会被计算

**简化后**：
$$\text{CE} = -\log(p_{\text{正确类别}})$$

### 4.3 直觉

- 模型认为正确类别概率 = 1.0 → loss = $-\log(1) = 0$（完美）
- 模型认为正确类别概率 = 0.5 → loss = $-\log(0.5) \approx 0.69$
- 模型认为正确类别概率 = 0.1 → loss = $-\log(0.1) \approx 2.3$（很差）
- 模型认为正确类别概率 = 0.001 → loss = $-\log(0.001) \approx 6.9$（灾难）

**核心直觉**：**模型对正确答案预测得越不自信，loss 越大**。

### 4.4 Python 实现

```python
def cross_entropy(probs, true_class):
    """
    probs: 模型输出的概率分布（softmax 后），shape = (K,)
    true_class: 真实类别的索引 (int)
    """
    return -np.log(probs[true_class] + 1e-10)  # +1e-10 防 log(0)

# 例子：3 分类
probs = np.array([0.7, 0.2, 0.1])
true_class = 0   # 真实是第 0 类
print(cross_entropy(probs, true_class))  # ~0.357

# 如果真实是第 2 类
print(cross_entropy(probs, 2))           # ~2.3 （loss 大，因为模型预测概率低）
```

### 4.5 LLM 训练中的交叉熵

```
给模型输入："苹果公司发布了"
正确的下一个 token 是 "新"
模型对整个词表输出概率：P(新)=0.3, P(和)=0.1, P(...)=0.6

loss = -log(0.3) ≈ 1.2

→ 训练目标：调整模型参数让 P(新) 变大（让 loss 变小）
```

训练过程就是**不停地做这个**，几十亿次迭代。

---

## 五、最大似然估计（Maximum Likelihood）

一句话知道：**让模型对训练数据里"真实答案"的概率尽可能大，就是最大似然**。

数学上，**最大化似然 ≡ 最小化交叉熵**。

**你不用懂推导**，知道这两件事等价就行。

---

## 六、KL 散度（选学，5 分钟）

衡量两个概率分布的"差异"：

$$D_{KL}(P \| Q) = \sum_i P(i) \log \frac{P(i)}{Q(i)}$$

### 你会在哪见到

- **RLHF**（ChatGPT 训练后期）：用 KL 散度约束新策略不要偏离原模型太多
- **蒸馏**：让小模型的输出分布接近大模型

**本周**：**见过就行**，不用深究。

---

## 七、一个完整的"分类 = softmax + 交叉熵"示例

```python
import numpy as np

def stable_softmax(x):
    x_max = np.max(x)
    exp_x = np.exp(x - x_max)
    return exp_x / np.sum(exp_x)

def cross_entropy(probs, true_class):
    return -np.log(probs[true_class] + 1e-10)

# 模拟一次"模型前向传播 + 计算 loss"
logits = np.array([2.0, 3.5, 1.0, 0.5])   # 模型的原始输出（4 分类）
true_class = 1                            # 真实类别是第 1 类

# 1. softmax 变概率
probs = stable_softmax(logits)
print(f"概率分布: {probs}")
# ~[0.16, 0.72, 0.06, 0.04]  ← 模型最看好第 1 类

# 2. 算 loss
loss = cross_entropy(probs, true_class)
print(f"交叉熵 loss: {loss:.4f}")
# ~0.33（还不错，模型对了）

# 3. 如果真实是第 3 类会怎样？
loss2 = cross_entropy(probs, 3)
print(f"真实=3 时 loss: {loss2:.4f}")
# ~3.22（很大，模型错得离谱）
```

**这就是 LLM 训练时每一步在做的事**。

---

## 📚 延伸阅读（选做）

- 3Blue1Brown 的 [深度学习系列](https://www.bilibili.com/video/BV1bx411M7Zx) 第 3 集"反向传播"前 5 分钟 —— **视觉化最直观的 softmax 讲解**

---

## ✍️ 本日练习

完成 [`练习/day3_练习.py`](./练习/day3_练习.py)：
- 手算 softmax
- 实现数值稳定版 softmax
- Temperature 对分布的影响（可视化）
- 交叉熵计算

---

## 🎯 今日收官清单

- [ ] 我能一句话解释 softmax 的作用
- [ ] 我能手算 softmax([1, 2, 3]) 的结果
- [ ] 我知道为什么要用 stable_softmax（减去 max）
- [ ] 我理解 temperature 大 → 分布更平 → 更随机
- [ ] 我知道 top_p = 0.9 是常见默认
- [ ] 我能说出"交叉熵 = -log(正确类别的概率)"
- [ ] 我知道 LLM 训练的 loss 就是交叉熵

---

## 🔖 下一步

明天 → [Day 4：微积分与梯度](./Day4-微积分与梯度.md)（反向传播的认知）
