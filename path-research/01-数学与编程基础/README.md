# 阶段 1：数学与编程基础

> 周期：1-2 个月｜目标：补齐数学直觉 + 掌握 PyTorch

---

## 子目录说明

```
01-阶段1-数学与编程基础/
├── 1.1-线性代数/        # 向量、矩阵、张量、特征值分解、SVD
├── 1.2-微积分/          # 导数、偏导、链式法则、梯度下降
├── 1.3-概率统计/        # 贝叶斯、KL散度、交叉熵
├── 1.4-Python与PyTorch/ # NumPy、Pandas、PyTorch
├── 资料/                # 通用资料（PDF、cheatsheet）
├── 笔记/                # 学习笔记（按日期）
├── 代码/                # Jupyter Notebook、练习代码
└── 产出/                # 阶段产出项目
```

---

## 知识点清单

### 1.1 线性代数
- [ ] 向量空间、线性组合、张成
- [ ] 矩阵作为线性变换
- [ ] 矩阵乘法、逆、转置、秩
- [ ] 特征值与特征向量
- [ ] SVD（奇异值分解）
- [ ] 张量与 einsum
- [ ] PCA（应用）

### 1.2 微积分
- [ ] 导数与偏导
- [ ] 链式法则（理解反向传播）
- [ ] 梯度、方向导数
- [ ] 简单的最优化

### 1.3 概率统计
- [ ] 条件概率、贝叶斯定理
- [ ] 期望、方差、协方差
- [ ] KL 散度、交叉熵
- [ ] 最大似然估计

### 1.4 Python 与 PyTorch
- [ ] NumPy 数组操作
- [ ] Pandas 数据处理
- [ ] PyTorch Tensor
- [ ] autograd 自动求导
- [ ] nn.Module 模型构建
- [ ] DataLoader 数据加载
- [ ] 训练循环

---

## 产出要求

- [ ] **手写 PCA**（仅用 NumPy，含 SVD 实现）
- [ ] **MNIST 分类器**（PyTorch，准确率 ≥ 98%）
- [ ] **完整学习笔记**（线性代数 + PyTorch 基础）

---

## 关键资源

详细资源清单见各子目录 README，通用入口：
- 📺 [3Blue1Brown《线性代数的本质》](https://www.bilibili.com/video/BV1ys411472E)
- 📺 [李沐《动手学深度学习》](https://zh.d2l.ai/)
- 📚 [Mathematics for Machine Learning (免费 PDF)](https://mml-book.github.io/)

---

## 时间安排建议

| 周 | 主题 | 重点 |
|----|------|------|
| W1 | 线性代数 | 3B1B 16 集 + NumPy |
| W2 | 线性代数进阶 | MIT 18.06 + 特征值/SVD |
| W3 | 微积分 + 概率 | 重点理解链式法则 |
| W4 | Python + PyTorch | NumPy + PyTorch 基础 |
| W5 | PyTorch 实战 | MNIST 分类器 |
| W6 | 综合产出 | 手写 PCA + 整理笔记 |
