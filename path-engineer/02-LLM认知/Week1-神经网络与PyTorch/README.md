# Week 1 · 神经网络 + PyTorch 速览（5 天）

> 🎯 **本周目标**：理解神经网络是怎么训练的，PyTorch 代码不再陌生
>
> ⏱️ **时间预算**：5 天 × 1.5h = 7.5 小时（工作日晚上）+ 周末复盘 1.5h，共约 9h
>
> 🪜 **关键认知**：你不是要"学会训练大模型"，是**要看到 PyTorch 代码时知道每一行在干什么**。

---

## 📌 核心心法（先看这个）

### 1. 这周到底学到什么程度

| ✅ 应该达到的 | ❌ 不要追求的 |
|------------|------------|
| 看到 `nn.Module` 子类，知道在定义模型 | 从零写一个深度学习框架 |
| 看到 `loss.backward()` 知道在干嘛 | 手推反向传播每一步梯度 |
| 能跑通 MNIST 训练并解释每一行 | 调出 99% 准确率刷榜 |
| 能解释为什么需要 GPU | 学会写 CUDA kernel |
| 知道 SGD vs Adam 的差别（一句话）| 读完《Deep Learning》Goodfellow |

### 2. 学习方式：**Java 类比 + 跑代码**

每个知识点的套路：

```
1. 看 5 分钟 Java 类比（建立心智模型）
2. 看一段最简 PyTorch 代码
3. 自己敲一遍（不要复制粘贴！）
4. 改几个参数看效果变化
5. 完成当天练习
```

### 3. 心理建设

> **第一天会觉得"概念很多但都很糊"** —— 正常，神经网络的直觉需要看完整训练循环才会建立。
>
> **第三天 PyTorch 上手就会**"咦，比 Java 简洁多了"。
>
> **第五天跑通 MNIST**，你就有"我能训练神经网络"的底气了。

---

## 🪜 学习起点

完成阶段 1 后你已经有的基础：

- ✅ Python 能看懂、能写脚本（[阶段 1 Week 1](../../01-基础速通/Week1-Python速通/)）
- ✅ NumPy 矩阵运算、广播、`@` 矩阵乘（[阶段 1 Week 1 Day 4](../../01-基础速通/Week1-Python速通/Day4-NumPy基础.md)）
- ✅ 知道 Softmax / 交叉熵 / 梯度的概念（[阶段 1 Week 3](../../01-基础速通/Week3-数学补盲/)）

> 💡 这意味着：本周 PyTorch ≈ **「带了 GPU 加速 + 自动求梯度的 NumPy」**，认知负担没你想的大。

---

## 🗓️ 5 天规划速览

| 天 | 主题 | 核心内容 | 产出 |
|----|------|---------|------|
| **Day 1** | [神经网络基础](./Day1-神经网络基础.md) | 神经元 / 激活函数 / MLP / Loss / 前向传播 | 一张神经网络结构图 |
| **Day 2** | [PyTorch 入门（上）](./Day2-PyTorch入门上.md) | Tensor / autograd / `nn.Module` | 自己写一个两层网络 |
| **Day 3** | [PyTorch 入门（下）](./Day3-PyTorch入门下.md) | Optimizer / DataLoader / GPU 调用 | 完整训练循环代码 |
| **Day 4** | [MNIST 实战](./Day4-MNIST实战.md) ⭐ | 30 行跑通手写识别 | 一个能跑的模型 + 准确率截图 |
| **Day 5** | [训练循环速查](./Day5-训练循环速查.md) | 把 4 天揉成一份模板 | 《PyTorch 训练循环模板》|

---

## 📦 配套资源

### 必备工具

| 工具 | 用途 | 安装 |
|------|------|------|
| **Python 3.11+** | 语言本体（已装）| `python3 --version` |
| **PyTorch 2.x** | 深度学习框架 | `pip install torch torchvision` |
| **Jupyter Lab** | 交互式调试（强烈推荐）| 已装 |
| **matplotlib** | 画训练曲线 | `pip install matplotlib` |

