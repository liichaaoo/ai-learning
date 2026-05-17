# Day 5 · 训练循环模板速查（永久使用）

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 Week 1 学的揉成一份永久可用的速查表 + 完成一个综合演练
> 📋 练习：[`练习/day5_综合.py`](./练习/day5_综合.py)

---

## 0. 心法

> **今天不是新概念**，是**整理 + 内化**。
>
> 整理出的内容会陪你做 RAG、做 Agent，甚至以后微调小模型——整个 AI 工程师生涯反复用。

---

## 1. 一图速记：训练循环全景

```
┌──────────────────────────────────────────────────────────────┐
│                    PyTorch 训练循环全景                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                            │
│  │  Dataset     │ ── __len__、__getitem__                    │
│  └──────┬───────┘                                            │
│         ↓                                                    │
│  ┌──────────────┐                                            │
│  │  DataLoader  │ ── batch / shuffle / num_workers           │
│  └──────┬───────┘                                            │
│         ↓ for x, y in loader:                                │
│         ↓                                                    │
│  ┌──────────────┐  forward                                   │
│  │  nn.Module   │ ───────────→ logits                        │
│  └──────┬───────┘                  ↓                         │
│         │                  ┌───────────────┐                 │
│         │                  │   Loss 函数   │                 │
│         │                  └───────┬───────┘                 │
│         │                          ↓                         │
│         │                  loss.backward() ⭐                │
│         │                          ↓                         │
│         │                  ┌───────────────┐                 │
│         │                  │   Optimizer   │                 │
│         └──────────────────┤  .step()      │                 │
│         参数更新 ←──────── │  .zero_grad() │                 │
│                            └───────────────┘                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

> 💡 **背下这张图**。下周看 Transformer 训练代码、阶段 3 看 LangChain4j 的 `EmbeddingModel.embed`，都是这套结构在不同层包装。

---

## 2. 五步训练循环（核心模板）

```python
for epoch in range(N):
    model.train()                           # ① 切训练模式
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)   # ② 数据搬设备

        # 五步圣经
        logits = model(x)                   # 1. forward
        loss = loss_fn(logits, y)           # 2. compute loss
        loss.backward()                     # 3. backward（自动求梯度）
        optimizer.step()                    # 4. 更新参数
        optimizer.zero_grad()               # 5. 梯度清零

    # 每个 epoch 评估一次
    model.eval()
    with torch.no_grad():
        for x, y in test_loader:
            ...
```

> ⭐ **能闭着眼写出来才算 Week 1 通关**。

---

## 3. 通用训练脚手架（可直接套用）

```python
"""
PyTorch 通用训练脚手架（Week 1 学习成果固化版）
功能：训练 + 评估 + 保存 + 训练曲线
"""
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader


