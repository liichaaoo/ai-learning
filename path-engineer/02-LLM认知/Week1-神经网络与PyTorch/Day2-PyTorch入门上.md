# Day 2 · PyTorch 入门（上）：Tensor + autograd + nn.Module

> ⏱️ 时间：1.5 小时
> 🎯 目标：把昨天 NumPy 写的"训练一条直线"用 PyTorch 重写，体会"自动求梯度"的爽
> 📋 练习：[`练习/day2_练习.py`](./练习/day2_练习.py)

---

## 0. 安装与验证（5 分钟）

```bash
# 推荐：在项目 venv 里装
source /Users/fletcherli/fletcher/AI/AI学习/.venv/bin/activate
pip install torch torchvision matplotlib

# 验证
python3 -c "import torch; print(torch.__version__)"
# 应该看到 2.x.x
```

Mac 用户额外验证 MPS（Apple Silicon GPU）：

```python
import torch
print(torch.backends.mps.is_available())     # True 表示能用 GPU
```

---

## 1. PyTorch 核心三件套（5 分钟）

```
┌─────────────────────────────────────────────────────────┐
│  1. Tensor    = 带 GPU 加速的 NumPy ndarray             │
│  2. autograd  = 自动求梯度（不用手推反向传播！）         │
│  3. nn.Module = 模型定义（相当于 Spring 的 @Component）  │
└─────────────────────────────────────────────────────────┘
```

> 🧠 **Java 类比**：
> - `Tensor` ≈ 带元信息的多维数组（额外记录 device、dtype、grad）
> - `autograd` ≈ AOP 自动织入：你写运算，它在背后记录"计算图"
> - `nn.Module` ≈ Spring Bean：声明字段、定义行为、可以注入嵌套

---

## 2. Tensor 基础（20 分钟）

### 2.1 创建 Tensor

```python
import torch

# 从 Python 列表/NumPy 创建
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([[1, 2], [3, 4]])

# 常用工厂方法（类似 NumPy）
zeros = torch.zeros(2, 3)             # 2×3 全零
ones  = torch.ones(2, 3)              # 2×3 全一
rand  = torch.randn(2, 3)             # 标准正态分布随机数
eye   = torch.eye(3)                  # 3×3 单位矩阵
arange = torch.arange(0, 10, 2)       # [0,2,4,6,8]

print(a.shape, a.dtype, a.device)     # torch.Size([3]) torch.float32 cpu
```

### 2.2 Tensor vs NumPy ndarray

| 维度 | NumPy ndarray | PyTorch Tensor |
|------|--------------|----------------|
| 设备 | 只能 CPU | CPU / GPU（cuda / mps）|
| 求梯度 | ❌ | ✅（设 `requires_grad=True`）|
| API 风格 | `np.dot`、`arr.shape` | `torch.matmul`、`tensor.shape`（**几乎一样**）|
| 互转 | `tensor.numpy()` ↔ `torch.from_numpy(arr)` | 同左 |

> 💡 **认知钩子**：把 Tensor 当成"加强版 NumPy"，学过 NumPy 90% 的 API 都能直接用。

### 2.3 常用运算

```python
import torch

a = torch.tensor([[1.0, 2], [3, 4]])
b = torch.tensor([[5.0, 6], [7, 8]])

# 元素级运算（和 NumPy 一样）
print(a + b)             # 加法
print(a * b)             # 元素级乘（不是矩阵乘！）
print(a ** 2)            # 平方

# 矩阵乘（重点！LLM 里到处都是）
print(a @ b)             # 推荐写法
print(torch.matmul(a, b)) # 等价

# 形状操作
x = torch.randn(2, 3, 4)
print(x.shape)                # torch.Size([2, 3, 4])
print(x.reshape(2, 12).shape) # 2×12
print(x.transpose(0, 1).shape) # 3×2×4（交换 0、1 维）

# 广播（broadcasting，和 NumPy 一样）
v = torch.tensor([1.0, 2, 3, 4])      # shape [4]
m = torch.zeros(5, 4)                  # shape [5, 4]
print((m + v).shape)                  # [5, 4]，每行加上 v
```

