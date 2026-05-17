"""
Day 5 练习 · 三大流派对比 + 综合演练

目标：
1. 把 GPT 风格 Block 升级为 Llama 风格（替换 LayerNorm → RMSNorm，GELU → SwiGLU）
2. 对比两者参数量差异
3. 自检本周通关（默写 + 解释）

完成方式：
1. 把每个 TODO 填完
2. 运行：python day5_流派对比与综合.py

📖 对应教程：../Day5-三大流派对比.md
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)


# ─────────────────────────────────────────────────────────────────
# 题 1：实现 RMSNorm
# ─────────────────────────────────────────────────────────────────
class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))   # 可学习的 scale γ

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        TODO：实现 RMSNorm
            rms = sqrt(mean(x², dim=-1, keepdim=True) + eps)
            return self.weight * x / rms

        ⚠️ 跟 LayerNorm 的区别：不减均值！只除均方根。
        """
        # 你的代码
        pass


def test_rmsnorm():
    print("== 题 1：RMSNorm ==")
    rms = RMSNorm(dim=8)
    x = torch.randn(2, 4, 8) * 5
    y = rms(x)
    print(f"输入形状: {x.shape}, 输出形状: {y.shape}")
    # 检查归一化效果：每个位置的 rms 应该接近 1
    rms_value = y.pow(2).mean(dim=-1).sqrt()
    print(f"输出 RMS（应该全接近 1）:\n{rms_value.detach().numpy().round(3)}")
    print()


# ─────────────────────────────────────────────────────────────────
# 题 2：实现 SwiGLU FFN
# ─────────────────────────────────────────────────────────────────
class SwiGLU_FFN(nn.Module):
    """Llama 用的 FFN，把 GELU 换成 SiLU(gate) * up 的门控形式"""
    def __init__(self, d_model: int, d_ff: int = None):
        super().__init__()
        # 为了让总参数 ≈ 标准 FFN，d_ff 通常调小到 2/3 · 4 · d_model
        d_ff = d_ff or int(2 / 3 * 4 * d_model)
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.up_proj = nn.Linear(d_model, d_ff, bias=False)
        self.down_proj = nn.Linear(d_ff, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        TODO：实现 SwiGLU
            return self.down_proj( F.silu(self.gate_proj(x)) * self.up_proj(x) )
        """
        # 你的代码
        pass


def test_swiglu():
    print("== 题 2：SwiGLU FFN ==")
    ffn = SwiGLU_FFN(d_model=64)
    x = torch.randn(2, 4, 64)
    y = ffn(x)
    print(f"输入: {x.shape}, 输出: {y.shape}")
    assert y.shape == x.shape
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 3：把 GPT Block 升级成 Llama Block
# ─────────────────────────────────────────────────────────────────
class MultiHeadAttention(nn.Module):
    """Day 3 的 MHA（直接复用）"""
    def __init__(self, d_model, n_heads, causal=False):
        super().__init__()
        self.d_model, self.n_heads, self.d_k = d_model, n_heads, d_model // n_heads
        self.causal = causal
        self.W_qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.W_O = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):
        B, L, D = x.shape
        qkv = self.W_qkv(x).view(B, L, 3, self.n_heads, self.d_k).permute(2, 0, 3, 1, 4)
        Q, K, V = qkv[0], qkv[1], qkv[2]
        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.d_k)
        if self.causal:
            mask = torch.tril(torch.ones(L, L, device=x.device)).bool()
            scores = scores.masked_fill(~mask, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        out = (attn @ V).transpose(1, 2).contiguous().view(B, L, D)
        return self.W_O(out)


class GPTBlock(nn.Module):
    """GPT 风格：LayerNorm + GELU FFN"""
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads, causal=True)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model),
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class LlamaBlock(nn.Module):
    """Llama 风格：RMSNorm + SwiGLU FFN（暂不加 RoPE，本周认知层）"""
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        # TODO：实现
        # norm1, norm2 用 RMSNorm
        # attn 跟 GPT 一样
        # ffn 用 SwiGLU_FFN
        # 你的代码
        pass

    def forward(self, x):
        """同 GPT Block：Pre-LN + 残差"""
        # TODO：你的代码
        pass


def test_llama_block():
    print("== 题 3：LlamaBlock ==")
    block = LlamaBlock(d_model=64, n_heads=4)
    x = torch.randn(2, 10, 64)
    y = block(x)
    print(f"输入: {x.shape}, 输出: {y.shape}")
    assert y.shape == x.shape
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 4：参数量对比 GPT vs Llama
# ─────────────────────────────────────────────────────────────────
def compare_params():
    print("== 题 4：参数量对比 ==")
    gpt = GPTBlock(d_model=64, n_heads=4)
    llama = LlamaBlock(d_model=64, n_heads=4)

    p_gpt = sum(p.numel() for p in gpt.parameters())
    p_llama = sum(p.numel() for p in llama.parameters())

    print(f"GPT Block 参数:    {p_gpt:,}")
    print(f"Llama Block 参数:  {p_llama:,}")
    print(f"差异比例: {(p_llama - p_gpt) / p_gpt * 100:+.1f}%")
    print("(SwiGLU 多一条 gate 路径，但 d_ff 调小到 2/3·4d，所以总量接近)\n")


# ─────────────────────────────────────────────────────────────────
# 题 5：终极自测——把答案写在注释里，对照教程检查
# ─────────────────────────────────────────────────────────────────
SELF_TEST = """
请用 1-2 句话回答以下问题，写完跟教程对照：

1. BERT / GPT / Llama 各自是什么结构（Encoder / Decoder）？
   答：

2. BERT 的训练目标是什么？GPT 的训练目标是什么？
   答：

3. 为什么 Self-Attention 要除以 √d_k？
   答：

4. Multi-Head 的好处是什么？为什么不直接加宽 d_model？
   答：

5. 因果掩码在干什么？谁用谁不用？
   答：

6. Llama 现代化三件套是哪三个？各自解决什么问题？
   答：

7. RAG 检索时常用的 Embedding 模型，背后是哪一类架构？
   答：（提示：句向量类）
"""


if __name__ == "__main__":
    test_rmsnorm()
    test_swiglu()
    test_llama_block()
    compare_params()
    print(SELF_TEST)
    print("✅ Week 2 通关！下周开始用 HuggingFace 玩真模型")
