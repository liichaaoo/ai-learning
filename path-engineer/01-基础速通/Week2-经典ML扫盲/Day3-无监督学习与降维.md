# Day 3 · 无监督学习与降维

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**理解"没标签时模型在干什么" + 会用 PCA 可视化数据**

---

## 🧭 今天的 3 个核心问题

1. **没有标准答案，模型凭什么"学习"？**
2. **聚类、降维、异常检测，分别解决什么问题？**
3. **为什么 AI 应用开发也要懂这些？**（剧透：RAG 的核心就用到"向量 + 相似度"）

---

## 一、无监督学习：没老师的学生

### 回顾：监督 vs 无监督

| 场景 | 有标签 | 典型任务 |
|------|-------|---------|
| 监督 | ✅ 有 | "这 1000 朵花是 setosa/versicolor/virginica"，预测第 1001 朵 |
| 无监督 | ❌ 没 | "这 1000 朵花，帮我分一下组"，让模型自己发现 setosa/versicolor/virginica |

**关键认知**：

> 无监督的"学习"，学的是**数据本身的结构**（哪些样本相似、哪些维度信息多）。
> 没人告诉它"对错"，它只能从数据的**内部规律**找答案。

---

## 二、无监督学习的三大任务

### 🎯 2.1 聚类（Clustering）

**一句话**：**把相似的样本分到同一组**。

**场景**：
- 用户分群（把 100 万用户分成 20 个群，做精准营销）
- 新闻聚类（自动发现热点话题）
- 图片去重（相似图片归一堆）

---

### 🎯 2.2 降维（Dimensionality Reduction）

**一句话**：**把高维数据"压扁"到低维，同时保留重要信息**。

**为什么要压**？
- 高维数据**画不出图**（你只能画 2D/3D）
- 高维度计算慢、占内存
- 高维度下距离不好定义（"维度灾难"）
- 很多维度是冗余的（"身高 cm" 和 "身高 m" 本质同一个信息）

**场景**：
- 把 1000 维的用户特征降到 2 维可视化
- 把 700+ 维的图片特征降到 50 维加速模型训练
- 给 AI 应用用的 **Embedding**（1024 维文本向量）降维

---

### 🎯 2.3 异常检测（Anomaly Detection）

**一句话**：**找出"不像大多数"的那些样本**。

**场景**：
- 信用卡盗刷检测（99.9% 交易正常，找那 0.1% 异常）
- 服务器异常监控
- 工厂生产次品检测

---

## 三、聚类算法名片（3 张）

### 🃏 名片 1：K-Means ⭐

```
直觉:   你告诉它"分成 K 组"
       它先随机选 K 个"中心点"
       然后重复：
         1. 把每个样本归到离它最近的中心
         2. 把中心移到这组样本的均值位置
       直到中心不再动
优点:   - 简单、快
缺点:   - 必须预先指定 K（你怎么知道分几组？）
        - 只认"球形"簇，遇到月牙形/环形分布就傻
        - 对初始值敏感
适用:   - 快速分群、baseline
        - 数据分布"大概是球形"时
sklearn: KMeans(n_clusters=K)
```

### 🃏 名片 2：DBSCAN

```
直觉:   "基于密度"的聚类
       某个点周围 eps 半径内至少有 min_samples 个邻居 → 核心点
       核心点连着的算一簇
       没人跟它玩的 → 异常点
优点:   - 不用预先指定 K
        - 能识别任意形状（月牙、环形都行）
        - 自动识别异常点
缺点:   - 参数 eps 和 min_samples 不好调
        - 高维数据上效果差
适用:   - 空间数据聚类（地理位置）
        - 需要找异常点时
sklearn: DBSCAN(eps=0.5, min_samples=5)
```

### 🃏 名片 3（选学）：层次聚类（Hierarchical Clustering）

```
直觉:   像"建族谱"
       从每个样本各自一组开始
       每次把"最像的两组"合并
       最后画出一棵"树状图"，你决定在哪一层切开
优点:   - 不用指定 K，切哪层得几个簇
        - 能看到"簇的演化过程"
缺点:   - 慢，O(n²) 起步，大数据跑不动
适用:   - 生物分类、文档聚类
sklearn: AgglomerativeClustering()
```

---

## 四、降维算法名片（2 张）

### 🃏 名片 1：PCA（主成分分析）⭐

```
直觉:   找到数据中"方差最大的方向"，投影下去
       就像给一堆点做"最佳视角"的拍照
优点:   - 快、稳定、可解释
        - 有明确的数学解（线性代数的特征值分解）
缺点:   - 只能线性降维
        - 对缩放敏感（用前要标准化）
适用:   - 降维可视化（降到 2D/3D）
        - 给后续 ML 算法加速（降到 50 维再训练）
        - Baseline（不知道用啥先试 PCA）
sklearn: PCA(n_components=2)
```

### 🃏 名片 2：t-SNE / UMAP

