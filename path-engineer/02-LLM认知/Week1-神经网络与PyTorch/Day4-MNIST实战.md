# Day 4 · MNIST 实战 ⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：30 行代码训练手写数字识别，准确率 > 97%
> 📋 练习：[`练习/day4_mnist.py`](./练习/day4_mnist.py)

---

## 0. 心法

> **今天是 Week 1 的"成果验收日"**。
>
> 跑通 MNIST 之后，你就有了"我能训练神经网络"的底气，下周看 Transformer 心里会非常稳。

---

## 1. MNIST 数据集（5 分钟）

- **是什么**：60000 张训练图 + 10000 张测试图，每张 28×28 灰度图，内容是手写数字 0-9
- **任务**：给一张图，预测它是 0-9 哪个数字（**10 分类**）
- **地位**："深度学习界的 Hello World"，几乎所有教程的第一个案例

```
图片 (28×28 灰度) → [神经网络] → 10 个 logit（每个类别的得分）→ argmax → 预测
```

---

## 2. 30 行版本（先跑通）

> 把 Day 3 的模板套上 MNIST，**不到 30 行**搞定。

```python
"""day4_mnist_minimal.py · 30 行 MNIST 完整训练"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ============ 1. 设备 ============
device = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)

# ============ 2. 数据 ============
transform = transforms.Compose([
    transforms.ToTensor(),                 # PIL → Tensor，值归到 [0, 1]
    transforms.Normalize((0.1307,), (0.3081,)),  # MNIST 均值、标准差（标准做法）
])
train_ds = datasets.MNIST('./data', train=True,  download=True, transform=transform)
test_ds  = datasets.MNIST('./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
test_loader  = DataLoader(test_ds,  batch_size=256)

# ============ 3. 模型（最简版：MLP）============
model = nn.Sequential(
    nn.Flatten(),                # (1, 28, 28) → (784,)
    nn.Linear(784, 128), nn.ReLU(),
    nn.Linear(128,  10),
).to(device)

# ============ 4. Loss + Optimizer ============
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-3)

# ============ 5. 训练 ============
for epoch in range(3):
    model.train()
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        loss = loss_fn(model(x), y)
        loss.backward(); optimizer.step(); optimizer.zero_grad()

    # 评估
    model.eval()
    correct = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=-1)
            correct += (pred == y).sum().item()
    print(f"Epoch {epoch+1}: 测试准确率 = {correct/len(test_ds):.4f}")
```

### 跑一下

```bash
cd /Users/fletcherli/fletcher/AI/AI学习
source .venv/bin/activate
pip install torch torchvision

# 进入练习目录
cd path-engineer/02-LLM认知/Week1-神经网络与PyTorch/练习
python day4_mnist.py
```

第一次运行会自动下载 MNIST（约 11MB），约 1-2 分钟训练完。**应该看到准确率 ≥ 97%**。

> 🎉 **恭喜，你训练了你的第一个神经网络。**

---

## 3. 拆解每一步在做什么（20 分钟）

### 3.1 数据：为什么要 Normalize

```python
transforms.Normalize((0.1307,), (0.3081,))
```

- 把像素值从 `[0, 1]` 重新中心化到 `[均值=0, 标准差=1]` 附近
- 这两个数（0.1307、0.3081）是 MNIST 训练集的**全局像素均值/标准差**，前人算好的
- **作用**：让网络更容易优化（特征分布合理）

> 💡 **拓展认知**：这是"数据预处理"的标准操作，所有 CV / NLP 任务都会做类似的归一化。

### 3.2 模型：为什么 784 → 128 → 10

```
输入 28×28 = 784 维
   ↓ Linear(784, 128) + ReLU       ← "把图像信息压缩到 128 维特征"
中间 128 维
   ↓ Linear(128, 10)                ← "把 128 维特征映射到 10 类得分"
输出 10 维（每类一个 logit）
```

- 输入 = 图像像素铺平
- 隐藏层 128 维：经验值，可以是 64 / 256 / 512
- 输出 10 = 类别数

> 💡 **没有标准答案**。隐藏层维度是超参，可以调。

### 3.3 Loss：为什么 CrossEntropyLoss

PyTorch 的 `nn.CrossEntropyLoss` 内部 = `LogSoftmax + NLLLoss`，你**不用自己写 softmax**：

```python
# 你只需要输出 logits（任意实数）
logits = model(x)                   # shape [B, 10]

# CrossEntropyLoss 内部自动做 softmax → log → 取真实类别概率 → 取负
loss = loss_fn(logits, y)           # y 是整数标签 shape [B]
```

> ⚠️ **常见坑**：千万不要在模型最后又加一个 `Softmax` 层。`CrossEntropyLoss` 里已经包含了。

### 3.4 训练循环：还是那 5 步

```python
for x, y in train_loader:
    x, y = x.to(device), y.to(device)
    loss = loss_fn(model(x), y)            # forward + 算 loss
    loss.backward()                         # 反向传播
    optimizer.step()                        # 更新参数
    optimizer.zero_grad()                   # 梯度清零
```

> ⭐ Day 3 学的模板，完全照搬。

### 3.5 评估：为什么用 argmax

```python
pred = model(x).argmax(dim=-1)        # shape [B, 10] → [B]
correct += (pred == y).sum().item()
```

- 模型输出 10 个 logit，**最大那个对应的类别就是预测**
- `argmax(dim=-1)` 沿"类别维"取最大下标
- 和真实 `y`（整数）比较，相等就 +1

---

## 4. 升级版：改进准确率到 99%（20 分钟）

> 跑通 30 行版后，试试这些改进：

### 4.1 加深网络

```python
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 256), nn.ReLU(),
    nn.Linear(256, 128), nn.ReLU(),       # 加一层
    nn.Linear(128,  10),
).to(device)
```