> 💡 **Mac 用户**：PyTorch 现已原生支持 Apple Silicon GPU（MPS 后端），M1/M2/M3 都能用 `device='mps'` 加速，**不用云 GPU 也能跑通本周内容**。

### 推荐资源（精选，不要贪多）

| 资源 | 形式 | 时长 | 推荐度 |
|------|------|------|------|
| [PyTorch 官方 60 分钟入门](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) | 文字 | 1h | ⭐⭐⭐⭐⭐（必跑）|
| [3Blue1Brown 神经网络系列](https://www.bilibili.com/video/BV1bx411M7Zx/) | 视频 | 1h | ⭐⭐⭐⭐⭐（建立直觉，B 站中文字幕）|
| [李宏毅深度学习课程](https://www.bilibili.com/video/BV1Wv411h7kN/) | 视频 | 选看前 5 节 | ⭐⭐⭐⭐ |
| [d2l.ai 中文版](https://zh.d2l.ai/) 第 3-5 章 | 文字 | 选读 | ⭐⭐⭐⭐（卡住时翻一翻）|
| 《动手学深度学习》李沐 | 书 | 1 个月 | ⭐⭐⭐（学完想深入再看）|

> 💡 **本周策略**：以**本目录的 Day1~5 教程**为主，补充看一遍 3Blue1Brown 第一集建立直觉。**别想着把所有资源刷完。**

---

## 🎯 本周完成标准（自测）

学完这 5 天，你应该能做到：

- [ ] **能解释什么是神经网络**：用一句话回答非技术同事
- [ ] **能看懂任意一段 PyTorch 训练代码**：知道每一行在做什么
- [ ] **能默写训练循环 4 步**：`forward → loss → backward → step`
- [ ] **MNIST 跑通且准确率 > 95%**：在 [Day 4](./Day4-MNIST实战.md) 完成
- [ ] **能解释梯度下降**：参数 = 参数 - 学习率 × 梯度
- [ ] **知道 SGD / Adam 的区别**：一句话级即可
- [ ] **不被 PyTorch 代码吓到**：阶段 3 看 Spring AI / HuggingFace 时心里有底

---

## 🚀 开始学习

### 推荐节奏

```
工作日晚上（每天 1.5h）：
  20:00 - 20:15  快速浏览当天 Day{N}.md
  20:15 - 21:15  对照教程敲代码 + 改参数实验
  21:15 - 21:30  做当天练习题（练习/dayN_练习.py）

周末（额外 1.5h）：
  - 复盘 Day 4 MNIST 项目，把准确率从 95% 提到 98%
  - 把训练曲线画出来，截图存进笔记
```

### 第一步

👉 现在打开 [Day 1 · 神经网络基础](./Day1-神经网络基础.md) 开始学习。

---

## 🆘 卡住了怎么办？

| 情况 | 解决方式 |
|------|---------|
| `pip install torch` 慢 | 换清华源：`pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 没有 GPU 跑得慢 | 本周代码 CPU 都能跑，MNIST 也只要 1-2 分钟 |
| Mac 想用 GPU | 用 `device = 'mps' if torch.backends.mps.is_available() else 'cpu'` |
| 报错 `CUDA out of memory` | 把 batch_size 调小（如 32 → 16）|
| 训练 loss 不下降 | 检查学习率（lr）、看输入数据是否归一化、看模型是否真的在调用 |
| 概念混乱 | 跳过去先跑通，回头再补 |

---

## 🔗 相关链接

- ⬆️ [回到阶段 2 总览](../README.md)
- ⬅️ [上一阶段 · 基础速通](../../01-基础速通/README.md)
- ➡️ [Week 2 · Transformer](../Week2-Transformer/) （下周）
- 📋 [path-engineer 主路径](../../README.md)
