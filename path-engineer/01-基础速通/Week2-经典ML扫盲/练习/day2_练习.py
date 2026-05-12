"""
Day 2 练习 · 监督学习核心算法

做题说明：
- 概念题：在 TODO 下面写答案
- 代码题：补全 / 运行
- 运行：python day2_练习.py
"""

# =============================================================================
# 题 1（概念）：算法名片复述
# =============================================================================
# 不查资料，填出每个算法的"直觉描述"（一句话）

cards = {
    "线性回归":   "",  # TODO:
    "逻辑回归":   "",  # TODO:
    "决策树":     "",  # TODO:
    "随机森林":   "",  # TODO:
    "XGBoost":   "",  # TODO:
    "KNN":       "",  # TODO:
    "SVM":       "",  # TODO:
}


# =============================================================================
# 题 2（选择）：场景选算法
# =============================================================================
# 每个场景选一个你觉得最合适的算法（多选也 OK，但要说理由）

scenarios = [
    {
        "场景": "银行要给审贷决策做模型，要求能解释为什么拒绝/通过",
        "你选": "",  # TODO: 提示 - 需要解释性
        "理由": "",
    },
    {
        "场景": "电商要预测用户下单金额（连续数值），有 100 万样本",
        "你选": "",  # TODO:
        "理由": "",
    },
    {
        "场景": "想要一个 baseline 快速验证想法，不管准确率",
        "你选": "",  # TODO:
        "理由": "",
    },
    {
        "场景": "Kaggle 结构化数据比赛，追求最高分数",
        "你选": "",  # TODO:
        "理由": "",
    },
]


# =============================================================================
# 题 3（代码）：多算法对比
# =============================================================================
# 跑一遍下面代码，观察不同算法在鸢尾花数据上的表现

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


def compare_models():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "逻辑回归":   LogisticRegression(max_iter=200),
        "决策树":     DecisionTreeClassifier(random_state=42),
        "随机森林":   RandomForestClassifier(random_state=42),
        "KNN(k=5)": KNeighborsClassifier(),
        "SVM":       SVC(),
        "朴素贝叶斯": GaussianNB(),
    }

    print(f"{'算法':<12} {'准确率':<10}")
    print("-" * 25)
    for name, model in models.items():
        model.fit(X_train, y_train)
        acc = model.score(X_test, y_test)
        print(f"{name:<12} {acc:.4f}")


# =============================================================================
# 题 4（代码）：sklearn API 统一性体验
# =============================================================================
# 下面函数要对任意模型都能用，请补全 TODO

def train_and_eval(model, X_train, y_train, X_test, y_test):
    """
    接收一个 sklearn 模型，训练并返回测试准确率。
    体会 sklearn 的"统一 API"。
    """
    # TODO: 1. 调用 model 的训练方法
    # model.???

    # TODO: 2. 调用 model 的评分方法（在测试集上）
    # acc = model.???

    # return acc
    pass


# =============================================================================
# 题 5（思考）：为什么大家都用 XGBoost？
# =============================================================================
# 网上流传一句话："上了 XGBoost，什么算法都得跪。"
# 结合今天学的内容，说说 XGBoost 相对单棵决策树、相对随机森林，各自的优势是什么？

# TODO 你的回答：
# - vs 决策树:
# - vs 随机森林:


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 3 · 多算法对比")
    print("=" * 60)
    compare_models()

    print()
    print("=" * 60)
    print("题 4 · 统一 API 体验")
    print("=" * 60)
    from sklearn.linear_model import LogisticRegression
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 你补全了 train_and_eval 函数后，下面应该能跑：
    # for Model in [LogisticRegression, DecisionTreeClassifier, RandomForestClassifier]:
    #     m = Model() if Model is not LogisticRegression else Model(max_iter=200)
    #     acc = train_and_eval(m, X_train, y_train, X_test, y_test)
    #     print(f"{Model.__name__}: {acc:.4f}")

    print()
    print("💡 观察：sklearn 所有模型都是 fit/predict/score 三板斧")
    print("   你以后看任何 ML 代码，都能快速定位是哪一步")
