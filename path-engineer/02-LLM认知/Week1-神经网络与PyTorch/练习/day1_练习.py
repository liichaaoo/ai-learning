"""
Day 1 练习 · 神经网络基础（NumPy 版）

目标：用 NumPy 把神经网络的核心概念过一遍。
所有练习都用 NumPy 完成，不引入 PyTorch（明天才用）。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day1_练习.py
3. 输出符合预期就算 OK
"""
import numpy as np

np.random.seed(42)


# ─────────────────────────────────────────────────────────────────
# 题 1：实现三个激活函数
# ─────────────────────────────────────────────────────────────────
def sigmoid(x: np.ndarray) -> np.ndarray:
    """TODO：实现 sigmoid: 1 / (1 + e^(-x))"""
    # 你的代码
    pass


def relu(x: np.ndarray) -> np.ndarray:
    """TODO：实现 ReLU: max(0, x)"""
    # 你的代码
    pass


def gelu(x: np.ndarray) -> np.ndarray:
    """TODO：实现 GeLU 近似公式（参考 Day1 §2.2）"""
    # 你的代码
    pass


def test_activations():
    x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    print("== 题 1：激活函数 ==")
    print("sigmoid:", np.round(sigmoid(x), 4))   # 期望: [0.1192, 0.2689, 0.5, 0.7311, 0.8808]
    print("relu:   ", relu(x))                    # 期望: [0, 0, 0, 1, 2]
    print("gelu:   ", np.round(gelu(x), 4))       # 期望: 接近 [-0.0454, -0.1588, 0, 0.8412, 1.9546]
    print()


# ─────────────────────────────────────────────────────────────────
# 题 2：实现单个神经元
# ─────────────────────────────────────────────────────────────────
def neuron(x: np.ndarray, w: np.ndarray, b: float, activation=relu) -> float:
    """
    TODO：实现一个神经元 = w·x + b → activation
    :param x: 输入向量 (n,)
    :param w: 权重 (n,)
    :param b: 偏置（标量）
    :return: 标量输出
    """
    # 你的代码
    pass


def test_neuron():
    x = np.array([1.0, 2.0, 3.0])
    w = np.array([0.5, -0.3, 0.8])
    b = 0.1
    print("== 题 2：单神经元 ==")
    print("output:", neuron(x, w, b))   # 期望: 2.4
    print()


# ─────────────────────────────────────────────────────────────────
# 题 3：实现一个 3 层 MLP 的前向传播
# 结构：4 维输入 → 8 维隐藏 → 8 维隐藏 → 2 维输出
# ─────────────────────────────────────────────────────────────────
class MLP:
    def __init__(self, in_dim=4, hidden_dim=8, out_dim=2):
        # 用小随机数初始化（× 0.1 避免太大）
        self.W1 = np.random.randn(hidden_dim, in_dim)     * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * 0.1
        self.b2 = np.zeros(hidden_dim)
        self.W3 = np.random.randn(out_dim, hidden_dim)    * 0.1
        self.b3 = np.zeros(out_dim)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """TODO：实现 3 层前向传播：每层 Linear + ReLU（最后一层不加激活）"""
        # 你的代码
        pass


def test_mlp():
    mlp = MLP()
    x = np.random.randn(4)
    out = mlp.forward(x)
    print("== 题 3：MLP 前向 ==")
    print("input shape :", x.shape)        # (4,)
    print("output shape:", out.shape)      # (2,)
    print("output:", out)
    print()


# ─────────────────────────────────────────────────────────────────
# 题 4：实现 MSE 损失和交叉熵损失
# ─────────────────────────────────────────────────────────────────
def mse_loss(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """TODO：均方误差 = mean((y_pred - y_true)^2)"""
    # 你的代码
    pass


def cross_entropy(logits: np.ndarray, label: int) -> float:
    """
    TODO：交叉熵
    1. 对 logits 做 softmax 得到概率
    2. 取真实类别的概率
    3. 取对数取负

    Hint: 防溢出，先减最大值再 exp（数值稳定 softmax）
    """
    # 你的代码
    pass


def test_losses():
    print("== 题 4：损失函数 ==")
    # MSE
    pred = np.array([1.0, 2.0, 3.0])
    true = np.array([1.5, 2.5, 3.5])
    print("MSE:", mse_loss(pred, true))         # 期望: 0.25

    # 交叉熵
    logits = np.array([2.0, 1.0, 0.1])
    print("CE(label=0):", round(cross_entropy(logits, 0), 4))  # 期望: ~0.4170
    print("CE(label=2):", round(cross_entropy(logits, 2), 4))  # 期望: ~2.3170
    print()


# ─────────────────────────────────────────────────────────────────
# 题 5（重点）：用梯度下降训练 y = w*x + b 拟合数据
# 真实关系：y = 3x - 2，用噪声数据训练
# ─────────────────────────────────────────────────────────────────
def train_linear():
    """TODO：训练 y = w*x + b 拟合下列数据，跑 1000 步"""
    np.random.seed(0)
    xs = np.linspace(-3, 3, 50)
    ys = 3 * xs - 2 + np.random.randn(50) * 0.3  # 加噪声

    w, b = 0.0, 0.0
    lr = 0.05

    print("== 题 5：训练线性回归 ==")
    for step in range(1000):
        # TODO：
        # 1. 前向：y_pred = w * xs + b
        # 2. loss = mse(y_pred, ys)
        # 3. 手推梯度：
        #    dw = 2 * mean((y_pred - ys) * xs)
        #    db = 2 * mean(y_pred - ys)
        # 4. 更新：w -= lr * dw, b -= lr * db
        pass  # 删掉 pass，写你的代码

        if step % 200 == 0:
            print(f"step {step:4d}: w={w:.4f}, b={b:.4f}")

    print(f"最终：w ≈ {w:.4f}（真实 3.0），b ≈ {b:.4f}（真实 -2.0）")
    print()


# ─────────────────────────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_activations()
    test_neuron()
    test_mlp()
    test_losses()
    train_linear()
    print("✅ Day 1 练习完成。明天进 PyTorch！")
