"""
Day 5 练习 · Week 1 综合演练

把这周学的揉成一份「通用训练脚手架」+ 用它重做 MNIST。

输出：
    - train_utils.py 不另开文件，直接放本文件
    - checkpoints/mnist_final.pth
    - checkpoints/curve.png
"""
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
DATA_DIR = Path(__file__).parent / "data"
CHECKPOINT_DIR.mkdir(exist_ok=True)


# ═════════════════════════════════════════════════════════════════
# 第一部分：通用训练脚手架（直接复用，下次做项目原样搬走）
# ═════════════════════════════════════════════════════════════════

def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


def train_one_epoch(model, loader, loss_fn, optimizer, device):
    model.train()
    total = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total += loss.item()
    return total / len(loader)


@torch.no_grad()
def evaluate(model, loader, device, task: str = 'classification'):
    model.eval()
    if task == 'classification':
        correct, total = 0, 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=-1)
            correct += (pred == y).sum().item()
            total += y.size(0)
        return correct / total
    # regression
    loss_fn = nn.MSELoss()
    total = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        total += loss_fn(model(x), y).item()
    return total / len(loader)


def fit(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int = 10,
    lr: float = 1e-3,
    save_path: str | None = None,
    task: str = 'classification',
) -> dict:
    device = get_device()
    print(f"[fit] 使用设备：{device}")
    model = model.to(device)

    loss_fn = nn.CrossEntropyLoss() if task == 'classification' else nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)

    history = {'train_loss': [], 'metric': []}

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        loss = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        metric = evaluate(model, test_loader, device, task)
        history['train_loss'].append(loss)
        history['metric'].append(metric)

        name = 'acc' if task == 'classification' else 'mse'
        print(f"  Epoch {epoch:3d}/{epochs} | "
              f"loss={loss:.4f} | {name}={metric:.4f} | "
              f"time={time.time()-t0:.1f}s")

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), save_path)
        print(f"[fit] 模型已保存：{save_path}")

    return history


def plot_history(history: dict, save_path: str | None = None):
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(history['train_loss'], 'b-o', label='train_loss')
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss', color='b')
    ax2 = ax1.twinx()
    ax2.plot(history['metric'], 'r-s', label='metric')
    ax2.set_ylabel('Metric', color='r')
    plt.title('Training Curve')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        print(f"[plot] 曲线已保存：{save_path}")


# ═════════════════════════════════════════════════════════════════
# 第二部分：用脚手架重做 MNIST
# ═════════════════════════════════════════════════════════════════

def run_mnist():
    from torchvision import datasets, transforms

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    train_ds = datasets.MNIST(str(DATA_DIR), train=True,  download=True, transform=transform)
    test_ds  = datasets.MNIST(str(DATA_DIR), train=False, download=True, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=64,  shuffle=True)
    test_loader  = DataLoader(test_ds,  batch_size=256, shuffle=False)

    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(128,  10),
    )

    history = fit(
        model, train_loader, test_loader,
        epochs=8, lr=1e-3,
        save_path=str(CHECKPOINT_DIR / "mnist_final.pth"),
    )

    plot_history(history, save_path=str(CHECKPOINT_DIR / "curve.png"))


# ═════════════════════════════════════════════════════════════════
# 第三部分（挑战）：用脚手架做一个回归任务
# ═════════════════════════════════════════════════════════════════
class SinDataset(torch.utils.data.Dataset):
    def __init__(self, n: int = 2000):
        self.xs = torch.linspace(-3.1416, 3.1416, n).unsqueeze(-1)
        self.ys = torch.sin(self.xs) + torch.randn_like(self.xs) * 0.05

    def __len__(self):
        return len(self.xs)

    def __getitem__(self, idx):
        return self.xs[idx], self.ys[idx]


def run_sin():
    """用同一份脚手架做回归（task='regression'）"""
    train_ds = SinDataset(2000)
    test_ds  = SinDataset(500)
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_loader  = DataLoader(test_ds,  batch_size=128)

    model = nn.Sequential(
        nn.Linear(1, 32), nn.ReLU(),
        nn.Linear(32, 32), nn.ReLU(),
        nn.Linear(32, 1),
    )

    history = fit(
        model, train_loader, test_loader,
        epochs=15, lr=1e-3, task='regression',
        save_path=str(CHECKPOINT_DIR / "sin.pth"),
    )

    # 测一下 sin(1.0) ≈ 0.8415
    device = get_device()
    model = model.to(device).eval()
    with torch.no_grad():
        x = torch.tensor([[1.0]], device=device)
        print(f"\n模型预测 sin(1.0) ≈ {model(x).item():.4f}（真实 0.8415）")


# ═════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("Week 1 综合演练 · 用通用脚手架做两个任务")
    print("=" * 60)

    print("\n>>> 任务 1：MNIST 分类")
    run_mnist()

    print("\n>>> 任务 2：sin 回归（同一份脚手架）")
    run_sin()

    print("\n" + "=" * 60)
    print("🎉 Week 1 完美收官！")
    print("=" * 60)
    print("""
你这周做了什么：
  ✅ 理解了神经网络是「会自调参的复合函数」
  ✅ 学会用 PyTorch 自动求梯度
  ✅ 掌握了五步训练循环
  ✅ 训练了 MNIST，准确率 > 97%
  ✅ 写出了一份能复用的训练脚手架

下周 Week 2：进入 Transformer 的世界 🚀
""")
