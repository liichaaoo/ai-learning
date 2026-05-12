# Day 5 · 综合实战：Notebook 精读与改造

> ⏱️ 目标时间：1.5-2 小时（周末做）
> 🎯 产出：**跑通并改造 2 份 Notebook，写一篇小结**

---

## 🧭 今天的主线

前 4 天是"学概念"。**今天是"用手把概念跑一遍"**。

不再写新教程，直接用你之前已经整理好的两份 Notebook 做精读：

| Notebook | 路径 | 重点 |
|----------|------|-----|
| **Notebook 1（入门）** | [`path-research/02-机器学习与深度学习/代码/01_鸢尾花分类入门.ipynb`](../../../path-research/02-机器学习与深度学习/代码/01_鸢尾花分类入门.ipynb) | 完整走一遍 7 步流程（Day 1 内容） |
| **Notebook 2（进阶）** | [`path-research/02-机器学习与深度学习/代码/02_监督学习实战_鸢尾花.ipynb`](../../../path-research/02-机器学习与深度学习/代码/02_监督学习实战_鸢尾花.ipynb) | 多算法对比 + 交叉验证 + 过拟合（Day 2-4 内容） |

---

## 📋 今天分 3 部分

### Part 1：启动环境（10 分钟）

确认你的 Jupyter 环境能用。如果之前跑过就跳过。

```bash
# 1. 进入项目目录
cd /Users/fletcherli/CodeBuddy/20260228220331/ai-learning

# 2. 启动 JupyterLab
bash start_jupyter.sh
# 或者 python3 -m jupyter lab
```

浏览器打开后，去 `path-research/02-机器学习与深度学习/代码/`。

---

### Part 2：精读 Notebook 1（30 分钟）⭐

**打开**：`01_鸢尾花分类入门.ipynb`

**任务清单**（一边看代码一边在脑中对应概念）：

- [ ] **Cell 1（导入）**：认出所有 import，和前 4 天学的对应
  - `train_test_split` → Day 1 的"划分数据集"
  - `StandardScaler` → Day 4 提到的"标准化"
  - `LogisticRegression` → Day 2 第 2 张名片
  - `confusion_matrix / classification_report` → Day 4 的评估
  - `PCA` → Day 3 的降维

- [ ] **Cell 2（加载数据）**：回答
  - 有几个样本？ 答：___
  - 有几个特征？ 答：___
  - 有几个类别？ 答：___

- [ ] **Cell 3（PCA 可视化）**：观察图
  - 三类能分开吗？
  - 哪两类容易混？（Day 3 的"数据内部结构"）

- [ ] **Cell 4（划分数据）**：注意 `stratify=y`
  - 不加会怎样？试试改成 `stratify=None`，看结果有没有变化

- [ ] **Cell 5（标准化）**：对照 Day 4 讲的
  - 为什么训练集用 `fit_transform` 而测试集用 `transform`？
  - 答：防止数据泄漏（测试集不能参与 scaler 的"学习"）

- [ ] **Cell 6-7（训练 & 评估）**：对照 Day 2 和 Day 4
  - 训练集准确率 vs 测试集准确率
  - 分类报告里每个数字的含义（用 Day 4 学的解读）

- [ ] **Cell 8（混淆矩阵）**：对照 Day 4 画的矩阵
  - 对角线上的数字表示什么？
  - 非对角线上的数字表示什么？

- [ ] **Cell 9（单点预测）**：这就是"模型部署"的最简版

---

### Part 3：挑战 Notebook 2（60 分钟）

**打开**：`02_监督学习实战_鸢尾花.ipynb`

**这份 Notebook 几乎把 Week 2 全部内容都用上了**。一边跑一边把下面问题的答案写在周报里：

- [ ] **多算法对比**：哪个算法准确率最高？
- [ ] **Pipeline + 交叉验证**：为什么要用 Pipeline？
  - 答：防止 scaler 在交叉验证时把测试集信息泄漏到训练
- [ ] **GridSearchCV**：调参自动化
  - 观察最优参数是什么
  - 试着改一下参数范围，看会不会更好