```
直觉:   非线性降维，特别擅长"保留局部结构"
       适合把高维 embedding 降到 2D 做可视化
优点:   - 可视化效果惊艳（簇很清晰）
        - UMAP 比 t-SNE 快很多
缺点:   - 不稳定（每次跑结果可能不同）
        - 只适合可视化，不适合当特征给下游模型
        - 慢（t-SNE 尤其）
适用:   - 展示 word embedding、图像特征
        - 论文里的漂亮图
sklearn: TSNE(n_components=2)
        (UMAP 不在 sklearn，需 pip install umap-learn)
```

> 💡 **你要记住的对比**：
> - **PCA**：工程主力，速度快，可复现
> - **t-SNE/UMAP**：可视化神器，只画图别当特征

---

## 五、与 AI 应用的关系（重点！）⭐⭐

这里是和你未来工作最相关的一段，**仔细看**。

### 5.1 Embedding = 一种"自动降维"

你后面要做 RAG（检索增强生成）的时候，会大量接触这个：

```python
# 用文本 embedding 模型，把一段话转成 1024 维向量
text = "苹果公司发布了新手机"
embedding = model.encode(text)  # shape=(1024,)
```

这个 1024 维向量就是**那段话的语义表示**。**本质上就是无监督学到的**。

### 5.2 向量相似度 = 聚类的底层逻辑

RAG 的"检索"做的事：

```python
# 1. 把用户问题转成向量
query_vec = encode("苹果公司最新动态")

# 2. 和知识库里所有文档向量算相似度
for doc_vec in all_docs:
    similarity = cosine_similarity(query_vec, doc_vec)

# 3. 取最相似的 Top-K 文档
```

**这个"找相似"的思路，就是 KNN / K-Means 的内核**。
所以学了今天的内容，你就理解了 RAG 检索的**底层直觉**。

### 5.3 PCA 可以给向量库"瘦身"

生产中有时为了加速，会用 PCA 把 1024 维降到 256 维再入库：
```python
pca = PCA(n_components=256)
small_vecs = pca.fit_transform(big_vecs)  # 1024 → 256
```

---

## 六、可运行示例：聚类 + 降维（鸢尾花）

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# 加载数据
X, y_true = load_iris(return_X_y=True)
target_names = load_iris().target_names

# 1. 降维：4维 → 2维（方便画图）
X_std = StandardScaler().fit_transform(X)
X_2d = PCA(n_components=2).fit_transform(X_std)

# 2. 聚类（假装不知道标签，让它自己分 3 组）
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
y_pred = kmeans.fit_predict(X_std)

# 3. 画图对比
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图：真实标签
for i, name in enumerate(target_names):
    axes[0].scatter(X_2d[y_true == i, 0], X_2d[y_true == i, 1], label=name)
axes[0].set_title("真实标签（监督视角）")
axes[0].legend()

# 右图：K-Means 结果
for i in range(3):
    axes[1].scatter(X_2d[y_pred == i, 0], X_2d[y_pred == i, 1], label=f"Cluster {i}")
axes[1].set_title("K-Means 聚类（无监督视角）")
axes[1].legend()

plt.tight_layout()
plt.show()
```

**看图时你会发现**：
- 两张图**长得非常像**
- K-Means 不知道"花名"，但它能按形态把花分成 3 组
- **这就是无监督的能力**：从数据本身发现结构

---

## 七、常见困惑解答

### Q1：无监督学习怎么评估好坏？没标签啊？

A：**很难**。常用几种：
- **轮廓系数**（Silhouette）：数字 -1~1，越大越好
- **肘部法则**（Elbow Method）：选合适的 K
- **业务解释**：聚出来的群，人工看看合不合理
- **事后有标签**：如果后面能拿到部分标签，对比一下

"无监督难评估"是它的天然痛点。

---

### Q2：聚类 vs 分类差在哪？

```
聚类：模型自己发现"有 3 种类型"，类型叫什么不知道
分类：你告诉模型"有 setosa/versicolor/virginica 3 类"，让它学
```

---

### Q3：PCA 和 t-SNE 选哪个？

| 用途 | 选谁 |
|------|-----|
| 给下游模型加速（特征降维） | **PCA** |
| 只是画个漂亮图给老板看 | **t-SNE / UMAP** |
| 不确定先试 | **PCA**（快、稳定） |

---

## 📚 延伸阅读

- [path-research 无监督学习.md](../../../path-research/02-机器学习与深度学习/笔记/经典ML/无监督学习.md)（已有详细笔记）

---

## ✍️ 本日练习

完成 [`练习/day3_练习.py`](./练习/day3_练习.py)：
- 聚类 vs 分类概念题
- 场景选型
- K-Means + PCA 可视化代码（可运行）

---

## 🎯 今日收官清单

- [ ] 我能说出聚类、降维、异常检测各自干嘛
- [ ] K-Means 和 DBSCAN 的核心区别我能说 1 条
- [ ] PCA 的作用我能用大白话解释
- [ ] 我理解"embedding = 自动降维 + 聚类的组合"
- [ ] 我知道 RAG 检索的底层就是"向量相似度"

---

## 🔖 下一步

明天 → [Day 4：模型评估与过拟合](./Day4-模型评估与过拟合.md)
