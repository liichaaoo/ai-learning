"""
Day 5 综合实战 · Mini-RAG + Mini-Attention

运行：python day5_综合实战.py

这是 Week 3 的毕业项目。你会把前 4 天学的数学全部串起来。
"""

import numpy as np


# =============================================================================
# Part 1: Mini-RAG 检索系统
# =============================================================================

def fake_embed(text: str, dim: int = 32) -> np.ndarray:
    """
    用字符频率做伪 embedding（真实场景用 bge-m3 等模型）。
    归一化到长度=1，让 cosine 相似度简化为点积。
    """
    vec = np.zeros(dim)
    for ch in text:
        vec[ord(ch) % dim] += 1
    norm = np.linalg.norm(vec)
    return vec / (norm + 1e-8)


def cosine_similarity(a, b):
    # 因为 a 和 b 都归一化过，cosine 相似度 = 点积
    return float(np.dot(a, b))


def mini_rag_demo():
    # 知识库
    docs = [
        "苹果公司发布了 iPhone 17，性能大幅提升",
        "Tim Cook 主持苹果公司 Q3 财报会议",
        "华为发布鸿蒙 5.0 操作系统",
        "AI 大模型训练需要大量 GPU 算力",
        "OpenAI 推出 GPT-5 模型",
        "苹果公司股价在财报后大幅上涨",
        "梨子在秋天成熟，含维生素 C",
        "深度学习在图像识别领域取得突破",
    ]

    # 建索引（预处理把所有文档向量化）
    doc_vecs = np.array([fake_embed(doc) for doc in docs])
    print(f"doc_vecs.shape = {doc_vecs.shape}\n")

    # 测试多个 query
    queries = [
        "苹果公司的最新产品动态",
        "大语言模型技术进展",
        "秋天水果",
    ]

    for query in queries:
        q_vec = fake_embed(query)

        # TODO: 用 cosine_similarity 算每个 doc 的分数（可以用 numpy 向量化加速）
        # scores = ???
        scores = doc_vecs @ q_vec   # 批量点积，因为已经归一化

        # 取 Top-3
        top_k_idx = np.argsort(scores)[-3:][::-1]

        print(f"Query: {query}")
        for rank, idx in enumerate(top_k_idx, 1):
            print(f"  Top {rank} [{scores[idx]:.4f}]: {docs[idx]}")
        print()

    print("💡 这就是 RAG 检索的最简版。把 fake_embed 换成真的 embedding 模型，")
    print("   把暴力比较换成向量库（Milvus/FAISS），就是生产系统。")


# =============================================================================
# Part 2: Mini-Attention
# =============================================================================

def stable_softmax(x, axis=-1):
    x_max = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - x_max)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V):
    """
    Transformer 的核心公式: softmax(QK^T / sqrt(d_k)) V

    Q, K, V: shape = (seq_len, d_k)

    返回:
      output:  (seq_len, d_k)
      weights: (seq_len, seq_len)  - 每行是注意力权重分布
    """
    d_k = Q.shape[-1]

    # TODO: 按公式实现 4 个步骤

    # Step 1: 点积得到 scores
    scores = Q @ K.T

    # Step 2: 缩放
    scores = scores / np.sqrt(d_k)

    # Step 3: softmax（按行做）
    weights = stable_softmax(scores, axis=-1)

    # Step 4: 加权 V
    output = weights @ V

    return output, weights


def mini_attention_demo():
    np.random.seed(42)
    seq_len = 4    # 4 个 token
    d_k = 8

    Q = np.random.randn(seq_len, d_k)
    K = np.random.randn(seq_len, d_k)
    V = np.random.randn(seq_len, d_k)

    output, weights = scaled_dot_product_attention(Q, K, V)

    print(f"Q/K/V shape:  {Q.shape}")
    print(f"output shape: {output.shape}   # 应该是 (4, 8)")
    print(f"weights shape: {weights.shape} # 应该是 (4, 4)")
    print()
    print(f"weights = \n{weights.round(3)}")
    print()

    # 验证每行和为 1
    print(f"每行和 = {weights.sum(axis=-1).round(3)}   (应该都是 1.0)")
    print()
    print("💡 weights[i, j] 表示第 i 个 token 对第 j 个 token 的关注度")
    print("   这个矩阵就是 Transformer 的'可解释性'起点")


# =============================================================================
# Part 3: 观察 attention 的规律（启发式理解）
# =============================================================================

def attention_with_meaning():
    """
    构造 Q 和 K 让它们有相似度关系，看 Attention 学到了什么
    """
    # 4 个 token 假装代表 ["苹果", "公司", "水果", "发布"]
    # 手工设计向量：苹果和公司关系近，苹果和水果关系近
    vectors = np.array([
        [1.0, 1.0, 0.0, 0.0],   # 苹果: 公司方向 + 水果方向
        [1.0, 0.0, 0.0, 0.0],   # 公司: 只有公司方向
        [0.0, 1.0, 0.0, 0.0],   # 水果: 只有水果方向
        [0.0, 0.0, 1.0, 0.0],   # 发布: 独立方向
    ])

    Q = K = V = vectors   # 简化：Q=K=V

    output, weights = scaled_dot_product_attention(Q, K, V)

    tokens = ["苹果", "公司", "水果", "发布"]
    print("Attention weights:")
    print(f"{'':8s}", end="")
    for t in tokens:
        print(f"{t:>8s}", end="")
    print()

    for i, t in enumerate(tokens):
        print(f"{t:8s}", end="")
        for j in range(len(tokens)):
            print(f"{weights[i, j]:>8.3f}", end="")
        print()

    print()
    print("💡 观察：")
    print("  - '苹果' 对 '公司' 和 '水果' 的注意力都较高（因为它向量里有两者的方向）")
    print("  - '公司' 最关注自己和'苹果'")
    print("  - '发布' 在自己的独立方向，大部分注意力在自己")
    print()
    print("  真实的 Transformer 不是手工设计向量，")
    print("  而是通过训练让这些向量'自己长出'语义关系。")


# =============================================================================
# Part 4: 思考题
# =============================================================================
# TODO 回答以下问题：

# 1. 为什么 RAG 用 cosine 相似度而不是欧氏距离？
# 你的答案:
# （提示：cosine 不受向量长度影响，更关注语义方向）

# 2. 为什么 Attention 的 QK^T 要除以 sqrt(d_k)？
# 你的答案:
# （提示：防止点积过大导致 softmax 梯度消失）

# 3. 为啥 attention weights 每一行加起来必须是 1？
# 你的答案:
# （提示：softmax 归一化的性质，每行是一个"注意力分布"）


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Part 1 · Mini-RAG 检索系统")
    print("=" * 60)
    mini_rag_demo()

    print()
    print("=" * 60)
    print("Part 2 · Mini-Attention（Transformer 核心）")
    print("=" * 60)
    mini_attention_demo()

    print()
    print("=" * 60)
    print("Part 3 · 看 Attention 学到了什么")
    print("=" * 60)
    attention_with_meaning()

    print()
    print("🎉 恭喜！你完成了 Week 3 的毕业项目")
    print("   从今天起，你可以自信地说：'我懂 LLM 的数学基础'")
    print()
    print("下一阶段：阶段 2 · LLM 认知（Transformer + HuggingFace）")
