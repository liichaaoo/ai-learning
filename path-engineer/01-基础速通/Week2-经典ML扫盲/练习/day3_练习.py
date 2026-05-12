"""
Day 3 练习 · 无监督学习与降维

运行：python day3_练习.py
（Day 3 练习会画图，确保你的环境能显示 matplotlib）
"""

# =============================================================================
# 题 1（概念）：监督 vs 无监督
# =============================================================================
# 下列场景是监督学习还是无监督学习？

tasks = [
    "根据 10 万份带情感标签的评论训练模型",       # TODO: 监督
    "把一个商城的 100 万用户自动分成若干群",       # TODO:
    "给信用卡系统找出异常交易",                   # TODO:
    "根据房屋信息预测房价",                       # TODO:
    "把 Word Embedding 画成 2D 可视化图",         # TODO:
    "自动发现今天最热门的 10 个新闻话题",         # TODO:
]


# =============================================================================
# 题 2（选择）：场景选算法
# =============================================================================
scenarios = [
    {
        "场景": "产品经理给你 10 万条评论，想知道用户在抱怨哪些主题",
        "选": "",  # TODO: 聚类
        "算法": "",
    },
    {
        "场景": "你要把 768 维的 BERT embedding 存到向量库，但觉得太大想瘦身",
        "选": "",  # TODO: 降维（PCA）
        "算法": "",
    },
    {
        "场景": "运维同学想从 1000 万条日志里找'长相诡异'的那些",
        "选": "",  # TODO: 异常检测或 DBSCAN
        "算法": "",
    },
    {
        "场景": "论文里要画一张图展示你模型的 embedding 效果",
        "选": "",  # TODO: 降维（t-SNE / UMAP）
        "算法": "",
    },
]


# =============================================================================
# 题 3（代码）：K-Means 聚类 + PCA 可视化
# =============================================================================
# 补全下面代码，运行后你会看到两张图对比
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


def kmeans_and_visualize():
    # 1. 加载数据
    X, y_true = load_iris(return_X_y=True)
    target_names = load_iris().target_names

    # 2. 标准化
    X_std = StandardScaler().fit_transform(X)

    # 3. TODO: PCA 降维到 2D
    # X_2d = PCA(???).fit_transform(X_std)
    X_2d = PCA(n_components=2).fit_transform(X_std)

    # 4. TODO: K-Means 聚类，K=3
    # kmeans = KMeans(???)
    # y_pred = kmeans.???(X_std)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    y_pred = kmeans.fit_predict(X_std)

    # 5. 画图
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for i, name in enumerate(target_names):
        axes[0].scatter(X_2d[y_true == i, 0], X_2d[y_true == i, 1], label=name)
    axes[0].set_title("Ground Truth (Supervised view)")
    axes[0].legend()

    for i in range(3):
        axes[1].scatter(X_2d[y_pred == i, 0], X_2d[y_pred == i, 1], label=f"Cluster {i}")
    axes[1].set_title("K-Means (Unsupervised view)")
    axes[1].legend()

    plt.tight_layout()
    plt.show()
    print("观察：两张图结构是否相似？这说明了什么？")


# =============================================================================
# 题 4（代码）：用 DBSCAN 找异常
# =============================================================================
from sklearn.cluster import DBSCAN
import numpy as np

def dbscan_anomaly_demo():
    # 构造"正常数据 + 少量异常"
    np.random.seed(42)
    normal = np.random.randn(100, 2)        # 正常点，分布在原点附近
    anomaly = np.array([[5, 5], [6, 6], [-4, -4]])  # 人为的异常点
    X = np.vstack([normal, anomaly])

    # TODO: DBSCAN 聚类
    # 提示：eps=0.5 太小会把正常点也当异常，eps=1.0 比较合适
    # db = DBSCAN(eps=???, min_samples=???)
    db = DBSCAN(eps=1.0, min_samples=5)
    labels = db.fit_predict(X)

    # label == -1 的就是异常点
    n_anomaly = (labels == -1).sum()
    print(f"DBSCAN 找出的异常点数量：{n_anomaly}")
    print(f"（真实人为添加的异常点：3 个）")

    # 画图
    plt.figure(figsize=(8, 6))
    plt.scatter(X[labels != -1, 0], X[labels != -1, 1], label='Normal', alpha=0.5)
    plt.scatter(X[labels == -1, 0], X[labels == -1, 1], c='red', label='Anomaly', s=100)
    plt.title("DBSCAN 异常检测")
    plt.legend()
    plt.show()


# =============================================================================
# 题 5（思考）：RAG 和今天学的内容有什么联系？
# =============================================================================
# 今天学了"向量"、"相似度"、"聚类"、"降维"
# 如果让你设计一个简化版 RAG（从 10000 篇文档中找到与问题最相关的 3 篇），
# 你会用今天学的哪些概念？

# TODO 你的思考：
# - 文档怎么表示？      （提示：embedding，一种降维/表示学习）
# - 怎么找最相似的？     （提示：向量相似度，像 KNN）
# - 可以不可以先聚类加速？（提示：先聚类，检索时只在近的簇里找）


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 3 · K-Means + PCA 可视化")
    print("=" * 60)
    kmeans_and_visualize()

    print()
    print("=" * 60)
    print("题 4 · DBSCAN 异常检测")
    print("=" * 60)
    dbscan_anomaly_demo()
