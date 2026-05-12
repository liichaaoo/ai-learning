# Day 2 · 监督学习核心算法

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**7 张算法"名片"能复述 + 会选算法**

---

## 🧭 今天你要解决的问题

面试官问："你大概知道几个 ML 算法？什么场景用哪个？"
你能张口就来 5-7 个，讲清楚它的**直觉、优缺点、适用场景**。

**不学**：算法数学推导、自己实现代码。

---

## 📋 7 张"算法名片"

下面 7 个是**你必须能识别的**，每个配一张 30 秒就能读完的名片。

---

### 🃏 名片 1：线性回归（Linear Regression）

```
类型:   监督学习 · 回归
直觉:   找一条"最能穿过所有点"的直线（或高维超平面）
公式:   y = w₁x₁ + w₂x₂ + ... + wₙxₙ + b
      （Java 程序员：就是 n 个系数相乘再相加的线性组合）
优点:   - 最简单、可解释性强（能看出每个特征的贡献）
        - 训练快
缺点:   - 只能拟合线性关系，数据弯弯曲曲就不行
适用:   - 预测连续数值（房价、销量、气温）
        - Baseline（基准模型）
sklearn: LinearRegression()
```

### 🃏 名片 2：逻辑回归（Logistic Regression）⭐

```
类型:   监督学习 · 分类（别被名字骗了！）
直觉:   给线性回归套一个 S 型函数，把输出压到 0-1 之间当概率
公式:   p = 1 / (1 + e^(-z))  其中 z 是线性组合
优点:   - 可解释、训练快
        - 输出是概率，方便设阈值
缺点:   - 只能处理线性可分问题
适用:   - 二分类（垃圾邮件、点击预测、风控）
        - 多分类（鸢尾花那种）
sklearn: LogisticRegression()
```

> 🎯 **为啥这个重要**：**面试必考**。工业界最常见的 baseline，讲不清=扣分。
>
> 💡 **常见坑**：名字有"回归"但是干分类的。"逻辑"是 logistic（S 型函数）的音译。

---

### 🃏 名片 3：决策树（Decision Tree）

```
类型:   监督学习 · 分类 & 回归都可以
直觉:   就是一堆 if/else 嵌套，每层问一个问题，叶子节点是答案
        ├─ 年龄 > 30？
        │  ├─ 是 → 收入 > 1 万？
        │  │   ├─ 是 → 会买
        │  │   └─ 否 → 不买
        │  └─ 否 → 不买
优点:   - 最直观、最像人思考
        - 不需要标准化数据
        - 可解释性极强（能画出来给老板看）
缺点:   - 单棵树容易过拟合
        - 对数据微小变化敏感（换一批数据树结构就变）
适用:   - 需要解释模型决策的场景（金融风控、医疗）
        - 特征有明显阈值含义时
sklearn: DecisionTreeClassifier() / DecisionTreeRegressor()
```

---

### 🃏 名片 4：随机森林（Random Forest）⭐

```
类型:   监督学习 · 分类 & 回归
直觉:   种 100 棵决策树，让它们投票（分类）或取平均（回归）
        每棵树只用部分数据 + 部分特征（这叫 Bagging + 随机特征）
优点:   - 比单棵决策树准得多
        - 不怎么过拟合
        - 能告诉你"哪些特征最重要"
缺点:   - 大数据时慢
        - 内存占用大
适用:   - 结构化数据（表格数据）的默认首选
        - 实在不知道用啥就用它
sklearn: RandomForestClassifier() / RandomForestRegressor()
```

> 🎯 **工业界名言**："不知道用什么，先用随机森林。"

---

### 🃏 名片 5：XGBoost / LightGBM（梯度提升树）⭐⭐⭐

```
类型:   监督学习 · 分类 & 回归
直觉:   一棵一棵依次加决策树，每棵树专门"弥补"上一棵的错误
       （随机森林是"并行投票"，这个是"串行改错"）
优点:   - 准确率通常比随机森林还高
        - 工业界 & Kaggle 竞赛霸主
        - 处理缺失值、分类特征都很好
缺点:   - 参数多、调参门槛高
        - 训练比随机森林慢
适用:   - 结构化数据的 SOTA（截至 2024 仍然是）
        - 比赛、线上业务模型首选
第三方库: XGBoost、LightGBM、CatBoost（三选一即可）
        （不是 sklearn 自带，pip install xgboost）
```

> 🎯 **你要记住这三个字母**：**XGBoost**。面试常问、实际工作会用。

---

### 🃏 名片 6：K 近邻（KNN）

```
类型:   监督学习 · 分类 & 回归
直觉:   来了个新点，看它最近的 K 个邻居是啥类别，就判成啥类别
        （像问你周围 5 个朋友支持哪个队来判断你支持哪个队）
优点:   - 超简单，没什么要"训练"的
        - 非参数方法，没假设数据分布
缺点:   - 预测慢（每次要跟所有训练数据算距离）
        - 对高维数据、对无关特征敏感
适用:   - 小数据集
        - 推荐系统的某些场景
sklearn: KNeighborsClassifier(n_neighbors=5)
```