### 2.4 设备切换：`.to(device)`

```python
import torch

# 选择设备（Mac M 系列优先 MPS，否则 CPU）
device = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)

x = torch.randn(1000, 1000)
x = x.to(device)              # 把数据搬到 GPU
print(x.device)               # 应该输出 cuda / mps / cpu

# 计算自动在所选设备上跑
y = x @ x.T
```

> ⚠️ **常见坑**：模型和数据**必须在同一个设备**上，否则报错。Day 4 实战会反复用到。

---

## 3. autograd：自动求梯度（25 分钟）

> ⭐ **这是 PyTorch 最爽的特性**。

### 3.1 一句话总结

> **任何标记了 `requires_grad=True` 的 Tensor，参与运算后调用 `.backward()`，PyTorch 会自动算出所有梯度。**

### 3.2 第一个例子：算 y = x² 在 x=3 处的梯度

```python
import torch

x = torch.tensor(3.0, requires_grad=True)   # ⭐ 关键：要求自动求梯度
y = x ** 2                                   # y = 9.0

y.backward()                                 # 反向传播
print(x.grad)                                # tensor(6.) 对应 dy/dx = 2x = 6
```

> 💡 **这就是反向传播自动化的奇迹**。
> 你只写了 `y = x**2`，PyTorch 在背后构建了计算图，知道 `dy/dx = 2x`。

### 3.3 多个参数：算 z = w*x + b 的梯度

```python
import torch

x = torch.tensor(2.0)                        # 输入（不需要梯度）
w = torch.tensor(3.0, requires_grad=True)    # 参数：要梯度
b = torch.tensor(1.0, requires_grad=True)    # 参数：要梯度

z = w * x + b                                # z = 7.0
z.backward()

print(w.grad)        # dz/dw = x = 2.0
print(b.grad)        # dz/db = 1.0
print(x.grad)        # None（没要求梯度）
```

### 3.4 用 PyTorch 重写昨天的"训练直线"

> 还记得昨天我们用 NumPy 手算梯度训练 `y = w*x + b` 吗？现在用 PyTorch：

```python
import torch

# 数据
xs = torch.tensor([1.0, 2.0, 3.0, 4.0])
ys = torch.tensor([3.0, 5.0, 7.0, 9.0])     # 真实关系：y = 2x + 1

# 参数（要学习的）
w = torch.tensor(0.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
lr = 0.01

for step in range(1000):
    # 1. 前向
    y_pred = w * xs + b

    # 2. Loss（MSE）
    loss = ((y_pred - ys) ** 2).mean()

    # 3. 反向传播（自动求梯度）⭐
    loss.backward()

    # 4. 更新参数（torch.no_grad() 表示这步不参与计算图）
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad

    # 5. 梯度清零（不清的话会累加！）
    w.grad.zero_()
    b.grad.zero_()

    if step % 100 == 0:
        print(f"step {step}: loss={loss.item():.4f}, w={w.item():.4f}, b={b.item():.4f}")

print(f"\n最终：w ≈ {w.item():.4f}, b ≈ {b.item():.4f}")
```

> 🎉 **对比昨天**：`dw = 2 * ((y_pred - ys) * xs).mean()` 这种手推公式**完全不用了**，`loss.backward()` 一行搞定。
>
> 这就是为什么 PyTorch 能扩展到几亿参数的网络——不管多少参数，都是一行 `backward()`。

### 3.5 关于 `optimizer` 的预告

上面手动写的 `w -= lr * w.grad` 在真实代码里会被 `optimizer.step()` 替代，**Day 3 讲**。

### 3.6 三个关键陷阱

```python
# ⚠️ 陷阱 1：梯度会累加，必须 zero_()
loss1.backward()
loss2.backward()       # 现在 .grad 是两次梯度的和！

# 正确做法：每次 backward 前 / 后清零
w.grad.zero_()         # 或 optimizer.zero_grad()

# ⚠️ 陷阱 2：更新参数要用 with torch.no_grad():
w -= lr * w.grad       # 错误：这步会被加进计算图
with torch.no_grad():  # 正确
    w -= lr * w.grad

# ⚠️ 陷阱 3：要从 Tensor 取数值用 .item()
print(loss)            # tensor(0.0123, grad_fn=<MeanBackward0>)
print(loss.item())     # 0.0123（普通 Python float）
```

