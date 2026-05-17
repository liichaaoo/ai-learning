"""
Day 2 练习 · PyTorch 入门（上）：Tensor + autograd + nn.Module

环境：
    pip install torch
    python day2_练习.py

完成方式：把每个 TODO 填完，运行后输出符合预期。
"""
import torch
import torch.nn as nn


# ─────────────────────────────────────────────────────────────────
# 题 1：Tensor 基础操作
# ─────────────────────────────────────────────────────────────────
def test_tensor_basics():
    print("== 题 1：Tensor 基础 ==")

    # TODO 1.1：创建一个 3×4 的全零 Tensor
    a = None  # ← 你的代码
    print("a.shape:", a.shape if a is not None else "TODO")  # 期望: torch.Size([3, 4])

    # TODO 1.2：创建一个 [1, 2, 3, 4, 5] 的 Tensor
    b = None  # ← 你的代码
    print("b:", b)  # 期望: tensor([1, 2, 3, 4, 5])

    # TODO 1.3：把 b reshape 成 (5, 1)
    c = None  # ← 你的代码
    print("c.shape:", c.shape if c is not None else "TODO")  # 期望: torch.Size([5, 1])

    # TODO 1.4：算两个矩阵的矩阵乘
    M1 = torch.tensor([[1.0, 2], [3, 4]])
    M2 = torch.tensor([[5.0, 6], [7, 8]])
    product = None  # ← 你的代码（用 @ 或 torch.matmul）
    print("M1 @ M2 =", product)  # 期望: tensor([[19., 22.], [43., 50.]])

    # TODO 1.5：取 product[0, 0] 的标量值（Python float）
    scalar = None  # ← 你的代码
    print("scalar:", scalar)  # 期望: 19.0
    print()


# ─────────────────────────────────────────────────────────────────
# 题 2：autograd 自动求梯度
# ─────────────────────────────────────────────────────────────────
def test_autograd():
    print("== 题 2：autograd ==")

    # TODO 2.1：创建一个标量 x=4.0，要求梯度
    x = None  # ← 你的代码
    # TODO 2.2：定义 y = x^3 + 2x，反向传播，输出 dy/dx 在 x=4 处的值
    # 期望：dy/dx = 3x^2 + 2 = 50
    if x is not None:
        y = x ** 3 + 2 * x
        y.backward()
        print(f"dy/dx at x=4 = {x.grad.item()}")  # 期望: 50.0
    else:
        print("TODO 2.1/2.2")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 3：用 PyTorch 重写 Day 1 题 5 的线性回归
# ─────────────────────────────────────────────────────────────────
def train_linear_torch():
    print("== 题 3：用 PyTorch 训练 y = w*x + b ==")

    torch.manual_seed(0)
    xs = torch.linspace(-3, 3, 50)
    ys = 3 * xs - 2 + torch.randn(50) * 0.3

    # TODO 3.1：创建参数 w, b，初值 0，requires_grad=True
    w = None  # ← 你的代码
    b = None  # ← 你的代码

    lr = 0.05
    for step in range(1000):
        # TODO 3.2：完成五步
        # 1. y_pred = w * xs + b
        # 2. loss = ((y_pred - ys) ** 2).mean()
        # 3. loss.backward()
        # 4. with torch.no_grad(): w -= lr*w.grad; b -= lr*b.grad
        # 5. w.grad.zero_(); b.grad.zero_()
        pass  # ← 删掉 pass，填你的代码

        if step % 200 == 0 and w is not None and w.grad is not None:
            print(f"step {step:4d}: w={w.item():.4f}, b={b.item():.4f}")

    if w is not None:
        print(f"最终：w ≈ {w.item():.4f}（真实 3.0），b ≈ {b.item():.4f}（真实 -2.0）")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 4：自定义 nn.Module
# ─────────────────────────────────────────────────────────────────
class MyMLP(nn.Module):
    """
    TODO：实现一个 3 层 MLP
    结构：in_dim → hidden → hidden → out_dim
    隐藏层用 ReLU 激活，输出层不激活
    """

    def __init__(self, in_dim: int, hidden: int, out_dim: int):
        super().__init__()
        # TODO 4.1：定义 3 个 nn.Linear + 1 个 nn.ReLU
        # self.fc1 = nn.Linear(...)
        # self.fc2 = nn.Linear(...)
        # self.fc3 = nn.Linear(...)
        # self.relu = nn.ReLU()
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO 4.2：实现前向传播
        # h = self.relu(self.fc1(x))
        # h = self.relu(self.fc2(h))
        # return self.fc3(h)
        pass


def test_mymlp():
    print("== 题 4：自定义 MLP ==")
    model = MyMLP(in_dim=4, hidden=8, out_dim=2)
    x = torch.randn(3, 4)            # 一个 batch=3 的输入
    try:
        y = model(x)
        print("y.shape:", y.shape)   # 期望: torch.Size([3, 2])
        n_params = sum(p.numel() for p in model.parameters())
        print(f"参数总数: {n_params}")  # 期望: 4*8+8 + 8*8+8 + 8*2+2 = 138
    except Exception as e:
        print("还没实现完，报错：", e)
    print()


# ─────────────────────────────────────────────────────────────────
# 题 5（挑战）：用 nn.Module 训练分类
# 数据：随机生成的二分类数据，输入 4 维，2 类
# ─────────────────────────────────────────────────────────────────
def train_classifier():
    print("== 题 5：训练 MLP 分类器 ==")

    torch.manual_seed(42)
    # 生成 200 个样本：前 100 个偏向 [1,1,1,1]，后 100 个偏向 [-1,-1,-1,-1]
    n = 100
    x_pos = torch.randn(n, 4) + 1.0
    x_neg = torch.randn(n, 4) - 1.0
    X = torch.cat([x_pos, x_neg], dim=0)
    y = torch.cat([torch.ones(n, dtype=torch.long),
                   torch.zeros(n, dtype=torch.long)], dim=0)

    # 打乱
    perm = torch.randperm(2 * n)
    X, y = X[perm], y[perm]

    # TODO 5.1：建模
    model = MyMLP(in_dim=4, hidden=8, out_dim=2)
    # TODO 5.2：损失（CrossEntropyLoss）
    loss_fn = None  # ← 你的代码
    # TODO 5.3：优化器（手动 SGD：用 model.parameters() 遍历更新）

    if loss_fn is None:
        print("TODO 未完成")
        return

    lr = 0.1
    for step in range(500):
        logits = model(X)
        loss = loss_fn(logits, y)
        loss.backward()

        # 手动 SGD（Day 3 会换成 optimizer.step()）
        with torch.no_grad():
            for p in model.parameters():
                p -= lr * p.grad
                p.grad.zero_()

        if step % 100 == 0:
            acc = (logits.argmax(dim=-1) == y).float().mean().item()
            print(f"step {step:4d}: loss={loss.item():.4f} acc={acc:.4f}")

    final_acc = (model(X).argmax(dim=-1) == y).float().mean().item()
    print(f"最终训练准确率：{final_acc:.4f}（应该接近 1.0）")
    print()


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_tensor_basics()
    test_autograd()
    train_linear_torch()
    test_mymlp()
    train_classifier()
    print("✅ Day 2 练习完成。明天上 Optimizer + DataLoader！")