- [ ] **学习曲线**：观察"过拟合 vs 正常"的对比图
  - `max_depth=None` 和 `max_depth=3` 的学习曲线差别在哪？
  - 这就是 Day 4 讲的过拟合的可视化
- [ ] **特征重要性**：看看随机森林认为哪些特征重要
  - 这是决策树/树模型特有的"可解释性"能力

---

## 🛠️ 挑战任务（做完会印象深刻）

### 挑战 1：改模型看差异 ⭐

把 Notebook 1 的：
```python
model = LogisticRegression(max_iter=200)
```
改成：
```python
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(max_depth=3)
```
再完整跑一遍。对比：
- 准确率有变化吗？
- 混淆矩阵错的位置还一样吗？
- 如果不设 `max_depth`，训练集会到 100% 吗？（**过拟合预警**）

### 挑战 2：类别不平衡 ⭐⭐

用下面代码**人为制造类别不平衡**：

```python
import numpy as np
# 只保留 20% 的 setosa，制造类别不平衡
mask_keep = (y != 0) | (np.random.rand(len(y)) < 0.2)
X_imba = X[mask_keep]
y_imba = y[mask_keep]
print(f"不平衡后各类数量: {np.bincount(y_imba)}")
```

然后重新训练，观察：
- 整体准确率 Accuracy
- 各类的 Precision/Recall/F1（对照 Day 4）
- setosa 类会不会 Recall 特别低？

这就是你在信用卡盗刷场景会遇到的**真实问题**。

### 挑战 3：用 K-Means 替代分类 ⭐⭐

假装你没有标签，对鸢尾花做 K-Means 聚类（K=3），然后对比聚类结果和真实标签：
```python
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
y_pred = kmeans.fit_predict(X_std)

# 看看聚类分组和真实标签能不能对上（虽然标签编号不一定一致）
from sklearn.metrics import confusion_matrix
print(confusion_matrix(y_true, y_pred))
```

这就是 Day 3 讲的"无监督发现数据结构"。

---

## ✍️ 今日产出要求

在你的**周报（W20）**里加一段"Week 2 学习小结"：

```markdown
## Week 2 学习小结

### 学到了什么（3-5 个关键点）
- ...
- ...

### 最难理解的概念（1-2 个）
- ...

### 挑战任务做了哪几个 + 观察到什么
- ...

### 还没搞懂，想继续深挖的问题
- ...
```

这段写到**周报里**，不另起文件。

---

## 🎯 本周的"出关自测"

回到 Week 2 总 [README.md](./README.md) 的"出关自测"部分，**闭卷答 10 道题**。

**能答出 7+ 题** → 恭喜，Week 2 通关，准备进入 Week 3（数学补盲）
**低于 7 题** → 回头看对应 Day 的教程

---

## 🎯 今日收官清单

- [ ] Notebook 1 完整跑通 + 能解读每一步
- [ ] Notebook 2 跑通 + 理解 Pipeline + 交叉验证 + 学习曲线
- [ ] 完成至少 1 个挑战任务
- [ ] 周报里补了 Week 2 学习小结
- [ ] 10 道出关自测答对 7+ 题

---

## 🎉 完成 Week 2 后，你已经具备：

- ✅ 能用大白话给人讲清楚 ML 是啥
- ✅ 能识别 7 张算法名片
- ✅ 能看懂 sklearn 代码每一步在干啥
- ✅ 能解读分类报告和混淆矩阵
- ✅ 能回答"过拟合"面试题
- ✅ **理解了 RAG 底层的"向量 + 相似度"哲学**（无监督的延伸）

**这足够你：**
- 应对大部分面试里的"ML 基础"部分
- 和算法同事无障碍沟通
- 看懂任何 AI 应用代码中的 ML 相关片段

---

## 🔖 下一步

- 本周末 → 写周报，总结
- 下周 → Week 3 · 数学补盲（只学 LLM 相关）
- 两周后 → 阶段 2 LLM 认知

加油，你正在走一条**非常高效的路径**。