---

## 4. nn.Module：模型组织方式（25 分钟）

### 4.1 为什么要 nn.Module

手写参数管理（像 §3.4）能用，但有几个问题：
- 参数多了管理混乱（GPT-3 有 1750 亿参数...）
- 每层都要手写 `w * x + b`，没有复用
- 没法批量保存/加载/转移到 GPU

`nn.Module` 解决：**像 Spring Bean 一样组织模型**。

### 4.2 Hello World：一个 Linear 层

```python
import torch
import torch.nn as nn

# nn.Linear(in_features, out_features) = "y = W @ x + b" 的 Bean 化
layer = nn.Linear(in_features=4, out_features=2)

# 自动创建了 W (2×4) 和 b (2)，且 requires_grad=True
print(layer.weight.shape)       # torch.Size([2, 4])
print(layer.bias.shape)         # torch.Size([2])

# 前向传播
x = torch.randn(4)
y = layer(x)                    # 等价于 layer.weight @ x + layer.bias
print(y.shape)                  # torch.Size([2])
```

### 4.3 自定义模型：继承 nn.Module

```python
import torch
import torch.nn as nn

class MyMLP(nn.Module):
    """一个简单的 3 层 MLP：4 → 8 → 8 → 2"""

    def __init__(self):
        super().__init__()                     # ⭐ 必须调父类
        self.fc1 = nn.Linear(4, 8)
        self.fc2 = nn.Linear(8, 8)
        self.fc3 = nn.Linear(8, 2)
        self.relu = nn.ReLU()

    def forward(self, x):                      # ⭐ 必须叫 forward
        h = self.relu(self.fc1(x))
        h = self.relu(self.fc2(h))
        y = self.fc3(h)                        # 输出层不加激活
        return y


# 使用
model = MyMLP()
x = torch.randn(4)
y = model(x)                                   # 等价于 model.forward(x)，但要写 model(x)
print(y.shape)                                 # torch.Size([2])

# 查看模型结构
print(model)
# MyMLP(
#   (fc1): Linear(in_features=4, out_features=8, bias=True)
#   (fc2): Linear(in_features=8, out_features=8, bias=True)
#   (fc3): Linear(in_features=8, out_features=2, bias=True)
#   (relu): ReLU()
# )

# 查看参数总数
total = sum(p.numel() for p in model.parameters())
print(f"总参数：{total}")        # 4*8+8 + 8*8+8 + 8*2+2 = 138
```

> 🧠 **Java 类比**：
> - `__init__` ≈ Spring Bean 构造 + `@Autowired` 注入子组件（fc1/fc2/fc3）
> - `forward` ≈ 业务方法
> - `model(x)` ≈ 调 `apply(x)`（PyTorch 让你不用写 `model.forward(x)`）

### 4.4 内置常用 nn 模块（认识就行，要用查文档）

| 模块 | 用途 |
|------|------|
| `nn.Linear` | 全连接层（最常用）|
| `nn.Conv2d` | 二维卷积（图像）|
| `nn.LSTM` / `nn.GRU` | 循环网络（老式 NLP）|
| `nn.MultiheadAttention` | **多头注意力（Week 2 主角）** |
| `nn.LayerNorm` | 层归一化（**Transformer 标配**）|
| `nn.Embedding` | 嵌入层（token id → 向量）|
| `nn.Dropout` | Dropout 正则化 |
| `nn.ReLU` / `nn.GELU` | 激活函数 |

> 💡 **本周记住**：`nn.Linear` + `nn.LayerNorm` + `nn.GELU` 这三件套，下周看 Transformer 时反复出现。

### 4.5 Sequential：偷懒式堆叠

如果模型只是"层接层"，可以用 `nn.Sequential` 简化：

```python
model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

x = torch.randn(4)
y = model(x)
```

> ⚠️ Sequential 适合简单情况；有分支、跳连接（如 Transformer 的 residual）必须自己写 `forward`。

