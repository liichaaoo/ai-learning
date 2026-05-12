# Day 5 · 综合应用（手搓 mini-Attention + mini-RAG）

> ⏱️ 目标时间：1.5-2 小时（周末做）
> 🎯 产出：**用前 4 天学的数学，亲手实现两个"迷你版 AI 系统"**

---

## 🧭 今天的主线

前 4 天你学了：
- Day 1：向量 + cosine 相似度（RAG 的检索底层）
- Day 2：矩阵乘法 + QK^T（Attention 的骨架）
- Day 3：Softmax + 交叉熵（概率分布 + loss）
- Day 4：梯度下降 + autograd（训练的引擎）

**今天把这些拼起来，做 2 个小项目**：

1. **Mini-RAG 检索系统**：用 Day 1 的 cosine 相似度做文档检索
2. **Mini-Attention**：用 Day 2+3 的矩阵乘法 + softmax，手撸 Attention 核心

做完这两个，你就能**看懂 95% 的 AI 教程代码**。

---

## Part 1：Mini-RAG 检索系统 ⭐

### 目标

模拟一个真实 RAG 系统的核心：
```
用户提问 → 把所有文档和问题都转成向量 → cosine 相似度 → Top-K 文档
```

### 简化版代码框架

```python
import numpy as np

# ============ 用 fake embedding 模拟真实的 embedding 模型 ============
def fake_embed(text: str) -> np.ndarray:
    """
    模拟真实的 embedding 模型。
    （实际用 sentence-transformers / bge-m3 等，这里用字符频率当 embedding）
    """
    vec = np.zeros(32)
    for ch in text:
        vec[ord(ch) % 32] += 1
    # 归一化（长度变成 1）
    return vec / (np.linalg.norm(vec) + 1e-8)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


# ============ 知识库：一堆文档 ============
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

# ============ 建索引（预处理：把所有文档向量化） ============
doc_vecs = [fake_embed(doc) for doc in docs]

# ============ 检索 ============
def retrieve(query: str, top_k: int = 3):
    q_vec = fake_embed(query)
    scores = [(i, cosine_similarity(q_vec, dv)) for i, dv in enumerate(doc_vecs)]
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_k]
    print(f"Query: {query}")
    for rank, (idx, score) in enumerate(top, 1):
        print(f"  Top {rank} [{score:.4f}]: {docs[idx]}")


# ============ 测试 ============
retrieve("苹果公司的最新产品动态", top_k=3)
```

### 你要思考的问题

1. 为什么要把 embedding 向量**归一化**（长度变成 1）？
   - 答：这样 cosine 相似度计算就简化成点积（提速）
2. 如果文档从 10 个变成 1000 万个，这个暴力比较还行吗？
   - 答：不行了，要用 **FAISS / Milvus 等向量库**（加速到近似 O(log n)）

### 这就是真实 RAG 系统的核心

把上面 `fake_embed` 换成 `bge-m3`，把暴力比较换成 Milvus，你就有了**生产可用的 RAG 基础设施**。阶段 3 会学。

---

## Part 2：Mini-Attention ⭐⭐⭐

### 目标

实现 Transformer 最核心的那个公式：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

### 完整代码（建议你一行一行打字，不要 copy）

```python
import numpy as np

def stable_softmax(x, axis=-1):
    """沿指定维度做稳定 softmax"""
    x_max = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - x_max)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V):
    """
    Attention 核心公式
    Q, K, V shape: (seq_len, d_k)
    """
    d_k = Q.shape[-1]

    # Step 1: Q @ K^T  (seq_len, seq_len)
    scores = Q @ K.T

    # Step 2: 缩放 (防止点积过大导致 softmax 梯度消失)
    scores = scores / np.sqrt(d_k)

    # Step 3: softmax 归一化 (每一行加起来=1)
    weights = stable_softmax(scores, axis=-1)

    # Step 4: 加权 V
    output = weights @ V

    return output, weights


# ============ 测试 ============
np.random.seed(42)
seq_len = 4    # 4 个 token
d_k = 8        # 每个向量 8 维

Q = np.random.randn(seq_len, d_k)
K = np.random.randn(seq_len, d_k)
V = np.random.randn(seq_len, d_k)

output, weights = scaled_dot_product_attention(Q, K, V)

print(f"Q.shape     = {Q.shape}")
print(f"output.shape = {output.shape}    # 应该和 V 一样: (4, 8)")
print(f"weights     = \n{weights.round(3)}")
print()
print("💡 每一行的 4 个数加起来 ≈ 1（softmax 的性质）")
print(f"   验证: weights 每行和 = {weights.sum(axis=-1)}")
```

