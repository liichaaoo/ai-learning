# Week 2 · 经典 ML 函数速查手册

> 本文档汇总 Week2 (Day1 ~ Day5) 练习中**实际使用过**的所有 sklearn API，按主题分组。
> 每个条目包含：功能描述、签名、参数、返回值、示例、Java 类比。
> 配套文件：`练习/day1_练习.py` ~ `练习/day4_练习.py`

---

## 目录

- [一、数据集加载（`sklearn.datasets`）](#一数据集加载sklearndatasets)
- [二、数据划分（`sklearn.model_selection`）](#二数据划分sklearnmodel_selection)
- [三、模型 - 监督学习（分类/回归）](#三模型---监督学习分类回归)
- [四、模型通用 API（fit / predict / score）](#四模型通用-apifit--predict--score)
- [五、评估指标（`sklearn.metrics`）](#五评估指标sklearnmetrics)
- [六、待补充：Day2-Day5 会用到的 API](#六待补充day2-day5-会用到的-api)

---

## 🎯 sklearn 心智模型（先看这个）

sklearn 的所有模型都遵循**同一套 4 步骨架**——这是它最大的设计哲学：

```python
from sklearn.xxx import SomeModel

# 步骤 1：建模型（new 一个对象，传超参数）
model = SomeModel(hyperparam1=..., hyperparam2=...)

# 步骤 2：训练（无返回值，模型在内部"学"完了）
model.fit(X_train, y_train)

# 步骤 3：预测（输入特征，输出标签）
y_pred = model.predict(X_test)

# 步骤 4（可选）：评分
acc = model.score(X_test, y_test)   # 内部就是 predict + accuracy
```

**记住这 4 步，换任何模型都通用** ——逻辑回归、决策树、随机森林、XGBoost、KNN、SVM 全是这套接口。

| sklearn 概念 | Java 类比 |
|------|---------|
| `Model` 类 | 一个 Bean / Service |
| `__init__()` 传超参数 | 构造函数传配置 |
| `fit()` | 一次性训练（类似初始化时加载数据）|
| `predict()` | 业务方法（输入 → 输出）|
| `random_state` | 单测里固定的种子，保证结果可复现 |

---

## 一、数据集加载（`sklearn.datasets`）

### `load_iris(return_X_y=False, as_frame=False)`

加载经典鸢尾花数据集（150 条，3 类，4 特征）。

- **`return_X_y`**：
  - `False`（默认）：返回一个 `Bunch` 对象（类似字典）
  - `True`：直接返回 `(X, y)` 元组（**练习中常用**）
- **`as_frame`**：是否返回 pandas DataFrame

```python
from sklearn.datasets import load_iris

# 方式 1：直接拿 X, y（练习里用的）
X, y = load_iris(return_X_y=True)
print(X.shape)   # (150, 4)
print(y.shape)   # (150,)

# 方式 2：拿完整对象（看类别名、特征名）
data = load_iris()
print(data.feature_names)   # ['sepal length (cm)', ...]
print(data.target_names)    # ['setosa', 'versicolor', 'virginica']
```

#### 同类的还有

| 函数 | 数据集 | 任务 |
|------|------|------|
| `load_iris()` | 鸢尾花 150 条 | 多分类 |
| `load_breast_cancer()` | 乳腺癌 569 条 | 二分类 |
| `load_digits()` | 手写数字 1797 条 | 多分类（8×8 图像）|
| `load_diabetes()` | 糖尿病指标 442 条 | 回归 |
| `load_wine()` | 葡萄酒 178 条 | 多分类 |

> 💡 **注意**：sklearn 的 `load_boston` 已被移除（数据集涉及伦理争议），改用 `fetch_california_housing()`。

---

## 二、数据划分（`sklearn.model_selection`）

### `train_test_split(X, y, test_size=0.25, random_state=None, stratify=None, shuffle=True)`

把数据集随机切分成训练集和测试集。**这是 ML 的第一步神圣仪式**。

#### 参数

- **`X, y`**：特征矩阵和标签
- **`test_size`**：测试集比例（默认 0.25）
  - 数据少：`0.2` 或 `0.25`
  - 数据多：`0.1` 或 `0.05` 也行
- **`random_state`**：随机种子。**写代码必填，否则结果不可复现**
  - 约定俗成用 `42`（《银河系漫游指南》梗）
- **`stratify`**：分层抽样
  - 通常传 `stratify=y`，保证训练集/测试集中各类别比例和原数据一致
  - **类别不平衡时必加**（比如 95% 正常 + 5% 异常）
- **`shuffle`**：是否先打乱（默认 True，几乎不用改）

#### 返回（**顺序重要！**）

```python
X_train, X_test, y_train, y_test = train_test_split(...)
#   ↑        ↑       ↑       ↑
#   X 在前 y 在后；train 在前 test 在后
```

**最常见的写错**：

```python
# ❌ 错位
X_train, y_train, X_test, y_test = train_test_split(X, y, ...)

# ✅ 正确
X_train, X_test, y_train, y_test = train_test_split(X, y, ...)
```

#### 完整示例

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y          # 类别不平衡时强烈建议
)

print(X_train.shape)   # (120, 4)
print(X_test.shape)    # (30, 4)
```

#### Java 类比

```java
// 类似把数据集分成训练 List 和测试 List
List<Sample> all = ...;
Collections.shuffle(all, new Random(42));
int splitPoint = (int)(all.size() * 0.8);
List<Sample> train = all.subList(0, splitPoint);
List<Sample> test  = all.subList(splitPoint, all.size());
```

---

### 待补充（Day4 会用到）

- `cross_val_score(model, X, y, cv=5)` — 交叉验证
- `KFold(n_splits=5)` / `StratifiedKFold` — K 折切分器
- `GridSearchCV` — 超参数网格搜索

---

## 三、模型 - 监督学习（分类/回归）

### `LogisticRegression(max_iter=100, C=1.0, penalty='l2', solver='lbfgs')`

逻辑回归（**别被名字骗了，它是分类模型**）。

> 名字里有"回归"是历史原因——它内部确实是先做线性回归再过 sigmoid。
> 但**用途是分类**，是工业界最常用的二分类基线模型。

#### 参数

- **`max_iter`**：最大迭代次数
  - 默认 100，**鸢尾花数据上不够会警告"未收敛"**，所以教程里设 200
  - Java 视角：类似设置 `Thread.sleep` 重试上限
- **`C`**：正则化强度的**倒数**（数值越小，正则化越强）
  - 默认 1.0，过拟合时调小（如 0.1）
- **`penalty`**：正则化类型，`'l2'`（默认）/ `'l1'` / `'elasticnet'`
- **`solver`**：优化算法，常用：
  - `'lbfgs'`（默认，小数据集快）
  - `'saga'`（大数据集 + L1）

#### 完整示例

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# 预测类别
y_pred = model.predict(X_test)
# 预测概率（每行加起来=1）
y_proba = model.predict_proba(X_test)
print(y_proba[:2])
# [[0.95 0.04 0.01],
#  [0.02 0.88 0.10]]   ← 3 个类别的概率
```

#### 拓展：还能拿到什么

```python
model.coef_         # 系数矩阵 (n_classes, n_features)
model.intercept_    # 截距 (n_classes,)
model.classes_      # 类别标签 [0, 1, 2]
```

---

### 待补充（Day2 会用到）

- `DecisionTreeClassifier(max_depth=...)` — 决策树
- `RandomForestClassifier(n_estimators=100)` — 随机森林
- `GradientBoostingClassifier()` / XGBoost — 梯度提升树
- `KNeighborsClassifier(n_neighbors=5)` — KNN
- `SVC(kernel='rbf')` — 支持向量机
- `GaussianNB()` — 朴素贝叶斯

### 待补充（Day3 会用到）

- `KMeans(n_clusters=3)` — K-Means 聚类
- `DBSCAN(eps=0.5, min_samples=5)` — 密度聚类
- `PCA(n_components=2)` — 主成分分析

---

## 四、模型通用 API（fit / predict / score）

**所有 sklearn 模型都有这 3 个方法**——这就是为什么换模型只需改一行代码。

### `model.fit(X_train, y_train)`

训练模型。

- **输入**：训练特征 + 训练标签
- **返回**：`self`（一般不接收）
- **副作用**：模型内部状态被更新（学到了规律）

```python
model.fit(X_train, y_train)
# 之后 model.coef_ 等内部属性才有值
```

> ⚠️ 常见误区：以为 `fit` 返回训练好的新模型 → `model = model.fit(...)`
> 虽然能跑（因为 `return self`），**但这是反模式**，约定上不接收返回值。

---

### `model.predict(X)`

预测类别标签（分类）或预测值（回归）。

- **输入**：特征矩阵 `(N, D)`
- **返回**：标签数组 `(N,)`

```python
y_pred = model.predict(X_test)
print(y_pred[:5])    # [1 0 2 1 1]   ← 类别下标
```

---

### `model.predict_proba(X)`（仅分类）

预测每个类别的**概率**。

- **返回**：概率矩阵 `(N, n_classes)`，**每行加起来=1**

```python
y_proba = model.predict_proba(X_test)
print(y_proba.shape)   # (30, 3)
print(y_proba.sum(axis=1))   # [1. 1. 1. ...]  ← 每行=1
```

#### `predict` vs `predict_proba` 的关系

```python
# predict 内部就是 argmax(predict_proba)
np.array_equal(
    y_pred,
    np.argmax(y_proba, axis=1)
)  # True
```

---

### `model.score(X, y)`

便捷方法，等价于 `accuracy_score(y, model.predict(X))`（分类）或 R² 分数（回归）。

```python
acc = model.score(X_test, y_test)
# 等价于
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
```

---

## 五、评估指标（`sklearn.metrics`）

### `accuracy_score(y_true, y_pred)`

分类准确率。

- **返回**：`float`，值在 `[0, 1]`

```python
from sklearn.metrics import accuracy_score

acc = accuracy_score(y_test, y_pred)
print(f"准确率：{acc:.2%}")    # 100.00%
```

#### 等价的 NumPy 写法

```python
import numpy as np
acc = (y_pred == y_test).mean()   # 一样的结果
```

---

### 待补充（Day4 会用到）

- `confusion_matrix(y_true, y_pred)` — 混淆矩阵
- `precision_score / recall_score / f1_score` — P/R/F1
- `classification_report(y_true, y_pred)` — 一份齐全报告
- `roc_auc_score` — AUC

---

## 六、待补充：Day2-Day5 会用到的 API

### Day 2 监督学习核心算法

```python
# 决策树
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(max_depth=5, random_state=42)

# 随机森林
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)

# KNN
from sklearn.neighbors import KNeighborsClassifier
model = KNeighborsClassifier(n_neighbors=5)
```

### Day 3 无监督学习与降维

```python
# K-Means
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X)

# PCA 降维
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)
```

### Day 4 模型评估与过拟合

```python
# 交叉验证
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
print(f"5 折准确率：{scores.mean():.2%} ± {scores.std():.2%}")

# 详细分类报告
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred, target_names=['类0', '类1', '类2']))
```

### Day 5 综合实战

可能用到的 Pipeline：

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=200))
])
pipe.fit(X_train, y_train)
acc = pipe.score(X_test, y_test)
```

---

## 🆘 常见疑惑速查

| 困惑 | 解法 |
|------|------|
| `train_test_split` 返回顺序记不住 | **X 前 y 后，train 前 test 后** |
| `LogisticRegression` 警告 "未收敛" | 加大 `max_iter`，比如 `max_iter=1000` |
| 想看每个类别的概率 | 用 `predict_proba()` 不要 `predict()` |
| 类别不平衡（如 95% vs 5%） | `train_test_split` 加 `stratify=y` |
| `fit()` 接不接返回值 | **不接**，约定俗成 |
| `random_state` 该不该设 | **永远要设**，否则结果不可复现 |
| 模型换了但接口要重学吗 | **不用**，sklearn 所有分类器都是 `fit/predict/score` |

---

## 📚 进阶资源

- sklearn 官方 cheatsheet：https://scikit-learn.org/stable/tutorial/machine_learning_map/
- sklearn 选模型流程图（必看一次）：根据数据量、是否有标签、是分类还是回归来推荐
- 已有更深笔记：`path-research/02-机器学习与深度学习/笔记/经典ML/`

---

> 📝 **维护说明**：本文档随 Week2 练习推进**渐进补充**。
> 当你做完每个 Day 的练习，回来对照检查"用到的 API 是否都在这里"。