def get_device() -> torch.device:
    """自动选择最佳设备：cuda > mps > cpu"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


def train_one_epoch(model, loader, loss_fn, optimizer, device):
    """训练一个 epoch，返回平均 loss"""
    model.train()
    total_loss = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader, device, task: str = 'classification'):
    """评估，返回准确率（分类）或 MSE（回归）"""
    model.eval()
    if task == 'classification':
        correct, total = 0, 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=-1)
            correct += (pred == y).sum().item()
            total += y.size(0)
        return correct / total
    else:  # regression
        total_loss = 0
        loss_fn = nn.MSELoss()
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            total_loss += loss_fn(model(x), y).item()
        return total_loss / len(loader)


def fit(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int = 10,
    lr: float = 1e-3,
    save_path: str | None = None,
    task: str = 'classification',
):
    """完整训练流程"""
    device = get_device()
    print(f"使用设备：{device}")
    model = model.to(device)

    if task == 'classification':
        loss_fn = nn.CrossEntropyLoss()
    else:
        loss_fn = nn.MSELoss()

    optimizer = optim.AdamW(model.parameters(), lr=lr)

    history = {'train_loss': [], 'metric': []}

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        metric = evaluate(model, test_loader, device, task)
        history['train_loss'].append(train_loss)
        history['metric'].append(metric)

        metric_name = 'acc' if task == 'classification' else 'mse'
        print(f"Epoch {epoch:3d}/{epochs} | "
              f"loss={train_loss:.4f} | {metric_name}={metric:.4f} | "
              f"time={time.time()-t0:.1f}s")

    # 保存
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), save_path)
        print(f"模型已保存：{save_path}")

    return history


def plot_history(history, save_path: str | None = None):
    """画训练曲线"""
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(history['train_loss'], 'b-', label='Train Loss')
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss', color='b')
    ax2 = ax1.twinx()
    ax2.plot(history['metric'], 'r-', label='Metric')
    ax2.set_ylabel('Metric', color='r')
    plt.title('Training Curve')
    if save_path:
        plt.savefig(save_path)
    plt.show()
```

> ⭐ 把这份代码存到笔记里，下次做任何 PyTorch 项目直接 import 用。

---

## 4. 综合演练：用脚手架重做 MNIST（30 分钟）

```python
"""day5_综合.py · 用脚手架重做 MNIST"""
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 假设上面的脚手架在 train_utils.py 里
from train_utils import fit, plot_history

# 1. 数据
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),
])
train_ds = datasets.MNIST('./data', train=True,  download=True, transform=transform)
test_ds  = datasets.MNIST('./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
test_loader  = DataLoader(test_ds,  batch_size=256)

# 2. 模型
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
    nn.Linear(128,  10),
)

# 3. 一行训练 + 评估 + 保存
history = fit(
    model, train_loader, test_loader,
    epochs=10, lr=1e-3,
    save_path='./checkpoints/mnist.pth',
)

# 4. 画曲线
plot_history(history, save_path='./checkpoints/curve.png')
```

> 💡 体会"工程化"的爽点：核心代码只剩**模型定义 + 一行 fit**，其他都被脚手架封装了。

---

## 5. PyTorch 速查表（永久版）

### 5.1 Tensor 速查

```python
# 创建
torch.tensor([1, 2, 3])          # 从 list
torch.zeros(3, 4)                # 全零
torch.ones(3, 4)                 # 全一
torch.randn(3, 4)                # 标准正态分布
torch.arange(0, 10, 2)           # [0,2,4,6,8]

# 形状
x.shape                          # torch.Size([...])
x.reshape(2, -1)                 # 改形状
x.transpose(0, 1)                # 交换两维
x.unsqueeze(0)                   # 加一维（[3] → [1, 3]）
x.squeeze()                      # 去掉所有大小为 1 的维

# 运算
a + b, a * b, a @ b              # 加 / 乘 / 矩阵乘
torch.matmul(a, b)               # @ 等价
a.sum(dim=-1, keepdim=True)      # 沿某维求和
a.mean(); a.max(); a.argmax(dim=-1)

# 设备 + 类型
x.to(device)
x.to(torch.float32)
x.cuda(); x.cpu()

# 取值
x.item()                         # 标量 → Python float
x.tolist()                       # → Python list
x.detach().cpu().numpy()         # → NumPy
```

### 5.2 nn 速查

```python
import torch.nn as nn

# 常用层
nn.Linear(in, out)                  # 全连接
nn.Embedding(vocab_size, dim)       # 词嵌入（Week 2 主角之一）
nn.LayerNorm(dim)                   # 层归一化（Transformer 标配）
nn.Dropout(0.1)                     # Dropout
nn.MultiheadAttention(dim, heads)   # Week 2 主角

# 激活函数
nn.ReLU(); nn.GELU(); nn.SiLU()

# 损失函数
nn.CrossEntropyLoss()           # 分类（含 Softmax）
nn.BCEWithLogitsLoss()          # 二分类（含 Sigmoid）
nn.MSELoss()                    # 回归

# 模型组装
nn.Sequential(layer1, layer2, ...)
class MyModel(nn.Module):
    def __init__(self): super().__init__(); ...
    def forward(self, x): return ...
```

### 5.3 Optimizer 速查

```python
import torch.optim as optim

# 主流三选一
optim.SGD(params, lr=0.01, momentum=0.9)
optim.Adam(params, lr=1e-3)
optim.AdamW(params, lr=1e-4, weight_decay=0.01)    # ⭐ LLM 主流

# 学习率调度
optim.lr_scheduler.StepLR(opt, step_size=3, gamma=0.5)
optim.lr_scheduler.CosineAnnealingLR(opt, T_max=100)
```

### 5.4 训练 / 推理切换

```python
model.train()                           # 训练模式
model.eval()                            # 评估模式

with torch.no_grad():                   # 禁用梯度
    pred = model(x)

@torch.no_grad()                        # 装饰器版
def evaluate(...): ...
```

### 5.5 保存 / 加载

```python
torch.save(model.state_dict(), 'model.pth')
model.load_state_dict(torch.load('model.pth'))
model.eval()
```

---

## 6. 常见坑大汇总（Week 1 总结）

| 现象 | 真相 |
|------|------|
| loss 不下降 | 检查 lr / 数据归一化 / `optimizer.zero_grad()` 是否漏 |
| loss 飞了（NaN）| lr 太大 / 数据有 NaN / 模型最后又加了 Softmax 与 CE 冲突 |
| 准确率始终很低（如 10%）| 看是不是分类问题用了回归 loss，反之亦然 |
| GPU 报 OOM | batch_size 太大 |
| MPS 报算子未实现 | 部分老 op MPS 不支持，退回 CPU |
| 模型 / 数据 device 不一致 | 都 `.to(device)` |
| eval 时结果飘 | 没 `model.eval()`，Dropout 还在乱丢 |
| 多次 backward 梯度变怪 | 没 `optimizer.zero_grad()` |
| Mac DataLoader 卡死 | `num_workers=0` |

---

## 7. Week 1 收官检查（必做）

> 完成这一节才算正式通关 Week 1。

### 7.1 概念自测（口述给自己听）

- [ ] 神经网络是什么？为什么要"非线性激活"？
- [ ] 前向传播 vs 反向传播分别在干什么？
- [ ] 默写五步训练循环
- [ ] 解释 epoch / batch / step 的关系
- [ ] SGD 和 Adam 哪个收敛快？为什么？
- [ ] 为什么 `model.train()` 和 `model.eval()` 要切换？

### 7.2 代码自测（手敲）

- [ ] 不看教程，从 `import torch` 开始写一个最简 MNIST（可以查 API 名）
- [ ] 自己写一个 Dataset 子类
- [ ] 写一个三层 MLP（用 nn.Module 子类，不能用 Sequential）
- [ ] 把训练曲线画出来

### 7.3 产出沉淀（写进笔记）

- [ ] **PyTorch 训练循环模板.md**（贴 §3 的脚手架）
- [ ] **PyTorch 速查表.md**（贴 §5）
- [ ] **MNIST 实战截图**（准确率 + 训练曲线 + 8 张预测样本）
- [ ] 一段反思："这周我学到了什么？哪里最卡？"

---

## 8. 与下周的连接

> 下周 Week 2 你会发现：**Transformer 也是 nn.Module 子类**。

```python
class TransformerBlock(nn.Module):                 # ← 还是 nn.Module
    def __init__(self, dim, heads):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads)
        self.ln1  = nn.LayerNorm(dim)
        self.ffn  = nn.Sequential(
            nn.Linear(dim, dim*4), nn.GELU(),
            nn.Linear(dim*4, dim),
        )
        self.ln2  = nn.LayerNorm(dim)

    def forward(self, x):                          # ← 还是 forward
        # 残差 + 注意力
        x = x + self.attn(self.ln1(x), self.ln1(x), self.ln1(x))[0]
        # 残差 + FFN
        x = x + self.ffn(self.ln2(x))
        return x
```

> 💡 **看到没？Transformer 用的所有积木 Day 2~3 全见过**：
> - `nn.Module` ✅
> - `nn.Linear` ✅
> - `nn.LayerNorm` ✅
> - `nn.GELU` ✅
> - 残差连接（`x + ...`）只是普通 Tensor 加法 ✅
>
> **唯一新东西是 `MultiheadAttention`**，下周专门讲。

---

## 📋 今日任务清单

- [ ] 把 §3 的脚手架代码保存到 `train_utils.py`
- [ ] 用脚手架跑一遍 §4 的综合演练
- [ ] 完成 §7.1 的概念自测（口述给自己听）
- [ ] 完成 §7.3 的笔记沉淀
- [ ] 在周报里写下这周的产出 + 反思

---

## 🎉 完成 Week 1，干得漂亮！

回头看看你这周做了什么：

```
Day 1：理解了神经网络的本质
Day 2：用 PyTorch 自动求梯度，训练了一条直线
Day 3：把训练循环工程化（Optimizer + DataLoader + GPU）
Day 4：训练真实模型识别手写数字，准确率 > 97%
Day 5（今天）：固化成永久速查表，准备好进 Transformer
```

> 🚀 **下周 Week 2，你会站在 Transformer 面前——LLM 全部建立在它之上。**

---

## 🔗 相关链接

- ⬆️ [回到 Week 1 总览](./README.md)
- ➡️ [Week 2 · Transformer](../Week2-Transformer/)（下周开放）
- 📋 [回到阶段 2 总览](../README.md)
- 🎓 [path-research 的深度学习章节](../../../path-research/)（学有余力可以读）
