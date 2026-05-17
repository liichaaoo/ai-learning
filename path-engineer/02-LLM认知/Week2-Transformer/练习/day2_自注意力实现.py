"""
Day 2 练习 · Self-Attention（PyTorch 版 + 因果掩码）

目标：能默写出标准 Self-Attention 实现 + 加因果掩码 + 跟 PyTorch 内置 SDPA 对齐。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day2_自注意力实现.py
3. 跟 F.scaled_dot_product_attention 的输出对齐 → 说明实现正确

📖 对应教程：../Day2-SelfAttention公式.md
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)


# ─────────────────────────────────────────────────────────────────
# 题 1：实现单头 Self-Attention（带可选因果掩码）
# ─────────────────────────────────────────────────────────────────
class SelfAttention(nn.Module):
    def __init__(self, d_model: int, d_k: int, causal: bool = False):
        super().__init__()
        self.d_k = d_k
        self.causal = causal
        self.W_Q = nn.Linear(d_model, d_k, bias=False)
        self.W_K = nn.Linear(d_model, d_k, bias=False)
        self.W_V = nn.Linear(d_model, d_k, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        TODO：实现 forward。
        x: (B, L, d_model)
        返回: (B, L, d_k)

        步骤：
          1. Q = self.W_Q(x), K = self.W_K(x), V = self.W_V(x)   各 (B, L, d_k)
          2. scores = Q @ K.transpose(-2, -1)                     (B, L, L)
          3. scores = scores / sqrt(d_k)
          4. 如果 causal=True，加下三角掩码（mask 上三角 → -inf）
          5. attn = F.softmax(scores, dim=-1)
          6. out = attn @ V                                       (B, L, d_k)
        """
        # 你的代码
        pass


def test_self_attention():
    print("== 题 1：Self-Attention（无掩码）==")
    B, L, d_model = 2, 4, 8
    x = torch.randn(B, L, d_model)

    attn = SelfAttention(d_model=d_model, d_k=d_model, causal=False)
    y = attn(x)
    print(f"输入: {x.shape}, 输出: {y.shape}")
    assert y.shape == (B, L, d_model), "输出形状错了"
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 2：跟 PyTorch 内置 SDPA 对齐
# ─────────────────────────────────────────────────────────────────
def test_align_with_sdpa():
    """
    用相同的 W_Q/W_K/W_V，看自己写的 attention 跟 F.scaled_dot_product_attention
    输出是否一致（差异应该在 1e-5 以下）。
    """
    print("== 题 2：跟 PyTorch SDPA 对齐 ==")
    B, L, d = 2, 4, 8
    x = torch.randn(B, L, d)

    attn = SelfAttention(d_model=d, d_k=d, causal=False)
    y_mine = attn(x)

    # 用同一组 W 算 Q/K/V，直接调内置
    Q = attn.W_Q(x)
    K = attn.W_K(x)
    V = attn.W_V(x)
    y_torch = F.scaled_dot_product_attention(Q, K, V, is_causal=False)

    diff = (y_mine - y_torch).abs().max().item()
    print(f"最大差异: {diff:.2e}  (应该 < 1e-5)")
    assert diff < 1e-5, "实现有 bug！"
    print("✓ 跟 PyTorch SDPA 一致\n")


# ─────────────────────────────────────────────────────────────────
# 题 3：因果掩码 —— 验证"未来位置"的权重确实是 0
# ─────────────────────────────────────────────────────────────────
def test_causal_mask():
    print("== 题 3：因果掩码 ==")
    B, L, d = 1, 5, 4
    x = torch.randn(B, L, d)

    attn = SelfAttention(d_model=d, d_k=d, causal=True)

    # 提取出 attn weights 看一下
    Q = attn.W_Q(x)
    K = attn.W_K(x)
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d)
    mask = torch.tril(torch.ones(L, L)).bool()
    scores = scores.masked_fill(~mask, float('-inf'))
    weights = F.softmax(scores, dim=-1)

    print(f"注意力权重矩阵（应该是下三角，上三角全 0）:")
    print(weights[0].detach().numpy().round(3))

    # 验证上三角全是 0
    upper = weights[0] * (~mask).float()
    assert upper.sum().item() < 1e-6, "因果掩码没生效！"
    print("✓ 因果掩码生效（上三角全 0）\n")


# ─────────────────────────────────────────────────────────────────
# 题 4：手动算一个数字例子（参考教程 §4）
# Q = [[1,0],[0,1]], K = [[1,0],[1,1]], V = [[1,2],[3,4]]
# 期望输出 ≈ [[2.00, 3.00], [2.34, 3.34]]
# ─────────────────────────────────────────────────────────────────
def test_numeric_example():
    print("== 题 4：数字例子手算对账 ==")
    Q = torch.tensor([[1.0, 0.0], [0.0, 1.0]]).unsqueeze(0)   # (1, 2, 2)
    K = torch.tensor([[1.0, 0.0], [1.0, 1.0]]).unsqueeze(0)
    V = torch.tensor([[1.0, 2.0], [3.0, 4.0]]).unsqueeze(0)

    out = F.scaled_dot_product_attention(Q, K, V, is_causal=False)
    print(f"输出:\n{out.squeeze(0).numpy().round(3)}")
    print("教程预期：[[2.00, 3.00], [2.34, 3.34]]")
    print("(允许 ±0.02 的误差)\n")


if __name__ == "__main__":
    test_self_attention()
    test_align_with_sdpa()
    test_causal_mask()
    test_numeric_example()
    print("✅ 通关后，应该能不看代码默写出 SelfAttention 类")