### 4.2 加 Dropout 防止过拟合

```python
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(128,  10),
).to(device)
```

> 💡 Dropout 训练时按概率丢弃部分神经元，让网络更健壮。`model.eval()` 会自动关闭。

### 4.3 多训练几个 epoch + 学习率衰减

```python
optimizer = optim.AdamW(model.parameters(), lr=1e-3)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

for epoch in range(10):
    train_one_epoch(...)
    scheduler.step()                  # 每 3 epoch lr 减半
    test_acc = evaluate(...)
```

### 4.4 上 CNN（认知级，下面先看代码）

MLP 把图片铺平后丢失了"空间结构"。**CNN（卷积神经网络）**保留了，准确率能轻松到 99%+：

```python
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool  = nn.MaxPool2d(2)
        self.fc1   = nn.Linear(64 * 7 * 7, 128)
        self.fc2   = nn.Linear(128, 10)
        self.relu  = nn.ReLU()
        self.flatten = nn.Flatten()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))   # 28→14
        x = self.pool(self.relu(self.conv2(x)))   # 14→7
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = SimpleCNN().to(device)
```

> 🎯 **本周不需要深究 CNN**。CNN 主要用于图像，但 LLM 全是 Transformer + 注意力，**CV 不是你的赛道**。
> 这里只是让你看一眼"换个模型结构"是什么感觉。

---

## 5. 看几张预测样本（10 分钟）

```python
import matplotlib.pyplot as plt

# 取一批测试数据
x_batch, y_batch = next(iter(test_loader))
x_batch = x_batch.to(device)

model.eval()
with torch.no_grad():
    pred = model(x_batch).argmax(dim=-1).cpu()

# 画前 8 张
fig, axes = plt.subplots(2, 4, figsize=(10, 5))
for i, ax in enumerate(axes.flat):
    img = x_batch[i].cpu().squeeze()       # (1, 28, 28) → (28, 28)
    ax.imshow(img, cmap='gray')
    ax.set_title(f"真实:{y_batch[i].item()} 预测:{pred[i].item()}")
    ax.axis('off')
plt.tight_layout()
plt.savefig('mnist_预测.png')
plt.show()
```

> 💡 把这张图截图存进笔记，是 Week 1 最有仪式感的产出。

---

## 6. 训练曲线可视化（10 分钟，加分项）

记录每个 epoch 的 train_loss 和 test_acc，画出来：

```python
import matplotlib.pyplot as plt

train_losses, test_accs = [], []

for epoch in range(10):
    train_loss = train_one_epoch(...)
    test_acc   = evaluate(...)
    train_losses.append(train_loss)
    test_accs.append(test_acc)
    print(f"Epoch {epoch+1}: loss={train_loss:.4f} acc={test_acc:.4f}")

# 画两条曲线
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(train_losses, 'b-', label='Train Loss')
ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss', color='b')

ax2 = ax1.twinx()
ax2.plot(test_accs, 'r-', label='Test Acc')
ax2.set_ylabel('Accuracy', color='r')

plt.title('MNIST 训练曲线')
plt.savefig('训练曲线.png')
plt.show()
```

> 💡 **训练曲线**是观察模型训练状态的核心工具，所有项目都要画。

---

## 7. 把这周学的串成一个故事

```
Day 1：神经网络是"会自己调参的复合函数"，训练 = 找好参数
       ↓
Day 2：PyTorch 用 Tensor + autograd 让"求梯度"自动化
       ↓
Day 3：Optimizer + DataLoader 把训练循环工程化
       ↓
Day 4（今天）：用真实数据集 MNIST 验证整套体系能跑通 ✅
       ↓
Day 5（明天）：把所有招式整理成一份《PyTorch 训练循环模板》速查
       ↓
Week 2：把"全连接 MLP"换成 Transformer，就是 LLM 的核心结构 ⭐
```

> 🎉 **本周 70% 已完成**。继续！

---

## 📋 今日任务清单

- [ ] 跑通 §2 的 30 行版 MNIST，**准确率截图存进笔记**
- [ ] 跑 §4.2 的 Dropout 版本，看准确率有没有提升
- [ ] 画 §6 的训练曲线，存进笔记
- [ ] 完成 [`练习/day4_mnist.py`](./练习/day4_mnist.py)
- [ ] 在你的笔记里写一段话："今天我训练了一个 ___ 模型，识别 ___，准确率 ___"

---

## 🎯 自测：今天你应该能...

- [ ] 不看教程，从 `import torch` 开始**默写**一份 MNIST 训练代码（可以查 API）
- [ ] 解释为什么模型最后**不能**加 Softmax（CrossEntropyLoss 已含）
- [ ] 解释为什么训练前要 `model.train()`、评估前要 `model.eval()`
- [ ] 准确率 > 97%，并且能解释每一行代码

---

## 🆘 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 数据下载失败 | 网络问题 | 手动从 `http://yann.lecun.com/exdb/mnist/` 下载放 `./data/MNIST/raw/` |
| Mac 跑 mps 报"未实现的算子" | 部分 op MPS 不支持 | 退回 CPU 即可（MNIST 几分钟就完）|
| 准确率只有 10% | 漏了 `optimizer.zero_grad()` 或 lr 太大 | 检查训练循环 |
| `RuntimeError: 1D target tensor expected` | 标签维度错 | y 应该是 `[B]` 整数，不是 one-hot |
| 训练飞快但准确率不升 | 模型没 `.to(device)` 但数据搬了 | 模型也要搬 |

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 5 · 训练循环速查](./Day5-训练循环速查.md)。

> 预告：把这一周所有招式整理成一份**永久速查表**，下周和阶段 3 / 阶段 4 反复使用。
