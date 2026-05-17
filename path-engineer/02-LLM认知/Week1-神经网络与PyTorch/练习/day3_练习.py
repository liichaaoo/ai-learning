"""
Day 3 练习 · PyTorch 入门（下）：Optimizer + DataLoader + GPU

要点：
- 用 optimizer 替换手写参数更新
- 用 Dataset / DataLoader 替换手写迭代
- 把训练代码搬到 GPU/MPS 跑
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


# ─────────────────────────────────────────────────────────────────
# 工具：选设备
# ─────────────────────────────────────────────────────────────────
def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


# ─────────────────────────────────────────────────────────────────
# 题 1：自定义 Dataset
# 数据：y = sin(x) + 噪声
# ─────────────────────────────────────────────────────────────────
class SinDataset(Dataset):
    """
    TODO：实现一个返回 (x, y) 的数据集
    其中 x ∈ [-π, π]，y = sin(x) + 小噪声
    """

    def __init__(self, n_samples: int = 1000):
        # TODO 1.1：生成 n_samples 个 x（均匀分布）
        # self.xs = torch.linspace(-3.1416, 3.1416, n_samples).unsqueeze(-1)  # shape [N, 1]
        # self.ys = torch.sin(self.xs) + torch.randn_like(self.xs) * 0.05
        pass

    def __len__(self):
        # TODO 1.2
        pass

    def __getitem__(self, idx):
        # TODO 1.3：返回 (x_i, y_i)
        pass


def test_dataset():
    print("== 题 1：Dataset ==")
    ds = SinDataset(100)
    try:
        print("len:", len(ds))            # 期望: 100
        x0, y0 = ds[0]
        print("x[0]:", x0, "y[0]:", y0)
    except Exception as e:
        print("TODO 未完成：", e)
    print()


# ─────────────────────────────────────────────────────────────────
# 题 2：DataLoader 迭代
# ─────────────────────────────────────────────────────────────────
def test_loader():
    print("== 题 2：DataLoader ==")
    ds = SinDataset(100)
    if len(ds) == 0:
        print("先完成题 1")
        return

    # TODO 2.1：创建 DataLoader，batch_size=16，shuffle=True
    loader = None  # ← 你的代码

    if loader is None:
        return
    for x, y in loader:
        print("batch x.shape:", x.shape, "batch y.shape:", y.shape)
        # 期望：torch.Size([16, 1]) torch.Size([16, 1])
        break
    print()


# ─────────────────────────────────────────────────────────────────
# 题 3：用 optimizer 重写线性回归
# ─────────────────────────────────────────────────────────────────
def train_linear_with_optimizer():
    print("== 题 3：optimizer 版线性回归 ==")
    torch.manual_seed(0)
    xs = torch.linspace(-3, 3, 50).unsqueeze(-1)
    ys = 3 * xs - 2 + torch.randn_like(xs) * 0.3

    model = nn.Linear(1, 1)
    loss_fn = nn.MSELoss()

    # TODO 3.1：用 optim.SGD 创建优化器，lr=0.05
    optimizer = None  # ← 你的代码

    if optimizer is None:
        print("TODO 未完成")
        return

    for step in range(1000):
        # TODO 3.2：完成五步训练循环
        # 1. y_pred = model(xs)
        # 2. loss = loss_fn(y_pred, ys)
        # 3. loss.backward()
        # 4. optimizer.step()
        # 5. optimizer.zero_grad()
        pass

        if step % 200 == 0:
            w = model.weight.item()
            b = model.bias.item()
            print(f"step {step:4d}: w={w:.4f}, b={b:.4f}")

    print(f"最终：w ≈ {model.weight.item():.4f}, b ≈ {model.bias.item():.4f}")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 4（挑战）：用 DataLoader + Adam 拟合 sin 曲线
# ─────────────────────────────────────────────────────────────────
class SinModel(nn.Module):
    """3 层 MLP 拟合 sin"""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 32), nn.ReLU(),
            nn.Linear(32, 32), nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x)


def train_sin():
    print("== 题 4：拟合 sin 曲线 ==")
    device = get_device()
    print("使用设备：", device)

    ds = SinDataset(2000)
    if len(ds) == 0:
        print("先完成题 1")
        return

    loader = DataLoader(ds, batch_size=64, shuffle=True)
    model = SinModel().to(device)
    loss_fn = nn.MSELoss()

    # TODO 4.1：用 Adam，lr=1e-3
    optimizer = None

    if optimizer is None:
        print("TODO 未完成")
        return

    for epoch in range(20):
        total_loss = 0.0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            # TODO 4.2：标准五步
            # logits = model(x)
            # loss = loss_fn(logits, y)
            # loss.backward()
            # optimizer.step()
            # optimizer.zero_grad()
            # total_loss += loss.item()
            pass

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}: avg_loss = {total_loss/len(loader):.6f}")

    # 测试一个点
    model.eval()
    with torch.no_grad():
        test_x = torch.tensor([[1.0]], device=device)
        pred = model(test_x).item()
        print(f"sin(1.0) 真实 ≈ 0.8415，模型预测 ≈ {pred:.4f}")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 5：保存 & 加载模型
# ─────────────────────────────────────────────────────────────────
def test_save_load():
    print("== 题 5：保存 / 加载 ==")
    model = SinModel()
    # TODO 5.1：保存 model.state_dict() 到 'sin_model.pth'
    # torch.save(...)
    pass

    # TODO 5.2：建一个新模型 model2，加载刚才的参数
    model2 = SinModel()
    # model2.load_state_dict(torch.load('sin_model.pth'))
    # model2.eval()

    # 比对两个模型的第一个参数是否相同
    p1 = next(model.parameters())
    p2 = next(model2.parameters())
    same = torch.allclose(p1, p2)
    print(f"参数是否一致：{same}（期望 True）")
    print()


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_dataset()
    test_loader()
    train_linear_with_optimizer()
    train_sin()
    test_save_load()
    print("✅ Day 3 练习完成。明天上 MNIST 实战！")
