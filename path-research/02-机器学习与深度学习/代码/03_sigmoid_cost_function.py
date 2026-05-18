"""
Sigmoid Cost Function (逻辑回归成本函数)
=========================================

内容:
1. sigmoid 激活函数（数值稳定版本，避免 exp 溢出）
2. 二分类交叉熵成本函数 (Binary Cross-Entropy / Log Loss)
3. 梯度计算 (用于梯度下降)
4. 一个完整的训练 demo

数学公式:
    z       = X @ w + b
    a = ŷ   = sigmoid(z) = 1 / (1 + exp(-z))

    单样本损失:
        L(ŷ, y) = -[ y·log(ŷ) + (1-y)·log(1-ŷ) ]

    成本函数 (m 个样本平均):
        J(w, b) = (1/m) * Σ L(ŷ_i, y_i)

    梯度:
        dJ/dw = (1/m) * Xᵀ @ (ŷ - y)
        dJ/db = (1/m) * Σ (ŷ - y)

约定:
    X: shape (m, n)   —— m 个样本, n 个特征 (不含偏置)
    y: shape (m,)     —— 标签, 取值 {0, 1}
    w: shape (n,)     —— 权重
    b: scalar         —— 偏置
"""

from typing import Any


import numpy as np


# ---------------------------------------------------------------------------
# 1. Sigmoid (数值稳定版本)
# ---------------------------------------------------------------------------
def sigmoid(z: np.ndarray) -> np.ndarray:
    """
    数值稳定的 sigmoid 实现。

    朴素写法 1 / (1 + exp(-z)) 在 z 是很大负数时，exp(-z) 会变成超大数导致 overflow；
    在 z 是很大正数时， exp(z) 也会 overflow。
    解决思路：根据 z 的正负，选择不会溢出的等价数学形式分别计算。

        z >= 0:  sigmoid(z) = 1 / (1 + exp(-z))      —— 此时 exp(-z) ∈ (0, 1]，安全
        z <  0:  sigmoid(z) = exp(z) / (1 + exp(z))  —— 此时 exp(z)  ∈ (0, 1)，安全
    """
    # ① 统一转成 float64 的 ndarray，方便后续做向量化运算
    z = np.asarray(z, dtype=np.float64)
    # ② 预先分配一个和 z 形状一样的输出数组，稍后按掩码填值
    out = np.empty_like(z)

    # ③ 构造布尔掩码：把 z 拆成 "非负部分" 和 "负数部分" 两组
    pos_mask = z >= 0      # True 的位置表示 z >= 0
    neg_mask = ~pos_mask   # 取反，True 的位置表示 z < 0

    # ④ 对 z >= 0 的元素：用 1 / (1 + exp(-z)) 公式计算
    #    -z 是非正数，exp(-z) ∈ (0, 1]，不会溢出
    out[pos_mask] = 1.0 / (1.0 + np.exp(-z[pos_mask]))

    # ⑤ 对 z < 0 的元素：用 exp(z) / (1 + exp(z)) 等价形式计算
    #    z 是负数，exp(z) ∈ (0, 1)，同样不会溢出
    exp_z = np.exp(z[neg_mask])
    out[neg_mask] = exp_z / (1.0 + exp_z)

    # ⑥ 返回最终的概率值，元素范围在 (0, 1)
    return out


# ---------------------------------------------------------------------------
# 2. 成本函数 (Binary Cross-Entropy)
# ---------------------------------------------------------------------------
def compute_cost(
    X: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    b: float,
    eps: float = 1e-15,
) -> float:
    """
    计算逻辑回归的成本（平均交叉熵损失）。

    Parameters
    ----------
    X : (m, n) 特征矩阵
    y : (m,)   标签 {0, 1}
    w : (n,)   权重
    b : float  偏置
    eps: 防止 log(0) 的小常数

    Returns
    -------
    cost : float
    """
    # ① 样本数 m，用于后面对总损失做平均
    m = X.shape[0]

    # ② 前向传播第一步：计算线性组合 z = X·w + b
    #    X: (m, n), w: (n,) -> 矩阵乘后是 (m,)，再加上标量 b（广播）
    z: Any = X @ w + b

    # ③ 前向传播第二步：把 z 通过 sigmoid 映射成 (0,1) 的概率 a = ŷ
    a = sigmoid(z)

    # ④ 数值保护：把 a 限制在 [eps, 1-eps]
    #    否则 a=0 时 log(a) = -inf，a=1 时 log(1-a) = -inf，会得到 NaN
    a = np.clip(a, eps, 1.0 - eps)

    # ⑤ 二分类交叉熵：
    #    单样本: L = -[ y·log(a) + (1-y)·log(1-a) ]
    #      - 当 y=1 时只剩 -log(a)：a 越接近 1，损失越小
    #      - 当 y=0 时只剩 -log(1-a)：a 越接近 0，损失越小
    #    np.mean 对 m 个样本求均值，得到整体成本 J
    cost = -np.mean(y * np.log(a) + (1.0 - y) * np.log(1.0 - a))

    # ⑥ 转成 Python float 返回（np.float64 → float），方便打印和比较
    return float(cost)


