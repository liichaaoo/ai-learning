"""
Linear Regression Cost Function (线性回归成本函数)
==================================================

内容:
1. 线性回归的预测函数 (hypothesis)
2. 均方误差成本函数 (Mean Squared Error, MSE)
3. 梯度计算 (用于梯度下降)
4. 梯度下降训练
5. 解析解 (Normal Equation) —— 与梯度下降结果对比验证
6. 一个完整的训练 demo

数学公式:
    预测:
        ŷ = X @ w + b

    单样本损失 (平方误差):
        L(ŷ, y) = (1/2) * (ŷ - y)^2
        —— 系数 1/2 只是为了求导后约掉 2，写不写都行

    成本函数 (m 个样本平均):
        J(w, b) = (1 / (2m)) * Σ (ŷ_i - y_i)^2

    梯度:
        dJ/dw = (1/m) * Xᵀ @ (ŷ - y)
        dJ/db = (1/m) * Σ (ŷ - y)

    解析解 (Normal Equation, 含偏置时令 X̃ = [X | 1]):
        θ* = (X̃ᵀ X̃)^(-1) X̃ᵀ y

约定:
    X: shape (m, n)   —— m 个样本, n 个特征 (不含偏置)
    y: shape (m,)     —— 连续目标值（实数）
    w: shape (n,)     —— 权重
    b: scalar         —— 偏置

与逻辑回归的对照:
    线性回归: ŷ = Xw + b ；                 损失 = (1/2)(ŷ-y)²    —— 用于回归
    逻辑回归: ŷ = sigmoid(Xw + b) ；        损失 = 二分类交叉熵    —— 用于分类
    两者最终的梯度形式是一样的：    dJ/dw = (1/m) Xᵀ(ŷ - y)
    区别只在 ŷ 怎么算 + 损失函数选什么。
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# 1. 预测函数 (hypothesis)
# ---------------------------------------------------------------------------
def predict(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    """
    线性回归的预测函数: ŷ = X @ w + b

    Parameters
    ----------
    X : (m, n) 特征矩阵
    w : (n,)   权重
    b : float  偏置

    Returns
    -------
    y_hat : (m,) 预测值
    """
    # X @ w 得到 (m,)，再加上标量 b（NumPy 广播会自动加到每个元素上）
    return X @ w + b


# ---------------------------------------------------------------------------
# 2. 成本函数 (Mean Squared Error)
# ---------------------------------------------------------------------------
def compute_cost(
    X: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    b: float,
) -> float:
    """
    计算线性回归的成本（均方误差，带 1/2 系数）。

        J(w, b) = (1 / (2m)) * Σ (ŷ_i - y_i)^2

    系数 1/2 是为了让求导后 (ŷ - y)·2·(1/2) = (ŷ - y)，公式更整洁。
    去掉 1/2 也只是常数倍数差异，对最优解的位置没有影响。

    Parameters
    ----------
    X : (m, n) 特征矩阵
    y : (m,)   真实目标值
    w : (n,)   权重
    b : float  偏置

    Returns
    -------
    cost : float
    """
    # ① 样本数 m，用于取平均
    m = X.shape[0]

    # ② 预测值 ŷ，shape (m,)
    y_hat = predict(X, w, b)

    # ③ 残差 (residual) = 预测 - 真实
    residual = y_hat - y                 # (m,)

    # ④ MSE: 平方后求和，再除以 2m
    #    np.dot(residual, residual) 等价于 Σ residual_i^2，但比 (residual**2).sum() 略快
    cost = float(np.dot(residual, residual) / (2 * m))
    return cost


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

    推导（单样本）:
        L = (1/2)(ŷ - y)^2,  ŷ = w·x + b
        dL/dw_j = (ŷ - y) * x_j
        dL/db   = (ŷ - y)

    推到 m 个样本求平均:
        dJ/dw = (1/m) * Xᵀ @ (ŷ - y)
        dJ/db = (1/m) * Σ (ŷ - y)

    Returns
    -------
    dw : (n,)
    db : float
    """
    # ① 样本数，用于平均
    m = X.shape[0]

    # ② 预测 + 残差。注意线性回归的"误差"形式 (ŷ - y) 与逻辑回归一致
    y_hat = predict(X, w, b)
    error = y_hat - y                    # (m,)

    # ③ 对权重 w 的梯度: Xᵀ · error / m
    #    Xᵀ shape (n, m)，error shape (m,) -> 结果 (n,)
    dw = (X.T @ error) / m

    # ④ 对偏置 b 的梯度: error 求和取平均
    db = float(np.sum(error) / m)

    return dw, db


