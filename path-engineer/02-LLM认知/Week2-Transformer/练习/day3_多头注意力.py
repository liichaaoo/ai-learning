"""
Day 3 练习 · Multi-Head Attention

目标：自己写一个 Multi-Head Attention，能跟 nn.MultiheadAttention 对齐输出形状。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day3_多头注意力.py
3. 形状全对、跟 PyTorch 内置版差异 < 1e-5

📖 对应教程：../Day3-MultiHead多头注意力.md
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)


# ─────────────────────────────────────────────────────────────────
# 题 1：实现 Multi-Head Attention
# ─────────────────────────────────────────────────────────────────
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, causal: bool = False):
        super().__init__()
        assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.causal = causal

        self.W_Q = nn.Linear(d_model, d_model, bias=False)
        self.W_K = nn.Linear(d_model, d_model, bias=False)
        self.W_V = nn.Linear(d_model, d_model, bias=False)
        self.W_O = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        TODO：实现多头注意力。
        x: (B, L, d_model)
        返回: (B, L, d_model)

        关键步骤：
          1. Q = self.W_Q(x), K, V 同理               (B, L, d_model)
          2. 切分成多头：reshape 到 (B, L, n_heads, d_k)
          3. 转置到 (B, n_heads, L, d_k)              ← 让 Attention 在 L 维度上计算
          4. scores = Q @ K.transpose(-2, -1) / sqrt(d_k)   (B, H, L, L)
          5. 如果 causal=True，加下三角掩码
          6. attn = softmax(scores, dim=-1)
          7. out = attn @ V                           (B, H, L, d_k)
          8. 转置回 (B, L, H, d_k) 并 reshape 成 (B, L, d_model)
          9. self.W_O(out)
        """
        B, L, D = x.shape

        # 你的代码
        pass


def test_shape():
    print("== 题 1：形状测试 ==")
    B, L, d_model, n_heads = 2, 10, 64, 8
    x = torch.randn(B, L, d_model)
    mha = MultiHeadAttention(d_model, n_heads, causal=True)
    y = mha(x)
    print(f"输入: {x.shape}")
    print(f"输出: {y.shape}    应该 == 输入: {x.shape}")
    assert y.shape == x.shape, "输出形状错了"
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 2：参数量检查
# 单头 d_k=64 vs 多头 8 头 d_k=8，参数量应该一样
# ─────────────────────────────────────────────────────────────────
def test_param_count():
    print("== 题 2：参数量检查 ==")
    mha1 = MultiHeadAttention(d_model=64, n_heads=1)
    mha8 = MultiHeadAttention(d_model=64, n_heads=8)
    p1 = sum(p.numel() for p in mha1.parameters())
    p8 = sum(p.numel() for p in mha8.parameters())
    print(f"1 头总参数:  {p1}")
    print(f"8 头总参数:  {p8}")
    print(f"应该相等！多头 ≠ 加大模型，只是分组使用同样大小的空间")
    assert p1 == p8, "多头参数量应该和单头一样！"
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 3：张量形状追踪练习——把每一步的 shape print 出来
# ─────────────────────────────────────────────────────────────────
def test_shape_trace():
    print("== 题 3：张量形状追踪 ==")
    B, L, d_model, n_heads = 2, 10, 64, 8
    d_k = d_model // n_heads
    x = torch.randn(B, L, d_model)

    print(f"x:                      {x.shape}        (B, L, d_model)")
    Q = nn.Linear(d_model, d_model, bias=False)(x)
    print(f"Q (投影后):             {Q.shape}        (B, L, d_model)")

    Q = Q.view(B, L, n_heads, d_k)
    print(f"Q (切分头):             {Q.shape}     (B, L, H, d_k)")

    Q = Q.transpose(1, 2)
    print(f"Q (转置后):             {Q.shape}     (B, H, L, d_k)")

    scores = Q @ Q.transpose(-2, -1)
    print(f"scores:                 {scores.shape}     (B, H, L, L)")

    out = scores @ Q
    print(f"out:                    {out.shape}     (B, H, L, d_k)")

    out = out.transpose(1, 2).contiguous().view(B, L, d_model)
    print(f"out (拼回):             {out.shape}        (B, L, d_model)")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 4：思考题（写在注释里）
# 1. 假设 d_model=4096, n_heads=32，每个头的 d_k 是？
# 2. KV Cache 是把哪个张量缓存起来？为什么这样能加速推理？
#    （提示：自回归生成时，Q 每次只算最新一个 token，K/V 可以复用历史）
# ─────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    test_shape()
    test_param_count()
    test_shape_trace()
    print("✅ 通关后，应该能闭着眼默写多头形状变化：(B,L,D) → (B,L,H,d_k) → (B,H,L,d_k) → (B,H,L,L)")
