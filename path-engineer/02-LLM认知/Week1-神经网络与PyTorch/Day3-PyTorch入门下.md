# Day 3 · PyTorch 入门（下）：Optimizer + DataLoader + GPU

> ⏱️ 时间：1.5 小时
> 🎯 目标：把昨天手写的训练循环工程化，得到一个可复用的"训练模板"
> 📋 练习：[`练习/day3_练习.py`](./练习/day3_练习.py)

---

## 0. 心法（5 分钟）

> 昨天我们做到了：自己写 `forward`、自己 `backward`、**自己手动更新参数**、**自己 zero_grad**。
>
> 今天的任务：把"手动"全部换成"框架做"，得到现代深度学习训练的标准范式。

```
昨天                              今天
─────────────────────────────────────────────────
for step in range(1000):          for epoch in range(N):
    y = w*x + b                       for batch in loader:    ⭐ DataLoader
    loss = ...                            y = model(batch.x)
    loss.backward()                       loss = loss_fn(y, batch.y)
    with torch.no_grad():                 loss.backward()
        w -= lr * w.grad                  optimizer.step()    ⭐ Optimizer
        w.grad.zero_()                    optimizer.zero_grad()
```

**这个模板，从 MLP 到 GPT-4，结构一模一样。**

---

## 1. Optimizer：把"手动更新"自动化（25 分钟）

### 1.1 三大主流优化器

| 优化器 | 一句话理解 | 推荐场景 |
|-------|-----------|---------|
| **SGD** | 朴素梯度下降，最经典 | 教学 / 简单任务 / 大批量预训练 |
| **SGD + Momentum** | SGD + "惯性"（避免在山谷里反复横跳）| 经典 CV |
| **Adam** ⭐ | 自适应学习率 + 动量，**当代首选** | LLM、Transformer 几乎全用这个或它的变体 |
| **AdamW** | Adam + 权重衰减修正版 | **GPT、Llama、BERT 都用 AdamW** |

> 💡 **本周记住一句话**：**不知道选啥就用 AdamW，lr=1e-3 起步**。

### 1.2 用 Optimizer 重写昨天的训练

```python
import torch
import torch.nn as nn
import torch.optim as optim

# 数据
xs = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
ys = torch.tensor([[3.0], [5.0], [7.0], [9.0]])

# 模型 + 损失 + 优化器
model = nn.Linear(1, 1)
loss_fn = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)    # ⭐ 把参数交给优化器

for step in range(1000):
    # 1. 前向
    y_pred = model(xs)

    # 2. 算 loss
    loss = loss_fn(y_pred, ys)

    # 3. 反向（自动求梯度）
    loss.backward()

    # 4. 更新参数（替代手写的 w -= lr * w.grad）
    optimizer.step()

    # 5. 梯度清零（替代手写的 w.grad.zero_()）
    optimizer.zero_grad()

    if step % 100 == 0:
        print(f"step {step}: loss={loss.item():.4f}")

print(f"最终：w ≈ {model.weight.item():.4f}, b ≈ {model.bias.item():.4f}")
```

> ✅ 跑一下，结果和 Day 2 §5 一样，但代码更"标准"。
>
> **模板已经成形**：`forward → loss → backward → step → zero_grad`。这就是著名的"五步循环"。

### 1.3 切换到 Adam 试试

把上面的 `optim.SGD` 换成 `optim.Adam`：

```python
optimizer = optim.Adam(model.parameters(), lr=0.01)
```

跑一遍会发现**收敛更快**（同样的 1000 步，loss 降得更低）。这就是自适应学习率的威力。

### 1.4 各 Optimizer API 速查

```python
# SGD
optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam（万金油）
optim.Adam(model.parameters(), lr=1e-3, betas=(0.9, 0.999))

# AdamW（LLM 主流）
optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
```

> 💡 **学习率经验值**（不绝对）：
> - SGD: 0.01 ~ 0.1
> - Adam / AdamW: 1e-4 ~ 1e-3
> - 大模型微调（LoRA）: 1e-4 ~ 5e-4

### 1.5 学习率调度器（认知级，要用查文档）

训练后期把 lr 调小一点能让 loss 降得更稳：

```python
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

for epoch in range(100):
    train_one_epoch(...)
    scheduler.step()                  # 每个 epoch 调一次 lr
```

> 🎯 **本周不用细究**，知道有这东西即可。LLM 训练几乎都会用 cosine schedule + warmup。

---

## 2. Dataset 和 DataLoader：批量喂数据（25 分钟）

### 2.1 为什么需要 DataLoader

之前我们一次喂全部数据进模型（`xs` 4 个样本一次性进）。真实场景：
- 数据集有几百万条，**塞不进内存**
- 一次只算一小批（**batch**），效率高 + 引入随机性