# ---------------------------------------------------------------------------
# 4. 梯度下降训练
# ---------------------------------------------------------------------------
def gradient_descent(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.01,
    num_iters: int = 1000,
    verbose: bool = True,
) -> tuple[np.ndarray, float, list[float]]:
    """
    用梯度下降训练线性回归。

    Returns
    -------
    w        : 训练后的权重
    b        : 训练后的偏置
    history  : 每次迭代的 cost
    """
    # ① 拿到样本数 m 和特征数 n
    m, n = X.shape

    # ② 参数初始化为 0
    #    线性回归的 MSE 成本也是凸函数，零初始化不会陷入局部最优
    w = np.zeros(n)
    b = 0.0

    # ③ 用列表记录每一步 cost，方便后面画 loss 曲线 / 调参
    history: list[float] = []

    # ④ 主循环：执行 num_iters 次梯度下降
    for i in range(num_iters):
        # 4.1 计算当前参数下的梯度
        dw, db = compute_gradient(X, y, w, b)

        # 4.2 沿负梯度方向更新参数: θ ← θ - lr · ∇J
        w -= lr * dw
        b -= lr * db

        # 4.3 记录更新后的 cost
        cost = compute_cost(X, y, w, b)
        history.append(cost)

        # 4.4 训练日志：每约 10% 进度打印一次，最后一轮也打印
        if verbose and (i % max(1, num_iters // 10) == 0 or i == num_iters - 1):
            print(f"iter {i:>5d} | cost = {cost:.6f}")

    return w, b, history


# ---------------------------------------------------------------------------
# 5. 解析解 (Normal Equation)
# ---------------------------------------------------------------------------
def normal_equation(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    """
    用解析解一次性求出最优 w, b：
        θ* = (X̃ᵀ X̃)^(-1) X̃ᵀ y
    其中 X̃ 是在 X 末尾拼接一列全 1，用于吸收偏置 b。

    适用条件:
        - 特征数 n 不太大（一般 n < 10000），否则求逆开销很大
        - X̃ᵀ X̃ 可逆（特征列线性无关）；不可逆时建议用伪逆 np.linalg.pinv
    """
    # ① 在 X 右侧加一列 1，构造增广矩阵 X̃，把 b 也吸收成权重的一部分
    m = X.shape[0]
    ones = np.ones((m, 1))
    X_aug = np.hstack([X, ones])         # (m, n+1)

    # ② 用 np.linalg.lstsq 求最小二乘解
    #    它在数值上比直接 (XᵀX)^-1 Xᵀy 更稳定（避免显式求逆）
    theta, *_ = np.linalg.lstsq(X_aug, y, rcond=None)   # (n+1,)

    # ③ 拆出 w 和 b
    w = theta[:-1]
    b = float(theta[-1])
    return w, b


# ---------------------------------------------------------------------------
# 6. Demo
# ---------------------------------------------------------------------------
def _demo() -> None:
    """构造一个带噪声的线性数据集，验证训练效果，并和解析解对比。"""
    # ① 固定随机种子，保证结果可复现
    rng = np.random.default_rng(42)

    # ② 设定真实参数 (作为"上帝视角"的 ground truth)
    #    我们想让模型学到的就是这组数
    true_w = np.array([2.0, -3.5])       # (n=2,)
    true_b = 4.0

    # ③ 生成样本特征 X：100 个样本，每个样本 2 个特征，均匀分布在 [-5, 5]
    m = 100
    X = rng.uniform(low=-5.0, high=5.0, size=(m, 2))

    # ④ 用真实参数生成标签 y，并加一点高斯噪声模拟真实数据
    noise = rng.normal(loc=0.0, scale=1.0, size=m)
    y = X @ true_w + true_b + noise

    # ⑤ 梯度下降求解
    print("=== 训练线性回归 (梯度下降) ===")
    w_gd, b_gd, _ = gradient_descent(X, y, lr=0.01, num_iters=2000, verbose=True)
    print(f"\n[GD]   学到 w = {w_gd}, b = {b_gd:.4f}")

    # ⑥ 解析解求解（同一份数据），与梯度下降结果对照
    w_ne, b_ne = normal_equation(X, y)
    print(f"[NE]   解析解 w = {w_ne}, b = {b_ne:.4f}")

    # ⑦ 对照真实参数（带噪声所以学到的不会完全等于真值，但应非常接近）
    print(f"[真值] w = {true_w}, b = {true_b:.4f}")

    # ⑧ 评估：在训练集上看看均方根误差 (RMSE)
    y_pred = predict(X, w_gd, b_gd)
    rmse = float(np.sqrt(np.mean((y_pred - y) ** 2)))
    print(f"\n训练集 RMSE (GD) = {rmse:.4f}")


if __name__ == "__main__":
    _demo()
