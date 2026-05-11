# 阶段 1 · 基础速通（3 周）

> 🎯 **目标**：能看懂 AI 代码 + 理解基本概念，**不求会写、不求深入**
>
> ⏱️ **周期**：3 周
>
> 🧭 **权重**：⭐⭐（仅为后续扫盲，不是重点）

---

## 📌 核心原则

> **够用就好。这阶段的目的是"扫盲"，不是"精通"。**

如果对某个知识点产生了"想深入研究"的冲动，**忍住**。等到阶段 3 实际做项目遇到时再回头补。

---

## 🗓️ 3 周分解

| 周 | 主题 | 状态 | 内容 |
|----|------|------|------|
| **Week 1** | [Python 速通](./Week1-Python速通/) ⭐ | ✅ **已开放** | 5 天教程 + 练习题，开箱即用 |
| **Week 2** | 经典 ML 扫盲 | ⏳ 待开放 | 复用 path-research 已有 Notebook |
| **Week 3** | 数学补盲 | ⏳ 待开放 | 只学 LLM 相关 |

---

## 🚀 Week 1 · Python 速通（已打磨完毕）

> 详见：[`Week1-Python速通/README.md`](./Week1-Python速通/README.md)

### 5 天计划速览

| 天 | 主题 | 教程 | 练习 |
|----|------|------|------|
| Day 1 | 基础语法（Java vs Python）| [📖 Day1](./Week1-Python速通/Day1-基础语法.md) | [📝 day1_练习.py](./Week1-Python速通/练习/day1_练习.py) |
| Day 2 | 数据结构（list/dict/set/tuple + 推导式）| [📖 Day2](./Week1-Python速通/Day2-数据结构.md) | [📝 day2_练习.py](./Week1-Python速通/练习/day2_练习.py) |
| Day 3 | 进阶（装饰器、上下文、异常、类型注解）| [📖 Day3](./Week1-Python速通/Day3-Python进阶.md) | [📝 day3_练习.py](./Week1-Python速通/练习/day3_练习.py) |
| Day 4 | NumPy 基础（shape、切片、矩阵运算）| [📖 Day4](./Week1-Python速通/Day4-NumPy基础.md) | [📝 day4_练习.py](./Week1-Python速通/练习/day4_练习.py) |
| Day 5 | 综合演练（**首次调用 LLM**）⭐ | [📖 Day5](./Week1-Python速通/Day5-综合演练.md) | [📝 day5_综合项目.py](./Week1-Python速通/练习/day5_综合项目.py) |

### 立即开始

```bash
# 1. 进入 Week 1 目录
cd path-engineer/01-基础速通/Week1-Python速通

# 2. 打开 README 看 5 天总览
cat README.md  # 或在 IDE 里打开

# 3. 开始 Day 1
cat Day1-基础语法.md
```

---

## 📚 Week 2 · 经典 ML 扫盲（计划）

> 状态：暂未开放（学完 Week 1 再来打磨）

### 计划内容
- Day 1-2：理解概念（监督/无监督/评估指标）
- Day 3：常见算法（决策树/随机森林/XGBoost/SVM）—— **认识就行**
- Day 4：跑通 path-research 已有 Notebook
- Day 5：欠拟合/过拟合（必懂）

### 已有资产（直接复用）

| 资产 | 位置 |
|------|------|
| 监督学习笔记 | `path-research/02-机器学习与深度学习/笔记/经典ML/监督学习.md` |
| 无监督学习笔记 | 同上目录 |
| 线性回归笔记 | 同上目录 |
| 鸢尾花 Notebook（含中文注释） | `path-research/02-机器学习与深度学习/代码/01_鸢尾花分类入门.ipynb` |
| 监督学习实战 Notebook | 同上目录 |

### 不学
- ❌ Kaggle 调参
- ❌ 复杂特征工程
- ❌ 树模型源码

---

## 📐 Week 3 · 数学补盲（计划）

> 状态：暂未开放

### 计划内容（**只学 LLM 相关**）
- Day 1-2：线性代数（向量内积、范数、矩阵乘法）
- Day 3：概率（条件概率、贝叶斯、高斯）
- Day 4：微积分（导数、梯度，**不推导反向传播**）
- Day 5：信息论（交叉熵、KL 散度）

### 已有资产
- `path-research/01-数学与编程基础/1.1-线性代数/` 已有完整笔记 + 80+ 练习题

### 不学
- ❌ 特征值分解 / SVD 推导
- ❌ 凸优化
- ❌ 概率统计检验

---

## ✅ 阶段完成标准

完成本阶段后，应该能做到：

- [ ] 看到一段 Python / PyTorch 代码，能猜出大概在做什么
- [ ] 看到一篇 AI 文章，能理解 80% 的术语
- [ ] 和算法同事能聊 10 分钟不露怯
- [ ] **调用过一次 LLM API**（Week 1 Day 5 已包含）
- [ ] **不再被"基础不够"焦虑感困扰**（这一点最重要）

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 2 · LLM 认知](../02-LLM认知/README.md)。

---

## 🔗 相关链接

- 📋 [path-engineer 主路径](../README.md)
- 🎓 [path-research（已有内容参考）](../../path-research/README.md)
- 📊 [岗位技能图谱](../../00-学习总览/AI大模型岗位技能图谱.md)
