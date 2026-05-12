"""
Day 4 练习 · 模型评估与过拟合

运行：python day4_练习.py
"""

# =============================================================================
# 题 1（概念）：场景该关注哪个指标？
# =============================================================================
# 每个场景选：Precision / Recall / F1 / AUC，并说明原因

scenarios = [
    {
        "场景": "反垃圾邮件（误判正常邮件成本极高）",
        "选": "",       # TODO: Precision
        "原因": "",     # TODO: 不想误伤用户
    },
    {
        "场景": "癌症早筛（漏诊成本极高）",
        "选": "",       # TODO: Recall
        "原因": "",
    },
    {
        "场景": "信用卡盗刷检测（1% 盗刷 + 误伤和漏检都有代价）",
        "选": "",       # TODO: F1
        "原因": "",
    },
    {
        "场景": "广告点击率预估（要的是模型整体排序能力）",
        "选": "",       # TODO: AUC
        "原因": "",
    },
]


# =============================================================================
# 题 2（计算）：手算 Precision / Recall / F1
# =============================================================================
# 某盗刷模型在测试集的混淆矩阵：
#   TP = 80   FP = 20
#   FN = 10   TN = 890
#
# 手动算（对答案前不要运行代码）：

# TODO: Precision = TP / (TP + FP) = 80 / (80+20) = ?
# TODO: Recall    = TP / (TP + FN) = 80 / (80+10) = ?
# TODO: F1        = 2 * P * R / (P + R) = ?
# TODO: Accuracy  = (TP + TN) / 总数 = ?

# 答案参考（自己算完再来比较）：
def check_answers():
    TP, FP, FN, TN = 80, 20, 10, 890
    P = TP / (TP + FP)
    R = TP / (TP + FN)
    F1 = 2 * P * R / (P + R)
    Acc = (TP + TN) / (TP + FP + FN + TN)
    print(f"Precision = {P:.4f}  (0.8000)")
    print(f"Recall    = {R:.4f}  (0.8889)")
    print(f"F1        = {F1:.4f}  (0.8421)")
    print(f"Accuracy  = {Acc:.4f}  (0.9700)")
    print()
    print("注意！Accuracy 97% 看起来很高，但 Recall 只有 88%，")
    print("意味着 12% 的盗刷被漏掉，实际上金融场景这很危险。")


# =============================================================================
# 题 3（代码）：真实代码跑一遍评估
# =============================================================================
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
)


def full_evaluation():
    X, y = load_iris(return_X_y=True)
    target_names = load_iris().target_names

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # 1. 准确率
    acc = accuracy_score(y_test, y_pred)
    print(f"准确率: {acc:.4f}")

    # 2. 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n混淆矩阵 (行=真实, 列=预测):")
    print(cm)

    # 3. 详细报告
    print(f"\n分类报告:")
    print(classification_report(y_test, y_pred, target_names=target_names))


# =============================================================================
# 题 4（代码）：交叉验证
# =============================================================================
from sklearn.model_selection import cross_val_score


def cross_validation_demo():
    X, y = load_iris(return_X_y=True)
    model = LogisticRegression(max_iter=200)

    # TODO: 用 5 折交叉验证评估模型
    # scores = cross_val_score(model, X, y, cv=???, scoring='accuracy')
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')

    print(f"5 折交叉验证各折准确率: {scores}")
    print(f"平均准确率: {scores.mean():.4f} ± {scores.std():.4f}")


# =============================================================================
# 题 5（代码）：观察过拟合
# =============================================================================
# 分别训练一个 max_depth=None（不限深度）和 max_depth=3 的决策树
# 对比训练集 vs 测试集的准确率差异

from sklearn.tree import DecisionTreeClassifier


def overfitting_demo():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    for max_depth in [None, 3]:
        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)

        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        gap = train_acc - test_acc

        print(f"max_depth={max_depth}:")
        print(f"  训练集准确率: {train_acc:.4f}")
        print(f"  测试集准确率: {test_acc:.4f}")
        print(f"  差距: {gap:.4f}  {'(轻微过拟合)' if gap > 0.05 else '(正常)'}")
        print()


# =============================================================================
# 题 6（思考）：如果你的模型训练集 99% 但测试集 60%，你会做什么？
# =============================================================================
# 按你觉得的优先级列出 3-5 个排查/修复动作

# TODO 你的答案：
# 1.
# 2.
# 3.


# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("题 2 · 手算 P/R/F1/Acc 答案对照")
    print("=" * 60)
    check_answers()

    print()
    print("=" * 60)
    print("题 3 · 完整评估示例")
    print("=" * 60)
    full_evaluation()

    print()
    print("=" * 60)
    print("题 4 · 交叉验证")
    print("=" * 60)
    cross_validation_demo()

    print()
    print("=" * 60)
    print("题 5 · 观察过拟合")
    print("=" * 60)
    overfitting_demo()