DataLoader 解决：**把数据切成 batch、自动打乱、并行预读**。

> 🧠 **Java 类比**：DataLoader ≈ Spring Data 的 `Pageable` + 异步预取。

### 2.2 自定义 Dataset：实现两个方法

```python
import torch
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    def __len__(self):                     # ⭐ 数据集大小
        return len(self.xs)

    def __getitem__(self, idx):            # ⭐ 取第 idx 个样本
        return self.xs[idx], self.ys[idx]


# 用 NumPy 造一些假数据
import numpy as np
np.random.seed(42)
xs = torch.from_numpy(np.random.randn(100, 4).astype(np.float32))
ys = torch.from_numpy(np.random.randint(0, 2, size=(100,)).astype(np.int64))

dataset = MyDataset(xs, ys)
print(len(dataset))                        # 100
print(dataset[0])                          # 第 0 个样本：(x, y)
```

### 2.3 包装成 DataLoader

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=16,           # 每批 16 个样本
    shuffle=True,            # 打乱（训练集要 True，测试集 False）
    num_workers=0,           # 并行加载的进程数（Mac 设 0 防卡）
)

# 迭代
for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)    # torch.Size([16, 4]) torch.Size([16])
    break                                  # 只看第一个 batch
```

> 💡 **关键认知**：DataLoader 自动把样本"堆叠"成 batch（`(4,) → (16, 4)`），shape 多了一维。

### 2.4 集成进训练循环

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# 假设 dataset 已经定义好了

loader = DataLoader(dataset, batch_size=16, shuffle=True)
model = nn.Linear(4, 2)                          # 4 维输入，2 类分类
loss_fn = nn.CrossEntropyLoss()                  # ⭐ 分类用交叉熵
optimizer = optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):                          # 把数据集过 10 遍
    total_loss = 0
    for batch_x, batch_y in loader:              # 每次取一个 batch
        # 1-5 步标准训练循环
        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    avg_loss = total_loss / len(loader)
    print(f"Epoch {epoch+1}: avg_loss={avg_loss:.4f}")
```

> ⭐ **这就是 PyTorch 训练的标准模板**。Day 4 用真实 MNIST 数据集套用这个模板。

### 2.5 内置 Dataset：torchvision

PyTorch 自带常用数据集（图像、文本、音频），不用自己写：

```python
from torchvision import datasets, transforms

# MNIST 手写数字（60000 训练 + 10000 测试）
transform = transforms.ToTensor()                # 把 PIL 图片转 Tensor
train_ds = datasets.MNIST(root='./data', train=True,  download=True, transform=transform)
test_ds  = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

print(len(train_ds), len(test_ds))               # 60000 10000
print(train_ds[0][0].shape, train_ds[0][1])      # torch.Size([1, 28, 28]) 5
```

> 💡 Day 4 直接用这个跑通 MNIST。

---

## 3. GPU 调用：把训练搬到加速器（15 分钟）

### 3.1 三个设备：cpu / cuda / mps

```python
import torch

device = torch.device(
    'cuda' if torch.cuda.is_available()           # NVIDIA GPU
    else 'mps' if torch.backends.mps.is_available()  # Apple Silicon
    else 'cpu'
)
print(f"使用设备：{device}")
```

> 💡 **本机情况判断**：
> - Mac M1/M2/M3：`mps`
> - Linux + NVIDIA：`cuda`
> - 其他：`cpu`（MNIST 也能跑，慢一点而已）

### 3.2 把模型和数据搬到设备

```python
model = MyModel().to(device)                     # 模型搬到设备

for batch_x, batch_y in loader:
    batch_x = batch_x.to(device)                 # 数据搬到设备
    batch_y = batch_y.to(device)

    logits = model(batch_x)                      # 计算自动在该设备上跑
    ...
```

> ⚠️ **三件套必须同设备**：模型、输入、目标。任意一个不同步就报错。

### 3.3 训练后取数据回 CPU

```python
y_pred = model(test_x.to(device))
y_pred_cpu = y_pred.detach().cpu().numpy()       # GPU → CPU → NumPy
```

> 💡 `detach()` 表示"和计算图断开"（推理不需要梯度），`cpu()` 搬回主存，`numpy()` 转成 NumPy。**这一连串组合很常见**。

### 3.4 性能小贴士

```python
# 1. pin_memory：DataLoader 加速 GPU 数据传输
loader = DataLoader(dataset, batch_size=64, pin_memory=True)

# 2. non_blocking：异步传输
batch_x = batch_x.to(device, non_blocking=True)

# 3. 推理用 torch.no_grad()：省内存 + 加速
with torch.no_grad():
    pred = model(test_x)
```

> 🎯 **本周不用都用上**，知道有就行。

---

## 4. 完整训练 + 评估模板（15 分钟）

