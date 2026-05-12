# Day 4 · 模型评估与过拟合

> ⏱️ 目标时间：1.5 小时
> 🎯 产出：**看得懂分类报告 + 能回答"过拟合是啥、怎么办"**

---

## 🧭 今天的 3 个核心问题

1. **怎么知道一个模型"好不好"？**（光看准确率远远不够）
2. **为什么模型在训练集完美，上线就拉垮？**（过拟合）
3. **交叉验证、正则化、调参，这些词都在说啥？**

> ⚠️ 本节是**本周最重要**的一节。面试、工作中遇到 ML 相关的问题，一大半是在问评估与过拟合。

---

## 一、为什么"准确率"不够用？

### 场景：信用卡盗刷检测

数据里 99% 是正常交易，1% 是盗刷。你训练了一个模型：

```python
def predict_model(transaction):
    return "正常"  # 永远预测"正常"
```

**这个"智障模型"的准确率 = 99%**！
- 因为 99% 的真实样本本来就是正常的
- 全预测正常，也就猜对了 99%

但这模型**毫无用处** —— 没检测出任何盗刷。

### 结论

**单看准确率（Accuracy）会骗人**，尤其是类别不平衡时。

> 🎯 记住这个：**类别不平衡场景下，准确率是个谎**。

---

## 二、混淆矩阵 Confusion Matrix ⭐

对于二分类（以"判断是否盗刷"为例）：

```
                  真实情况
                 盗刷    正常
预测  盗刷       TP       FP
为    正常       FN       TN
```

| 缩写 | 英文全称 | 含义 | 例子（盗刷检测） |
|------|---------|------|----------------|
| **TP** | True Positive | 真正例 | 真盗刷，预测盗刷 ✅ |
| **FP** | False Positive | 假正例 | 正常交易，被当盗刷 ⚠️（误伤用户）|
| **FN** | False Negative | 假反例 | 真盗刷，没检测出 ❌（漏网！）|
| **TN** | True Negative | 真反例 | 正常交易，预测正常 ✅ |

> 💡 **记忆技巧**：
> - 第一个字母 T/F：**预测对不对**
> - 第二个字母 P/N：**预测结果是啥**（正/负）
>
> 比如 FN = F(预测错了) + N(预测为负) = 预测为负但错了 = 真实是正

---

## 三、核心指标（必须记住 4 个）

### 3.1 准确率 Accuracy

```
Accuracy = (TP + TN) / (TP + FP + FN + TN)
        = 预测对的 / 总数
```

**缺陷**：类别不平衡时没用（见上面"智障模型"）。

---

### 3.2 精确率 Precision（查准率）

```
Precision = TP / (TP + FP)
        = 预测为"盗刷"的里，真的是盗刷的比例
```

**什么时候关注**：**误伤成本高**的场景
- 反垃圾邮件：把正常邮件误判为垃圾 → 用户骂娘
- 疾病初筛：正常人被说有病 → 吓个半死 + 花冤枉钱做复检

---

### 3.3 召回率 Recall（查全率）

```
Recall = TP / (TP + FN)
      = 所有真盗刷里，被你检出的比例
```

**什么时候关注**：**漏检成本高**的场景
- 盗刷检测：漏掉一笔，真金白银损失
- 癌症筛查：漏诊 → 延误治疗

---

### 3.4 F1 分数

```
F1 = 2 * Precision * Recall / (Precision + Recall)
   ≈ Precision 和 Recall 的"平均"（调和平均）
```

**什么时候用**：
- **Precision 和 Recall 同等重要时**，用 F1 综合评估
- 面试标准答案："类别不平衡时用 F1 而不是 Accuracy"

---

### 🎯 Precision vs Recall 经典对比

想象你是医生，要判断病人是不是得了癌症：

| 策略 | Precision | Recall | 问题 |
|------|-----------|--------|------|
| 宁可错杀一千，不放过一个 | 低 | 高 | 很多人被虚惊，过度医疗 |
| 宁可放过一千，绝不冤枉一个 | 高 | 低 | 漏诊，耽误治疗 |
| **都要兼顾** | 中 | 中 | F1 高，平衡 |

---

## 四、ROC / AUC（听过就行，不展开）

```
ROC 曲线:  x轴=FPR（假阳性率），y轴=TPR（真阳性率 = Recall）
          画出不同阈值下的权衡曲线

AUC:      ROC 曲线下的面积
          0.5 = 瞎猜，1.0 = 完美
          一般 > 0.8 算不错
```

**你要记的一句话**：**AUC 是"模型整体排序能力"的综合指标**，受类别不平衡影响较小。

---

## 五、分类报告（看懂就够了）⭐

sklearn 的 `classification_report()` 输出长这样：

```
               precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        10
  versicolor       0.90      0.90      0.90        10
   virginica       0.90      0.90      0.90        10

    accuracy                           0.93        30
   macro avg       0.93      0.93      0.93        30
weighted avg       0.93      0.93      0.93        30
```

怎么读：
- 每行是一个类别的 P/R/F1
- **support** 是这个类别的样本数
- **macro avg** = 简单平均（各类平等）
- **weighted avg** = 按样本数加权平均