---

### 🃏 名片 7：支持向量机（SVM）

```
类型:   监督学习 · 分类（主要）
直觉:   找一条分隔线（超平面），让两类数据的"安全距离"最大
优点:   - 高维数据效果好（文本分类曾经的王者）
        - 小样本也能训练
缺点:   - 大数据集慢、难调参
        - 不容易输出概率
适用:   - 传统的文本分类（现在被神经网络挤压）
        - 特征多、样本少的场景
sklearn: SVC()（分类）/ SVR()（回归）
```

---

### 🃏 名片 8（选学）：朴素贝叶斯（Naive Bayes）

```
类型:   监督学习 · 分类
直觉:   算"这句话里出现"中奖"" × "出现"转账"" × ... 的条件概率乘积
        每个特征当作"独立"（所以叫"朴素"）
优点:   - 极快，在线学习也 OK
        - 文本分类老朋友
缺点:   - "特征独立"的假设经常不成立
适用:   - 垃圾邮件分类、新闻分类
        - 数据量极小时
sklearn: MultinomialNB()
```

---

## 🗺️ 算法"地图"总览

```
你有标签 → 监督学习
│
├── 任务是分类（预测类别）
│   ├── 要解释性 → 决策树
│   ├── 要快速 baseline → 逻辑回归
│   ├── 结构化数据要准 → 随机森林 / XGBoost ⭐
│   ├── 文本 → 朴素贝叶斯 / SVM
│   └── 不知道用啥 → 随机森林
│
└── 任务是回归（预测数值）
    ├── 简单场景 → 线性回归（基准）
    └── 复杂场景 → 随机森林 / XGBoost ⭐
```

**你记住这张图，90% 的结构化数据 ML 场景就能选对算法了。**

---

## 🎯 sklearn 的统一 API（调包侠的春天）

**一个好消息**：上面所有算法，**sklearn 里都是同一套 API**。

```python
from sklearn.xxx import SomeModel

model = SomeModel()           # 1. 创建
model.fit(X_train, y_train)   # 2. 训练
y_pred = model.predict(X_test) # 3. 预测
score = model.score(X_test, y_test) # 4. 评估（准确率）
```

想换算法？**改一行 import 就行**：

```python
# from sklearn.linear_model import LogisticRegression as Model
# from sklearn.tree import DecisionTreeClassifier as Model
# from sklearn.ensemble import RandomForestClassifier as Model
from xgboost import XGBClassifier as Model   # XGBoost 也差不多

model = Model()
model.fit(X_train, y_train)  # 后面完全一样
```

**Java 类比**：就像 Spring 的 `BeanFactory`，不管底层是啥实现，你都是 `getBean()`。

---

## 🧪 实际对比代码（跑一遍有感觉）

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    "逻辑回归":      LogisticRegression(max_iter=200),
    "决策树":        DecisionTreeClassifier(random_state=42),
    "随机森林":      RandomForestClassifier(random_state=42),
    "KNN(k=5)":     KNeighborsClassifier(),
    "SVM":          SVC(),
    "朴素贝叶斯":    GaussianNB(),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"{name:10s}: {acc:.4f}")
```

**预期输出**（鸢尾花数据集比较简单，大家都很高）：
```
逻辑回归:   1.0000
决策树:     1.0000
随机森林:   1.0000
KNN(k=5):  1.0000
SVM:       1.0000
朴素贝叶斯: 0.9667
```

> 💡 **启发**：简单数据集上"算法差异很小"，**真正拉开差距的是数据质量和特征工程**。

---

## 📚 延伸阅读（真想深入某个算法再看）

本次 Week 2 的级别**不需要读这些**，但给你标好位置以备未来：

| 主题 | 路径 |
|------|------|
| **监督学习全景笔记** | [path-research/02-机器学习与深度学习/笔记/经典ML/监督学习.md](../../../path-research/02-机器学习与深度学习/笔记/经典ML/监督学习.md) |
| **线性回归深入** | [path-research/.../线性回归.md](../../../path-research/02-机器学习与深度学习/笔记/经典ML/线性回归.md) |

---

## ✍️ 本日练习

完成 [`练习/day2_练习.py`](./练习/day2_练习.py)：
- 算法名片填空
- 算法选择题
- sklearn 代码跑一遍对比

---

## 🎯 今日收官清单

- [ ] 我能说出 7 个监督学习算法的名字
- [ ] 每个算法能说 1 句"直觉描述" + 1 个"适用场景"
- [ ] 我知道为什么"逻辑回归"叫回归但做分类
- [ ] 我知道"不知道用啥先用随机森林"
- [ ] 我听到 XGBoost 不会一脸懵
- [ ] 我知道 sklearn 的统一 API：fit / predict / score

---

## 🔖 下一步

明天 → [Day 3：无监督学习与降维](./Day3-无监督学习与降维.md)