把今天学的全部串起来：

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# ============ 0. 设备 ============
device = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)

# ============ 1. 模型 ============
class MLPClassifier(nn.Module):
    def __init__(self, in_dim, hidden, out_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, out_dim),
        )
    def forward(self, x):
        return self.net(x)

model = MLPClassifier(in_dim=4, hidden=32, out_dim=2).to(device)

# ============ 2. 损失 + 优化器 ============
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-3)

# ============ 3. 数据（这里用假数据，Day 4 换 MNIST）============
# train_loader, test_loader = ...

# ============ 4. 训练函数 ============
def train_one_epoch(model, loader, loss_fn, optimizer, device):
    model.train()
    total_loss = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)

        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        total_loss += loss.item()
    return total_loss / len(loader)

# ============ 5. 评估函数 ============
@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        pred = model(x).argmax(dim=-1)
        correct += (pred == y).sum().item()
        total += y.size(0)
    return correct / total

# ============ 6. 主循环 ============
# for epoch in range(10):
#     train_loss = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
#     test_acc   = evaluate(model, test_loader, device)
#     print(f"Epoch {epoch+1}: loss={train_loss:.4f}, acc={test_acc:.4f}")
```

> ⭐ **这个模板背下来**。Day 4 / Day 5 + 阶段 3 / 阶段 4 反复用。

---

## 5. 模型保存与加载（5 分钟）

```python
# 保存：只存参数（推荐）
torch.save(model.state_dict(), 'model.pth')

# 加载
model = MLPClassifier(4, 32, 2)                  # 先建一个同结构的模型
model.load_state_dict(torch.load('model.pth'))
model.eval()                                     # 切换到推理模式
```

> 💡 **为什么不存整个模型对象**：跨 PyTorch 版本可能不兼容，存参数最稳。

---

## 6. 常见疑惑 FAQ（5 分钟）

### Q1：epoch / batch / step / iteration 都是啥？

A：
- **batch**：一次喂的数据量（如 16 / 32 / 64）
- **iteration / step**：一次 batch 训练（=1 次 forward+backward）
- **epoch**：把数据集**完整过一遍**

举例：60000 样本 + batch_size=64 → 1 epoch ≈ 938 个 step。

### Q2：为什么要 `model.train()` / `model.eval()`？

A：因为有些层在训练 / 推理时行为不同：
- **Dropout**：训练时随机丢弃神经元，推理时不丢
- **BatchNorm**：训练时用当前 batch 的均值方差，推理时用累计的全局统计

> 💡 **不切换会导致推理结果不稳定**，记得切。

### Q3：`@torch.no_grad()` 装饰器是干嘛的？

A：标记函数内不需要计算梯度。**评估 / 推理时用，省内存、加速**。
等价于：
```python
with torch.no_grad():
    ...
```

### Q4：lr 怎么调？

A：
1. **AdamW 默认 1e-3 试**
2. loss 不降 → lr 调小（× 0.1）
3. loss 飞了 → lr 调小（× 0.1）
4. loss 降得太慢 → lr 调大（× 3）

---

## 📋 今日任务清单

- [ ] 把 §1.2 的代码**手敲一遍**，体会 optimizer 的简洁
- [ ] 跑通 §2.4 的 DataLoader 训练循环，看 loss 怎么变化
- [ ] 验证你的设备：跑 §3.1 看是 `cpu` / `cuda` / `mps`
- [ ] **把 §4 的完整模板存到笔记里**，明天 MNIST 直接套
- [ ] 完成 [`练习/day3_练习.py`](./练习/day3_练习.py)

---

## 🎯 自测：今天你应该能...

- [ ] 不查资料默写出"5 步训练循环"
- [ ] 解释 SGD vs Adam vs AdamW 的区别（一句话级）
- [ ] 自己定义一个 Dataset 子类
- [ ] 解释 epoch / batch / step 的关系
- [ ] 把模型和数据搬到 GPU 上跑
- [ ] 保存和加载模型参数

---

## 🆘 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| Mac 上 `num_workers > 0` 卡死 | macOS fork 问题 | 设 `num_workers=0` |
| GPU OOM（out of memory）| batch_size 太大 | 调小 batch_size |
| 评估时 loss 突然变怪 | 没切 `model.eval()` | Dropout 仍在乱丢 |
| 训练 loss 降不下来 | lr 不对 / 模型太小 / 数据问题 | 先 lr × 0.1 试 |
| `argmax` 维度搞错 | 不确定哪一维 | 分类任务用 `argmax(dim=-1)`（最后一维）|

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 4 · MNIST 实战](./Day4-MNIST实战.md) ⭐。

> 预告：30 行代码训练你的第一个真实神经网络，识别手写数字 0-9，准确率 > 97%。