---

## 5. 把 §3.4 升级成 nn.Module 风格（10 分钟）

```python
import torch
import torch.nn as nn

# 数据
xs = torch.tensor([[1.0], [2.0], [3.0], [4.0]])    # shape [4, 1]
ys = torch.tensor([[3.0], [5.0], [7.0], [9.0]])    # shape [4, 1]

# 模型 = 一个 Linear 层
model = nn.Linear(1, 1)
loss_fn = nn.MSELoss()

# 手动 SGD（Day 3 会换成 optimizer）
lr = 0.01

for step in range(1000):
    # 1. 前向
    y_pred = model(xs)

    # 2. Loss
    loss = loss_fn(y_pred, ys)

    # 3. 反向
    loss.backward()

    # 4. 更新（手动版）
    with torch.no_grad():
        for param in model.parameters():
            param -= lr * param.grad
            param.grad.zero_()

    if step % 100 == 0:
        w = model.weight.item()
        b = model.bias.item()
        print(f"step {step}: loss={loss.item():.4f}, w={w:.4f}, b={b:.4f}")

print(f"\n最终：w ≈ {model.weight.item():.4f}, b ≈ {model.bias.item():.4f}")
```

> ✅ 跑一下，效果和 §3.4 一样，但代码更"工程化"。
>
> Day 3 会进一步用 `optim.SGD` / `optim.Adam` 替代手写更新。

---

## 6. 常见疑惑 FAQ（5 分钟）

### Q1：`requires_grad=True` 是设给"参数"还是"输入"？

A：**只设给参数**（要学习的东西）。
- `nn.Linear` 内部的 weight、bias 自动 `requires_grad=True`
- 输入数据通常不需要

### Q2：为什么 `model(x)` 而不是 `model.forward(x)`？

A：`model(x)` 会调 `__call__`，里面除了 `forward` 还有 hook、device 检查等。**永远写 `model(x)`**。

### Q3：`Tensor.detach()` 是什么？

A：**从计算图里"剥离"**，得到一个不参与梯度计算的副本。常用于：
- 把 Tensor 转 NumPy 时：`tensor.detach().cpu().numpy()`
- 推理（不训练）时减少内存

### Q4：`model.train()` 和 `model.eval()` 是什么？

A：模式切换。
- `model.train()`：训练模式（Dropout/BN 启用）
- `model.eval()`：推理模式（Dropout/BN 关闭）
- Day 4 / Day 5 用到。

---

## 📋 今日任务清单

- [ ] 装好 PyTorch，验证版本和设备
- [ ] 把 §2.3、§3.2、§3.4 的代码**手敲一遍**
- [ ] 跑通 §5 的 nn.Module 版训练，对比 §3.4 体会差别
- [ ] 完成 [`练习/day2_练习.py`](./练习/day2_练习.py)
- [ ] 在笔记里画一张图：`Tensor → autograd → nn.Module` 的关系

---

## 🎯 自测：今天你应该能...

- [ ] 解释 Tensor 和 NumPy ndarray 的 3 个区别
- [ ] 写一个 `requires_grad=True` 的 Tensor 并用 `.backward()` 求梯度
- [ ] 自己写一个继承 `nn.Module` 的简单模型
- [ ] 解释 `forward` 为什么不用手动调
- [ ] 知道梯度要 `zero_()` 清零

---

## 🆘 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| `RuntimeError: element 0 of tensors does not require grad` | 漏写 `requires_grad=True` | 把要求梯度的 tensor 加上 |
| 梯度越训越大、loss 飞了 | 没有 `zero_grad()` | 每次 backward 前/后清零 |
| `Expected all tensors to be on the same device` | 模型在 GPU、数据在 CPU（或反过来）| 都 `.to(device)` |
| `model.weight.grad is None` | 还没 backward 过，或者参数不在计算图里 | 检查 forward 是否真的用了它 |

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 3 · PyTorch 入门（下）](./Day3-PyTorch入门下.md)。

> 预告：明天用 `optimizer` 替换手写更新参数、用 `DataLoader` 替换手写迭代、把训练循环组装成"工程化"模板。