# ---------------------------------------------------------------------------
# 3. 梯度
# ---------------------------------------------------------------------------
def compute_gradient(
    X: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    b: float,
) -> tuple[np.ndarray, float]:
    """
    计算成本函数对 w, b 的梯度。

    Returns
    -------
    dw : (n,)
    db : float
    """
    # ① 样本数，用来做平均
    m = X.shape[0]

    # ② 前向传播：算出当前参数下每个样本的预测概率 a = sigmoid(X·w + b)
    a = sigmoid(X @ w + b)

    # ③ 误差向量 (m,)：预测概率 - 真实标签
    #    对交叉熵 + sigmoid 这一对组合，求导后得到的形式正好就是 (a - y)
    #    （这是逻辑回归梯度公式中最关键的化简结果）
    error = a - y                       # (m,)

    # ④ 对权重 w 的梯度：dJ/dw = (1/m) * Xᵀ · (a - y)
    #    Xᵀ: (n, m)，error: (m,) -> 结果是 (n,)，正好对应 n 个权重
    dw = (X.T @ error) / m              # (n,)

    # ⑤ 对偏置 b 的梯度：dJ/db = (1/m) * Σ (a - y)
    #    把误差求和再平均即可（因为 b 对每个样本的贡献都是 1）
    db = float(np.sum(error) / m)

    # ⑥ 返回梯度，供外层做参数更新使用
    return dw, db


# ---------------------------------------------------------------------------
# 4. 梯度下降训练
# ---------------------------------------------------------------------------
def gradient_descent(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.1,
    num_iters: int = 1000,
    verbose: bool = True,
) -> tuple[np.ndarray, float, list[float]]:
    """
    用梯度下降训练逻辑回归。

    Returns
    -------
    w        : 训练后的权重
    b        : 训练后的偏置
    history  : 每次迭代的 cost
    """
    # ① 拿到样本数 m 和特征数 n（m 这里没直接用到，但常见地保留以便扩展）
    m, n = X.shape

    # ② 参数初始化：w 全 0，b 为 0
    #    逻辑回归的损失函数是凸的，零初始化是 OK 的（神经网络中则不行）
    w = np.zeros(n)
    b = 0.0

    # ③ 用一个列表保存每一步的 cost，方便后续画 loss 曲线
    history: list[float] = []

    # ④ 主循环：执行 num_iters 次梯度下降
    for i in range(num_iters):
        # 4.1 计算当前参数下的梯度
        dw, db = compute_gradient(X, y, w, b)

        # 4.2 沿着负梯度方向更新参数：θ ← θ - lr · ∇J(θ)
        #     lr (learning rate) 控制每一步走多远
        w -= lr * dw
        b -= lr * db

        # 4.3 用更新后的参数重新计算 cost，记录到 history
        cost = compute_cost(X, y, w, b)
        history.append(cost)

        # 4.4 训练日志：大约每 10% 进度打印一次，最后一轮也打印
        if verbose and (i % max(1, num_iters // 10) == 0 or i == num_iters - 1):
            print(f"iter {i:>5d} | cost = {cost:.6f}")

    # ⑤ 返回最终参数 + cost 历史
    return w, b, history


# ---------------------------------------------------------------------------
# 5. Demo
# ---------------------------------------------------------------------------
def _demo() -> None:
    """构造一个简单的二分类数据集，验证训练效果。"""
    # ① 创建一个固定种子的随机数生成器，保证每次运行结果一致，方便复现
    rng = np.random.default_rng(42)

    # ② 构造两类二维高斯样本：
    #    - 类 0：均值 (-2, -2)，标准差 1
    #    - 类 1：均值 (+2, +2)，标准差 1
    #    两类在二维平面上线性可分，非常适合验证逻辑回归
    n_per_class = 100
    X0 = rng.normal(loc=-2.0, scale=1.0, size=(n_per_class, 2))
    X1 = rng.normal(loc=+2.0, scale=1.0, size=(n_per_class, 2))

    # ③ 把两类样本拼到一起，并构造对应标签 y ∈ {0, 1}
    X = np.vstack([X0, X1])                                  # (200, 2)
    y = np.hstack([np.zeros(n_per_class), np.ones(n_per_class)])  # (200,)

    # ④ 打乱样本顺序，避免训练时前 100 个全是类 0、后 100 个全是类 1
    #    （对全批量梯度下降影响不大，但是好习惯，对小批量/在线训练很重要）
    idx = rng.permutation(len(y))
    X, y = X[idx], y[idx]

    # ⑤ 调用梯度下降进行训练
    print("=== 训练逻辑回归 ===")
    w, b, _ = gradient_descent(X, y, lr=0.1, num_iters=500, verbose=True)
    print(f"\n学到的参数: w = {w}, b = {b:.4f}")

    # ⑥ 评估：在训练集上做预测
    #    - 先算概率 a = sigmoid(Xw + b)
    #    - 以 0.5 为阈值进行分类：a >= 0.5 -> 1，否则 0
    #    - 与真实标签比较得到准确率
    pred = (sigmoid(X @ w + b) >= 0.5).astype(int)
    acc = float(np.mean(pred == y))
    print(f"训练集准确率: {acc:.4f}")


if __name__ == "__main__":
    _demo()
