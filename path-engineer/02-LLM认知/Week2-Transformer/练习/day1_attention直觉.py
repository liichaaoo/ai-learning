"""
Day 1 练习 · Attention 直觉（NumPy 版）

目标：用 NumPy 把 Attention 的"直觉部分"过一遍——形状变化 + softmax 权重含义。
不引入 PyTorch（明天才用）。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day1_attention直觉.py
3. 输出符合预期就算 OK

📖 对应教程：../Day1-Attention直观理解.md
"""
import numpy as np

np.random.seed(42)


# ─────────────────────────────────────────────────────────────────
# 题 1：实现 softmax（数值稳定版）
# ─────────────────────────────────────────────────────────────────
def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    TODO：实现按指定 axis 做 softmax。
    提示：为了数值稳定，先减去最大值再 exp。
        e_x = exp(x - x.max(axis, keepdims=True))
        return e_x / e_x.sum(axis, keepdims=True)
    """
    # 你的代码
    pass


def test_softmax():
    print("== 题 1：softmax ==")
    x = np.array([[1.0, 2.0, 3.0],
                  [3.0, 2.0, 1.0]])
    s = softmax(x, axis=-1)
    print("softmax 结果:\n", np.round(s, 4))
    print("每行和:", s.sum(axis=-1))   # 期望: [1. 1.]
    print()


# ─────────────────────────────────────────────────────────────────
# 题 2：实现一个最简 Self-Attention（无掩码）
# 输入: x (L, d) —— L 个 token，每个 d 维
# 输出: out (L, d) —— 每个 token 的"上下文增强表示"
# ─────────────────────────────────────────────────────────────────
def self_attention(x: np.ndarray, W_Q: np.ndarray,
                   W_K: np.ndarray, W_V: np.ndarray) -> tuple:
    """
    TODO：实现 Attention(Q, K, V) = softmax(QK^T / √d_k) · V
    步骤：
      1. Q = x @ W_Q,  K = x @ W_K,  V = x @ W_V
      2. scores = Q @ K.T / sqrt(d_k)
      3. attn = softmax(scores, axis=-1)
      4. out = attn @ V
    返回 (out, attn) 两个数组
    """
    # 你的代码
    pass


def test_self_attention():
    print("== 题 2：Self-Attention ==")
    L, d = 4, 8
    x = np.random.randn(L, d)
    W_Q = np.random.randn(d, d) * 0.1
    W_K = np.random.randn(d, d) * 0.1
    W_V = np.random.randn(d, d) * 0.1

    out, attn = self_attention(x, W_Q, W_K, W_V)
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {out.shape}    (应该跟输入一样: {x.shape})")
    print(f"attn 形状: {attn.shape}   (应该是 (L, L) = ({L}, {L}))")
    print(f"attn 每行和: {attn.sum(axis=-1)}   (应该全是 1)")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 3：观察 attn 矩阵——构造一个"明显应该看回去"的例子
# 让一个 token 的输入向量和另一个特定 token 高度相似，
# 看 attn 权重是否如预期高
# ─────────────────────────────────────────────────────────────────
def test_attention_pattern():
    print("== 题 3：观察 attn 模式 ==")

    # 构造 4 个 token，让 token 3 的方向跟 token 0 非常接近
    L, d = 4, 8
    x = np.random.randn(L, d)
    x[3] = x[0] + np.random.randn(d) * 0.05   # token 3 ≈ token 0

    # 用恒等矩阵（不投影），直接把 x 当 Q/K/V
    W_Q = np.eye(d)
    W_K = np.eye(d)
    W_V = np.eye(d)

    out, attn = self_attention(x, W_Q, W_K, W_V)
    print(f"attn 矩阵（每行加起来=1）:\n{np.round(attn, 3)}")
    print(f"\n观察：第 3 行的列 0（token 3 看 token 0）的权重: {attn[3, 0]:.3f}")
    print("应该比第 3 行其他位置（除了它自己）的权重明显更高！")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 4（思考题，写在注释里）：
# 1. 为什么 softmax 要 axis=-1，不能 axis=0？
# 2. 假设序列长度从 4 变成 1024，attn 矩阵的形状是？内存占用如何变化？
#    （提示：O(L²) —— 这就是为什么 LLM 长 context 这么贵）
# ─────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    test_softmax()
    test_self_attention()
    test_attention_pattern()
    print("✅ 全部跑通后，再回去看 Day1 §3 的图书馆类比，会有"对上了"的感觉")
