"""
Day 1 练习 · 向量与矩阵（LLM 视角）

运行：python day1_练习.py
"""

import numpy as np


# =============================================================================
# 题 1（手算 + 代码验证）
# =============================================================================
# 给定 a = [2, 3, 4]，b = [5, 6, 7]，不打开 Python，先手算：
#
# TODO: a + b = ___
# TODO: a - b = ___
# TODO: 3 * a = ___
# TODO: a 和 b 的点积 = ___
# TODO: a 的 L2 范数 ≈ ___

def verify_q1():
    a = np.array([2, 3, 4])
    b = np.array([5, 6, 7])
    print(f"a + b = {a + b}")              # [7 9 11]
    print(f"a - b = {a - b}")              # [-3 -3 -3]
    print(f"3 * a = {3 * a}")              # [6 9 12]
    print(f"a · b = {np.dot(a, b)}")       # 56
    print(f"||a|| = {np.linalg.norm(a):.4f}")  # 5.3852


# =============================================================================
# 题 2（核心）：实现 cosine 相似度
# =============================================================================
# TODO: 不查资料，根据公式
# cos_sim(a, b) = (a · b) / (||a|| * ||b||)
# 自己实现 cosine_similarity 函数

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # TODO: 你的实现
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# =============================================================================
# 题 3：理解"cosine 不受长度影响"
# =============================================================================
# 用下面 3 对向量测试，观察结果

def test_cosine_properties():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 4.0, 6.0])       # 是 a 的 2 倍（方向一样）
    c = np.array([1.0, 0.0, 0.0])       # 和 a 方向不同
    d = np.array([-1.0, -2.0, -3.0])    # 和 a 方向完全相反

    print(f"cos(a, b)  = {cosine_similarity(a, b):.4f}")  # ≈ 1.0 方向相同
    print(f"cos(a, c)  = {cosine_similarity(a, c):.4f}")  # 有部分相似
    print(f"cos(a, d)  = {cosine_similarity(a, d):.4f}")  # -1.0 完全相反

    # TODO 思考：为什么 cos(a, b) = 1？（虽然长度差 2 倍）
    # 答案：因为它们方向完全一致，cosine 只看方向不看长度


# =============================================================================
# 题 4：mini-RAG 检索模拟
# =============================================================================
# 场景：有 5 个文档（用假 embedding），用户问一个问题，找 Top-2 相关文档

def mini_rag_demo():
    # 伪造文档 embedding（实际用 bge-m3 等模型生成，这里用随机值）
    np.random.seed(42)
    docs = {
        "doc1: 苹果公司发布 iPhone 17":      np.array([0.9, 0.1, 0.05, 0.0]),
        "doc2: Tim Cook 主持财报会议":       np.array([0.7, 0.2, 0.05, 0.0]),
        "doc3: 鸿蒙操作系统更新":            np.array([0.1, 0.9, 0.05, 0.0]),
        "doc4: 梨子种植技术":                np.array([0.05, 0.05, 0.9, 0.0]),
        "doc5: 苹果手机销售数据":            np.array([0.85, 0.15, 0.05, 0.0]),
    }

    query = "苹果公司的最新产品"
    query_vec = np.array([0.88, 0.12, 0.05, 0.0])  # 假的 query embedding

    # TODO: 算出 query 与每个文档的 cosine 相似度
    scores = []
    for doc_name, doc_vec in docs.items():
        sim = cosine_similarity(query_vec, doc_vec)
        scores.append((doc_name, sim))

    # 按相似度降序
    scores.sort(key=lambda x: x[1], reverse=True)

    print(f"Query: {query}\n")
    print("相似度排名（Top-5）：")
    for i, (name, sim) in enumerate(scores, 1):
        print(f"  {i}. [{sim:.4f}]  {name}")

    print()
    print("💡 观察：Top-2 应该是 doc1 和 doc5（都是苹果公司相关）")
    print("   这就是 RAG 检索的最简版本。")


# =============================================================================
# 题 5：矩阵形状练习
# =============================================================================
# 下面是常见的 LLM 张量形状，你能解释每个是什么意思吗？

shapes = {
    "(100, 1024)":            "",  # TODO: 100 条文本的 embedding，每条 1024 维
    "(32, 512, 768)":         "",  # TODO: batch=32, 序列长度 512, 每个 token 768 维
    "(8, 12, 64, 64)":        "",  # TODO: batch=8, 12 个 attention head, 64x64 注意力矩阵
    "(768, 512)":             "",  # TODO: 权重矩阵，把 768 维输入变成 512 维输出
}


# =============================================================================
# 题 6：NumPy 矩阵基本操作
# =============================================================================

def numpy_matrix_ops():
    # 构造矩阵
    A = np.array([[1, 2, 3],
                  [4, 5, 6]])

    print(f"A = \n{A}")
    print(f"A.shape = {A.shape}")
    print(f"A.ndim  = {A.ndim}")

    # TODO: 打印 A 的转置 A.T 和它的形状
    print(f"\nA.T = \n{A.T}")
    print(f"A.T.shape = {A.T.shape}")

    # 提取第 0 行
    print(f"\nA[0] = {A[0]}       （第 0 行）")
    # 提取第 1 列
    print(f"A[:, 1] = {A[:, 1]}  （第 1 列）")
    # 提取单个元素
    print(f"A[1, 2] = {A[1, 2]}  （第 1 行第 2 列）")


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 1 · 向量基本运算")
    print("=" * 60)
    verify_q1()

    print()
    print("=" * 60)
    print("题 3 · Cosine 不受长度影响")
    print("=" * 60)
    test_cosine_properties()

    print()
    print("=" * 60)
    print("题 4 · Mini-RAG 检索")
    print("=" * 60)
    mini_rag_demo()

    print()
    print("=" * 60)
    print("题 6 · 矩阵基本操作")
    print("=" * 60)
    numpy_matrix_ops()

    print()
    print("✅ Day 1 练习完成。明天继续 Day 2：矩阵乘法与 Attention 基石")
