"""
Day 4 练习 · 微积分与梯度（认知级）

运行：python day4_练习.py

⚠️ 需要先装 PyTorch:
    pip install torch
"""

import numpy as np


# =============================================================================
# 题 1（概念）：复盘
# =============================================================================
# 不查资料，用自己的话回答（写在注释里）：

# TODO: 1. 导数是什么？
# 你的答案:

# TODO: 2. 梯度的方向指向什么？
# 你的答案:

# TODO: 3. 为什么叫"梯度下降"而不是"梯度上升"？
# 你的答案:

# TODO: 4. 链式法则一句话解释
# 你的答案:

# TODO: 5. 反向传播在干什么？
# 你的答案:


# =============================================================================
# 题 2（数值）：用"数值微分"模拟导数
# =============================================================================
# 导数的定义：f'(x) ≈ (f(x+h) - f(x)) / h，当 h 很小时
# 我们不会这样算（精度差），但这有助于你理解"导数是变化率"

def numerical_derivative(f, x, h=1e-5):
    """求 f 在 x 点的数值导数"""
    return (f(x + h) - f(x - h)) / (2 * h)


def q2_derivative_demo():
    # f(x) = x² 的导数应该是 2x
    f = lambda x: x ** 2
    for x in [1.0, 2.0, 3.0, 5.0]:
        numerical = numerical_derivative(f, x)
        theoretical = 2 * x
        print(f"f(x) = x², x={x}: 数值导数={numerical:.6f}, 理论={theoretical:.6f}")

    print()
    print("💡 数值导数和理论解基本一致")
    print("   实际 PyTorch 用的是'解析求导'（按规则自动推），精度更高")


# =============================================================================
# 题 3（PyTorch 基础）：autograd 初体验
# =============================================================================

def q3_autograd_demo():
    try:
        import torch
    except ImportError:
        print("❌ 请先安装 PyTorch: pip install torch")
        return

    # y = x² + 2x + 1，求 x=3 时的 dy/dx
    x = torch.tensor(3.0, requires_grad=True)
    y = x ** 2 + 2 * x + 1

    # 一行搞定！
    y.backward()

    print(f"x = 3")
    print(f"y = x² + 2x + 1 = {y.item()}")
    print(f"dy/dx = {x.grad.item()}   # 理论值 2x+2=8")
    print()
    print("💡 autograd 自动推出了导数，你没写任何公式！")


# =============================================================================
# 题 4（核心）：一维线性回归的完整训练循环
# =============================================================================
# 目标：学习 y = 2x + 1 这个函数
# 模型：y_pred = w * x + b
# 训练：让 w 从随机初始化最终学到 2，b 学到 1

def q4_linear_regression():
    try:
        import torch
    except ImportError:
        print("❌ 请先安装 PyTorch: pip install torch")
        return

    # 1. 生成假数据: y = 2x + 1 + 噪声
    torch.manual_seed(42)
    X = torch.linspace(0, 10, 100).reshape(-1, 1)
    y_true = 2 * X + 1 + torch.randn_like(X) * 0.5

    # 2. 初始化参数（可训练）
    w = torch.randn(1, requires_grad=True)
    b = torch.randn(1, requires_grad=True)

    # 3. 优化器（对 w 和 b 做梯度下降）
    optimizer = torch.optim.SGD([w, b], lr=0.01)

    print(f"初始 w={w.item():.4f}, b={b.item():.4f}")
    print()

    # 4. 训练循环
    for epoch in range(200):
        # Forward
        y_pred = w * X + b
        loss = ((y_pred - y_true) ** 2).mean()   # MSE

        # 三板斧：zero_grad → backward → step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 40 == 0:
            print(f"Epoch {epoch+1:3d}: loss={loss.item():.4f}, w={w.item():.4f}, b={b.item():.4f}")

    print()
    print(f"✅ 学完：w={w.item():.4f} (目标 2.0)")
    print(f"   学完：b={b.item():.4f} (目标 1.0)")
    print()
    print("💡 这就是神经网络训练的本质：")
    print("   每次算 loss、反向传播、更新参数，重复几百次")
    print("   参数慢慢逼近真实值")


# =============================================================================
# 题 5（理解）：梯度消失直观感受
# =============================================================================
# 为什么深层网络训练难？看下面的"梯度连乘"

def q5_gradient_vanishing():
    # 假设每一层的梯度都是 0.5（比如用 sigmoid 激活函数）
    # 经过 N 层反向传播，梯度变成 0.5^N
    layers_to_try = [1, 3, 5, 10, 20, 50]

    print("每层梯度=0.5 时，反向传到第 N 层的梯度:")
    for n in layers_to_try:
        grad = 0.5 ** n
        print(f"  N={n:2d} 层: grad = {grad:.10f}")

    print()
    print("💡 观察：层数一多，梯度几乎变成 0 —— 这就是'梯度消失'")
    print("   导致深层网络最底层的参数几乎学不动")
    print("   解决方法: ReLU 激活函数、残差连接（ResNet）、LayerNorm")


# =============================================================================
# 题 6（思考）：训练循环的 4 步为啥是这个顺序？
# =============================================================================
# 标准顺序是：
#   1. y_pred = model(x)        forward
#   2. loss = criterion(...)
#   3. optimizer.zero_grad()    清零上一步的梯度
#   4. loss.backward()          反向传播算梯度
#   5. optimizer.step()         更新参数
#
# TODO: 如果把 zero_grad 忘了会怎样？
# 你的答案:
# （提示：梯度会累加，参数被错误地 over-update）

# TODO: 如果把 backward 和 step 反过来会怎样？
# 你的答案:
# （提示：step 时梯度还没算，无法更新）


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 2 · 数值导数 vs 理论导数")
    print("=" * 60)
    q2_derivative_demo()

    print()
    print("=" * 60)
    print("题 3 · PyTorch autograd")
    print("=" * 60)
    q3_autograd_demo()

    print()
    print("=" * 60)
    print("题 4 · 完整训练循环（学 y = 2x + 1）")
    print("=" * 60)
    q4_linear_regression()

    print()
    print("=" * 60)
    print("题 5 · 梯度消失直观")
    print("=" * 60)
    q5_gradient_vanishing()

    print()
    print("✅ Day 4 练习完成。最后一天 Day 5：综合应用（手搓 Attention）")
