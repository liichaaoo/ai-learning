# 2.1 经典机器学习

> 核心知识点：**线性回归、逻辑回归、决策树、SVM、集成学习（Bagging/Boosting）、聚类与降维**
> 周期：约 3 周｜目标：吃透经典算法的数学推导 + sklearn 实战 + 至少 1 个算法手写复现

---

## 学习目标

完成本节后你应该能够：
- 用数学语言推导线性回归、逻辑回归、SVM 的优化目标与求解过程
- 讲清楚 **偏差-方差分解**、**过拟合/欠拟合**、**正则化**（L1/L2）背后的直觉
- 区分 **Bagging vs Boosting** 的机制差异，能手画随机森林 / GBDT / XGBoost 的训练流程
- 熟练使用 `sklearn` 搭建完整 Pipeline（预处理 → 特征工程 → 模型 → 调参 → 评估）
- **不调用 sklearn 手写一版线性回归 + 逻辑回归 + 决策树（ID3/CART 任选）**
- 面试级别回答：LR vs SVM、GBDT vs 随机森林、L1 为何稀疏

> 🎯 **配套练习题**：待补充（建议 Kaggle 入门赛 Titanic / House Prices 各做一次）

---

## 视频课程（强烈推荐先看）

> 🌐 **访问提示**：Coursera 因制裁限制国内无法注册，下表已优先给出 **B 站 / 网易云课堂** 等国内可访问镜像。YouTube 资源标注 🪜 代表需科学上网。

