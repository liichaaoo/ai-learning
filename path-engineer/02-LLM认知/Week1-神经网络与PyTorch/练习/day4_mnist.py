"""
Day 4 练习 · MNIST 手写数字识别（你的第一个真实神经网络）

环境：
    pip install torch torchvision matplotlib

目标：
    1. 跑通 30 行版本，准确率 > 97%
    2. 加 Dropout，看准确率
    3. 画训练曲线 + 8 张预测样本（截图存进笔记）
"""
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DATA_DIR = Path(__file__).parent / "data"
CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────
# 设备
# ─────────────────────────────────────────────────────────────────
def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


# ─────────────────────────────────────────────────────────────────
# 数据
# ─────────────────────────────────────────────────────────────────
def get_loaders(batch_size: int = 64):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    train_ds = datasets.MNIST(str(DATA_DIR), train=True,  download=True, transform=transform)
    test_ds  = datasets.MNIST(str(DATA_DIR), train=False, download=True, transform=transform)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader  = DataLoader(test_ds,  batch_size=256,        shuffle=False, num_workers=0)
    return train_loader, test_loader, test_ds


# ─────────────────────────────────────────────────────────────────
# 模型：MLP（不带 Dropout）
# ─────────────────────────────────────────────────────────────────
def build_mlp() -> nn.Module:
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 128), nn.ReLU(),
        nn.Linear(128, 10),
    )


# 模型：MLP（带 Dropout，更鲁棒）
def build_mlp_dropout() -> nn.Module:
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(128,  10),
    )


# ─────────────────────────────────────────────────────────────────
# 训练 + 评估
# ─────────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, loss_fn, optimizer, device):
    model.train()
    total_loss = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader, device) -> float:
    model.eval()
    correct, total = 0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        pred = model(x).argmax(dim=-1)
        correct += (pred == y).sum().item()
        total += y.size(0)
    return correct / total


# ─────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────
def main(use_dropout: bool = True, epochs: int = 5):
    device = get_device()
    print(f"使用设备：{device}")

    train_loader, test_loader, test_ds = get_loaders()

    model = (build_mlp_dropout() if use_dropout else build_mlp()).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"模型参数总数：{n_params:,}")

    loss_fn = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)

    history = {"loss": [], "acc": []}

    for epoch in range(1, epochs + 1):
        loss = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        acc = evaluate(model, test_loader, device)
        history["loss"].append(loss)
        history["acc"].append(acc)
        print(f"Epoch {epoch:2d}/{epochs} | train_loss={loss:.4f} | test_acc={acc:.4f}")

    # 保存
    save_path = CHECKPOINT_DIR / ("mnist_dropout.pth" if use_dropout else "mnist.pth")
    torch.save(model.state_dict(), save_path)
    print(f"模型已保存：{save_path}")

    # 画图
    try:
        plot_results(model, test_ds, history, device)
    except Exception as e:
        print(f"画图跳过（可能没装 matplotlib）：{e}")

    return model, history


def plot_results(model, test_ds, history, device):
    """画训练曲线 + 8 张样本预测"""
    import matplotlib.pyplot as plt

    # 训练曲线
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(history["loss"], 'b-o', label='train_loss')
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss', color='b')
    ax2 = ax1.twinx()
    ax2.plot(history["acc"], 'r-s', label='test_acc')
    ax2.set_ylabel('Accuracy', color='r')
    plt.title('MNIST Training Curve')
    plt.tight_layout()
    plt.savefig(CHECKPOINT_DIR / "训练曲线.png")
    print(f"训练曲线已保存：{CHECKPOINT_DIR / '训练曲线.png'}")

    # 预测样本
    model.eval()
    fig, axes = plt.subplots(2, 4, figsize=(10, 5))
    for i, ax in enumerate(axes.flat):
        img, label = test_ds[i]
        with torch.no_grad():
            pred = model(img.unsqueeze(0).to(device)).argmax(dim=-1).item()
        ax.imshow(img.squeeze(), cmap='gray')
        color = 'green' if pred == label else 'red'
        ax.set_title(f"真实:{label} 预测:{pred}", color=color)
        ax.axis('off')
    plt.tight_layout()
    plt.savefig(CHECKPOINT_DIR / "预测样本.png")
    print(f"预测样本已保存：{CHECKPOINT_DIR / '预测样本.png'}")


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== 跑 MLP（带 Dropout）===")
    main(use_dropout=True, epochs=5)
    print("\n✅ Day 4 完成。把 checkpoints/ 下的两张图截到笔记里！")
