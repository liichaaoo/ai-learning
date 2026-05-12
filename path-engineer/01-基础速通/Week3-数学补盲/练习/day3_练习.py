"""
Day 3 练习 · 概率与信息论（Softmax + 交叉熵）

运行：python day3_练习.py
"""

import numpy as np


# =============================================================================
# 题 1（手算）：Softmax
# =============================================================================
# 对 [1, 2, 3] 做 softmax：
#
# 步骤：
#   e^1 ≈ 2.718
#   e^2 ≈ 7.389
#   e^3 ≈ 20.086
#   总和 ≈ 30.193
#   概率 ≈ [2.718/30.193, 7.389/30.193, 20.086/30.193]
#
# TODO: 手算答案（保留 4 位小数）
# softmax([1, 2, 3]) ≈ [___, ___, ___]

def verify_q1():
    x = np.array([1.0, 2.0, 3.0])
    exp_x = np.exp(x)
    probs = exp_x / np.sum(exp_x)
    print(f"softmax([1,2,3]) = {probs}")
    print("标准答案: [0.0900, 0.2447, 0.6652]")


# =============================================================================
# 题 2（实现）：Softmax 的两个版本
# =============================================================================
# 实现基础版和数值稳定版

def softmax(x):
    """TODO: 基础版"""
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x)


def stable_softmax(x):
    """TODO: 数值稳定版（减去最大值）"""
    x_max = np.max(x)
    exp_x = np.exp(x - x_max)
    return exp_x / np.sum(exp_x)


def test_softmax_versions():
    # 正常输入：两个实现应该一样
    x = np.array([2.0, 1.0, 0.1])
    print(f"普通版: {softmax(x)}")
    print(f"稳定版: {stable_softmax(x)}")

    # 极端输入：普通版会 overflow，稳定版 OK
    x_large = np.array([1000.0, 999.0, 998.0])
    try:
        y = softmax(x_large)
        print(f"普通版(极端): {y}")
    except Exception as e:
        print(f"普通版(极端): 溢出")

    print(f"稳定版(极端): {stable_softmax(x_large)}")
    print()
    print("💡 工业界一律用稳定版")


# =============================================================================
# 题 3（实验）：Temperature 对分布的影响
# =============================================================================

def temperature_demo():
    logits = np.array([2.0, 1.5, 1.0, 0.5])

    for T in [0.1, 0.5, 1.0, 2.0, 5.0]:
        # TODO: 算一下 T 下的 softmax 概率
        probs = stable_softmax(logits / T)
        print(f"T = {T:.1f}: {probs.round(3)}")

    print()
    print("💡 观察：")
    print("  T 小 → 分布陡（几乎只选 top1）→ 输出确定")
    print("  T 大 → 分布平（各选项机会均等）→ 输出多样")
    print("  实践中 T=0 相当于贪心选 top1（argmax）")


# =============================================================================
# 题 4（实验）：Top-p 采样
# =============================================================================

def top_p_demo():
    probs = np.array([0.4, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02])

    for p in [0.5, 0.8, 0.95]:
        # 按概率降序排序（已经是了）
        sorted_probs = np.sort(probs)[::-1]
        cumsum = np.cumsum(sorted_probs)
        # 找到累加第一次超过 p 的位置
        k = np.searchsorted(cumsum, p) + 1
        print(f"top_p={p}: 只在前 {k} 个 token 里采样")
        print(f"           保留概率: {sorted_probs[:k].round(3)}")


# =============================================================================
# 题 5（核心）：交叉熵
# =============================================================================

def cross_entropy(probs: np.ndarray, true_class: int) -> float:
    """TODO: 实现交叉熵（加 1e-10 防 log(0)）"""
    return -np.log(probs[true_class] + 1e-10)


def cross_entropy_demo():
    probs = np.array([0.7, 0.2, 0.1])

    # 真实标签是 0（模型预测对了）
    loss_correct = cross_entropy(probs, 0)
    print(f"正确预测 (p=0.7): loss = {loss_correct:.4f}")

    # 真实标签是 1（模型不太准）
    loss_mid = cross_entropy(probs, 1)
    print(f"中等预测 (p=0.2): loss = {loss_mid:.4f}")

    # 真实标签是 2（模型完全错了）
    loss_wrong = cross_entropy(probs, 2)
    print(f"错误预测 (p=0.1): loss = {loss_wrong:.4f}")

    print()
    print("💡 结论：模型对正确答案的预测概率越低，loss 越大")


# =============================================================================
# 题 6（综合）：模拟一次 LLM 训练的 loss 计算
# =============================================================================
# 场景：模型对下一个 token 输出 logits，词表大小 = 5
# 真实的下一个 token index = 2

def llm_forward_demo():
    np.random.seed(42)
    vocab_size = 5
    true_token_id = 2

    # 模型最后一层输出的 logits
    logits = np.random.randn(vocab_size) * 2
    print(f"logits = {logits.round(3)}")

    # 1. softmax 变概率
    probs = stable_softmax(logits)
    print(f"probs  = {probs.round(3)}")
    print(f"预测的 top token: {np.argmax(probs)}")
    print(f"真实 token:      {true_token_id}")

    # 2. 算 loss
    loss = cross_entropy(probs, true_token_id)
    print(f"loss = {loss:.4f}")
    print()
    print("💡 整个 LLM 训练就是对无数个这样的 (logits, true_token) 求平均 loss")
    print("   然后反向传播调整参数（Day 4 讲）")


# =============================================================================
# 题 7（思考）：调 API 时遇到
# =============================================================================
# 同事告诉你某个接口要求代码生成尽量稳定，问你 temperature 该设多少？
# 又有一个创意写作场景，要求"不要总是一样的输出"，temperature 设多少？

# TODO: 你的回答
# - 代码生成: temperature =
# - 创意写作: temperature =


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 1 · Softmax 手算验证")
    print("=" * 60)
    verify_q1()

    print()
    print("=" * 60)
    print("题 2 · 两个版本的 softmax")
    print("=" * 60)
    test_softmax_versions()

    print()
    print("=" * 60)
    print("题 3 · Temperature 效果")
    print("=" * 60)
    temperature_demo()

    print()
    print("=" * 60)
    print("题 4 · Top-p 采样")
    print("=" * 60)
    top_p_demo()

    print()
    print("=" * 60)
    print("题 5 · 交叉熵")
    print("=" * 60)
    cross_entropy_demo()

    print()
    print("=" * 60)
    print("题 6 · 模拟 LLM 训练 loss")
    print("=" * 60)
    llm_forward_demo()

    print()
    print("✅ Day 3 练习完成。明天 Day 4：微积分与梯度（反向传播认知）")