### 入门首选（国内可直连）
| 资源 | 时长 | 备注 |
|------|------|------|
| ⭐ [吴恩达《机器学习》2022 新版（B 站搬运，中英字幕）](https://www.bilibili.com/video/BV1Pa411X76s) | 3 门课 / ~60h | **最佳入门**，Python 作业代码：[GitHub](https://github.com/greyhatguy007/Machine-Learning-Specialization-Coursera) |
| [吴恩达《机器学习》2022 新版（网易云课堂官方汉化）](https://study.163.com/course/introduction/1210076550.htm) | — | 官方正版中文字幕，免费 |
| [吴恩达《机器学习》老版 Octave（B 站）](https://www.bilibili.com/video/BV164411b7dx) | 18 周 | 数学推导更细，中文字幕 |
| [林轩田《机器学习基石 + 技法》（B 站）](https://www.bilibili.com/video/BV1Cx411i7op) | 16+16 周 | **台大神课**，理论扎实 |

> 📦 **吴恩达新版课程作业/讲义下载**（无需 Coursera 账号）：
> - 作业代码：https://github.com/greyhatguy007/Machine-Learning-Specialization-Coursera
> - 讲义笔记：https://github.com/kaieye/2022-Machine-Learning-Specialization

### 系统课程
| 资源 | 适合 |
|------|------|
| ⭐ [李宏毅《机器学习》2021/2023（台大官网）](https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php) | **最活泼**，中文讲解（讲义可直接下） |
| ⭐ [李宏毅《机器学习》B 站搬运](https://www.bilibili.com/video/BV1Wv411h7kN) | 国内直连版本 |
| [CS229 — Andrew Ng（斯坦福官网）](https://cs229.stanford.edu/) | 想读懂 paper、做研究（讲义 PDF 免费） |
| [CS229 B 站搬运（中英字幕）](https://www.bilibili.com/video/BV1JE411w7Ub) | 国内直连版本 |
| [StatQuest（YouTube）🪜](https://www.youtube.com/@statquest) | ⭐ **每个算法配 10 分钟动画**，极佳复习 |
| [StatQuest B 站官方号](https://space.bilibili.com/3493277319105074) | 国内直连，部分视频有中文字幕 |

---

## 书籍

### 入门
- 📘 ⭐ **《机器学习》—— 周志华（西瓜书）** — 中文教科书首选
- 📘 ⭐ **《机器学习公式详解》（南瓜书）** https://github.com/datawhalechina/pumpkin-book — 西瓜书公式推导补充
- 📘 **《统计学习方法》—— 李航** — 数学严谨，面试常考

### 进阶
- 📘 ⭐ **《The Elements of Statistical Learning》(ESL)** — Hastie, Tibshirani, Friedman
  - 免费 PDF：https://hastie.su.domains/ElemStatLearn/
- 📘 **《Pattern Recognition and Machine Learning》(PRML)** — Bishop（贝叶斯视角）
- 📘 **《Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow》** — Aurélien Géron（**实战首选**）

### AI 加餐 / 速查
- ⭐ **[sklearn 官方 User Guide](https://scikit-learn.org/stable/user_guide.html)** — 边查边学
- ⭐ **[Distill.pub — 可视化机器学习](https://distill.pub/)**
- **[ML Cheatsheet — Stanford CS229](https://stanford.edu/~shervine/teaching/cs-229/)**
- **[《机器学习中的数学》— MML Book 第 5-12 章](https://mml-book.github.io/)**

---

## 按知识点精读

### 1. 监督学习基础
- **线性回归 / 岭回归 / Lasso**
  - 西瓜书第 3 章；ESL 第 3 章
  - 推导：最小二乘闭式解、梯度下降解、正则化几何解释（L1 稀疏 vs L2 平滑）
- **逻辑回归（Logistic Regression）**
  - 推导：Sigmoid → 最大似然 → 交叉熵损失
  - 对比 Softmax 回归（多分类）
- **评估指标**：MSE/RMSE/MAE、Accuracy/Precision/Recall/F1、ROC-AUC、PR 曲线
  - ⭐ 必读：[Google ML Crash Course — Classification](https://developers.google.com/machine-learning/crash-course/classification)

### 2. 树模型
- **决策树**：ID3 / C4.5 / CART（信息增益、增益率、基尼系数）
- **随机森林**：Bagging + 随机特征子集
- ⭐ **GBDT（梯度提升树）**：加法模型 + 前向分步算法 + 负梯度拟合
- ⭐ **XGBoost / LightGBM / CatBoost**（**工业界爆款，面试必考**）
  - 必读论文：[XGBoost: A Scalable Tree Boosting System (KDD'16)](https://arxiv.org/abs/1603.02754)
  - [LightGBM 原理](https://lightgbm.readthedocs.io/en/latest/Features.html)
  - StatQuest 视频：Gradient Boost / XGBoost 4 集连播

### 3. SVM（支持向量机）
- 硬间隔 → 软间隔 → 核技巧
- 对偶问题、KKT 条件、SMO 算法（了解思想即可）
- 核函数：线性 / 多项式 / **RBF（高斯核）**
- 参考：林轩田《机器学习技法》第 1-6 讲、西瓜书第 6 章

### 4. 无监督学习
- **聚类**：K-Means（EM 思想）、层次聚类、DBSCAN、GMM
- **降维**：PCA（上一章已学）、t-SNE、UMAP
  - 必看：[How to Use t-SNE Effectively (Distill)](https://distill.pub/2016/misread-tsne/)

### 5. 模型选择与调优（⭐ 工程必备）
- **偏差-方差分解**：西瓜书 2.5 节
- **交叉验证**：K-Fold、Stratified K-Fold、时间序列 CV
- **超参数搜索**：Grid Search / Random Search / Bayesian Optimization（Optuna）
- **特征工程**：缺失值、类别编码、归一化、特征交叉、目标编码
  - ⭐ [Kaggle — Feature Engineering 课程](https://www.kaggle.com/learn/feature-engineering)

### 6. 概率图模型（了解即可）
- 朴素贝叶斯、HMM（后续 NLP 会用）
- 李航《统计学习方法》第 4、10 章

---

## 3 周学习计划

```
Week 1: 线性/逻辑回归 + 评估指标
        → 吴恩达 Course 1 + 西瓜书 3 章
        → 手写线性回归（梯度下降 + 闭式解两种实现）

Week 2: 树模型 + SVM
        → 西瓜书 4、6、8 章 + StatQuest 决策树/GBDT 视频
        → sklearn 实战 Titanic，跑通 RF / XGBoost / LightGBM 对比

Week 3: 无监督 + 调优 + 综合项目
        → K-Means / PCA / t-SNE 可视化 MNIST
        → 完成 Kaggle House Prices（进 Top 50%）

检验：能在白板上推导 LR 损失函数、手画 GBDT 训练流程、说清 L1 为何稀疏
```

---

## 实战练习

### sklearn 基础 Pipeline
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(C=1.0, penalty="l2", max_iter=1000)),
])
scores = cross_val_score(pipe, X, y, cv=5, scoring="roc_auc")
print(scores.mean(), scores.std())
```

### 手写线性回归（梯度下降）
```python
import numpy as np

class LinearRegressionGD:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr, self.epochs = lr, epochs

    def fit(self, X, y):
        X = np.c_[np.ones(len(X)), X]          # 加偏置列
        self.w = np.zeros(X.shape[1])
        for _ in range(self.epochs):
            grad = X.T @ (X @ self.w - y) / len(X)
            self.w -= self.lr * grad
        return self

    def predict(self, X):
        return np.c_[np.ones(len(X)), X] @ self.w
```

### XGBoost 快速上手
```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

X_tr, X_va, y_tr, y_va = train_test_split(X, y, test_size=0.2, random_state=42)
model = xgb.XGBClassifier(
    n_estimators=500, max_depth=6, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    eval_metric="auc", early_stopping_rounds=30,
)
model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=50)
```

### K-Means 可视化
```python
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

X, _ = make_blobs(n_samples=500, centers=4, random_state=0)
km = KMeans(n_clusters=4, n_init=10).fit(X)
plt.scatter(X[:, 0], X[:, 1], c=km.labels_, cmap="viridis")
plt.scatter(*km.cluster_centers_.T, c="red", marker="x", s=200)
```

---

## 产出 Checklist

- [ ] 笔记：线性回归 3 种推导（最小二乘 / MLE / 梯度下降）
- [ ] 笔记：逻辑回归损失函数推导 + 为什么不用 MSE
- [ ] 笔记：偏差-方差分解图示 + 举例
- [ ] 笔记：L1 vs L2 正则化（几何图 + 为何 L1 稀疏）
- [ ] 笔记：决策树分裂准则对比（信息增益/增益率/基尼）
- [ ] 笔记：Bagging vs Boosting 对比表 + GBDT/XGBoost 流程图
- [ ] 笔记：SVM 对偶问题与核技巧
- [ ] **代码：手写线性回归 + 逻辑回归**（闭式解 & 梯度下降）→ 放 `../代码/`
- [ ] **代码：手写 CART 决策树**（递归分裂 + 剪枝）
- [ ] **项目：Kaggle Titanic 端到端 Pipeline**（目标 ≥ 80%）→ 放 `../产出/`
- [ ] **项目：Kaggle House Prices**（LightGBM + 特征工程，目标 Top 50%）

---

## 经典面试题（自测）

- [ ] 为什么逻辑回归用交叉熵而不是 MSE？
- [ ] L1 正则化为什么能产生稀疏解？（画图解释）
- [ ] 随机森林 vs GBDT 的核心区别？
- [ ] XGBoost 相比 GBDT 做了哪些工程优化？（二阶导、正则、列采样、直方图…）
- [ ] SVM 为什么要用对偶？核函数本质是什么？
- [ ] K-Means 对初始点敏感怎么办？（K-Means++）
- [ ] ROC-AUC 与 PR-AUC 什么时候用哪个？（类别不均衡场景）
- [ ] 特征归一化对哪些算法重要？哪些不重要？（树模型不需要）

---

## 待定/疑问

记录学习中遇到的问题，定期回看：

```
- [ ] (示例) XGBoost 的二阶泰勒展开比一阶好在哪里？
- [ ] (示例) 为什么 GBDT 每棵树拟合的是负梯度而不是残差？
- [ ] (示例) SVM 的支持向量一定在间隔边界上吗？
```