**对类别不平衡场景，重点看 macro avg！**

---

## 六、过拟合 vs 欠拟合 ⭐⭐⭐

### 6.1 什么是过拟合

```
训练集准确率:  99%   ← 看起来完美
测试集准确率:  60%   ← 上线傻眼
```

模型把**训练数据的噪声也当成规律学了**，就像学生死记硬背了习题答案，换个题就不会。

### 6.2 什么是欠拟合

```
训练集准确率:  65%   ← 训练就没学好
测试集准确率:  60%   ← 上线也一般
```

模型太简单，规律都没学到。

### 6.3 一图看懂

```
简单模型  ←————————————————————→  复杂模型

 欠拟合     恰到好处（目标区）     过拟合
  ↓              ↓                   ↓
训练差           训练好               训练好
测试差           测试好               测试差
```

---

## 七、如何判断过拟合？

**方法 1：对比训练集和测试集分数**

```python
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"训练: {train_score:.3f}, 测试: {test_score:.3f}")

# 诊断:
# 差距 < 5%:   正常
# 差距 > 10%:  过拟合
# 都很差:      欠拟合
```

**方法 2：看学习曲线（Learning Curve）**

随着训练数据增加，训练分数和测试分数如何变化。

---

## 八、怎么解决过拟合？⭐

按优先级记这 5 个方法：

### 1. 增加训练数据（最有效但最难）
- 数据多了，噪声被平均，规律浮出水面
- 工业界：80% 的过拟合用"加数据"能解

### 2. 简化模型
- 决策树限制 `max_depth=5`
- 随机森林少点树
- 逻辑回归加正则化

### 3. 正则化（L1/L2）

```python
LogisticRegression(C=0.1)   # C 越小 → 正则化越强
```

**直觉**：惩罚模型的"复杂度"（权重绝对值之和），逼它用尽量简单的权重。

- **L1 正则化**：会把不重要的特征权重直接置 0（自带特征选择）
- **L2 正则化**：让所有权重都变小但不为 0（大多默认用这个）

### 4. 交叉验证（Cross Validation）

**问题**：只划一次 train/test，运气差的话划分不均衡。

**解法**：K 折交叉验证
```
把数据分 5 份：
Fold 1: [验证] [训练] [训练] [训练] [训练]
Fold 2: [训练] [验证] [训练] [训练] [训练]
Fold 3: [训练] [训练] [验证] [训练] [训练]
Fold 4: [训练] [训练] [训练] [验证] [训练]
Fold 5: [训练] [训练] [训练] [训练] [验证]

跑 5 次，取 5 次分数的平均
```

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
print(f"5 折准确率: {scores.mean():.3f} ± {scores.std():.3f}")
```

### 5. 早停 / 集成 / Dropout（深度学习常用，本周略过）

---

## 九、超参数 vs 参数（别搞混）

- **参数**（Parameter）：**模型训练出来的**，比如线性回归的系数 w
- **超参数**（Hyperparameter）：**你手动设定的**，比如 K-Means 的 K、决策树的 max_depth

**超参数怎么选？** → **Grid Search**（网格搜索）

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 10, None]
}
grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid.fit(X_train, y_train)
print(grid.best_params_)
```

GridSearch 会帮你**自动把所有组合都试一遍**，选最优的那组。

---

## 十、完整的"正确"训练流程 ⭐

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# 1. 划分数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 2. 用 Pipeline 串联"预处理 + 模型"（防数据泄漏）
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(random_state=42))
])

# 3. 网格搜索 + 交叉验证
param_grid = {'clf__n_estimators': [50, 100], 'clf__max_depth': [3, 5, None]}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring='f1_macro', n_jobs=-1)
grid.fit(X_train, y_train)

# 4. 用最优模型预测测试集
best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)

# 5. 看详细报告
print(f"最佳参数: {grid.best_params_}")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

**本周你不用能写出来**，但**你要能看懂每一步对应的概念**。

---

## 📚 延伸阅读

`path-research/02-机器学习与深度学习/代码/02_监督学习实战_鸢尾花.ipynb` 里有**过拟合可视化对比**（学习曲线），明天精读 Notebook 时会看到。

---

## ✍️ 本日练习

完成 [`练习/day4_练习.py`](./练习/day4_练习.py)：
- 场景题：选 Precision 还是 Recall
- 混淆矩阵计算
- 交叉验证实操

---

## 🎯 今日收官清单

- [ ] 我能画出混淆矩阵并说明 TP/FP/FN/TN
- [ ] 我能说出 Precision vs Recall 各自关注什么
- [ ] 我知道为什么不平衡数据不能只看 Accuracy
- [ ] 我能描述过拟合和欠拟合
- [ ] 我至少能说出 3 种解决过拟合的方法
- [ ] 我理解交叉验证是为什么（防止划分不均衡）
- [ ] 我能区分参数和超参数

---

## 🔖 下一步

明天 → [Day 5：综合实战（鸢尾花 Notebook 精读）](./Day5-综合实战.md)
