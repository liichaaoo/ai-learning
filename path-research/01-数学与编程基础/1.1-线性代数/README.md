# 1.1 线性代数

> 核心知识点：**向量、矩阵、张量、特征值分解**
> 周期：约 2 周｜目标：建立几何直觉 + NumPy 实操能力

---

## 学习目标

完成本节后你应该能够：
- 用几何视角解释向量、矩阵乘法、特征向量
- 用 NumPy 完成所有基础运算
- 用 einsum 写出复杂张量运算
- **不调用 sklearn 手写 PCA**

> 🎯 **配套练习题**：[练习题/README.md](./练习题/README.md) — 7 章 80+ 道题 + 4 个综合项目

---

## 视频课程（强烈推荐先看）

### 入门首选
| 资源 | 时长 | 备注 |
|------|------|------|
| ⭐ [3Blue1Brown《线性代数的本质》](https://www.bilibili.com/video/BV1ys411472E) | 16 集 / 3h | **必看，几何直觉拉满** |
| [YouTube 原版](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) | — | 英文原版 |
| 李永乐《线性代数》 | — | 中文系统讲解 |

### 系统课程
| 资源 | 适合 |
|------|------|
| [MIT 18.06 — Gilbert Strang](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) | 想深入理解 |
| ⭐ [MIT 18.065 — Strang（矩阵方法）](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/) | **AI 方向首选** |
| [CS229 线代速查](http://cs229.stanford.edu/section/cs229-linalg.pdf) | 快速复习 |

---

## 书籍

### 入门
- 📘 **《线性代数应该这样学》(Linear Algebra Done Right)** — Sheldon Axler
  - 免费 PDF：https://linear.axler.net/
- 📘 **《Introduction to Linear Algebra》** — Gilbert Strang（MIT 18.06 教材）

### 进阶
- 📘 《Matrix Analysis》 — Horn & Johnson（矩阵理论圣经）
- 📘 《Matrix Computations》 — Golub & Van Loan（数值线代）

### 中文
- 📘 《线性代数及其应用》 — David C. Lay
- 📘 《矩阵分析与应用》 — 张贤达

### AI 加餐
- ⭐ **《The Matrix Cookbook》**（矩阵求导手册）
  https://www.math.uwaterloo.ca/~hwolkowi/matrixcookbook.pdf
- ⭐ **《Mathematics for Machine Learning》第 2-4 章**
  https://mml-book.github.io/
- **fast.ai《Computational Linear Algebra》**
  https://github.com/fastai/numerical-linear-algebra

---

## 按知识点精读

### 1. 向量（Vector）
- 3B1B 第 1-3 集：向量、线性组合、张成空间
- NumPy 实战：加法、点积、叉积、范数

### 2. 矩阵（Matrix）
- 3B1B 第 3-7 集：**矩阵 = 线性变换**（最重要的认知！）
- MIT 18.06 Lecture 1-4
- 重点：矩阵乘法 4 种理解、逆/转置/秩、特殊矩阵

### 3. 张量（Tensor）
> ML 中的"张量"≠数学张量，本质是多维数组

- [李沐《动手学深度学习》第 2 章](https://zh.d2l.ai/chapter_preliminaries/ndarray.html)
- [PyTorch Tensor 教程](https://pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html)
- ⭐ **[Einsum is All You Need](https://rockt.github.io/2018/04/30/einsum)**（**理解 Transformer 必备**）

### 4. 特征值分解（Eigendecomposition）
- 3B1B 第 14 集：**看完秒懂**
- MIT 18.06 Lecture 21-22
- 关联学习：
  - **SVD（奇异值分解）** — AI 中比特征值分解更常用
  - **PCA（主成分分析）** — 经典应用
- 必读：
  - [PCA Tutorial — Shlens](https://arxiv.org/abs/1404.1100)
  - [SVD 通俗介绍 (AMS)](https://www.ams.org/publicoutreach/feature-column/fcarc-svd)

---

## 3 周学习计划

```
Week 1: 3B1B 16 集 + NumPy 向量/矩阵实操
        ↓
Week 2: MIT 18.06 选听 (Lec 1-10, 21-22) + 习题
        ↓
Week 3: 张量与 einsum + SVD/PCA 实战
        ↓
检验：能用 NumPy 手写 PCA 算法
```

---

## 实战练习

### NumPy 基础
```python
import numpy as np
v = np.array([1, 2, 3])
A = np.array([[1, 2], [3, 4]])
np.dot(v, v)            # 点积
A @ A                   # 矩阵乘法
np.linalg.inv(A)        # 逆矩阵
np.linalg.matrix_rank(A)  # 秩
```

### 特征值与 SVD
```python
eigenvalues, eigenvectors = np.linalg.eig(A)
U, S, Vt = np.linalg.svd(A)
```

### einsum 实战
```python
import torch
A = torch.randn(10, 3, 4)
B = torch.randn(10, 4, 5)
# 批量矩阵乘法
C = torch.einsum('bij,bjk->bik', A, B)
```

---

## 产出 Checklist

- [ ] 笔记：向量与线性变换的几何理解
- [ ] 笔记：矩阵乘法的 4 种视角
- [ ] 笔记：特征值/特征向量直观解释
- [ ] 笔记：SVD vs 特征值分解对比
- [ ] 笔记：einsum 用法整理
- [ ] **代码：手写 PCA（不调用 sklearn）** → 放到 `../产出/`
- [ ] **代码：用 SVD 做图像压缩 demo**

---

## 待定/疑问

记录学习中遇到的问题，定期回看：

```
- [ ] (示例) SVD 中 U/Σ/V^T 的几何意义？
- [ ] (示例) 为什么协方差矩阵是对称的？
```