### 你刚刚手撸的是什么？

**Transformer 里最核心的一块代码**。你把它复制进 PyTorch，加上可训练的 Q/K/V 投影矩阵，就是完整的 Self-Attention Layer。

阶段 2（LLM 认知）会再深入，但**你今天已经领先了大多数 AI 爱好者**。

---

## Part 3：综合练习 + 思考题

### 综合练习

完成 [`练习/day5_综合实战.py`](./练习/day5_综合实战.py)，包含：
1. 手搓 RAG
2. 手搓 Attention
3. 观察 attention weights（Transformer 可解释性的起点）

### 关键思考题

#### Q1：Attention 的 weights 告诉了我们什么？

如果你在句子 "苹果公司发布了新 iPhone" 上跑 Attention，某个 token "苹果" 的 attention weights 可能长这样：
```
苹果 → [苹果: 0.1, 公司: 0.5, 发布: 0.1, 了: 0.1, 新: 0.1, iPhone: 0.1]
```
意思是"苹果"这个 token 主要在关注"公司"这个词（帮助消歧：苹果是"公司"不是"水果"）。

**这就是 Transformer 的"可解释性"起点**。

#### Q2：为什么 $QK^T$ 要除以 $\sqrt{d_k}$？

提示：Day 3 讲过 softmax 对输入大小敏感。如果点积结果很大，softmax 会把它变成"one-hot 分布"（一个 1，其他全 0），梯度消失。
缩放是为了**把点积的方差控制在 1 左右**，保证 softmax 输出是"有意义的分布"，不是极端情况。

---

## 🎯 本周出关自测（回顾 Week3 README 的 10 道题）

```
1. 点积和 cosine 相似度的关系？
2. (3, 5) @ (5, 2) 的结果形状？
3. (4, 5) @ (4, 5) 能乘吗？
4. Softmax 做什么？
5. 交叉熵衡量什么？
6. 梯度是什么？指向哪？
7. 为什么叫梯度下降？
8. L1 和 L2 范数的区别？
9. 广播是什么？
10. Attention 的 QK^T 本质上算什么？
```

**答对 7+ 题 → Week 3 通过 → 阶段 1 完结 🎉**

---

## ✍️ Week 3 学习小结（写到周报里）

在你下周的周报里补这段：

```markdown
## Week 3 学习小结

### 我掌握的新能力
- 看 AI 代码时先看 shape（不再懵）
- 能给同事讲 cosine 相似度、softmax 的作用
- 看到 Attention 公式不害怕，能拆解每个步骤
- 理解 PyTorch 训练循环的 4 步

### 最难理解的概念
- ???

### Day 5 的两个小项目
- Mini-RAG: 检索效果如何？
- Mini-Attention: attention weights 呈现了什么规律？

### 阶段 1 总结（3 周回顾）
- Week 1 Python 速通：
- Week 2 ML 扫盲：
- Week 3 数学补盲：
- 最有价值的收获：
- 最想继续深挖的方向：
```

---

## 🎉 完成本周后你拥有

**阶段 1 完结**！你正式具备了：

- ✅ Python 开发能力（Java 老兵的跨语言迁移）
- ✅ 经典 ML 术语库 + 能看懂算法代码
- ✅ LLM 相关的数学基础（向量/矩阵/softmax/梯度）
- ✅ PyTorch 基本用法 + 训练循环

**你现在可以：**
- 读懂 HuggingFace、LangChain、Spring AI 的源码
- 和算法同事就"Attention / RAG / LLM"做正常对话
- 进入阶段 2 学 Transformer、HuggingFace 不再被吓到
- 写简历能用"掌握 LLM 基础原理"这句话（问心无愧）

---

## 🚀 下一步

- **本周末**：完成本练习 + 写 Week 3 学习小结 + 写本周周报
- **下周**：进入阶段 2 · LLM 认知（Transformer + HuggingFace）⭐ 越来越有趣了

---

> 💡 **庆祝一下**：3 周基础速通，从 Java 工程师跨到"能读 AI 代码"，
> 大多数人要花 2-3 个月（还学不完）。**你走的是一条被精心优化的路径**。
