"""
Day 4 练习 · Transformer Block + TinyGPT

目标：把 Day 3 的 MHA 装进完整的 Transformer Block，再堆出一个能跑的 TinyGPT。
不训练（只验证前向传播形状正确）。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day4_transformer_block.py
3. logits 形状对、参数量在合理范围 → OK

📖 对应教程：../Day4-Transformer完整架构.md
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)


# ─────────────────────────────────────────────────────────────────
# Day 3 实现的多头注意力（这里直接给一份正确版，你专心做 Block）
# ─────────────────────────────────────────────────────────────────
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, causal=False):
        super().__init__()
        assert d_model % n_heads == 0
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


# ─────────────────────────────────────────────────────────────────
# 题 1：实现一个 Pre-LN 的 Transformer Block
# ─────────────────────────────────────────────────────────────────
class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_ff: int = None):
        super().__init__()
        d_ff = d_ff or 4 * d_model

        # TODO：定义 ln1, attn, ln2, ffn
        # ln1, ln2: nn.LayerNorm(d_model)
        # attn: MultiHeadAttention(d_model, n_heads, causal=True)
        # ffn: 两层 Linear + GELU 中间
        # 你的代码
        pass

    def forward(self, x):
        """
        TODO：实现 Pre-LN 风格的 forward
            x = x + self.attn(self.ln1(x))
            x = x + self.ffn(self.ln2(x))
            return x
        """
        # 你的代码
        pass


def test_block():
    print("== 题 1：Transformer Block ==")
    block = TransformerBlock(d_model=64, n_heads=4)
    x = torch.randn(2, 10, 64)
    y = block(x)
    print(f"输入: {x.shape}, 输出: {y.shape}")
    assert y.shape == x.shape, "Block 输出形状错了"
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 2：堆 N 个 Block 拼成 TinyGPT
# ─────────────────────────────────────────────────────────────────
class TinyGPT(nn.Module):
    def __init__(self, vocab_size, d_model=128, n_heads=4, n_layers=4, max_len=256):
        super().__init__()
        # TODO：定义所有组件
        # tok_emb: nn.Embedding(vocab_size, d_model)
        # pos_emb: nn.Embedding(max_len, d_model)
        # blocks: nn.ModuleList of n_layers TransformerBlock
        # ln_f:   final LayerNorm
        # head:   nn.Linear(d_model, vocab_size, bias=False)
        # 你的代码
        pass

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        """
        TODO：实现前向传播
        idx: (B, L) 整数 token id
        返回: (B, L, vocab_size) logits

        步骤：
          1. pos = torch.arange(L, device=idx.device)
          2. x = self.tok_emb(idx) + self.pos_emb(pos)
          3. for block in self.blocks: x = block(x)
          4. x = self.ln_f(x)
          5. return self.head(x)
        """
        # 你的代码
        pass


def test_tiny_gpt():
    print("== 题 2：TinyGPT ==")
    vocab_size = 1000
    model = TinyGPT(vocab_size, d_model=64, n_heads=4, n_layers=2)

    idx = torch.randint(0, vocab_size, (2, 10))
    logits = model(idx)
    print(f"输入: {idx.shape}")
    print(f"logits: {logits.shape}    应该是 (2, 10, {vocab_size})")
    assert logits.shape == (2, 10, vocab_size), "logits 形状错了"

    n_params = sum(p.numel() for p in model.parameters())
    print(f"总参数量: {n_params:,}")
    print("✓ 通过\n")


# ─────────────────────────────────────────────────────────────────
# 题 3：玩一下 —— 用未训练的 TinyGPT 做"伪生成"
# 看看自回归是怎么工作的（输出会是乱码，因为没训练）
# ─────────────────────────────────────────────────────────────────
@torch.no_grad()
def sample_demo():
    print("== 题 3：自回归生成（未训练，输出是乱码也正常）==")
    vocab_size = 100
    model = TinyGPT(vocab_size, d_model=64, n_heads=4, n_layers=2)
    model.eval()

    prompt = torch.tensor([[1, 2, 3]])      # (1, 3)
    print(f"起始 prompt: {prompt.tolist()}")

    for _ in range(5):
        logits = model(prompt)              # (1, L, vocab)
        last_logits = logits[:, -1, :]      # 只取最后一个位置
        # 简单贪婪采样
        next_token = last_logits.argmax(dim=-1, keepdim=True)
        prompt = torch.cat([prompt, next_token], dim=1)

    print(f"生成 5 步后: {prompt.tolist()}")
    print("(这就是 GPT 自回归生成的核心循环——Week 3 会加 Temperature/Top-p 等采样)\n")


if __name__ == "__main__":
    test_block()
    test_tiny_gpt()
    sample_demo()
    print("✅ 通关：你已经亲手搭出了一个完整的 GPT 架构")
